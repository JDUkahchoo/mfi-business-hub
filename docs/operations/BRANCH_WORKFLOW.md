# Branch and Worktree Workflow

## Core rule

One task has one GitHub issue, one named writer, one feature branch, and one isolated worktree. Other agents may inspect or review that worktree but must not edit it.

## 1. Define the task

The GitHub issue records the objective, scope, non-goals, acceptance criteria, security or authority considerations, dependencies, and required verification. Material ambiguity is resolved before implementation begins.

## 2. Assign ownership

Assign exactly one writer. Record the writer, branch, worktree path, reviewer, and next action in `HANDOFF.md`. If ownership changes, the current owner updates the handoff before the new writer edits.

## 3. Create the branch and worktree

Use descriptive branches:

```text
feat/<issue>-<short-name>
fix/<issue>-<short-name>
docs/<issue>-<short-name>
chore/<issue>-<short-name>
```

For the main checkout, create linked worktrees under its ignored `.worktrees/` directory. From an existing linked worktree, create the next worktree as a sibling outside the current worktree rather than nesting it. Never share one feature worktree between concurrent writers.

## 4. Implement and verify

The writer reads `AGENTS.md`, the relevant source-of-truth documents, and the issue before editing. Use failing tests first for behavior changes. Keep changes within the issue scope, preserve unrelated work, and record verification evidence rather than asserting success from inspection alone.

## 5. Review

The reviewer operates read-only and returns findings in severity order with file and line references. The reviewer does not fix its own findings on the writer's branch. Critical and important findings are resolved before merge; deferred minor findings are recorded explicitly.

## 6. Approve and merge

Joshua approves changes that affect business intent, architecture, authority, security posture, external communication, cost commitments, or irreversible effects. Passing tests and reviewer approval do not replace human approval where governance requires it.

Pushes and merges are deliberate external actions. The writer confirms the target remote and base branch, obtains the required approval, and avoids force-pushes unless Joshua explicitly authorizes one for a known branch.

## 7. Handoff and cleanup

After merge, update `HANDOFF.md` with the merged commit, verification, current owner, milestone status, and next action. Before cleanup, inventory tracked changes, ordinary untracked files, and ignored files. Preserve unique material outside the target and verify that copy before removing the worktree. Remove a worktree only after its work exists in a commit and the merge or preservation decision is confirmed. Never force-remove a worktree containing unique changes.

## Emergency rule

If two assistants have edited the same branch, stop both writers. Preserve both working states, compare changes, appoint one integration owner, and reconcile through a new branch. Do not resolve the conflict by overwriting whichever version appears older.
