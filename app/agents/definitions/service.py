from __future__ import annotations

from app.organization import GrantSubjectType, OrganizationRepository, OwnerType, SeatType

from .errors import DefinitionFinding, DefinitionValidationError
from .models import GovernedAgentDefinition
from .policy import COHORT_1_AGENT_IDS
from .prompt_loader import PromptLoader, compose_prompt
from .repository import AgentManifestRepository


class AgentDefinitionService:
    def __init__(
        self,
        organization_repository: OrganizationRepository,
        manifest_repository: AgentManifestRepository,
        prompt_loader: PromptLoader,
        expected_agent_ids: frozenset[str] = COHORT_1_AGENT_IDS,
    ) -> None:
        self._organization_repository = organization_repository
        self._manifest_repository = manifest_repository
        self._prompt_loader = prompt_loader
        self._expected_agent_ids = expected_agent_ids

    def load_all(self) -> tuple[GovernedAgentDefinition, ...]:
        registry = self._organization_repository.load()
        manifests = self._manifest_repository.load_all()
        findings: list[DefinitionFinding] = []

        outside_cohort = self._expected_agent_ids - COHORT_1_AGENT_IDS
        for agent_id in sorted(outside_cohort):
            findings.append(
                DefinitionFinding("expected_agent_ids", f"agent {agent_id!r} is outside Cohort 1")
            )

        manifest_ids = [manifest.agent_id for manifest in manifests]
        for agent_id in sorted(self._expected_agent_ids - frozenset(manifest_ids)):
            findings.append(
                DefinitionFinding("manifests", f"missing requested manifest {agent_id!r}")
            )
        for agent_id in sorted(frozenset(manifest_ids) - self._expected_agent_ids):
            findings.append(
                DefinitionFinding("manifests", f"unexpected manifest {agent_id!r}")
            )
        for agent_id in sorted({item for item in manifest_ids if manifest_ids.count(item) > 1}):
            findings.append(
                DefinitionFinding("manifests", f"duplicate manifest {agent_id!r}")
            )

        grants_by_id = {grant.id: grant for grant in registry.authority_grants}
        definitions: list[GovernedAgentDefinition] = []
        for manifest in manifests:
            agent_id = manifest.agent_id
            if agent_id not in self._expected_agent_ids or agent_id not in COHORT_1_AGENT_IDS:
                continue
            canonical = registry.get_agent(agent_id)
            if canonical is None:
                findings.append(
                    DefinitionFinding(agent_id, "does not exist in the organization registry")
                )
                continue

            owner_valid = True
            if canonical.owner_type is OwnerType.ROLE:
                owner_valid = registry.get_role(canonical.owner_id) is not None
            elif canonical.owner_type is OwnerType.SEAT:
                seat = registry.get_seat(canonical.owner_id)
                owner_valid = seat is not None and seat.seat_type in (
                    SeatType.HUMAN,
                    SeatType.HYBRID,
                )
            if not owner_valid:
                findings.append(
                    DefinitionFinding(
                        f"{agent_id}.owner_id",
                        f"invalid accountable owner {canonical.owner_id!r}",
                    )
                )

            resolved_grants = []
            for grant_id in manifest.authority_grant_ids:
                grant = grants_by_id.get(grant_id)
                if grant is None:
                    findings.append(
                        DefinitionFinding(
                            f"{agent_id}.authority_grant_ids",
                            f"unknown authority grant {grant_id!r}",
                        )
                    )
                    continue
                targets_agent = (
                    grant.subject_type is GrantSubjectType.AGENT
                    and grant.subject_id == agent_id
                )
                targets_owner_seat = (
                    canonical.owner_type is OwnerType.SEAT
                    and grant.subject_type is GrantSubjectType.SEAT
                    and grant.subject_id == canonical.owner_id
                )
                if not targets_agent and not targets_owner_seat:
                    findings.append(
                        DefinitionFinding(
                            f"{agent_id}.authority_grant_ids",
                            f"grant {grant_id!r} targets {grant.subject_id!r}, not this agent or its accountable seat",
                        )
                    )
                    continue
                resolved_grants.append(grant)

            try:
                prompt_sources = self._prompt_loader.load(manifest.prompt_sources)
            except DefinitionValidationError as exc:
                findings.extend(
                    DefinitionFinding(f"{agent_id}.{item.path}", item.message)
                    for item in exc.findings
                )
                continue

            definitions.append(
                GovernedAgentDefinition(
                    registry_record=canonical,
                    manifest=manifest,
                    prompt_sources=prompt_sources,
                    composed_prompt=compose_prompt(prompt_sources),
                    resolved_grants=tuple(resolved_grants),
                )
            )

        if findings:
            raise DefinitionValidationError(findings)
        return tuple(sorted(definitions, key=lambda item: item.registry_record.id))
