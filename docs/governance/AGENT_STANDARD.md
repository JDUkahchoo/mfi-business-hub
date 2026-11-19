# MFI Agent Standard

## Purpose

Every MFI agent must be understandable, reviewable, provider-independent, and limited to explicit authority. An agent is not production-ready merely because its prompt or model call works.

## Required definition

Each registered agent must define:

- canonical ID and display name;
- business purpose and accountable human or hybrid owner;
- lifecycle status and version;
- responsibilities and explicit non-responsibilities;
- accepted inputs and structured outputs;
- allowed tools, systems, and data classifications;
- authority levels and approval requirements;
- prompt source and configuration source;
- model capability requirements and routing policy;
- audit events, failure behavior, and escalation destination;
- tests and acceptance criteria.

The canonical registry entry references the prompt and configuration; OpenCode or other assistant definitions mirror these sources instead of duplicating policy.

## Identity and provider independence

Agent identity is defined by business purpose, prompt, authority, tools, and owner. It must not be named or implemented as a thin alias for a model provider.

Agents request capabilities from the Model Gateway. Provider selection follows the [Hybrid Architecture](../architecture/HYBRID_ARCHITECTURE.md), including local-only and human-only restrictions.

## Authority and approvals

Permissions default to denied. Each agent receives only the minimum `READ`, `WRITE`, `PROPOSE`, `APPROVE`, and `EXECUTE` scopes required by its approved role. Those terms are defined in the [Authority Matrix](AUTHORITY_MATRIX.md).

An agent must stop and escalate when:

- required authority or approval is missing;
- instructions conflict with governance or law;
- data classification is unknown or incompatible with routing;
- an action is irreversible, externally binding, or outside its assigned scope;
- confidence, evidence, or system state is insufficient for a material decision.

## Prompts and configuration

Prompts live under `prompts/` and are versioned with the repository. They describe purpose, boundaries, expected outputs, escalation behavior, and prohibited actions. Secrets, personal credentials, and environment-specific endpoints do not belong in prompts.

Configuration under `config/` may select approved policies or capability requirements. It must not silently expand authority beyond the registry and authority matrix.

## Tools and data

Tool access is explicit and scoped. An agent must validate tool results as untrusted input, minimize retrieved data, respect source access controls, and preserve provenance when producing business output. Write or execute access must not be inferred from read access.

## Auditability

Material runs record the requesting identity, agent ID and version, job/task ID, data classification, routing decision, selected provider or node, tools used, approvals, outcome, and sanitized error state. Logs must not expose secrets or unrestricted protected content.

## Quality gates

Before activation, an agent requires:

1. a complete registry record;
2. reviewed prompt and configuration;
3. authority and data-scope review;
4. tests for normal, denied, malformed, and escalation paths;
5. audit-event verification;
6. human acceptance by the accountable owner.

Material changes to purpose, authority, tools, or data scope require reapproval. Provider substitutions within already approved capability and routing policy do not redefine the agent, but still require compatibility testing.

## Lifecycle

Use these states consistently: `PLANNED`, `DRAFT`, `TESTING`, `ACTIVE`, `SUSPENDED`, and `RETIRED`. Suspension stops new work without deleting history. Retirement preserves identity, versions, and audit records while preventing future execution.

