# MFI Business Hub Handoff

- **Updated:** 2026-11-20 America/Chicago
- **Repository:** `https://github.com/JDUkahchoo/mfi-business-hub.git`
- **Branch:** `feature/agent-definition-loader`
- **Worktree:** `D:\Joshua\Claude\projects\APPS\mfi-business-hub\mfi-business-hub\.worktrees\agent-definition-loader`
- **Base commit:** `de669c3` — local `main` and `origin/main` were aligned when the feature branch started
- **Current owner:** Codex (final local verification complete; do not push or merge)
- **Current milestone:** Milestone 1 — Cohort 1 agent-definition framework

## Current objective

Build and visibly review a local, read-only framework for six Cohort 1 agent definitions. Keep every agent `PLANNED`, deny tools and authority by default, and do not add runtime execution or provider bindings.

## Implementation commits

- `b269641` — design Cohort 1 agent-definition framework
- `c1cc022` — plan Cohort 1 agent-definition framework
- `17b87d0` — add immutable agent-definition domain model
- `4d13aba` — add strict manifest validation and repository
- `af2c623` — add contained prompt loading and composition
- `b29c619` — join canonical definitions and report readiness
- `270e7dd` — define the representative MFI Orchestrator package
- `5f16b3e` — define all six Cohort 1 packages
- `aafe2a7` — add local inspection commands, status documentation, and handoff
- Branch `HEAD` — remediate all Important independent-review findings

## Completed feature work

- Added immutable definition, prompt, joined-definition, evidence, and readiness records under `app/agents/definitions/`.
- Added strict, atomic JSON manifest loading with unknown-field, type, duplicate-member, duplicate-ID, filename-parity, policy, and provider-independence checks.
- Added contained Markdown prompt loading with lexical and resolved-path escape prevention, UTF-8 validation, exact section requirements, source fingerprints, and provenance-aware composition.
- Joined manifests to canonical identity, lifecycle, version, purpose, ownership, and grants from `config/organization/registry.json` without duplicating those fields.
- Added complete manifests and readable prompts for the Orchestrator, QA Auditor, and four Pillar Leads.
- Added typed readiness reporting that separates definition completeness from activation eligibility and never changes lifecycle state.
- Added read-only `validate`, `summary`, `show`, and `readiness` commands plus an operator guide.
- Corrected roadmap, architecture, and registry status language without claiming an agent runtime exists.

## Current branch state

- Local implementation is on `feature/agent-definition-loader`; nothing from this feature has been pushed or merged.
- The framework, six packages, inspection commands, and review remediations are verified with 197 passing unit tests (1 host-permission symlink test skipped and covered by platform-neutral resolved-containment tests).
- All six load as definition `COMPLETE`, lifecycle `PLANNED`, activation `BLOCKED`, with zero tools and zero authority grants; zero are activation-eligible.
- The feature branch started from `de669c3`; local `main` and `origin/main` were aligned at that commit.
- No seat is staffed, no agent is activated, and no authority grant is present.
- The Control Plane, authentication, database, live agent execution, routing, approvals, and audit persistence remain future work.
- Independent whole-branch review found no Critical issues. All eight Important findings were reproduced with failing tests and remediated in one fix pass.

## Verification evidence

- `python -m pytest tests/unit -q` — 197 passed, 1 skipped for Windows symlink permission.
- `python -m app.agents.definitions.cli validate` — `6 Cohort 1 definitions valid; 12 prompt sources loaded; 0 authority grants resolved.`
- `python -m app.agents.definitions.cli summary` — six deterministic `COMPLETE  PLANNED  BLOCKED` rows.
- `python -m app.agents.definitions.cli readiness` — `6 definition-complete; 0 activation-eligible; 6 blocked.`
- `python -m app.agents.definitions.cli show mfi-orchestrator` — canonical metadata, contracts, prompt paths, fingerprints, and blockers; no prompt body by default.
- Tests confirm all commands are read-only and work outside the repository directory.
- Independent-review focused regression suite — 12 new failures observed before fixes, then 77 passed and 1 skipped after fixes.
- `git diff --check` — clean after review remediation.

## Next action

Codex: complete. The local branch is verified and independently reviewed with no unresolved Critical or Important findings.

Joshua: inspect the local reports and choose whether to keep the branch, merge it locally, or later push. No publish or merge is authorized yet.

## Known constraints

- Restricted automation environments may need explicit access to traverse the D: working tree; a restricted Git traversal error does not imply repository corruption.
- OpenCode's background service may retain stale agent discovery across branch switches; run `opencode reload` before validating changed OpenCode agents.
- Gemma and Nemotron assignments remain routing preferences, not canonical MFI agent identities.
- The JSON registry is an interim version-controlled store until a deliberate database migration milestone.

## Transfer protocol

Before another writer edits `main`, update the timestamp, owner, completed work, verification evidence, and next action. Reviewers remain read-only and return findings rather than editing the writer's branch.
