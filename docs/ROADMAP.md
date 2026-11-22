# Roadmap

## Milestones

**Milestone 0 — Repository stabilization and existing Hub validation**

- **Complete.** Maintain the shared repository structure and source-of-truth documents.
- **Complete.** Locate and assess existing assets before migration.
- **Complete.** Establish version control and a repeatable development environment.

**Milestone 1 — Organizational model and agent framework**

- **Complete.** Represent pillars, cross-pillar functions, roles, vacant seats, governed agent identities, and explicit authority grants.
- **Complete.** Implement strict registry-backed definition, prompt, validation, inspection, and readiness loading for the six Cohort 1 identities.
- **Complete locally.** Provide a read-only browser dashboard for reviewing those definitions and blockers before deployment decisions.

**Milestone 2 — Authority, approvals, audit, and model gateway**

- Enforce scoped authority and approval prerequisites.
- Record material actions and routing decisions.
- Route provider-independent capability requests to approved local or cloud adapters.

**Milestone 3 — Cohort 1 agents**

- Implement and test runtime behavior for the Orchestrator and QA Auditor definitions.
- Implement and test runtime behavior for the four Pillar Lead definitions.

**Milestone 4 — Cross-company agents**

- Business Development, Government Business, and Private Sector leads.
- CFO, COO, and CTO copilots supporting their accountable humans.

**Milestone 5 — Hybrid Control Plane and Compute Plane foundation**

- Authenticated Control Plane foundation and worker-node registry.
- Outbound-initiated worker connectivity and governed job lifecycle.

**Milestone 6+ — Specialist agents and business applications**

- Add specialist capabilities only when ownership, authority, data scope, and acceptance tests are defined.

## Current position

Milestone 1 definition framework and local review dashboard are complete on the feature branch. The canonical organization registry and six Cohort 1 manifest/prompt packages are implemented and inspectable in the browser. Every Cohort 1 definition is complete while its registry lifecycle remains `PLANNED` and activation remains blocked.

Milestone 2 enforcement and gateway work is pending. The local dashboard is not the hosted Control Plane. No agent runtime, model routing, tool execution, approval engine, audit persistence, authentication, database, deployed Control Plane, or Compute Plane worker is implemented. The six remaining registered agent identities do not yet have definition packages.

Architecture direction is defined in the [architecture documents](architecture/ARCHITECTURE.md); agent rollout status is defined in the [Agent Registry](governance/AGENT_REGISTRY.md).
