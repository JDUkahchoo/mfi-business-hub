# Organizational Registry Core Design

## Intent

The first MFI Business Hub product capability will turn the existing organization, agent, and authority governance documents into a small executable registry. It gives future Control Plane, permissions, approval, agent-routing, and audit features one validated source for answering four basic questions:

1. What business pillars and organizational roles exist?
2. Who or what occupies each organizational seat?
3. Which governed AI agents exist, and who is accountable for them?
4. What authority has been explicitly granted within a defined scope?

This foundation is for Joshua and future MFI operators, as well as the software components that will consume the registry. It must preserve human authority and provider-independent agent identity from the start.

## Goals

- Represent the four MFI business pillars and cross-company functions without confusing the latter for additional pillars.
- Represent organizational roles and `HUMAN`, `AI`, `HYBRID`, and `VACANT` seat assignments.
- Represent canonical agents using the lifecycle states already defined by governance.
- Represent explicit `READ`, `WRITE`, `PROPOSE`, `APPROVE`, and `EXECUTE` grants within named scopes.
- Load the registry from version-controlled JSON and reject invalid or internally inconsistent data with clear, deterministic errors.
- Seed the registry with the organizational and Cohort 1 agent identities already approved in the governance documents.
- Provide a read-only command that validates the registry and prints a concise summary for humans and automation.
- Keep domain behavior independent of web frameworks, databases, model providers, and AI SDKs.

## Non-goals

- No web UI, API server, authentication, database, or networking.
- No live model calls, LM Studio integration, agent execution, job routing, or prompt implementation.
- No approval workflow, audit persistence, or enforcement at an external system boundary yet.
- No automatic authority inheritance or inference.
- No activation of any agent. Seeded agents remain `PLANNED`.
- No attempt to model every future department, employee, contractor, or legal entity.

## Anti-goals

The feature is a failure if it:

- lets a vacant human seat transfer authority to an AI agent;
- treats a model or provider name as the identity of an MFI agent;
- grants authority implicitly because a role, seat, or agent exists;
- allows dangling references, duplicate identities, or silently ignored malformed data;
- creates a second source of truth that drifts from the governance documents;
- introduces infrastructure or framework dependencies before they are needed.

## Constraints and source of truth

The implementation must conform to:

- `docs/governance/ORGANIZATION.md` for pillars, seat types, human precedence, and cross-company functions;
- `docs/governance/AGENT_STANDARD.md` for agent definition and lifecycle requirements;
- `docs/governance/AUTHORITY_MATRIX.md` for authority semantics and non-delegable defaults;
- `docs/governance/AGENT_REGISTRY.md` for canonical agent IDs and initial status;
- `docs/architecture/ARCHITECTURE.md` for package boundaries and provider independence.

The current repository is a Python scaffold with `pytest` and no application framework. The core will therefore use Python's standard library and JSON. JSON remains an interim version-controlled store until a deliberate database milestone.

The source-of-truth boundary is explicit:

- governance Markdown remains authoritative for organizational policy, authority semantics, agent standards, and lifecycle rules;
- `config/organization/registry.json` becomes authoritative for structured role, seat, agent, and grant records once this feature lands;
- `docs/governance/AGENT_REGISTRY.md` remains the human-readable governance catalog and must point to the structured registry instead of presenting itself as a competing runtime record store;
- parity tests pin the initially approved canonical agent IDs and statuses so an update cannot silently change only one representation.

Future record changes update the structured registry first and include any corresponding governance-catalog change in the same reviewed commit. Future policy changes begin in governance Markdown and include any required registry changes in the same reviewed commit.

## Approaches considered

### 1. Python domain models with validated JSON storage — selected

Define typed Python domain objects, load declarative JSON through a strict repository boundary, and validate both record shape and cross-record business rules. This produces executable behavior now, is dependency-light, and can later sit behind an API or database adapter without changing the domain language.

Tradeoff: some schema validation code must be written and maintained in Python instead of relying on a framework.

### 2. JSON-only registry and schema files

Store records as JSON and validate them with JSON Schema. This is simple for configuration, but cross-record rules such as accountable-seat references, human precedence, and agent/role relationships are awkward. It would also leave future application code without a clear domain model.

### 3. Database-backed registry with an API

Build persistence, migrations, and endpoints immediately. This is closer to the future Control Plane, but it prematurely selects infrastructure and substantially expands the first milestone before the domain rules have stabilized.

Approach 1 was selected because it creates the stable domain boundary needed by both later approaches while keeping the first build small and testable.

## Domain model

All identifiers are stable lowercase kebab-case strings. Display names are separate from IDs.

### Enumerations

- `PillarId`: the four fixed pillar IDs:
  - `infrastructure-supply-chain`
  - `technology-gaming-entertainment`
  - `investments`
  - `incubation`
- `SeatType`: `HUMAN`, `AI`, `HYBRID`, `VACANT`.
- `AuthorityLevel`: `READ`, `WRITE`, `PROPOSE`, `APPROVE`, `EXECUTE`.
- `AgentStatus`: `PLANNED`, `DRAFT`, `TESTING`, `ACTIVE`, `SUSPENDED`, `RETIRED`.
- `OwnerType`: `SEAT` or `ROLE`, used to make agent accountability explicit without inventing a person record.

### Records

`RoleDefinition`

- `id`
- `display_name`
- `description`
- optional `pillar_id`; omitted for enterprise or cross-company roles

`SeatAssignment`

- `id`
- `role_id`
- `seat_type`
- optional `human_name`
- zero or more `agent_ids`

Seat content rules:

- `HUMAN` requires `human_name` and has no assigned agents.
- `AI` requires at least one agent and has no `human_name`.
- `HYBRID` requires both `human_name` and at least one agent.
- `VACANT` has neither a human name nor assigned agents.

The human name is a display value in this milestone, not an authentication identity. A future identity system may replace it with a user reference.

`AgentDefinition`

- `id`
- `display_name`
- `purpose`
- `status`
- `version`
- `owner_type`
- `owner_id`

The owner reference must resolve to a known seat or role according to `owner_type`. Provider and model fields are deliberately absent. Operational requirements such as prompts, tools, routing policy, and audit events remain future agent-implementation records; they are not fabricated for agents that are still only `PLANNED`.

`AuthorityGrant`

- `id`
- `subject_type`: `SEAT` or `AGENT`
- `subject_id`
- `level`
- `scope`
- optional `requires_human_approval`, defaulting to `false`

`scope` is an explicit lowercase dotted name such as `organization.registry.read`; wildcards are rejected in this milestone. Each grant provides exactly one authority level. Levels are not cumulative: every permitted level must be separately granted.

`OrganizationRegistry`

- immutable collections of roles, seats, agents, and authority grants
- indexed lookup helpers by canonical ID
- summary counts for the validation command

## Storage layout

Use one canonical file:

`config/organization/registry.json`

Top-level keys are:

- `schema_version`
- `roles`
- `seats`
- `agents`
- `authority_grants`

One file makes review of the small initial graph straightforward and allows validation to be atomic. The loader exposes a repository interface so the JSON adapter can later be replaced by a database without changing consumers.

The initial seed will include:

- a role and seat for each of the four pillar leads;
- enterprise orchestration and quality-assurance roles/seats;
- business development, government business, and private-sector roles/seats;
- human finance, operations, and technology leadership roles/seats supporting the three executive copilots;
- all 12 canonical agents currently listed in `AGENT_REGISTRY.md`, all with status `PLANNED`;
- every seat as `VACANT`, with no human name and no assigned agent, because staffing has not been approved;
- each planned agent accountable to its matching role through an `owner_type: ROLE` reference, without implying that it occupies the vacant seat;
- no authority grants by default.

Leaving every seat vacant and the initial grant list empty is intentional: the seed describes approved organizational definitions, not actual staffing, activation, or authority. Those require later explicit decisions.

## Package and component design

`app/organization/models.py`

- enum and immutable dataclass definitions
- no file access or framework imports

`app/organization/errors.py`

- `RegistryError` base class
- structured load and validation errors with record location and human-readable reason

`app/organization/validation.py`

- ID, enum, required-field, seat-content, reference, provider-independence, and authority-scope rules
- returns all deterministic validation findings in stable order rather than stopping at the first problem

`app/organization/repository.py`

- read-only repository protocol consumed by application code

`app/organization/json_repository.py`

- strict UTF-8 JSON loading
- rejects unknown keys, missing keys, wrong types, duplicate IDs, and unsupported `schema_version`
- constructs models only after validation succeeds

`app/organization/cli.py`

- read-only `validate` and `summary` behavior through `python -m app.organization.cli`
- exit code `0` for a valid registry and nonzero for invalid input
- no mutation commands

## Validation rules

The validator will enforce:

1. Canonical IDs match lowercase kebab-case and are unique within each record type.
2. The four allowed pillar IDs are fixed; cross-company roles have no `pillar_id`.
3. Every role, seat, agent owner, assigned agent, and grant subject reference resolves.
4. Seat content matches its `SeatType` exactly.
5. A registered agent assigned to seats has a single accountable owner reference, but may support more than one seat only if the seed data explicitly lists those assignments.
6. Agent IDs and display names may not encode configured provider/model identifiers. The first denylist covers known routing providers/models from project documentation and is kept in validation policy, not in the models.
7. Agent versions are non-empty semantic versions such as `0.1.0`.
8. Authority scopes are explicit dotted identifiers with no wildcard.
9. Every grant level is independent; no higher level implies a lower one.
10. `APPROVE` grants to agents are rejected in this milestone. `EXECUTE` grants to agents require `requires_human_approval: true`. This conservative rule implements the current default boundary without claiming to solve every future policy exception.
11. Empty authority grants are valid and mean deny by default.
12. Unknown fields are errors so misspellings cannot silently weaken policy.

Human precedence is expressed structurally: a `HYBRID` seat always has a human owner, and a `VACANT` seat cannot contain agents. The registry does not calculate succession or transfer authority.

## Read and validation flow

```text
registry.json
    -> strict JSON shape checks
    -> domain and cross-reference validation
    -> immutable OrganizationRegistry
    -> read-only lookup or summary
```

On failure, no partial registry is returned. The caller receives a stable list of findings that identifies the JSON location and rule violated. The command prints these findings without a Python traceback for ordinary data errors.

## Error handling

- Missing/unreadable files produce a concise load error and nonzero exit.
- Malformed JSON includes line and column information.
- Unsupported schema versions fail explicitly.
- Validation gathers independent findings so users can correct one edit cycle rather than one error at a time.
- Programming errors are not disguised as data errors.
- The loader performs no recovery mutation and never rewrites registry data.

## Testing and acceptance

Unit tests will cover:

- successful loading of the committed seed registry;
- exact seed counts and the four pillar associations;
- all initial seats remaining vacant and all planned agents owned by roles rather than assigned to seats;
- every seat-type content rule;
- duplicate and malformed IDs;
- missing references and owner-type mismatches;
- unknown fields and unsupported schema versions;
- provider/model-coupled agent IDs;
- invalid versions and authority scopes;
- deny-by-default with an empty grant list;
- rejected AI `APPROVE` and guarded AI `EXECUTE` grants;
- deterministic multi-error output;
- CLI success, summary, invalid-data, and missing-file exit behavior.

Acceptance criteria:

1. `python -m pytest tests/unit -q` passes.
2. `python -m app.organization.cli validate` validates the committed registry.
3. `python -m app.organization.cli summary` reports the registry without changing files.
4. All 12 governed agent IDs appear once, remain `PLANNED`, and contain no provider identity.
5. No authority grant exists unless it is explicitly present in the JSON.
6. Existing repository structure and OpenCode policy tests remain green.

## Security and governance

- The registry contains no credentials, provider endpoints, personal contact information, or protected business data.
- A human display name is the only optional person-related value in this milestone and should be limited to a business-facing name.
- Loading registry data grants no runtime access by itself. Later permissions enforcement must consume validated grants and still enforce approval and audit requirements.
- Seed data does not claim that planned roles or agents are staffed, active, or authorized.

## Migration and compatibility

`schema_version` begins at `1`. Unsupported versions fail instead of being guessed. Future migrations will be explicit, tested transformations. The repository protocol insulates consumers from the JSON layout and supports a later database adapter.

## Builder calls

The following implementation details are left to the builder because they do not change the product behavior:

- exact internal helper names and module-private functions;
- whether validation findings are represented by a small dataclass or named tuple;
- exact summary wording, provided it is stable and contains counts for roles, seats, agents, and grants;
- test fixture organization;
- whether the CLI accepts an optional registry path for tests, provided the default is the committed canonical file.

## Delivery boundary

This project ends with a validated, read-only organizational registry core and its seed data. The next project may expose it through the Control Plane or use it to begin the permission/approval engine, but neither is included here.
