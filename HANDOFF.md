# MFI Business Hub Handoff

- **Updated:** 2026-11-21 America/Chicago
- **Repository:** `https://github.com/JDUkahchoo/mfi-business-hub.git`
- **Branch:** `feature/local-review-dashboard`
- **Worktree:** `D:\Joshua\Claude\projects\APPS\mfi-business-hub\mfi-business-hub\.worktrees\local-review-dashboard`
- **Latest local integration:** `1339182` — agent-definition framework integrated and verified on Windows
- **Current owner:** Codex (local dashboard implementation complete; final branch review pending)
- **Current milestone:** Local review dashboard over the completed Cohort 1 definition framework

## Current objective

Complete and independently review the polished, read-only local browser dashboard before any merge, push, or deployment choice. Preserve `PLANNED`/`BLOCKED` lifecycle safety, prompt privacy by default, and the absence of tools, grants, runtime execution, or provider bindings.

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
- `27add58` — remediate all Important independent-review findings
- `7100f94` — record local agent-framework integration
- `1339182` — make prompt contract-parity verification line-ending neutral on Windows
- `be5c7ff` — plan the local agent review dashboard
- `99b5743` — add governed dashboard snapshot service
- `07af4a7` — add loopback read-only HTTP server
- `be502bb` — add local dashboard command
- `98b5308` — add data-driven browser review interface

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

- Local dashboard design and implementation plan are documented under `docs/superpowers/`.
- The dashboard is standard-library Python plus static local browser assets, loopback-only, read-only, and dependency-free.
- Browser views include Overview, Agents, Agent Detail, Readiness, and an explicit prompt viewer; prompt text is absent from default responses.
- Repeated prompt paths with inconsistent fingerprints fail the request atomically with refresh guidance.
- Desktop, agent-ledger, detail, and mobile-width screenshots were reviewed from the real local server.
- Dashboard branch verification: 258 tests passed, 1 Windows symlink-permission test skipped with platform-neutral coverage passing.
- The verified feature is merged into local `main` at `27add58`; nothing from this feature has been pushed to GitHub.
- The framework, dashboard services/server/CLI/assets, inspection commands, and read-only acceptance proof are covered by 258 passing unit tests (1 host-permission symlink test skipped and covered by platform-neutral resolved-containment tests).
- All six load as definition `COMPLETE`, lifecycle `PLANNED`, activation `BLOCKED`, with zero tools and zero authority grants; zero are activation-eligible.
- `origin/main` remains at `de669c3`; local `main` now contains the reviewed agent-definition commits.
- No seat is staffed, no agent is activated, and no authority grant is present.
- The Control Plane, authentication, database, live agent execution, routing, approvals, and audit persistence remain future work.
- Independent whole-branch review found no Critical issues. All eight Important findings were reproduced with failing tests and remediated in one fix pass.
- Merged-result verification exposed and fixed one CRLF-only test assumption; the feature worktree and merged feature branch were then removed.

## Verification evidence

- `python -m pytest tests/unit -q` — 258 passed, 1 skipped for Windows symlink permission.
- Read-only acceptance exercises all six detail and prompt routes plus health, dashboard, HEAD, 404, traversal, and mutation rejection while preserving source bytes and modification times.
- `python -m app.agents.definitions.cli validate` — `6 Cohort 1 definitions valid; 12 prompt sources loaded; 0 authority grants resolved.`
- `python -m app.agents.definitions.cli summary` — six deterministic `COMPLETE  PLANNED  BLOCKED` rows.
- `python -m app.agents.definitions.cli readiness` — `6 definition-complete; 0 activation-eligible; 6 blocked.`
- `python -m app.agents.definitions.cli show mfi-orchestrator` — canonical metadata, contracts, prompt paths, fingerprints, and blockers; no prompt body by default.
- Tests confirm all commands are read-only and work outside the repository directory.
- Independent-review focused regression suite — 12 new failures observed before fixes, then 77 passed and 1 skipped after fixes.
- `git diff --check` — clean after review remediation.

## Next action

Codex: run the final whole-branch review, fix any Critical or Important findings with regression tests, and present the live local checkpoint.

Joshua: review the real dashboard at the printed loopback URL. Merge, GitHub publishing, and deployment remain separate later decisions.

## Known constraints

- Restricted automation environments may need explicit access to traverse the D: working tree; a restricted Git traversal error does not imply repository corruption.
- OpenCode's background service may retain stale agent discovery across branch switches; run `opencode reload` before validating changed OpenCode agents.
- Gemma and Nemotron assignments remain routing preferences, not canonical MFI agent identities.
- The JSON registry is an interim version-controlled store until a deliberate database migration milestone.

## Transfer protocol

Before another writer edits `main`, update the timestamp, owner, completed work, verification evidence, and next action. Reviewers remain read-only and return findings rather than editing the writer's branch.
