from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from app.agents.definitions.errors import DefinitionValidationError
from app.agents.definitions.json_repository import (
    JsonAgentManifestRepository,
    parse_manifest_data,
)
from app.agents.definitions.models import (
    ApproverType,
    DataClassification,
    EvidenceType,
    ExecutionPolicy,
)


def test_parses_complete_manifest(valid_manifest_data: dict[str, object]) -> None:
    manifest = parse_manifest_data(valid_manifest_data, "mfi-orchestrator.json")

    assert manifest.agent_id == "mfi-orchestrator"
    assert manifest.responsibilities == (
        "Coordinate task decomposition and dependencies.",
    )
    assert manifest.input_contracts[0].required_fields == ("request_id", "objective")
    assert manifest.allowed_data_classifications == (
        DataClassification.PUBLIC,
        DataClassification.INTERNAL,
    )
    assert manifest.approval_requirements[0].approver is ApproverType.ACCOUNTABLE_HUMAN
    assert manifest.acceptance_criteria[0].evidence_type is EvidenceType.TEST
    assert manifest.routing_policy.execution_policy is ExecutionPolicy.LOCAL_PREFERRED
    assert manifest.routing_policy.cloud_fallback_allowed is False
    assert manifest.allowed_tools == ()
    assert manifest.authority_grant_ids == ()


@pytest.mark.parametrize(
    ("mutate", "expected_path"),
    [
        (lambda data: data.update(extra="value"), "manifest.extra"),
        (lambda data: data.pop("agent_id"), "manifest.agent_id"),
        (lambda data: data.update(schema_version=True), "manifest.schema_version"),
        (lambda data: data.update(schema_version=2), "manifest.schema_version"),
        (lambda data: data.update(responsibilities="not-a-list"), "manifest.responsibilities"),
        (
            lambda data: data["routing_policy"].update(extra=False),
            "manifest.routing_policy.extra",
        ),
        (
            lambda data: data["routing_policy"].update(cloud_fallback_allowed=0),
            "manifest.routing_policy.cloud_fallback_allowed",
        ),
        (
            lambda data: data["approval_requirements"][0].update(approver="OWNER"),
            "manifest.approval_requirements[0].approver",
        ),
        (
            lambda data: data["approval_requirements"][0].update(approver=""),
            "manifest.approval_requirements[0].approver",
        ),
        (
            lambda data: data["allowed_data_classifications"].append(""),
            "manifest.allowed_data_classifications[2]",
        ),
        (
            lambda data: data["acceptance_criteria"][0].update(evidence_type=""),
            "manifest.acceptance_criteria[0].evidence_type",
        ),
        (
            lambda data: data["input_contracts"][0].update(required_fields=[1]),
            "manifest.input_contracts[0].required_fields[0]",
        ),
    ],
)
def test_rejects_shape_type_and_enum_errors(
    valid_manifest_data: dict[str, object], mutate, expected_path: str
) -> None:
    data = deepcopy(valid_manifest_data)
    mutate(data)

    with pytest.raises(DefinitionValidationError) as exc_info:
        parse_manifest_data(data, "manifest")

    assert expected_path in {finding.path for finding in exc_info.value.findings}


def test_rejects_non_object_root() -> None:
    with pytest.raises(DefinitionValidationError) as exc_info:
        parse_manifest_data([], "manifest")

    assert exc_info.value.findings[0].path == "manifest"


def test_accumulates_independent_shape_errors(
    valid_manifest_data: dict[str, object],
) -> None:
    valid_manifest_data.pop("agent_id")
    valid_manifest_data["schema_version"] = False
    valid_manifest_data["responsibilities"] = ["valid", 4]

    with pytest.raises(DefinitionValidationError) as exc_info:
        parse_manifest_data(valid_manifest_data, "manifest")

    paths = {finding.path for finding in exc_info.value.findings}
    assert {
        "manifest.agent_id",
        "manifest.schema_version",
        "manifest.responsibilities[1]",
    } <= paths


def _manifest_for(data: dict[str, object], agent_id: str) -> dict[str, object]:
    result = deepcopy(data)
    result["agent_id"] = agent_id
    result["prompt_sources"] = [
        "prompts/agents/shared/governance.md",
        f"prompts/agents/cohort-1/{agent_id}/system.md",
    ]
    return result


def _write_manifest(directory: Path, name: str, data: dict[str, object]) -> None:
    (directory / name).write_text(json.dumps(data), encoding="utf-8")


def test_repository_loads_direct_manifests_in_filename_order(
    tmp_path: Path, valid_manifest_data: dict[str, object]
) -> None:
    first = "mfi-incubation-lead"
    second = "mfi-orchestrator"
    _write_manifest(tmp_path, f"{second}.json", _manifest_for(valid_manifest_data, second))
    _write_manifest(tmp_path, f"{first}.json", _manifest_for(valid_manifest_data, first))

    manifests = JsonAgentManifestRepository(
        tmp_path, frozenset({first, second})
    ).load_all()

    assert tuple(item.agent_id for item in manifests) == (first, second)


@pytest.mark.parametrize("kind", ["missing", "file"])
def test_repository_rejects_missing_or_non_directory_path(
    tmp_path: Path, kind: str
) -> None:
    path = tmp_path / kind
    if kind == "file":
        path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(DefinitionValidationError) as exc_info:
        JsonAgentManifestRepository(path, frozenset()).load_all()

    assert exc_info.value.findings[0].path == str(path)


@pytest.mark.parametrize("entry_name", ["notes.txt", ".hidden.json", "nested"])
def test_repository_rejects_unexpected_direct_entries(
    tmp_path: Path, entry_name: str
) -> None:
    entry = tmp_path / entry_name
    if entry_name == "nested":
        entry.mkdir()
    else:
        entry.write_text("unexpected", encoding="utf-8")

    with pytest.raises(DefinitionValidationError) as exc_info:
        JsonAgentManifestRepository(tmp_path, frozenset()).load_all()

    assert entry_name in str(exc_info.value)


@pytest.mark.parametrize(
    ("raw", "message_fragment"),
    [
        (b"\xff", "UTF-8"),
        (b"{not-json", "JSON"),
        (b'{"schema_version": 1, "schema_version": 1}', "duplicate JSON member"),
    ],
)
def test_repository_rejects_unreadable_or_malformed_json(
    tmp_path: Path, raw: bytes, message_fragment: str
) -> None:
    (tmp_path / "mfi-orchestrator.json").write_bytes(raw)

    with pytest.raises(DefinitionValidationError) as exc_info:
        JsonAgentManifestRepository(
            tmp_path, frozenset({"mfi-orchestrator"})
        ).load_all()

    assert message_fragment in str(exc_info.value)


@pytest.mark.parametrize(
    ("filename", "agent_id"),
    [
        ("wrong-name.json", "mfi-orchestrator"),
        ("MFI-ORCHESTRATOR.json", "mfi-orchestrator"),
    ],
)
def test_repository_requires_exact_lowercase_filename_parity(
    tmp_path: Path,
    valid_manifest_data: dict[str, object],
    filename: str,
    agent_id: str,
) -> None:
    _write_manifest(tmp_path, filename, _manifest_for(valid_manifest_data, agent_id))

    with pytest.raises(DefinitionValidationError) as exc_info:
        JsonAgentManifestRepository(tmp_path, frozenset({agent_id})).load_all()

    assert "filename must equal" in str(exc_info.value)


def test_repository_rejects_duplicate_ids_and_missing_or_extra_expected_ids(
    tmp_path: Path, valid_manifest_data: dict[str, object]
) -> None:
    _write_manifest(tmp_path, "mfi-orchestrator.json", valid_manifest_data)
    _write_manifest(tmp_path, "copy.json", valid_manifest_data)

    with pytest.raises(DefinitionValidationError) as exc_info:
        JsonAgentManifestRepository(
            tmp_path, frozenset({"mfi-orchestrator", "mfi-qa-auditor"})
        ).load_all()

    text = str(exc_info.value)
    assert "duplicate agent ID" in text
    assert "missing expected agent ID 'mfi-qa-auditor'" in text


def test_repository_accumulates_errors_across_files(
    tmp_path: Path, valid_manifest_data: dict[str, object]
) -> None:
    (tmp_path / "a.json").write_text("{bad", encoding="utf-8")
    bad = _manifest_for(valid_manifest_data, "mfi-orchestrator")
    bad["responsibilities"] = [""]
    _write_manifest(tmp_path, "mfi-orchestrator.json", bad)

    with pytest.raises(DefinitionValidationError) as exc_info:
        JsonAgentManifestRepository(
            tmp_path, frozenset({"mfi-orchestrator"})
        ).load_all()

    paths = tuple(item.path for item in exc_info.value.findings)
    assert any(path.startswith("a.json") for path in paths)
    assert any(path.startswith("mfi-orchestrator.json") for path in paths)
    assert paths == tuple(sorted(paths))


def test_duplicate_id_diagnostic_retains_successful_source_filenames_after_bad_file(
    tmp_path: Path, valid_manifest_data: dict[str, object]
) -> None:
    (tmp_path / "a-invalid.json").write_text("{bad", encoding="utf-8")
    _write_manifest(tmp_path, "copy.json", valid_manifest_data)
    _write_manifest(tmp_path, "mfi-orchestrator.json", valid_manifest_data)

    with pytest.raises(DefinitionValidationError) as exc_info:
        JsonAgentManifestRepository(
            tmp_path, frozenset({"mfi-orchestrator"})
        ).load_all()

    duplicate = next(
        finding
        for finding in exc_info.value.findings
        if "duplicate agent ID" in finding.message
    )
    assert "copy.json" in duplicate.message
    assert "mfi-orchestrator.json" in duplicate.message
    assert "a-invalid.json" not in duplicate.message
