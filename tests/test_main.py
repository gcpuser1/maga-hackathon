"""The entry point: exit 0 pass, 1 fail, 2 usage, for each stage that needs no model."""

from pathlib import Path
import sys

import pytest

from maga.__main__ import main

P1 = sorted((Path(__file__).parent / "fixtures" / "claude_code" / "p1").glob("*.jsonl"))


def _maga(monkeypatch: pytest.MonkeyPatch, *args: str) -> int:
    monkeypatch.setattr(sys, "argv", ["maga", *args])
    return main()


def test_read_then_find_on_the_synthetic_sessions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    assert _maga(monkeypatch, "find") == 1  # no entries yet: a fail, not a crash
    assert _maga(monkeypatch, "read", *map(str, P1)) == 0
    assert '"new_entries": 21' in capsys.readouterr().out
    assert _maga(monkeypatch, "find") == 0
    assert "vite --port $PORT_LIST --strictPort" in capsys.readouterr().out
    assert len(list((tmp_path / ".maga/state/candidates").glob("*.json"))) == 1


@pytest.mark.parametrize("stage", ["build", "check", "verify", "propose"])
def test_a_stage_with_no_approved_contract_fails_and_does_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str
) -> None:
    monkeypatch.chdir(tmp_path)
    assert _maga(monkeypatch, stage, "cand_missing") == 1
    assert not (tmp_path / ".maga/artifacts").exists()


def test_decide_with_no_candidate_is_a_usage_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert _maga(monkeypatch, "decide", "cand_missing") == 2


@pytest.mark.parametrize("args", [[], ["publish"], ["check"]])
def test_a_usage_error_exits_2(monkeypatch: pytest.MonkeyPatch, args: list[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        _maga(monkeypatch, *args)
    assert caught.value.code == 2
