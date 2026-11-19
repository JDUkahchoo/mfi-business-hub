from dataclasses import FrozenInstanceError, fields

import pytest

from app.agents.definitions.models import (
    AcceptanceCriterion,
    ActivationEligibility,
    AgentManifest,
    ApprovalRequirement,
    ApproverType,
    ContractSpec,
    DataClassification,
    DefinitionCompleteness,
    EscalationDestination,
    EscalationPolicy,
    EvidenceType,
    ExecutionPolicy,
    FailureAction,
    FailureBehavior,
    GovernedAgentDefinition,
    LoadedPromptSource,
    ReadinessEvidence,
    ReadinessReport,
    RoutingPolicy,
    RuntimeTestCategory,
)
from app.organization import (
    AgentDefinition,
    AgentStatus,
    AuthorityGrant,
    AuthorityLevel,
    GrantSubjectType,
    OwnerType,
)
from app.agents.definitions import AgentManifestRepository as PublicRepository
from app.agents.definitions.errors import (
    AgentDefinitionError,
    DefinitionFinding,
    DefinitionLoadError,
    DefinitionValidationError,
)
from app.agents.definitions.policy import (
    AGENT_ID_PATTERN,
    AUDIT_EVENT_PATTERN,
    COHORT_1_AGENT_IDS,
    FIELD_NAME_PATTERN,
    KNOWN_SYSTEM_IDS,
    PROVIDER_MODEL_DENYLIST,
    REQUIRED_AUDIT_EVENTS,
    REQUIRED_PROMPT_HEADINGS,
)
from app.agents.definitions.repository import AgentManifestRepository


def test_policy_enums_expose_only_the_governed_values() -> None:
    assert tuple(item.value for item in DataClassification) == (
        "PUBLIC",
        "INTERNAL",
        "CONFIDENTIAL",
        "RESTRICTED",
        "LOCAL_ONLY",
    )
    assert tuple(item.value for item in ExecutionPolicy) == (
        "LOCAL_ONLY",
        "LOCAL_PREFERRED",
        "APPROVED_PROVIDER",
        "HUMAN_ONLY",
    )
    assert tuple(item.value for item in ApproverType) == ("ACCOUNTABLE_HUMAN",)
    assert tuple(item.value for item in EvidenceType) == (
        "TEST",
        "REVIEW",
        "HUMAN_ACCEPTANCE",
        "AUDIT_VERIFICATION",
    )
    assert tuple(item.value for item in FailureAction) == (
        "STOP_AND_ESCALATE",
        "PRESERVE_AND_ESCALATE",
    )
    assert tuple(item.value for item in EscalationDestination) == (
        "ACCOUNTABLE_OWNER",
    )
    assert tuple(item.value for item in DefinitionCompleteness) == (
        "COMPLETE",
        "INCOMPLETE",
    )
    assert tuple(item.value for item in ActivationEligibility) == (
        "ELIGIBLE",
        "BLOCKED",
    )
    assert tuple(item.value for item in RuntimeTestCategory) == (
        "NORMAL",
        "DENIED",
        "MALFORMED",
        "ESCALATION",
    )


def _manifest() -> AgentManifest:
    return AgentManifest(
        schema_version=1,
        agent_id="mfi-orchestrator",
        responsibilities=("Coordinate work.",),
        non_responsibilities=("Do not approve work.",),
        input_contracts=(
            ContractSpec("work-request", "Work to coordinate.", ("request_id",)),
        ),
        output_contracts=(
            ContractSpec("coordination-plan", "Proposed plan.", ("task_order",)),
        ),
        allowed_tools=(),
        allowed_systems=("mfi-business-hub",),
        allowed_data_classifications=(
            DataClassification.PUBLIC,
            DataClassification.INTERNAL,
        ),
        authority_grant_ids=(),
        approval_requirements=(
            ApprovalRequirement(
                "external-communication",
                "Before sending an external communication.",
                ApproverType.ACCOUNTABLE_HUMAN,
            ),
        ),
        prompt_sources=(
            "prompts/agents/shared/governance.md",
            "prompts/agents/cohort-1/mfi-orchestrator/system.md",
        ),
        capability_requirements=("reasoning", "structured-output"),
        routing_policy=RoutingPolicy(ExecutionPolicy.LOCAL_PREFERRED, False),
        audit_events=("agent.run.requested",),
        failure_behavior=FailureBehavior(
            FailureAction.STOP_AND_ESCALATE,
            FailureAction.STOP_AND_ESCALATE,
            FailureAction.PRESERVE_AND_ESCALATE,
            True,
        ),
        escalation=EscalationPolicy(
            EscalationDestination.ACCOUNTABLE_OWNER,
            True,
            ("Missing authority.",),
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                "normal-path-tested",
                "Normal behavior is verified.",
                EvidenceType.TEST,
            ),
        ),
    )


def test_domain_records_are_frozen_slotted_and_use_immutable_collections() -> None:
    manifest = _manifest()

    records = (
        manifest,
        manifest.input_contracts[0],
        manifest.approval_requirements[0],
        manifest.acceptance_criteria[0],
        manifest.routing_policy,
        manifest.failure_behavior,
        manifest.escalation,
    )
    for record in records:
        assert not hasattr(record, "__dict__")
        assert not hasattr(record, "update")
        with pytest.raises(FrozenInstanceError):
            setattr(record, fields(record)[0].name, None)

    assert isinstance(manifest.responsibilities, tuple)
    assert isinstance(manifest.allowed_data_classifications, tuple)
    assert isinstance(manifest.escalation.conditions, tuple)


def test_joined_definition_is_read_only_and_preserves_canonical_types() -> None:
    canonical = AgentDefinition(
        id="mfi-orchestrator",
        display_name="MFI Orchestrator",
        purpose="Coordinate work.",
        status=AgentStatus.PLANNED,
        version="0.1.0",
        owner_type=OwnerType.ROLE,
        owner_id="role-coo",
    )
    grant = AuthorityGrant(
        id="grant-read",
        subject_type=GrantSubjectType.AGENT,
        subject_id="mfi-orchestrator",
        level=AuthorityLevel.READ,
        scope="internal plans",
    )
    source = LoadedPromptSource(
        path="prompts/agents/shared/governance.md",
        text="Governance",
        sha256_digest="abc123",
    )
    definition = GovernedAgentDefinition(
        registry_record=canonical,
        manifest=_manifest(),
        prompt_sources=(source,),
        composed_prompt="Governance",
        resolved_grants=(grant,),
    )

    assert definition.registry_record is canonical
    assert definition.prompt_sources == (source,)
    assert definition.resolved_grants == (grant,)
    assert not hasattr(definition, "__dict__")
    with pytest.raises(FrozenInstanceError):
        definition.composed_prompt = "changed"


def test_readiness_records_default_to_no_evidence_and_ordered_blockers() -> None:
    evidence = ReadinessEvidence()

    assert evidence.runtime_implementation_verified is False
    assert evidence.runtime_test_categories == frozenset()
    assert evidence.verified_audit_events == frozenset()
    assert evidence.satisfied_acceptance_criteria == frozenset()
    assert evidence.accountable_human_accepted is False
    assert not hasattr(evidence, "__dict__")

    report = ReadinessReport(
        agent_id="mfi-orchestrator",
        completeness=DefinitionCompleteness.COMPLETE,
        eligibility=ActivationEligibility.BLOCKED,
        blocker_codes=("lifecycle-planned", "runtime-missing"),
    )
    assert report.blocker_codes == ("lifecycle-planned", "runtime-missing")
    with pytest.raises(FrozenInstanceError):
        report.blocker_codes = ()


def test_definition_findings_are_stable_sorted_and_share_public_error_base() -> None:
    later = DefinitionFinding("z.json.agent_id", "is invalid")
    earlier = DefinitionFinding("a.json.schema_version", "must equal 1")

    error = DefinitionValidationError((later, earlier))

    assert str(earlier) == "a.json.schema_version: must equal 1"
    assert error.findings == (earlier, later)
    assert str(error) == (
        "a.json.schema_version: must equal 1\n"
        "z.json.agent_id: is invalid"
    )
    assert isinstance(error, AgentDefinitionError)
    assert isinstance(DefinitionLoadError("bad input"), AgentDefinitionError)


def test_manifest_repository_protocol_is_structural_and_public() -> None:
    class InMemoryRepository:
        def load_all(self) -> tuple[AgentManifest, ...]:
            return (_manifest(),)

    repository = InMemoryRepository()

    assert isinstance(repository, AgentManifestRepository)
    assert isinstance(repository, PublicRepository)
    assert repository.load_all()[0].agent_id == "mfi-orchestrator"


def test_policy_catalog_exposes_exact_cohort_boundaries() -> None:
    assert COHORT_1_AGENT_IDS == frozenset(
        {
            "mfi-orchestrator",
            "mfi-qa-auditor",
            "mfi-infrastructure-lead",
            "mfi-tech-entertainment-lead",
            "mfi-investments-lead",
            "mfi-incubation-lead",
        }
    )
    assert REQUIRED_AUDIT_EVENTS == (
        "agent.run.requested",
        "agent.run.started",
        "agent.run.completed",
        "agent.run.failed",
        "agent.run.escalated",
    )
    assert REQUIRED_PROMPT_HEADINGS == (
        "## Purpose",
        "## Responsibilities",
        "## Inputs",
        "## Outputs",
        "## Boundaries",
        "## Escalation",
        "## Prohibited actions",
    )
    assert KNOWN_SYSTEM_IDS == frozenset({"mfi-business-hub"})
    assert PROVIDER_MODEL_DENYLIST == frozenset(
        {"anthropic", "claude", "openai", "grok", "lmstudio", "gemma", "nemotron"}
    )
    assert AGENT_ID_PATTERN.fullmatch("mfi-qa-auditor")
    assert not AGENT_ID_PATTERN.fullmatch("MFI QA")
    assert FIELD_NAME_PATTERN.fullmatch("request_id")
    assert not FIELD_NAME_PATTERN.fullmatch("request-id")
    assert AUDIT_EVENT_PATTERN.fullmatch("agent.run.started")
    assert not AUDIT_EVENT_PATTERN.fullmatch("Agent Run Started")
