# worker/ - MFI Compute Node (planned)

This will become the **local MFI Compute Node**, responsible for:

- LM Studio and local models (Gemma, Nemotron)
- secure job processing
- node registration
- queued local jobs

**Status: not started.** No networking is implemented. LM Studio must never be exposed directly to the public internet; remote access, when built, goes through authenticated, outbound-initiated node connections.

See the [Compute Node Standard](../docs/architecture/NODE_STANDARD.md) and [Hybrid Architecture](../docs/architecture/HYBRID_ARCHITECTURE.md) for the approved worker contract.
