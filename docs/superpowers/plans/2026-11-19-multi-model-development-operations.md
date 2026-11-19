# Multi-Model Development Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore reliable Git operations and establish a governed Codex/Claude/OpenCode collaboration workflow with bounded Gemma and Nemotron local roles.

**Architecture:** GitHub issues and isolated branches/worktrees provide task ownership; Codex leads implementation, Claude provides independent architecture/review, and OpenCode supplies functional local subagents. Provider assignments remain routing policy rather than canonical MFI agent identity.

**Tech Stack:** Git, GitHub, Markdown, OpenCode V2 agent files, Python, pytest

**Spec:** `docs/superpowers/specs/2026-11-19-multi-model-development-operations-design.md`

## Global Constraints

- Preserve commit `2e9738e` and remote `https://github.com/JDUkahchoo/mfi-business-hub.git`.
- Do not replace Git metadata until tracked and untracked working-tree content is independently inventoried.
- Keep the broken `.git` directory as a recoverable backup outside the repository.
- Do not push, merge, or delete the backup without explicit approval.
- Do not hard-code undiscovered LM Studio model identifiers.
- Do not add product features or runtime provider integrations.
- Local roles may not access secrets, push, merge, approve their own work, or operate outside their assigned worktree.

## Review Focus

- Git recovery must not lose uncommitted or untracked files.
- Agent permissions must not allow local roles to push, merge, or read secret files.
- Functional role names must remain independent from provider/model names.
- Handoff instructions must identify one current owner and one next action without embedding secrets.
- Documentation links and source-of-truth paths must remain consistent after adding operations documents.

---

### Task 1: Recover the local Git worktree safely

**Resolution:** Git metadata was healthy. Restricted execution could read repository metadata but could not traverse the D: working tree, producing a misleading worktree error. Claude's original `.git` metadata was restored, and unrestricted verification confirmed a normal clean checkout at `2e9738e`. Metadata replacement is not required.

**Files:**
- Preserve outside repository: timestamped backup of current `.git`
- Replace only after verification: `.git`

**Interfaces:**
- Consumes: current working tree, commit `2e9738e`, and `origin`
- Produces: a normal clean `main` checkout with functional status/diff/add operations

- [x] **Step 1: Compare every tracked working file with the index and list untracked paths without using `git status`**

Expected: no modified tracked files and no unexpected untracked files other than the newly approved spec and plan.

- [x] **Step 2: Clone `origin` into a separate temporary directory**

Expected: clone checks out `main` at `2e9738e` and `git status --short --branch` succeeds.

- [x] **Step 3: Diagnose the failure before replacing Git metadata**

The same metadata worked when the process had D: worktree access. Restore the original metadata rather than replacing a healthy repository. Preserve the diagnostic replacement backup until the feature commit is verified.

- [x] **Step 4: Verify repository identity and working state with D: worktree access**

Run branch, remote, log, status, and diff checks. Expected: `main`, correct `origin`, `HEAD` at `2e9738e`, and only the approved new spec/plan are untracked.

### Task 2: Lock operational artifacts into the structural test

**Files:**
- Modify: `tests/unit/test_repo_structure.py`

**Interfaces:**
- Consumes: approved artifact paths
- Produces: file-versus-directory-aware repository contract

- [ ] **Step 1: Add failing expectations for the handoff, operations docs, ADR, and OpenCode agent files**

Split `REQUIRED_FILES` and `REQUIRED_DIRECTORIES`; use `is_file()` and `is_dir()`. Include `config/`, `scripts/`, `docs/decisions/`, and both planning directories.

- [ ] **Step 2: Run the structure tests and confirm failure for the missing operational artifacts**

Run: `python -m pytest tests/unit/test_repo_structure.py -q`

Expected: FAIL listing the new missing files.

### Task 3: Add the development operating model and handoff

**Files:**
- Create: `HANDOFF.md`
- Create: `docs/operations/AI_DEVELOPMENT_ROLES.md`
- Create: `docs/operations/BRANCH_WORKFLOW.md`
- Create: `docs/decisions/0001-multi-model-development-operating-model.md`
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: approved responsibility and Git ownership model
- Produces: durable working rules and current-state handoff

- [ ] **Step 1: Write the responsibility and routing policy**

Define Codex, Claude, local analyst, local execution worker, OpenCode, and human responsibilities; make Gemma/Nemotron assignments replaceable routing defaults.

- [ ] **Step 2: Write the branch/worktree workflow**

Define issue acceptance criteria, branch naming, isolated worktrees, single writer, read-only review, verification, approval, merge, and cleanup.

- [ ] **Step 3: Record the architecture decision**

Capture context, selected lead-and-specialist approach, rejected alternatives, consequences, and reevaluation triggers.

- [ ] **Step 4: Create the current handoff**

Record repository, branch, latest commit, milestone, completed foundation, current owner, next action, verification evidence, known constraints, and update rules.

- [ ] **Step 5: Link the operating documents from repository entry points**

Update `AGENTS.md`, `README.md`, and `docs/README.md` without duplicating their authoritative content.

### Task 4: Add bounded OpenCode local roles

**Files:**
- Create: `.opencode/agents/local-analyst.md`
- Create: `.opencode/agents/execution-worker.md`
- Create: `.opencode/README.md`
- Delete after migration: `.opencode/agents/README.md`

**Interfaces:**
- Consumes: responsibility and permission policy from Task 3
- Produces: OpenCode-discoverable functional subagents

- [ ] **Step 1: Add the local analyst agent**

Use OpenCode V2 frontmatter, `mode: subagent`, bounded steps, and permissions denying edits, shell execution, secret reads, and external-directory access.

- [ ] **Step 2: Add the execution-worker agent**

Use OpenCode V2 frontmatter, `mode: subagent`, bounded steps, and permissions denying secret reads, external-directory access, Git push, merges, destructive Git commands, and governance-file edits.

- [ ] **Step 3: Update OpenCode guidance**

Keep general guidance outside the agent-discovery directory so it is not parsed as an executable agent. Explain model selection through `/models`, prefer discovered LM Studio assignments, and prohibit guessed or committed credentials/model IDs.

### Task 5: Verify and commit locally

**Files:**
- Modify if needed: structural test and documentation links

**Interfaces:**
- Consumes: all prior task outputs
- Produces: reviewed local commit ready for user-approved push

- [ ] **Step 1: Run the full unit suite**

Run: `python -m pytest tests/unit -q`

Expected: all tests PASS.

- [ ] **Step 2: Validate all relative Markdown links and search for stale source-of-truth paths**

Expected: zero broken links and zero stale active-document references.

- [ ] **Step 3: Validate Git and inspect the complete diff**

Expected: only approved operational artifacts, tests, and navigation changes.

- [ ] **Step 4: Request independent read-only review and fix Critical or Important findings**

- [ ] **Step 5: Commit the approved work locally**

Commit message: `docs: define multi-model development workflow`

- [ ] **Step 6: Update `HANDOFF.md` with the resulting commit and rerun verification if that update changes the commit**

Do not push until Joshua explicitly approves the external update.
