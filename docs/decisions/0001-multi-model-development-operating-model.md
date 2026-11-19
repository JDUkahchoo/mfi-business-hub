# ADR 0001: Multi-Model Development Operating Model

- **Status:** Accepted
**Date:** 2026-11-19

## Context

The MFI Business Hub is being developed with multiple cloud and local assistants. Allowing every assistant to act as an equal writer in one checkout would create conflicting plans, unclear ownership, duplicated work, and unsafe merges. Using only one model would be simpler but would give up independent review and economical private local processing.

## Decision

Adopt a lead-and-specialist model:

- Joshua remains product owner and final human authority.
- Codex is the primary engineering and integration lead.
- Claude is the architecture and independent review lead.
- OpenCode provides functional local subagents.
- Gemma 4 is the preferred initial routing assignment for the local analyst role.
- NVIDIA Nemotron 3.5 Lightning is the preferred initial routing assignment for the local execution-worker role.
- GitHub issues, isolated branches/worktrees, and a single named writer define ownership.
- Provider assignments may change after evaluation without renaming the functional role or changing its authority.

## Alternatives rejected

### Codex-only development

Operationally simple, but it removes independent model review and underuses private local compute.

### Peer multi-agent editing

Potentially faster for independent work, but unsafe when agents share mutable files or make incompatible architectural assumptions.

## Consequences

- Work may spend more time in explicit handoff and review, but ownership and recovery are clearer.
- Local models can reduce cloud exposure and cost for bounded tasks, but they require task-specific evaluation.
- Review independence is preserved by preventing reviewers from editing the branch they judge.
- Model routing remains replaceable and does not leak into permanent organizational identity.
- Every material session must keep `HANDOFF.md` current.

## Reevaluation triggers

Revisit this decision when representative evaluations show a different model is materially safer or more effective, when the team adopts automated branch isolation, when OpenCode permission behavior changes, or when the MFI Model Gateway becomes the authoritative runtime router.
