from __future__ import annotations

from dataclasses import FrozenInstanceError
import json

import pytest

from app.local_dashboard.models import (
    AcceptanceCriterionView,
    AgentDetailView,
    AgentSummaryView,
    ApprovalView,
    ContractView,
    DashboardCounts,
    DashboardSnapshot,
    HealthView,
    PillarView,
    PromptSourceView,
    PromptView,
    ReadinessGroupView,
    VIEW_MODEL_TYPES,
)


def _samples() -> tuple[object, ...]:
    source = PromptSourceView("prompts/shared.md", "a" * 64)
    contract = ContractView("request", "A request.", ("request_id",))
    approval = ApprovalView("external", "Before sending.", "ACCOUNTABLE_HUMAN")
    criterion = AcceptanceCriterionView("tested", "Normal path tested.", "TEST")
    summary = AgentSummaryView(
        "mfi-orchestrator", "MFI Orchestrator", "Coordinate.", "ROLE",
        "enterprise-orchestration", "COORDINATION", "COMPLETE", "PLANNED",
        "BLOCKED", 0, 0,
    )
    detail = AgentDetailView(
        agent_id="mfi-orchestrator", display_name="MFI Orchestrator",
        purpose="Coordinate.", version="0.1.0", owner_type="ROLE",
        owner_id="enterprise-orchestration", role_category="COORDINATION",
        completeness="COMPLETE", lifecycle="PLANNED", eligibility="BLOCKED",
        responsibilities=("Coordinate.",), non_responsibilities=("Do not execute.",),
        input_contracts=(contract,), output_contracts=(contract,), allowed_tools=(),
        allowed_systems=("mfi-business-hub",), data_classifications=("PUBLIC",),
        capability_requirements=("reasoning",), routing_execution_policy="LOCAL_PREFERRED",
        cloud_fallback_allowed=False, approval_requirements=(approval,),
        audit_events=("agent.run.requested",), failure_on_validation="STOP_AND_ESCALATE",
        failure_on_missing_authority="STOP_AND_ESCALATE",
        failure_on_dependency="PRESERVE_AND_ESCALATE", preserve_working_artifacts=True,
        escalation_destination="ACCOUNTABLE_OWNER", escalation_include_evidence=True,
        escalation_conditions=("Missing authority.",), acceptance_criteria=(criterion,),
        prompt_sources=(source,), blockers=("lifecycle-status-planned",),
    )
    counts = DashboardCounts(6, 6, 0, 6, 0, 6, 0, 0)
    pillar = PillarView("investments", "Investments", "Investment work.", ("mfi-investments-lead",))
    readiness = ReadinessGroupView("lifecycle", "Lifecycle", ("lifecycle-status-planned",))
    dashboard = DashboardSnapshot(
        "2026-11-21T12:00:00Z", counts, (pillar,), (summary,), (readiness,),
        ("Definitions do not activate agents.",),
    )
    return (
        counts, pillar, contract, approval, criterion, source, readiness, summary,
        detail, dashboard, PromptView("mfi-orchestrator", "Prompt body", (source,)),
        HealthView("ok", True, "2026-11-21T12:00:00Z"),
    )


def _assert_json_safe(value: object) -> None:
    if isinstance(value, dict):
        assert all(isinstance(key, str) for key in value)
        for item in value.values():
            _assert_json_safe(item)
    elif isinstance(value, list):
        for item in value:
            _assert_json_safe(item)
    else:
        assert value is None or type(value) in (str, int, bool)


def test_all_view_models_are_frozen_slotted_and_json_safe() -> None:
    samples = _samples()
    assert {type(item) for item in samples} == set(VIEW_MODEL_TYPES)
    for item in samples:
        assert hasattr(type(item), "__slots__")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            setattr(item, next(iter(item.__dataclass_fields__)), "changed")
        payload = item.to_payload()
        _assert_json_safe(payload)
        json.dumps(payload)


def test_snapshot_and_detail_payloads_use_the_governed_contract_keys() -> None:
    samples = _samples()
    detail = next(item for item in samples if isinstance(item, AgentDetailView)).to_payload()
    snapshot = next(item for item in samples if isinstance(item, DashboardSnapshot)).to_payload()
    prompt = next(item for item in samples if isinstance(item, PromptView)).to_payload()
    assert tuple(snapshot) == (
        "generated_at", "counts", "pillars", "agents", "readiness_blockers",
        "safety_boundaries",
    )
    assert "composed_prompt" not in detail
    assert detail["routing"] == {
        "execution_policy": "LOCAL_PREFERRED", "cloud_fallback_allowed": False
    }
    assert detail["failure_behavior"]["preserve_working_artifacts"] is True
    assert prompt["composed_prompt"] == "Prompt body"
