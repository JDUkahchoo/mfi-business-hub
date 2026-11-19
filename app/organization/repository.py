from typing import Protocol, runtime_checkable

from .models import OrganizationRegistry


@runtime_checkable
class OrganizationRepository(Protocol):
    def load(self) -> OrganizationRegistry: ...
