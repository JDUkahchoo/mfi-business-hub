# MFI Business Hub Architecture

## Purpose

The MFI Business Hub is a hybrid human-and-AI operating system for Multifaceted Investments LLC. It provides one governed place to coordinate business work, approvals, knowledge, agents, and compute across local machines and cloud services.

This document defines the system boundaries and dependency direction. Detailed deployment and worker requirements live in [Hybrid Architecture](HYBRID_ARCHITECTURE.md) and [Node Standard](NODE_STANDARD.md).

## Architectural principles

1. Humans retain final authority. AI agents operate only within explicitly assigned permissions.
2. Agent identity is independent of model provider: `Agent -> Model Gateway -> Provider`.
3. Sensitive or local-only work must remain on approved local compute nodes.
4. LM Studio and local model servers are never exposed directly to the public internet.
5. Approvals, executions, routing decisions, and material agent actions are auditable.
6. The current JSON knowledge store remains valid until a deliberate database migration milestone.
7. Planned architecture is not represented as implemented functionality.

## System planes

### Control Plane

The cloud/web-facing coordination layer owns users, authentication, roles, permissions, approvals, tasks, the agent registry, the worker-node registry, central metadata, and audit records. It assigns work but does not directly expose or administer a local model server.

### Compute Plane

Registered worker nodes perform approved local work such as LM Studio inference, Gemma or Nemotron inference, embeddings, document processing, and private data operations. Nodes establish authenticated outbound connections and claim only compatible jobs.

### Cloud AI Plane

Approved external providers such as Claude, OpenAI, and Grok provide optional reasoning capacity. They are reached through the Model Gateway, subject to data classification, authority, cost, and provider policy.

## Core domains

- `app/core/`: orchestration, configuration, routing, permissions, approvals, notifications, and audit behavior.
- `app/agents/`: agent runtime implementations grouped by business function.
- `app/organization/`: people, roles, departments, pillars, and seat assignments.
- `app/business/`: leads, opportunities, proposals, projects, contracts, tasks, decisions, and risks.
- `app/knowledge/`: documents, repositories, retrieval, and knowledge-store boundaries.
- `app/nodes/`: worker registry, job records, and worker coordination.
- `app/integrations/`: provider and external-system adapters.
- `config/`: declarative environment, model, permission, and agent settings.
- `prompts/`: versioned agent instructions referenced rather than duplicated by runtime definitions.
- `web/`: the future Control Plane user interface.
- `worker/`: the future local Compute Plane runtime.

Dependencies should point from business and agent behavior toward stable core interfaces. Provider-specific code stays behind integration adapters; organizational roles and agent definitions must not import or encode a single provider as their identity.

## Model Gateway

```text
Agent -> MFI Model Gateway -> Routing Policy -> Approved Provider
                                             -> LM Studio
                                             -> Claude
                                             -> OpenAI
                                             -> Grok
```

Routing considers the job's data classification, execution policy, required capabilities, approved providers, node availability, cost limits, and fallback rules. Provider credentials remain outside source control.

## Data ownership

- The Control Plane is authoritative for identities, permissions, approvals, registries, task state, and durable audit metadata.
- Compute nodes own temporary execution state and explicitly local-only artifacts.
- Knowledge sources retain their own provenance and access restrictions.
- Prompts and configuration are versioned project assets; secrets and runtime logs are not.

## Security invariants

- Deny unassigned authority by default.
- Require human approval where the [Authority Matrix](../governance/AUTHORITY_MATRIX.md) requires it.
- Never infer executive authority from an unfilled human role.
- Encrypt authenticated traffic between planes when networking is implemented.
- Minimize data sent to external providers and block cloud routing for local-only work.
- Record who or what requested, approved, routed, and executed material work.

## Implementation status

The repository currently contains a package and documentation scaffold. The Control Plane, Compute Plane, Model Gateway, permissions engine, approval engine, audit system, worker protocol, and business agents remain planned work. See the [Roadmap](../ROADMAP.md).

