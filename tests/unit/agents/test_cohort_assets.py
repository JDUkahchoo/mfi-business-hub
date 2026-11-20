from __future__ import annotations

from pathlib import Path

from app.agents.definitions.json_repository import JsonAgentManifestRepository
from app.agents.definitions.models import (
    ActivationEligibility,
    DataClassification,
    DefinitionCompleteness,
    ExecutionPolicy,
)
from app.agents.definitions.prompt_loader import PromptLoader
from app.agents.definitions.readiness import evaluate_readiness
from app.agents.definitions.service import AgentDefinitionService
from app.organization import AgentStatus, JsonOrganizationRepository


REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_definitions(expected_agent_ids: frozenset[str]):
    return AgentDefinitionService(
        JsonOrganizationRepository(REPO_ROOT / "config/organization/registry.json"),
        JsonAgentManifestRepository(
            REPO_ROOT / "config/agents/cohort-1", expected_agent_ids
        ),
        PromptLoader(REPO_ROOT),
        expected_agent_ids=expected_agent_ids,
    ).load_all()


def test_orchestrator_definition_package() -> None:
    definitions = _load_definitions(frozenset({"mfi-orchestrator"}))

    assert len(definitions) == 1
    definition = definitions[0]
    manifest = definition.manifest
    assert definition.registry_record.id == "mfi-orchestrator"
    assert definition.registry_record.display_name == "MFI Orchestrator"
    assert definition.registry_record.purpose == (
        "Routes governed tasks and coordinates registered agents."
    )
    assert definition.registry_record.status is AgentStatus.PLANNED
    assert definition.registry_record.version == "0.1.0"
    assert definition.registry_record.owner_id == "enterprise-orchestration"
    assert manifest.allowed_tools == ()
    assert manifest.authority_grant_ids == ()
    assert manifest.allowed_data_classifications == (
        DataClassification.PUBLIC,
        DataClassification.INTERNAL,
    )
    assert manifest.routing_policy.execution_policy is ExecutionPolicy.LOCAL_PREFERRED
    assert manifest.routing_policy.cloud_fallback_allowed is False
    assert manifest.prompt_sources == (
        "prompts/agents/shared/governance.md",
        "prompts/agents/cohort-1/mfi-orchestrator/system.md",
    )
    assert manifest.capability_requirements == (
        "reasoning",
        "structured-output",
        "task-decomposition",
        "coordination",
    )
    assert manifest.input_contracts[0].id == "task-brief"
    assert manifest.output_contracts[0].id == "coordination-plan"
    assert definition.resolved_grants == ()

    readiness = evaluate_readiness(definition)
    assert readiness.completeness is DefinitionCompleteness.COMPLETE
    assert readiness.eligibility is ActivationEligibility.BLOCKED
    assert readiness.blocker_codes[0] == "lifecycle-status-planned"
