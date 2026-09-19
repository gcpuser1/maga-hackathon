"""TT-ACC, TT-G1I-001, and the revision budget of TT-REV for Gate 1."""

from collections.abc import Callable
from pathlib import Path
import shutil

import pytest

from maga.schemas import Contract, Package
from maga.triage import GOLDEN
from maga.verifier import PROBES, Run, check, gate1_verdict, run_suite

FIXTURES = Path(__file__).parent / "fixtures" / "model_responses"
SUITE = FIXTURES / "test_start.py.txt"
PROBE = Path(__file__).parents[1] / "src" / "maga" / "gate1" / "probe_start.py"
PACKAGE = Package(
    candidate_id="cand_vite_strict_port_001",
    script_path=str(PROBE),
    skill_path="SKILL.md",
    test_path=str(SUITE),
    contract=Contract.model_validate_json(GOLDEN),
)
needs_docker = pytest.mark.skipif(shutil.which("docker") is None, reason="Gate 1 needs Docker")
FAILED: Run = (1, "FAILED t.py::test_case_c", "")
PASSED: Run = (0, "", "")
NO_CONTAINER: Run = (None, "", "infrastructure: down")


def _stub(script_runs: list[Run], probe: Run = FAILED) -> tuple[list[str], Callable[..., Run]]:
    calls: list[str] = []

    def suite(_script: Path, _tests: Path, variant: str = "") -> Run:
        calls.append(variant or "script")
        return probe if variant else script_runs.pop(0)

    return calls, suite


@needs_docker
@pytest.mark.parametrize(
    ("variant", "failed"),
    [
        ("", set[str]()),  # TT-ACC-001: the positive control
        ("noop", {"test_case_a", "test_case_b", "test_case_d"}),  # TT-ACC-002
        ("autoincrement", {"test_case_c"}),  # TT-ACC-003
        ("skip_origin", {"test_a_rejected_origin"}),  # TT-ACC-004
        ("duplicate", {"test_case_d"}),  # TT-ACC-005
    ],
)
def test_acc_the_suite_passes_the_correct_script_and_fails_each_defect(
    variant: str, failed: set[str]
) -> None:
    code, out, _ = run_suite(PROBE, SUITE, variant)
    assert code == (1 if failed else 0), out
    assert "7 passed" in out or failed
    for name in failed:
        assert any(line.startswith("FAILED") and name in line for line in out.splitlines()), out


@needs_docker
def test_g1i_001_no_network_is_reachable(tmp_path: Path) -> None:
    online = tmp_path / "test_online.py"
    online.write_text(
        "import socket\n\n\ndef test_dns_and_route():\n"
        "    socket.create_connection(('1.1.1.1', 53), timeout=3).close()\n"
    )
    code, out, _ = run_suite(PROBE, online)
    assert code == 1, out
    assert "Network is unreachable" in out or "OSError" in out


def test_the_probes_run_before_the_script_and_a_pass_stores_the_results() -> None:
    calls, suite = _stub([(0, "PASSED t.py::test_case_a\nPASSED t.py::test_case_b", "")])
    verdict = gate1_verdict(PACKAGE, 0, suite)
    assert calls == [*PROBES, "script"]
    assert verdict.outcome == "pass"
    assert verdict.test_results == {
        "probe:noop": "rejected",
        "probe:skip_origin": "rejected",
        "test_case_a": "PASSED",
        "test_case_b": "PASSED",
    }


def test_a_suite_that_passes_a_probe_is_invalid_and_never_grades_the_script(
    tmp_path: Path,
) -> None:
    calls, suite = _stub([PASSED], probe=PASSED)
    revisions: list[str] = []
    verdict = check(PACKAGE, tmp_path, lambda log: revisions.append(log) or PACKAGE, suite)
    assert verdict.outcome == "fail"
    assert verdict.stderr_log.startswith("suite_invalid")
    assert verdict.test_results == {"probe:noop": "NOT rejected"}
    assert "script" not in calls
    assert revisions == []  # no revision of the script can repair a weak suite


@pytest.mark.parametrize(
    ("runs", "outcome", "revisions"),
    [
        ([PASSED], "pass", 0),
        ([FAILED, FAILED, PASSED], "pass", 2),
        ([FAILED, FAILED, FAILED, PASSED], "pass", 3),  # TT-REV-001: the third revision is allowed
        ([FAILED, FAILED, FAILED, FAILED, PASSED], "fail", 3),  # the fourth failure ends the loop
        ([FAILED, NO_CONTAINER], "inconclusive", 1),  # infrastructure: stop, use no revision
    ],
)
def test_rev_one_first_attempt_plus_three_revisions(
    tmp_path: Path, runs: list[Run], outcome: str, revisions: int
) -> None:
    logs: list[str] = []
    _, suite = _stub(list(runs))
    verdict = check(PACKAGE, tmp_path, lambda log: logs.append(log) or PACKAGE, suite)
    assert (verdict.outcome, verdict.total_revisions, len(logs)) == (outcome, revisions, revisions)
    assert all("FAILED t.py::test_case_c" in log for log in logs)  # TT-REV-006: the failure log
    stored = (tmp_path / "verification" / f"{PACKAGE.candidate_id}_verdict.json").read_text()
    assert f'"outcome": "{outcome}"' in stored
    assert PACKAGE.contract == Contract.model_validate_json(GOLDEN)


def test_an_inconclusive_probe_run_is_not_a_failure() -> None:
    _, suite = _stub([PASSED], probe=NO_CONTAINER)
    assert gate1_verdict(PACKAGE, 0, suite).outcome == "inconclusive"
