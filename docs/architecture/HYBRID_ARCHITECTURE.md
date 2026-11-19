# Hybrid Architecture

## Purpose

The MFI Business Hub separates coordination from execution so business control can be available through a secure web application while sensitive and compute-heavy work can remain on approved local machines.

## Plane responsibilities

| Plane | Owns | Does not own |
|---|---|---|
| Control Plane | Identity, authentication, permissions, approvals, tasks, registries, durable audit metadata, web UI | Direct local-model access or ungoverned execution |
| Compute Plane | Local inference, embeddings, document processing, private/local-only jobs, temporary execution artifacts | Global authority, user identity, or approval policy |
| Cloud AI Plane | Optional approved external reasoning and generation | MFI agent identity, organizational authority, or local-only data |

## Secure job flow

1. A human or authorized agent creates a job in the Control Plane.
2. The permissions and approval layers determine whether the job may proceed.
3. The Model Gateway assigns an execution policy and eligible providers or nodes.
4. An approved worker or cloud adapter claims the job using scoped credentials.
5. Execution produces results, status, and auditable metadata.
6. The Control Plane records the outcome and requests any required human acceptance or follow-up.

Workers initiate outbound authenticated connections. The Control Plane never opens a public route to LM Studio or another local model server.

## Routing policies

Every job declares or inherits one of these policies:

- `LOCAL_ONLY`: run only on an approved local node; fail closed if none is eligible.
- `LOCAL_PREFERRED`: try eligible local capacity first, then use an explicitly approved cloud fallback.
- `CLOUD_ALLOWED`: use an approved local or cloud provider according to capability, availability, and cost policy.
- `HUMAN_ONLY`: do not submit the content to an AI provider; route to a human workflow.

Fallback is never automatic when it would cross a data-classification or approval boundary. A failed local-only job remains pending or failed rather than leaking to a cloud provider.

## Worker registry

The Control Plane maintains a registry entry for each node containing a stable node ID, owner, environment, status, capabilities, approved data classes, software version, last heartbeat, and revocation state. A node advertises capabilities; it does not grant itself authority.

Initial nodes may include the primary MFI desktop and later approved laptops or workstations. Hardware names and model inventory are configuration, not application code.

## Trust boundaries

- User-to-Control-Plane requests require authenticated user identity.
- Agent requests require registered agent identity and scoped authority.
- Worker connections require registered node identity and revocable credentials.
- Provider calls require an approved adapter, data policy, and secret stored outside the repository.
- Job results are untrusted input until validated and associated with their requester, executor, and approvals.

## Failure behavior

- Loss of a worker heartbeat prevents new job assignment without erasing the node record.
- Expired leases return jobs to an eligible queue only when retry policy permits.
- Provider failures do not bypass authority or data-routing rules.
- Duplicate delivery must be handled with idempotent job identifiers.
- Partial results remain labeled incomplete and are not treated as accepted business output.
- Revoked nodes and agents cannot claim new work.

## Deployment direction

The Control Plane is intended for Cloudflare-hosted web infrastructure. Compute nodes remain locally operated. Exact transport, queue, database, and Cloudflare product choices will be made in a later implementation decision record after the required behavior is tested.

