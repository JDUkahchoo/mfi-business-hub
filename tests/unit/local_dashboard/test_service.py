from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from app.agents.definitions.errors import DefinitionFinding, DefinitionValidationError
from app.local_dashboard.service import InconsistentSnapshotError, LocalDashboardService, UnknownAgentError


ORDER = (
    "mfi-orchestrator", "mfi-qa-auditor", "mfi-infrastructure-lead",
    "mfi-tech-entertainment-lead", "mfi-investments-lead", "mfi-incubation-lead",
)


def _clock() -> datetime:
    return datetime(2026, 11, 21, 18, 30, tzinfo=timezone.utc)


class SequenceDefinitionService:
    def __init__(self, *results):
        self.results = list(results)
        self.calls = 0

    def load_all(self):
        result = self.results[min(self.calls, len(self.results) - 1)]
        self.calls += 1
        if isinstance(result, Exception):
            raise result
        return result


def test_builds_canonical_six_agent_snapshot(definition_service) -> None:
    payload = LocalDashboardService(definition_service, clock=_clock).dashboard().to_payload()
    assert payload["generated_at"] == "2026-11-21T18:30:00Z"
    assert tuple(agent["agent_id"] for agent in payload["agents"]) == ORDER
    assert payload["counts"] == {
        "definitions": 6, "complete": 6, "active": 0, "planned": 6,
        "eligible": 0, "blocked": 6, "tools": 0, "grants": 0,
    }
    assert tuple(pillar["pillar_id"] for pillar in payload["pillars"]) == (
        "infrastructure-supply-chain", "technology-gaming-entertainment",
        "investments", "incubation",
    )
    assert [agent["role_category"] for agent in payload["agents"][:2]] == ["COORDINATION", "ASSURANCE"]
    assert all(agent["completeness"] == "COMPLETE" for agent in payload["agents"])
    assert all(agent["lifecycle"] == "PLANNED" for agent in payload["agents"])
    assert all(agent["eligibility"] == "BLOCKED" for agent in payload["agents"])


def test_detail_contains_governed_fields_but_never_prompt_text(definition_service) -> None:
    payload = LocalDashboardService(definition_service, clock=_clock).agent_detail("mfi-orchestrator").to_payload()
    assert payload["agent_id"] == "mfi-orchestrator"
    for key in ("responsibilities", "non_responsibilities", "input_contracts", "output_contracts", "approvals", "audit_events", "acceptance_criteria"):
        assert payload[key]
    assert all(len(source["sha256"]) == 64 for source in payload["prompt_sources"])
    serialized = repr(payload).casefold()
    assert "composed_prompt" not in serialized
    assert "human decisions take precedence" not in serialized


def test_prompt_is_available_only_from_explicit_prompt_method(definition_service) -> None:
    prompt = LocalDashboardService(definition_service, clock=_clock).prompt("mfi-orchestrator").to_payload()
    assert prompt["agent_id"] == "mfi-orchestrator"
    assert "Human decisions and established MFI governance take precedence" in prompt["composed_prompt"]
    assert len(prompt["sources"]) == 2


def test_unknown_agent_is_a_stable_domain_error(definition_service) -> None:
    service = LocalDashboardService(definition_service, clock=_clock)
    with pytest.raises(UnknownAgentError, match="unknown agent ID"):
        service.agent_detail("missing-agent")
    with pytest.raises(UnknownAgentError, match="unknown agent ID"):
        service.prompt("missing-agent")


def test_rejects_mixed_fingerprints_for_a_repeated_prompt_path(definition_service) -> None:
    definitions = definition_service.load_all()
    target = definitions[1]
    changed_source = replace(target.prompt_sources[0], sha256_digest="f" * 64)
    mixed = (definitions[0], replace(target, prompt_sources=(changed_source, *target.prompt_sources[1:])), *definitions[2:])
    with pytest.raises(InconsistentSnapshotError) as exc_info:
        LocalDashboardService(SequenceDefinitionService(mixed), clock=_clock).dashboard()
    assert "prompts/agents/shared/governance.md" in str(exc_info.value)
    assert "Human decisions" not in str(exc_info.value)


def test_accepts_repeated_prompt_path_when_fingerprints_match(definition_service) -> None:
    definitions = definition_service.load_all()
    payload = LocalDashboardService(SequenceDefinitionService(definitions), clock=_clock).dashboard().to_payload()
    assert payload["counts"]["definitions"] == 6


def test_validation_failure_is_atomic_and_has_deterministic_findings() -> None:
    error = DefinitionValidationError((DefinitionFinding("z.path", "second"), DefinitionFinding("a.path", "first")))
    service = LocalDashboardService(SequenceDefinitionService(error), clock=_clock)
    with pytest.raises(DefinitionValidationError) as exc_info:
        service.dashboard()
    assert tuple(str(item) for item in exc_info.value.findings) == ("a.path: first", "z.path: second")


def test_prompt_request_loads_a_fresh_snapshot(definition_service) -> None:
    definitions = definition_service.load_all()
    changed = tuple(replace(item, composed_prompt=item.composed_prompt + "\nFresh snapshot.") for item in definitions)
    sequence = SequenceDefinitionService(definitions, changed)
    service = LocalDashboardService(sequence, clock=_clock)
    service.agent_detail("mfi-orchestrator")
    prompt = service.prompt("mfi-orchestrator")
    assert sequence.calls == 2
    assert prompt.composed_prompt.endswith("Fresh snapshot.")
