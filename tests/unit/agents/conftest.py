from __future__ import annotations

from copy import deepcopy

import pytest


@pytest.fixture
def valid_manifest_data() -> dict[str, object]:
    data: dict[str, object] = {
        "schema_version": 1,
        "agent_id": "mfi-orchestrator",
        "responsibilities": ["Coordinate task decomposition and dependencies."],
        "non_responsibilities": ["Do not approve or execute work."],
        "input_contracts": [
            {
                "id": "work-request",
                "description": "A governed request for coordination.",
                "required_fields": ["request_id", "objective"],
            }
        ],
        "output_contracts": [
            {
                "id": "coordination-plan",
                "description": "A proposed sequence and ownership plan.",
                "required_fields": ["task_order", "owner_recommendations"],
            }
        ],
        "allowed_tools": [],
        "allowed_systems": ["mfi-business-hub"],
        "allowed_data_classifications": ["PUBLIC", "INTERNAL"],
        "authority_grant_ids": [],
        "approval_requirements": [
            {
                "id": "external-communication",
                "trigger": "Before any external communication is sent.",
                "approver": "ACCOUNTABLE_HUMAN",
            }
        ],
        "prompt_sources": [
            "prompts/agents/shared/governance.md",
            "prompts/agents/cohort-1/mfi-orchestrator/system.md",
        ],
        "capability_requirements": [
            "reasoning",
            "structured-output",
            "task-decomposition",
            "coordination",
        ],
        "routing_policy": {
            "execution_policy": "LOCAL_PREFERRED",
            "cloud_fallback_allowed": False,
        },
        "audit_events": [
            "agent.run.requested",
            "agent.run.started",
            "agent.run.completed",
            "agent.run.failed",
            "agent.run.escalated",
        ],
        "failure_behavior": {
            "on_validation_failure": "STOP_AND_ESCALATE",
            "on_missing_authority": "STOP_AND_ESCALATE",
            "on_dependency_failure": "PRESERVE_AND_ESCALATE",
            "preserve_working_artifacts": True,
        },
        "escalation": {
            "destination": "ACCOUNTABLE_OWNER",
            "include_evidence": True,
            "conditions": [
                "Missing authority.",
                "Conflicting instructions.",
                "Unknown or incompatible data classification.",
                "Insufficient evidence.",
                "Material uncertainty.",
            ],
        },
        "acceptance_criteria": [
            {
                "id": "normal-path-tested",
                "description": "Normal behavior is verified.",
                "evidence_type": "TEST",
            }
        ],
    }
    return deepcopy(data)
