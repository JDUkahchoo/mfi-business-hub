from __future__ import annotations

from collections.abc import Mapping

from app.organization import AgentStatus

from .errors import DefinitionFinding, DefinitionValidationError
from .models import (
    ActivationEligibility,
    DefinitionCompleteness,
    GovernedAgentDefinition,
    ReadinessEvidence,
    ReadinessReport,
    RuntimeTestCategory,
)
from .prompt_loader import compose_prompt, validate_loaded_prompt_sources
from .validation import validate_manifest


_RUNTIME_TEST_ORDER = (
    RuntimeTestCategory.NORMAL,
    RuntimeTestCategory.DENIED,
    RuntimeTestCategory.MALFORMED,
    RuntimeTestCategory.ESCALATION,
)


def _definition_is_complete(definition: GovernedAgentDefinition) -> bool:
    if validate_manifest(definition.manifest):
        return False
    if definition.registry_record.id != definition.manifest.agent_id:
        return False
    if tuple(source.path for source in definition.prompt_sources) != definition.manifest.prompt_sources:
        return False
    if validate_loaded_prompt_sources(definition.prompt_sources):
        return False
    if definition.composed_prompt != compose_prompt(definition.prompt_sources):
        return False
    if tuple(grant.id for grant in definition.resolved_grants) != definition.manifest.authority_grant_ids:
        return False
    return True


def _validate_evidence(
    definition: GovernedAgentDefinition, evidence: ReadinessEvidence
) -> None:
    findings: list[DefinitionFinding] = []
    if type(evidence.runtime_implementation_verified) is not bool:
        findings.append(
            DefinitionFinding(
                "runtime_implementation_verified", "must be a boolean"
            )
        )
    if type(evidence.accountable_human_accepted) is not bool:
        findings.append(
            DefinitionFinding("accountable_human_accepted", "must be a boolean")
        )
    for category in evidence.runtime_test_categories:
        if not isinstance(category, RuntimeTestCategory):
            findings.append(
                DefinitionFinding(
                    "runtime_test_categories", f"unknown test category {category!r}"
                )
            )
    known_audits = frozenset(definition.manifest.audit_events)
    for event in sorted(evidence.verified_audit_events - known_audits):
        findings.append(
            DefinitionFinding("verified_audit_events", f"unknown audit event {event!r}")
        )
    known_criteria = frozenset(
        criterion.id for criterion in definition.manifest.acceptance_criteria
    )
    for criterion_id in sorted(evidence.satisfied_acceptance_criteria - known_criteria):
        findings.append(
            DefinitionFinding(
                "satisfied_acceptance_criteria",
                f"unknown acceptance criterion {criterion_id!r}",
            )
        )
    if findings:
        raise DefinitionValidationError(findings)


def evaluate_readiness(
    definition: GovernedAgentDefinition,
    evidence: ReadinessEvidence | None = None,
) -> ReadinessReport:
    supplied = evidence or ReadinessEvidence()
    _validate_evidence(definition, supplied)

    complete = _definition_is_complete(definition)
    blockers: list[str] = []
    if not complete:
        blockers.append("definition-invalid")

    if definition.registry_record.status is not AgentStatus.ACTIVE:
        blockers.append(
            f"lifecycle-status-{definition.registry_record.status.value.casefold()}"
        )
    if not supplied.runtime_implementation_verified:
        blockers.append("runtime-implementation-missing")
    for category in _RUNTIME_TEST_ORDER:
        if category not in supplied.runtime_test_categories:
            blockers.append(f"runtime-test-{category.value.casefold()}-missing")
    for event in definition.manifest.audit_events:
        if event not in supplied.verified_audit_events:
            blockers.append(f"audit-event-{event.replace('.', '-')}-missing")
    for criterion in definition.manifest.acceptance_criteria:
        if criterion.id not in supplied.satisfied_acceptance_criteria:
            blockers.append(f"acceptance-criterion-{criterion.id}-missing")
    if not supplied.accountable_human_accepted:
        blockers.append("accountable-human-acceptance-missing")

    return ReadinessReport(
        agent_id=definition.registry_record.id,
        completeness=(
            DefinitionCompleteness.COMPLETE
            if complete
            else DefinitionCompleteness.INCOMPLETE
        ),
        eligibility=(
            ActivationEligibility.ELIGIBLE
            if not blockers
            else ActivationEligibility.BLOCKED
        ),
        blocker_codes=tuple(blockers),
    )


def evaluate_all(
    definitions: tuple[GovernedAgentDefinition, ...],
    evidence_by_agent: Mapping[str, ReadinessEvidence] | None = None,
) -> tuple[ReadinessReport, ...]:
    evidence_map = evidence_by_agent or {}
    definition_ids = [definition.registry_record.id for definition in definitions]
    findings: list[DefinitionFinding] = []
    for agent_id in sorted(set(evidence_map) - set(definition_ids)):
        findings.append(
            DefinitionFinding("evidence_by_agent", f"unknown agent ID {agent_id!r}")
        )
    for agent_id in sorted({item for item in definition_ids if definition_ids.count(item) > 1}):
        findings.append(
            DefinitionFinding("definitions", f"duplicate agent ID {agent_id!r}")
        )
    if findings:
        raise DefinitionValidationError(findings)

    return tuple(
        evaluate_readiness(definition, evidence_map.get(definition.registry_record.id))
        for definition in sorted(definitions, key=lambda item: item.registry_record.id)
    )
