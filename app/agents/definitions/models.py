from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.organization import AgentDefinition, AuthorityGrant, RoleDefinition


class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    LOCAL_ONLY = "LOCAL_ONLY"


class ExecutionPolicy(str, Enum):
    LOCAL_ONLY = "LOCAL_ONLY"
    LOCAL_PREFERRED = "LOCAL_PREFERRED"
    APPROVED_PROVIDER = "APPROVED_PROVIDER"
    HUMAN_ONLY = "HUMAN_ONLY"


class ApproverType(str, Enum):
    ACCOUNTABLE_HUMAN = "ACCOUNTABLE_HUMAN"


class EvidenceType(str, Enum):
    TEST = "TEST"
    REVIEW = "REVIEW"
    HUMAN_ACCEPTANCE = "HUMAN_ACCEPTANCE"
    AUDIT_VERIFICATION = "AUDIT_VERIFICATION"


class FailureAction(str, Enum):
    STOP_AND_ESCALATE = "STOP_AND_ESCALATE"
    PRESERVE_AND_ESCALATE = "PRESERVE_AND_ESCALATE"


class EscalationDestination(str, Enum):
    ACCOUNTABLE_OWNER = "ACCOUNTABLE_OWNER"


class DefinitionCompleteness(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class ActivationEligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    BLOCKED = "BLOCKED"


class RuntimeTestCategory(str, Enum):
    NORMAL = "NORMAL"
    DENIED = "DENIED"
    MALFORMED = "MALFORMED"
    ESCALATION = "ESCALATION"


@dataclass(frozen=True, slots=True)
class ContractSpec:
    id: str
    description: str
    required_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ApprovalRequirement:
    id: str
    trigger: str
    approver: ApproverType


@dataclass(frozen=True, slots=True)
class AcceptanceCriterion:
    id: str
    description: str
    evidence_type: EvidenceType


@dataclass(frozen=True, slots=True)
class RoutingPolicy:
    execution_policy: ExecutionPolicy
    cloud_fallback_allowed: bool


@dataclass(frozen=True, slots=True)
class FailureBehavior:
    on_validation_failure: FailureAction
    on_missing_authority: FailureAction
    on_dependency_failure: FailureAction
    preserve_working_artifacts: bool


@dataclass(frozen=True, slots=True)
class EscalationPolicy:
    destination: EscalationDestination
    include_evidence: bool
    conditions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AgentManifest:
    schema_version: int
    agent_id: str
    responsibilities: tuple[str, ...]
    non_responsibilities: tuple[str, ...]
    input_contracts: tuple[ContractSpec, ...]
    output_contracts: tuple[ContractSpec, ...]
    allowed_tools: tuple[str, ...]
    allowed_systems: tuple[str, ...]
    allowed_data_classifications: tuple[DataClassification, ...]
    authority_grant_ids: tuple[str, ...]
    approval_requirements: tuple[ApprovalRequirement, ...]
    prompt_sources: tuple[str, ...]
    capability_requirements: tuple[str, ...]
    routing_policy: RoutingPolicy
    audit_events: tuple[str, ...]
    failure_behavior: FailureBehavior
    escalation: EscalationPolicy
    acceptance_criteria: tuple[AcceptanceCriterion, ...]


@dataclass(frozen=True, slots=True)
class LoadedPromptSource:
    path: str
    text: str
    sha256_digest: str


@dataclass(frozen=True, slots=True)
class GovernedAgentDefinition:
    registry_record: AgentDefinition
    manifest: AgentManifest
    prompt_sources: tuple[LoadedPromptSource, ...]
    composed_prompt: str
    resolved_grants: tuple[AuthorityGrant, ...]
    owner_role: RoleDefinition | None = None


@dataclass(frozen=True, slots=True)
class ReadinessEvidence:
    runtime_implementation_verified: bool = False
    runtime_test_categories: frozenset[RuntimeTestCategory] = field(
        default_factory=frozenset
    )
    verified_audit_events: frozenset[str] = field(default_factory=frozenset)
    satisfied_acceptance_criteria: frozenset[str] = field(default_factory=frozenset)
    accountable_human_accepted: bool = False


@dataclass(frozen=True, slots=True)
class ReadinessReport:
    agent_id: str
    completeness: DefinitionCompleteness
    eligibility: ActivationEligibility
    blocker_codes: tuple[str, ...]
