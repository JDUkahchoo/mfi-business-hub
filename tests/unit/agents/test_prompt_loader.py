from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from app.agents.definitions.errors import DefinitionValidationError
from app.agents.definitions.prompt_loader import PromptLoader, compose_prompt


SHARED_PATH = "prompts/agents/shared/governance.md"
AGENT_PATH = "prompts/agents/cohort-1/mfi-orchestrator/system.md"


def _agent_prompt() -> str:
    return """## Purpose
Coordinate governed work.

## Responsibilities
Propose task order.

## Inputs
Governed work requests.

## Outputs
Coordination plans.

## Boundaries
No execution authority.

## Escalation
Escalate uncertainty.

## Prohibited actions
Do not approve work.
"""


def _write_prompt(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    return path


def test_loads_utf8_sources_in_order_with_digest_and_unchanged_text(
    tmp_path: Path,
) -> None:
    shared_text = "Human decisions take precedence.\nEvidence is required.\n"
    agent_text = _agent_prompt() + "Unicode remains unchanged: café.\n"
    _write_prompt(tmp_path, SHARED_PATH, shared_text)
    _write_prompt(tmp_path, AGENT_PATH, agent_text)

    sources = PromptLoader(tmp_path).load((SHARED_PATH, AGENT_PATH))

    assert tuple(source.path for source in sources) == (SHARED_PATH, AGENT_PATH)
    assert tuple(source.text for source in sources) == (shared_text, agent_text)
    assert sources[0].sha256_digest == hashlib.sha256(
        shared_text.encode("utf-8")
    ).hexdigest()
    assert sources[1].sha256_digest == hashlib.sha256(
        agent_text.encode("utf-8")
    ).hexdigest()


def test_composes_prompt_deterministically_with_source_provenance(
    tmp_path: Path,
) -> None:
    shared_text = "Human decisions take precedence.\n"
    agent_text = _agent_prompt()
    _write_prompt(tmp_path, SHARED_PATH, shared_text)
    _write_prompt(tmp_path, AGENT_PATH, agent_text)
    sources = PromptLoader(tmp_path).load((SHARED_PATH, AGENT_PATH))

    composed = compose_prompt(sources)

    assert composed == (
        f"--- BEGIN PROMPT SOURCE: {SHARED_PATH} ---\n"
        f"{shared_text}"
        f"--- END PROMPT SOURCE: {SHARED_PATH} ---\n\n"
        f"--- BEGIN PROMPT SOURCE: {AGENT_PATH} ---\n"
        f"{agent_text}"
        f"--- END PROMPT SOURCE: {AGENT_PATH} ---"
    )


@pytest.mark.parametrize(
    "paths",
    [
        ("",),
        ("../outside.md",),
        ("config/not-a-prompt.md",),
        ("prompts/agents/shared/governance.txt",),
        (SHARED_PATH, SHARED_PATH),
    ],
)
def test_rejects_lexically_unsafe_or_duplicate_paths(
    tmp_path: Path, paths: tuple[str, ...]
) -> None:
    _write_prompt(tmp_path, SHARED_PATH, "Governance\n")

    with pytest.raises(DefinitionValidationError):
        PromptLoader(tmp_path).load(paths)


def test_rejects_absolute_missing_and_non_file_paths(tmp_path: Path) -> None:
    directory_path = "prompts/agents/shared/directory.md"
    (tmp_path / directory_path).mkdir(parents=True)
    absolute = str((tmp_path / SHARED_PATH).resolve())

    for path in (absolute, SHARED_PATH, directory_path):
        with pytest.raises(DefinitionValidationError):
            PromptLoader(tmp_path).load((path,))


def test_rejects_resolved_path_escape_even_when_lexically_inside_prompts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = _write_prompt(tmp_path, SHARED_PATH, "Governance\n")
    outside = tmp_path.parent / "outside-governance.md"
    original_resolve = Path.resolve

    def redirected_resolve(path: Path, *args, **kwargs) -> Path:
        if path == target:
            return outside
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", redirected_resolve)

    with pytest.raises(DefinitionValidationError) as exc_info:
        PromptLoader(tmp_path).load((SHARED_PATH,))

    assert "resolves outside" in str(exc_info.value)


def test_rejects_prompt_root_that_resolves_outside_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = _write_prompt(tmp_path, SHARED_PATH, "Governance\n")
    repository = tmp_path.resolve()
    prompt_root = repository / "prompts"
    outside_root = repository.parent / "redirected-prompts"
    outside_target = outside_root / "agents/shared/governance.md"
    original_resolve = Path.resolve

    def redirected_resolve(path: Path, *args, **kwargs) -> Path:
        if path == prompt_root:
            return outside_root
        if path == target:
            return outside_target
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", redirected_resolve)

    with pytest.raises(DefinitionValidationError) as exc_info:
        PromptLoader(repository).load((SHARED_PATH,))

    assert "prompt root" in str(exc_info.value)


def test_rejects_symlink_escape_when_supported(tmp_path: Path) -> None:
    outside = tmp_path / "outside.md"
    outside.write_text("Outside prompt", encoding="utf-8")
    link = tmp_path / SHARED_PATH
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"host cannot create symlinks: {exc}")

    with pytest.raises(DefinitionValidationError):
        PromptLoader(tmp_path).load((SHARED_PATH,))


def test_rejects_invalid_utf8_and_blank_prompt_files(tmp_path: Path) -> None:
    invalid = tmp_path / SHARED_PATH
    invalid.parent.mkdir(parents=True, exist_ok=True)
    invalid.write_bytes(b"\xff")
    with pytest.raises(DefinitionValidationError) as invalid_error:
        PromptLoader(tmp_path).load((SHARED_PATH,))
    assert "UTF-8" in str(invalid_error.value)

    invalid.write_text("  \n", encoding="utf-8")
    with pytest.raises(DefinitionValidationError) as blank_error:
        PromptLoader(tmp_path).load((SHARED_PATH,))
    assert "blank" in str(blank_error.value)


@pytest.mark.parametrize("change", ["missing", "repeated"])
def test_agent_prompt_requires_each_exact_heading_once(
    tmp_path: Path, change: str
) -> None:
    text = _agent_prompt()
    if change == "missing":
        text = text.replace("## Inputs\n", "")
    else:
        text += "\n## Inputs\nRepeated.\n"
    _write_prompt(tmp_path, AGENT_PATH, text)

    with pytest.raises(DefinitionValidationError) as exc_info:
        PromptLoader(tmp_path).load((AGENT_PATH,))

    assert "## Inputs" in str(exc_info.value)


@pytest.mark.parametrize(
    ("path", "text"),
    [
        (SHARED_PATH, "Do not use Open AI."),
        (AGENT_PATH, _agent_prompt() + "Use Ne-mo-tron."),
    ],
)
def test_rejects_normalized_provider_or_model_tokens_in_every_prompt(
    tmp_path: Path, path: str, text: str
) -> None:
    _write_prompt(tmp_path, path, text)

    with pytest.raises(DefinitionValidationError) as exc_info:
        PromptLoader(tmp_path).load((path,))

    assert "provider/model" in str(exc_info.value)
