from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from app.agents.definitions.cli import main


REPO_ROOT = Path(__file__).resolve().parents[3]
COHORT_IDS = (
    "mfi-incubation-lead",
    "mfi-infrastructure-lead",
    "mfi-investments-lead",
    "mfi-orchestrator",
    "mfi-qa-auditor",
    "mfi-tech-entertainment-lead",
)


def _source_paths(root: Path) -> tuple[Path, ...]:
    return (
        root / "config/organization/registry.json",
        *sorted((root / "config/agents/cohort-1").glob("*.json")),
        *sorted((root / "prompts/agents").rglob("*.md")),
    )


def _snapshot(root: Path) -> tuple[tuple[Path, bytes, int], ...]:
    return tuple((path, path.read_bytes(), path.stat().st_mtime_ns) for path in _source_paths(root))


@pytest.mark.parametrize("command", ["validate", "summary", "readiness"])
def test_cli_success_commands_are_read_only(
    command: str, capsys: pytest.CaptureFixture[str]
) -> None:
    before = _snapshot(REPO_ROOT)

    assert main((command,)) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert _snapshot(REPO_ROOT) == before
    if command == "validate":
        assert captured.out == (
            "6 Cohort 1 definitions valid; 12 prompt sources loaded; "
            "0 authority grants resolved.\n"
        )
    elif command == "readiness":
        assert captured.out == (
            "6 definition-complete; 0 activation-eligible; 6 blocked.\n"
        )
    else:
        rows = captured.out.splitlines()
        assert len(rows) == 6
        assert tuple(row.split()[0] for row in rows) == COHORT_IDS
        assert all("COMPLETE" in row and "PLANNED" in row and "BLOCKED" in row for row in rows)


def test_show_hides_prompt_by_default_and_reveals_only_on_request(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(("show", "mfi-orchestrator")) == 0
    hidden = capsys.readouterr()

    assert "MFI Orchestrator" in hidden.out
    assert "task-brief" in hidden.out
    assert "coordination-plan" in hidden.out
    assert "prompts/agents/shared/governance.md" in hidden.out
    assert "lifecycle-status-planned" in hidden.out
    assert "Human decisions and established MFI governance" not in hidden.out
    assert "BEGIN PROMPT SOURCE" not in hidden.out

    assert main(("show", "mfi-orchestrator", "--with-prompt")) == 0
    revealed = capsys.readouterr()
    assert "BEGIN PROMPT SOURCE: prompts/agents/shared/governance.md" in revealed.out
    assert "BEGIN PROMPT SOURCE: prompts/agents/cohort-1/mfi-orchestrator/system.md" in revealed.out
    assert "Human decisions and established MFI governance" in revealed.out


def test_show_rejects_abbreviated_prompt_reveal_flag_without_disclosure(
    tmp_path: Path,
) -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(REPO_ROOT)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.agents.definitions.cli",
            "show",
            "mfi-orchestrator",
            "--with",
        ],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 2
    assert "Human decisions and established MFI governance" not in completed.stdout
    assert "BEGIN PROMPT SOURCE" not in completed.stdout


def _copy_definition_sources(destination: Path) -> None:
    (destination / "config/organization").mkdir(parents=True)
    (destination / "config/agents").mkdir(parents=True)
    (destination / "prompts").mkdir()
    shutil.copy2(
        REPO_ROOT / "config/organization/registry.json",
        destination / "config/organization/registry.json",
    )
    shutil.copytree(
        REPO_ROOT / "config/agents/cohort-1",
        destination / "config/agents/cohort-1",
    )
    shutil.copytree(REPO_ROOT / "prompts/agents", destination / "prompts/agents")


def test_cli_errors_are_concise_without_tracebacks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _copy_definition_sources(tmp_path)
    manifest_path = tmp_path / "config/agents/cohort-1/mfi-orchestrator.json"
    manifest_path.write_text("{not-json", encoding="utf-8")

    assert main(("--repo-root", str(tmp_path), "validate")) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "mfi-orchestrator.json" in captured.err
    assert "invalid JSON" in captured.err
    assert "Traceback" not in captured.err
    assert all("\r" not in line for line in captured.err.splitlines())


def test_cli_rejects_unknown_agent_unsafe_prompt_and_missing_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(("show", "unknown-agent")) == 2
    unknown = capsys.readouterr()
    assert "unknown agent ID" in unknown.err
    assert "Traceback" not in unknown.err

    _copy_definition_sources(tmp_path)
    manifest_path = tmp_path / "config/agents/cohort-1/mfi-orchestrator.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["prompt_sources"][1] = "prompts/../outside.md"
    manifest_path.write_text(json.dumps(data), encoding="utf-8")
    assert main(("--repo-root", str(tmp_path), "validate")) == 2
    unsafe = capsys.readouterr()
    assert "prompt_sources" in unsafe.err
    assert "Traceback" not in unsafe.err

    missing_root = tmp_path / "missing"
    assert main(("--repo-root", str(missing_root), "validate")) == 2
    missing = capsys.readouterr()
    assert "directory does not exist" in missing.err or "cannot read registry" in missing.err
    assert "Traceback" not in missing.err


@pytest.mark.parametrize("command", ["validate", "summary", "readiness", "show"])
def test_module_commands_work_outside_repository(
    tmp_path: Path, command: str
) -> None:
    arguments = [sys.executable, "-m", "app.agents.definitions.cli", command]
    if command == "show":
        arguments.append("mfi-orchestrator")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(REPO_ROOT)

    completed = subprocess.run(
        arguments,
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Traceback" not in completed.stderr
