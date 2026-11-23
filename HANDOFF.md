# MFI Business Hub Handoff

- **Updated:** 2026-11-23 America/Chicago
- **Repository:** `https://github.com/JDUkahchoo/mfi-business-hub.git`
- **Branch:** `main`
- **Worktree:** `D:\Joshua\Claude\projects\APPS\mfi-business-hub\mfi-business-hub`
- **Latest verified feature integration:** `5499be3` — local dashboard review findings resolved
- **Current owner:** Codex (Projects and Ventures Workspace discovery and design)
- **Current milestone:** Projects and Ventures Workspace; Vague is the proposed first real venture workspace

## Current objective

Design the Projects and Ventures Workspace so MFI can organize real work such as the Vague tabletop game through governed project records, milestones, decisions, evidence, and accountable-human ownership. Do not add runtime agents, authority grants, deployment, or persistent mutation behavior before Joshua approves the workspace design.

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
- `4bc28dd` — complete local dashboard checkpoint and operating documentation
- `5499be3` — resolve all Important local dashboard review findings

## Completed feature work

- Added immutable definition, prompt, joined-definition, evidence, and readiness records under `app/agents/definitions/`.
- Added strict, atomic JSON manifest loading with unknown-field, type, duplicate-member, duplicate-ID, filename-parity, policy, and provider-independence checks.
- Added contained Markdown prompt loading with lexical and resolved-path escape prevention, UTF-8 validation, exact section requirements, source fingerprints, and provenance-aware composition.
- Joined manifests to canonical identity, lifecycle, version, purpose, ownership, and grants from `config/organization/registry.json` without duplicating those fields.
- Added complete manifests and readable prompts for the Orchestrator, QA Auditor, and four Pillar Leads.
- Added typed readiness reporting that separates definition completeness from activation eligibility and never changes lifecycle state.
- Added read-only `validate`, `summary`, `show`, and `readiness` commands plus an operator guide.
- Corrected roadmap, architecture, and registry status language without claiming an agent runtime exists.
- Added the loopback-only, read-only local browser dashboard with Overview, Agents, Agent Detail, Readiness, and explicit prompt-review views.
- Added atomic source-version checks, loopback authority validation, static-asset containment, browser race protection, complete governance detail rendering, and read-only acceptance coverage.

## Current branch state

- Local dashboard design and implementation plan are documented under `docs/superpowers/` and merged into local `main`.
- The dashboard is standard-library Python plus static local browser assets, loopback-only, read-only, and dependency-free.
- Browser views include Overview, Agents, Agent Detail, Readiness, and an explicit prompt viewer; prompt text is absent from default responses.
- Repeated prompt paths with inconsistent fingerprints fail the request atomically with refresh guidance.
- Desktop, agent-ledger, detail, and mobile-width screenshots were reviewed from the real local server.
- Dashboard branch verification: 267 tests passed, 2 Windows symlink-permission tests skipped with platform-neutral coverage passing.
- The verified dashboard feature is merged into local `main` through `5499be3`.
- The framework, dashboard services/server/CLI/assets, inspection commands, and read-only acceptance proof are covered by 267 passing unit tests (2 host-permission symlink tests skipped and covered by platform-neutral containment tests).
- All six load as definition `COMPLETE`, lifecycle `PLANNED`, activation `BLOCKED`, with zero tools and zero authority grants; zero are activation-eligible.
- No seat is staffed, no agent is activated, and no authority grant is present.
- The Control Plane, authentication, database, live agent execution, routing, approvals, and audit persistence remain future work.
- Independent whole-branch review found no Critical issues. All seven Important findings were reproduced with failing tests and remediated in one fix pass.
- Merged-result verification exposed and fixed one CRLF-only test assumption; the feature worktree and merged feature branch were then removed.

## Verification evidence

- `python -m pytest tests/unit -q` — 267 passed, 2 skipped for Windows symlink permission.
- Read-only acceptance exercises all six detail and prompt routes plus health, dashboard, HEAD, 404, traversal, and mutation rejection while preserving source bytes and modification times.
- `python -m app.agents.definitions.cli validate` — `6 Cohort 1 definitions valid; 12 prompt sources loaded; 0 authority grants resolved.`
- `python -m app.agents.definitions.cli summary` — six deterministic `COMPLETE  PLANNED  BLOCKED` rows.
- `python -m app.agents.definitions.cli readiness` — `6 definition-complete; 0 activation-eligible; 6 blocked.`
- `python -m app.agents.definitions.cli show mfi-orchestrator` — canonical metadata, contracts, prompt paths, fingerprints, and blockers; no prompt body by default.
- Tests confirm all commands are read-only and work outside the repository directory.
- Independent-review focused regression suite — 12 new failures observed before fixes, then 77 passed and 1 skipped after fixes.
- `git diff --check` — clean after review remediation.

## Next action

Codex: lead discovery, approach selection, and an approved design for the Projects and Ventures Workspace before implementation planning.

Joshua: identify where the current Vague material is stored and describe what a useful first Vague session in the Hub should accomplish.

Claude: independently review the proposed workspace architecture and governance after Codex writes the design; remain read-only on Codex's branch.

Gemma 4: after Joshua identifies and approves the source material, prepare a private structured inventory under the analyst staging boundary. Nemotron remains reserved for later bounded fixtures and test scenarios.

## Known constraints

- Restricted automation environments may need explicit access to traverse the D: working tree; a restricted Git traversal error does not imply repository corruption.
- OpenCode's background service may retain stale agent discovery across branch switches; run `opencode reload` before validating changed OpenCode agents.
- Gemma and Nemotron assignments remain routing preferences, not canonical MFI agent identities.
- The JSON registry is an interim version-controlled store until a deliberate database migration milestone.
- Deferred local-dashboard improvements `DASH-001` through `DASH-004` are recorded in `docs/operations/LOCAL_DASHBOARD.md`; none blocks the next design milestone.

## Transfer protocol

Before another writer edits `main`, update the timestamp, owner, completed work, verification evidence, and next action. Reviewers remain read-only and return findings rather than editing the writer's branch.
