"""A hand-written script that satisfies the golden contract, with switchable defects.

Gate 1 runs the acceptance suite against the defects first: a suite that passes a no-op, or a
script that skips the Origin check, proves nothing about the generated script.
MAGA_VARIANT: noop, skip_origin, autoincrement, duplicate. Unset means the correct script.
"""

import http.client
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from typing import NoReturn

VARIANT = os.environ.get("MAGA_VARIANT", "")
BACKEND_PORT = 4000
OK = 200
PID_FILE = Path("apps/web/.vite.pid")
TIMEOUT_SECONDS = 15


def finish(code: int, **result: object) -> NoReturn:
    sys.stdout.write(json.dumps(result) + "\n")
    sys.exit(code)


def status(port: int, path: str = "/", origin: str | None = None) -> int:
    connection = http.client.HTTPConnection("localhost", port, timeout=2)
    try:
        connection.request("GET", path, headers={"Origin": origin} if origin else {})
        return connection.getresponse().status
    except OSError:
        return 0
    finally:
        connection.close()


def origin_accepted(port: int) -> bool:
    if VARIANT == "skip_origin":
        return True
    return status(BACKEND_PORT, "/api/health", f"http://localhost:{port}") == OK


def free(port: int) -> bool:
    with socket.socket() as probe:
        return probe.connect_ex(("127.0.0.1", port)) != 0


def owned() -> tuple[int, int] | None:
    try:
        pid, port = (int(part) for part in PID_FILE.read_text().split())
        os.kill(pid, 0)
    except (OSError, ValueError):
        return None
    return pid, port


def stop() -> None:
    running = owned()
    if running:
        os.kill(running[0], signal.SIGTERM)  # only the PID that this script recorded
    PID_FILE.unlink(missing_ok=True)
    finish(0, status="stopped", pid=running[0] if running else None)


def start() -> None:
    config = Path("packages/config/ports.json")
    if not config.exists():
        finish(1, status="error", reason="precondition_failed", detail=f"{config} is absent")
    ports = json.loads(config.read_text())["frontend_ports"]
    running = None if VARIANT == "duplicate" else owned()
    if running and status(running[1]) == OK and origin_accepted(running[1]):
        finish(0, status="ready", port=running[1], pid=running[0])
    port = next((p for p in ports if free(p)), None)
    strict = ["--strictPort"]
    if VARIANT == "autoincrement":
        port, strict = next(p for p in range(ports[0], ports[0] + 50) if free(p)), []
    if port is None:
        finish(1, status="error", reason="all_permitted_ports_exhausted", tried=ports)
    vite = subprocess.Popen(
        ["vite", "--port", str(port), *strict],
        cwd="apps/web",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    deadline = time.monotonic() + TIMEOUT_SECONDS
    while status(port) != OK:
        if vite.poll() is not None or time.monotonic() > deadline:
            vite.kill()
            finish(1, status="error", reason="precondition_failed", detail="vite did not start")
        time.sleep(0.1)
    if not origin_accepted(port):
        vite.terminate()
        finish(1, status="error", reason="cors_origin_rejected", port=port)
    PID_FILE.write_text(f"{vite.pid} {port}")
    finish(0, status="ready", port=port, pid=vite.pid)


if __name__ == "__main__":
    if VARIANT == "noop":
        sys.exit(0)
    stop() if sys.argv[1:] == ["stop"] else start()
