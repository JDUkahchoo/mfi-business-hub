from pathlib import Path
import re

from app.organization.json_repository import JsonOrganizationRepository
from app.organization.models import AgentStatus, OwnerType, PillarId, SeatType

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "config" / "organization" / "registry.json"
CATALOG_PATH = REPO_ROOT / "docs" / "governance" / "AGENT_REGISTRY.md"

EXPECTED_AGENT_IDS = {
    "mfi-orchestrator",
    "mfi-qa-auditor",
    "mfi-infrastructure-lead",
    "mfi-tech-entertainment-lead",
    "mfi-investments-lead",
    "mfi-incubation-lead",
    "mfi-business-development-lead",
    "mfi-government-business-lead",
    "mfi-private-sector-lead",
    "mfi-cfo-copilot",
    "mfi-coo-copilot",
    "mfi-cto-copilot",
}

EXPECTED_AGENT_ROLES = {
    "mfi-orchestrator": "enterprise-orchestration",
    "mfi-qa-auditor": "quality-assurance",
    "mfi-infrastructure-lead": "infrastructure-leadership",
    "mfi-tech-entertainment-lead": "technology-gaming-entertainment-leadership",
    "mfi-investments-lead": "investments-leadership",
    "mfi-incubation-lead": "incubation-leadership",
    "mfi-business-development-lead": "business-development-leadership",
    "mfi-government-business-lead": "government-business-leadership",
    "mfi-private-sector-lead": "private-sector-leadership",
    "mfi-cfo-copilot": "finance-leadership",
    "mfi-coo-copilot": "operations-leadership",
    "mfi-cto-copilot": "technology-leadership",
}

EXPECTED_SEAT_ROLES = {
    f"{role_id}-seat": role_id for role_id in EXPECTED_AGENT_ROLES.values()
}


def _catalog_agent_statuses() -> dict[str, str]:
    row = re.compile(
        r"^\| `(?P<id>mfi-[^`]+)` \|.*\| `(?P<status>PLANNED|DRAFT|TESTING|ACTIVE|SUSPENDED|RETIRED)` \|$",
        re.MULTILINE,
    )
    return {
        match.group("id"): match.group("status")
        for match in row.finditer(CATALOG_PATH.read_text(encoding="utf-8"))
    }


def test_committed_seed_registry_matches_approved_organization() -> None:
    registry = JsonOrganizationRepository(REGISTRY_PATH).load()

    assert len(registry.roles) == 12
    assert len(registry.seats) == 12
    assert len(registry.agents) == 12
    assert registry.authority_grants == ()

    pillar_roles = {
        role.id: role.pillar_id for role in registry.roles if role.pillar_id is not None
    }
    assert pillar_roles == {
        "infrastructure-leadership": PillarId.INFRASTRUCTURE_SUPPLY_CHAIN,
        "technology-gaming-entertainment-leadership": (
            PillarId.TECHNOLOGY_GAMING_ENTERTAINMENT
        ),
        "investments-leadership": PillarId.INVESTMENTS,
        "incubation-leadership": PillarId.INCUBATION,
    }

    for seat in registry.seats:
        assert seat.seat_type is SeatType.VACANT
        assert seat.human_name is None
        assert seat.agent_ids == ()

    assert {agent.id for agent in registry.agents} == EXPECTED_AGENT_IDS
    assert {agent.id: agent.owner_id for agent in registry.agents} == EXPECTED_AGENT_ROLES
    assert {seat.id: seat.role_id for seat in registry.seats} == EXPECTED_SEAT_ROLES
    assert _catalog_agent_statuses() == {
        agent.id: agent.status.value for agent in registry.agents
    }
    for agent in registry.agents:
        assert agent.status is AgentStatus.PLANNED
        assert agent.version == "0.1.0"
        assert agent.owner_type is OwnerType.ROLE
        assert registry.get_role(agent.owner_id) is not None
