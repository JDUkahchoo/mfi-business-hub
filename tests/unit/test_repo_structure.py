from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "README.md", "AGENTS.md", "requirements.txt", ".env.example", ".gitignore",
    "docs/README.md", "docs/ROADMAP.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/architecture/HYBRID_ARCHITECTURE.md",
    "docs/architecture/NODE_STANDARD.md",
    "docs/governance/ORGANIZATION.md",
    "docs/governance/AGENT_STANDARD.md",
    "docs/governance/AUTHORITY_MATRIX.md",
    "docs/governance/AGENT_REGISTRY.md",
    "app/core/model_router", "app/integrations/lm_studio", "prompts/pillar_leads",
    "data/knowledge", "web/README.md", "worker/README.md", ".opencode/agents/README.md",
]

LEGACY_DOCUMENT_PATHS = [
    "ARCHITECTURE.md",
    "docs/ORGANIZATION.md",
    "docs/AGENT_STANDARD.md",
    "docs/AUTHORITY_MATRIX.md",
    "docs/AGENT_REGISTRY.md",
]


def _env_keys_with_values(text):
    offenders = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if "KEY" in key and value.strip():
            offenders.append(key.strip())
    return offenders


def test_required_paths_exist():
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    assert not missing, missing


def test_legacy_document_paths_are_removed():
    remaining = [p for p in LEGACY_DOCUMENT_PATHS if (ROOT / p).exists()]
    assert not remaining, remaining


def test_env_secret_check_reports_only_variable_names():
    sample = "OPENAI_API_KEY=synthetic-secret-value\nMFI_ENV=development\n"

    result = _env_keys_with_values(sample)

    assert result == ["OPENAI_API_KEY"]
    assert "synthetic-secret-value" not in repr(result)


def test_env_example_has_no_secrets():
    offenders = _env_keys_with_values((ROOT / ".env.example").read_text())
    assert not offenders, f"Secret values found for variables: {', '.join(offenders)}"


def test_gitignore_excludes_env():
    assert ".env" in (ROOT / ".gitignore").read_text().splitlines()
