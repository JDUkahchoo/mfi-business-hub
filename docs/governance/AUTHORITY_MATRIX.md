# MFI Authority Matrix

## Authority levels

| Level | Meaning | Typical AI boundary |
|---|---|---|
| `READ` | View specifically authorized information. | Allowed only for assigned sources and data classes. |
| `WRITE` | Create or update drafts, records, or working artifacts. | Allowed in scoped systems; does not imply approval or external effect. |
| `PROPOSE` | Recommend a decision or prepare an action for review. | Normal ceiling for material business, legal, financial, or personnel decisions. |
| `APPROVE` | Authorize a proposal to proceed. | Human-owned by default; any exception must be explicit, narrow, and revocable. |
| `EXECUTE` | Carry out an approved action or produce an external effect. | Requires explicit scope and any prerequisite human approval. |

Authority is cumulative only when explicitly granted. `WRITE` does not imply `READ` for unrelated data, `PROPOSE` does not imply `APPROVE`, and `APPROVE` does not automatically imply `EXECUTE`.

## Default decision matrix

| Activity | AI agent | Accountable human |
|---|---|---|
| Research and summarize authorized information | `READ`, `WRITE` | Defines scope and accepts material conclusions |
| Draft internal plans, correspondence, or proposals | `WRITE`, `PROPOSE` | Reviews and approves where required |
| Change prompts or non-secret configuration | `PROPOSE`; limited `WRITE` in development | Approves activation and authority changes |
| Send external communications | Draft only unless explicitly delegated | Approves recipient, claims, and send action |
| Commit funds, sign terms, or enter contracts | `PROPOSE` only | `APPROVE` and `EXECUTE` through an authorized person |
| Make employment, legal, tax, or regulated decisions | Research or draft support only | Owns decision and professional review |
| Delete records or perform irreversible actions | `PROPOSE` by default | Approves scope and recovery plan |
| Run approved reversible automation | Scoped `EXECUTE` | Defines limits and monitors exceptions |

## Non-delegable defaults

Unless a later policy explicitly and lawfully says otherwise, AI agents may not independently:

- sign contracts or represent themselves as corporate officers;
- open, close, or control financial accounts;
- transfer funds or commit company capital;
- hire, terminate, discipline, or set compensation;
- provide final legal, tax, medical, or regulated professional determinations;
- publish binding claims or confidential information externally;
- expand their own permissions, approve their own material actions, or disable audit controls.

A vacant human role does not relax these restrictions.

## Approval requirements

Approvals identify the proposal, approver, timestamp, scope, conditions, expiration when applicable, and resulting execution. A materially changed proposal requires new approval. Self-approval by the proposing agent is prohibited for actions requiring human review.

## Escalation

When authority is unclear, the agent stops before the external or irreversible effect, preserves its draft and evidence, and routes the matter to the accountable human or hybrid seat. Failure to obtain an answer is not approval.

## Enforcement direction

The future permissions engine will enforce scoped grants; the approval engine will bind approvals to actions; and the audit system will record decisions and execution. Until those systems exist, this document governs project design and manual operating procedures rather than claiming automated enforcement.

