from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Protocol, TypeVar


class _Identified(Protocol):
    id: str


_Record = TypeVar("_Record", bound=_Identified)


def _unique_index(records: tuple[_Record, ...], label: str) -> Mapping[str, _Record]:
    index: dict[str, _Record] = {}
    for record in records:
        if record.id in index:
            raise ValueError(f"duplicate {label} ID: {record.id}")
        index[record.id] = record
    return MappingProxyType(index)


class PillarId(str, Enum):
    INFRASTRUCTURE_SUPPLY_CHAIN = "infrastructure-supply-chain"
    TECHNOLOGY_GAMING_ENTERTAINMENT = "technology-gaming-entertainment"
    INVESTMENTS = "investments"
    INCUBATION = "incubation"


class SeatType(str, Enum):
    HUMAN = "HUMAN"
    AI = "AI"
    HYBRID = "HYBRID"
    VACANT = "VACANT"


class AuthorityLevel(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    PROPOSE = "PROPOSE"
    APPROVE = "APPROVE"
    EXECUTE = "EXECUTE"


class AgentStatus(str, Enum):
    PLANNED = "PLANNED"
    DRAFT = "DRAFT"
    TESTING = "TESTING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class OwnerType(str, Enum):
    SEAT = "SEAT"
    ROLE = "ROLE"


class GrantSubjectType(str, Enum):
    SEAT = "SEAT"
    AGENT = "AGENT"


@dataclass(frozen=True, slots=True)
class RoleDefinition:
    id: str
    display_name: str
    description: str
    pillar_id: PillarId | None = None


@dataclass(frozen=True, slots=True)
class SeatAssignment:
    id: str
    role_id: str
    seat_type: SeatType
    human_name: str | None = None
    agent_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    id: str
    display_name: str
    purpose: str
    status: AgentStatus
    version: str
    owner_type: OwnerType
    owner_id: str


@dataclass(frozen=True, slots=True)
class AuthorityGrant:
    id: str
    subject_type: GrantSubjectType
    subject_id: str
    level: AuthorityLevel
    scope: str
    requires_human_approval: bool = False


@dataclass(frozen=True, slots=True)
class OrganizationRegistry:
    roles: tuple[RoleDefinition, ...]
    seats: tuple[SeatAssignment, ...]
    agents: tuple[AgentDefinition, ...]
    authority_grants: tuple[AuthorityGrant, ...]
    _role_index: Mapping[str, RoleDefinition] = field(init=False, repr=False, compare=False)
    _seat_index: Mapping[str, SeatAssignment] = field(init=False, repr=False, compare=False)
    _agent_index: Mapping[str, AgentDefinition] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_role_index",
            _unique_index(self.roles, "roles"),
        )
        object.__setattr__(
            self,
            "_seat_index",
            _unique_index(self.seats, "seats"),
        )
        object.__setattr__(
            self,
            "_agent_index",
            _unique_index(self.agents, "agents"),
        )
        _unique_index(self.authority_grants, "authority_grants")

    @property
    def role_index(self) -> Mapping[str, RoleDefinition]:
        return self._role_index

    @property
    def seat_index(self) -> Mapping[str, SeatAssignment]:
        return self._seat_index

    @property
    def agent_index(self) -> Mapping[str, AgentDefinition]:
        return self._agent_index

    def get_role(self, role_id: str) -> RoleDefinition | None:
        return self._role_index.get(role_id)

    def get_seat(self, seat_id: str) -> SeatAssignment | None:
        return self._seat_index.get(seat_id)

    def get_agent(self, agent_id: str) -> AgentDefinition | None:
        return self._agent_index.get(agent_id)
