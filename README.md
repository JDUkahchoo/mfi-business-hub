# Multifaceted Investments Business Hub

The **MFI Business Hub** is the shared foundation humans, Codex, Claude Code, and OpenCode use to build a governed hybrid human-and-AI operating system for Multifaceted Investments LLC.

## Current status

This repository currently provides the package layout, architecture and governance documents, environment and secrets safeguards, and structural tests. It does **not** yet contain a runnable Hub, web Control Plane, local worker, model gateway, permissions engine, or implemented business agents.

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

## Implementation boundary

The existing orchestrator, prompts, or JSON store referenced by earlier planning have not been located or migrated into this repository. When available, they must be assessed before migration. The current JSON knowledge-store direction remains valid until a deliberate database milestone.
