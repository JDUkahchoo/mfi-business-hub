from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import AgentManifest


@runtime_checkable
class AgentManifestRepository(Protocol):
    def load_all(self) -> tuple[AgentManifest, ...]: ...
