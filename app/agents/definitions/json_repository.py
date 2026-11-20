from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, TypeVar

from .errors import DefinitionFinding, DefinitionValidationError
from .models import (
    AcceptanceCriterion,
    AgentManifest,
    ApprovalRequirement,
    ApproverType,
    ContractSpec,
    DataClassification,
    EscalationDestination,
    EscalationPolicy,
    EvidenceType,
    ExecutionPolicy,
    FailureAction,
    FailureBehavior,
    RoutingPolicy,
)
from .policy import COHORT_1_AGENT_IDS
from .validation import validate_manifest


_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version", "agent_id", "responsibilities", "non_responsibilities",
        "input_contracts", "output_contracts", "allowed_tools", "allowed_systems",
        "allowed_data_classifications", "authority_grant_ids", "approval_requirements",
        "prompt_sources", "capability_requirements", "routing_policy", "audit_events",
        "failure_behavior", "escalation", "acceptance_criteria",
    }
)
_EnumT = TypeVar("_EnumT")


def parse_manifest_data(data: object, source: str) -> AgentManifest:
    findings: list[DefinitionFinding] = []

    def finding(path: str, message: str) -> None:
        findings.append(DefinitionFinding(path, message))

    def object_value(value: object, path: str, required: frozenset[str]) -> dict[str, object]:
        if type(value) is not dict:
            finding(path, "must be an object")
            return {}
        result = value
        for name in sorted(required - result.keys()):
            finding(f"{path}.{name}", "is required")
        for name in sorted(result.keys() - required):
            finding(f"{path}.{name}", "is not allowed")
        return result

    def string_value(value: object, path: str) -> str:
        if type(value) is not str:
            finding(path, "must be a string")
            return ""
        return value

    def bool_value(value: object, path: str) -> bool:
        if type(value) is not bool:
            finding(path, "must be a boolean")
            return False
        return value

    def string_list(value: object, path: str) -> tuple[str, ...]:
        if type(value) is not list:
            finding(path, "must be a list")
            return ()
        return tuple(string_value(item, f"{path}[{index}]") for index, item in enumerate(value))

    def enum_value(value: object, path: str, enum_type: Callable[[str], _EnumT]) -> _EnumT | None:
        raw = string_value(value, path)
        if not raw:
            if type(value) is str:
                finding(path, "must not be empty")
            return None
        try:
            return enum_type(raw)
        except ValueError:
            finding(path, f"has unsupported value {raw!r}")
            return None

    root = object_value(data, source, _TOP_LEVEL_FIELDS)
    schema_version = root.get("schema_version")
    if type(schema_version) is not int:
        finding(f"{source}.schema_version", "must be an integer")
    elif schema_version != 1:
        finding(f"{source}.schema_version", "must equal 1")
    agent_id = string_value(root.get("agent_id"), f"{source}.agent_id")

    def contracts(name: str) -> tuple[ContractSpec, ...]:
        path = f"{source}.{name}"
        value = root.get(name)
        if type(value) is not list:
            finding(path, "must be a list")
            return ()
        records: list[ContractSpec] = []
        keys = frozenset({"id", "description", "required_fields"})
        for index, item in enumerate(value):
            item_path = f"{path}[{index}]"
            record = object_value(item, item_path, keys)
            records.append(ContractSpec(
                id=string_value(record.get("id"), f"{item_path}.id"),
                description=string_value(record.get("description"), f"{item_path}.description"),
                required_fields=string_list(record.get("required_fields"), f"{item_path}.required_fields"),
            ))
        return tuple(records)

    classifications: list[DataClassification] = []
    raw_classifications = root.get("allowed_data_classifications")
    if type(raw_classifications) is not list:
        finding(f"{source}.allowed_data_classifications", "must be a list")
    else:
        for index, item in enumerate(raw_classifications):
            parsed = enum_value(item, f"{source}.allowed_data_classifications[{index}]", DataClassification)
            if parsed is not None:
                classifications.append(parsed)

    def approvals() -> tuple[ApprovalRequirement, ...]:
        path = f"{source}.approval_requirements"
        value = root.get("approval_requirements")
        if type(value) is not list:
            finding(path, "must be a list")
            return ()
        records: list[ApprovalRequirement] = []
        keys = frozenset({"id", "trigger", "approver"})
        for index, item in enumerate(value):
            item_path = f"{path}[{index}]"
            record = object_value(item, item_path, keys)
            records.append(ApprovalRequirement(
                id=string_value(record.get("id"), f"{item_path}.id"),
                trigger=string_value(record.get("trigger"), f"{item_path}.trigger"),
                approver=enum_value(record.get("approver"), f"{item_path}.approver", ApproverType),  # type: ignore[arg-type]
            ))
        return tuple(records)

    routing_data = object_value(root.get("routing_policy"), f"{source}.routing_policy", frozenset({"execution_policy", "cloud_fallback_allowed"}))
    routing = RoutingPolicy(
        execution_policy=enum_value(routing_data.get("execution_policy"), f"{source}.routing_policy.execution_policy", ExecutionPolicy),  # type: ignore[arg-type]
        cloud_fallback_allowed=bool_value(routing_data.get("cloud_fallback_allowed"), f"{source}.routing_policy.cloud_fallback_allowed"),
    )
    failure_data = object_value(root.get("failure_behavior"), f"{source}.failure_behavior", frozenset({"on_validation_failure", "on_missing_authority", "on_dependency_failure", "preserve_working_artifacts"}))
    failure = FailureBehavior(
        on_validation_failure=enum_value(failure_data.get("on_validation_failure"), f"{source}.failure_behavior.on_validation_failure", FailureAction),  # type: ignore[arg-type]
        on_missing_authority=enum_value(failure_data.get("on_missing_authority"), f"{source}.failure_behavior.on_missing_authority", FailureAction),  # type: ignore[arg-type]
        on_dependency_failure=enum_value(failure_data.get("on_dependency_failure"), f"{source}.failure_behavior.on_dependency_failure", FailureAction),  # type: ignore[arg-type]
        preserve_working_artifacts=bool_value(failure_data.get("preserve_working_artifacts"), f"{source}.failure_behavior.preserve_working_artifacts"),
    )
    escalation_data = object_value(root.get("escalation"), f"{source}.escalation", frozenset({"destination", "include_evidence", "conditions"}))
    escalation = EscalationPolicy(
        destination=enum_value(escalation_data.get("destination"), f"{source}.escalation.destination", EscalationDestination),  # type: ignore[arg-type]
        include_evidence=bool_value(escalation_data.get("include_evidence"), f"{source}.escalation.include_evidence"),
        conditions=string_list(escalation_data.get("conditions"), f"{source}.escalation.conditions"),
    )

    criteria_value = root.get("acceptance_criteria")
    criteria: list[AcceptanceCriterion] = []
    criteria_path = f"{source}.acceptance_criteria"
    if type(criteria_value) is not list:
        finding(criteria_path, "must be a list")
    else:
        keys = frozenset({"id", "description", "evidence_type"})
        for index, item in enumerate(criteria_value):
            item_path = f"{criteria_path}[{index}]"
            record = object_value(item, item_path, keys)
            criteria.append(AcceptanceCriterion(
                id=string_value(record.get("id"), f"{item_path}.id"),
                description=string_value(record.get("description"), f"{item_path}.description"),
                evidence_type=enum_value(record.get("evidence_type"), f"{item_path}.evidence_type", EvidenceType),  # type: ignore[arg-type]
            ))

    manifest = AgentManifest(
        schema_version=schema_version if type(schema_version) is int else 0,
        agent_id=agent_id,
        responsibilities=string_list(root.get("responsibilities"), f"{source}.responsibilities"),
        non_responsibilities=string_list(root.get("non_responsibilities"), f"{source}.non_responsibilities"),
        input_contracts=contracts("input_contracts"),
        output_contracts=contracts("output_contracts"),
        allowed_tools=string_list(root.get("allowed_tools"), f"{source}.allowed_tools"),
        allowed_systems=string_list(root.get("allowed_systems"), f"{source}.allowed_systems"),
        allowed_data_classifications=tuple(classifications),
        authority_grant_ids=string_list(root.get("authority_grant_ids"), f"{source}.authority_grant_ids"),
        approval_requirements=approvals(),
        prompt_sources=string_list(root.get("prompt_sources"), f"{source}.prompt_sources"),
        capability_requirements=string_list(root.get("capability_requirements"), f"{source}.capability_requirements"),
        routing_policy=routing,
        audit_events=string_list(root.get("audit_events"), f"{source}.audit_events"),
        failure_behavior=failure,
        escalation=escalation,
        acceptance_criteria=tuple(criteria),
    )
    if findings:
        raise DefinitionValidationError(findings)
    return manifest


class JsonAgentManifestRepository:
    def __init__(self, directory: Path, expected_agent_ids: frozenset[str] = COHORT_1_AGENT_IDS) -> None:
        self._directory = directory
        self._expected_agent_ids = expected_agent_ids

    def load_all(self) -> tuple[AgentManifest, ...]:
        if not self._directory.exists():
            raise DefinitionValidationError(
                (DefinitionFinding(str(self._directory), "directory does not exist"),)
            )
        if not self._directory.is_dir():
            raise DefinitionValidationError(
                (DefinitionFinding(str(self._directory), "must be a directory"),)
            )

        findings: list[DefinitionFinding] = []
        parsed_manifests: list[tuple[str, AgentManifest]] = []
        try:
            entries = sorted(self._directory.iterdir(), key=lambda item: item.name)
        except OSError as exc:
            raise DefinitionValidationError(
                (DefinitionFinding(str(self._directory), f"cannot read directory: {exc}"),)
            ) from exc

        json_files: list[Path] = []
        for entry in entries:
            if (
                not entry.is_file()
                or entry.suffix != ".json"
                or entry.name.startswith(".")
            ):
                findings.append(
                    DefinitionFinding(entry.name, "unexpected directory entry")
                )
            else:
                json_files.append(entry)

        for path in json_files:
            try:
                text = path.read_bytes().decode("utf-8")
            except UnicodeDecodeError as exc:
                findings.append(
                    DefinitionFinding(path.name, f"must contain valid UTF-8: {exc}")
                )
                continue
            except OSError as exc:
                findings.append(DefinitionFinding(path.name, f"cannot read file: {exc}"))
                continue

            try:
                data = json.loads(text, object_pairs_hook=_reject_duplicate_members)
            except _DuplicateMemberError as exc:
                findings.append(
                    DefinitionFinding(path.name, f"duplicate JSON member {exc.member!r}")
                )
                continue
            except json.JSONDecodeError as exc:
                findings.append(
                    DefinitionFinding(
                        path.name,
                        f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
                    )
                )
                continue

            try:
                manifest = parse_manifest_data(data, path.name)
            except DefinitionValidationError as exc:
                findings.extend(exc.findings)
                continue

            expected_filename = f"{manifest.agent_id}.json"
            if path.name != expected_filename or path.name != path.name.casefold():
                findings.append(
                    DefinitionFinding(
                        path.name,
                        f"filename must equal {expected_filename!r} exactly",
                    )
                )
            for semantic in validate_manifest(manifest):
                findings.append(
                    DefinitionFinding(f"{path.name}.{semantic.path}", semantic.message)
                )
            parsed_manifests.append((path.name, manifest))

        by_id: dict[str, list[str]] = {}
        for source_name, manifest in parsed_manifests:
            by_id.setdefault(manifest.agent_id, []).append(source_name)
        for agent_id, sources in sorted(by_id.items()):
            if len(sources) > 1:
                findings.append(
                    DefinitionFinding(
                        "agent_id",
                        f"duplicate agent ID {agent_id!r} in {', '.join(sources)}",
                    )
                )

        actual_ids = frozenset(manifest.agent_id for _, manifest in parsed_manifests)
        for agent_id in sorted(self._expected_agent_ids - actual_ids):
            findings.append(
                DefinitionFinding("agent_id", f"missing expected agent ID {agent_id!r}")
            )
        for agent_id in sorted(actual_ids - self._expected_agent_ids):
            findings.append(
                DefinitionFinding("agent_id", f"unexpected agent ID {agent_id!r}")
            )

        if findings:
            raise DefinitionValidationError(findings)
        return tuple(
            sorted(
                (manifest for _, manifest in parsed_manifests),
                key=lambda item: item.agent_id,
            )
        )


class _DuplicateMemberError(ValueError):
    def __init__(self, member: str) -> None:
        self.member = member
        super().__init__(member)


def _reject_duplicate_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateMemberError(key)
        result[key] = value
    return result
