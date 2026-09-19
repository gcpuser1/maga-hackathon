"""TT-PUB: the approval binds to the package content, and the read-back is a real check."""

from pathlib import Path

import pytest

from maga.publisher import (
    Destination,
    PrService,
    PublishError,
    approve_package,
    git,
    package_hash,
    publish,
)
from maga.schemas import Verdict

CANDIDATE = "cand_a"
TARGET = Path(".claude/skills/vite-safe-dev-server")


def _staged(root: Path) -> Path:
    staged = root / "staged"
    for name, text in {
        "SKILL.md": "---\nname: x\ndescription: y\n---\n",
        "scripts/start.py": "print('ok')\n",
        "tests/test_start.py": "def test_a(): pass\n",
    }.items():
        (staged / name).parent.mkdir(parents=True, exist_ok=True)
        (staged / name).write_text(text)
    return staged


def _verdict(state: Path, staged: Path, gate: int = 2, outcome: str = "pass") -> None:
    verdict = Verdict.model_validate(
        {
            "candidate_id": CANDIDATE,
            "gate_number": gate,
            "outcome": outcome,
            "total_revisions": 0,
            "test_results": {"package_sha256": package_hash(staged)},
            "stdout_log": "",
            "stderr_log": "",
            "execution_duration_ms": 1,
            "timestamp": "2026-01-05T10:00:06Z",
        }
    )
    folder = state / "verification"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{CANDIDATE}_gate{gate}_verdict.json").write_text(verdict.model_dump_json())


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A target repository with a local bare remote, a dirty tree, and no .gitignore."""
    remote, work = tmp_path / "remote.git", tmp_path / "work"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    git(tmp_path, "init", "-q", "-b", "main", str(work))
    for key, value in {"user.name": "t", "user.email": "t@example.invalid"}.items():
        git(work, "config", key, value)
    (work / "README.md").write_text("demo\n")
    git(work, "add", "README.md")
    git(work, "commit", "-q", "-m", "init")
    git(work, "remote", "add", "origin", str(remote))
    (work / "README.md").write_text("demo, modified and not committed\n")
    (work / "notes.txt").write_text("untracked\n")
    (work / ".maga/state").mkdir(parents=True)
    (work / ".maga/state/secret.json").write_text("{}")
    return work


def _service(head: str | None = None, error: str = "") -> PrService:
    def read_back(worktree: Path, _url: str) -> str:
        if error:
            raise PublishError(error)
        return head or git(worktree, "rev-parse", "HEAD")

    def open_pr(_repo: Path, _branch: str, _title: str, _body: str) -> str:
        return "https://example.invalid/pull/1"

    return PrService(open_pr, read_back)


def _ready(tmp_path: Path) -> tuple[Path, Path]:
    state, staged = tmp_path / "state", _staged(tmp_path)
    _verdict(state, staged)
    approve_package(state, CANDIDATE, staged)
    return state, staged


@pytest.mark.parametrize(
    ("change", "valid"),
    [
        ("scripts/start.py", False),
        ("SKILL.md", False),
        ("tests/test_start.py", False),
        ("scripts/extra.sh", False),
        ("", True),  # the control
    ],
)
def test_pub_001_the_approval_is_bound_to_the_package_content(
    tmp_path: Path, repo: Path, change: str, *, valid: bool
) -> None:
    state, staged = _ready(tmp_path)
    if change:
        with (staged / change).open("a") as file:
            file.write("#")
        _verdict(state, staged)  # the verdict follows the change, so only the approval is stale
    if valid:
        assert publish(state, CANDIDATE, staged, Destination(repo, TARGET), _service())
    else:
        with pytest.raises(PublishError, match="no human approval for this exact package"):
            publish(state, CANDIDATE, staged, Destination(repo, TARGET), _service())


def test_pub_002_an_approval_does_not_move_to_another_candidate(
    tmp_path: Path, repo: Path
) -> None:
    state, staged = _ready(tmp_path)
    approvals = state / "approvals"
    (approvals / "cand_b_package.json").write_text(
        (approvals / f"{CANDIDATE}_package.json").read_text()
    )
    verdicts = state / "verification"
    (verdicts / "cand_b_gate2_verdict.json").write_text(
        (verdicts / f"{CANDIDATE}_gate2_verdict.json").read_text()
    )
    with pytest.raises(PublishError, match="no human approval"):
        publish(state, "cand_b", staged, Destination(repo, TARGET), _service())


def test_pub_003_only_the_approved_files_are_committed(tmp_path: Path, repo: Path) -> None:
    state, staged = _ready(tmp_path)
    url = publish(state, CANDIDATE, staged, Destination(repo, TARGET), _service())
    assert url == "https://example.invalid/pull/1"
    remote = repo.parent / "remote.git"
    committed = git(remote, "show", "--name-only", "--format=", f"maga/{CANDIDATE}").splitlines()
    assert sorted(committed) == sorted(
        f"{TARGET}/{name}" for name in ("SKILL.md", "scripts/start.py", "tests/test_start.py")
    )
    script = git(remote, "show", f"maga/{CANDIDATE}:{TARGET}/scripts/start.py")
    assert script == "print('ok')"
    assert (repo / "notes.txt").exists()  # the caller's checkout is untouched
    assert git(repo, "branch", "--show-current") == "main"


@pytest.mark.parametrize(
    ("service", "message"),
    [
        (_service(head="0" * 40), "read-back mismatch"),
        (_service(error="HTTP 404: no such pull request"), "HTTP 404"),
    ],
)
def test_pub_004_the_read_back_detects_a_difference(
    tmp_path: Path, repo: Path, service: PrService, message: str
) -> None:
    state, staged = _ready(tmp_path)
    with pytest.raises(PublishError, match=message):
        publish(state, CANDIDATE, staged, Destination(repo, TARGET), service)


@pytest.mark.parametrize("verdict", ["none", "gate1_pass", "gate2_fail"])
def test_pub_005_a_gate_2_pass_for_this_package_is_required(
    tmp_path: Path, repo: Path, verdict: str
) -> None:
    state, staged = tmp_path / "state", _staged(tmp_path)
    approve_package(state, CANDIDATE, staged)
    if verdict == "gate1_pass":
        _verdict(state, staged, gate=1)
    if verdict == "gate2_fail":
        _verdict(state, staged, outcome="fail")
    with pytest.raises(PublishError, match="Gate 2"):
        publish(state, CANDIDATE, staged, Destination(repo, TARGET), _service())
    assert git(repo, "branch", "--list", "maga/*") == ""
