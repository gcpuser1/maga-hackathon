"""TT-PAR and TT-RDX: Claude Code transcript parsing and secret redaction."""

import json
from pathlib import Path
from typing import Any

import pytest

from maga.reader import PLACEHOLDER, parse_session, read, redact

P1 = Path(__file__).parent / "fixtures" / "claude_code" / "p1"
# Built at runtime, so no file holds a complete secret-shaped literal.
SECRETS = {
    "API_KEY=" + "FAKE_SECRET_VALUE_001": "FAKE_SECRET_VALUE_001",
    "Authorization: Bearer " + "FAKE_SECRET_VALUE_002": "FAKE_SECRET_VALUE_002",
    "ghp_" + "FAKE" * 9: "FAKE" * 9,
    "AKIA" + "FAKE" * 4: "FAKE" * 4,
    "sk-" + "FAKE" * 6: "FAKE" * 6,
    "xoxb-" + "FAKE-FAKE": "FAKE-FAKE",
}


def _line(number: int, kind: str, content: object, **extra: object) -> dict[str, Any]:
    return {
        "type": kind,
        "sessionId": "sess-x",
        "uuid": f"sess-x-L{number:02d}",
        "timestamp": f"2026-01-05T10:00:{number:02d}.000Z",
        "cwd": "/home/dev_x/repo",
        "message": {"role": kind, "content": content},
        **extra,
    }


def _call(number: int, tool_id: str, command: str, **more: object) -> dict[str, Any]:
    tool_input = {"command": command, **more}
    block = {"type": "tool_use", "id": tool_id, "name": "Bash", "input": tool_input}
    return _line(number, "assistant", [block])


def _result(number: int, tool_id: str, content: str, *, is_error: bool) -> dict[str, Any]:
    block = {
        "type": "tool_result",
        "tool_use_id": tool_id,
        "content": content,
        "is_error": is_error,
    }
    return _line(number, "user", [block])


def _write(tmp_path: Path, lines: list[dict[str, Any] | str]) -> Path:
    path = tmp_path / "sess-x.jsonl"
    path.write_text(
        "".join((ln if isinstance(ln, str) else json.dumps(ln)) + "\n" for ln in lines)
    )
    return path


def test_par_001_002_008_map_the_lines_and_keep_the_identifiers() -> None:
    entries, malformed = parse_session(P1 / "sess-a.jsonl")
    assert malformed == 0
    assert [e.entry_id for e in entries] == [f"sess-a-L{n:02d}" for n in (1, 4, 5, 6, 7, 8, 9)]
    assert [e.step_index for e in entries] == list(range(7))
    human, call, result = entries[:3]
    assert (human.source, human.entry_type, human.content) == (
        "user",
        "user_input",
        "Start the web frontend.",
    )
    assert (call.source, call.entry_type, call.tool_name) == ("model", "tool_call", "Bash")
    assert call.command_line == "pnpm --dir /home/dev_a/workspace/apps/web install"
    assert call.working_dir == "/home/dev_a/workspace"
    assert (result.entry_type, result.exit_code) == ("tool_result", 0)
    assert {e.session_id for e in entries} == {"sess-a"}
    assert call.timestamp.isoformat() == "2026-01-05T10:00:04+00:00"
    stored = "".join(e.model_dump_json() for e in entries)
    assert "MARKER" not in stored


def test_par_001_model_prose_is_a_generic_message(tmp_path: Path) -> None:
    lines = [_line(1, "assistant", [{"type": "text", "text": "The frontend is ready."}])]
    (entry,), _ = parse_session(_write(tmp_path, [*lines]))
    assert (entry.source, entry.entry_type) == ("model", "generic_message")


def test_a_meta_user_line_is_not_a_human_message(tmp_path: Path) -> None:
    body = [{"type": "text", "text": "Base directory for this skill: /repo/.claude/skills/x"}]
    lines = [_line(1, "user", "Start the web frontend."), _line(2, "user", body, isMeta=True)]
    human, meta = parse_session(_write(tmp_path, [*lines]))[0]
    assert (human.source, human.entry_type) == ("user", "user_input")
    assert (meta.source, meta.entry_type) == ("system", "generic_message")


def test_par_008_an_unknown_line_type_is_not_imported(tmp_path: Path) -> None:
    lines = [
        _line(n, kind, "BOOKKEEPING_MARKER_002") for n, kind in enumerate(["ai-title", "mode"])
    ]
    assert parse_session(_write(tmp_path, [*lines])) == ([], 0)


def test_par_003_join_a_call_with_its_result_by_tool_use_id(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        [
            _line(1, "user", "Start vite."),
            _call(2, "toolu_x_01", "vite"),
            _call(3, "toolu_x_02", "vite --port 5174"),
            _result(4, "toolu_x_02", "ready", is_error=False),
            _line(5, "user", "continue"),
            _result(6, "toolu_x_01", "Exit code 1\nPort 5173 is in use", is_error=True),
        ],
    )
    entries, _ = parse_session(path)
    exit_codes = {e.command_line: e.exit_code for e in entries if e.entry_type == "tool_call"}
    assert exit_codes == {"vite": 1, "vite --port 5174": 0}
    assert [e.exit_code for e in entries if e.entry_type == "user_input"] == [None, None]


def test_par_004_a_malformed_line_is_counted_and_the_rest_is_imported(tmp_path: Path) -> None:
    good = [_line(n, "user", f"message {n}") for n in (1, 2, 4, 5)]
    no_uuid = {key: value for key, value in _line(6, "user", "no uuid").items() if key != "uuid"}
    path = _write(tmp_path, [*good[:2], '{"type": "assistant", "sessionId":', *good[2:], no_uuid])
    entries, malformed = parse_session(path)
    assert (len(entries), malformed) == (4, 2)
    assert read([path], tmp_path / "state")["malformed_lines"] == 2


@pytest.mark.parametrize(
    ("is_error", "content", "expected"),
    [
        (False, "Done", 0),
        (True, "Exit code 1\nPort 5173 is in use", 1),
        (True, "Exit code 127\ncommand not found", 127),
        (True, "Command timed out", None),
    ],
)
def test_par_005_parse_the_exit_code(
    tmp_path: Path, *, is_error: bool, content: str, expected: int | None
) -> None:
    lines = [_call(1, "toolu_x_01", "vite"), _result(2, "toolu_x_01", content, is_error=is_error)]
    entries, _ = parse_session(_write(tmp_path, [*lines]))
    assert [e.exit_code for e in entries] == [expected, expected]


def test_par_005_missing_data_is_unknown(tmp_path: Path) -> None:
    call = _call(1, "toolu_x_01", "vite")
    del call["cwd"]
    absent = _result(3, "toolu_x_02", "fine", is_error=False)
    del absent["message"]["content"][0]["is_error"]
    entries, _ = parse_session(_write(tmp_path, [call, _call(2, "toolu_x_02", "ls"), absent]))
    assert (entries[0].exit_code, entries[0].working_dir) == (None, None)
    assert entries[1].exit_code is None


def test_par_006_import_once(tmp_path: Path) -> None:
    state = tmp_path / "state"
    reports = [read([P1 / "sess-a.jsonl"], state) for _ in range(3)]
    assert [r["new_entries"] for r in reports] == [7, 0, 0]
    stored = json.loads((state / "entries" / "sess-a.json").read_text())
    assert len({e["entry_id"] for e in stored}) == len(stored) == 7


def test_an_oversized_result_keeps_its_head_and_tail_with_a_marker(tmp_path: Path) -> None:
    text = "\n".join(f"LINE-{n:04d}" for n in range(1, 2001))
    lines = [_call(1, "toolu_x_01", "seq"), _result(2, "toolu_x_01", text, is_error=False)]
    entries, _ = parse_session(_write(tmp_path, [*lines]))
    output = entries[1].sanitized_output or ""
    assert output.startswith("LINE-0001")
    assert output.endswith("LINE-2000")
    assert "characters omitted" in output
    assert len(output) < 1100


@pytest.mark.parametrize("secret", SECRETS)
def test_rdx_001_005_redact_each_pattern_and_stay_stable(secret: str) -> None:
    once = redact(f"export {secret} && pnpm dev")
    assert SECRETS[secret] not in once
    assert PLACEHOLDER in once
    assert once.endswith(" && pnpm dev")
    assert redact(once) == once


@pytest.mark.parametrize("field", ["command_line", "content", "sanitized_output", "args"])
def test_rdx_002_redaction_covers_every_text_field(tmp_path: Path, field: str) -> None:
    secret = "API_KEY=" + "FAKE_SECRET_VALUE_001"
    lines = {
        "command_line": _call(1, "toolu_x_01", f"export {secret} && pnpm dev"),
        "content": _line(1, "user", f"use {secret}"),
        "sanitized_output": _result(1, "toolu_x_01", f"env: {secret}", is_error=False),
        "args": _call(1, "toolu_x_01", "pnpm dev", description=f"run with {secret}"),
    }
    (entry,), _ = parse_session(_write(tmp_path, [lines[field]]))
    assert "FAKE_SECRET_VALUE_001" not in entry.model_dump_json()
    assert PLACEHOLDER in entry.model_dump_json()


@pytest.mark.parametrize(
    "text",
    [
        "pnpm --dir /home/dev_a/workspace/apps/web exec vite --port 5173 --strictPort",
        "echo Bearing load is fine",
        "open the task-list-of-the-whole-team-today file",
    ],
)
def test_rdx_004_redaction_keeps_non_secret_text(text: str) -> None:
    assert redact(text) == text


def test_rdx_006_known_limit_a_prose_password_is_not_redacted() -> None:
    text = "the database password is " + "FAKE_SECRET_VALUE_003"
    assert "FAKE_SECRET_VALUE_003" in redact(text), "known limit, not a wanted behaviour"
