from __future__ import annotations

from contextlib import contextmanager
import http.client
import json
from pathlib import Path
import socket
import threading

import pytest

from app.agents.definitions.errors import DefinitionFinding, DefinitionValidationError
from app.local_dashboard.server import create_server, validate_host, validate_port
from app.local_dashboard.service import LocalDashboardService


@pytest.fixture
def static_root(tmp_path: Path) -> Path:
    root = tmp_path / "static"
    root.mkdir()
    (root / "index.html").write_text("<!doctype html><title>MFI Hub</title>", encoding="utf-8")
    (root / "styles.css").write_text("body { color: #183047; }", encoding="utf-8")
    (root / "app.js").write_text("document.title = 'MFI Hub';", encoding="utf-8")
    return root


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
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def request(port: int, method: str, path: str, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    connection.request(method, path, headers=headers or {})
    response = connection.getresponse()
    body = response.read()
    headers = {key.casefold(): value for key, value in response.getheaders()}
    connection.close()
    return response.status, headers, body


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost"])
def test_accepts_only_explicit_loopback_hosts(host: str) -> None:
    assert validate_host(host) == host


@pytest.mark.parametrize("host", ["", "0.0.0.0", "::1", "192.168.1.4", 7, None])
def test_rejects_every_other_bind_host(host) -> None:
    with pytest.raises(ValueError, match="127.0.0.1 or localhost"):
        validate_host(host)


@pytest.mark.parametrize("port", [1, 8765, 65535])
def test_accepts_valid_ports(port: int) -> None:
    assert validate_port(port) == port


@pytest.mark.parametrize("port", [True, False, 0, -1, 65536, "8765", None])
def test_rejects_invalid_ports(port) -> None:
    with pytest.raises(ValueError, match="integer from 1 through 65535"):
        validate_port(port)


def test_serves_all_read_routes_and_head_without_a_body(definition_service, static_root: Path) -> None:
    service = LocalDashboardService(definition_service)
    routes = {
        "/api/dashboard": "application/json; charset=utf-8",
        "/api/health": "application/json; charset=utf-8",
        "/api/agents/mfi-orchestrator": "application/json; charset=utf-8",
        "/api/agents/mfi-orchestrator/prompt": "application/json; charset=utf-8",
        "/": "text/html; charset=utf-8",
        "/index.html": "text/html; charset=utf-8",
        "/styles.css": "text/css; charset=utf-8",
        "/app.js": "text/javascript; charset=utf-8",
    }
    with running_server(service, static_root) as port:
        for path, content_type in routes.items():
            status, headers, body = request(port, "GET", path)
            assert status == 200, path
            assert headers["content-type"] == content_type
            assert int(headers["content-length"]) == len(body)
            assert body
            head_status, head_headers, head_body = request(port, "HEAD", path)
            assert head_status == 200, path
            assert head_headers["content-type"] == content_type
            assert int(head_headers["content-length"]) == len(body)
            assert head_body == b""


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_rejects_mutation_methods(method: str, definition_service, static_root: Path) -> None:
    with running_server(LocalDashboardService(definition_service), static_root) as port:
        status, headers, body = request(port, method, "/api/dashboard")
    assert status == 405
    assert headers["allow"] == "GET, HEAD"
    assert b"method_not_allowed" in body


def test_disables_caching_for_api_and_static_responses(definition_service, static_root: Path) -> None:
    with running_server(LocalDashboardService(definition_service), static_root) as port:
        for path in ("/api/dashboard", "/", "/styles.css"):
            assert request(port, "GET", path)[1]["cache-control"] == "no-store"


@pytest.mark.parametrize("path", [
    "/missing", "/assets/", "/../secret.txt", "/%2e%2e/secret.txt",
    "/%252e%252e/secret.txt", "/..%5csecret.txt", "/%5c%5cserver/share",
    "/C:%5cWindows%5cwin.ini", "/%00index.html", "/secret.txt?file=/index.html",
])
def test_rejects_unknown_and_traversal_paths_without_disclosure(
    path: str, definition_service, static_root: Path
) -> None:
    secret = static_root.parent / "secret.txt"
    secret.write_text("not-for-browser", encoding="utf-8")
    with running_server(LocalDashboardService(definition_service), static_root) as port:
        status, _, body = request(port, "GET", path)
    assert status == 404
    assert b"not-for-browser" not in body
    assert str(static_root).encode() not in body


def test_unknown_agent_returns_stable_escaped_404(definition_service, static_root: Path) -> None:
    with running_server(LocalDashboardService(definition_service), static_root) as port:
        status, _, body = request(port, "GET", "/api/agents/missing%0Aagent")
    assert status == 404
    assert b"not_found" in body
    assert b"Traceback" not in body
    assert b"\\n" in body
    assert b"\nagent" not in body


class ErrorService:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def __getattr__(self, _name):
        def fail(*_args):
            raise self.error
        return fail


def test_maps_validation_findings_to_atomic_422(static_root: Path) -> None:
    error = DefinitionValidationError((
        DefinitionFinding("manifest\npath", "bad\rvalue"),
        DefinitionFinding("prompt", "missing"),
    ))
    with running_server(ErrorService(error), static_root) as port:
        status, headers, body = request(port, "GET", "/api/dashboard")
    assert status == 422
    assert headers["content-type"] == "application/json; charset=utf-8"
    assert b'"code":"validation_failed"' in body
    assert b'"findings"' in body
    findings = json.loads(body)["error"]["findings"]
    assert findings[0] == "manifest\\npath: bad\\rvalue"
    assert b'"agents"' not in body


def test_maps_programming_errors_to_generic_500_and_logs_detail(static_root: Path, capsys) -> None:
    with running_server(ErrorService(RuntimeError("private boom")), static_root) as port:
        status, _, body = request(port, "GET", "/api/dashboard")
    captured = capsys.readouterr()
    assert status == 500
    assert b"internal_error" in body
    assert b"private boom" not in body
    assert "private boom" in captured.err


def test_rejects_non_loopback_http_authority(definition_service, static_root: Path) -> None:
    with running_server(LocalDashboardService(definition_service), static_root) as port:
        status, _, body = request(
            port, "GET", "/api/dashboard", {"Host": f"attacker.example:{port}"}
        )
    assert status == 421
    assert b"invalid_authority" in body
    assert b'"agents"' not in body


def test_server_startup_rejects_missing_or_escaping_allowlisted_asset(
    definition_service, static_root: Path
) -> None:
    (static_root / "app.js").unlink()
    with pytest.raises(ValueError, match="static asset"):
        create_server(LocalDashboardService(definition_service), static_root, port=8764)


def test_server_startup_rejects_allowlisted_symlink_escape(
    definition_service, static_root: Path, tmp_path: Path
) -> None:
    outside = tmp_path / "outside.js"
    outside.write_text("private", encoding="utf-8")
    asset = static_root / "app.js"
    asset.unlink()
    try:
        asset.symlink_to(outside)
    except OSError as error:
        pytest.skip(f"host does not permit symlink creation: {error}")
    with pytest.raises(ValueError, match="outside the static root"):
        create_server(LocalDashboardService(definition_service), static_root, port=8764)
