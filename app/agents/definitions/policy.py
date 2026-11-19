from __future__ import annotations

import re


COHORT_1_AGENT_IDS = frozenset(
    {
        "mfi-orchestrator",
        "mfi-qa-auditor",
        "mfi-infrastructure-lead",
        "mfi-tech-entertainment-lead",
        "mfi-investments-lead",
        "mfi-incubation-lead",
    }
)

REQUIRED_AUDIT_EVENTS = (
    "agent.run.requested",
    "agent.run.started",
    "agent.run.completed",
    "agent.run.failed",
    "agent.run.escalated",
)

REQUIRED_PROMPT_HEADINGS = (
    "## Purpose",
    "## Responsibilities",
    "## Inputs",
    "## Outputs",
    "## Boundaries",
    "## Escalation",
    "## Prohibited actions",
)

KNOWN_SYSTEM_IDS = frozenset({"mfi-business-hub"})
PROVIDER_MODEL_DENYLIST = frozenset(
    {"anthropic", "claude", "openai", "grok", "lmstudio", "gemma", "nemotron"}
)

AGENT_ID_PATTERN = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
FIELD_NAME_PATTERN = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*")
CAPABILITY_ID_PATTERN = AGENT_ID_PATTERN
AUDIT_EVENT_PATTERN = re.compile(r"[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)+")
