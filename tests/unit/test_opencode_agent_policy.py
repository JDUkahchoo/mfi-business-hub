from scripts.validate_opencode_agents import resolve_effect, validate_agents


SAFE_ANALYST = {
    "id": "local-analyst",
    "model": {"providerID": "lmstudio", "id": "google/gemma-4-e2b"},
    "permissions": [
        {"action": "*", "resource": "*", "effect": "allow"},
        {"action": "*", "resource": "*", "effect": "deny"},
        {"action": "read", "resource": "docs/**", "effect": "allow"},
    ],
}

SAFE_WORKER = {
    "id": "execution-worker",
    "model": {
        "providerID": "lmstudio",
        "id": "nvidia-nemotron-3.5-lightning-30b-a3b",
    },
    "permissions": [
        {"action": "*", "resource": "*", "effect": "allow"},
        {"action": "*", "resource": "*", "effect": "deny"},
        {"action": "read", "resource": "app/**", "effect": "allow"},
        {
            "action": "edit",
            "resource": "data/development/worker-output/**",
            "effect": "allow",
        },
    ],
}


def test_permission_resolution_uses_last_matching_rule():
    permissions = SAFE_ANALYST["permissions"]

    assert resolve_effect(permissions, "read", "docs/README.md") == "allow"
    assert resolve_effect(permissions, "read", ".env") == "deny"
    assert resolve_effect(permissions, "edit", "docs/README.md") == "deny"
    assert resolve_effect(permissions, "subagent", "general") == "deny"


def test_safe_effective_agent_policies_are_accepted():
    assert validate_agents([SAFE_ANALYST, SAFE_WORKER]) == []


def test_default_allow_and_host_shell_access_are_rejected():
    unsafe_worker = {
        **SAFE_WORKER,
        "permissions": [
            {"action": "*", "resource": "*", "effect": "allow"},
            {"action": "shell", "resource": "*", "effect": "ask"},
            {"action": "shell", "resource": "python -m pytest *", "effect": "allow"},
        ],
    }

    findings = validate_agents([SAFE_ANALYST, unsafe_worker])

    assert "execution-worker: shell must be denied" in findings
    assert "execution-worker: governance edits must be denied" in findings
