"""TT-G2R: the Gate 2 run criteria, the 4-of-5 rule, and the run-again rule, with a stub runner."""

from pathlib import Path

import pytest

from maga.gate2 import PASS_AT, RUNS, TASK, AgentRun, RunnerError, gate2_verdict, run_passed
from maga.schemas import Contract, Entry, Package
from maga.triage import GOLDEN

DEMO = Path(__file__).parents[1] / "fixtures" / "demo-monorepo"
SKILL_DIR = ".claude/skills/vite-safe-dev-server"
SCRIPT_CALL = f"python {SKILL_DIR}/scripts/start.py"


def _run(*items: str, human: str = "") -> list[Entry]:
    """The successful run of the specification, with `items` as the tool calls after the skill read."""
    commands = [f"cat {SKILL_DIR}/SKILL.md", *items]
    texts = [("user_input", TASK), *[("tool_call", command) for command in commands]]
    if human:
        texts.insert(2, ("user_input", human))
    return [
        Entry.model_validate(
            {
                "entry_id": f"e{index}",
                "session_id": "run",
                "step_index": index,
                "source": "user" if kind == "user_input" else "model",
                "entry_type": kind,
                "timestamp": "2026-01-05T10:00:00Z",
                "content" if kind != "tool_call" else "command_line": text,
            }
        )
        for index, (kind, text) in enumerate(texts)
    ]


GOOD = _run(SCRIPT_CALL)
NO_CALL = _run("git status")


@pytest.fixture
def package(tmp_path: Path) -> Package:
    (tmp_path / "SKILL.md").write_text("---\nname: x\ndescription: y\n---\n")
    (tmp_path / "start.py").write_text("print('ok')\n")
    return Package(
        candidate_id="cand_vite_strict_port_001",
        script_path=str(tmp_path / "start.py"),
        skill_path=str(tmp_path / "SKILL.md"),
        test_path=str(tmp_path / "test_start.py"),
        contract=Contract.model_validate_json(GOLDEN),
    )


@pytest.mark.parametrize(
    ("entries", "exit_code", "passed"),
    [
        (GOOD, 0, True),  # TT-G2R-003 case 1
        (_run(f"cd /tmp/x && uv run python3 {SKILL_DIR}/scripts/start.py start"), 0, True),
        (NO_CALL, 0, False),  # case 2
        (_run(f"cat {SKILL_DIR}/scripts/start.py"), 0, False),  # case 3: read, not run
        (_run(SCRIPT_CALL, human="yes, go ahead"), 0, False),  # TT-G2R-009: intervention
        (GOOD, 1, False),  # TT-G2R-009: fatal error
        (_run("pnpm --dir apps/web exec vite --port 5173", SCRIPT_CALL), 0, False),  # TT-G2R-011
        (_run(SCRIPT_CALL, "npx vite --port 5175"), 0, False),
        (_run(SCRIPT_CALL, "cd apps/web && pnpm dev"), 0, False),
        (_run(SCRIPT_CALL, "cat apps/web/vite.config.ts"), 0, True),  # names Vite, starts nothing
    ],
)
def test_g2r_003_009_011_run_criteria(
    entries: list[Entry], exit_code: int, *, passed: bool
) -> None:
    assert run_passed(entries, exit_code) is passed


def test_g2r_003_a_script_path_in_prose_is_not_a_call() -> None:
    prose = GOOD[0].model_copy(
        update={"entry_type": "generic_message", "content": "I could run scripts/start.py"}
    )
    assert not run_passed([*NO_CALL, prose], 0)


@pytest.mark.parametrize(
    ("successes", "outcome"), [(0, "fail"), (3, "fail"), (4, "pass"), (5, "pass")]
)
def test_g2r_001_002_006_five_fresh_runs_and_the_four_of_five_rule(
    package: Package, successes: int, outcome: str
) -> None:
    calls: list[tuple[Path, str]] = []

    def runner(workdir: Path, task: str) -> AgentRun:
        calls.append((workdir, task))
        (workdir / "LEFTOVER").write_text("from an earlier run")
        return (GOOD if len(calls) <= successes else NO_CALL), 0

    verdict = gate2_verdict(package, DEMO, runner, total_revisions=1)
    assert (verdict.gate_number, verdict.outcome, verdict.total_revisions) == (2, outcome, 1)
    assert [verdict.test_results[f"run_{n}"] for n in range(1, RUNS + 1)] == (
        ["passed"] * successes + ["failed"] * (RUNS - successes)
    )
    workdirs = [workdir for workdir, _ in calls]
    assert len(set(workdirs)) == RUNS == 5
    assert PASS_AT == 4
    for workdir in workdirs:  # each run saw a fresh copy with the skill installed
        assert (workdir / SKILL_DIR / "scripts" / "start.py").read_text() == "print('ok')\n"
        assert (workdir / "packages/config/ports.json").exists()
    for _, task in calls:  # TT-G2R-002: the agent must discover the skill
        assert not any(name in task for name in ("start.py", "scripts/", "SKILL", "vite-safe"))


def test_g2r_007_a_run_that_cannot_execute_is_run_again_and_not_counted(package: Package) -> None:
    script = [GOOD, GOOD, GOOD, GOOD, RunnerError("API error"), NO_CALL]

    def runner(_workdir: Path, _task: str) -> AgentRun:
        step = script.pop(0)
        if isinstance(step, RunnerError):
            raise step
        return step, 0

    verdict = gate2_verdict(package, DEMO, runner, total_revisions=0)
    assert script == []  # 6 runner calls
    assert verdict.outcome == "pass"
    assert verdict.test_results["run_5"] == "failed"
    assert verdict.test_results["uncounted_attempts"] == ["run_5 attempt 1: API error"]


def test_g2r_012_two_failed_attempts_of_one_run_give_inconclusive(package: Package) -> None:
    calls: list[Path] = []

    def runner(workdir: Path, _task: str) -> AgentRun:
        calls.append(workdir)
        if len(calls) > 2:
            message = "API error"
            raise RunnerError(message)
        return GOOD, 0

    verdict = gate2_verdict(package, DEMO, runner, total_revisions=1)
    assert (verdict.outcome, verdict.total_revisions, len(calls)) == ("inconclusive", 1, 4)
    assert "run_3" not in verdict.test_results
