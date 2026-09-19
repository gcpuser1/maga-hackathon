"""CHECK, Gate 2: does a fresh agent find the skill and run the script, in 4 of 5 runs?"""

from collections.abc import Callable
import contextlib
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from typing import TypedDict

from maga.reader import parse_session
from maga.schemas import Entry, Package, Verdict

RUNS = 5
PASS_AT = 4
_ATTEMPTS = 2  # a run that cannot execute is run again once, and is not counted
# An ordinary goal. It names no script, no skill, and no path (ARCHITECTURE.md 9.2).
TASK = "Start the web frontend and verify that the backend accepts requests from it."
_AGENT_TIMEOUT_SECONDS = 600
_HARNESS = Path(__file__).parent / "gate1"
_ALLOWED_ORIGINS = ("http://localhost:5173", "http://localhost:5174")
_STEP = re.compile(r"&&|\|\||;|\n")
_PREFIX = r"^\s*(?:\w+=\S*\s+)*(?:nohup\s+)?"
# A call runs the script. `cat scripts/start.py` and prose about the script are not calls.
_SCRIPT_CALL = re.compile(
    _PREFIX + r"(?:uv run\s+)?(?:\S*python[\d.]*\s+)?\S*scripts/start\.py(?:\s|$)"
)
_VITE_LAUNCH = re.compile(
    _PREFIX
    + r"(?:(?:npx\s+|(?:pnpm|yarn)\s+(?:(?:--dir|-C)\s+\S+\s+)?(?:exec\s+)?|\S*node_modules/\.bin/)?vite(?:\s|$)"
    r"|(?:pnpm|npm|yarn)\s+(?:(?:--dir|-C)\s+\S+\s+)?(?:run\s+)?dev\b)"
)

AgentRun = tuple[list[Entry], int]  # the transcript of the run, and the exit code of the agent
Runner = Callable[[Path, str], AgentRun]


class RunnerError(Exception):
    """The run could not execute: infrastructure, not a result about the skill."""


def run_passed(entries: list[Entry], exit_code: int) -> bool:
    """The run criteria of ARCHITECTURE.md 9.2."""
    commands = [e.command_line for e in entries if e.entry_type == "tool_call" and e.command_line]
    steps = [step for command in commands for step in _STEP.split(command)]
    humans = [e for e in entries if e.entry_type == "user_input"]
    return (
        exit_code == 0
        and len(humans) <= 1  # a second human message is an intervention
        and any(_SCRIPT_CALL.match(step) for step in steps)
        and not any(_VITE_LAUNCH.match(step) for step in steps)
    )


def install_skill(package: Package, repo: Path) -> Path:
    """Put the skill and its script where Claude Code loads project skills. The tests stay out."""
    skill = repo / ".claude" / "skills" / package.contract.workflow_name
    (skill / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(package.skill_path, skill / "SKILL.md")
    shutil.copy(package.script_path, skill / "scripts" / "start.py")
    return skill


def _fresh_copy(demo_repo: Path) -> Path:
    """A new, isolated copy of the demo repository, so no run carries another run's changes."""
    workdir = Path(tempfile.mkdtemp(prefix="maga_gate2_")) / demo_repo.name
    shutil.copytree(demo_repo, workdir)
    return workdir


def fresh_workdir(package: Package, demo_repo: Path) -> Path:
    """A new copy of the demo repository with the skill where Claude Code loads project skills."""
    workdir = _fresh_copy(demo_repo)
    install_skill(package, workdir)
    return workdir


def _run_series(
    make_workdir: Callable[[], Path],
    runner: Runner,
    judge: Callable[[list[Entry], int], bool],
    record: Callable[[list[Entry], int], None] | None = None,
) -> tuple[dict[str, str], list[str], int, bool]:
    """RUNS attempts of TASK, each retried once on a RunnerError.

    Returns the per-run "passed"/"failed" results, the uncounted-attempt log, how many runs
    `judge` found true, and whether a run used up every attempt without executing at all
    (the caller reports that case as inconclusive, and stops asking for further runs).
    `record`, when given, sees every run's raw transcript and exit code, regardless of `judge`.
    """
    results: dict[str, str] = {}
    uncounted: list[str] = []
    passed = 0
    gave_up = False
    for number in range(1, RUNS + 1):
        for attempt in range(1, _ATTEMPTS + 1):
            try:
                entries, exit_code = runner(make_workdir(), TASK)
            except RunnerError as error:
                uncounted.append(f"run_{number} attempt {attempt}: {error}")
                if attempt == _ATTEMPTS:
                    gave_up = True
                continue
            if record:
                record(entries, exit_code)
            ok = judge(entries, exit_code)
            passed += ok
            results[f"run_{number}"] = "passed" if ok else "failed"
            break
        if gave_up:
            break
    return results, uncounted, passed, gave_up


def gate2_verdict(
    package: Package, demo_repo: Path, runner: Runner, total_revisions: int
) -> Verdict:
    started = time.monotonic()
    results, uncounted, passed, gave_up = _run_series(
        lambda: fresh_workdir(package, demo_repo), runner, run_passed
    )
    outcome = "inconclusive" if gave_up else ("pass" if passed >= PASS_AT else "fail")
    test_results = {
        "execution": "unconfined developer-host run, not a sandbox",
        **results,
        "uncounted_attempts": uncounted,
    }
    return Verdict.model_validate(
        {
            "candidate_id": package.candidate_id,
            "gate_number": 2,
            "outcome": outcome,
            "total_revisions": total_revisions,
            "test_results": test_results,
            "stdout_log": f"{passed} of {RUNS} runs passed; the threshold is {PASS_AT}",
            "stderr_log": "\n".join(uncounted),
            "execution_duration_ms": int((time.monotonic() - started) * 1000),
            "timestamp": datetime.now(UTC),
        }
    )


class _Health(BaseHTTPRequestHandler):
    # ponytail: the same 8 lines as the stub in gate1/conftest.py, which pytest owns.
    def do_GET(self) -> None:  # the name that BaseHTTPRequestHandler calls
        permitted = self.headers.get("Origin") in _ALLOWED_ORIGINS
        self.send_response(HTTPStatus.OK if permitted else HTTPStatus.FORBIDDEN)
        self.end_headers()


def claude_runner(workdir: Path, task: str) -> AgentRun:
    """One fresh headless Claude Code session, with the backend stub and the vite stand-in."""
    try:
        backend = HTTPServer(("127.0.0.1", 4000), _Health)
    except OSError as error:
        message = f"port 4000 is busy, so the backend stub cannot start: {error}"
        raise RunnerError(message) from error
    threading.Thread(target=backend.serve_forever, daemon=True).start()
    registry = workdir.parent / "vite_pids"  # the stand-in records its PID here
    env = {
        **os.environ,
        "PATH": f"{_HARNESS}{os.pathsep}{os.environ['PATH']}",
        "MAGA_VITE_PIDS": str(registry),
    }
    try:
        done = subprocess.run(
            [
                "claude",
                "-p",
                task,
                "--output-format",
                "json",
                "--allowedTools",
                "Bash",
                "Read",
                "Skill",
            ],
            cwd=workdir,
            env=env,
            stdin=subprocess.DEVNULL,  # an inherited stdin is appended to the prompt
            capture_output=True,
            text=True,
            timeout=_AGENT_TIMEOUT_SECONDS,
            check=False,
        )
        session_id = json.loads(done.stdout)["session_id"]
        (transcript,) = (Path.home() / ".claude" / "projects").glob(f"*/{session_id}.jsonl")
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError) as error:
        message = f"the agent run gave no transcript: {error}"
        raise RunnerError(message) from error
    finally:
        backend.shutdown()
        backend.server_close()
        for pid in registry.read_text().split() if registry.exists() else []:
            with contextlib.suppress(ProcessLookupError):
                os.kill(int(pid), signal.SIGTERM)  # only the processes that this run started
    return parse_session(transcript)[0], done.returncode


def _vite_call(entries: list[Entry]) -> bool:
    calls = [e.command_line for e in entries if e.entry_type == "tool_call" and e.command_line]
    return any(_VITE_LAUNCH.match(step) for call in calls for step in _STEP.split(call))


def _baseline_ok(_entries: list[Entry], exit_code: int) -> bool:
    """A run with no script to call has no run_passed-equivalent oracle for correctness.

    ponytail: "ok" here means the agent did not end in a fatal error, nothing more. Reading the
    raw transcripts is still how a person judges whether it bound an unpermitted port or touched
    something it should not have under port exhaustion (ARCHITECTURE.md 8.2).
    """
    return exit_code == 0


class _RunRecord(TypedDict):
    exit_code: int
    tool_calls: int
    tokens: int
    launched_vite_directly: bool


class SideReport(TypedDict):
    pass_rate: str
    average_tool_calls: float
    average_tokens: float
    direct_vite_launches: int
    uncounted_attempts: list[str]
    runs: list[_RunRecord]


class Comparison(TypedDict):
    candidate_id: str
    task: str
    baseline: SideReport
    skill_equipped: SideReport


def _side(
    make_workdir: Callable[[], Path], runner: Runner, judge: Callable[[list[Entry], int], bool]
) -> SideReport:
    raw: list[_RunRecord] = []

    def record(entries: list[Entry], exit_code: int) -> None:
        raw.append(
            {
                "exit_code": exit_code,
                "tool_calls": sum(1 for e in entries if e.entry_type == "tool_call"),
                "tokens": sum((e.tokens_in or 0) + (e.tokens_out or 0) for e in entries),
                "launched_vite_directly": _vite_call(entries),
            }
        )

    _results, uncounted, passed, _gave_up = _run_series(make_workdir, runner, judge, record)
    calls = [run["tool_calls"] for run in raw]
    tokens = [run["tokens"] for run in raw]
    return {
        "pass_rate": f"{passed}/{RUNS}",
        "average_tool_calls": round(sum(calls) / len(calls), 1) if calls else 0.0,
        "average_tokens": round(sum(tokens) / len(tokens), 1) if tokens else 0.0,
        "direct_vite_launches": sum(1 for run in raw if run["launched_vite_directly"]),
        "uncounted_attempts": uncounted,
        "runs": raw,
    }


def compare(
    package: Package, demo_repo: Path, state: Path, runner: Runner = claude_runner
) -> Comparison:
    """The before/after comparison of ARCHITECTURE.md 8.3: RUNS fresh runs of TASK, with and
    without the skill installed, in equivalent fresh copies of demo_repo. Same task, same model,
    same limits; only the presence of the skill differs.
    """
    report: Comparison = {
        "candidate_id": package.candidate_id,
        "task": TASK,
        "baseline": _side(lambda: _fresh_copy(demo_repo), runner, _baseline_ok),
        "skill_equipped": _side(lambda: fresh_workdir(package, demo_repo), runner, run_passed),
    }
    target = state / "comparison" / f"{package.candidate_id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2))
    return report
