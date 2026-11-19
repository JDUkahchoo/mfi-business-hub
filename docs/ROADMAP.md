# Roadmap

## Milestones

**Milestone 0 — Repository stabilization and existing Hub validation**

- Maintain the shared repository structure and source-of-truth documents.
- Locate and assess any existing orchestrator, prompt, and JSON-store assets before migration.
- Establish version control and a repeatable development environment.

**Milestone 1 — Organizational model and agent framework**

- Represent pillars, cross-pillar functions, people, roles, and seat types.
- Implement registry-backed agent definitions and prompt/configuration loading.

**Milestone 2 — Authority, approvals, audit, and model gateway**

- Enforce scoped authority and approval prerequisites.
- Record material actions and routing decisions.
- Route provider-independent capability requests to approved local or cloud adapters.

**Milestone 3 — Cohort 1 agents**

- Orchestrator and QA Auditor.
- Four Pillar Lead agents.

**Milestone 4 — Cross-company agents**

- Business Development, Government Business, and Private Sector leads.
- CFO, COO, and CTO copilots supporting their accountable humans.

**Milestone 5 — Hybrid Control Plane and Compute Plane foundation**

- Authenticated Control Plane foundation and worker-node registry.
- Outbound-initiated worker connectivity and governed job lifecycle.

**Milestone 6+ — Specialist agents and business applications**

- Add specialist capabilities only when ownership, authority, data scope, and acceptance tests are defined.

## Current position

Milestone 0. The scaffold and documentation baseline exist. Existing Hub code, prompts, and JSON data have not been located or migrated, and no runtime components are implemented.

Architecture direction is defined in the [architecture documents](architecture/ARCHITECTURE.md); agent rollout status is defined in the [Agent Registry](governance/AGENT_REGISTRY.md).
