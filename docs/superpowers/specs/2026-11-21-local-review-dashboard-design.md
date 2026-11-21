# Local Agent Review Dashboard Design

## Intent

Build the first live, visual MFI Business Hub experience entirely locally so Joshua can inspect the six Cohort 1 agent definitions, understand their boundaries, and make product judgments before any deployment work begins.

The dashboard is a read-only review surface over the existing organization registry, agent manifests, prompts, and readiness evaluator. It does not create a Control Plane account system, activate an agent, call a model, persist evidence, grant authority, or perform business work.

## Why this is the next slice

The definition framework is complete and independently reviewed, but its current experience is command-line output and source files. A browser view will make relationships, readiness blockers, and role boundaries easier to assess. Building the local review surface before deployment also lets the information architecture and visual language mature without prematurely choosing Cloudflare products, authentication, a database, or a JavaScript framework.

## Goals

- Provide one local command that starts a browser-accessible dashboard on loopback only.
- Show all six Cohort 1 agents with canonical names, purposes, owners, lifecycle, definition completeness, and activation eligibility.
- Make `COMPLETE`, `PLANNED`, and `BLOCKED` visually distinct so definition completeness is never confused with activation.
- Show responsibilities, non-responsibilities, contracts, capabilities, routing policy, data classifications, approval requirements, audit obligations, escalation policy, and readiness blockers.
- Show the four MFI pillars as a coherent operating structure rather than an undifferentiated card grid.
- Keep prompt bodies hidden until the user deliberately requests them.
- Load all data through the existing validated services; the UI must not parse source JSON independently.
- Remain dependency-light, local-only, read-only, responsive, keyboard accessible, and testable.

## Non-goals

- No agent chat, runtime execution, orchestration, model calls, embeddings, or worker connection.
- No login, users, sessions, permissions engine, approval engine, or database.
- No evidence submission, status change, activation action, editing, saving, or file upload.
- No Cloudflare project, deployment configuration, public hostname, remote access, or analytics.
- No definition packages for the remaining six registered agent identities.
- No attempt to simulate features that do not exist.

## Anti-goals

The dashboard fails if it:

- implies that a complete definition is active or ready to perform work;
- duplicates or hard-codes canonical agent data in browser assets;
- exposes prompt bodies on initial page load or in the default agent response;
- binds directly to a non-loopback interface by default;
- writes to registry, manifest, prompt, evidence, status, or runtime files;
- introduces a framework or build chain that obscures the simple local review purpose;
- looks like a generic SaaS template instead of an MFI operating console;
- becomes a disguised first implementation of the production Control Plane.

## Approaches considered

### 1. Standard-library local server plus static browser application — selected

Use Python's standard-library HTTP server components for a loopback-only read API and static HTML, CSS, and JavaScript under `web/local-dashboard/`. The API adapts the already validated Python definition services into browser-safe view models.

This gives Joshua a live interface with no new runtime dependency or package manager. The static browser layer can later inform a production Control Plane without becoming its deployment architecture.

Tradeoff: this is intentionally a local review tool, not a scalable production web stack.

### 2. Full JavaScript application framework

A component framework and development server would make future UI growth easier, but would add Node tooling, dependencies, and a deployment-shaped architecture before the product navigation has been reviewed.

### 3. Production Control Plane foundation now

Starting authentication, a database, permissions, and Cloudflare services now would create a more durable platform, but would combine product design with security and deployment decisions. It works against the stated goal of building and judging the experience locally first.

## Technical boundary

Create a focused Python package under `app/local_dashboard/`:

- `models.py`: immutable JSON-safe dashboard view models.
- `service.py`: converts validated governed definitions and readiness reports into dashboard snapshots.
- `server.py`: loopback-only `ThreadingHTTPServer` request handling and static asset delivery.
- `cli.py`: `python -m app.local_dashboard.cli` entry point.

Create static assets under `web/local-dashboard/`:

- `index.html`: semantic application shell and initial loading state.
- `styles.css`: complete responsive visual system.
- `app.js`: navigation, rendering, filters, prompt reveal, and error states.

Runtime code continues to use only Python's standard library. Browser JavaScript uses no external CDN, font, analytics, or network dependency.

## Data flow

```text
registry.json + six manifests + seven prompt files
                    |
                    v
existing strict repositories and PromptLoader
                    |
                    v
AgentDefinitionService + readiness evaluator
                    |
                    v
LocalDashboardService (read-only view models)
                    |
                    v
loopback JSON endpoints -> static browser application
```

The browser never reads repository files directly. The dashboard service loads one all-or-nothing validated snapshot per request and returns no partial data when validation fails. Because the shared governance prompt is loaded for each agent by the existing service, the snapshot builder also requires every repeated prompt path to have the same SHA-256 fingerprint within that snapshot. If a local edit produces inconsistent fingerprints during a request, the request fails closed with refresh guidance; it does not retry or mix versions. The next browser refresh starts a new snapshot.

## Local server behavior

Default command:

```powershell
python -m app.local_dashboard.cli
```

Defaults:

- bind host: `127.0.0.1`;
- port: `8765`;
- repository root: resolved from the installed source location;
- optional `--repo-root` and `--port` for tests and local flexibility;
- optional `--open` to launch the default browser after the server is ready.

The server prints the exact local URL and a clear stop instruction. Binding to any host other than `127.0.0.1` or `localhost` is rejected in this milestone. Port values must be integers from 1 through 65535. Startup validation errors are concise and do not produce a traceback.

Only `GET` and `HEAD` are supported. Mutation methods return `405 Method Not Allowed`. Static paths are allowlisted and cannot traverse outside `web/local-dashboard/`. There is no directory listing. API and HTML responses use `Cache-Control: no-store`; assets may use short local cache headers only when fingerprints are later introduced.

## API surface

### `GET /api/dashboard`

Returns the complete non-prompt snapshot:

- generated timestamp;
- counts for definitions, lifecycle states, activation eligibility, tools, and grants;
- the four governed pillars;
- six ordered agent summaries;
- aggregate readiness blockers;
- explicit safety-boundary statements.

### `GET /api/agents/{agent_id}`

Returns one complete non-prompt agent detail view:

- canonical registry metadata;
- responsibilities and boundaries;
- input and output contracts;
- capabilities, systems, and data classifications;
- routing request;
- approval requirements;
- audit events;
- failure and escalation policies;
- prompt source paths and SHA-256 fingerprints;
- definition completeness, activation eligibility, and ordered blockers.

Prompt body text is absent from this response.

### `GET /api/agents/{agent_id}/prompt`

Returns composed prompt text and source provenance only after the browser's explicit “Reveal prompt text” action calls this endpoint. Unknown IDs return `404`. The initial page and ordinary agent-detail request never call this endpoint.

### `GET /api/health`

Returns a minimal local status and snapshot validation result without revealing prompt or agent details.

## Information architecture

The dashboard is a single-page review application with four navigable views.

### Overview

The opening view answers three questions immediately:

1. What exists?
2. What is safe to review?
3. What is still blocked?

It shows a horizontal governance ribbon with `6 definitions complete`, `0 active`, `0 tools`, and `0 authority grants`. Beneath it, a four-pillar field places the pillar leads in their operating areas while Orchestrator and QA Auditor occupy an enterprise coordination rail.

### Agents

A compact ledger lists all six agents. Rows—not identical cards—show name, canonical ID, accountable owner, role type, definition status, lifecycle, and activation state. Filters allow `All`, `Coordination`, `Assurance`, and `Pillar leads`, plus text search.

Selecting a row opens the agent detail view without a page reload.

### Agent detail

The detail view uses a two-column review layout:

- main column: purpose, responsibilities, inputs/outputs, capabilities, and boundaries;
- context column: lifecycle, owner, routing, data classes, approvals, audit obligations, prompt fingerprints, and blockers.

Prompt text remains behind a deliberate reveal control with a statement that viewing a prompt does not run the agent. Closing the viewer removes the prompt text from the visible document.

### Readiness

The readiness view groups blockers by policy sequence: lifecycle, runtime, runtime tests, audit implementation, acceptance criteria, and accountable-human acceptance. It explains why `COMPLETE` and `BLOCKED` can both be true.

## Visual direction

### Concept: governed operations folio

The interface should feel like an investment operating folio crossed with a systems control board: composed, legible, evidence-oriented, and quietly technical. It should not look like a consumer chat product, a crypto terminal, or a generic rounded-card admin template.

The memorable element is the governance ribbon—a continuous status band that keeps the system's actual safety state visible across every view. Everything else remains restrained.

### Color tokens

- `folio-paper` — `#F3F5F2`: main light field with a slight green cast.
- `charter-navy` — `#183047`: navigation and primary text.
- `blueprint` — `#2E668F`: links, selected rows, and structural highlights.
- `brass` — `#B8873E`: accountable-human and review emphasis.
- `safe-teal` — `#39776E`: definition-complete state.
- `hold-amber` — `#C66B2B`: planned/blocked state and material caution.

White is used selectively for review surfaces. Red is reserved for actual load failures, not ordinary blocked readiness.

### Typography

- Display and section titles: `Cambria`, with Georgia as fallback, using generous line height and sentence case.
- Navigation, status, tables, and body: `Bahnschrift`, with Segoe UI and system sans-serif fallbacks.
- Canonical IDs and digests use the UI sans face with tabular figures rather than a decorative monospace treatment.

No remote font loading is allowed.

### Layout

Desktop uses a narrow fixed navigation rail and a broad content canvas aligned to a twelve-column grid. Detail pages reserve roughly two-thirds for role content and one-third for governance context. Text is left aligned; numeric state summaries use tabular alignment.

```text
┌──────────────┬───────────────────────────────────────────────────────┐
│ MFI Hub      │ Governance ribbon: 6 complete | 0 active | 0 grants │
│              ├───────────────────────────────────────────────────────┤
│ Overview     │ Page title                               Local review │
│ Agents       │                                                       │
│ Readiness    │ Enterprise rail: Orchestrator | QA Auditor           │
│              │                                                       │
│ local only   │ ┌────────────┬────────────┬────────────┬────────────┐ │
│              │ │Infrastructure│Technology │Investments │Incubation  │ │
│              │ │ lead       │ lead       │ lead       │ lead       │ │
│              │ └────────────┴────────────┴────────────┴────────────┘ │
└──────────────┴───────────────────────────────────────────────────────┘
```

Mobile collapses navigation into a compact top bar, turns the governance ribbon into a horizontally scrollable status line, and stacks detail context after the main content. No essential information depends on hover.

### Interaction and motion

- One brief page-load reveal may bring the governance ribbon and primary view into focus.
- Agent selection, filters, prompt reveal, and view changes use direct state changes with restrained transitions.
- `prefers-reduced-motion` disables nonessential motion.
- Keyboard focus is always visible.
- Prompt reveal returns focus to its trigger when closed.

## Browser behavior

- Use semantic landmarks, headings, buttons, tables/lists, and dialog behavior.
- Render all API strings through `textContent`; never insert repository content with `innerHTML`.
- Keep URL hash state for `#overview`, `#agents`, `#agent/<id>`, and `#readiness` so refresh and browser navigation are predictable.
- Show loading, validation-error, network-error, unknown-agent, and empty-filter states with specific recovery guidance.
- Preserve the last selected filter and search only in memory for the current browser session; do not use persistent browser storage.

## Security and governance invariants

- The server is loopback-only and read-only.
- The dashboard has no activation, approval, edit, save, execute, or send controls.
- Prompt bodies are absent from initial HTML and default API responses.
- Every visible agent identity comes from the canonical registry join.
- Every lifecycle and readiness state comes from the validated domain services.
- Tools and grants are displayed as counts and exact validated values; the UI cannot add them.
- Error messages escape control characters and never expose a traceback to the browser.
- All source files must remain byte-for-byte and modification-time unchanged across dashboard requests.

## Error handling

- Startup fails closed if the repository root, static asset root, registry, manifests, or prompts are invalid.
- API validation failures return a stable JSON error object with HTTP `422` and one escaped line per finding.
- Unknown routes and agent IDs return `404`.
- Unsupported methods return `405` with an `Allow` header.
- Static-path traversal, encoded traversal, drive-qualified paths, and unexpected assets return `404` without filesystem details.
- Programming errors are not converted into data errors in the service layer; the HTTP boundary returns a generic local `500` response and logs the exception to the console for development.

## Testing and acceptance

Automated tests cover:

- immutable and JSON-safe dashboard view models;
- exact six-agent snapshot counts and canonical ordering;
- correct separation of completeness, lifecycle, and eligibility;
- all detail fields sourced from governed definitions;
- rejection of inconsistent fingerprints for a repeated prompt path during one snapshot;
- prompt body absent from dashboard and agent-detail payloads;
- prompt body present only in the explicit prompt endpoint;
- unknown agent, invalid source data, and atomic failure behavior;
- loopback host and port validation;
- static allowlist, traversal rejection, content types, and no directory listing;
- `GET`, `HEAD`, unsupported methods, `404`, `405`, `422`, and generic `500` behavior;
- commands working from outside the repository directory;
- browser assets containing no external network dependencies;
- source registry, manifest, and prompt bytes and modification times unchanged after requests.

Manual visual verification covers desktop and mobile widths, keyboard navigation, focus management, reduced motion, loading/error/empty states, long blocker lists, and prompt reveal/close behavior. Screenshots are reviewed before the local checkpoint is presented.

Acceptance criteria:

1. `python -m app.local_dashboard.cli` serves a usable dashboard at `http://127.0.0.1:8765/`.
2. The overview shows six complete definitions, zero active agents, zero tools, zero grants, and six blocked agents.
3. All six agent detail views match canonical registry and validated manifest data.
4. Prompt text is not present until explicitly revealed.
5. No request mutates source files or lifecycle state.
6. The interface works at desktop and mobile widths with visible keyboard focus.
7. The complete unit suite passes and independent review has no unresolved Critical or Important findings.
8. Nothing is deployed or pushed without Joshua's separate choice.

## Documentation updates

- Update `web/README.md` to distinguish the implemented local review dashboard from the future hosted Control Plane.
- Update the repository `README.md` current status and local run instructions.
- Add `docs/operations/LOCAL_DASHBOARD.md` with start, stop, troubleshooting, and safety-boundary instructions.
- Update `docs/ROADMAP.md` and `HANDOFF.md` without claiming authentication, deployment, or agent runtime exists.

## Builder calls

The builder may choose private helper names, response serialization details, CSS class names, responsive breakpoints, and the exact wording of non-governance interface hints.

The builder may not add dependencies, broaden the server bind address, add mutation endpoints, expose prompts by default, duplicate canonical data in browser assets, add runtime/model behavior, or introduce deployment configuration.

## Delivery boundary

This project ends with a polished local browser dashboard and operating guide. It remains a review tool over validated repository assets. Production Control Plane architecture, authentication, persistent data, permissions, approvals, audit storage, remote hosting, and agent execution remain later projects.
