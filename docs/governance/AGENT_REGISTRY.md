# MFI Agent Registry

## Purpose

This governance catalog defines the policy meaning of canonical agent identities and their planned rollout. The structured records in [`config/organization/registry.json`](../../config/organization/registry.json) are the machine-readable source for roles, seats, agents, lifecycle status, and explicit authority grants. Runtime configuration, prompts, and OpenCode definitions reference those canonical IDs rather than creating competing names.

Governance rules and lifecycle semantics remain authoritative in this document and the related governance documents. Structured record changes begin in the JSON registry and include any corresponding catalog update in the same reviewed commit; policy changes begin in governance documentation and include any required structured-record change in that commit.

## Status legend

- `PLANNED`: approved identity and direction; definition assets may exist, but no activated runtime authority exists.
- `DRAFT`: definition or prompt is being prepared.
- `TESTING`: implementation exists but is not authorized for production work.
- `ACTIVE`: approved for its documented production scope.
- `SUSPENDED`: temporarily unable to accept work.
- `RETIRED`: permanently inactive; history retained.

All agents below are currently `PLANNED`. The six Cohort 1 identities have complete manifest and prompt assets plus local readiness reporting; this does not create a runtime, grant authority, or permit activation. The remaining six identities have registry records only.

## Cohort 1 — orchestration, assurance, and pillar leadership

Definition status for all six: `COMPLETE`. Activation eligibility for all six: `BLOCKED`. Each definition has zero tools and zero authority grants. Inspect them with the [local definition commands](../operations/AGENT_DEFINITION_INSPECTION.md).

| Canonical ID | Function | Accountable area | Status |
|---|---|---|---|
| `mfi-orchestrator` | Routes governed tasks and coordinates agents | Enterprise operations | `PLANNED` |
| `mfi-qa-auditor` | Reviews outputs, evidence, policy compliance, and audit completeness | Quality assurance | `PLANNED` |
| `mfi-infrastructure-lead` | Supports Infrastructure & Supply Chain planning and coordination | Infrastructure & Supply Chain | `PLANNED` |
| `mfi-tech-entertainment-lead` | Supports technology, gaming, and entertainment work | Technology / Gaming / Entertainment | `PLANNED` |
| `mfi-investments-lead` | Supports investment research and governed opportunity analysis | Investments | `PLANNED` |
| `mfi-incubation-lead` | Supports validation and development of new ventures | Incubation | `PLANNED` |

## Cross-company revenue and executive copilots

| Canonical ID | Function | Accountable area | Status |
|---|---|---|---|
| `mfi-business-development-lead` | Coordinates pipeline development across pillars and channels | Business development | `PLANNED` |
| `mfi-government-business-lead` | Coordinates government-market opportunities across pillars | Government business | `PLANNED` |
| `mfi-private-sector-lead` | Coordinates commercial opportunities across pillars | Private-sector business | `PLANNED` |
| `mfi-cfo-copilot` | Provides governed finance analysis and draft recommendations | Human finance leadership | `PLANNED` |
| `mfi-coo-copilot` | Provides governed operating analysis and coordination support | Human operations leadership | `PLANNED` |
| `mfi-cto-copilot` | Provides governed technology analysis and architecture support | Human technology leadership | `PLANNED` |

## Specialist expansion

Finance, operations, technology, legal/risk, HR, customer success, government, private-sector, and other specialist agents are added only when they have an accountable owner, non-overlapping purpose, authority definition, prompt, tests, and activation approval under the [Agent Standard](AGENT_STANDARD.md).

## Registry rules

- Canonical IDs are stable and lowercase with hyphens.
- One ID represents one governed agent identity across prompts, configuration, logs, and assistant adapters.
- Model names do not appear in canonical IDs.
- A directory, prompt, or OpenCode definition does not make an agent active.
- Status changes require recorded review and, for `ACTIVE`, accountable human approval.
- Retired IDs are not reused for different purposes.

