from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath

from .errors import DefinitionFinding, DefinitionValidationError
from .models import LoadedPromptSource
from .policy import PROVIDER_MODEL_DENYLIST, REQUIRED_PROMPT_HEADINGS


class PromptLoader:
    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def load(self, paths: tuple[str, ...]) -> tuple[LoadedPromptSource, ...]:
        findings: list[DefinitionFinding] = []
        candidates: list[tuple[str, Path]] = []
        seen: set[str] = set()
        prompt_root = (self._repo_root / "prompts").resolve()

        for index, raw_path in enumerate(paths):
            source_path = f"prompt_sources[{index}]"
            if not raw_path:
                findings.append(DefinitionFinding(source_path, "must not be empty"))
                continue
            if raw_path in seen:
                findings.append(DefinitionFinding(source_path, f"duplicate path {raw_path!r}"))
                continue
            seen.add(raw_path)

            logical = PurePosixPath(raw_path)
            if logical.is_absolute() or Path(raw_path).is_absolute():
                findings.append(DefinitionFinding(source_path, "must be repository-relative"))
                continue
            if "\\" in raw_path or ".." in logical.parts:
                findings.append(DefinitionFinding(source_path, "contains an unsafe path segment"))
                continue
            if logical.suffix != ".md":
                findings.append(DefinitionFinding(source_path, "must reference a .md file"))
                continue
            if not logical.parts or logical.parts[0] != "prompts":
                findings.append(DefinitionFinding(source_path, "must be inside prompts/"))
                continue

            candidate = self._repo_root.joinpath(*logical.parts)
            resolved = candidate.resolve()
            if not resolved.is_relative_to(prompt_root):
                findings.append(
                    DefinitionFinding(source_path, "resolves outside the prompts directory")
                )
                continue
            if not candidate.exists():
                findings.append(DefinitionFinding(source_path, "file does not exist"))
                continue
            if not candidate.is_file():
                findings.append(DefinitionFinding(source_path, "must reference a file"))
                continue
            candidates.append((raw_path, candidate))

        if findings:
            raise DefinitionValidationError(findings)

        sources: list[LoadedPromptSource] = []
        for logical_path, candidate in candidates:
            try:
                raw = candidate.read_bytes()
                text = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                findings.append(
                    DefinitionFinding(logical_path, f"must contain valid UTF-8: {exc}")
                )
                continue
            except OSError as exc:
                findings.append(DefinitionFinding(logical_path, f"cannot read file: {exc}"))
                continue

            if not text.strip():
                findings.append(DefinitionFinding(logical_path, "prompt must not be blank"))
            if logical_path.startswith("prompts/agents/cohort-1/"):
                lines = text.splitlines()
                for heading in REQUIRED_PROMPT_HEADINGS:
                    count = lines.count(heading)
                    if count != 1:
                        findings.append(
                            DefinitionFinding(
                                logical_path,
                                f"heading {heading!r} must appear exactly once (found {count})",
                            )
                        )

            normalized = re.sub(r"[^a-z0-9]", "", text.casefold())
            for token in sorted(PROVIDER_MODEL_DENYLIST):
                if token in normalized:
                    findings.append(
                        DefinitionFinding(
                            logical_path,
                            f"contains prohibited provider/model token {token!r}",
                        )
                    )

            sources.append(
                LoadedPromptSource(
                    path=logical_path,
                    text=text,
                    sha256_digest=hashlib.sha256(raw).hexdigest(),
                )
            )

        if findings:
            raise DefinitionValidationError(findings)
        return tuple(sources)


def compose_prompt(sources: tuple[LoadedPromptSource, ...]) -> str:
    chunks: list[str] = []
    for source in sources:
        text = source.text if source.text.endswith("\n") else f"{source.text}\n"
        chunks.append(
            f"--- BEGIN PROMPT SOURCE: {source.path} ---\n"
            f"{text}"
            f"--- END PROMPT SOURCE: {source.path} ---"
        )
    return "\n\n".join(chunks)
