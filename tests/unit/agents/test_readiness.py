from __future__ import annotations

from dataclasses import replace
import hashlib

import pytest

from app.agents.definitions.errors import DefinitionValidationError
from app.agents.definitions.json_repository import parse_manifest_data
from app.agents.definitions.models import (
    ActivationEligibility,
    DefinitionCompleteness,
    GovernedAgentDefinition,
    LoadedPromptSource,
    ReadinessEvidence,
    RuntimeTestCategory,
)
from app.agents.definitions.readiness import evaluate_all, evaluate_readiness
from app.agents.definitions.prompt_loader import compose_prompt
from app.organization import AgentDefinition, AgentStatus, OwnerType


def _definition(valid_manifest_data: dict[str, object]) -> GovernedAgentDefinition:
    manifest = parse_manifest_data(valid_manifest_data, "manifest")
    prompt_texts = (
        "Human decisions take precedence.\n",
        """## Purpose
Coordinate work.
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
""",
    )
    sources = tuple(
        LoadedPromptSource(
            path,
            text,
            hashlib.sha256(text.encode("utf-8")).hexdigest(),
        )
        for path, text in zip(manifest.prompt_sources, prompt_texts, strict=True)
    )
    return GovernedAgentDefinition(
        registry_record=AgentDefinition(
            id="mfi-orchestrator",
            display_name="MFI Orchestrator",
            purpose="Coordinate governed work.",
            status=AgentStatus.PLANNED,
            version="0.1.0",
            owner_type=OwnerType.ROLE,
            owner_id="role-coo",
        ),
        manifest=manifest,
        prompt_sources=sources,
        composed_prompt=compose_prompt(sources),
        resolved_grants=(),
    )


def test_complete_planned_definition_reports_ordered_missing_evidence_blockers(
    valid_manifest_data: dict[str, object],
) -> None:
    report = evaluate_readiness(_definition(valid_manifest_data))

    assert report.completeness is DefinitionCompleteness.COMPLETE
    assert report.eligibility is ActivationEligibility.BLOCKED
    assert report.blocker_codes == (
        "lifecycle-status-planned",
        "runtime-implementation-missing",
        "runtime-test-normal-missing",
        "runtime-test-denied-missing",
        "runtime-test-malformed-missing",
        "runtime-test-escalation-missing",
        "audit-event-agent-run-requested-missing",
        "audit-event-agent-run-started-missing",
        "audit-event-agent-run-completed-missing",
        "audit-event-agent-run-failed-missing",
        "audit-event-agent-run-escalated-missing",
        "acceptance-criterion-normal-path-tested-missing",
        "accountable-human-acceptance-missing",
    )


def test_complete_evidence_cannot_make_planned_agent_eligible(
    valid_manifest_data: dict[str, object],
) -> None:
    definition = _definition(valid_manifest_data)
    evidence = ReadinessEvidence(
        runtime_implementation_verified=True,
        runtime_test_categories=frozenset(RuntimeTestCategory),
        verified_audit_events=frozenset(definition.manifest.audit_events),
        satisfied_acceptance_criteria=frozenset(
            item.id for item in definition.manifest.acceptance_criteria
        ),
        accountable_human_accepted=True,
    )

    report = evaluate_readiness(definition, evidence)

    assert report.completeness is DefinitionCompleteness.COMPLETE
    assert report.eligibility is ActivationEligibility.BLOCKED
    assert report.blocker_codes == ("lifecycle-status-planned",)
    assert definition.registry_record.status is AgentStatus.PLANNED


@pytest.mark.parametrize("kind", ["category", "audit", "criterion"])
def test_rejects_unknown_readiness_evidence_references(
    valid_manifest_data: dict[str, object], kind: str
) -> None:
    definition = _definition(valid_manifest_data)
    kwargs = {}
    if kind == "category":
        kwargs["runtime_test_categories"] = frozenset({"UNKNOWN"})
    elif kind == "audit":
        kwargs["verified_audit_events"] = frozenset({"agent.run.unknown"})
    else:
        kwargs["satisfied_acceptance_criteria"] = frozenset({"unknown-criterion"})

    with pytest.raises(DefinitionValidationError):
        evaluate_readiness(definition, ReadinessEvidence(**kwargs))


def test_rejects_non_boolean_readiness_evidence_flags(
    valid_manifest_data: dict[str, object],
) -> None:
    definition = _definition(valid_manifest_data)

    with pytest.raises(DefinitionValidationError) as exc_info:
        evaluate_readiness(
            definition,
            ReadinessEvidence(
                runtime_implementation_verified="false",  # type: ignore[arg-type]
                accountable_human_accepted="false",  # type: ignore[arg-type]
            ),
        )

    text = str(exc_info.value)
    assert "runtime_implementation_verified" in text
    assert "accountable_human_accepted" in text


def test_evaluate_all_rejects_unknown_agent_evidence_and_sorts_reports(
    valid_manifest_data: dict[str, object],
) -> None:
    definition = _definition(valid_manifest_data)

    with pytest.raises(DefinitionValidationError) as exc_info:
        evaluate_all((definition,), {"unknown-agent": ReadinessEvidence()})

    assert "unknown-agent" in str(exc_info.value)


def test_definition_completeness_failure_precedes_evidence_gaps(
    valid_manifest_data: dict[str, object],
) -> None:
    definition = _definition(valid_manifest_data)
    invalid = replace(
        definition,
        manifest=replace(definition.manifest, allowed_tools=("unsafe-tool",)),
    )

    report = evaluate_readiness(invalid)

    assert report.completeness is DefinitionCompleteness.INCOMPLETE
    assert report.blocker_codes[0] == "definition-invalid"
    assert report.eligibility is ActivationEligibility.BLOCKED


@pytest.mark.parametrize("corruption", ["blank-text", "bad-digest", "bad-composition"])
def test_prompt_integrity_is_required_for_definition_completeness(
    valid_manifest_data: dict[str, object], corruption: str
) -> None:
    definition = _definition(valid_manifest_data)
    if corruption == "blank-text":
        first = replace(definition.prompt_sources[0], text="")
        invalid = replace(
            definition, prompt_sources=(first, definition.prompt_sources[1])
        )
    elif corruption == "bad-digest":
        first = replace(definition.prompt_sources[0], sha256_digest="not-a-digest")
        invalid = replace(
            definition, prompt_sources=(first, definition.prompt_sources[1])
        )
    else:
        invalid = replace(definition, composed_prompt="unrelated prompt text")

    report = evaluate_readiness(invalid)

    assert report.completeness is DefinitionCompleteness.INCOMPLETE
    assert report.blocker_codes[0] == "definition-invalid"
