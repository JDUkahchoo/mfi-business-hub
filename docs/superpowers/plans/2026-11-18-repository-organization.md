# MFI Business Hub Repository Organization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate MFI Business Hub architecture and governance documentation into an authoritative, assistant-friendly repository structure without changing product behavior.

**Architecture:** Preserve the existing code scaffold and introduce explicit documentation boundaries for architecture and governance. A repository-level `AGENTS.md`, documentation index, updated cross-links, and structural tests keep Claude Code, Codex, OpenCode, and humans aligned.

**Tech Stack:** Markdown, Python 3, pytest

**Spec:** `docs/superpowers/specs/2026-11-18-repository-organization-design.md`

## Global Constraints

- Do not implement product features, networking, model-provider clients, databases, or agent runtime behavior.
- Preserve the existing `app/`, `config/`, `data/`, `prompts/`, `scripts/`, `tests/`, `web/`, `worker/`, and `.opencode/` scaffolds.
- Preserve `.env.example` secret placeholders and `.gitignore` secret exclusions.
- Do not expose LM Studio or local models directly to the public internet.
- Keep agent identity independent from model-provider selection.
- Do not grant AI executive authority because a human seat is vacant.
- The directory is not currently a Git repository; verification checkpoints replace commit steps.

## Review Focus

- Stale links after document moves must be detected by a repository-wide Markdown link check.
- Duplicate or conflicting source-of-truth paths must not remain after consolidation.
- The authority language must consistently distinguish `PROPOSE`, `APPROVE`, and `EXECUTE`.
- Node security guidance must require outbound-initiated authenticated connectivity and prohibit public LM Studio exposure.
- Shared assistant instructions must preserve user work and prohibit secrets from being committed.

---

### Task 1: Lock the target documentation paths in tests

**Files:**
- Modify: `tests/unit/test_repo_structure.py`

**Interfaces:**
- Consumes: the approved path list in the design document
- Produces: structural assertions used to verify all later tasks

- [ ] **Step 1: Replace the legacy path expectations with the approved documentation paths**

Assert the existence of `AGENTS.md`, `docs/README.md`, all three files under `docs/architecture/`, all four files under `docs/governance/`, the roadmap, component READMEs, and existing scaffold anchors.

- [ ] **Step 2: Add an assertion that legacy document locations no longer exist**

Cover root `ARCHITECTURE.md` and the four governance files directly under `docs/`.

- [ ] **Step 3: Run the structure tests and confirm they fail for missing target paths**

Run: `pytest tests/unit/test_repo_structure.py -v`

Expected: FAIL because the new paths do not yet exist.

### Task 2: Consolidate and expand architecture documentation

**Files:**
- Create: `docs/architecture/ARCHITECTURE.md`
- Create: `docs/architecture/HYBRID_ARCHITECTURE.md`
- Create: `docs/architecture/NODE_STANDARD.md`
- Delete after incorporation: `ARCHITECTURE.md`

**Interfaces:**
- Consumes: current root architecture seed, README architecture direction, and approved design
- Produces: authoritative system, hybrid-plane, and node boundaries referenced by all other documentation

- [ ] **Step 1: Move and expand the system architecture document**

Define system context, plane boundaries, model-gateway dependency direction, core domains, data ownership, security invariants, and phased implementation status.

- [ ] **Step 2: Add the hybrid architecture document**

Define Control Plane, Compute Plane, Cloud AI Plane, local-preferred/cloud-fallback/local-only routing, worker registry, job lifecycle, trust boundaries, and failure behavior.

- [ ] **Step 3: Add the node standard**

Define node identity, enrollment, capabilities, heartbeats, job claims, secrets, logs, updates, revocation, and minimum security requirements without committing to a premature transport implementation.

- [ ] **Step 4: Remove the incorporated root seed document**

Verify all useful statements from `ARCHITECTURE.md` appear in the new architecture set before deletion.

### Task 3: Consolidate and expand governance documentation

**Files:**
- Create: `docs/governance/ORGANIZATION.md`
- Create: `docs/governance/AGENT_STANDARD.md`
- Create: `docs/governance/AUTHORITY_MATRIX.md`
- Create: `docs/governance/AGENT_REGISTRY.md`
- Delete after incorporation: `docs/ORGANIZATION.md`
- Delete after incorporation: `docs/AGENT_STANDARD.md`
- Delete after incorporation: `docs/AUTHORITY_MATRIX.md`
- Delete after incorporation: `docs/AGENT_REGISTRY.md`

**Interfaces:**
- Consumes: current governance seeds, README principles, roadmap cohorts, and architecture boundaries
- Produces: canonical organizational and agent-governance references

- [ ] **Step 1: Expand the organization document**

Record the four pillars, cross-pillar revenue functions, `HUMAN`/`AI`/`HYBRID`/`VACANT` seat types, human precedence, and separation between organizational roles and runtime providers.

- [ ] **Step 2: Expand the agent standard**

Specify required metadata, prompt ownership, inputs and outputs, tool and data scopes, authority, provider-independent model requirements, auditability, approvals, testing, versioning, and retirement.

- [ ] **Step 3: Expand the authority matrix**

Define `READ`, `WRITE`, `PROPOSE`, `APPROVE`, and `EXECUTE`, default AI boundaries, human approval points, forbidden actions, and escalation rules.

- [ ] **Step 4: Expand the agent registry**

List canonical identifiers by cohort and function, distinguish registered/planned/implemented status, and state that the registry governs identity while OpenCode definitions mirror it.

- [ ] **Step 5: Remove the incorporated governance seed files**

Verify their useful content exists under `docs/governance/` before deletion.

### Task 4: Add shared navigation and assistant coordination

**Files:**
- Create: `AGENTS.md`
- Create: `docs/README.md`
- Modify: `README.md`
- Modify: `docs/ROADMAP.md`
- Modify: `.opencode/agents/README.md`
- Modify: `web/README.md`
- Modify: `worker/README.md`

**Interfaces:**
- Consumes: authoritative architecture and governance paths from Tasks 2 and 3
- Produces: consistent entry points and working rules for every repository participant

- [ ] **Step 1: Add repository-wide assistant instructions**

Define source-of-truth order, preservation rules, change discipline, secrets policy, approval boundaries, testing expectations, and multi-assistant coordination practices.

- [ ] **Step 2: Add the documentation index**

Describe each authoritative document, distinguish current implementation from planned architecture, and provide relative links.

- [ ] **Step 3: Rewrite the root README links and status language**

Keep setup instructions and the current/planned distinction while pointing to the new documentation hierarchy.

- [ ] **Step 4: Update supporting documents**

Correct links and terminology in the roadmap, OpenCode guidance, and web/worker READMEs.

### Task 5: Verify structure, links, and preservation

**Files:**
- Modify if needed: `tests/unit/test_repo_structure.py`
- Modify if needed: any Markdown file with a broken local link

**Interfaces:**
- Consumes: all prior task outputs
- Produces: verified repository organization

- [ ] **Step 1: Run the complete unit-test directory**

Run: `pytest tests/unit -v`

Expected: all tests PASS.

- [ ] **Step 2: Search for stale legacy paths and seed warnings**

Expected: no references to root `ARCHITECTURE.md`, legacy `docs/*.md` governance paths, or `SEED DRAFT` remain outside historical planning records where explicitly quoted.

- [ ] **Step 3: Validate every relative Markdown link**

Run a read-only link-validation script over all tracked Markdown files and confirm every local target exists.

- [ ] **Step 4: Inspect the final tree and confirm no application scaffold was removed**

Compare the final top-level and application-directory layout with the design constraints.

- [ ] **Step 5: Record the verification results**

Summarize tests, link validation, final paths, and the fact that no product features or dependencies were added.

