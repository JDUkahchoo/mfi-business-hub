# MFI Business Hub Repository Organization Design

## Intent

Turn the existing MFI Business Hub scaffold into the shared, authoritative workspace used by humans, Claude Code, Codex, and OpenCode. The reorganization must make the architecture and governance easy to find without introducing product features or discarding useful seed material.

## Goals

- Preserve the existing application, worker, web, prompt, configuration, data, and test scaffolds.
- Establish clear homes for architecture and governance documents.
- Replace temporary seed warnings with useful, internally consistent source-of-truth documents.
- Add the previously planned hybrid architecture and compute-node standards.
- Give all coding assistants one set of repository coordination instructions.
- Keep links and the repository-structure test aligned with the new layout.

## Non-goals

- Implement the Control Plane, Compute Plane, model gateway, agents, database, or networking.
- Add or upgrade runtime dependencies.
- Migrate an external orchestrator or data store that is not present in this repository.
- Invent business policies beyond the architectural and governance principles already recorded in the scaffold and prior project discussion.

## Anti-goals

- Do not delete seed information before its useful content is incorporated.
- Do not expose LM Studio or local models directly to the public internet.
- Do not couple an agent identity to a particular model provider.
- Do not allow AI authority to expand merely because a human seat is vacant.
- Do not perform a speculative source-code restructure while the packages are still empty scaffolds.

## Constraints

- The project is currently not a Git repository, so all moves must be verified directly on disk.
- No older source-of-truth copies were found under `D:\Joshua\Claude`; the current seed documents and the approved project direction are the available inputs.
- The repository will remain Python-oriented for its application and tests, with separate `web/` and `worker/` boundaries.
- Existing secrets protections in `.gitignore` and `.env.example` must remain intact.

## Approaches Considered

### 1. Documentation-first consolidation — selected

Keep the application scaffold stable, organize architecture documents under `docs/architecture/`, organize governance documents under `docs/governance/`, add a documentation index and shared assistant instructions, and update tests and links. This improves clarity now without locking in premature implementation choices.

### 2. Minimal additive pass

Leave all existing files where they are and only add the two missing documents. This has the lowest immediate churn but leaves source-of-truth material fragmented and does not solve multi-assistant coordination.

### 3. Full domain-first repository redesign

Reorganize both documentation and source packages around deployable services immediately. This may eventually be appropriate, but the repository does not yet contain enough implementation to justify those boundaries.

## Approved Structure

```text
docs/
  README.md
  architecture/
    ARCHITECTURE.md
    HYBRID_ARCHITECTURE.md
    NODE_STANDARD.md
  governance/
    ORGANIZATION.md
    AGENT_STANDARD.md
    AUTHORITY_MATRIX.md
    AGENT_REGISTRY.md
  decisions/
  superpowers/
    specs/
    plans/
  ROADMAP.md
AGENTS.md
```

The existing `app/`, `config/`, `data/`, `prompts/`, `scripts/`, `tests/`, `web/`, `worker/`, and `.opencode/` structures remain in place.

## Document Responsibilities

- `README.md`: project entry point, status, quick start, and links.
- `docs/README.md`: documentation map and source-of-truth hierarchy.
- `docs/architecture/ARCHITECTURE.md`: system-wide components, boundaries, and dependency direction.
- `docs/architecture/HYBRID_ARCHITECTURE.md`: control, compute, and cloud-AI planes plus secure job routing.
- `docs/architecture/NODE_STANDARD.md`: worker identity, registration, capabilities, security, lifecycle, and job rules.
- `docs/governance/ORGANIZATION.md`: pillars, cross-pillar functions, seats, and reporting principles.
- `docs/governance/AGENT_STANDARD.md`: definition, lifecycle, prompts, provider independence, audit, and safety requirements for agents.
- `docs/governance/AUTHORITY_MATRIX.md`: authority vocabulary, default boundaries, approval rules, and escalation.
- `docs/governance/AGENT_REGISTRY.md`: canonical agent identifiers, cohorts, ownership, and implementation status.
- `AGENTS.md`: shared repository working rules for coding assistants.

## Verification

- Update `tests/unit/test_repo_structure.py` to assert the approved paths exist and obsolete root/document paths do not.
- Check that all local Markdown links resolve.
- Run `pytest tests/unit`.
- Inspect the final tree and search for stale references to moved documents.

