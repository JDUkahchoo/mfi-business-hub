from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from app.agents.definitions.errors import DefinitionValidationError
from app.agents.definitions.json_repository import parse_manifest_data
from app.agents.definitions.prompt_loader import PromptLoader
from app.agents.definitions.service import AgentDefinitionService
from app.organization import (
    AgentDefinition,
    AgentStatus,
    AuthorityGrant,
    AuthorityLevel,
    GrantSubjectType,
    OrganizationRegistry,
    OwnerType,
    RoleDefinition,
)


def _agent_prompt() -> str:
    return """## Purpose
Coordinate governed work.
## Responsibilities
Propose task order.
## Inputs
Governed requests.
## Outputs
Coordination plans.
## Boundaries
No execution authority.
## Escalation
Escalate uncertainty.
## Prohibited actions
Do not approve work.
"""


def _write_prompts(root: Path) -> tuple[Path, Path]:
    shared = root / "prompts/agents/shared/governance.md"
    specific = root / "prompts/agents/cohort-1/mfi-orchestrator/system.md"
    shared.parent.mkdir(parents=True)
    specific.parent.mkdir(parents=True)
    shared.write_text("Human decisions take precedence.\n", encoding="utf-8")
    specific.write_text(_agent_prompt(), encoding="utf-8")
    return shared, specific


def _registry(
    *,
    agent_id: str = "mfi-orchestrator",
    owner_id: str = "role-coo",
    grants: tuple[AuthorityGrant, ...] = (),
) -> OrganizationRegistry:
    return OrganizationRegistry(
        roles=(RoleDefinition("role-coo", "COO", "Operations owner."),),
        seats=(),
        agents=(
            AgentDefinition(
                id=agent_id,
                display_name="MFI Orchestrator",
                purpose="Coordinate governed work.",
                status=AgentStatus.PLANNED,
                version="0.1.0",
                owner_type=OwnerType.ROLE,
                owner_id=owner_id,
            ),
        ),
        authority_grants=grants,
    )


class InMemoryOrganizationRepository:
    def __init__(self, registry: OrganizationRegistry) -> None:
        self.registry = registry
        self.load_count = 0

    def load(self) -> OrganizationRegistry:
        self.load_count += 1
        return self.registry


class InMemoryManifestRepository:
    def __init__(self, manifests: tuple) -> None:
        self.manifests = manifests

    def load_all(self) -> tuple:
        return self.manifests


def test_joins_manifest_to_canonical_registry_and_prompts_without_writes(
    tmp_path: Path, valid_manifest_data: dict[str, object]
) -> None:
    prompt_paths = _write_prompts(tmp_path)
    before = tuple((path.read_bytes(), path.stat().st_mtime_ns) for path in prompt_paths)
    manifest = parse_manifest_data(valid_manifest_data, "manifest")
    organization_repository = InMemoryOrganizationRepository(_registry())

    definitions = AgentDefinitionService(
        organization_repository,
        InMemoryManifestRepository((manifest,)),
        PromptLoader(tmp_path),
        expected_agent_ids=frozenset({"mfi-orchestrator"}),
    ).load_all()

    assert organization_repository.load_count == 1
    assert len(definitions) == 1
    definition = definitions[0]
    assert definition.registry_record.display_name == "MFI Orchestrator"
    assert definition.registry_record.purpose == "Coordinate governed work."
    assert definition.registry_record.status is AgentStatus.PLANNED
    assert definition.registry_record.version == "0.1.0"
    assert definition.registry_record.owner_id == "role-coo"
    assert tuple(source.path for source in definition.prompt_sources) == manifest.prompt_sources
    assert definition.resolved_grants == ()
    assert tuple((path.read_bytes(), path.stat().st_mtime_ns) for path in prompt_paths) == before


@pytest.mark.parametrize("case", ["missing", "extra", "unknown", "bad-owner"])
def test_rejects_registry_manifest_join_mismatches(
    tmp_path: Path, valid_manifest_data: dict[str, object], case: str
) -> None:
    _write_prompts(tmp_path)
    manifest = parse_manifest_data(valid_manifest_data, "manifest")
    expected = frozenset({"mfi-orchestrator"})
    registry = _registry()
    manifests = (manifest,)
    if case == "missing":
        manifests = ()
    elif case == "extra":
        expected = frozenset()
    elif case == "unknown":
        registry = _registry(agent_id="mfi-qa-auditor")
    else:
        registry = _registry(owner_id="missing-role")

    with pytest.raises(DefinitionValidationError):
        AgentDefinitionService(
            InMemoryOrganizationRepository(registry),
            InMemoryManifestRepository(manifests),
            PromptLoader(tmp_path),
            expected_agent_ids=expected,
        ).load_all()


def test_rejects_missing_or_wrong_subject_authority_grants(
    tmp_path: Path, valid_manifest_data: dict[str, object]
) -> None:
    _write_prompts(tmp_path)
    manifest = parse_manifest_data(valid_manifest_data, "manifest")
    grant = AuthorityGrant(
        id="grant-read",
        subject_type=GrantSubjectType.AGENT,
        subject_id="another-agent",
        level=AuthorityLevel.READ,
        scope="internal plans",
    )
    manifest = replace(manifest, authority_grant_ids=("grant-read", "missing-grant"))

    with pytest.raises(DefinitionValidationError) as exc_info:
        AgentDefinitionService(
            InMemoryOrganizationRepository(_registry(grants=(grant,))),
            InMemoryManifestRepository((manifest,)),
            PromptLoader(tmp_path),
            expected_agent_ids=frozenset({"mfi-orchestrator"}),
        ).load_all()

    assert "missing-grant" in str(exc_info.value)
    assert "another-agent" in str(exc_info.value)
