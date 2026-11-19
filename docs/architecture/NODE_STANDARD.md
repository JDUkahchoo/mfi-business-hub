# MFI Compute Node Standard

## Purpose

This standard defines the minimum contract for a machine that participates in the MFI Compute Plane. It is transport-neutral so the project can choose an implementation later without weakening identity, security, or audit requirements.

## Node identity

Each node has one stable, unique ID and a registry record owned by the Control Plane. The record includes:

- display name and human owner;
- environment and operating system;
- enabled status and revocation state;
- supported job types and model capabilities;
- approved data classifications;
- worker software version;
- last successful heartbeat and health summary.

Reinstalling a worker does not silently inherit a previous node's credentials. Credential replacement requires a new enrollment or an explicitly approved rotation.

## Enrollment

Enrollment requires a one-time, short-lived invitation created by an authorized human. The node proves possession of its generated credential, registers its metadata, and receives only the scopes required for heartbeat, compatible job claims, result submission, and approved configuration retrieval.

Node credentials must be revocable and stored using the operating system's protected secret storage when available. They are never committed to this repository or written to ordinary logs.

## Capabilities

A node advertises factual capabilities such as available providers, installed local models, embedding support, document-processing support, memory class, and concurrency limits. The Control Plane intersects those claims with administrator-approved policy before assigning work.

Capability advertisement is not permission. A node with a model installed cannot accept a data class or business action that its registry policy forbids.

## Connectivity and heartbeats

- Connections are outbound-initiated and authenticated.
- LM Studio and other local model servers bind only to trusted local interfaces and are not exposed publicly.
- Heartbeats report health and capabilities without including prompt content, secrets, or private job data.
- A missed-heartbeat threshold changes the node to unavailable for new work.
- Clock skew and intermittent connectivity must not expand a node's access.

## Job handling

1. Claim only jobs matching the node's approved capabilities and data classes.
2. Use a unique job ID and bounded lease so retries can be made safely.
3. Validate the job envelope before processing any content.
4. Keep local-only inputs and artifacts on approved storage.
5. Report structured status, sanitized diagnostics, and result metadata.
6. Delete temporary artifacts according to the job's retention policy.
7. Never choose a cloud fallback independently; routing changes come from the Control Plane.

Workers must treat jobs as potentially duplicated. Side-effecting jobs require an idempotency key and any approval required by the [Authority Matrix](../governance/AUTHORITY_MATRIX.md).

## Logging and audit

Node logs may include timestamps, node ID, job ID, software version, state transitions, durations, provider/model identifiers, and sanitized error codes. API keys, bearer tokens, node credentials, and other secrets must never appear in logs at any level. Full prompts, protected documents, and unrestricted model output are excluded unless a separately approved data-retention policy explicitly requires a narrowly scoped record.

Material job events are returned to the Control Plane for durable audit. Local logs support diagnosis but are not the sole audit record.

## Updates and compatibility

Workers report a semantic software version and supported protocol version. The Control Plane may block obsolete or vulnerable versions. Updates must preserve local configuration and require a health check before the node returns to service.

## Suspension and revocation

Authorized humans can suspend or revoke a node. Suspension prevents new claims while preserving investigation data. Revocation invalidates credentials and requires re-enrollment before the machine can participate again.

## Minimum acceptance checklist

A node is not production-ready until it can demonstrate authenticated enrollment, credential protection, heartbeat timeout, capability filtering, lease expiry, duplicate-job safety, sanitized logs, revocation, and fail-closed handling of `LOCAL_ONLY` work.

