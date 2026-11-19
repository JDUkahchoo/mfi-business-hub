import copy
from pathlib import Path

import pytest

from app.organization.errors import RegistryLoadError, RegistryValidationError
from app.organization.json_repository import JsonOrganizationRepository, parse_registry_data
from app.organization.models import AgentStatus, OwnerType, PillarId, SeatType


def _finding_paths(error: RegistryValidationError) -> set[str]:
    return {finding.path for finding in error.findings}


def test_loads_complete_registry_and_converts_domain_types(registry_file: Path) -> None:
    registry = JsonOrganizationRepository(registry_file).load()

    assert registry.roles[0].pillar_id is PillarId.INVESTMENTS
    assert registry.seats[0].seat_type is SeatType.VACANT
    assert registry.agents[0].status is AgentStatus.PLANNED
    assert registry.agents[0].owner_type is OwnerType.ROLE
    assert isinstance(registry.roles, tuple)
    assert isinstance(registry.seats, tuple)
    assert isinstance(registry.agents, tuple)
    assert isinstance(registry.authority_grants, tuple)


def test_rejects_missing_top_level_key(valid_registry_data: dict[str, object]) -> None:
    data = copy.deepcopy(valid_registry_data)
    del data["agents"]

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert "agents" in _finding_paths(caught.value)


def test_rejects_unknown_top_level_key(valid_registry_data: dict[str, object]) -> None:
    data = copy.deepcopy(valid_registry_data)
    data["unexpected"] = []

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert "unexpected" in _finding_paths(caught.value)


def test_rejects_missing_record_key(valid_registry_data: dict[str, object]) -> None:
    data = copy.deepcopy(valid_registry_data)
    del data["roles"][0]["description"]  # type: ignore[index]

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert "roles[0].description" in _finding_paths(caught.value)


def test_rejects_unknown_record_key(valid_registry_data: dict[str, object]) -> None:
    data = copy.deepcopy(valid_registry_data)
    data["agents"][0]["provider"] = "cloud"  # type: ignore[index]

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert "agents[0].provider" in _finding_paths(caught.value)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("roles", {}),
        ("seats", "not-a-list"),
        ("agents", None),
        ("authority_grants", 1),
    ],
)
def test_rejects_wrong_collection_types(
    valid_registry_data: dict[str, object],
    field: str,
    bad_value: object,
) -> None:
    data = copy.deepcopy(valid_registry_data)
    data[field] = bad_value

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert field in _finding_paths(caught.value)


def test_rejects_wrong_scalar_type(valid_registry_data: dict[str, object]) -> None:
    data = copy.deepcopy(valid_registry_data)
    data["roles"][0]["id"] = 123  # type: ignore[index]

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert "roles[0].id" in _finding_paths(caught.value)


def test_rejects_boolean_schema_version(valid_registry_data: dict[str, object]) -> None:
    data = copy.deepcopy(valid_registry_data)
    data["schema_version"] = True

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert "schema_version" in _finding_paths(caught.value)


def test_rejects_integer_where_boolean_is_required(
    valid_registry_data: dict[str, object],
) -> None:
    data = copy.deepcopy(valid_registry_data)
    data["authority_grants"] = [
        {
            "id": "research-read",
            "subject_type": "AGENT",
            "subject_id": "mfi-investments-lead",
            "level": "READ",
            "scope": "research.documents",
            "requires_human_approval": 1,
        }
    ]

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert "authority_grants[0].requires_human_approval" in _finding_paths(caught.value)


def test_rejects_both_records_with_duplicate_ids(
    valid_registry_data: dict[str, object],
) -> None:
    data = copy.deepcopy(valid_registry_data)
    data["agents"].append(copy.deepcopy(data["agents"][0]))  # type: ignore[union-attr,index]

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    paths = _finding_paths(caught.value)
    assert "agents[0].id" in paths
    assert "agents[1].id" in paths


@pytest.mark.parametrize(
    ("collection", "field", "bad_value", "expected_path"),
    [
        ("roles", "pillar_id", "unknown-pillar", "roles[0].pillar_id"),
        ("seats", "seat_type", "UNKNOWN", "seats[0].seat_type"),
        ("agents", "status", "UNKNOWN", "agents[0].status"),
        ("agents", "owner_type", "UNKNOWN", "agents[0].owner_type"),
    ],
)
def test_rejects_invalid_enum_as_a_validation_finding(
    valid_registry_data: dict[str, object],
    collection: str,
    field: str,
    bad_value: str,
    expected_path: str,
) -> None:
    data = copy.deepcopy(valid_registry_data)
    data[collection][0][field] = bad_value  # type: ignore[index]

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert expected_path in _finding_paths(caught.value)


@pytest.mark.parametrize(
    ("field", "bad_value", "expected_path"),
    [
        ("subject_type", "UNKNOWN", "authority_grants[0].subject_type"),
        ("level", "UNKNOWN", "authority_grants[0].level"),
    ],
)
def test_rejects_invalid_grant_enum_as_a_validation_finding(
    valid_registry_data: dict[str, object],
    field: str,
    bad_value: str,
    expected_path: str,
) -> None:
    data = copy.deepcopy(valid_registry_data)
    grant = {
        "id": "research-read",
        "subject_type": "AGENT",
        "subject_id": "mfi-investments-lead",
        "level": "READ",
        "scope": "research.documents",
    }
    grant[field] = bad_value
    data["authority_grants"] = [grant]

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert expected_path in _finding_paths(caught.value)


@pytest.mark.parametrize("name", ["missing.json", "registry-directory"])
def test_translates_missing_or_unreadable_path_to_load_error(
    tmp_path: Path,
    name: str,
) -> None:
    path = tmp_path / name
    if name == "registry-directory":
        path.mkdir()

    with pytest.raises(RegistryLoadError) as caught:
        JsonOrganizationRepository(path).load()

    assert str(path) in str(caught.value)
    assert "Traceback" not in str(caught.value)


def test_translates_malformed_json_with_line_and_column(tmp_path: Path) -> None:
    path = tmp_path / "malformed.json"
    path.write_text('{\n  "schema_version": }', encoding="utf-8")

    with pytest.raises(RegistryLoadError) as caught:
        JsonOrganizationRepository(path).load()

    assert "line 2" in str(caught.value)
    assert "column" in str(caught.value)
    assert "Traceback" not in str(caught.value)


def test_translates_non_utf8_content_to_load_error(tmp_path: Path) -> None:
    path = tmp_path / "non-utf8.json"
    path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(RegistryLoadError) as caught:
        JsonOrganizationRepository(path).load()

    assert str(path) in str(caught.value)
    assert "UTF-8" in str(caught.value)
    assert "Traceback" not in str(caught.value)


def test_rejects_unsupported_schema_version(
    valid_registry_data: dict[str, object],
) -> None:
    data = copy.deepcopy(valid_registry_data)
    data["schema_version"] = 2

    with pytest.raises(RegistryValidationError) as caught:
        parse_registry_data(data)

    assert "schema_version" in _finding_paths(caught.value)
    assert "unsupported version" in str(caught.value)
