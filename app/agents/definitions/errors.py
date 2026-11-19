from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class AgentDefinitionError(Exception):
    """Base class for expected agent-definition data failures."""


class DefinitionLoadError(AgentDefinitionError):
    """Raised when a definition source cannot be read or decoded."""


@dataclass(frozen=True, slots=True, order=True)
class DefinitionFinding:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class DefinitionValidationError(AgentDefinitionError):
    def __init__(self, findings: Iterable[DefinitionFinding]) -> None:
        self.findings = tuple(sorted(findings, key=lambda item: (item.path, item.message)))
        super().__init__("\n".join(str(finding) for finding in self.findings))
