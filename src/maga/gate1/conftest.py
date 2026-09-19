"""The Gate 1 harness: the fixtures that generator.CONSTRAINTS promises to the acceptance tests."""

from collections.abc import Callable, Iterator
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
from typing import cast

import pytest

PERMITTED = [5173, 5174]
HARNESS = Path(__file__).parent


class Backend(HTTPServer):
    """The backend stub. A test can change `allowed` to make the backend reject an Origin."""

    origins: list[str | None]
    allowed: list[str]


class _Health(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # the name that BaseHTTPRequestHandler calls
        stub = cast("Backend", self.server)
        origin = self.headers.get("Origin")
        stub.origins.append(origin)
        self.send_response(HTTPStatus.OK if origin in stub.allowed else HTTPStatus.FORBIDDEN)
        self.end_headers()


@pytest.fixture
def repo(tmp_path: Path) -> Iterator[Path]:
    (tmp_path / "packages/config").mkdir(parents=True)
    (tmp_path / "packages/config/ports.json").write_text(json.dumps({"frontend_ports": PERMITTED}))
    (tmp_path / "apps/web").mkdir(parents=True)
    (tmp_path / "apps/api/src").mkdir(parents=True)
    origins = [f"http://localhost:{port}" for port in PERMITTED]
    (tmp_path / "apps/api/src/server.js").write_text(f"const allowed = {json.dumps(origins)};\n")
    yield tmp_path
    pid_file = tmp_path / "apps/web/.vite.pid"
    if pid_file.exists():  # hygiene: stop only what the script under test recorded
        try:
            os.kill(int(pid_file.read_text().split()[0]), signal.SIGKILL)
        except (ValueError, IndexError, ProcessLookupError):
            return


@pytest.fixture
def backend() -> Iterator[Backend]:
    server = Backend(("127.0.0.1", 4000), _Health)
    server.origins = []
    server.allowed = [f"http://localhost:{port}" for port in PERMITTED]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield server
    server.shutdown()
    server.server_close()


@pytest.fixture
def occupy() -> Iterator[Callable[[int], socket.socket]]:
    sockets: list[socket.socket] = []

    def _occupy(port: int) -> socket.socket:
        listener = socket.socket()
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", port))
        listener.listen()
        sockets.append(listener)
        return listener

    yield _occupy
    for listener in sockets:
        listener.close()


@pytest.fixture
def run(repo: Path) -> Callable[..., subprocess.CompletedProcess[str]]:
    env = {**os.environ, "PATH": f"{HARNESS}{os.pathsep}{os.environ['PATH']}"}

    def _run(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, os.environ["MAGA_SCRIPT"], *args],
            cwd=repo,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    return _run
