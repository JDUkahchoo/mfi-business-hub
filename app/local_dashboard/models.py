from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DashboardCounts:
    definitions: int
    complete: int
    active: int
    planned: int
    eligible: int
    blocked: int
    tools: int
    grants: int

    def to_payload(self) -> dict[str, object]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class PillarView:
    pillar_id: str
    display_name: str
    description: str
    agent_ids: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {"pillar_id": self.pillar_id, "display_name": self.display_name,
                "description": self.description, "agent_ids": list(self.agent_ids)}


@dataclass(frozen=True, slots=True)
class ContractView:
    id: str
    description: str
    required_fields: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {"id": self.id, "description": self.description,
                "required_fields": list(self.required_fields)}


@dataclass(frozen=True, slots=True)
class ApprovalView:
    id: str
    trigger: str
    approver: str

    def to_payload(self) -> dict[str, object]:
        return {"id": self.id, "trigger": self.trigger, "approver": self.approver}


@dataclass(frozen=True, slots=True)
class AcceptanceCriterionView:
    id: str
    description: str
    evidence_type: str

    def to_payload(self) -> dict[str, object]:
        return {"id": self.id, "description": self.description,
                "evidence_type": self.evidence_type}


@dataclass(frozen=True, slots=True)
class PromptSourceView:
    path: str
    sha256: str

    def to_payload(self) -> dict[str, object]:
        return {"path": self.path, "sha256": self.sha256}


@dataclass(frozen=True, slots=True)
class ReadinessGroupView:
    stage: str
    label: str
    blocker_codes: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {"stage": self.stage, "label": self.label,
                "blocker_codes": list(self.blocker_codes)}


@dataclass(frozen=True, slots=True)
class AgentSummaryView:
    agent_id: str
    display_name: str
    purpose: str
    owner_type: str
    owner_id: str
    role_category: str
    completeness: str
    lifecycle: str
    eligibility: str
    tools: int
    grants: int

    def to_payload(self) -> dict[str, object]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class AgentDetailView:
    agent_id: str
    display_name: str
    purpose: str
    version: str
    owner_type: str
    owner_id: str
    role_category: str
    completeness: str
    lifecycle: str
    eligibility: str
    responsibilities: tuple[str, ...]
    non_responsibilities: tuple[str, ...]
    input_contracts: tuple[ContractView, ...]
    output_contracts: tuple[ContractView, ...]
    allowed_tools: tuple[str, ...]
    allowed_systems: tuple[str, ...]
    data_classifications: tuple[str, ...]
    capability_requirements: tuple[str, ...]
    routing_execution_policy: str
    cloud_fallback_allowed: bool
    approval_requirements: tuple[ApprovalView, ...]
    audit_events: tuple[str, ...]
    failure_on_validation: str
    failure_on_missing_authority: str
    failure_on_dependency: str
    preserve_working_artifacts: bool
    escalation_destination: str
    escalation_include_evidence: bool
    escalation_conditions: tuple[str, ...]
    acceptance_criteria: tuple[AcceptanceCriterionView, ...]
    prompt_sources: tuple[PromptSourceView, ...]
    blockers: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "agent_id": self.agent_id, "display_name": self.display_name,
            "purpose": self.purpose, "version": self.version,
            "owner_type": self.owner_type, "owner_id": self.owner_id,
            "role_category": self.role_category, "completeness": self.completeness,
            "lifecycle": self.lifecycle, "eligibility": self.eligibility,
            "responsibilities": list(self.responsibilities),
            "non_responsibilities": list(self.non_responsibilities),
            "input_contracts": [item.to_payload() for item in self.input_contracts],
            "output_contracts": [item.to_payload() for item in self.output_contracts],
            "allowed_tools": list(self.allowed_tools),
            "allowed_systems": list(self.allowed_systems),
            "data_classifications": list(self.data_classifications),
            "capability_requirements": list(self.capability_requirements),
            "routing": {"execution_policy": self.routing_execution_policy,
                        "cloud_fallback_allowed": self.cloud_fallback_allowed},
            "approvals": [item.to_payload() for item in self.approval_requirements],
            "audit_events": list(self.audit_events),
            "failure_behavior": {
                "on_validation_failure": self.failure_on_validation,
                "on_missing_authority": self.failure_on_missing_authority,
                "on_dependency_failure": self.failure_on_dependency,
                "preserve_working_artifacts": self.preserve_working_artifacts,
            },
            "escalation": {"destination": self.escalation_destination,
                           "include_evidence": self.escalation_include_evidence,
                           "conditions": list(self.escalation_conditions)},
            "acceptance_criteria": [item.to_payload() for item in self.acceptance_criteria],
            "prompt_sources": [item.to_payload() for item in self.prompt_sources],
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    generated_at: str
    counts: DashboardCounts
    pillars: tuple[PillarView, ...]
    agents: tuple[AgentSummaryView, ...]
    readiness_blockers: tuple[ReadinessGroupView, ...]
    safety_boundaries: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "generated_at": self.generated_at,
            "counts": self.counts.to_payload(),
            "pillars": [item.to_payload() for item in self.pillars],
            "agents": [item.to_payload() for item in self.agents],
            "readiness_blockers": [item.to_payload() for item in self.readiness_blockers],
            "safety_boundaries": list(self.safety_boundaries),
        }


@dataclass(frozen=True, slots=True)
class PromptView:
    agent_id: str
    composed_prompt: str
    sources: tuple[PromptSourceView, ...]

    def to_payload(self) -> dict[str, object]:
        return {"agent_id": self.agent_id, "composed_prompt": self.composed_prompt,
                "sources": [item.to_payload() for item in self.sources]}


@dataclass(frozen=True, slots=True)
class HealthView:
    status: str
    snapshot_valid: bool
    generated_at: str

    def to_payload(self) -> dict[str, object]:
        return {"status": self.status, "snapshot_valid": self.snapshot_valid,
                "generated_at": self.generated_at}


VIEW_MODEL_TYPES = (
    DashboardCounts, PillarView, ContractView, ApprovalView,
    AcceptanceCriterionView, PromptSourceView, ReadinessGroupView,
    AgentSummaryView, AgentDetailView, DashboardSnapshot, PromptView, HealthView,
)
