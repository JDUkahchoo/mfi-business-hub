from __future__ import annotations

from pathlib import Path

from app.agents.definitions.json_repository import JsonAgentManifestRepository
from app.agents.definitions.models import (
    ActivationEligibility,
    DataClassification,
    DefinitionCompleteness,
    ExecutionPolicy,
)
from app.agents.definitions.prompt_loader import PromptLoader
from app.agents.definitions.readiness import evaluate_readiness
from app.agents.definitions.service import AgentDefinitionService
from app.agents.definitions.policy import COHORT_1_AGENT_IDS, REQUIRED_AUDIT_EVENTS
from app.organization import AgentStatus, JsonOrganizationRepository


REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_definitions(expected_agent_ids: frozenset[str]):
    return AgentDefinitionService(
        JsonOrganizationRepository(REPO_ROOT / "config/organization/registry.json"),
        JsonAgentManifestRepository(
            REPO_ROOT / "config/agents/cohort-1", expected_agent_ids
        ),
        PromptLoader(REPO_ROOT),
        expected_agent_ids=expected_agent_ids,
    ).load_all()


def test_orchestrator_definition_package() -> None:
    definitions = tuple(
        definition
        for definition in _load_definitions(COHORT_1_AGENT_IDS)
        if definition.registry_record.id == "mfi-orchestrator"
    )

    assert len(definitions) == 1
    definition = definitions[0]
    manifest = definition.manifest
    assert definition.registry_record.id == "mfi-orchestrator"
    assert definition.registry_record.display_name == "MFI Orchestrator"
    assert definition.registry_record.purpose == (
        "Routes governed tasks and coordinates registered agents."
    )
    assert definition.registry_record.status is AgentStatus.PLANNED
    assert definition.registry_record.version == "0.1.0"
    assert definition.registry_record.owner_id == "enterprise-orchestration"
    assert manifest.allowed_tools == ()
    assert manifest.authority_grant_ids == ()
    assert manifest.allowed_data_classifications == (
        DataClassification.PUBLIC,
        DataClassification.INTERNAL,
    )
    assert manifest.routing_policy.execution_policy is ExecutionPolicy.LOCAL_PREFERRED
    assert manifest.routing_policy.cloud_fallback_allowed is False
    assert manifest.prompt_sources == (
        "prompts/agents/shared/governance.md",
        "prompts/agents/cohort-1/mfi-orchestrator/system.md",
    )
    assert manifest.capability_requirements == (
        "reasoning",
        "structured-output",
        "task-decomposition",
        "coordination",
    )
    assert manifest.input_contracts[0].id == "task-brief"
    assert manifest.output_contracts[0].id == "coordination-plan"
    assert definition.resolved_grants == ()

    readiness = evaluate_readiness(definition)
    assert readiness.completeness is DefinitionCompleteness.COMPLETE
    assert readiness.eligibility is ActivationEligibility.BLOCKED
    assert readiness.blocker_codes[0] == "lifecycle-status-planned"


def test_cohort_asset_tree_has_exact_six_definition_packages() -> None:
    manifest_ids = {
        path.stem for path in (REPO_ROOT / "config/agents/cohort-1").glob("*.json")
    }
    prompt_ids = {
        path.name
        for path in (REPO_ROOT / "prompts/agents/cohort-1").iterdir()
        if path.is_dir()
    }

    assert manifest_ids == COHORT_1_AGENT_IDS
    assert prompt_ids == COHORT_1_AGENT_IDS


def test_all_six_cohort_packages_join_canonical_registry_and_remain_blocked() -> None:
    definitions = _load_definitions(COHORT_1_AGENT_IDS)

    assert tuple(item.registry_record.id for item in definitions) == tuple(
        sorted(COHORT_1_AGENT_IDS)
    )
    expected_capabilities = {
        "mfi-orchestrator": (
            "reasoning",
            "structured-output",
            "task-decomposition",
            "coordination",
        ),
        "mfi-qa-auditor": (
            "reasoning",
            "structured-output",
            "evidence-review",
            "policy-review",
        ),
        "mfi-infrastructure-lead": (
            "reasoning",
            "structured-output",
            "domain-analysis",
            "risk-identification",
        ),
        "mfi-tech-entertainment-lead": (
            "reasoning",
            "structured-output",
            "domain-analysis",
            "risk-identification",
        ),
        "mfi-investments-lead": (
            "reasoning",
            "structured-output",
            "domain-analysis",
            "risk-identification",
        ),
        "mfi-incubation-lead": (
            "reasoning",
            "structured-output",
            "domain-analysis",
            "risk-identification",
        ),
    }
    for definition in definitions:
        agent_id = definition.registry_record.id
        manifest = definition.manifest
        assert definition.registry_record.status is AgentStatus.PLANNED
        assert definition.registry_record.version == "0.1.0"
        assert definition.registry_record.owner_id
        assert manifest.allowed_tools == ()
        assert manifest.authority_grant_ids == ()
        assert manifest.routing_policy.execution_policy is ExecutionPolicy.LOCAL_PREFERRED
        assert manifest.routing_policy.cloud_fallback_allowed is False
        assert manifest.allowed_data_classifications == (
            DataClassification.PUBLIC,
            DataClassification.INTERNAL,
        )
        assert manifest.audit_events == REQUIRED_AUDIT_EVENTS
        assert manifest.prompt_sources == (
            "prompts/agents/shared/governance.md",
            f"prompts/agents/cohort-1/{agent_id}/system.md",
        )
        assert manifest.capability_requirements == expected_capabilities[agent_id]
        if agent_id == "mfi-qa-auditor":
            assert manifest.input_contracts[0].id == "review-package"
            assert manifest.output_contracts[0].id == "assurance-report"
        elif agent_id != "mfi-orchestrator":
            assert manifest.input_contracts[0].id == "pillar-work-brief"
            assert manifest.output_contracts[0].id == "pillar-analysis"
        readiness = evaluate_readiness(definition)
        assert readiness.completeness is DefinitionCompleteness.COMPLETE
        assert readiness.eligibility is ActivationEligibility.BLOCKED
