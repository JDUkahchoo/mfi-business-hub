from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "README.md", "AGENTS.md", "HANDOFF.md", "requirements.txt", ".env.example", ".gitignore",
    "docs/README.md", "docs/ROADMAP.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/architecture/HYBRID_ARCHITECTURE.md",
    "docs/architecture/NODE_STANDARD.md",
    "docs/governance/ORGANIZATION.md",
    "docs/governance/AGENT_STANDARD.md",
    "docs/governance/AUTHORITY_MATRIX.md",
    "docs/governance/AGENT_REGISTRY.md",
    "docs/operations/AI_DEVELOPMENT_ROLES.md",
    "docs/operations/BRANCH_WORKFLOW.md",
    "docs/decisions/0001-multi-model-development-operating-model.md",
    "web/README.md", "worker/README.md", ".opencode/README.md",
    ".opencode/agents/local-analyst.md",
    ".opencode/agents/execution-worker.md",
    "data/development/worker-output/.gitkeep",
    "data/knowledge/analyst-input/.gitkeep",
]

REQUIRED_DIRECTORIES = [
    "app/core/model_router",
    "app/integrations/lm_studio",
    "config",
    "data/development/worker-output",
    "data/knowledge",
    "data/knowledge/analyst-input",
    "docs/decisions",
    "docs/operations",
    "docs/superpowers/plans",
    "docs/superpowers/specs",
    "prompts/pillar_leads",
    "scripts",
]

LEGACY_DOCUMENT_PATHS = [
    "ARCHITECTURE.md",
    "docs/ORGANIZATION.md",
    "docs/AGENT_STANDARD.md",
    "docs/AUTHORITY_MATRIX.md",
    "docs/AGENT_REGISTRY.md",
    ".opencode/agents/README.md",
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


def test_required_files_exist_as_files():
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).is_file()]
    assert not missing, missing


def test_required_directories_exist_as_directories():
    missing = [p for p in REQUIRED_DIRECTORIES if not (ROOT / p).is_dir()]
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
