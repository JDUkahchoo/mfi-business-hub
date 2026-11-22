from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sys
import traceback
from urllib.parse import unquote, urlsplit

from app.agents.definitions.errors import AgentDefinitionError
from app.organization import RegistryError

from .service import InconsistentSnapshotError, LocalDashboardService, UnknownAgentError


_STATIC_ROUTES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
_DETAIL_ROUTE = re.compile(r"^/api/agents/([^/]+)$")
_PROMPT_ROUTE = re.compile(r"^/api/agents/([^/]+)/prompt$")


def validate_host(host: str) -> str:
    if type(host) is not str or host not in ("127.0.0.1", "localhost"):
        raise ValueError("host must be 127.0.0.1 or localhost")
    return host


def validate_port(port: int) -> int:
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("port must be an integer from 1 through 65535")
    return port


def _safe_text(value: object) -> str:
    text = str(value)
    replacements = {"\n": "\\n", "\r": "\\r", "\t": "\\t"}
    return "".join(
        character if character.isprintable() else replacements.get(character, f"\\x{ord(character):02x}")
        for character in text
    )


def make_handler(
    service: LocalDashboardService, static_root: Path
) -> type[BaseHTTPRequestHandler]:
    root = static_root.resolve()

    class DashboardRequestHandler(BaseHTTPRequestHandler):
        server_version = "MFILocalDashboard/1"
        sys_version = ""

        def do_GET(self) -> None:
            self._dispatch(include_body=True)

        def do_HEAD(self) -> None:
            self._dispatch(include_body=False)

        def do_POST(self) -> None:
            self._method_not_allowed()

        def do_PUT(self) -> None:
            self._method_not_allowed()

        def do_PATCH(self) -> None:
            self._method_not_allowed()

        def do_DELETE(self) -> None:
            self._method_not_allowed()

        def _method_not_allowed(self) -> None:
            self._send_json(
                405,
                {"error": {"code": "method_not_allowed", "message": "Only GET and HEAD are supported."}},
                include_body=self.command != "HEAD",
                extra_headers={"Allow": "GET, HEAD"},
            )

        def _dispatch(self, include_body: bool) -> None:
            try:
                raw_path = urlsplit(self.path).path
                path = unquote(raw_path, errors="strict")
                if path == "/api/dashboard":
                    self._send_json(200, service.dashboard().to_payload(), include_body)
                    return
                if path == "/api/health":
                    self._send_json(200, service.health().to_payload(), include_body)
                    return
                prompt_match = _PROMPT_ROUTE.fullmatch(path)
                if prompt_match:
                    agent_id = prompt_match.group(1)
                    self._send_json(200, service.prompt(agent_id).to_payload(), include_body)
                    return
                detail_match = _DETAIL_ROUTE.fullmatch(path)
                if detail_match:
                    agent_id = detail_match.group(1)
                    self._send_json(200, service.agent_detail(agent_id).to_payload(), include_body)
                    return
                static = _STATIC_ROUTES.get(path)
                if static is not None:
                    self._send_static(*static, include_body=include_body)
                    return
                self._not_found(include_body, f"route {_safe_text(path)!r} was not found")
            except UnknownAgentError as error:
                self._not_found(include_body, _safe_text(error))
            except (AgentDefinitionError, RegistryError, InconsistentSnapshotError) as error:
                findings = getattr(error, "findings", None)
                lines = [_safe_text(item) for item in findings] if findings is not None else [_safe_text(error)]
                self._send_json(
                    422,
                    {"error": {"code": "validation_failed", "message": "The governed snapshot is invalid. Correct the listed source data and refresh.", "findings": lines}},
                    include_body,
                )
            except Exception:
                traceback.print_exc(file=sys.stderr)
                self._send_json(
                    500,
                    {"error": {"code": "internal_error", "message": "The local dashboard could not complete this request."}},
                    include_body,
                )

        def _not_found(self, include_body: bool, message: str) -> None:
            self._send_json(
                404,
                {"error": {"code": "not_found", "message": message}},
                include_body,
            )

        def _send_static(self, filename: str, content_type: str, include_body: bool) -> None:
            candidate = root / filename
            try:
                body = candidate.read_bytes()
            except (FileNotFoundError, IsADirectoryError):
                self._not_found(include_body, "static asset was not found")
                return
            self._send(200, body, content_type, include_body)

        def _send_json(
            self,
            status: int,
            payload: dict[str, object],
            include_body: bool,
            extra_headers: dict[str, str] | None = None,
        ) -> None:
            body = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
            self._send(status, body, "application/json; charset=utf-8", include_body, extra_headers)

        def _send(
            self,
            status: int,
            body: bytes,
            content_type: str,
            include_body: bool,
            extra_headers: dict[str, str] | None = None,
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            for key, value in (extra_headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            if include_body:
                self.wfile.write(body)

        def log_message(self, _format: str, *_args: object) -> None:
            return

    return DashboardRequestHandler


def create_server(
    service: LocalDashboardService,
    static_root: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> ThreadingHTTPServer:
    validated_host = validate_host(host)
    validated_port = validate_port(port)
    root = static_root.resolve()
    if not root.is_dir():
        raise ValueError("static asset root must be an existing directory")
    server = ThreadingHTTPServer(
        (validated_host, validated_port), make_handler(service, root)
    )
    server.daemon_threads = True
    return server
