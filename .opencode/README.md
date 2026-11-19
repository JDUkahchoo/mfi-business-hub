# OpenCode Development Roles

The files under `agents/` define OpenCode development roles. They support repository work and do not replace the MFI business-agent registry (`../docs/governance/AGENT_REGISTRY.md`).

- `agents/local-analyst.md` is a read-only private analysis role.
- `agents/execution-worker.md` reads approved source paths and writes proposed patches or transformation artifacts only to `data/development/worker-output/`; it has no host shell, Git publishing, or governance authority.
- Development responsibilities and routing defaults are defined in `../docs/operations/AI_DEVELOPMENT_ROLES.md`.
- Business-agent identity and authority remain governed by `../docs/governance/AGENT_REGISTRY.md` and `../docs/governance/AGENT_STANDARD.md`.

Do not put general Markdown documentation inside `.opencode/agents/`. OpenCode treats every Markdown file there as an executable agent definition.

## Model selection

OpenCode 2.3.0 and LM Studio discovery verified these project-local model IDs on 2026-11-19:

- `local-analyst`: `lmstudio/google/gemma-4-e2b`
- `execution-worker`: `lmstudio/nvidia-nemotron-3.5-lightning-30b-a3b`

Use OpenCode's `/models` selector to confirm they remain available before a run. The Gemma model was installed but not loaded during verification; Nemotron was loaded with an 8,192-token runtime context despite supporting a larger maximum, so keep initial execution tasks bounded.

After switching branches or merging changes to `.opencode/`, run `opencode reload` before agent discovery or permission validation. The background service can otherwise retain the prior branch's agent catalog.

The role files begin with deny-all permissions and add only narrow read or staging-output access. Codex or another trusted engineering lead applies proposed patches and runs tests. Update model assignments only after `/models` confirms a replacement and representative evaluation supports the routing change. Do not commit credentials or copy a documentation example's model ID unless that exact ID is present in the local catalog.

OpenCode automatically discovers LM Studio at its default local address when the server is available. Keep local model servers bound to trusted local interfaces; never expose LM Studio directly to the public internet.
