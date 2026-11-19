# Agent Definition Framework and Cohort 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, read-only agent-definition framework with complete manifests and inspectable prompts for the six Cohort 1 agents while keeping every agent `PLANNED` and activation-blocked.

**Architecture:** Strict per-agent JSON manifests are loaded from one explicit directory, joined to canonical organization-registry records, and composed with safely contained Markdown prompt sources. Immutable services expose validated definitions and readiness reports; a read-only CLI makes the local work visible without model calls, runtime execution, authority changes, or GitHub publication.

**Tech Stack:** Python standard library (`dataclasses`, `enum`, `json`, `pathlib`, `argparse`, `re`, `hashlib`, `types`, `typing`), Markdown assets, JSON, pytest 8+

**Spec:** `docs/superpowers/specs/2026-11-19-agent-definition-framework-design.md`

## Global Constraints

- Build only on `feature/agent-definition-loader`; do not push, merge, call external services, or change `main`.
- Runtime code uses only Python's standard library.
- Implement exactly the six approved Cohort 1 IDs; create no manifests or prompts for the remaining six registry agents.
- Canonical display name, purpose, status, version, owner, seats, and authority remain sourced from `config/organization/registry.json` and never appear in manifests.
- All six registry agents remain `PLANNED`; manifests use empty `allowed_tools` and `authority_grant_ids`.
- All six use `LOCAL_PREFERRED` with `cloud_fallback_allowed: false`, and allow only `PUBLIC` and `INTERNAL` data.
- Every definition references shared governance first and its own system prompt second.
- Reject unknown JSON fields, wrong types, booleans used as integers, duplicate JSON members, duplicate IDs, unsafe paths, invalid UTF-8, missing headings, and provider/model coupling.
- The provider/model denylist is `anthropic`, `claude`, `openai`, `grok`, `lmstudio`, `gemma`, and `nemotron`, normalized across case, whitespace, and punctuation and applied to all manifest and prompt strings.
- Every Cohort 1 manifest declares exactly the five audit events named in the spec.
- Loading, validation, showing, and readiness evaluation are read-only and never interpolate prompt content.
- Definition completeness and activation eligibility remain separate; no evidence can make a `PLANNED` agent activation-eligible.

## Review Focus

- A prompt path that is lexically inside `prompts/` but resolves through a symlink/junction outside it must be rejected; Task 3 pins resolved containment.
- Case-insensitive filename/agent-ID mismatches on Windows must not silently load the wrong definition; Task 2 pins exact lowercase filename parity.
- A manifest with one malformed record must not hide independent errors in another file; Task 2 pins deterministic cross-file error accumulation.
- Readiness evidence containing unknown test categories, audit events, or criterion IDs must be rejected rather than counted; Task 4 pins every reference boundary.
- `show` must never print composed prompt text unless `--with-prompt` is present, including error paths; Task 7 pins default-output secrecy and explicit reveal behavior.

---

## File Structure

- Create `app/agents/definitions/__init__.py`: supported public API.
- Create `app/agents/definitions/models.py`: immutable manifest, joined-definition, prompt, evidence, and readiness records and enums.
- Create `app/agents/definitions/errors.py`: deterministic definition findings and public exceptions.
- Create `app/agents/definitions/policy.py`: exact Cohort 1 IDs, vocabularies, audit events, prompt headings, known systems, and denylist.
- Create `app/agents/definitions/repository.py`: read-only manifest repository protocol.
- Create `app/agents/definitions/validation.py`: domain and governance validation.
- Create `app/agents/definitions/json_repository.py`: strict directory discovery and JSON parsing.
- Create `app/agents/definitions/prompt_loader.py`: contained prompt loading and composition.
- Create `app/agents/definitions/service.py`: organization/manifest/prompt join.
- Create `app/agents/definitions/readiness.py`: completeness and activation evaluation.
- Create `app/agents/definitions/cli.py`: read-only local inspection commands.
- Modify `app/agents/__init__.py`: export the small supported framework API.
- Create `config/agents/cohort-1/*.json`: six manifests.
- Create `prompts/agents/shared/governance.md`: shared rules.
- Create `prompts/agents/cohort-1/<agent-id>/system.md`: six role prompts.
- Create `tests/unit/agents/`: domain, repository, prompt, service, readiness, asset, and CLI tests.
- Create `docs/operations/AGENT_DEFINITION_INSPECTION.md`: local review guide.
- Modify `docs/ROADMAP.md`, `docs/governance/AGENT_REGISTRY.md`, `docs/architecture/ARCHITECTURE.md`, and `HANDOFF.md`: accurate implementation status and transfer.

### Task 1: Immutable definition domain and contracts

**Files:**
- Create: `app/agents/definitions/models.py`
- Create: `app/agents/definitions/errors.py`
- Create: `app/agents/definitions/policy.py`
- Create: `app/agents/definitions/repository.py`
- Create: `app/agents/definitions/__init__.py`
- Create: `tests/unit/agents/test_definition_models.py`

**Interfaces:**
- Consumes: `AgentDefinition` and `AuthorityGrant` from `app.organization`.
- Produces: enums `DataClassification`, `ExecutionPolicy`, `ApproverType`, `EvidenceType`, `FailureAction`, `EscalationDestination`, `DefinitionCompleteness`, `ActivationEligibility`, `RuntimeTestCategory`; immutable records `ContractSpec`, `ApprovalRequirement`, `AcceptanceCriterion`, `RoutingPolicy`, `FailureBehavior`, `EscalationPolicy`, `AgentManifest`, `LoadedPromptSource`, `GovernedAgentDefinition`, `ReadinessEvidence`, `ReadinessReport`; errors `DefinitionFinding`, `AgentDefinitionError`, `DefinitionLoadError`, `DefinitionValidationError`; and runtime-checkable `AgentManifestRepository.load_all() -> tuple[AgentManifest, ...]`.

- [ ] **Step 1: Write failing enum and immutable-record tests**

Assert exact enum values from the spec, frozen/slotted records, tuple/frozenset collection fields, and read-only joined definitions. Verify `ReadinessEvidence()` defaults to false/empty values and no record exposes a mutation method.

- [ ] **Step 2: Run Task 1 tests and verify missing imports**

Run: `python -m pytest tests/unit/agents/test_definition_models.py -q`

Expected: collection/import failure because `app.agents.definitions` does not exist.

- [ ] **Step 3: Implement exact domain records**

Use these required signatures:

```python
@dataclass(frozen=True, slots=True)
class ContractSpec:
    id: str
    description: str
    required_fields: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class RoutingPolicy:
    execution_policy: ExecutionPolicy
    cloud_fallback_allowed: bool

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
```

Define `GovernedAgentDefinition` with canonical registry record, manifest, loaded prompt sources, composed prompt, and resolved grants. Define `ReadinessReport` with agent ID, completeness, eligibility, and ordered blocker codes.

- [ ] **Step 4: Write failing error/protocol/public-API tests**

Assert `DefinitionFinding` formats `<path>: <message>`, `DefinitionValidationError` sorts/exposes findings, load and validation errors share `AgentDefinitionError`, and a structural repository with `load_all()` satisfies the protocol.

- [ ] **Step 5: Implement error, policy, protocol, and exports**

Policy constants must include the exact six IDs, five audit events, seven prompt headings, known system `mfi-business-hub`, field-name patterns, and provider/model denylist from Global Constraints.

- [ ] **Step 6: Verify and commit Task 1**

Run: `python -m pytest tests/unit/agents/test_definition_models.py tests/unit -q`

Expected: new tests and the existing 108-test baseline PASS.

```bash
git add app/agents tests/unit/agents
git commit -m "feat: add agent definition domain model"
```

### Task 2: Strict manifest validation and repository

**Files:**
- Create: `app/agents/definitions/validation.py`
- Create: `app/agents/definitions/json_repository.py`
- Create: `tests/unit/agents/conftest.py`
- Create: `tests/unit/agents/test_manifest_validation.py`
- Create: `tests/unit/agents/test_manifest_repository.py`

**Interfaces:**
- Consumes: Task 1 models, policy, errors, and repository protocol.
- Produces: `validate_manifest(manifest: AgentManifest) -> tuple[DefinitionFinding, ...]`, `parse_manifest_data(data: object, source: str) -> AgentManifest`, and `JsonAgentManifestRepository(directory: Path, expected_agent_ids: frozenset[str] = COHORT_1_AGENT_IDS).load_all() -> tuple[AgentManifest, ...]`.

- [ ] **Step 1: Create a complete valid raw-manifest fixture and failing successful-parse test**

The fixture uses `mfi-orchestrator`, empty tools/grants, `mfi-business-hub`, `PUBLIC`/`INTERNAL`, exact routing/failure/escalation shapes, exact audit events, two prompt sources, at least one input/output contract, structured approvals, and structured acceptance criteria. Assert enum conversion and immutable tuples.

- [ ] **Step 2: Run the focused repository test and verify failure**

Run: `python -m pytest tests/unit/agents/test_manifest_repository.py::test_parses_complete_manifest -q`

Expected: FAIL because parser/repository do not exist.

- [ ] **Step 3: Implement strict single-manifest parsing**

Reject non-object roots, missing/unknown keys at every level, wrong scalar/list types, `bool` as integer schema version, invalid enums, duplicate JSON members, and unsupported schema versions. Gather independent shape findings in stable path order and return no partial manifest.

- [ ] **Step 4: Write failing semantic validation tests**

Cover malformed/duplicate IDs, blank or duplicate statements, empty contracts, invalid required fields, nonexact routing/failure/escalation settings, unknown system/tool IDs, data classification outside `PUBLIC`/`INTERNAL` for Cohort 1, nonempty grants/tools, provider/model tokens anywhere in nested manifest strings, missing/extra audit events, duplicate prompt sources, and unsafe filename/agent-ID mismatch.

- [ ] **Step 5: Implement manifest semantic validation**

Normalize brand/model scanning across punctuation and spacing. Validate every nested string recursively while permitting generic `provider`, `local model`, and `cloud model`. Return all independent findings sorted by `(path, message)`.

- [ ] **Step 6: Write failing directory-discovery and cross-file tests**

Cover missing/not-directory paths, invalid UTF-8, malformed JSON, duplicate JSON members, direct non-JSON files, hidden files, nested directories, duplicate IDs, exact lowercase filename parity, case-only mismatch, missing/extra expected Cohort 1 IDs, deterministic filename ordering, and one malformed file plus an independent error in a later file.

- [ ] **Step 7: Implement atomic directory loading**

Read direct entries only. Reject unexpected entries rather than ignoring them. Preserve source filename in every diagnostic and raise one `DefinitionValidationError` containing all independently discoverable findings. Return no manifests if any file fails.

- [ ] **Step 8: Verify and commit Task 2**

Run: `python -m pytest tests/unit/agents/test_manifest_validation.py tests/unit/agents/test_manifest_repository.py tests/unit -q`

Expected: all existing and Task 1–2 tests PASS.

```bash
git add app/agents/definitions/validation.py app/agents/definitions/json_repository.py tests/unit/agents
git commit -m "feat: validate agent definition manifests"
```

### Task 3: Safe prompt loading and composition

**Files:**
- Create: `app/agents/definitions/prompt_loader.py`
- Create: `tests/unit/agents/test_prompt_loader.py`

**Interfaces:**
- Consumes: `LoadedPromptSource`, policy headings/denylist, and definition errors.
- Produces: `PromptLoader(repo_root: Path)`, `PromptLoader.load(paths: tuple[str, ...]) -> tuple[LoadedPromptSource, ...]`, and `compose_prompt(sources: tuple[LoadedPromptSource, ...]) -> str`.

- [ ] **Step 1: Write failing successful-load/composition tests**

Create temporary shared and agent Markdown files with all required agent-specific headings. Assert source order, repository-relative paths, unchanged UTF-8 text, SHA-256 digest, and deterministic composed output with visible source provenance.

- [ ] **Step 2: Run prompt tests and verify failure**

Run: `python -m pytest tests/unit/agents/test_prompt_loader.py -q`

Expected: FAIL because `PromptLoader` does not exist.

- [ ] **Step 3: Implement lexical and resolved containment before reading**

Reject absolute paths, empty paths, `..`, non-`.md` suffixes, paths outside `prompts/`, duplicates, missing/not-file targets, and resolved paths outside the resolved prompt root. Do not expand variables or templates.

- [ ] **Step 4: Write failing content-policy tests**

Cover invalid UTF-8, empty/whitespace files, repeated/missing required headings in agent-specific prompts, provider/model tokens in shared or specific text, and a symlink/junction from inside `prompts/` to an outside file. Skip only the symlink construction test when the host cannot create one; resolved-containment behavior still receives a platform-neutral unit test.

- [ ] **Step 5: Implement content validation and composition**

Shared governance is exempt only from role-specific heading requirements, never from brand/model scanning. Agent-specific prompt paths under `cohort-1` require every exact heading once. `compose_prompt` inserts a stable provenance banner per source and never interpolates content.

- [ ] **Step 6: Verify and commit Task 3**

Run: `python -m pytest tests/unit/agents/test_prompt_loader.py tests/unit -q`

Expected: all tests PASS.

```bash
git add app/agents/definitions/prompt_loader.py tests/unit/agents/test_prompt_loader.py
git commit -m "feat: load governed prompt sources safely"
```

### Task 4: Definition join service and readiness evaluator

**Files:**
- Create: `app/agents/definitions/service.py`
- Create: `app/agents/definitions/readiness.py`
- Create: `tests/unit/agents/test_definition_service.py`
- Create: `tests/unit/agents/test_readiness.py`

**Interfaces:**
- Consumes: `OrganizationRepository`, `AgentManifestRepository`, `PromptLoader`, Task 1 models/errors/policy, and canonical authority grants.
- Produces: `AgentDefinitionService(organization_repository, manifest_repository, prompt_loader).load_all() -> tuple[GovernedAgentDefinition, ...]`, `evaluate_readiness(definition: GovernedAgentDefinition, evidence: ReadinessEvidence | None = None) -> ReadinessReport`, and `evaluate_all(definitions, evidence_by_agent=None) -> tuple[ReadinessReport, ...]`.

- [ ] **Step 1: Write failing successful-join tests**

Use in-memory repositories and real temporary prompts. Assert six/selected requested IDs join canonical display/purpose/status/version/owner from the organization registry, prompt source order is preserved, empty grant IDs resolve to an empty tuple, and loading changes no input files.

- [ ] **Step 2: Run service tests and verify failure**

Run: `python -m pytest tests/unit/agents/test_definition_service.py -q`

Expected: FAIL because service does not exist.

- [ ] **Step 3: Implement atomic registry-manifest-prompt join**

Load the organization registry once per call. Reject unknown/out-of-cohort IDs, missing/extra requested manifests, nonmatching filenames already surfaced by the repository, invalid owner references, authority grants that do not exist or do not target the agent/its human-owned seat, and any prompt failure. Sort definitions by agent ID and return none on error.

- [ ] **Step 4: Write failing readiness tests**

Assert a valid joined definition is `COMPLETE` but `BLOCKED` with exact ordered codes for `PLANNED`, missing runtime implementation, four missing runtime test categories, missing five audit verifications, missing acceptance criteria evidence, and missing human acceptance. Assert fully populated evidence still leaves `PLANNED` blocked. Reject unknown evidence agent IDs, categories, audit events, and criterion IDs.

- [ ] **Step 5: Implement typed, read-only readiness evaluation**

Readiness consumes evidence but stores nothing and changes no lifecycle state. Definition-completeness failures are reported before evidence gaps. Blocker codes are stable lowercase kebab-case strings sorted in policy order, not alphabetically.

- [ ] **Step 6: Verify and commit Task 4**

Run: `python -m pytest tests/unit/agents/test_definition_service.py tests/unit/agents/test_readiness.py tests/unit -q`

Expected: all tests PASS.

```bash
git add app/agents/definitions/service.py app/agents/definitions/readiness.py tests/unit/agents
git commit -m "feat: join definitions and report readiness"
```

### Task 5: Shared governance and representative Orchestrator definition

**Files:**
- Create: `prompts/agents/shared/governance.md`
- Create: `prompts/agents/cohort-1/mfi-orchestrator/system.md`
- Create: `config/agents/cohort-1/mfi-orchestrator.json`
- Create: `tests/unit/agents/test_cohort_assets.py`

**Interfaces:**
- Consumes: Tasks 2–4 loaders/services with expected IDs configurable to `{mfi-orchestrator}` for this checkpoint.
- Produces: the first complete production-shaped definition package and a reusable content pattern Joshua can inspect before the other five are added.

- [ ] **Step 1: Write failing representative-asset test**

Assert the Orchestrator manifest uses exact conservative policies, empty tools/grants, exact two prompt paths, capabilities `reasoning`, `structured-output`, `task-decomposition`, and `coordination`, canonical registry join, complete definition status, and blocked activation.

- [ ] **Step 2: Run the representative test and verify missing assets**

Run: `python -m pytest tests/unit/agents/test_cohort_assets.py::test_orchestrator_definition_package -q`

Expected: FAIL because representative manifest/prompts do not exist.

- [ ] **Step 3: Write shared governance prompt**

Cover human precedence, deny-by-default authority/tools, evidence/provenance, data minimization, no self-approval, stop-before-external-effect, escalation with preserved work, provider-independent identity, untrusted inputs, and no claim of officer/employee status. Use no brand/model names.

- [ ] **Step 4: Write Orchestrator manifest and prompt**

Prompt sections must cover task decomposition, recommended ownership/dependencies, structured coordination plan, material-risk escalation, and explicit prohibitions on approval, activation, external execution, self-authority, and provider selection. Contracts are `task-brief` input and `coordination-plan` output with explicit snake-case fields.

- [ ] **Step 5: Verify representative package and show local checkpoint**

Run: `python -m pytest tests/unit/agents/test_cohort_assets.py::test_orchestrator_definition_package -q`

Expected: PASS.

Show Joshua the three local files and a concise joined-definition/readiness output in commentary; continue unless he redirects the active work.

- [ ] **Step 6: Commit Task 5**

```bash
git add config/agents/cohort-1/mfi-orchestrator.json prompts/agents tests/unit/agents/test_cohort_assets.py
git commit -m "feat: define MFI Orchestrator"
```

### Task 6: Complete all six Cohort 1 definition packages

**Files:**
- Create: the five remaining `config/agents/cohort-1/*.json` manifests.
- Create: the five remaining `prompts/agents/cohort-1/<agent-id>/system.md` files.
- Modify: `tests/unit/agents/test_cohort_assets.py`

**Interfaces:**
- Consumes: representative pattern and all framework services.
- Produces: exactly six canonical, definition-complete, activation-blocked Cohort 1 packages.

- [ ] **Step 1: Write failing six-agent parity tests**

Assert exact six IDs and filenames; two prompt sources each; canonical registry fields; exact audit events; empty tools/grants; conservative routing; exact capability sets; no remaining-six manifests; and six `COMPLETE`/`BLOCKED` readiness results.

Capability sets:

- QA Auditor: `reasoning`, `structured-output`, `evidence-review`, `policy-review`.
- Each Pillar Lead: `reasoning`, `structured-output`, `domain-analysis`, `risk-identification`.

Input/output contracts:

- QA Auditor: `review-package` -> `assurance-report`.
- Each Pillar Lead: `pillar-work-brief` -> `pillar-analysis`.

- [ ] **Step 2: Run parity tests and verify five packages are missing**

Run: `python -m pytest tests/unit/agents/test_cohort_assets.py -q`

Expected: FAIL listing the five missing manifest IDs/files.

- [ ] **Step 3: Add QA Auditor package**

Define evidence/quality/policy review, missing-approval and audit-completeness findings, and structured assurance output. Prohibit self-approval, source alteration, evidence suppression, and final regulated determinations.

- [ ] **Step 4: Add four Pillar Lead packages**

Each uses its canonical pillar only, shared manifest shape, and role-specific purpose/boundaries. Define analysis, planning, dependencies, risks, and escalation. Prohibit funds, contracts, regulated decisions, executive claims, external effects, and out-of-pillar work.

- [ ] **Step 5: Verify six packages and show local checkpoint**

Run: `python -m pytest tests/unit/agents/test_cohort_assets.py tests/unit -q`

Expected: exactly six packages load; all tests PASS.

Show Joshua the six-agent ID/status/readiness summary in commentary.

- [ ] **Step 6: Commit Task 6**

```bash
git add config/agents/cohort-1 prompts/agents/cohort-1 tests/unit/agents/test_cohort_assets.py
git commit -m "feat: define Cohort 1 agents"
```

### Task 7: Inspection CLI, documentation, and handoff

**Files:**
- Create: `app/agents/definitions/cli.py`
- Create: `tests/unit/agents/test_definition_cli.py`
- Create: `docs/operations/AGENT_DEFINITION_INSPECTION.md`
- Modify: `app/agents/definitions/__init__.py`
- Modify: `app/agents/__init__.py`
- Modify: `docs/ROADMAP.md`
- Modify: `docs/governance/AGENT_REGISTRY.md`
- Modify: `docs/architecture/ARCHITECTURE.md`
- Modify: `HANDOFF.md`

**Interfaces:**
- Consumes: canonical organization repository, manifest repository, prompt loader, service, and readiness evaluator.
- Produces: `main(argv: Sequence[str] | None = None) -> int` and `python -m app.agents.definitions.cli {validate,summary,show,readiness}`.

- [ ] **Step 1: Write failing CLI success/read-only tests**

Assert exact validate count `6 definitions`, `12 prompt sources`, and `0 authority grants`; deterministic six-row summary; readiness count `6 definition-complete; 0 activation-eligible; 6 blocked`; `show mfi-orchestrator` includes metadata/contracts/paths/blockers but no prompt body; `--with-prompt` includes both source provenance banners and text; and no command changes bytes or modification times of registry, manifests, or prompts.

- [ ] **Step 2: Run CLI tests and verify failure**

Run: `python -m pytest tests/unit/agents/test_definition_cli.py -q`

Expected: FAIL because CLI does not exist.

- [ ] **Step 3: Implement CLI success behavior and safe defaults**

Resolve default repository paths from `__file__`, not current working directory. Sort all output by agent ID. Print prompt content only when `show` receives `--with-prompt`.

- [ ] **Step 4: Write failing CLI error/external-directory tests**

Cover unknown agent ID, malformed manifest, unsafe prompt path, missing directory, concise one-line-per-finding stderr, no traceback, exit `2`, and all commands working with an external current directory plus repository `PYTHONPATH`.

- [ ] **Step 5: Implement expected-error handling and module entry point**

Catch only public load/validation errors, never programming errors. Escape control characters in diagnostics so one finding remains one output line. Add `raise SystemExit(main())` module execution.

- [ ] **Step 6: Write local inspection guide and correct status docs**

Document the four commands, local-only/no-activation boundary, `--with-prompt`, and how to interpret blockers. Mark Milestone 0 complete, Milestone 1 framework complete, and runtime/authority/model work pending. Update architecture implementation status without claiming an agent runtime exists. Update the governance catalog to state six definitions exist while all statuses remain `PLANNED`.

- [ ] **Step 7: Update handoff and run pre-commit local verification**

Record branch ownership, exact commits, local-only state, visible checkpoints, test/CLI evidence, independent-review next action, and the rule that nothing is pushed without Joshua's choice.

Run:

```bash
python -m pytest tests/unit -q
python -m app.agents.definitions.cli validate
python -m app.agents.definitions.cli summary
python -m app.agents.definitions.cli readiness
python -m app.agents.definitions.cli show mfi-orchestrator
git diff --check main...HEAD
git status --short --branch
```

Expected: all tests pass; exact six/12/zero counts; six complete and blocked; no prompt text in default show; diff check clean; status lists only the intended Task 7 changes.

- [ ] **Step 8: Commit Task 7**

```bash
git add app/agents docs HANDOFF.md tests/unit/agents/test_definition_cli.py
git commit -m "feat: add local agent definition inspection"
```

- [ ] **Step 9: Repeat complete verification on the committed branch**

Repeat every Step 7 command.

Expected: all functional outputs remain exact, diff check is clean, and status shows `feature/agent-definition-loader` with no uncommitted files.

- [ ] **Step 10: Request independent whole-branch review**

Review `main...HEAD` for authority expansion, false activation/readiness claims, identity drift, unsafe prompt containment, provider coupling, strict-parser gaps, source-of-truth drift, prompt disclosure, and untested reasonable-user behavior. Resolve every Critical or Important finding with a failing regression test before code changes; rerun Step 7 afterward. Show Joshua the final local reports and defer push/merge choice to him.

## Completion Criteria

- Exactly six Cohort 1 manifests and six agent-specific prompts load with one shared governance prompt.
- Canonical identity/lifecycle/version/ownership come only from the organization registry.
- Definitions are immutable, provider-independent, prompt-contained, and strict-schema validated.
- All six definitions are `COMPLETE`, remain `PLANNED`, and are `BLOCKED` from activation.
- Tools and authority grants remain empty; no runtime/model/network behavior exists.
- Joshua can inspect representative files, six-agent summaries, readiness blockers, and prompt text locally.
- All existing and new tests pass, independent review has no unresolved Critical/Important findings, and nothing is pushed without Joshua's explicit choice.
