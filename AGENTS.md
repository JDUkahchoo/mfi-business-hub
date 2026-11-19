# Shared Repository Instructions

These instructions apply to humans and coding assistants working in the MFI Business Hub repository.

## Start here

Read these files before making architectural, governance, agent, or authority changes:

1. `README.md`
2. `docs/README.md`
3. `docs/architecture/ARCHITECTURE.md`
4. the relevant document under `docs/governance/`
5. `docs/ROADMAP.md`

More specific instructions in a future subdirectory-level `AGENTS.md` take precedence only within that directory.

## Source-of-truth rules

- Architecture belongs in `docs/architecture/`.
- Organization, agent identity, agent requirements, and authority belong in `docs/governance/`.
- Prompts belong under `prompts/`; adapters such as `.opencode/agents/` reference them instead of duplicating policy.
- Provider-specific code belongs under `app/integrations/`; agents request capabilities through `app/core/model_router/`.
- Do not describe planned components as implemented. Use the status language in `docs/ROADMAP.md` and `docs/governance/AGENT_REGISTRY.md`.

## Change discipline

- Preserve user and other-agent work. Inspect the current file and repository status immediately before editing.
- Make narrow changes tied to the current task; do not reorganize unrelated files opportunistically.
- Avoid simultaneous edits to the same file. When multiple assistants are active, assign file or directory ownership first.
- Do not overwrite a file whose contents changed unexpectedly during your task. Stop, compare, and reconcile.
- Keep links relative and update all references when moving documents.
- Add or update tests for executable behavior and structural contracts; run the relevant suite before reporting completion.
- Record durable architectural choices under `docs/decisions/` when implementation begins to depend on them.

## Safety and governance

- Never commit `.env`, credentials, tokens, private keys, protected customer data, unrestricted model transcripts, or runtime logs.
- LM Studio and local model servers must not be exposed directly to the public internet.
- Do not bypass authority, approval, audit, routing, or data-classification rules to make a workflow easier.
- AI agents do not gain executive or human approval authority because a human seat is vacant.
- Do not send external communications, commit funds, accept contracts, or perform irreversible business actions without the required human approval.

## Current implementation boundary

This repository is currently a foundation scaffold. Empty packages and directories marked by `.gitkeep` are planned boundaries, not completed features. Do not add framework or infrastructure dependencies until the milestone being implemented requires them and the choice is recorded.

