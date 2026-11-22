from __future__ import annotations

from contextlib import contextmanager
import http.client
import json
from pathlib import Path
import socket
import threading

from app.local_dashboard.server import create_server
from app.local_dashboard.service import LocalDashboardService


@contextmanager
def running_server(service, static_root: Path):
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    server = create_server(service, static_root, port=port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def request(port: int, method: str, path: str) -> tuple[int, bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    connection.request(method, path)
    response = connection.getresponse()
    body = response.read()
    connection.close()
    return response.status, body


def _snapshot(paths: set[Path]) -> dict[Path, tuple[bytes, int]]:
    return {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}


def _governed_files(repo_root: Path) -> set[Path]:
    return {
        path
        for root in (
            repo_root / "config/organization",
            repo_root / "config/agents/cohort-1",
            repo_root / "prompts/agents",
        )
        for path in root.rglob("*")
        if path.is_file()
    }


def test_all_dashboard_requests_leave_governed_sources_and_lifecycle_unchanged(
    repo_root: Path, definition_service
) -> None:
    definitions = definition_service.load_all()
    registry_path = repo_root / "config/organization/registry.json"
    tracked = {registry_path, *sorted((repo_root / "config/agents/cohort-1").glob("*.json"))}
    tracked.update(
        repo_root.joinpath(*source.path.split("/"))
        for definition in definitions
        for source in definition.prompt_sources
    )
    before = _snapshot(tracked)
    before_files = _governed_files(repo_root)
    lifecycle_before = {
        item["id"]: item["status"]
        for item in json.loads(registry_path.read_text(encoding="utf-8"))["agents"]
    }

    with running_server(
        LocalDashboardService(definition_service), repo_root / "web/local-dashboard"
    ) as port:
        status, dashboard_body = request(port, "GET", "/api/dashboard")
        assert status == 200
        dashboard = json.loads(dashboard_body)
        assert dashboard["counts"]["definitions"] == 6
        assert dashboard["counts"]["active"] == 0
        assert dashboard["counts"]["blocked"] == 6
        assert "composed_prompt" not in dashboard_body.decode("utf-8")

        assert request(port, "GET", "/api/health")[0] == 200
        assert request(port, "HEAD", "/api/dashboard") == (200, b"")
        for agent_id in (definition.registry_record.id for definition in definitions):
            detail_status, detail_body = request(port, "GET", f"/api/agents/{agent_id}")
            prompt_status, prompt_body = request(port, "GET", f"/api/agents/{agent_id}/prompt")
            assert detail_status == prompt_status == 200
            assert "composed_prompt" not in detail_body.decode("utf-8")
            assert json.loads(prompt_body)["composed_prompt"]

        assert request(port, "GET", "/missing")[0] == 404
        assert request(port, "GET", "/%2e%2e/registry.json")[0] == 404
        assert request(port, "POST", "/api/dashboard")[0] == 405

    lifecycle_after = {
        item["id"]: item["status"]
        for item in json.loads(registry_path.read_text(encoding="utf-8"))["agents"]
    }
    assert _snapshot(tracked) == before
    assert _governed_files(repo_root) == before_files
    assert lifecycle_after == lifecycle_before
