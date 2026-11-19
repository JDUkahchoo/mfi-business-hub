# Organizational Registry Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only, strictly validated organizational registry containing MFI roles, vacant seats, planned agents, and explicit authority grants.

**Architecture:** Immutable Python domain models live in `app/organization`, a read-only repository protocol separates consumers from storage, and a strict JSON adapter loads the canonical `config/organization/registry.json`. Shape errors and cross-record governance violations are reported as deterministic validation findings; a small CLI validates or summarizes the registry without mutation.

**Tech Stack:** Python standard library (`dataclasses`, `enum`, `json`, `pathlib`, `typing`, `argparse`, `re`, `types`), JSON, pytest 8+

**Spec:** `docs/superpowers/specs/2026-11-19-organizational-registry-core-design.md`

## Global Constraints

- Use only Python's standard library at runtime; add no framework, database, schema, model-provider, or AI SDK dependency.
- The only pillar IDs are `infrastructure-supply-chain`, `technology-gaming-entertainment`, `investments`, and `incubation`.
- Seat types are exactly `HUMAN`, `AI`, `HYBRID`, and `VACANT`.
- Agent statuses are exactly `PLANNED`, `DRAFT`, `TESTING`, `ACTIVE`, `SUSPENDED`, and `RETIRED`.
- Authority levels are exactly `READ`, `WRITE`, `PROPOSE`, `APPROVE`, and `EXECUTE`; levels never imply one another.
- All initial seats are `VACANT`, all 12 agents are `PLANNED` and owned by matching roles, and `authority_grants` is empty.
- Canonical identities must remain provider-independent; known provider/model names are invalid in agent IDs and display names.
- Registry loading is read-only, atomic, UTF-8, and rejects unknown fields, malformed types, duplicates, dangling references, and unsupported schema versions.
- No agent receives `APPROVE`; an agent `EXECUTE` grant requires `requires_human_approval: true`.
- Governance Markdown remains authoritative for policy; `config/organization/registry.json` is authoritative for structured registry records.

## Review Focus

- JSON booleans must not pass integer checks (`bool` is a Python `int` subclass); Task 3 pins exact type rejection.
- Duplicate IDs must not be silently accepted when read-only indexes are constructed; Task 3 pins both duplicate paths.
- A malformed record must not suppress independent errors in later records; Task 3 pins stable multi-error collection and ordering.
- CLI defaults must work from a current directory outside the repository; Task 5 pins repository-relative default-path resolution.
- Unexpected filesystem errors must produce a concise load error rather than a traceback or partial registry; Task 3 and Task 5 pin unreadable/missing-file behavior.

---

## File Structure

- Create `app/organization/models.py`: enums, immutable records, immutable indexes, and lookup helpers.
- Create `app/organization/errors.py`: structured findings and public registry exceptions.
- Create `app/organization/repository.py`: read-only repository protocol.
- Create `app/organization/validation.py`: cross-record governance and semantic validation.
- Create `app/organization/json_repository.py`: strict JSON shape parsing and atomic model construction.
- Create `app/organization/cli.py`: read-only `validate` and `summary` commands.
- Modify `app/organization/__init__.py`: publish the small supported public API.
- Create `config/organization/registry.json`: canonical schema-version-1 seed records.
- Create `tests/unit/organization/conftest.py`: reusable valid raw registry and temporary JSON fixtures.
- Create `tests/unit/organization/test_models.py`: enum, immutability, and lookup behavior.
- Create `tests/unit/organization/test_validation.py`: cross-record governance rules.
- Create `tests/unit/organization/test_json_repository.py`: JSON shape, type, and load failures.
- Create `tests/unit/organization/test_seed_registry.py`: committed seed parity and deny-by-default assertions.
- Create `tests/unit/organization/test_cli.py`: command output, default path, and exit behavior.
- Modify `docs/governance/AGENT_REGISTRY.md`: identify JSON as the structured record source without changing policy.
- Modify `HANDOFF.md`: record the Codex feature branch, implementation evidence, and next integration action.

### Task 1: Immutable domain model and repository contract

**Files:**
- Create: `app/organization/models.py`
- Create: `app/organization/repository.py`
- Modify: `app/organization/__init__.py`
- Create: `tests/unit/organization/test_models.py`

**Interfaces:**
- Consumes: no feature interfaces.
- Produces: `PillarId`, `SeatType`, `AuthorityLevel`, `AgentStatus`, `OwnerType`, `GrantSubjectType`, `RoleDefinition`, `SeatAssignment`, `AgentDefinition`, `AuthorityGrant`, `OrganizationRegistry`, and `OrganizationRepository.load() -> OrganizationRegistry`.

- [ ] **Step 1: Write failing enum and immutable-record tests**

Add tests named `test_governance_enums_have_exact_values`, `test_domain_records_are_immutable`, and `test_registry_collections_are_tuples`. Assert the exact values from Global Constraints and that field assignment raises `dataclasses.FrozenInstanceError`.

- [ ] **Step 2: Run the model tests and verify failure**

Run: `python -m pytest tests/unit/organization/test_models.py -q`

Expected: FAIL during import because `app.organization.models` does not exist.

- [ ] **Step 3: Implement enums and frozen record signatures**

In `models.py`, define:

```python
class PillarId(str, Enum): ...
class SeatType(str, Enum): ...
class AuthorityLevel(str, Enum): ...
class AgentStatus(str, Enum): ...
class OwnerType(str, Enum):  # SEAT, ROLE
class GrantSubjectType(str, Enum):  # SEAT, AGENT

@dataclass(frozen=True, slots=True)
class RoleDefinition:
    id: str
    display_name: str
    description: str
    pillar_id: PillarId | None = None

@dataclass(frozen=True, slots=True)
class SeatAssignment:
    id: str
    role_id: str
    seat_type: SeatType
    human_name: str | None = None
    agent_ids: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class AgentDefinition:
    id: str
    display_name: str
    purpose: str
    status: AgentStatus
    version: str
    owner_type: OwnerType
    owner_id: str

@dataclass(frozen=True, slots=True)
class AuthorityGrant:
    id: str
    subject_type: GrantSubjectType
    subject_id: str
    level: AuthorityLevel
    scope: str
    requires_human_approval: bool = False
```

- [ ] **Step 4: Write failing registry lookup and repository protocol tests**

Add `test_registry_builds_read_only_indexes_and_returns_records_by_id` and `test_repository_protocol_accepts_load_implementation`. Assert `get_role`, `get_seat`, and `get_agent` return known records or `None`; mutation through each exposed index raises `TypeError`; and a class with `load() -> OrganizationRegistry` satisfies the runtime-checkable protocol.

- [ ] **Step 5: Implement registry and protocol interfaces**

Define `OrganizationRegistry` as a frozen, slotted dataclass with tuple fields `roles`, `seats`, `agents`, and `authority_grants`; build private `MappingProxyType` indexes in `__post_init__`; expose `get_role(id)`, `get_seat(id)`, `get_agent(id)`, and read-only index properties. Define `@runtime_checkable class OrganizationRepository(Protocol)` with `load(self) -> OrganizationRegistry`.

- [ ] **Step 6: Export the supported public API and run tests**

Publish the domain records, enums, and protocol from `app/organization/__init__.py`.

Run: `python -m pytest tests/unit/organization/test_models.py -q`

Expected: all Task 1 tests PASS.

- [ ] **Step 7: Commit Task 1**

```bash
git add app/organization tests/unit/organization/test_models.py
git commit -m "feat: add organizational registry domain model"
```

### Task 2: Cross-record governance validation

**Files:**
- Create: `app/organization/errors.py`
- Create: `app/organization/validation.py`
- Create: `tests/unit/organization/conftest.py`
- Create: `tests/unit/organization/test_validation.py`

**Interfaces:**
- Consumes: all Task 1 model types.
- Produces: `ValidationFinding(path: str, message: str)`, `RegistryError`, `RegistryLoadError`, `RegistryValidationError(findings)`, and `validate_registry(registry: OrganizationRegistry) -> tuple[ValidationFinding, ...]`.

- [ ] **Step 1: Add a reusable valid registry fixture and failing relationship tests**

Create a smallest-valid fixture with one pillar role, one `VACANT` seat, one `PLANNED` role-owned agent, and no grants. Add tests for dangling `role_id`, dangling assigned agent, invalid `owner_id` for both `ROLE` and `SEAT`, and dangling grant subjects. Each test asserts the exact finding path such as `seats[0].role_id` and a message containing the missing ID.

- [ ] **Step 2: Run relationship tests and verify failure**

Run: `python -m pytest tests/unit/organization/test_validation.py -q`

Expected: FAIL because validation interfaces do not exist.

- [ ] **Step 3: Implement structured findings, exceptions, and reference validation**

`ValidationFinding` is frozen, ordered, and formats as `<path>: <message>`. `RegistryValidationError` stores a tuple of findings and joins their string forms in its message. `validate_registry` accumulates findings and returns them sorted by `(path, message)`.

- [ ] **Step 4: Write failing seat-content tests**

Parameterize all invalid combinations:

- `HUMAN`: missing/blank `human_name` or nonempty `agent_ids`;
- `AI`: present `human_name` or empty `agent_ids`;
- `HYBRID`: missing/blank `human_name` or empty `agent_ids`;
- `VACANT`: present `human_name` or nonempty `agent_ids`.

Also assert a valid example of each type has no seat-content finding.

- [ ] **Step 5: Implement exact seat-content validation and run focused tests**

Run: `python -m pytest tests/unit/organization/test_validation.py -q`

Expected: relationship and seat tests PASS.

- [ ] **Step 6: Write failing semantic and authority tests**

Add tests for malformed kebab IDs, duplicate IDs in every collection, non-semantic versions, wildcard or non-dotted scopes, known provider/model terms (`anthropic`, `claude`, `openai`, `grok`, `lmstudio`, `gemma`, `nemotron`) in agent IDs or display names, agent `APPROVE`, agent `EXECUTE` without human approval, and valid independent `READ`, `WRITE`, `PROPOSE`, and guarded `EXECUTE` grants. Assert an empty grant tuple is valid.

- [ ] **Step 7: Implement semantic and authority validation**

Use exact patterns:

- canonical ID: `^[a-z0-9]+(?:-[a-z0-9]+)*$`;
- version: `^\d+\.\d+\.\d+$`;
- scope: `^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$`.

Detect provider/model terms case-insensitively using both non-alphanumeric tokens and a compact alphanumeric form, so variants such as `LM Studio`, `lm-studio`, and `lmstudio` are equivalent. Do not infer authority between grants.

- [ ] **Step 8: Pin deterministic independent-error collection**

Add `test_validation_returns_all_independent_findings_in_stable_order` with invalid records in at least two collections. Assert the complete `(path, message)` tuple and verify repeated calls return the same sequence.

- [ ] **Step 9: Run Task 2 tests and commit**

Run: `python -m pytest tests/unit/organization/test_validation.py -q`

Expected: all Task 2 tests PASS.

```bash
git add app/organization/errors.py app/organization/validation.py tests/unit/organization
git commit -m "feat: validate organizational governance rules"
```

### Task 3: Strict JSON repository

**Files:**
- Create: `app/organization/json_repository.py`
- Create: `tests/unit/organization/test_json_repository.py`
- Modify: `tests/unit/organization/conftest.py`
- Modify: `app/organization/__init__.py`

**Interfaces:**
- Consumes: Task 1 models and repository protocol; Task 2 findings, exceptions, and `validate_registry`.
- Produces: `JsonOrganizationRepository(path: Path)`, `JsonOrganizationRepository.load() -> OrganizationRegistry`, and `parse_registry_data(data: object) -> OrganizationRegistry`.

- [ ] **Step 1: Write failing successful-load and strict-shape tests**

Add tests that load a complete valid temporary file and assert enum conversion and tuple fields. Parameterize missing and unknown top-level keys, missing and unknown record keys, wrong container types, wrong scalar types, and an integer supplied where a boolean is required.

- [ ] **Step 2: Run repository tests and verify failure**

Run: `python -m pytest tests/unit/organization/test_json_repository.py -q`

Expected: FAIL because `JsonOrganizationRepository` does not exist.

- [ ] **Step 3: Implement strict shape parsing and model construction**

Require top-level keys `schema_version`, `roles`, `seats`, `agents`, and `authority_grants`; accept only integer `schema_version == 1` while explicitly rejecting `bool`; require exact record key sets with only the documented optional keys; and validate scalar/container types before enum conversion. Convert lists to tuples. Collect shape findings across records in stable path order and raise one `RegistryValidationError`; construct and return no partial registry.

- [ ] **Step 4: Write failing duplicate and malformed-enum tests**

Assert duplicate IDs return findings for both later duplicate record paths without index overwrite, and invalid enum values produce record-field findings rather than raw `ValueError`.

- [ ] **Step 5: Integrate cross-record validation**

After shape-safe model construction, call `validate_registry`; raise `RegistryValidationError` when findings are nonempty, otherwise return the complete registry.

- [ ] **Step 6: Write failing file-boundary tests**

Add tests for missing path, unreadable path/directory path, malformed JSON with line and column, non-UTF-8 content, and unsupported `schema_version`. Assert each raises `RegistryLoadError` or `RegistryValidationError` as appropriate and does not expose a traceback in the exception text.

- [ ] **Step 7: Implement UTF-8 file loading and concise error translation**

`JsonOrganizationRepository.__init__(path: Path)` stores the path. `load()` uses `Path.read_text(encoding="utf-8")`, translates `OSError` and `UnicodeError` to `RegistryLoadError`, translates `json.JSONDecodeError` with line/column, and passes decoded data to `parse_registry_data`.

- [ ] **Step 8: Export repository API, run tests, and commit**

Run: `python -m pytest tests/unit/organization/test_json_repository.py tests/unit/organization/test_validation.py tests/unit/organization/test_models.py -q`

Expected: all Task 1–3 tests PASS.

```bash
git add app/organization tests/unit/organization
git commit -m "feat: load registry from strict JSON"
```

### Task 4: Canonical MFI seed registry and governance parity

**Files:**
- Create: `config/organization/registry.json`
- Create: `tests/unit/organization/test_seed_registry.py`
- Modify: `docs/governance/AGENT_REGISTRY.md`

**Interfaces:**
- Consumes: `JsonOrganizationRepository` from Task 3.
- Produces: canonical schema-version-1 data with 12 roles, 12 vacant seats, 12 planned role-owned agents, and zero authority grants.

- [ ] **Step 1: Write failing seed parity test**

Assert the canonical file loads and has:

- exactly 12 roles, 12 seats, 12 agents, and 0 grants;
- the four pillar roles mapped to the exact `PillarId` values;
- every seat `VACANT`, with `human_name is None` and `agent_ids == ()`;
- every agent `PLANNED`, version `0.1.0`, `owner_type == ROLE`, and an existing matching role;
- the exact 12 canonical IDs currently listed in `docs/governance/AGENT_REGISTRY.md`;
- no authority inferred from roles, seats, or agents.

- [ ] **Step 2: Run seed test and verify failure**

Run: `python -m pytest tests/unit/organization/test_seed_registry.py -q`

Expected: FAIL because `config/organization/registry.json` does not exist.

- [ ] **Step 3: Add the canonical seed data**

Create these matching role IDs and agents:

| Role ID | Agent ID | Pillar ID |
|---|---|---|
| `enterprise-orchestration` | `mfi-orchestrator` | none |
| `quality-assurance` | `mfi-qa-auditor` | none |
| `infrastructure-leadership` | `mfi-infrastructure-lead` | `infrastructure-supply-chain` |
| `technology-gaming-entertainment-leadership` | `mfi-tech-entertainment-lead` | `technology-gaming-entertainment` |
| `investments-leadership` | `mfi-investments-lead` | `investments` |
| `incubation-leadership` | `mfi-incubation-lead` | `incubation` |
| `business-development-leadership` | `mfi-business-development-lead` | none |
| `government-business-leadership` | `mfi-government-business-lead` | none |
| `private-sector-leadership` | `mfi-private-sector-lead` | none |
| `finance-leadership` | `mfi-cfo-copilot` | none |
| `operations-leadership` | `mfi-coo-copilot` | none |
| `technology-leadership` | `mfi-cto-copilot` | none |

Use seat ID `<role-id>-seat`; leave every seat vacant. Copy agent display name, purpose, and accountable-area meaning from the governance catalog without adding provider/model names or implementation claims.

- [ ] **Step 4: Clarify the governance source-of-truth boundary**

Update `docs/governance/AGENT_REGISTRY.md` to state that `config/organization/registry.json` is the canonical structured record source once present, while the Markdown remains the governance catalog and policy explanation. Preserve all existing IDs, meanings, statuses, and links.

- [ ] **Step 5: Run seed and full tests, then commit**

Run: `python -m pytest tests/unit -q`

Expected: all existing and new tests PASS.

```bash
git add config/organization/registry.json docs/governance/AGENT_REGISTRY.md tests/unit/organization/test_seed_registry.py
git commit -m "feat: seed canonical MFI organization registry"
```

### Task 5: Read-only CLI, documentation handoff, and final verification

**Files:**
- Create: `app/organization/cli.py`
- Create: `tests/unit/organization/test_cli.py`
- Modify: `HANDOFF.md`

**Interfaces:**
- Consumes: Task 3 `JsonOrganizationRepository` and Task 2 public errors; Task 4 canonical data.
- Produces: `main(argv: Sequence[str] | None = None) -> int` and executable `python -m app.organization.cli {validate,summary} [--registry PATH]`.

- [ ] **Step 1: Write failing CLI success tests**

Assert:

- `main(["validate", "--registry", path])` returns `0` and prints exactly `Registry valid.\n`;
- `main(["summary", "--registry", path])` returns `0` and prints exactly `Registry valid: 12 roles, 12 seats, 12 agents, 0 authority grants.\n`;
- neither command changes the registry file's bytes or modification time.

- [ ] **Step 2: Run CLI tests and verify failure**

Run: `python -m pytest tests/unit/organization/test_cli.py -q`

Expected: FAIL because `app.organization.cli` does not exist.

- [ ] **Step 3: Implement CLI parsing and success behavior**

Define `DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "config" / "organization" / "registry.json"`. Use subcommands `validate` and `summary`, both accepting optional `--registry PATH`, and return integer exit codes from `main`.

- [ ] **Step 4: Write failing CLI failure and external-current-directory tests**

Assert malformed, invalid, missing, and unreadable registry inputs return `2`, print one concise `error: ...` line per finding to stderr, and emit no traceback. Spawn `python -m app.organization.cli summary` with `cwd` set to a temporary external directory and `PYTHONPATH` set to the repository root; assert exit `0` and exact summary output.

- [ ] **Step 5: Implement concise error output and module entry point**

Catch only `RegistryLoadError` and `RegistryValidationError`; print stable errors to stderr; return `2`. Let programming errors surface. Add `if __name__ == "__main__": raise SystemExit(main())`.

- [ ] **Step 6: Run focused CLI tests and real commands**

Run: `python -m pytest tests/unit/organization/test_cli.py -q`

Expected: all CLI tests PASS.

Run: `python -m app.organization.cli validate`

Expected: `Registry valid.` and exit `0`.

Run: `python -m app.organization.cli summary`

Expected: `Registry valid: 12 roles, 12 seats, 12 agents, 0 authority grants.` and exit `0`.

- [ ] **Step 7: Update branch handoff**

Update `HANDOFF.md` with branch `feature/organizational-registry-core`, Codex as feature writer, Claude still responsible only for publishing the already-verified `main`, exact implementation commits, verification results, and the next action of independent branch review followed by Joshua's merge choice. Do not claim the feature is merged, pushed, or active.

- [ ] **Step 8: Run complete verification**

Run:

```bash
python -m pytest tests/unit -q
python -m app.organization.cli validate
python -m app.organization.cli summary
git diff --check main...HEAD
git status --short --branch
```

Expected: all tests pass; both commands exit `0` with exact approved output; diff check prints nothing; status shows the feature branch with no uncommitted files.

- [ ] **Step 9: Commit Task 5**

```bash
git add app/organization/cli.py tests/unit/organization/test_cli.py HANDOFF.md
git commit -m "feat: add registry validation CLI"
```

- [ ] **Step 10: Request independent review**

Have a fresh reviewer inspect `main...HEAD` for governance bypasses, incomplete validation, source-of-truth drift, unsafe error handling, and untested behaviors. Resolve every Critical or Important finding with a failing regression test before changing implementation; rerun Step 8 afterward.

## Completion Criteria

- The committed canonical registry loads atomically into immutable models.
- All 12 current agent identities are present exactly once, remain `PLANNED`, and contain no provider/model identity.
- All 12 initial seats are vacant and no authority grant exists.
- Invalid shape, types, enums, references, seat contents, IDs, versions, scopes, providers, and agent authority are rejected with deterministic findings.
- The read-only CLI works from inside or outside the repository and never mutates registry data.
- Existing repository and OpenCode policy tests still pass.
- Independent review has no unresolved Critical or Important findings.
