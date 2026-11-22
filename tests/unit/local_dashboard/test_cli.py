from __future__ import annotations

from pathlib import Path

import pytest

from app.local_dashboard import cli


def test_default_repo_root_is_source_relative_not_cwd(tmp_path: Path, monkeypatch) -> None:
    expected = Path(cli.__file__).resolve().parents[2]
    monkeypatch.chdir(tmp_path)
    assert cli._default_repo_root() == expected


def test_parser_exposes_exact_local_options(tmp_path: Path) -> None:
    defaults = cli._parser().parse_args([])
    assert defaults.host == "127.0.0.1"
    assert defaults.port == 8765
    assert defaults.repo_root == cli._default_repo_root()
    assert defaults.open_browser is False

    custom = cli._parser().parse_args([
        "--repo-root", str(tmp_path), "--host", "localhost", "--port", "9123", "--open"
    ])
    assert custom.repo_root == tmp_path
    assert custom.host == "localhost"
    assert custom.port == 9123
    assert custom.open_browser is True


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (["--host", "0.0.0.0"], "host must be 127.0.0.1 or localhost"),
        (["--port", "0"], "port must be an integer from 1 through 65535"),
        (["--port", "65536"], "port must be an integer from 1 through 65535"),
    ],
)
def test_invalid_bind_arguments_fail_concisely(arguments, message, capsys) -> None:
    assert cli.main(arguments) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.strip() == f"Error: {message}"
    assert "Traceback" not in captured.err


def test_invalid_repository_fails_before_server_start(tmp_path: Path, monkeypatch, capsys) -> None:
    started = False

    def forbidden_server(*_args, **_kwargs):
        nonlocal started
        started = True
        raise AssertionError("server must not start")

    monkeypatch.setattr(cli, "create_server", forbidden_server)
    assert cli.main(["--repo-root", str(tmp_path)]) == 2
    assert started is False
    assert "web/local-dashboard" in capsys.readouterr().err.replace("\\", "/")


class FakeHealth:
    def to_payload(self):
        return {"status": "ok", "snapshot_valid": True, "generated_at": "fixed"}


class FakeService:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    def health(self):
        self.events.append("health")
        return FakeHealth()


class FakeServer:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.closed = False

    def serve_forever(self):
        self.events.append("serve")
        raise KeyboardInterrupt

    def server_close(self):
        self.events.append("close")
        self.closed = True


def test_starts_prints_opens_after_ready_and_closes_cleanly(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    static = tmp_path / "web/local-dashboard"
    static.mkdir(parents=True)
    events: list[str] = []
    server = FakeServer(events)

    monkeypatch.setattr(cli, "_build_service", lambda _root: FakeService(events))

    def fake_create(_service, _static, host, port):
        events.append(f"create:{host}:{port}")
        return server

    monkeypatch.setattr(cli, "create_server", fake_create)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: events.append(f"open:{url}"))

    assert cli.main(["--repo-root", str(tmp_path), "--open"]) == 0
    assert events == [
        "health", "create:127.0.0.1:8765", "open:http://127.0.0.1:8765/",
        "serve", "close",
    ]
    assert server.closed is True
    output = capsys.readouterr().out
    assert "Dashboard: http://127.0.0.1:8765/" in output
    assert "Stop: Ctrl+C" in output
    assert "Dashboard stopped." in output


def test_open_is_not_called_without_flag(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "web/local-dashboard").mkdir(parents=True)
    events: list[str] = []
    monkeypatch.setattr(cli, "_build_service", lambda _root: FakeService(events))
    monkeypatch.setattr(cli, "create_server", lambda *_args, **_kwargs: FakeServer(events))
    monkeypatch.setattr(cli.webbrowser, "open", lambda _url: events.append("open"))
    assert cli.main(["--repo-root", str(tmp_path)]) == 0
    assert "open" not in events
