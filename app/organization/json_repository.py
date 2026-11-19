from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .errors import RegistryLoadError, RegistryValidationError, ValidationFinding
from .models import (
    AgentDefinition,
    AgentStatus,
    AuthorityGrant,
    AuthorityLevel,
    GrantSubjectType,
    OrganizationRegistry,
    OwnerType,
    PillarId,
    RoleDefinition,
    SeatAssignment,
    SeatType,
)
from .validation import validate_registry

_TOP_LEVEL_KEYS = {
    "schema_version",
    "roles",
    "seats",
    "agents",
    "authority_grants",
}


def _finding(findings: list[ValidationFinding], path: str, message: str) -> None:
    findings.append(ValidationFinding(path, message))


def _as_record(
    value: object,
    path: str,
    required: set[str],
    optional: set[str],
    findings: list[ValidationFinding],
) -> Mapping[str, object] | None:
    if not isinstance(value, dict):
        _finding(findings, path, "must be an object")
        return None
    for key in sorted(required - value.keys()):
        _finding(findings, f"{path}.{key}", "is required")
    for key in sorted(value.keys() - required - optional):
        _finding(findings, f"{path}.{key}", "is not allowed")
    if required - value.keys() or value.keys() - required - optional:
        return None
    return value


def _string(
    record: Mapping[str, object],
    key: str,
    path: str,
    findings: list[ValidationFinding],
) -> str | None:
    value = record[key]
    if not isinstance(value, str):
        _finding(findings, f"{path}.{key}", "must be a string")
        return None
    return value


def _optional_string(
    record: Mapping[str, object],
    key: str,
    path: str,
    findings: list[ValidationFinding],
) -> str | None:
    value = record.get(key)
    if value is not None and not isinstance(value, str):
        _finding(findings, f"{path}.{key}", "must be a string or null")
        return None
    return value


def _enum_value(
    enum_type: type[Any],
    value: str | None,
    field_path: str,
    findings: list[ValidationFinding],
) -> Any | None:
    if value is None:
        return None
    try:
        return enum_type(value)
    except ValueError:
        allowed = ", ".join(item.value for item in enum_type)
        _finding(findings, field_path, f"must be one of: {allowed}")
        return None


def _record_list(
    data: Mapping[str, object],
    key: str,
    findings: list[ValidationFinding],
) -> list[object]:
    value = data.get(key)
    if not isinstance(value, list):
        if key in data:
            _finding(findings, key, "must be a list")
        return []
    return value


def _parse_roles(values: list[object], findings: list[ValidationFinding]) -> list[RoleDefinition]:
    roles: list[RoleDefinition] = []
    for index, value in enumerate(values):
        path = f"roles[{index}]"
        before = len(findings)
        record = _as_record(
            value,
            path,
            {"id", "display_name", "description"},
            {"pillar_id"},
            findings,
        )
        if record is None:
            continue
        role_id = _string(record, "id", path, findings)
        display_name = _string(record, "display_name", path, findings)
        description = _string(record, "description", path, findings)
        raw_pillar = _optional_string(record, "pillar_id", path, findings)
        pillar_id = _enum_value(PillarId, raw_pillar, f"{path}.pillar_id", findings)
        if len(findings) == before:
            roles.append(RoleDefinition(role_id, display_name, description, pillar_id))  # type: ignore[arg-type]
    return roles


def _parse_seats(values: list[object], findings: list[ValidationFinding]) -> list[SeatAssignment]:
    seats: list[SeatAssignment] = []
    for index, value in enumerate(values):
        path = f"seats[{index}]"
        before = len(findings)
        record = _as_record(
            value,
            path,
            {"id", "role_id", "seat_type"},
            {"human_name", "agent_ids"},
            findings,
        )
        if record is None:
            continue
        seat_id = _string(record, "id", path, findings)
        role_id = _string(record, "role_id", path, findings)
        raw_type = _string(record, "seat_type", path, findings)
        seat_type = _enum_value(SeatType, raw_type, f"{path}.seat_type", findings)
        human_name = _optional_string(record, "human_name", path, findings)
        raw_agents = record.get("agent_ids", [])
        agent_ids: tuple[str, ...] = ()
        if not isinstance(raw_agents, list):
            _finding(findings, f"{path}.agent_ids", "must be a list")
        elif not all(isinstance(agent_id, str) for agent_id in raw_agents):
            _finding(findings, f"{path}.agent_ids", "must contain only strings")
        else:
            agent_ids = tuple(raw_agents)
        if len(findings) == before:
            seats.append(
                SeatAssignment(
                    seat_id,  # type: ignore[arg-type]
                    role_id,  # type: ignore[arg-type]
                    seat_type,
                    human_name,
                    agent_ids,
                )
            )
    return seats


def _parse_agents(values: list[object], findings: list[ValidationFinding]) -> list[AgentDefinition]:
    agents: list[AgentDefinition] = []
    required = {
        "id",
        "display_name",
        "purpose",
        "status",
        "version",
        "owner_type",
        "owner_id",
    }
    for index, value in enumerate(values):
        path = f"agents[{index}]"
        before = len(findings)
        record = _as_record(value, path, required, set(), findings)
        if record is None:
            continue
        agent_id = _string(record, "id", path, findings)
        display_name = _string(record, "display_name", path, findings)
        purpose = _string(record, "purpose", path, findings)
        raw_status = _string(record, "status", path, findings)
        status = _enum_value(AgentStatus, raw_status, f"{path}.status", findings)
        version = _string(record, "version", path, findings)
        raw_owner_type = _string(record, "owner_type", path, findings)
        owner_type = _enum_value(OwnerType, raw_owner_type, f"{path}.owner_type", findings)
        owner_id = _string(record, "owner_id", path, findings)
        if len(findings) == before:
            agents.append(
                AgentDefinition(
                    agent_id,  # type: ignore[arg-type]
                    display_name,  # type: ignore[arg-type]
                    purpose,  # type: ignore[arg-type]
                    status,
                    version,  # type: ignore[arg-type]
                    owner_type,
                    owner_id,  # type: ignore[arg-type]
                )
            )
    return agents


def _parse_grants(values: list[object], findings: list[ValidationFinding]) -> list[AuthorityGrant]:
    grants: list[AuthorityGrant] = []
    required = {"id", "subject_type", "subject_id", "level", "scope"}
    for index, value in enumerate(values):
        path = f"authority_grants[{index}]"
        before = len(findings)
        record = _as_record(value, path, required, {"requires_human_approval"}, findings)
        if record is None:
            continue
        grant_id = _string(record, "id", path, findings)
        raw_subject_type = _string(record, "subject_type", path, findings)
        subject_type = _enum_value(
            GrantSubjectType,
            raw_subject_type,
            f"{path}.subject_type",
            findings,
        )
        subject_id = _string(record, "subject_id", path, findings)
        raw_level = _string(record, "level", path, findings)
        level = _enum_value(AuthorityLevel, raw_level, f"{path}.level", findings)
        scope = _string(record, "scope", path, findings)
        requires_human_approval = record.get("requires_human_approval", False)
        if type(requires_human_approval) is not bool:
            _finding(findings, f"{path}.requires_human_approval", "must be a boolean")
        if len(findings) == before:
            grants.append(
                AuthorityGrant(
                    grant_id,  # type: ignore[arg-type]
                    subject_type,
                    subject_id,  # type: ignore[arg-type]
                    level,
                    scope,  # type: ignore[arg-type]
                    requires_human_approval,
                )
            )
    return grants


def parse_registry_data(data: object) -> OrganizationRegistry:
    findings: list[ValidationFinding] = []
    if not isinstance(data, dict):
        raise RegistryValidationError((ValidationFinding("$", "must be an object"),))

    for key in sorted(_TOP_LEVEL_KEYS - data.keys()):
        _finding(findings, key, "is required")
    for key in sorted(data.keys() - _TOP_LEVEL_KEYS):
        _finding(findings, key, "is not allowed")

    schema_version = data.get("schema_version")
    if type(schema_version) is not int:
        if "schema_version" in data:
            _finding(findings, "schema_version", "must be an integer")
    elif schema_version != 1:
        _finding(findings, "schema_version", "unsupported version; expected 1")

    roles = _parse_roles(_record_list(data, "roles", findings), findings)
    seats = _parse_seats(_record_list(data, "seats", findings), findings)
    agents = _parse_agents(_record_list(data, "agents", findings), findings)
    grants = _parse_grants(_record_list(data, "authority_grants", findings), findings)

    if findings:
        raise RegistryValidationError(findings)

    registry = OrganizationRegistry(tuple(roles), tuple(seats), tuple(agents), tuple(grants))
    semantic_findings = validate_registry(registry)
    if semantic_findings:
        raise RegistryValidationError(semantic_findings)
    return registry


class JsonOrganizationRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> OrganizationRegistry:
        try:
            text = self.path.read_text(encoding="utf-8")
        except UnicodeError as error:
            raise RegistryLoadError(
                f"cannot decode registry as UTF-8: {self.path}: {error}"
            ) from error
        except OSError as error:
            raise RegistryLoadError(f"cannot read registry: {self.path}: {error}") from error

        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise RegistryLoadError(
                f"malformed JSON in {self.path}: line {error.lineno}, "
                f"column {error.colno}: {error.msg}"
            ) from error
        return parse_registry_data(data)
