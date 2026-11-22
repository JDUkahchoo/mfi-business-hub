# web/ — Local Review Dashboard and Future Control Plane Boundary

`web/local-dashboard/` contains the implemented dependency-free, read-only local browser interface for inspecting the six validated Cohort 1 definitions. Start it through Python; opening `index.html` directly does not provide its validated API data.

```powershell
python -m app.local_dashboard.cli --open
```

This interface binds to loopback only and has no mutations, authentication, database, deployment, model calls, worker connection, or agent runtime. See the [operating guide](../docs/operations/LOCAL_DASHBOARD.md).

The future **Cloudflare-hosted MFI Control Plane** remains planned: users, authentication, permissions, approvals, central database, tasks, audit records, and registered worker connectivity are not implemented here. The production Control Plane will never talk to LM Studio directly; local compute will be reached only through registered worker nodes.

See the [Hybrid Architecture](../docs/architecture/HYBRID_ARCHITECTURE.md) for the approved boundary. Production framework and Cloudflare product choices remain future decisions.
