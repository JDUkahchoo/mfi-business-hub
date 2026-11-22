from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys
import webbrowser

from app.agents.definitions.errors import AgentDefinitionError
from app.agents.definitions.json_repository import JsonAgentManifestRepository
from app.agents.definitions.prompt_loader import PromptLoader
from app.agents.definitions.service import AgentDefinitionService
from app.organization import JsonOrganizationRepository, RegistryError

from .server import create_server, validate_host, validate_port
from .service import InconsistentSnapshotError, LocalDashboardService, governed_source_versions


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _build_service(repo_root: Path) -> LocalDashboardService:
    return LocalDashboardService(
        AgentDefinitionService(
            JsonOrganizationRepository(repo_root / "config/organization/registry.json"),
            JsonAgentManifestRepository(repo_root / "config/agents/cohort-1"),
            PromptLoader(repo_root),
        ),
        source_versions=lambda: governed_source_versions(repo_root),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the read-only MFI agent review dashboard.",
        allow_abbrev=False,
    )
    parser.add_argument("--repo-root", type=Path, default=_default_repo_root())
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", dest="open_browser")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    server = None
    try:
        host = validate_host(arguments.host)
        port = validate_port(arguments.port)
        repo_root = arguments.repo_root.resolve()
        static_root = repo_root / "web/local-dashboard"
        if not static_root.is_dir():
            raise ValueError(f"static asset root does not exist: {static_root}")
        service = _build_service(repo_root)
        service.health()
        server = create_server(service, static_root, host=host, port=port)
    except (ValueError, OSError, AgentDefinitionError, RegistryError, InconsistentSnapshotError) as error:
        print(f"Error: {error}", file=sys.stderr)
        if server is not None:
            server.server_close()
        return 2

    url = f"http://{host}:{port}/"
    print(f"Dashboard: {url}")
    print("Stop: Ctrl+C")
    if arguments.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Dashboard stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
