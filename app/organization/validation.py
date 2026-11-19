import re
from collections import defaultdict
from collections.abc import Sequence
from typing import Protocol

from .errors import ValidationFinding
from .models import (
    AuthorityLevel,
    GrantSubjectType,
    OrganizationRegistry,
    OwnerType,
    SeatType,
)

_CANONICAL_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMANTIC_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
_AUTHORITY_SCOPE = re.compile(r"^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$")
_PROVIDER_TERMS = {
    "anthropic",
    "claude",
    "openai",
    "grok",
    "lmstudio",
    "gemma",
    "nemotron",
}


class _Identified(Protocol):
    id: str


def _validate_ids(
    collection_name: str,
    records: Sequence[_Identified],
    findings: list[ValidationFinding],
) -> None:
    positions: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        positions[record.id].append(index)
        if not _CANONICAL_ID.fullmatch(record.id):
            findings.append(
                ValidationFinding(
                    f"{collection_name}[{index}].id",
                    "must be lowercase kebab-case",
                )
            )
    for record_id, indices in positions.items():
        if len(indices) > 1:
            for index in indices:
                findings.append(
                    ValidationFinding(
                        f"{collection_name}[{index}].id",
                        f"duplicate ID: {record_id}",
                    )
                )


def _contains_provider_term(value: str) -> bool:
    tokens = set(re.findall(r"[a-z0-9]+", value.lower()))
    compact = "".join(re.findall(r"[a-z0-9]+", value.lower()))
    return bool(tokens & _PROVIDER_TERMS) or any(term in compact for term in _PROVIDER_TERMS)


def validate_registry(registry: OrganizationRegistry) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    _validate_ids("roles", registry.roles, findings)
    _validate_ids("seats", registry.seats, findings)
    _validate_ids("agents", registry.agents, findings)
    _validate_ids("authority_grants", registry.authority_grants, findings)

    role_ids = {role.id for role in registry.roles}
    seat_ids = {seat.id for seat in registry.seats}
    agent_ids = {agent.id for agent in registry.agents}

    for index, seat in enumerate(registry.seats):
        if seat.role_id not in role_ids:
            findings.append(
                ValidationFinding(
                    f"seats[{index}].role_id",
                    f"unknown role ID: {seat.role_id}",
                )
            )
        for agent_index, agent_id in enumerate(seat.agent_ids):
            if agent_id not in agent_ids:
                findings.append(
                    ValidationFinding(
                        f"seats[{index}].agent_ids[{agent_index}]",
                        f"unknown agent ID: {agent_id}",
                    )
                )

        human_required = seat.seat_type in (SeatType.HUMAN, SeatType.HYBRID)
        agents_required = seat.seat_type in (SeatType.AI, SeatType.HYBRID)
        has_human_name = bool(seat.human_name and seat.human_name.strip())

        if human_required and not has_human_name:
            findings.append(
                ValidationFinding(
                    f"seats[{index}].human_name",
                    f"{seat.seat_type.value} seat requires a human name",
                )
            )
        if not human_required and seat.human_name is not None:
            findings.append(
                ValidationFinding(
                    f"seats[{index}].human_name",
                    f"{seat.seat_type.value} seat cannot have a human name",
                )
            )
        if agents_required and not seat.agent_ids:
            findings.append(
                ValidationFinding(
                    f"seats[{index}].agent_ids",
                    f"{seat.seat_type.value} seat requires at least one agent",
                )
            )
        if not agents_required and seat.agent_ids:
            findings.append(
                ValidationFinding(
                    f"seats[{index}].agent_ids",
                    f"{seat.seat_type.value} seat cannot have assigned agents",
                )
            )

    for index, agent in enumerate(registry.agents):
        known_owners = role_ids if agent.owner_type is OwnerType.ROLE else seat_ids
        if agent.owner_id not in known_owners:
            findings.append(
                ValidationFinding(
                    f"agents[{index}].owner_id",
                    f"unknown {agent.owner_type.value.lower()} ID: {agent.owner_id}",
                )
            )
        if not _SEMANTIC_VERSION.fullmatch(agent.version):
            findings.append(
                ValidationFinding(
                    f"agents[{index}].version",
                    "must be semantic version x.y.z",
                )
            )
        if _contains_provider_term(agent.id):
            findings.append(
                ValidationFinding(
                    f"agents[{index}].id",
                    "must not encode a provider or model name",
                )
            )
        if _contains_provider_term(agent.display_name):
            findings.append(
                ValidationFinding(
                    f"agents[{index}].display_name",
                    "must not encode a provider or model name",
                )
            )

    for index, grant in enumerate(registry.authority_grants):
        known_subjects = agent_ids if grant.subject_type is GrantSubjectType.AGENT else seat_ids
        if grant.subject_id not in known_subjects:
            findings.append(
                ValidationFinding(
                    f"authority_grants[{index}].subject_id",
                    f"unknown {grant.subject_type.value.lower()} ID: {grant.subject_id}",
                )
            )
        if not _AUTHORITY_SCOPE.fullmatch(grant.scope):
            findings.append(
                ValidationFinding(
                    f"authority_grants[{index}].scope",
                    "must be an explicit lowercase dotted scope without wildcards",
                )
            )
        if (
            grant.subject_type is GrantSubjectType.AGENT
            and grant.level is AuthorityLevel.APPROVE
        ):
            findings.append(
                ValidationFinding(
                    f"authority_grants[{index}].level",
                    "agents cannot receive APPROVE authority",
                )
            )
        if (
            grant.subject_type is GrantSubjectType.AGENT
            and grant.level is AuthorityLevel.EXECUTE
            and not grant.requires_human_approval
        ):
            findings.append(
                ValidationFinding(
                    f"authority_grants[{index}].requires_human_approval",
                    "agent EXECUTE authority requires human approval",
                )
            )

    return tuple(sorted(findings))
