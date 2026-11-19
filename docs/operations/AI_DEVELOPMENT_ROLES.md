# AI Development Roles

## Purpose

This policy assigns development responsibilities across Joshua, Codex, Claude, and OpenCode local models. It governs repository work; it does not create corporate roles or change the authority of MFI business agents.

Functional roles remain stable while provider assignments may change after evaluation. A model is an execution dependency, not an organizational identity.

## Responsibility matrix

| Participant or role | Primary responsibility | Normal outputs | Approval boundary |
|---|---|---|---|
| Joshua | Product owner and final authority | Objectives, priorities, approvals, merge decisions | Approves architecture, authority changes, external effects, pushes, and merges when required |
| Codex | Engineering lead | Plans, implementation, tests, integration, Git hygiene, final verification | Works only on its assigned branch/worktree; does not self-authorize material external actions |
| Claude | Architecture and independent review lead | Requirements, architecture proposals, threat reviews, code-review findings | Remains read-only while reviewing another writer's branch; writes only on an explicitly assigned branch |
| Local analyst | Private analysis and knowledge preparation | Extraction, classification, summaries, multimodal interpretation, draft research | Reads only approved documentation or staged analyst inputs; no edits, shell, search tools, connectors, secrets, delegation, pushes, merges, or approvals |
| Local execution worker | High-volume bounded implementation support | Source analysis and proposed patches or transformations written to its staging-output directory | No source edits, shell or test execution, connectors, secrets, governance changes, permission changes, pushes, merges, delegation, or self-approval |
| OpenCode | Local role orchestration | Agent selection, tool mediation, and model routing within configured permissions | Does not become an MFI authority or bypass branch ownership |

## Preferred routing assignments

- **Local analyst → Gemma 4.** Preferred for private document understanding, multimodal material, structured extraction, summarization, and offline drafting.
- **Local execution worker → NVIDIA Nemotron 3.5 Lightning.** Preferred for high-volume source analysis, transformations, patch proposals, and narrow coding tickets. A trusted engineering lead applies changes and executes verification until an isolated credential-free runner exists.
- **Engineering lead → Codex.** Preferred for repository implementation, testing, integration, and complex repair work.
- **Architecture/review lead → Claude.** Preferred for independent requirements, architecture, security review, and second-pass critique.

These are defaults, not guarantees. Select actual OpenCode models from `/models` after LM Studio discovery. Do not enter a model ID from documentation unless that exact ID appears in the local catalog.

## Routing rules

1. Route by task requirements, data classification, capability, cost, and latency—not by habit.
2. `LOCAL_ONLY` work stays with approved local roles. Failure or unavailability does not silently permit cloud fallback.
3. Use the lightest model that passes representative acceptance tests.
4. Escalate architectural ambiguity, authority changes, and cross-component integration to the engineering or architecture lead.
5. Require independent review for security, permissions, external effects, and changes spanning multiple source-of-truth documents.
6. Keep model selection out of canonical MFI business-agent IDs and prompts unless a capability requirement genuinely depends on it.

## Local staging boundaries

- Place sanitized analyst inputs under ignored `data/knowledge/analyst-input/`. The analyst cannot browse other repository or host paths.
- The execution worker writes only under ignored `data/development/worker-output/`. Treat every proposed patch or artifact as untrusted input until Codex or another assigned engineering lead reviews it.
- Local roles have a deny-all permission baseline. Unlisted OpenCode tools, MCP connectors, delegation, shell execution, external directories, and networks remain denied.
- Do not grant the execution worker host test execution until a credential-free, network-restricted runner can prevent writes to Git metadata, governance, instructions, and unrelated workspace paths.

## Evaluation before activation

Each routing assignment must be tested on representative MFI tasks for correctness, instruction following, tool-call reliability, latency, hardware usage, and safe refusal. Record failures as well as successes. A model remains experimental until it consistently meets the task's acceptance criteria.

## Review independence

The reviewer must not edit the implementation being reviewed. Findings identify severity, file and line, user impact, and a suggested correction. The assigned writer applies accepted fixes and reruns verification. Joshua resolves disagreements that change scope, authority, risk tolerance, or business intent.

## Sources

- [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection)
- [Google Gemma 4 overview](https://ai.google.dev/gemma/docs/core.md)
- [NVIDIA Nemotron 3.5 Lightning](https://developer.nvidia.com/blog/Nvidia-nemotron-3-5-lightning-delivers-fast-accurate-specialized-task-execution-for-long-running-agents/)
- [OpenCode agents](https://opencode.ai/docs/agents)
- [OpenCode local models](https://opencode.ai/docs/models)
