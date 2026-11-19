from dataclasses import replace
from types import SimpleNamespace
import pytest

from app.organization.errors import (
    RegistryError,
    RegistryLoadError,
    RegistryValidationError,
    ValidationFinding,
)
from app.organization.models import (
    AuthorityGrant,
    AuthorityLevel,
    GrantSubjectType,
    OrganizationRegistry,
    OwnerType,
    SeatType,
)
from app.organization.validation import validate_registry


def test_validation_finding_formats_path_and_message() -> None:
    finding = ValidationFinding("agents[0].id", "must be lowercase kebab-case")

    assert str(finding) == "agents[0].id: must be lowercase kebab-case"


def test_registry_validation_error_sorts_and_exposes_findings() -> None:
    findings = (
        ValidationFinding("seats[0].id", "invalid seat"),
        ValidationFinding("agents[0].id", "invalid agent"),
    )

    error = RegistryValidationError(findings)

    assert error.findings == tuple(sorted(findings))
    assert str(error) == "agents[0].id: invalid agent\nseats[0].id: invalid seat"


def test_registry_load_error_is_a_registry_error() -> None:
    assert isinstance(RegistryLoadError("cannot read registry"), RegistryError)


def test_rejects_seat_with_missing_role(valid_registry: OrganizationRegistry) -> None:
    seat = replace(valid_registry.seats[0], role_id="missing-role")
    registry = replace(valid_registry, seats=(seat,))

    findings = validate_registry(registry)

    assert "seats[0].role_id" in [finding.path for finding in findings]
    assert any("missing-role" in finding.message for finding in findings)


def test_rejects_seat_with_missing_assigned_agent(valid_registry: OrganizationRegistry) -> None:
    seat = replace(
        valid_registry.seats[0],
        seat_type=SeatType.AI,
        agent_ids=("missing-agent",),
    )
    registry = replace(valid_registry, seats=(seat,))

    findings = validate_registry(registry)

    assert "seats[0].agent_ids[0]" in [finding.path for finding in findings]
    assert any("missing-agent" in finding.message for finding in findings)


@pytest.mark.parametrize(
    ("owner_type", "owner_id", "expected_path"),
    [
        (OwnerType.ROLE, "missing-role", "agents[0].owner_id"),
        (OwnerType.SEAT, "missing-seat", "agents[0].owner_id"),
    ],
)
def test_rejects_agent_with_missing_owner(
    valid_registry: OrganizationRegistry,
    owner_type: OwnerType,
    owner_id: str,
    expected_path: str,
) -> None:
    agent = replace(valid_registry.agents[0], owner_type=owner_type, owner_id=owner_id)
    registry = replace(valid_registry, agents=(agent,))

    findings = validate_registry(registry)

    assert expected_path in [finding.path for finding in findings]
    assert any(owner_id in finding.message for finding in findings)


@pytest.mark.parametrize(
    ("subject_type", "subject_id"),
    [
        (GrantSubjectType.AGENT, "missing-agent"),
        (GrantSubjectType.SEAT, "missing-seat"),
    ],
)
def test_rejects_grant_with_missing_subject(
    valid_registry: OrganizationRegistry,
    subject_type: GrantSubjectType,
    subject_id: str,
) -> None:
    grant = AuthorityGrant(
        id="research-read",
        subject_type=subject_type,
        subject_id=subject_id,
        level=AuthorityLevel.READ,
        scope="research.documents",
    )
    registry = replace(valid_registry, authority_grants=(grant,))

    findings = validate_registry(registry)

    assert "authority_grants[0].subject_id" in [finding.path for finding in findings]
    assert any(subject_id in finding.message for finding in findings)


@pytest.mark.parametrize(
    ("seat_type", "human_name", "agent_ids", "expected_field"),
    [
        (SeatType.HUMAN, None, (), "human_name"),
        (SeatType.HUMAN, "Joshua", ("mfi-investments-lead",), "agent_ids"),
        (SeatType.AI, "Joshua", ("mfi-investments-lead",), "human_name"),
        (SeatType.AI, None, (), "agent_ids"),
        (SeatType.HYBRID, "  ", ("mfi-investments-lead",), "human_name"),
        (SeatType.HYBRID, "Joshua", (), "agent_ids"),
        (SeatType.VACANT, "Joshua", (), "human_name"),
        (SeatType.VACANT, None, ("mfi-investments-lead",), "agent_ids"),
    ],
)
def test_rejects_invalid_seat_content(
    valid_registry: OrganizationRegistry,
    seat_type: SeatType,
    human_name: str | None,
    agent_ids: tuple[str, ...],
    expected_field: str,
) -> None:
    seat = replace(
        valid_registry.seats[0],
        seat_type=seat_type,
        human_name=human_name,
        agent_ids=agent_ids,
    )
    registry = replace(valid_registry, seats=(seat,))

    paths = [finding.path for finding in validate_registry(registry)]

    assert f"seats[0].{expected_field}" in paths


@pytest.mark.parametrize(
    ("seat_type", "human_name", "agent_ids"),
    [
        (SeatType.HUMAN, "Joshua", ()),
        (SeatType.AI, None, ("mfi-investments-lead",)),
        (SeatType.HYBRID, "Joshua", ("mfi-investments-lead",)),
        (SeatType.VACANT, None, ()),
    ],
)
def test_accepts_valid_seat_content(
    valid_registry: OrganizationRegistry,
    seat_type: SeatType,
    human_name: str | None,
    agent_ids: tuple[str, ...],
) -> None:
    seat = replace(
        valid_registry.seats[0],
        seat_type=seat_type,
        human_name=human_name,
        agent_ids=agent_ids,
    )
    registry = replace(valid_registry, seats=(seat,))

    paths = [finding.path for finding in validate_registry(registry)]

    assert "seats[0].human_name" not in paths
    assert "seats[0].agent_ids" not in paths


@pytest.mark.parametrize("collection_name", ["roles", "seats", "agents", "authority_grants"])
def test_rejects_malformed_canonical_ids(
    valid_registry: OrganizationRegistry,
    collection_name: str,
) -> None:
    if collection_name == "authority_grants":
        record = AuthorityGrant(
            id="Bad Grant",
            subject_type=GrantSubjectType.AGENT,
            subject_id=valid_registry.agents[0].id,
            level=AuthorityLevel.READ,
            scope="research.documents",
        )
    else:
        record = replace(getattr(valid_registry, collection_name)[0], id="Bad ID")
    registry = replace(valid_registry, **{collection_name: (record,)})

    paths = [finding.path for finding in validate_registry(registry)]

    assert f"{collection_name}[0].id" in paths


@pytest.mark.parametrize("collection_name", ["roles", "seats", "agents", "authority_grants"])
def test_rejects_duplicate_ids(
    valid_registry: OrganizationRegistry,
    collection_name: str,
) -> None:
    if collection_name == "authority_grants":
        first = AuthorityGrant(
            id="research-read",
            subject_type=GrantSubjectType.AGENT,
            subject_id=valid_registry.agents[0].id,
            level=AuthorityLevel.READ,
            scope="research.documents",
        )
    else:
        first = getattr(valid_registry, collection_name)[0]
    collections = {
        "roles": valid_registry.roles,
        "seats": valid_registry.seats,
        "agents": valid_registry.agents,
        "authority_grants": valid_registry.authority_grants,
    }
    collections[collection_name] = (first, first)
    registry = SimpleNamespace(**collections)

    paths = [finding.path for finding in validate_registry(registry)]  # type: ignore[arg-type]

    assert f"{collection_name}[0].id" in paths
    assert f"{collection_name}[1].id" in paths


def test_rejects_non_semantic_agent_version(valid_registry: OrganizationRegistry) -> None:
    agent = replace(valid_registry.agents[0], version="version-one")
    registry = replace(valid_registry, agents=(agent,))

    findings = validate_registry(registry)

    assert any(finding.path == "agents[0].version" for finding in findings)


@pytest.mark.parametrize("scope", ["research", "research.*", "Research.documents", ".research"])
def test_rejects_invalid_authority_scope(
    valid_registry: OrganizationRegistry,
    scope: str,
) -> None:
    grant = AuthorityGrant(
        id="research-read",
        subject_type=GrantSubjectType.AGENT,
        subject_id=valid_registry.agents[0].id,
        level=AuthorityLevel.READ,
        scope=scope,
    )
    registry = replace(valid_registry, authority_grants=(grant,))

    findings = validate_registry(registry)

    assert any(finding.path == "authority_grants[0].scope" for finding in findings)


@pytest.mark.parametrize(
    "display_name",
    [
        "Anthropic Analyst",
        "Claude Analyst",
        "OpenAI Analyst",
        "Grok Analyst",
        "LM Studio Analyst",
        "Gemma Analyst",
        "Nemotron Analyst",
    ],
)
def test_rejects_provider_or_model_name_in_agent_display_name(
    valid_registry: OrganizationRegistry,
    display_name: str,
) -> None:
    agent = replace(valid_registry.agents[0], display_name=display_name)
    registry = replace(valid_registry, agents=(agent,))

    findings = validate_registry(registry)

    assert any(finding.path == "agents[0].display_name" for finding in findings)


def test_rejects_provider_name_in_agent_id(valid_registry: OrganizationRegistry) -> None:
    agent = replace(valid_registry.agents[0], id="mfi-claude-analyst")
    registry = replace(valid_registry, agents=(agent,))

    findings = validate_registry(registry)

    assert any(finding.path == "agents[0].id" and "provider" in finding.message for finding in findings)


def test_rejects_agent_approve_grant(valid_registry: OrganizationRegistry) -> None:
    grant = AuthorityGrant(
        id="research-approve",
        subject_type=GrantSubjectType.AGENT,
        subject_id=valid_registry.agents[0].id,
        level=AuthorityLevel.APPROVE,
        scope="research.documents",
    )
    registry = replace(valid_registry, authority_grants=(grant,))

    findings = validate_registry(registry)

    assert any(finding.path == "authority_grants[0].level" for finding in findings)


def test_rejects_unguarded_agent_execute_grant(valid_registry: OrganizationRegistry) -> None:
    grant = AuthorityGrant(
        id="research-execute",
        subject_type=GrantSubjectType.AGENT,
        subject_id=valid_registry.agents[0].id,
        level=AuthorityLevel.EXECUTE,
        scope="research.documents",
        requires_human_approval=False,
    )
    registry = replace(valid_registry, authority_grants=(grant,))

    findings = validate_registry(registry)

    assert any(
        finding.path == "authority_grants[0].requires_human_approval"
        for finding in findings
    )


def test_accepts_independent_agent_grants_with_guarded_execute(
    valid_registry: OrganizationRegistry,
) -> None:
    levels = (
        AuthorityLevel.READ,
        AuthorityLevel.WRITE,
        AuthorityLevel.PROPOSE,
        AuthorityLevel.EXECUTE,
    )
    grants = tuple(
        AuthorityGrant(
            id=f"research-{level.value.lower()}",
            subject_type=GrantSubjectType.AGENT,
            subject_id=valid_registry.agents[0].id,
            level=level,
            scope="research.documents",
            requires_human_approval=level is AuthorityLevel.EXECUTE,
        )
        for level in levels
    )
    registry = replace(valid_registry, authority_grants=grants)

    assert validate_registry(registry) == ()


def test_empty_grants_are_valid_and_do_not_infer_authority(
    valid_registry: OrganizationRegistry,
) -> None:
    assert valid_registry.authority_grants == ()
    assert validate_registry(valid_registry) == ()


def test_validation_returns_all_independent_findings_in_stable_order(
    valid_registry: OrganizationRegistry,
) -> None:
    seat = replace(valid_registry.seats[0], id="Bad Seat")
    agent = replace(valid_registry.agents[0], version="one")
    registry = replace(valid_registry, seats=(seat,), agents=(agent,))
    expected = (
        ("agents[0].version", "must be semantic version x.y.z"),
        ("seats[0].id", "must be lowercase kebab-case"),
    )

    first = tuple((finding.path, finding.message) for finding in validate_registry(registry))
    second = tuple((finding.path, finding.message) for finding in validate_registry(registry))

    assert first == expected
    assert second == expected


@pytest.mark.parametrize(
    ("level", "expected_path"),
    [
        (AuthorityLevel.APPROVE, "authority_grants[0].level"),
        (
            AuthorityLevel.EXECUTE,
            "authority_grants[0].requires_human_approval",
        ),
    ],
)
def test_ai_only_seat_receives_agent_authority_restrictions(
    valid_registry: OrganizationRegistry,
    level: AuthorityLevel,
    expected_path: str,
) -> None:
    seat = replace(
        valid_registry.seats[0],
        seat_type=SeatType.AI,
        agent_ids=(valid_registry.agents[0].id,),
    )
    grant = AuthorityGrant(
        id=f"research-{level.value.lower()}",
        subject_type=GrantSubjectType.SEAT,
        subject_id=seat.id,
        level=level,
        scope="research.documents",
        requires_human_approval=False,
    )
    registry = replace(valid_registry, seats=(seat,), authority_grants=(grant,))

    paths = [finding.path for finding in validate_registry(registry)]

    assert expected_path in paths


@pytest.mark.parametrize(
    ("seat_type", "human_name", "agent_ids"),
    [
        (SeatType.HUMAN, "Joshua", ()),
        (SeatType.HYBRID, "Joshua", ("mfi-investments-lead",)),
    ],
)
def test_human_owned_seat_can_receive_approve_and_unguarded_execute(
    valid_registry: OrganizationRegistry,
    seat_type: SeatType,
    human_name: str,
    agent_ids: tuple[str, ...],
) -> None:
    seat = replace(
        valid_registry.seats[0],
        seat_type=seat_type,
        human_name=human_name,
        agent_ids=agent_ids,
    )
    grants = (
        AuthorityGrant(
            id="research-approve",
            subject_type=GrantSubjectType.SEAT,
            subject_id=seat.id,
            level=AuthorityLevel.APPROVE,
            scope="research.documents",
        ),
        AuthorityGrant(
            id="research-execute",
            subject_type=GrantSubjectType.SEAT,
            subject_id=seat.id,
            level=AuthorityLevel.EXECUTE,
            scope="research.documents",
            requires_human_approval=False,
        ),
    )
    registry = replace(valid_registry, seats=(seat,), authority_grants=grants)

    assert validate_registry(registry) == ()


@pytest.mark.parametrize(
    ("seat_type", "human_name", "agent_ids", "is_valid_owner"),
    [
        (SeatType.HUMAN, "Joshua", (), True),
        (SeatType.HYBRID, "Joshua", ("mfi-investments-lead",), True),
        (SeatType.AI, None, ("mfi-investments-lead",), False),
        (SeatType.VACANT, None, (), False),
    ],
)
def test_agent_seat_owner_must_have_a_human(
    valid_registry: OrganizationRegistry,
    seat_type: SeatType,
    human_name: str | None,
    agent_ids: tuple[str, ...],
    is_valid_owner: bool,
) -> None:
    seat = replace(
        valid_registry.seats[0],
        seat_type=seat_type,
        human_name=human_name,
        agent_ids=agent_ids,
    )
    agent = replace(
        valid_registry.agents[0],
        owner_type=OwnerType.SEAT,
        owner_id=seat.id,
    )
    registry = replace(valid_registry, seats=(seat,), agents=(agent,))

    paths = [finding.path for finding in validate_registry(registry)]

    if is_valid_owner:
        assert "agents[0].owner_id" not in paths
    else:
        assert "agents[0].owner_id" in paths
