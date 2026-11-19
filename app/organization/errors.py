from dataclasses import dataclass
from typing import Iterable
@dataclass(frozen=True, order=True, slots=True)
class ValidationFinding:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class RegistryError(Exception):
    """Base class for expected registry data errors."""


class RegistryLoadError(RegistryError):
    """Raised when registry data cannot be read or decoded."""


class RegistryValidationError(RegistryError):
    def __init__(self, findings: Iterable[ValidationFinding]) -> None:
        self.findings = tuple(sorted(findings))
        super().__init__("\n".join(str(finding) for finding in self.findings))
