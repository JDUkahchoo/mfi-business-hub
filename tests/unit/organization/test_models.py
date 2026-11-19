from dataclasses import FrozenInstanceError

import pytest

from app.organization.models import (
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
from app.organization.repository import OrganizationRepository


def test_governance_enums_have_exact_values() -> None:
    assert {item.value for item in PillarId} == {
        "infrastructure-supply-chain",
        "technology-gaming-entertainment",
        "investments",
        "incubation",
    }
    assert {item.value for item in SeatType} == {"HUMAN", "AI", "HYBRID", "VACANT"}
    assert {item.value for item in AuthorityLevel} == {
        "READ",
        "WRITE",
        "PROPOSE",
        "APPROVE",
        "EXECUTE",
    }
    assert {item.value for item in AgentStatus} == {
        "PLANNED",
        "DRAFT",
        "TESTING",
        "ACTIVE",
        "SUSPENDED",
        "RETIRED",
    }
    assert {item.value for item in OwnerType} == {"SEAT", "ROLE"}
    assert {item.value for item in GrantSubjectType} == {"SEAT", "AGENT"}


def test_domain_records_are_immutable() -> None:
    role = RoleDefinition(
        id="investments-leadership",
        display_name="Investments Leadership",
        description="Coordinates investment activity.",
        pillar_id=PillarId.INVESTMENTS,
    )
    seat = SeatAssignment(
        id="investments-leadership-seat",
        role_id=role.id,
        seat_type=SeatType.VACANT,
    )
    agent = AgentDefinition(
        id="mfi-investments-lead",
        display_name="MFI Investments Lead",
        purpose="Supports investment planning.",
        status=AgentStatus.PLANNED,
        version="0.1.0",
        owner_type=OwnerType.ROLE,
        owner_id=role.id,
    )
    grant = AuthorityGrant(
        id="investments-read",
        subject_type=GrantSubjectType.AGENT,
        subject_id=agent.id,
        level=AuthorityLevel.READ,
        scope="investments.research",
    )

    for record in (role, seat, agent, grant):
        with pytest.raises(FrozenInstanceError):
            record.id = "changed"  # type: ignore[misc]


def test_registry_collections_are_tuples() -> None:
    registry = OrganizationRegistry(
        roles=(),
        seats=(),
        agents=(),
        authority_grants=(),
    )

    assert isinstance(registry.roles, tuple)
    assert isinstance(registry.seats, tuple)
    assert isinstance(registry.agents, tuple)
    assert isinstance(registry.authority_grants, tuple)


def test_registry_builds_read_only_indexes_and_returns_records_by_id() -> None:
    role = RoleDefinition(
        id="investments-leadership",
        display_name="Investments Leadership",
        description="Coordinates investment activity.",
    )
    seat = SeatAssignment(
        id="investments-leadership-seat",
        role_id=role.id,
        seat_type=SeatType.VACANT,
    )
    agent = AgentDefinition(
        id="mfi-investments-lead",
        display_name="MFI Investments Lead",
        purpose="Supports investment planning.",
        status=AgentStatus.PLANNED,
        version="0.1.0",
        owner_type=OwnerType.ROLE,
        owner_id=role.id,
    )
    registry = OrganizationRegistry(
        roles=(role,),
        seats=(seat,),
        agents=(agent,),
        authority_grants=(),
    )

    assert registry.get_role(role.id) is role
    assert registry.get_seat(seat.id) is seat
    assert registry.get_agent(agent.id) is agent
    assert registry.get_role("missing") is None
    assert registry.get_seat("missing") is None
    assert registry.get_agent("missing") is None

    with pytest.raises(TypeError):
        registry.role_index[role.id] = role  # type: ignore[index]
    with pytest.raises(TypeError):
        registry.seat_index[seat.id] = seat  # type: ignore[index]
    with pytest.raises(TypeError):
        registry.agent_index[agent.id] = agent  # type: ignore[index]


def test_repository_protocol_accepts_load_implementation() -> None:
    registry = OrganizationRegistry(roles=(), seats=(), agents=(), authority_grants=())

    class InMemoryRepository:
        def load(self) -> OrganizationRegistry:
            return registry

    repository = InMemoryRepository()

    assert isinstance(repository, OrganizationRepository)
    assert repository.load() is registry
