# Inspecting Cohort 1 Agent Definitions

The MFI Business Hub includes six local, version-controlled Cohort 1 definition packages. These commands validate and display the packages without calling a model, running an agent, changing lifecycle state, granting authority, or writing to the source files.

Run commands from the repository root. They also work from another directory when the repository is available on Python's module path.

## Validate all definitions

```powershell
python -m app.agents.definitions.cli validate
```

The expected result is six valid definitions, 12 loaded prompt sources, and zero resolved authority grants.

## View the six-agent summary

```powershell
python -m app.agents.definitions.cli summary
```

Each row shows definition completeness, registry lifecycle status, and activation eligibility. `COMPLETE  PLANNED  BLOCKED` means the files are internally complete, but no runtime or activation authority exists.

## View aggregate readiness

```powershell
python -m app.agents.definitions.cli readiness
```

The initial result is six definition-complete agents, zero activation-eligible agents, and six blocked agents. Blockers are evidence requirements and safety gates; this command reports them but does not satisfy or remove them.

## Inspect one agent

```powershell
python -m app.agents.definitions.cli show mfi-orchestrator
```

The safe default shows canonical registry metadata, contracts, prompt paths and fingerprints, tools, grants, and readiness blockers. It does not print prompt bodies.

To inspect the version-controlled prompt text explicitly:

```powershell
python -m app.agents.definitions.cli show mfi-orchestrator --with-prompt
```

The revealed prompt includes a provenance banner for each source. This is a local inspection feature, not runtime prompt execution.

## Safety boundary

- All six registry records remain `PLANNED`.
- All manifests have empty tool and authority-grant lists.
- No runtime, model call, network action, approval decision, audit persistence, or external effect is implemented here.
- A `COMPLETE` definition is not an active agent.
- Only a future governed implementation with required tests, audit enforcement, accountable-human acceptance, and lifecycle approval can change activation eligibility.
