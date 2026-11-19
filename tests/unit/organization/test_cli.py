import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from app.organization.cli import main

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "config" / "organization" / "registry.json"


@pytest.mark.parametrize(
    ("command", "expected_output"),
    [
        ("validate", "Registry valid.\n"),
        (
            "summary",
            "Registry valid: 12 roles, 12 seats, 12 agents, 0 authority grants.\n",
        ),
    ],
)
def test_successful_commands_are_read_only(
    capsys: pytest.CaptureFixture[str],
    command: str,
    expected_output: str,
) -> None:
    before_bytes = REGISTRY_PATH.read_bytes()
    before_mtime = REGISTRY_PATH.stat().st_mtime_ns

    exit_code = main([command, "--registry", str(REGISTRY_PATH)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == expected_output
    assert captured.err == ""
    assert REGISTRY_PATH.read_bytes() == before_bytes
    assert REGISTRY_PATH.stat().st_mtime_ns == before_mtime


@pytest.mark.parametrize("kind", ["missing", "directory", "malformed"])
def test_cli_reports_load_errors_without_traceback(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    kind: str,
) -> None:
    path = tmp_path / "registry.json"
    if kind == "directory":
        path.mkdir()
    elif kind == "malformed":
        path.write_text('{"schema_version": }', encoding="utf-8")

    exit_code = main(["validate", "--registry", str(path)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert len(captured.err.splitlines()) == 1
    assert captured.err.startswith("error: ")
    assert "Traceback" not in captured.err


def test_cli_prints_one_error_line_per_validation_finding(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    valid_registry_data: dict[str, object],
) -> None:
    data = copy.deepcopy(valid_registry_data)
    data["seats"][0]["id"] = "Bad Seat"  # type: ignore[index]
    data["agents"][0]["version"] = "one"  # type: ignore[index]
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    exit_code = main(["summary", "--registry", str(path)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert captured.err.splitlines() == [
        "error: agents[0].version: must be semantic version x.y.z",
        "error: seats[0].id: must be lowercase kebab-case",
    ]
    assert "Traceback" not in captured.err


def test_module_uses_repository_relative_default_outside_repo(tmp_path: Path) -> None:
    environment = os.environ.copy()
    existing_python_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(REPO_ROOT)
        if not existing_python_path
        else f"{REPO_ROOT}{os.pathsep}{existing_python_path}"
    )

    completed = subprocess.run(
        [sys.executable, "-m", "app.organization.cli", "summary"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stdout == (
        "Registry valid: 12 roles, 12 seats, 12 agents, 0 authority grants.\n"
    )
    assert completed.stderr == ""
