"""Validate effective OpenCode permissions for MFI local development roles."""

from __future__ import annotations

import fnmatch
import json
import sys
from typing import Any


EXPECTED_MODELS = {
    "local-analyst": ("lmstudio", "google/gemma-4-e2b"),
    "execution-worker": (
        "lmstudio",
        "nvidia-nemotron-3.5-lightning-30b-a3b",
    ),
}


def resolve_effect(
    permissions: list[dict[str, str]], action: str, resource: str
) -> str | None:
    """Return the last matching OpenCode permission effect."""

    effect = None
    for rule in permissions:
        if fnmatch.fnmatchcase(action, rule["action"]) and fnmatch.fnmatchcase(
            resource, rule["resource"]
        ):
            effect = rule["effect"]
    return effect


def _expect(
    findings: list[str],
    agent_id: str,
    permissions: list[dict[str, str]],
    action: str,
    resource: str,
    expected: str,
    label: str,
) -> None:
    actual = resolve_effect(permissions, action, resource)
    if actual != expected:
        expected_word = {"allow": "allowed", "deny": "denied"}.get(expected, expected)
        findings.append(f"{agent_id}: {label} must be {expected_word}")


def validate_agents(agents: list[dict[str, Any]]) -> list[str]:
    """Return security-policy findings for the required effective agents."""

    findings: list[str] = []
    by_id = {agent.get("id"): agent for agent in agents}

    for agent_id, (provider_id, model_id) in EXPECTED_MODELS.items():
        agent = by_id.get(agent_id)
        if agent is None:
            findings.append(f"{agent_id}: agent is missing")
            continue

        model = agent.get("model") or {}
        if (model.get("providerID"), model.get("id")) != (provider_id, model_id):
            findings.append(f"{agent_id}: model assignment is not the verified local ID")

        permissions = agent.get("permissions") or []
        if not any(
            rule == {"action": "*", "resource": "*", "effect": "deny"}
            for rule in permissions
        ):
            findings.append(f"{agent_id}: deny-all baseline is missing")

        for action, resource, label in (
            ("shell", "python -m pytest tests/unit -q", "shell"),
            ("subagent", "general", "delegation"),
            ("external_directory", "D:/outside/file.txt", "external access"),
            ("webfetch", "https://example.com", "network access"),
            ("mcp__github__search", "*", "connector access"),
            ("read", ".env", "environment-secret reads"),
            ("read", "secrets/token.txt", "credential-file reads"),
        ):
            _expect(findings, agent_id, permissions, action, resource, "deny", label)

    analyst = by_id.get("local-analyst")
    if analyst:
        permissions = analyst.get("permissions") or []
        _expect(
            findings,
            "local-analyst",
            permissions,
            "read",
            "docs/README.md",
            "allow",
            "approved documentation reads",
        )
        _expect(
            findings,
            "local-analyst",
            permissions,
            "edit",
            "docs/README.md",
            "deny",
            "edits",
        )

    worker = by_id.get("execution-worker")
    if worker:
        permissions = worker.get("permissions") or []
        _expect(
            findings,
            "execution-worker",
            permissions,
            "read",
            "app/core/example.py",
            "allow",
            "approved source reads",
        )
        _expect(
            findings,
            "execution-worker",
            permissions,
            "edit",
            "data/development/worker-output/task.patch",
            "allow",
            "review-output edits",
        )
        _expect(
            findings,
            "execution-worker",
            permissions,
            "edit",
            "app/core/example.py",
            "deny",
            "source edits",
        )
        _expect(
            findings,
            "execution-worker",
            permissions,
            "edit",
            "docs/governance/AUTHORITY_MATRIX.md",
            "deny",
            "governance edits",
        )

    return findings


def main() -> int:
    agents = json.load(sys.stdin)
    findings = validate_agents(agents)
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}", file=sys.stderr)
        return 1
    print("OpenCode local-agent policy is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
