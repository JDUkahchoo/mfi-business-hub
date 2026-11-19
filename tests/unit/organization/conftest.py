import pytest

from app.organization.models import (
    AgentDefinition,
    AgentStatus,
    OrganizationRegistry,
    OwnerType,
    PillarId,
    RoleDefinition,
    SeatAssignment,
    SeatType,
)


@pytest.fixture
def valid_registry() -> OrganizationRegistry:
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
    return OrganizationRegistry(
        roles=(role,),
        seats=(seat,),
        agents=(agent,),
        authority_grants=(),
    )
