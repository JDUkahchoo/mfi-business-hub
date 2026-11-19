# MFI Business Hub Documentation

This directory contains the durable source-of-truth documents for the MFI Business Hub. The root [README](../README.md) is the project entry point; this file maps the governing documents.

## Architecture

- [System Architecture](architecture/ARCHITECTURE.md) — system boundaries, core domains, dependency direction, data ownership, and security invariants.
- [Hybrid Architecture](architecture/HYBRID_ARCHITECTURE.md) — Control, Compute, and Cloud AI planes; secure job flow; routing; trust boundaries; and failure behavior.
- [Compute Node Standard](architecture/NODE_STANDARD.md) — enrollment, identity, capabilities, connectivity, jobs, logs, updates, and revocation for local workers.

## Governance

- [Organization](governance/ORGANIZATION.md) — four pillars, cross-pillar functions, seat types, roles, and human precedence.
- [Agent Standard](governance/AGENT_STANDARD.md) — required definition, permissions, prompts, tools, audit, quality gates, and lifecycle for agents.
- [Authority Matrix](governance/AUTHORITY_MATRIX.md) — `READ`, `WRITE`, `PROPOSE`, `APPROVE`, and `EXECUTE` boundaries.
- [Agent Registry](governance/AGENT_REGISTRY.md) — canonical agent IDs, rollout cohorts, and implementation status.

## Delivery

- [Roadmap](ROADMAP.md) — milestone order and current position.
- `decisions/` — durable architecture decision records when implementation choices are made.
- `superpowers/specs/` and `superpowers/plans/` — approved designs and implementation plans supporting repository work.

## Source-of-truth order

When documents overlap, use the most specific governing document: authority questions go to the Authority Matrix; agent identity goes to the Agent Registry; agent construction goes to the Agent Standard; system boundaries go to the architecture set. If two authoritative documents genuinely conflict, stop implementation and reconcile both in the same change.

## Status language

The architecture documents describe the approved direction. They do not claim that a component exists. The Roadmap and Agent Registry provide implementation status, while tests and runnable code provide evidence of completed behavior.

