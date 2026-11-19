# Multi-Model Development Operations Design

## Intent

Establish a durable way for Joshua, Codex, Claude, Gemma 4, and NVIDIA Nemotron 3.5 Lightning to collaborate on the MFI Business Hub without overwriting one another, duplicating authority, or coupling permanent MFI agent identities to model vendors.

## Goals

- Restore a reliable local Git working tree while preserving commit `2e9738e` and the `origin` remote.
- Make Codex the primary implementation lead and Claude the architecture/review lead.
- Use OpenCode to expose bounded local functional roles for private analysis and high-volume execution.
- Assign Gemma 4 as the preferred local analyst and Nemotron 3.5 Lightning as the preferred local execution worker, subject to installed-model discovery and evaluation.
- Enforce one issue, one branch/worktree, one writer, and independent review before merge.
- Add a durable handoff that every material work session updates.
- Preserve human approval for architecture, authority changes, external effects, and merges.

## Non-goals

- Implement MFI business agents, the model gateway, the Control Plane, or the Compute Plane.
- Hard-code provider names into canonical MFI business-agent IDs.
- Assume an LM Studio model identifier that has not been discovered on the local machine.
- Give local models permission to push, merge, approve their own work, access secrets, or operate outside the assigned worktree.
- Replace GitHub issues, branches, tests, or human review with model-to-model conversation.

## Anti-goals

- Multiple assistants editing the same branch or file concurrently.
- A reviewer silently becoming an implementer.
- Treating a successful model response as verification.
- Sending local-only data to cloud models as an automatic fallback.
- Recording API keys, credentials, protected content, or unrestricted prompts in handoffs or logs.

## Current constraints

- The remote is `https://github.com/JDUkahchoo/mfi-business-hub.git`.
- `main` and `origin/main` point to initial commit `2e9738e`.
- No repository handoff currently exists.
- Git recognizes the local directory as a worktree, but `git status`, `git diff`, and `git add` fail with `fatal: this operation must be run in a work tree`.
- The current working files must be compared with `HEAD` before Git metadata is repaired or replaced.
- LM Studio discovery and OpenCode execution require access outside the present restricted environment and may need explicit approval.

## Approaches considered

### 1. Codex-only development

Use Codex for all implementation, planning, and review. This is simple but wastes Claude's independent review value and the privacy and throughput benefits of local models.

### 2. Peer multi-agent editing

Allow Codex, Claude, Gemma, and Nemotron to edit the same checkout as equal peers. This maximizes concurrency but creates unclear ownership, conflicting plans, and unsafe merges.

### 3. Lead-and-specialist workflow — selected

Codex owns implementation and integration, Claude owns architecture and independent review, and OpenCode routes bounded local roles to Gemma or Nemotron. GitHub issues and isolated branches/worktrees define ownership, while Joshua approves material decisions and merges.

## Responsibility model

| Participant | Primary responsibility | May write | Must not independently do |
|---|---|---|---|
| Joshua | Product owner and final authority | Any approved repository or business artifact | Delegate non-delegable human authority by absence |
| Codex | Engineering lead, plans, implementation, tests, integration | Assigned feature branch/worktree | Merge or push material work without the required approval |
| Claude | Architecture, requirements, threat review, independent code review | Assigned design/review branch when explicitly requested | Co-edit the implementer's branch or self-approve reviewed work |
| Local analyst role | Private document analysis, extraction, summaries, multimodal interpretation | Draft output locations explicitly assigned to the task | Edit product code, run shell commands, or access secrets |
| Local execution-worker role | Source analysis, transformations, and tightly scoped patch proposals | Only `data/development/worker-output/`; a trusted engineering lead applies changes and runs tests | Run host shell commands, edit repository source, push, merge, change governance, delegate, use connectors, or expand its own permissions |
| OpenCode | Local role and model orchestration | Configuration and session state within approved scope | Act as organizational authority or bypass Git ownership |

Preferred initial assignments are Gemma 4 for the local analyst role and Nemotron 3.5 Lightning for the local execution-worker role. These are routing defaults, not permanent identities; evaluations may change the provider assignment without redefining the role.

## Git and ownership workflow

```text
Human-approved objective
        -> GitHub issue with acceptance criteria
        -> one named owner
        -> one branch and isolated worktree
        -> tests and recorded verification
        -> independent review
        -> human-approved merge to main
        -> HANDOFF.md updated
```

Only the named owner writes to a task branch. Reviewers remain read-only and return findings. If ownership changes, the handoff records the transfer before the new writer edits.

## Safe Git recovery

1. Enumerate tracked files and compare their working-tree hashes with the index/`HEAD` without relying on `git status`.
2. Enumerate untracked files outside `.git` and preserve any unexpected content.
3. Clone `origin` to a separate temporary directory and verify the clone has a functional worktree at commit `2e9738e`.
4. Move the broken `.git` directory to a timestamped backup outside the repository.
5. Move the verified clone's `.git` directory into the existing project root, leaving working files in place.
6. Verify `status`, `diff`, branch, remote, log, and tests before deleting no backups.

The backup remains until the repaired checkout and first new commit are verified.

## Repository artifacts

- `HANDOFF.md`: concise current state, ownership, verification, next action, and known risks.
- `docs/operations/AI_DEVELOPMENT_ROLES.md`: responsibilities, routing defaults, escalation, and evaluation rules.
- `docs/operations/BRANCH_WORKFLOW.md`: issue, branch, worktree, writer, reviewer, merge, and handoff procedure.
- `docs/decisions/0001-multi-model-development-operating-model.md`: durable record of the selected approach.
- `.opencode/agents/local-analyst.md`: read-only local analysis role.
- `.opencode/agents/execution-worker.md`: bounded local execution role with no push/merge authority.
- Updated `AGENTS.md`, `README.md`, `docs/README.md`, and structural tests.

## Verification

- Git working-tree commands operate normally against `main` and `origin` remains correct.
- The working tree is clean before repository artifacts are added.
- OpenCode agent definitions use current V2 frontmatter and restrictive permissions.
- Local Markdown links resolve.
- Structural tests distinguish required files from required directories.
- The complete unit suite passes.
- No secrets, provider credentials, or guessed local model identifiers are committed.
