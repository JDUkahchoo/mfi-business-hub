from __future__ import annotations

import re
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Iterable

from .errors import DefinitionFinding
from .models import AgentManifest, DataClassification, EscalationDestination, ExecutionPolicy, FailureAction
from .policy import (
    AGENT_ID_PATTERN,
    CAPABILITY_ID_PATTERN,
    FIELD_NAME_PATTERN,
    KNOWN_SYSTEM_IDS,
    PROVIDER_MODEL_DENYLIST,
    REQUIRED_AUDIT_EVENTS,
)


def _duplicates(items: Iterable[str]) -> frozenset[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return frozenset(duplicates)


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _string_values(value: object, path: str) -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Enum):
        yield path, str(value.value)
    elif is_dataclass(value) and not isinstance(value, type):
        for item in fields(value):
            yield from _string_values(getattr(value, item.name), f"{path}.{item.name}")
    elif isinstance(value, (tuple, list, frozenset)):
        for index, item in enumerate(value):
            yield from _string_values(item, f"{path}[{index}]")


def validate_manifest(manifest: AgentManifest) -> tuple[DefinitionFinding, ...]:
    findings: list[DefinitionFinding] = []

    def add(path: str, message: str) -> None:
        findings.append(DefinitionFinding(path, message))

    if not AGENT_ID_PATTERN.fullmatch(manifest.agent_id):
        add("agent_id", "must be lowercase kebab-case")

    for name in ("responsibilities", "non_responsibilities"):
        values = getattr(manifest, name)
        if not values:
            add(name, "must not be empty")
        for index, value in enumerate(values):
            if not value.strip():
                add(f"{name}[{index}]", "must not be blank")
        for value in sorted(_duplicates(values)):
            add(name, f"contains duplicate statement {value!r}")

    for direction in ("input_contracts", "output_contracts"):
        contracts = getattr(manifest, direction)
        if not contracts:
            add(direction, "must not be empty")
        for duplicate in sorted(_duplicates(item.id for item in contracts)):
            add(direction, f"contains duplicate contract ID {duplicate!r}")
        for index, contract in enumerate(contracts):
            base = f"{direction}[{index}]"
            if not AGENT_ID_PATTERN.fullmatch(contract.id):
                add(f"{base}.id", "must be lowercase kebab-case")
            if not contract.description.strip():
                add(f"{base}.description", "must not be blank")
            if not contract.required_fields:
                add(f"{base}.required_fields", "must not be empty")
            for field_index, field_name in enumerate(contract.required_fields):
                if not FIELD_NAME_PATTERN.fullmatch(field_name):
                    add(f"{base}.required_fields[{field_index}]", "must be lowercase snake_case")
            for duplicate in sorted(_duplicates(contract.required_fields)):
                add(f"{base}.required_fields", f"contains duplicate field {duplicate!r}")

    if manifest.allowed_tools:
        add("allowed_tools", "must be empty for Cohort 1")
    if not manifest.allowed_systems:
        add("allowed_systems", "must contain mfi-business-hub")
    for index, system in enumerate(manifest.allowed_systems):
        if system not in KNOWN_SYSTEM_IDS:
            add(f"allowed_systems[{index}]", f"unknown system {system!r}")
    if manifest.authority_grant_ids:
        add("authority_grant_ids", "must be empty for Cohort 1")

    allowed_classifications = {DataClassification.PUBLIC, DataClassification.INTERNAL}
    if not manifest.allowed_data_classifications:
        add("allowed_data_classifications", "must not be empty")
    for index, classification in enumerate(manifest.allowed_data_classifications):
        if classification not in allowed_classifications:
            add(f"allowed_data_classifications[{index}]", "is not allowed for Cohort 1")

    if not manifest.approval_requirements:
        add("approval_requirements", "must not be empty")
    for duplicate in sorted(_duplicates(item.id for item in manifest.approval_requirements)):
        add("approval_requirements", f"contains duplicate ID {duplicate!r}")
    for index, requirement in enumerate(manifest.approval_requirements):
        if not AGENT_ID_PATTERN.fullmatch(requirement.id):
            add(f"approval_requirements[{index}].id", "must be lowercase kebab-case")
        if not requirement.trigger.strip():
            add(f"approval_requirements[{index}].trigger", "must not be blank")

    expected_prompts = (
        "prompts/agents/shared/governance.md",
        f"prompts/agents/cohort-1/{manifest.agent_id}/system.md",
    )
    if manifest.prompt_sources != expected_prompts:
        add("prompt_sources", "must contain shared governance then the agent system prompt")
    for duplicate in sorted(_duplicates(manifest.prompt_sources)):
        add("prompt_sources", f"contains duplicate path {duplicate!r}")

    if not manifest.capability_requirements:
        add("capability_requirements", "must not be empty")
    for index, capability in enumerate(manifest.capability_requirements):
        if not CAPABILITY_ID_PATTERN.fullmatch(capability):
            add(f"capability_requirements[{index}]", "must be lowercase kebab-case")
    for duplicate in sorted(_duplicates(manifest.capability_requirements)):
        add("capability_requirements", f"contains duplicate capability {duplicate!r}")

    if manifest.routing_policy.execution_policy is not ExecutionPolicy.LOCAL_PREFERRED:
        add("routing_policy.execution_policy", "must be LOCAL_PREFERRED for Cohort 1")
    if manifest.routing_policy.cloud_fallback_allowed:
        add("routing_policy.cloud_fallback_allowed", "must be false for Cohort 1")
    if manifest.audit_events != REQUIRED_AUDIT_EVENTS:
        add("audit_events", "must contain exactly the five required audit events")

    expected_failure = (
        FailureAction.STOP_AND_ESCALATE,
        FailureAction.STOP_AND_ESCALATE,
        FailureAction.PRESERVE_AND_ESCALATE,
        True,
    )
    actual_failure = (
        manifest.failure_behavior.on_validation_failure,
        manifest.failure_behavior.on_missing_authority,
        manifest.failure_behavior.on_dependency_failure,
        manifest.failure_behavior.preserve_working_artifacts,
    )
    if actual_failure != expected_failure:
        add("failure_behavior", "must use the conservative Cohort 1 failure policy")

    if manifest.escalation.destination is not EscalationDestination.ACCOUNTABLE_OWNER:
        add("escalation.destination", "must be ACCOUNTABLE_OWNER")
    if not manifest.escalation.include_evidence:
        add("escalation.include_evidence", "must be true")
    conditions = " ".join(manifest.escalation.conditions).casefold()
    for required in ("authority", "conflict", "classification", "evidence", "uncertainty"):
        if required not in conditions:
            add("escalation.conditions", f"must cover {required}")

    if not manifest.acceptance_criteria:
        add("acceptance_criteria", "must not be empty")
    for duplicate in sorted(_duplicates(item.id for item in manifest.acceptance_criteria)):
        add("acceptance_criteria", f"contains duplicate ID {duplicate!r}")
    for index, criterion in enumerate(manifest.acceptance_criteria):
        if not AGENT_ID_PATTERN.fullmatch(criterion.id):
            add(f"acceptance_criteria[{index}].id", "must be lowercase kebab-case")
        if not criterion.description.strip():
            add(f"acceptance_criteria[{index}].description", "must not be blank")

    for path, text in _string_values(manifest, "manifest"):
        normalized = _normalized(text)
        for token in sorted(PROVIDER_MODEL_DENYLIST):
            if token in normalized:
                add(path, f"contains prohibited provider/model token {token!r}")

    return tuple(sorted(findings, key=lambda item: (item.path, item.message)))
