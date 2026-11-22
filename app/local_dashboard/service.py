from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from app.agents.definitions.models import GovernedAgentDefinition, ReadinessReport
from app.agents.definitions.readiness import evaluate_all
from app.agents.definitions.service import AgentDefinitionService

from .models import (
    AcceptanceCriterionView, AgentDetailView, AgentSummaryView, ApprovalView,
    ContractView, DashboardCounts, DashboardSnapshot, HealthView, PillarView,
    PromptSourceView, PromptView, ReadinessGroupView,
)


_AGENT_ORDER = (
    "mfi-orchestrator", "mfi-qa-auditor", "mfi-infrastructure-lead",
    "mfi-tech-entertainment-lead", "mfi-investments-lead", "mfi-incubation-lead",
)
_PILLAR_ORDER = (
    "infrastructure-supply-chain", "technology-gaming-entertainment",
    "investments", "incubation",
)
_PILLAR_NAMES = {
    "infrastructure-supply-chain": "Infrastructure & Supply Chain",
    "technology-gaming-entertainment": "Technology / Gaming / Entertainment",
    "investments": "Investments",
    "incubation": "Incubation",
}
_ENTERPRISE_CATEGORIES = {
    "enterprise-orchestration": "COORDINATION",
    "quality-assurance": "ASSURANCE",
}
_SAFETY_BOUNDARIES = (
    "Definition completeness does not activate an agent.",
    "This dashboard cannot approve, execute, edit, save, or send work.",
    "Prompt review does not call a model or run an agent.",
)


class UnknownAgentError(LookupError):
    pass


class InconsistentSnapshotError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class _LoadedSnapshot:
    definitions: tuple[GovernedAgentDefinition, ...]
    reports: tuple[ReadinessReport, ...]
    generated_at: str


class LocalDashboardService:
    def __init__(
        self,
        definition_service: AgentDefinitionService,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._definition_service = definition_service
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _load(self) -> _LoadedSnapshot:
        definitions = self._definition_service.load_all()
        digests: dict[str, set[str]] = defaultdict(set)
        for definition in definitions:
            for source in definition.prompt_sources:
                digests[source.path].add(source.sha256_digest)
        inconsistent = sorted(path for path, values in digests.items() if len(values) > 1)
        if inconsistent:
            joined = ", ".join(inconsistent)
            raise InconsistentSnapshotError(
                f"prompt source changed during snapshot: {joined}; refresh to retry"
            )
        reports = evaluate_all(definitions)
        now = self._clock().astimezone(timezone.utc).isoformat(timespec="seconds")
        return _LoadedSnapshot(definitions, reports, now.replace("+00:00", "Z"))

    @staticmethod
    def _category(definition: GovernedAgentDefinition) -> str:
        role = definition.owner_role
        if role is not None and role.pillar_id is not None:
            return "PILLAR_LEAD"
        if role is not None:
            return _ENTERPRISE_CATEGORIES.get(role.id, "ENTERPRISE")
        return "ENTERPRISE"

    @staticmethod
    def _ordered(definitions: tuple[GovernedAgentDefinition, ...]) -> tuple[GovernedAgentDefinition, ...]:
        positions = {agent_id: index for index, agent_id in enumerate(_AGENT_ORDER)}
        return tuple(sorted(definitions, key=lambda item: (positions.get(item.registry_record.id, len(positions)), item.registry_record.id)))

    @staticmethod
    def _report_map(snapshot: _LoadedSnapshot) -> dict[str, ReadinessReport]:
        return {report.agent_id: report for report in snapshot.reports}

    def dashboard(self) -> DashboardSnapshot:
        snapshot = self._load()
        reports = self._report_map(snapshot)
        ordered = self._ordered(snapshot.definitions)
        summaries = tuple(self._summary(item, reports[item.registry_record.id]) for item in ordered)
        counts = DashboardCounts(
            definitions=len(ordered),
            complete=sum(item.completeness.value == "COMPLETE" for item in snapshot.reports),
            active=sum(item.registry_record.status.value == "ACTIVE" for item in ordered),
            planned=sum(item.registry_record.status.value == "PLANNED" for item in ordered),
            eligible=sum(item.eligibility.value == "ELIGIBLE" for item in snapshot.reports),
            blocked=sum(item.eligibility.value == "BLOCKED" for item in snapshot.reports),
            tools=sum(len(item.manifest.allowed_tools) for item in ordered),
            grants=sum(len(item.resolved_grants) for item in ordered),
        )
        return DashboardSnapshot(
            snapshot.generated_at, counts, self._pillars(ordered), summaries,
            self._readiness_groups(snapshot.reports), _SAFETY_BOUNDARIES,
        )

    def agent_detail(self, agent_id: str) -> AgentDetailView:
        snapshot = self._load()
        definition = self._find(snapshot.definitions, agent_id)
        report = self._report_map(snapshot)[agent_id]
        manifest = definition.manifest
        record = definition.registry_record
        contracts = lambda values: tuple(ContractView(item.id, item.description, item.required_fields) for item in values)
        return AgentDetailView(
            agent_id=record.id, display_name=record.display_name, purpose=record.purpose,
            version=record.version, owner_type=record.owner_type.value, owner_id=record.owner_id,
            role_category=self._category(definition), completeness=report.completeness.value,
            lifecycle=record.status.value, eligibility=report.eligibility.value,
            responsibilities=manifest.responsibilities,
            non_responsibilities=manifest.non_responsibilities,
            input_contracts=contracts(manifest.input_contracts),
            output_contracts=contracts(manifest.output_contracts),
            allowed_tools=manifest.allowed_tools, allowed_systems=manifest.allowed_systems,
            data_classifications=tuple(item.value for item in manifest.allowed_data_classifications),
            capability_requirements=manifest.capability_requirements,
            routing_execution_policy=manifest.routing_policy.execution_policy.value,
            cloud_fallback_allowed=manifest.routing_policy.cloud_fallback_allowed,
            approval_requirements=tuple(ApprovalView(item.id, item.trigger, item.approver.value) for item in manifest.approval_requirements),
            audit_events=manifest.audit_events,
            failure_on_validation=manifest.failure_behavior.on_validation_failure.value,
            failure_on_missing_authority=manifest.failure_behavior.on_missing_authority.value,
            failure_on_dependency=manifest.failure_behavior.on_dependency_failure.value,
            preserve_working_artifacts=manifest.failure_behavior.preserve_working_artifacts,
            escalation_destination=manifest.escalation.destination.value,
            escalation_include_evidence=manifest.escalation.include_evidence,
            escalation_conditions=manifest.escalation.conditions,
            acceptance_criteria=tuple(AcceptanceCriterionView(item.id, item.description, item.evidence_type.value) for item in manifest.acceptance_criteria),
            prompt_sources=self._sources(definition), blockers=report.blocker_codes,
        )

    def prompt(self, agent_id: str) -> PromptView:
        snapshot = self._load()
        definition = self._find(snapshot.definitions, agent_id)
        return PromptView(agent_id, definition.composed_prompt, self._sources(definition))

    def health(self) -> HealthView:
        snapshot = self._load()
        return HealthView("ok", True, snapshot.generated_at)

    def _summary(self, definition: GovernedAgentDefinition, report: ReadinessReport) -> AgentSummaryView:
        record = definition.registry_record
        return AgentSummaryView(
            record.id, record.display_name, record.purpose, record.owner_type.value,
            record.owner_id, self._category(definition), report.completeness.value,
            record.status.value, report.eligibility.value,
            len(definition.manifest.allowed_tools), len(definition.resolved_grants),
        )

    @staticmethod
    def _sources(definition: GovernedAgentDefinition) -> tuple[PromptSourceView, ...]:
        return tuple(PromptSourceView(item.path, item.sha256_digest) for item in definition.prompt_sources)

    @staticmethod
    def _find(definitions: tuple[GovernedAgentDefinition, ...], agent_id: str) -> GovernedAgentDefinition:
        for definition in definitions:
            if definition.registry_record.id == agent_id:
                return definition
        raise UnknownAgentError(f"unknown agent ID {agent_id!r}")

    @staticmethod
    def _pillars(definitions: tuple[GovernedAgentDefinition, ...]) -> tuple[PillarView, ...]:
        grouped: dict[str, list[str]] = defaultdict(list)
        descriptions: dict[str, str] = {}
        for definition in definitions:
            role = definition.owner_role
            if role is not None and role.pillar_id is not None:
                grouped[role.pillar_id.value].append(definition.registry_record.id)
                descriptions[role.pillar_id.value] = role.description
        return tuple(PillarView(item, _PILLAR_NAMES[item], descriptions.get(item, ""), tuple(grouped[item])) for item in _PILLAR_ORDER)

    @staticmethod
    def _readiness_groups(reports: tuple[ReadinessReport, ...]) -> tuple[ReadinessGroupView, ...]:
        rules = (
            ("lifecycle", "Lifecycle", lambda code: code.startswith("lifecycle-")),
            ("runtime", "Runtime implementation", lambda code: code == "runtime-implementation-missing"),
            ("runtime_tests", "Runtime tests", lambda code: code.startswith("runtime-test-")),
            ("audit", "Audit implementation", lambda code: code.startswith("audit-event-")),
            ("acceptance", "Acceptance criteria", lambda code: code.startswith("acceptance-criterion-")),
            ("human", "Accountable-human acceptance", lambda code: code == "accountable-human-acceptance-missing"),
        )
        all_codes = tuple(dict.fromkeys(code for report in reports for code in report.blocker_codes))
        return tuple(ReadinessGroupView(stage, label, tuple(code for code in all_codes if predicate(code))) for stage, label, predicate in rules)
