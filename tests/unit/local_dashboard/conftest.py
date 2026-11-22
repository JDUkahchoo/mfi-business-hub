from __future__ import annotations

from pathlib import Path

import pytest

from app.agents.definitions.json_repository import JsonAgentManifestRepository
from app.agents.definitions.prompt_loader import PromptLoader
from app.agents.definitions.service import AgentDefinitionService
from app.organization import JsonOrganizationRepository


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@pytest.fixture
def definition_service(repo_root: Path) -> AgentDefinitionService:
    return AgentDefinitionService(
        JsonOrganizationRepository(repo_root / "config/organization/registry.json"),
        JsonAgentManifestRepository(repo_root / "config/agents/cohort-1"),
        PromptLoader(repo_root),
    )
