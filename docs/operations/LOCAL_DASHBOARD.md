# Local Agent Review Dashboard

## Purpose

The local dashboard is a read-only review surface for the six validated Cohort 1 agent definitions. It shows canonical identity, ownership, responsibilities, contracts, routing requests, prompt provenance, and activation blockers. It does not run, activate, approve, edit, or deploy an agent.

## Start

From the repository root with Python available:

```powershell
python -m app.local_dashboard.cli
```

Open `http://127.0.0.1:8765/`. The server binds only to loopback, so another computer cannot connect to it.

Optional arguments:

```powershell
python -m app.local_dashboard.cli --open
python -m app.local_dashboard.cli --port 9123
python -m app.local_dashboard.cli --repo-root D:\path\to\mfi-business-hub
python -m app.local_dashboard.cli --host localhost
```

Only `127.0.0.1` and `localhost` are accepted. Ports must be integers from 1 through 65535.

## Stop

Return to the terminal that started the dashboard and press `Ctrl+C`. The server prints `Dashboard stopped.` and releases the port.

## Prompt privacy

Prompt bodies are absent from the opening page, dashboard API, and ordinary agent-detail API. The browser requests composed prompt text only after **Reveal prompt text** is selected. Closing the viewer removes that text from the visible document. Revealing a prompt does not call a model or run an agent.

## Troubleshooting

- **Site cannot be reached:** confirm the terminal is still running and use the exact URL it printed.
- **Port already in use:** stop the other local process or start with another port, such as `--port 9123`.
- **Validation stopped safely:** inspect the listed registry, manifest, or prompt finding. The dashboard returns no partial snapshot when governed data is invalid.
- **Unknown agent:** return to **Agents** and select a canonical ledger row.
- **Browser did not open:** omit `--open` and paste the printed loopback URL into a browser manually.

## Safety boundary

This milestone has no login, users, database, permissions engine, approval engine, audit store, model gateway, worker connection, agent runtime, editing, evidence submission, activation control, public hostname, analytics, or deployment configuration. Source registry, manifest, prompt, and lifecycle files remain unchanged by dashboard requests.

## Deferred improvements

These reviewed follow-ups do not block local use or the Projects and Ventures Workspace milestone:

- **DASH-001 — Malformed URL response:** map invalid percent-encoding to the stable JSON `404` response instead of the generic local `500` boundary.
- **DASH-002 — Complete method rejection:** return the documented JSON `405` and `Allow` header for every unsupported HTTP method, not only `POST`, `PUT`, `PATCH`, and `DELETE`.
- **DASH-003 — Visible loading feedback:** show prompt-load failures beside the reveal control and use a neutral detail-loading state rather than an error-styled placeholder.
- **DASH-004 — Status-label contrast:** darken small amber status text to meet the 4.5:1 normal-text contrast target while preserving amber borders and emphasis.

