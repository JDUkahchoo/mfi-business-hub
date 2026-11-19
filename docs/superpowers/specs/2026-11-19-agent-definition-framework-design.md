# Agent Definition Framework and Cohort 1 Design

## Intent

Complete the remaining agent-framework portion of Milestone 1 by making MFI agent definitions, prompt sources, configuration, and readiness checks executable and reviewable. The first production-shaped definitions cover only the six Cohort 1 agents:

- `mfi-orchestrator`
- `mfi-qa-auditor`
- `mfi-infrastructure-lead`
- `mfi-tech-entertainment-lead`
- `mfi-investments-lead`
- `mfi-incubation-lead`

Everything is built and reviewed locally on an isolated branch. Nothing in this project pushes to GitHub, calls a model, activates an agent, or grants runtime authority. Joshua will see readable prompt files and command-line validation/readiness output before deciding whether the pattern should be applied to the remaining six registered agents.

## Why Cohort 1 first

The six-agent cohort contains three meaningfully different roles: orchestration, independent quality review, and domain/pillar leadership. That is enough variety to test the framework without prematurely copying an unproven format across all 12 agents. Feedback from these definitions will shape the later cross-company and executive-copilot cohort.

## Goals

- Define one provider-independent manifest format for governed MFI agents.
- Join each manifest to the canonical identity, owner, lifecycle status, purpose, and version in `config/organization/registry.json` rather than duplicating those fields.
- Load and compose version-controlled shared governance instructions with an agent-specific prompt.
- Strictly validate manifest structure, prompt paths, prompt content, registry references, authority references, and policy values.
- Provide a visible summary and per-agent readiness report Joshua can inspect locally.
- Create complete, readable manifests and prompts for the six Cohort 1 agents.
- Keep all six agents `PLANNED`, unstaffed, unauthorized, and unable to execute.
- Update roadmap and governance status language so completed framework work is not still described as a scaffold.

## Non-goals

- No model calls, LM Studio connection, cloud-provider connection, embeddings, tools, job execution, or agent-to-agent delegation.
- No status transition from `PLANNED`.
- No authority grants, tool permissions, external system access, or approval decisions.
- No runtime prompt injection defenses beyond validating trusted version-controlled prompt assets; runtime input handling belongs with execution.
- No implementation of the six remaining registry agents.
- No web UI, API, authentication, database, audit persistence, permissions engine, approval engine, or Model Gateway.
- No GitHub push, pull request, or merge as part of implementation; integration remains a separate Joshua decision after local review.

## Anti-goals

The feature is a failure if it:

- duplicates canonical identity, lifecycle, version, purpose, or ownership in manifests and creates drift;
- treats a prompt file or complete manifest as activation;
- names or binds an MFI agent to Claude, OpenAI, Gemma, Nemotron, LM Studio, or another provider;
- grants authority or tool access that is absent from the organizational registry;
- permits prompt paths to escape the repository's `prompts/` directory;
- silently accepts unknown fields, missing prompt sections, malformed contracts, or stale agent references;
- reports an agent as activation-ready without human acceptance, runtime-path tests, and audit enforcement evidence;
- hides the work from Joshua until the end instead of exposing inspectable local checkpoints.

## Constraints and source-of-truth boundaries

- `config/organization/registry.json` remains authoritative for canonical agent ID, display name, purpose, version, lifecycle status, owner, seats, and authority grants.
- `docs/governance/AGENT_STANDARD.md` remains authoritative for required definition content and activation gates.
- `docs/governance/AUTHORITY_MATRIX.md` remains authoritative for permission meaning and non-delegable defaults.
- Agent manifests are authoritative only for operational specification fields not stored in the organization registry.
- Markdown prompt files under `prompts/` are authoritative prompt sources.
- OpenCode agent profiles remain development-assistant roles and are not MFI runtime agent definitions.
- Python's standard library and pytest remain the only implementation dependencies.

## Approaches considered

### 1. Typed manifests joined to the organization registry — selected

Store one strict JSON manifest per agent and join it at load time to the canonical registry record. Load shared and agent-specific Markdown prompt sources through a safe path boundary. This prevents identity drift, makes individual agents easy to inspect, and leaves a clean adapter boundary for a future database or Control Plane.

Tradeoff: the loader must validate relationships across JSON files, prompts, and the organization registry.

### 2. Put complete agent definitions inside the organization registry

This would reduce file count, but it would mix stable organizational identity with detailed prompt, routing, contract, audit, and acceptance configuration. Changes to an agent's operational behavior would make the core organization registry noisy and harder to govern.

### 3. Put behavior entirely in Markdown prompts

This is easy to read but difficult to validate reliably. Permissions, inputs, outputs, routing requirements, audit events, and readiness gates would become unstructured prose and could not safely support later runtime enforcement.

Approach 1 was selected because it preserves the source-of-truth boundaries already established in Milestone 1.

## Storage layout

```text
config/agents/cohort-1/
  mfi-orchestrator.json
  mfi-qa-auditor.json
  mfi-infrastructure-lead.json
  mfi-tech-entertainment-lead.json
  mfi-investments-lead.json
  mfi-incubation-lead.json

prompts/agents/shared/
  governance.md

prompts/agents/cohort-1/<agent-id>/
  system.md
```

The loader discovers JSON files in the explicit `config/agents/cohort-1/` directory in filename order. A manifest filename must equal `<agent_id>.json`. Hidden files, nested directories, non-JSON files, and duplicate IDs are rejected rather than ignored.

## Manifest format

Each manifest contains these exact top-level fields:

- `schema_version`: integer `1`.
- `agent_id`: canonical registry ID; the only identity field repeated in order to establish the join.
- `responsibilities`: nonempty list of distinct, nonblank statements.
- `non_responsibilities`: nonempty list of distinct, nonblank boundaries.
- `input_contracts`: nonempty list of named input contracts.
- `output_contracts`: nonempty list of named output contracts.
- `allowed_tools`: list of governed tool IDs; empty for all Cohort 1 definitions in this milestone.
- `allowed_systems`: list of governed system IDs; limited to `mfi-business-hub` for descriptive access, not runtime authorization.
- `allowed_data_classifications`: nonempty list drawn from the defined classification vocabulary.
- `authority_grant_ids`: list of exact grant IDs from the organization registry; empty for all Cohort 1 definitions.
- `approval_requirements`: nonempty list describing conditions that stop and escalate; these do not create approvals.
- `prompt_sources`: ordered list of repository-relative Markdown prompt paths.
- `capability_requirements`: nonempty list of provider-independent capability IDs.
- `routing_policy`: declarative routing constraints for later Model Gateway use.
- `audit_events`: nonempty list of event names a future runtime must emit.
- `failure_behavior`: structured stop, preserve, and report behavior.
- `escalation`: structured accountable-owner escalation behavior.
- `acceptance_criteria`: nonempty list of observable criteria required before lifecycle advancement.

Unknown fields are errors. Manifest data never repeats `display_name`, `purpose`, `status`, `version`, `owner_type`, or `owner_id`; the joined definition obtains those from the validated organization registry.

### Contracts

Each input/output contract has:

- `id`: lowercase kebab-case, unique within its direction;
- `description`: nonblank text;
- `required_fields`: a nonempty list of distinct lowercase snake-case field names.

Contracts describe the future structured boundary without executing or validating live task payloads in this milestone.

### Approval requirements

Each approval requirement is a structured record:

- `id`: lowercase kebab-case, unique within the manifest;
- `trigger`: nonblank description of the material action or condition;
- `approver`: exactly `ACCOUNTABLE_HUMAN` in this milestone.

The initial manifests include requirements for external communications, financial or contractual commitments, irreversible actions, regulated decisions, and any action exceeding an explicit grant. These records are declarations for a future approval engine and cannot create an approval.

### Acceptance criteria

Each acceptance criterion is a structured record:

- `id`: lowercase kebab-case, unique within the manifest;
- `description`: nonblank observable result;
- `evidence_type`: one of `TEST`, `REVIEW`, `HUMAN_ACCEPTANCE`, or `AUDIT_VERIFICATION`.

Criteria describe required evidence; a manifest cannot mark its own criterion satisfied.

### Routing policy

`routing_policy` has this exact shape:

```json
{
  "execution_policy": "LOCAL_PREFERRED",
  "cloud_fallback_allowed": false
}
```

Both keys are required and unknown keys are errors. Other execution-policy enum values are valid framework values for future definitions, but all six Cohort 1 manifests use the exact conservative values above.

### Failure behavior

`failure_behavior` has this exact shape:

```json
{
  "on_validation_failure": "STOP_AND_ESCALATE",
  "on_missing_authority": "STOP_AND_ESCALATE",
  "on_dependency_failure": "PRESERVE_AND_ESCALATE",
  "preserve_working_artifacts": true
}
```

Allowed action values are `STOP_AND_ESCALATE` and `PRESERVE_AND_ESCALATE`. Cohort 1 uses the exact values above; no retry, ignore, or continue behavior exists in this milestone.

### Escalation

`escalation` has this exact shape:

```json
{
  "destination": "ACCOUNTABLE_OWNER",
  "include_evidence": true,
  "conditions": ["..."]
}
```

`destination` is exactly `ACCOUNTABLE_OWNER`; `include_evidence` must be `true`; and `conditions` is a nonempty list of distinct, nonblank statements covering missing authority, conflicting instructions, unknown/incompatible data classification, insufficient evidence, and material uncertainty.

### Policy vocabularies

Data classifications are:

- `PUBLIC`
- `INTERNAL`
- `CONFIDENTIAL`
- `RESTRICTED`
- `LOCAL_ONLY`

Execution policies are:

- `LOCAL_ONLY`
- `LOCAL_PREFERRED`
- `APPROVED_PROVIDER`
- `HUMAN_ONLY`

Every Cohort 1 manifest uses `LOCAL_PREFERRED` with cloud fallback disabled. This is a conservative routing request for a future Model Gateway, not a model assignment. Cohort 1 allows only `PUBLIC` and `INTERNAL` data initially.

Capability IDs are lowercase kebab-case and provider-independent, such as `reasoning`, `structured-output`, `evidence-review`, `task-decomposition`, and `domain-analysis`. Provider or model names are rejected wherever agent-owned identifiers or display text appear.

Audit event names use lowercase dotted syntax. The initial required set is:

- `agent.run.requested`
- `agent.run.started`
- `agent.run.completed`
- `agent.run.failed`
- `agent.run.escalated`

Every Cohort 1 manifest must contain exactly these five distinct events, with no additions or omissions. Expanding the event vocabulary requires a reviewed policy/schema change. These are declared obligations for a later audited runtime; declaring them does not claim that audit persistence exists.

### Provider/model coupling boundary

The known brand/model token denylist initially contains `anthropic`, `claude`, `openai`, `grok`, `lmstudio`, `gemma`, and `nemotron`, with spacing and punctuation normalized. Validation applies it case-insensitively to every manifest string value and every loaded shared or agent-specific prompt. Generic terms such as `provider`, `local model`, and `cloud model` are allowed because they express provider-independent policy. Brand/model names are unnecessary even in negative instructions and are rejected consistently rather than interpreted by context.

## Prompt model

Every manifest references two prompt sources in this exact order:

1. `prompts/agents/shared/governance.md`
2. `prompts/agents/cohort-1/<agent-id>/system.md`

The shared prompt contains human-precedence, deny-by-default, evidence, data-minimization, no-self-approval, escalation, and no-provider-identity rules. Agent-specific prompts contain only role-specific behavior.

Each agent-specific prompt must contain these exact level-two headings once:

- `## Purpose`
- `## Responsibilities`
- `## Inputs`
- `## Outputs`
- `## Boundaries`
- `## Escalation`
- `## Prohibited actions`

The prompt loader:

- resolves paths against the repository root;
- rejects absolute paths, `..`, symlink/path escapes, non-`.md` files, duplicates, missing files, invalid UTF-8, empty files, and files outside `prompts/`;
- preserves source order and returns the source path with each text block;
- composes sources with an explicit separator that records provenance;
- never expands environment variables or template expressions;
- does not execute or interpolate prompt content.

## Domain and package design

Create a focused package under `app/agents/definitions/`:

- `models.py`: immutable enums and records for manifests, contracts, routing, escalation, failure behavior, prompt sources, joined definitions, and readiness reports.
- `errors.py`: load and validation findings with stable paths and deterministic ordering.
- `validation.py`: manifest-local and cross-source governance validation.
- `repository.py`: read-only definition-repository protocol.
- `json_repository.py`: strict manifest-directory and JSON loading.
- `prompt_loader.py`: safe Markdown source loading and composition.
- `service.py`: joins manifests, prompts, and organization registry records into immutable governed definitions.
- `readiness.py`: computes definition-completeness and activation-blocker reports without changing lifecycle state.
- `cli.py`: visible local `validate`, `summary`, `show`, and `readiness` commands.

`app/agents/__init__.py` exposes only the small supported public API. Provider-specific code remains absent; future provider adapters belong under `app/integrations/`.

## Joined definition

`GovernedAgentDefinition` combines:

- the canonical `AgentDefinition` from the organization registry;
- the validated `AgentManifest`;
- ordered loaded prompt sources;
- composed prompt text;
- resolved authority grants (empty for Cohort 1).

The join fails if:

- the agent ID is unknown, duplicated, or outside the six approved Cohort 1 IDs;
- the filename and `agent_id` differ;
- a registry agent lacks a manifest or a manifest lacks a registry agent in the requested cohort;
- an authority grant ID is missing, belongs to another subject, or exceeds the registry record;
- a prompt path is unsafe or invalid;
- manifest provider/model coupling is detected;
- the manifest attempts tool or system access that is not recognized by this milestone's policy catalog.

The joined definition is read-only. Loading it has no external effect.

## Cohort 1 definition content

### MFI Orchestrator

- Coordinates task decomposition, ownership recommendations, dependency ordering, and escalation drafts.
- Does not approve work, activate agents, assign itself authority, execute external actions, or choose a provider.
- Capabilities: `reasoning`, `structured-output`, `task-decomposition`, `coordination`.

### MFI QA Auditor

- Reviews evidence, output quality, policy alignment, missing approvals, and audit completeness.
- Does not approve its own findings, alter source work, suppress evidence, or act as final legal/financial authority.
- Capabilities: `reasoning`, `structured-output`, `evidence-review`, `policy-review`.

### Four Pillar Leads

- Analyze and draft plans within their registered pillar, identify dependencies and risks, and escalate cross-pillar or material decisions.
- Do not commit funds, sign terms, make regulated decisions, claim executive authority, or operate outside their pillar.
- Shared capabilities: `reasoning`, `structured-output`, `domain-analysis`, `risk-identification`.
- Each prompt names only its governed pillar and its approved scope; shared policy remains in the common governance prompt.

All six have empty `allowed_tools` and `authority_grant_ids` in this milestone.

## Readiness model

Readiness has two separate results so a complete definition is never confused with an active agent:

### Definition completeness

`COMPLETE` only when the registry record, manifest, prompt sources, contracts, boundaries, routing request, audit obligations, escalation behavior, and acceptance criteria all validate.

### Activation eligibility

`BLOCKED` until all Agent Standard quality gates have evidence. Initial blockers for every Cohort 1 agent include:

- lifecycle status is `PLANNED`;
- no runtime implementation exists;
- no normal, denied, malformed, or escalation-path runtime test evidence exists;
- no audit-event implementation evidence exists;
- no accountable-human acceptance record exists.

Empty tools and grants are valid deny-by-default configuration, not validation errors. The readiness service reports blockers but never changes status, writes evidence, or activates an agent.

### Readiness evidence interface

Readiness is not hard-coded, but this milestone does not persist evidence. `evaluate_readiness` accepts an immutable optional `ReadinessEvidence`; omission means no evidence exists. The record contains:

- `runtime_implementation_verified: bool`;
- `runtime_test_categories: frozenset` drawn from `NORMAL`, `DENIED`, `MALFORMED`, and `ESCALATION`;
- `verified_audit_events: frozenset[str]`;
- `satisfied_acceptance_criteria: frozenset[str]`;
- `accountable_human_accepted: bool`.

The evaluator validates evidence references against the definition, reports missing gates, and remains read-only. There is no evidence repository, signer, approval record, or trust claim yet. Even fully populated test evidence cannot make a `PLANNED` registry agent activation-eligible; lifecycle and future enforcement gates still block it. This establishes the durable input boundary later milestones can populate without pretending evidence currently exists.

## Visible local review experience

Joshua can inspect the work at four checkpoints:

1. File tree and one representative manifest before the remaining five are patterned.
2. Shared governance prompt and one role-specific prompt before all prompts are finalized.
3. Validation summary showing all six definitions and loaded prompt sources.
4. Readiness report showing six complete definitions and zero activation-eligible agents, with blocker reasons.

CLI behavior:

```text
python -m app.agents.definitions.cli validate
6 Cohort 1 definitions valid; 12 prompt sources loaded; 0 authority grants resolved.

python -m app.agents.definitions.cli summary
mfi-orchestrator                 COMPLETE  PLANNED  BLOCKED
mfi-qa-auditor                   COMPLETE  PLANNED  BLOCKED
...

python -m app.agents.definitions.cli show mfi-orchestrator
[human-readable joined metadata, contracts, prompt source paths, and readiness; no prompt text]

python -m app.agents.definitions.cli show mfi-orchestrator --with-prompt
[the same report followed by composed prompt text with source provenance]

python -m app.agents.definitions.cli readiness
6 definition-complete; 0 activation-eligible; 6 blocked.
```

`show` hides prompt text by default; `--with-prompt` makes the local, version-controlled prompt visible when Joshua wants to review it. Commands are read-only and support explicit repository/config paths for tests. Ordinary data errors print concise stable diagnostics without tracebacks.

## Error handling

- Directory, file, UTF-8, JSON, and duplicate-member failures become concise load errors.
- Shape and semantic findings are accumulated when independent and sorted by path/message.
- Unsafe prompt paths fail before file content is read.
- No partial definition set is returned when any requested Cohort 1 definition fails.
- Programming errors are not disguised as configuration errors.
- No loader rewrites manifests, prompts, registry data, or lifecycle status.

## Testing and acceptance

Tests cover:

- immutable manifest, prompt, joined-definition, and readiness records;
- exact enum and policy vocabularies;
- strict JSON keys, types, enums, duplicate members, duplicate IDs, and filename/ID parity;
- missing/extra Cohort 1 definitions and registry joins;
- malformed contracts, blank/duplicate statements, provider/model coupling, unsafe tool/system IDs, and policy syntax;
- authority-grant resolution and attempts to expand authority;
- safe prompt containment, traversal, absolute path, symlink escape, extension, duplicate path, UTF-8, missing file, empty file, and required headings;
- deterministic multi-error output with original file/record locations;
- exact Cohort 1 agent IDs, registry status/version/owner joins, empty tools/grants, and prompt source order;
- definition-complete versus activation-blocked separation;
- readiness evidence validation, missing evidence gates, and the rule that evidence cannot activate a `PLANNED` agent;
- CLI success, failure, external-current-directory behavior, exact counts, and read-only file behavior;
- `show` output with prompt text hidden by default and exposed only with `--with-prompt`;
- continued success of all organizational registry and OpenCode policy tests.

Acceptance criteria:

1. The complete unit suite passes.
2. All four CLI commands work locally against the committed assets.
3. Exactly six Cohort 1 definitions load; the remaining six registry agents do not gain manifests in this project.
4. All six remain registry status `PLANNED`, with no tools, authority grants, runtime, or provider binding.
5. Readiness reports six `COMPLETE` definitions and zero activation-eligible agents.
6. Joshua is shown representative files and the final local reports before any integration or push choice.
7. Independent review has no unresolved Critical or Important findings.

## Documentation updates

- Update `docs/ROADMAP.md` current position to reflect completion of the organization registry and agent-definition framework while stating that no runtime agent exists.
- Update `docs/governance/AGENT_REGISTRY.md` to distinguish `PLANNED` agents with complete definition assets from activated implementations.
- Update `HANDOFF.md` with the local branch, exact verification, visible-review checkpoints, and next decision.
- Add a short operator guide under `docs/operations/` for inspecting definitions and readiness locally.

## Builder calls

The builder may choose:

- internal helper names and private parsing functions;
- test-fixture organization;
- column spacing and deterministic formatting details for CLI tables;
- the exact separator text between composed prompt sources, provided source provenance is visible;
- whether manifest discovery is implemented with `Path.iterdir()` or `glob()`, provided only the explicit directory's direct `.json` files are accepted and ordering is deterministic.

The builder may not broaden agent scope, add tools or grants, change lifecycle status, add providers, weaken prompt containment, or create definitions for the remaining six agents.

## Delivery boundary

This project ends with a locally validated agent-definition framework, six complete Cohort 1 definition packages, inspectable prompts, and readiness output that keeps every agent blocked from activation. Model routing, runtime execution, permissions enforcement, approvals, audit persistence, and Cohort 1 agent behavior remain later projects.
