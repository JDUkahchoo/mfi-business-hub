# Multifaceted Investments Business Hub

The **MFI Business Hub** is the shared foundation humans, Codex, Claude Code, and OpenCode use to build a governed hybrid human-and-AI operating system for Multifaceted Investments LLC.

## Current status

This repository now provides a validated registry-backed definition framework for six Cohort 1 agents and a runnable, read-only local browser dashboard for reviewing them. All six definitions are `COMPLETE`, their lifecycle remains `PLANNED`, and activation remains `BLOCKED`; no tools or authority grants are present.

It does **not** contain the hosted Control Plane, authentication, a database, a local worker, model gateway, permissions or approval engines, audit persistence, deployment configuration, or an agent runtime.

See the [Roadmap](docs/ROADMAP.md) for delivery order and the [documentation index](docs/README.md) for authoritative project references.

## Business structure

MFI operates across four pillars:

1. Infrastructure & Supply Chain
2. Technology / Gaming / Entertainment
3. Investments
4. Incubation

Government Business and Private Sector Business are cross-pillar revenue functions, not additional pillars. See [Organization](docs/governance/ORGANIZATION.md).

## Human and AI governance

Seats are `HUMAN`, `AI`, `HYBRID`, or `VACANT`. Humans outrank AI agents in the same functional area, and a vacant human seat does not grant an AI agent executive authority.

The authority vocabulary is `READ`, `WRITE`, `PROPOSE`, `APPROVE`, and `EXECUTE`. See the [Authority Matrix](docs/governance/AUTHORITY_MATRIX.md), [Agent Standard](docs/governance/AGENT_STANDARD.md), and [Agent Registry](docs/governance/AGENT_REGISTRY.md).

## Hybrid architecture

- **Control Plane:** web UI, identity, permissions, approvals, registries, tasks, central metadata, and audit records.
- **Compute Plane:** registered local workers for LM Studio, Gemma, Nemotron, embeddings, document processing, and local-only jobs.
- **Cloud AI Plane:** approved external reasoning providers reached through the MFI Model Gateway.

Agents are independent of providers:

```text
Agent -> MFI Model Gateway -> Approved local or cloud provider
```

Read the [System Architecture](docs/architecture/ARCHITECTURE.md), [Hybrid Architecture](docs/architecture/HYBRID_ARCHITECTURE.md), and [Compute Node Standard](docs/architecture/NODE_STANDARD.md).

## Repository map

```text
app/        Python application and domain packages
config/     Declarative agent, environment, model, and permission settings
data/       Local development, knowledge, registry, and ignored runtime-log areas
docs/       Architecture, governance, roadmap, decisions, and implementation plans
prompts/    Versioned agent prompts grouped by business function
scripts/    Repository and operational scripts
tests/      Unit, integration, agent, permission, and fixture tests
web/        Planned Cloudflare-hosted Control Plane boundary
worker/     Planned local Compute Plane runtime boundary
.opencode/  OpenCode adapters that mirror authoritative agent definitions
```

Shared coding-assistant rules are in [AGENTS.md](AGENTS.md).

## Development collaboration

Codex is the primary engineering lead, Claude is the architecture and independent review lead, and OpenCode supplies bounded local analyst and execution-worker roles. Gemma 4 and Nemotron 3.5 Lightning are preferred initial local routing assignments, not permanent agent identities.

Read the current [handoff](HANDOFF.md), [AI development roles](docs/operations/AI_DEVELOPMENT_ROLES.md), and [branch/worktree workflow](docs/operations/BRANCH_WORKFLOW.md) before starting repository work.

## Development setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the current verification suite:

```powershell
python -m pytest tests/unit -v
```

Run the local review dashboard:

```powershell
python -m app.local_dashboard.cli --open
```

See the [local dashboard operating guide](docs/operations/LOCAL_DASHBOARD.md) for its loopback-only and read-only boundaries.

## Implementation boundary

The current dashboard is a local review tool, not the production Control Plane. The JSON registry remains the version-controlled source for this milestone until a deliberate database migration. Deployment, authentication, persistent approvals/audits, model routing, worker connectivity, and agent execution require separate reviewed milestones.
