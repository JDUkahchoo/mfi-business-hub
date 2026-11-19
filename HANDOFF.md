# MFI Business Hub Handoff

- **Updated:** 2026-11-19 14:43 America/Chicago
- **Repository:** `https://github.com/JDUkahchoo/mfi-business-hub.git`
- **Feature branch:** `feature/organizational-registry-core`
- **Feature worktree:** `D:\Joshua\Claude\projects\APPS\mfi-business-hub\mfi-business-hub\.worktrees\organizational-registry-core`
- **Feature base:** `8f01bd8` — docs: hand off GitHub push to Claude
- **Current feature writer:** Codex
- **Main publishing owner:** Claude, limited to publishing the already-verified local `main`
- **Current milestone:** Milestone 1 — organizational registry core

## Current objective

Deliver the first executable MFI Business Hub product capability: a read-only organizational registry for roles, seats, governed agents, and explicit authority grants. Preserve human precedence, deny authority by default, and keep agent identity independent of model providers.

## Feature branch commits

- `9ab395a` — design organizational registry core
- `4f14bc8` — plan organizational registry core
- `615f6be` — add organizational registry domain model
- `36c036f` — validate organizational governance rules
- `d5ff56a` — load registry from strict JSON
- `392ab73` — seed canonical MFI organization registry
- `HEAD` — add registry validation CLI and this feature handoff

## Completed feature work

- Added immutable Python domain models and read-only indexes under `app/organization/`.
- Added deterministic validation for references, seat composition, canonical IDs, duplicates, versions, provider-independent agent identity, scopes, and AI authority limits.
- Added strict, atomic UTF-8 JSON loading with concise file, encoding, syntax, shape, enum, and semantic errors.
- Added `config/organization/registry.json` with 12 roles, 12 vacant seats, 12 `PLANNED` role-owned agents, and zero authority grants.
- Clarified that governance Markdown defines policy while JSON is the structured record source.
- Added read-only `validate` and `summary` commands through `python -m app.organization.cli`.
- Added unit coverage for domain, validation, JSON loading, canonical seed data, CLI output, error behavior, read-only behavior, and execution outside the repository directory.

## Current branch state

- The feature exists only on `feature/organizational-registry-core`; it has not been pushed or merged.
- No seat is staffed, no agent is activated, and no authority grant is present.
- The Control Plane, authentication, database, live agent execution, routing, approvals, and audit persistence remain future work.
- Local `main` was still four commits ahead of the locally known `origin/main` at 2026-11-19 14:43 America/Chicago. Claude's earlier non-force publishing task remains separate from this feature branch.

## Verification evidence

- `python -m pytest tests/unit -q` — 93 passed after the CLI implementation.
- `python -m app.organization.cli validate` — `Registry valid.`
- `python -m app.organization.cli summary` — `Registry valid: 12 roles, 12 seats, 12 agents, 0 authority grants.`
- Test evidence confirms both CLI commands leave the canonical JSON bytes and modification time unchanged.
- `git diff --check` was clean after Tasks 1 through 4; final branch verification is required after this handoff commit.

## Next action

Codex: complete final branch verification, prepare the review package, and obtain a fresh independent review of `main...HEAD`. Address every Critical or Important finding with a failing regression test before changing implementation. Then present Joshua with the verified merge choices; do not merge or push without his direction.

Claude: independently verify and publish the already-approved local `main` to `origin/main` without force. Do not merge or publish the Codex feature branch unless Joshua assigns that action.

## Known constraints

- Restricted automation environments may need explicit access to traverse the D: working tree; a restricted Git traversal error does not imply repository corruption.
- OpenCode's background service may retain stale agent discovery across branch switches; run `opencode reload` before validating changed OpenCode agents.
- Gemma and Nemotron assignments remain routing preferences, not canonical MFI agent identities.
- The JSON registry is an interim version-controlled store until a deliberate database migration milestone.

## Transfer protocol

Before another writer edits this feature branch, update the timestamp, owner, completed work, verification evidence, and next action. Reviewers remain read-only and return findings rather than editing the writer's branch.
