# MFI Business Hub Handoff

- **Updated:** 2026-11-19 11:56 America/Chicago
- **Repository:** `https://github.com/JDUkahchoo/mfi-business-hub.git`
- **Branch:** `chore/multi-model-development-operations`
- **Worktree:** `D:\Joshua\Claude\projects\APPS\mfi-business-hub\mfi-business-hub`
- **Base commit:** `2e9738e` — Initial repository structure for MFI Business Hub
- **Last verified implementation commit:** `8093fbd` — multi-model development workflow
- **Current owner:** Joshua (push/merge approval decision)
- **Independent reviewer:** completed; Critical and Important permission findings remediated with deny-all profiles and staged-output boundaries
**Current milestone:** Milestone 0 — repository stabilization and existing Hub validation

## Current objective

Establish the governed development workflow for Joshua, Codex, Claude, and OpenCode local models. This includes functional role definitions, single-writer branch rules, local-agent permission boundaries, and a durable handoff.

## Completed foundation

- GitHub repository and `origin/main` exist at commit `2e9738e`.
- Architecture and governance source-of-truth documents are organized under `docs/`.
- Shared repository instructions exist in `AGENTS.md`.
- Structural and secret-safety tests exist under `tests/unit/`.
- The multi-model operating design and implementation plan are recorded under `docs/superpowers/`.

## Work in progress

- Branch `chore/multi-model-development-operations` contains verified local commit `8093fbd` and has not been pushed.
- Development responsibilities, branch workflow, and ADR 0001 are present.
- OpenCode discovered the configured Gemma and Nemotron models.
- `local-analyst` is deny-all except approved documentation and staged analyst inputs.
- `execution-worker` is deny-all except approved source reads and writes under `data/development/worker-output/`; it cannot run host shell commands or edit repository source.
- No product runtime, business agent, Control Plane, or Compute Plane implementation is part of this branch.

## Next action

Joshua: approve or decline pushing `chore/multi-model-development-operations` to `origin` for review and later merge.

## Verification evidence

- `python -m pytest tests/unit -q` — 9 passed.
- `opencode debug agents | python scripts/validate_opencode_agents.py` — effective local-agent policy valid.
- Local Markdown validation — 43 relative links resolved.
- `git diff --check` — clean.
- OpenCode agent discovery exposes the two intended functional roles with verified LM Studio IDs; general documentation is outside the agent-discovery directory.
- Independent review completed; all Critical and Important findings were addressed.

## Verification required before transfer

1. Run `python -m pytest tests/unit -q`.
2. Validate every local Markdown link.
3. Inspect `git status`, `git diff --check`, and the complete branch diff.
4. Confirm OpenCode role files cannot push, merge, access secrets, or escape the assigned workspace.
5. Record the last verified implementation commit and remaining next action in a follow-up handoff commit; refer to the containing handoff commit as `HEAD` rather than attempting a self-referential hash.

## Known constraints

- The repository is healthy. Restricted automation environments may need explicit access to traverse the D: working tree; do not diagnose metadata corruption from that misleading Git error alone.
- OpenCode 2.3.0 discovered `lmstudio/google/gemma-4-e2b` and `lmstudio/nvidia-nemotron-3.5-lightning-30b-a3b`. Gemma was installed but not loaded; Nemotron was loaded with an 8,192-token runtime context during validation.
- Gemma 4 and Nemotron 3.5 Lightning are preferred routing assignments, not canonical MFI agent identities.
- Historical orchestrator, prompt, or JSON-store assets referenced by earlier planning have not been located or migrated.

## Transfer protocol

Before a new writer edits this branch, the current owner must update the timestamp, owner, completed work, verification evidence, and next action. Reviewers remain read-only and return findings rather than editing the writer's branch.
