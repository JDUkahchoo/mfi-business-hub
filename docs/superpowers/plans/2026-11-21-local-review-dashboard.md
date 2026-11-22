# Local Agent Review Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished, read-only, loopback-only browser dashboard for reviewing the six validated Cohort 1 agent definitions without activating agents, exposing prompts by default, or changing repository data.

**Architecture:** A dependency-free Python adapter converts `AgentDefinitionService` and readiness results into immutable JSON-safe view models. A standard-library `ThreadingHTTPServer` exposes four read-only APIs plus an allowlisted static application; the browser renders the approved governed-operations-folio interface with semantic HTML, hash navigation, and an explicit prompt-reveal request.

**Tech Stack:** Python 3 standard library, immutable dataclasses, `ThreadingHTTPServer`, vanilla HTML/CSS/JavaScript, pytest.

**Spec:** `docs/superpowers/specs/2026-11-21-local-review-dashboard-design.md`

## Global Constraints

- Runtime code uses only the Python standard library; browser assets use no framework, CDN, remote font, analytics, or external network dependency.
- Bind only to `127.0.0.1` or `localhost`; reject ports outside `1..65535`.
- Support only read operations; `GET` and `HEAD` are allowed, mutation methods return `405`, and the dashboard writes no repository or browser-persistent data.
- Load canonical agent data only through the existing validated repositories, `AgentDefinitionService`, and readiness evaluator; browser assets contain no duplicated agent records.
- Keep prompt bodies absent from the HTML, dashboard snapshot, agent summaries, and agent-detail response; fetch them only from the explicit prompt endpoint.
- Fail a request atomically on validation errors or inconsistent SHA-256 values for any repeated prompt path; do not retry or combine versions.
- Allowlist static paths, disable directory listing, return `Cache-Control: no-store` for HTML and APIs, and reveal no filesystem paths in route errors.
- Preserve the exact governance state: six complete definitions, six `PLANNED`, six `BLOCKED`, zero tools, zero grants, and zero activation-eligible agents.
- Preserve source bytes and modification times across every dashboard request.
- Do not add deployment configuration, authentication, model/runtime calls, activation controls, mutations, or GitHub publishing.

## Review Focus

- A shared prompt edited between agent loads must produce one atomic validation failure, never a mixed snapshot; pin this in Task 1.
- Missing, malformed, or concurrently changing registry/manifest/prompt sources must return a stable `422` without partial agent data; pin this in Tasks 1 and 2.
- Plain, encoded, backslash, and drive-qualified traversal attempts must return `404` without local path disclosure; pin this in Task 2.
- Unknown or control-character-bearing agent IDs and unexpected routes must produce escaped, stable errors rather than tracebacks; pin this in Task 2.
- Requests, including explicit prompt reveal, must leave every registry, manifest, prompt, and lifecycle source byte and modification time unchanged; pin this in Task 5.

---

## File Structure

- `app/local_dashboard/__init__.py` — local-dashboard public package boundary.
- `app/local_dashboard/models.py` — frozen view models and deterministic JSON payload conversion.
- `app/local_dashboard/service.py` — validated snapshot construction, fingerprint consistency, agent lookup, and prompt separation.
- `app/local_dashboard/server.py` — loopback HTTP boundary, routing, error mapping, and allowlisted static serving.
- `app/local_dashboard/cli.py` — argument validation, service/server wiring, URL printing, optional browser opening, and clean shutdown.
- `web/local-dashboard/index.html` — semantic application shell and loading/error roots.
- `web/local-dashboard/styles.css` — approved governed-operations-folio design, responsive layout, focus, and reduced motion.
- `web/local-dashboard/app.js` — API client, safe renderers, hash navigation, filters, dialog, prompt reveal, and recovery states.
- `tests/unit/local_dashboard/` — focused model, service, server, CLI, and asset tests.
- `docs/operations/LOCAL_DASHBOARD.md` plus existing status documents — operating instructions and honest milestone state.

### Task 1: Immutable dashboard models and governed snapshot service

**Files:**
- Create: `app/local_dashboard/__init__.py`
- Create: `app/local_dashboard/models.py`
- Create: `app/local_dashboard/service.py`
- Create: `tests/unit/local_dashboard/__init__.py`
- Create: `tests/unit/local_dashboard/conftest.py`
- Create: `tests/unit/local_dashboard/test_models.py`
- Create: `tests/unit/local_dashboard/test_service.py`

**Interfaces:**
- Consumes: `AgentDefinitionService.load_all() -> tuple[GovernedAgentDefinition, ...]`, `evaluate_all(...) -> tuple[ReadinessReport, ...]`, and registry owner-role/pillar relationships already present in each joined definition's source registry.
- Produces: frozen `DashboardCounts`, `PillarView`, `ContractView`, `ApprovalView`, `AcceptanceCriterionView`, `PromptSourceView`, `ReadinessGroupView`, `AgentSummaryView`, `AgentDetailView`, `DashboardSnapshot`, `PromptView`, and `HealthView`, each with `to_payload() -> dict[str, object]`; `UnknownAgentError`; `InconsistentSnapshotError`; and `LocalDashboardService.dashboard()`, `.agent_detail(agent_id)`, `.prompt(agent_id)`, and `.health()`.

- [ ] **Step 1: Write failing model tests**

Assert every view model is a frozen, slotted dataclass; nested payloads contain only `dict`, `list`, `str`, `int`, `bool`, and `None`; tuples become arrays; and `json.dumps(model.to_payload())` succeeds without a custom encoder.

- [ ] **Step 2: Run the model tests and confirm the missing-package failure**

Run: `python -m pytest tests/unit/local_dashboard/test_models.py -v`

Expected: FAIL because `app.local_dashboard.models` does not exist.

- [ ] **Step 3: Implement the immutable view-model vocabulary**

Use exact payload keys from the spec: `generated_at`, `counts`, `pillars`, `agents`, `readiness_blockers`, and `safety_boundaries` for `DashboardSnapshot`; registry metadata, responsibilities/boundaries, contracts, capability/system/data/routing/approval/audit/failure/escalation/source/readiness fields for `AgentDetailView`; and `agent_id`, `composed_prompt`, and `sources` for `PromptView`. Store enum values as strings at the adapter boundary and sort only where governance order is not already defined.

- [ ] **Step 4: Run model tests to green**

Run: `python -m pytest tests/unit/local_dashboard/test_models.py -v`

Expected: PASS.

- [ ] **Step 5: Write failing service tests for the real six-agent repository**

Test `LocalDashboardService` with a fixed UTC clock and the existing JSON repositories. Assert:

- ordered summaries are `mfi-orchestrator`, `mfi-qa-auditor`, `mfi-infrastructure-lead`, `mfi-tech-entertainment-lead`, `mfi-investments-lead`, `mfi-incubation-lead`;
- counts are definitions `6`, complete `6`, active `0`, planned `6`, eligible `0`, blocked `6`, tools `0`, grants `0`;
- the four registry-derived pillars each contain the correct lead while Orchestrator is `COORDINATION` and QA Auditor is `ASSURANCE`;
- completeness, lifecycle, and eligibility remain separate fields;
- detail payloads contain all governed manifest fields and source fingerprints but no `composed_prompt`, prompt `text`, or equivalent body field;
- prompt payload includes composed text only when `.prompt(agent_id)` is called;
- unknown IDs raise `UnknownAgentError`;
- the generated timestamp is deterministic under the injected clock.

- [ ] **Step 6: Add failing atomicity and concurrency-focused service tests**

Use injected definition services to assert: one validation exception yields no snapshot; two appearances of a shared source path with different digests raise `InconsistentSnapshotError`; the same digest repeated is accepted; prompt lookup reloads a full fresh snapshot instead of reusing stale detail state; and finding messages are deterministic and contain no prompt bodies.

- [ ] **Step 7: Run service tests and confirm failures**

Run: `python -m pytest tests/unit/local_dashboard/test_service.py -v`

Expected: FAIL because `LocalDashboardService` is not implemented.

- [ ] **Step 8: Implement `LocalDashboardService`**

Constructor: `LocalDashboardService(definition_service: AgentDefinitionService, clock: Callable[[], datetime] | None = None)`. Each public method loads and validates one all-or-nothing snapshot. `_load()` must compare all `(path, sha256_digest)` pairs, reject a path associated with more than one digest, call `evaluate_all`, build registry-derived pillar/category context, and never cache definitions or prompt text between requests.

- [ ] **Step 9: Run Task 1 tests and the existing definition suite**

Run: `python -m pytest tests/unit/local_dashboard/test_models.py tests/unit/local_dashboard/test_service.py tests/unit/agents -q`

Expected: all selected tests pass, with only the existing host-permission symlink skip permitted.

- [ ] **Step 10: Commit Task 1**

```powershell
git add app/local_dashboard tests/unit/local_dashboard
git commit -m "feat: add governed dashboard snapshot service"
```

### Task 2: Loopback read-only HTTP server and security boundary

**Files:**
- Create: `app/local_dashboard/server.py`
- Create: `tests/unit/local_dashboard/test_server.py`

**Interfaces:**
- Consumes: Task 1's `LocalDashboardService` public methods and `to_payload()` results.
- Produces: `validate_host(host: str) -> str`, `validate_port(port: int) -> int`, `make_handler(service: LocalDashboardService, static_root: Path) -> type[BaseHTTPRequestHandler]`, and `create_server(service, static_root, host="127.0.0.1", port=8765) -> ThreadingHTTPServer`.

- [ ] **Step 1: Write failing host, port, and route tests**

Assert only `127.0.0.1` and `localhost` are accepted; booleans, non-integers, `0`, and values above `65535` are rejected. Start an ephemeral loopback server and verify `GET`/`HEAD` for `/api/dashboard`, `/api/health`, `/api/agents/{id}`, `/api/agents/{id}/prompt`, `/`, `/index.html`, `/styles.css`, and `/app.js`, including correct JSON or static content types and empty HEAD bodies.

- [ ] **Step 2: Add failing method, cache, error, and traversal tests**

Assert:

- `POST`, `PUT`, `PATCH`, and `DELETE` return `405` with `Allow: GET, HEAD`;
- APIs and HTML include `Cache-Control: no-store`;
- unknown agent/routes/assets and directory requests return `404`;
- `/../`, `%2e%2e`, double-encoded traversal, backslashes, UNC-like paths, drive-qualified paths, NUL encoding, query tricks, and unexpected filenames never escape the allowlist or disclose a filesystem path;
- domain validation failures map to `422` as `{"error":{"code":"validation_failed","message":...,"findings":[...]}}` with one escaped line per finding and no partial data;
- control characters in findings and agent IDs are escaped;
- an unexpected exception maps to generic `500` browser JSON while the console log receives the exception;
- unknown IDs map to `404`, and no error contains a traceback.

- [ ] **Step 3: Run the server tests and confirm failure**

Run: `python -m pytest tests/unit/local_dashboard/test_server.py -v`

Expected: FAIL because `app.local_dashboard.server` does not exist.

- [ ] **Step 4: Implement the HTTP boundary**

Use a handler factory bound to one service and one resolved static root. Parse only URL paths, percent-decode once for classification while rejecting ambiguous/unsafe forms, map only the exact API patterns, and serve only the four static aliases/files. Serialize compact UTF-8 JSON, set `Content-Length`, suppress bodies for HEAD, provide deterministic error codes, and override default directory behavior and verbose request logging without hiding unexpected console exceptions.

- [ ] **Step 5: Run Task 2 tests and the Task 1 regression set**

Run: `python -m pytest tests/unit/local_dashboard/test_server.py tests/unit/local_dashboard/test_service.py tests/unit/local_dashboard/test_models.py -q`

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```powershell
git add app/local_dashboard/server.py tests/unit/local_dashboard/test_server.py
git commit -m "feat: add loopback dashboard server"
```

### Task 3: Local command, startup validation, and operator-visible lifecycle

**Files:**
- Create: `app/local_dashboard/cli.py`
- Create: `tests/unit/local_dashboard/test_cli.py`

**Interfaces:**
- Consumes: the existing JSON repositories and prompt loader plus Task 1's service and Task 2's server factory.
- Produces: `_default_repo_root() -> Path`, `_build_service(repo_root: Path) -> LocalDashboardService`, `_parser() -> argparse.ArgumentParser`, and `main(argv: Sequence[str] | None = None) -> int`; public command `python -m app.local_dashboard.cli`.

- [ ] **Step 1: Write failing CLI tests**

Assert default repo-root resolution works from a current directory outside the repository; defaults are `127.0.0.1:8765`; `--repo-root`, `--host`, `--port`, and `--open` parse exactly; non-loopback hosts and invalid ports return exit code `2` with one concise diagnostic and no traceback; invalid repository/static/definition data fail before serving; a fake server prints `Dashboard: http://127.0.0.1:8765/` and `Stop: Ctrl+C`; `--open` calls `webbrowser.open` only after the server is ready; and `KeyboardInterrupt` closes the server and exits cleanly.

- [ ] **Step 2: Run CLI tests and confirm failure**

Run: `python -m pytest tests/unit/local_dashboard/test_cli.py -v`

Expected: FAIL because the CLI module does not exist.

- [ ] **Step 3: Implement CLI wiring and fail-closed startup**

Resolve the repository root, require `web/local-dashboard` and the governed sources, construct `JsonOrganizationRepository`, `JsonAgentManifestRepository`, `PromptLoader`, `AgentDefinitionService`, and `LocalDashboardService`, then perform one health validation before calling `serve_forever()`. Catch expected registry/definition/configuration errors for concise stderr output; do not swallow programming errors after startup.

- [ ] **Step 4: Run the command tests and an outside-directory smoke check**

Run: `python -m pytest tests/unit/local_dashboard/test_cli.py -q`

Run from a temporary directory: `python -m app.local_dashboard.cli --port 0`

Expected: the tests pass; the smoke command exits `2` with the exact invalid-port message and no import/path failure.

- [ ] **Step 5: Commit Task 3**

```powershell
git add app/local_dashboard/cli.py tests/unit/local_dashboard/test_cli.py
git commit -m "feat: add local dashboard command"
```

### Task 4: Approved governed-operations-folio browser experience

**Files:**
- Create: `web/local-dashboard/index.html`
- Create: `web/local-dashboard/styles.css`
- Create: `web/local-dashboard/app.js`
- Create: `tests/unit/local_dashboard/test_assets.py`

**Interfaces:**
- Consumes: `/api/dashboard`, `/api/agents/{agent_id}`, and the explicit `/prompt` endpoint from Task 2.
- Produces: hash routes `#overview`, `#agents`, `#agent/<id>`, and `#readiness`; in-memory filter/search state; semantic detail dialog; deliberate prompt reveal/close behavior.

- [ ] **Step 1: Write failing static-contract tests**

Assert the HTML contains semantic landmarks, one `h1`, navigation buttons/links, loading and fatal-error roots, status live region, and no agent records or prompt bodies. Assert all three assets contain no `http://`, `https://`, protocol-relative URL, CDN, remote font, inline event handler, `localStorage`, `sessionStorage`, `eval`, or mutation/activation endpoint. Assert JavaScript calls the prompt endpoint only inside the explicit reveal handler and renders API strings through `textContent`/node construction rather than repository-content `innerHTML`.

- [ ] **Step 2: Run asset tests and confirm failure**

Run: `python -m pytest tests/unit/local_dashboard/test_assets.py -v`

Expected: FAIL because the static application does not exist.

- [ ] **Step 3: Implement the semantic shell and design tokens**

Build the narrow charter-navy navigation rail, persistent governance ribbon, folio-paper canvas, enterprise coordination rail, four-pillar field, compact agent ledger, two-column detail view, and readiness sequence using the exact approved color and font tokens. Add visible focus, 44px minimum interactive targets, responsive top navigation and stacked details, horizontal ribbon overflow, `prefers-reduced-motion`, print-safe contrast, and no hover-only information.

- [ ] **Step 4: Implement safe data rendering and navigation**

Use a small state object held only in memory. Fetch the non-prompt dashboard at startup; lazy-fetch detail on agent selection; use `URLSearchParams` only for request construction, `encodeURIComponent` for IDs, and DOM node creation plus `textContent` for all API values. Preserve filter/search for the current page lifetime, synchronize hash/history, and render exact loading, network, validation, unknown-agent, and empty-filter recovery messages.

- [ ] **Step 5: Implement accessible prompt reveal and close**

The reveal button must explain that viewing does not run the agent, call `/prompt` only after activation, show provenance beside composed text, and never cache the body outside the active detail state. Closing hides/removes the prompt text, clears the prompt state, and returns focus to the reveal trigger. Escape exits the viewer, focus remains contained while open, and route changes clear revealed prompt content.

- [ ] **Step 6: Run asset and HTTP integration tests**

Run: `python -m pytest tests/unit/local_dashboard/test_assets.py tests/unit/local_dashboard/test_server.py -q`

Expected: PASS.

- [ ] **Step 7: Start the real app and conduct the visual checkpoint**

Run: `python -m app.local_dashboard.cli --port 8765 --open`

Manually verify at approximately `1440x900`, `1024x768`, and `390x844`: overview hierarchy; all ledger filters/search; six detail routes; long blocker wrapping; keyboard-only navigation; visible focus; prompt reveal/close/focus return; reduced-motion behavior; loading/network/validation/unknown/empty states; no horizontal page overflow; and no controls implying activation, approval, execution, editing, saving, or sending. Capture desktop and mobile screenshots for review, but do not add throwaway mockup files to product assets.

- [ ] **Step 8: Commit Task 4**

```powershell
git add web/local-dashboard tests/unit/local_dashboard/test_assets.py
git commit -m "feat: add local agent review interface"
```

### Task 5: Read-only acceptance proof and operating documentation

**Files:**
- Create: `tests/unit/local_dashboard/test_read_only_acceptance.py`
- Create: `docs/operations/LOCAL_DASHBOARD.md`
- Modify: `README.md`
- Modify: `web/README.md`
- Modify: `docs/ROADMAP.md`
- Modify: `HANDOFF.md`

**Interfaces:**
- Consumes: the complete local dashboard command and real governed repository assets.
- Produces: end-to-end local acceptance evidence, start/stop/troubleshooting guide, and accurate repository status for the next contributor.

- [ ] **Step 1: Write the failing read-only acceptance test**

Snapshot bytes and `st_mtime_ns` for `config/organization/registry.json`, all six `config/agents/cohort-1/*.json` files, and all referenced prompt Markdown files. Exercise health, dashboard, every detail route, every prompt route, HEAD, 404, traversal, and mutation-method responses through a real ephemeral server; then assert every tracked file and canonical lifecycle value is unchanged and that no new file appears in the governed source directories.

- [ ] **Step 2: Run the acceptance test and address only product defects it exposes**

Run: `python -m pytest tests/unit/local_dashboard/test_read_only_acceptance.py -v`

Expected: PASS after any minimal server/service correction; never weaken the unchanged-file assertions.

- [ ] **Step 3: Write the local operating guide**

Document prerequisites, `python -m app.local_dashboard.cli`, optional `--port`, `--repo-root`, and `--open`, exact loopback-only boundary, Ctrl+C stop procedure, port-in-use and invalid-source troubleshooting, prompt-reveal privacy behavior, and an explicit list of what the tool cannot do.

- [ ] **Step 4: Update status documentation honestly**

Update the repository and web READMEs, roadmap, and handoff to say the local review dashboard exists while the hosted Control Plane, authentication, database, permissions, approvals, audit persistence, model routing, worker connectivity, deployment, and agent runtime do not. Record the feature branch/worktree, verification commands, screenshots reviewed, and next decision without claiming a push or deployment.

- [ ] **Step 5: Run complete verification**

Run: `python -m pytest tests/unit -q`

Run: `python -m app.agents.definitions.cli validate`

Run: `python -m app.agents.definitions.cli readiness`

Run: `git diff --check`

Expected: the complete unit suite passes with only the documented Windows symlink-permission skip; validation reports six definitions and zero grants; readiness reports six complete, zero eligible, six blocked; diff check is clean.

- [ ] **Step 6: Perform final local smoke test**

Start `python -m app.local_dashboard.cli --port 8765`, request `/api/health`, `/api/dashboard`, one detail route, and its prompt route, then stop with Ctrl+C. Confirm the printed URL works, response counts match acceptance, prompt text appears only in the prompt response, and shutdown releases the port.

- [ ] **Step 7: Commit Task 5**

```powershell
git add tests/unit/local_dashboard/test_read_only_acceptance.py docs/operations/LOCAL_DASHBOARD.md README.md web/README.md docs/ROADMAP.md HANDOFF.md
git commit -m "docs: complete local dashboard checkpoint"
```

## Self-Review Result

- Spec coverage: every goal, API, view, visual rule, browser behavior, error state, security invariant, acceptance criterion, and documentation update maps to a task above.
- Step scan: each step produces one testable artifact or verification result; private helper and CSS naming remain intentionally delegated to the implementer.
- Type consistency: Task 1 owns all payload models and service methods consumed unchanged by Tasks 2-5; endpoint names and hash routes match the design.
- Review Focus: all five high-risk input/failure classes are pinned in Tasks 1, 2, and 5.
- Proportion: the plan fixes interfaces and acceptance behavior without transcribing implementation bodies.

