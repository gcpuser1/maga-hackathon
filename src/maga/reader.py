"""READ: parse Claude Code session files into redacted Entry records (ARCHITECTURE.md 3)."""

from collections.abc import Iterable, Iterator
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, cast

from pydantic import BaseModel, Field, TypeAdapter

from maga.schemas import Entry

PLACEHOLDER = "[REDACTED_SECRET]"
# Pattern redaction is incomplete protection (ARCHITECTURE.md 2.2 decision 11).
_SECRETS = [
    (re.compile(r"(\w*API_KEY\s*[=:]\s*)\S+"), rf"\1{PLACEHOLDER}"),
    (re.compile(r"(Bearer\s+)[\w.~+/=-]{8,}"), rf"\1{PLACEHOLDER}"),
    (re.compile(r"\bgh[pousr]_\w{8,}"), PLACEHOLDER),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), PLACEHOLDER),
    (re.compile(r"\bsk-[\w-]{16,}"), PLACEHOLDER),
    (re.compile(r"\bxox[bp]-[\w-]+"), PLACEHOLDER),
    (re.compile(r"\bAIza[\w-]{35}"), PLACEHOLDER),
]
_EXIT_CODE = re.compile(r"Exit code (\d+)")
_HEAD, _TAIL = 600, 400
_ENTRIES = TypeAdapter(list[Entry])
_CHECKPOINTS = TypeAdapter(dict[str, list[int]])
# Raise it when the parse rules change. A checkpoint of another version is parsed again, so the
# stored entries never stay behind the parser.
PARSER_VERSION = 2


class _Message(BaseModel):
    content: str | list[dict[str, Any]]
    usage: dict[str, Any] = Field(default_factory=dict)


class _Line(BaseModel):
    session_id: str = Field(alias="sessionId")
    uuid: str
    timestamp: datetime
    cwd: str | None = None
    # The harness writes meta lines (a loaded skill body, a command caveat). No person typed them.
    is_meta: bool = Field(default=False, alias="isMeta")
    message: _Message


def redact(text: str) -> str:
    for pattern, replacement in _SECRETS:
        text = pattern.sub(replacement, text)
    return text


def _clip(text: str) -> str:
    """Redact, then keep the head and the tail of an oversized text."""
    text = redact(text)
    if len(text) <= _HEAD + _TAIL:
        return text
    omitted = len(text) - _HEAD - _TAIL
    return f"{text[:_HEAD]}\n[... {omitted} characters omitted ...]\n{text[-_TAIL:]}"


def _scrub(value: object) -> object:
    if isinstance(value, str):
        return _clip(value)
    if isinstance(value, dict):
        return {key: _scrub(item) for key, item in cast("dict[str, object]", value).items()}
    if isinstance(value, list):
        return [_scrub(item) for item in cast("list[object]", value)]
    return value


def _exit_code(is_error: object, text: str) -> int | None:
    if is_error is False:
        return 0
    found = _EXIT_CODE.match(text) if is_error is True else None
    return int(found[1]) if found else None


def _result_text(content: object) -> str:
    if isinstance(content, str):
        return content
    blocks = cast("list[dict[str, object]]", content) if isinstance(content, list) else []
    return "\n".join(str(block.get("text", "")) for block in blocks)


def _fields(kind: str, block: dict[str, Any], *, is_meta: bool) -> dict[str, Any] | None:
    """Map one content block to Entry fields. None for a block with no procedure evidence."""
    if block.get("type") == "text":
        human = kind == "user" and not is_meta
        return {
            "source": "user" if human else "system" if kind == "user" else "model",
            "entry_type": "user_input" if human else "generic_message",
            "content": _clip(str(block.get("text", ""))),
        }
    if block.get("type") == "tool_use":
        tool_input = cast("dict[str, Any]", block.get("input") or {})
        command = tool_input.get("command")
        return {
            "source": "model",
            "entry_type": "tool_call",
            "tool_name": block.get("name"),
            "command_line": redact(command) if isinstance(command, str) else None,
            "args": _scrub(tool_input),
        }
    if block.get("type") == "tool_result":
        text = _result_text(block.get("content"))
        return {
            "source": "system",
            "entry_type": "tool_result",
            "exit_code": _exit_code(block.get("is_error"), text),
            "sanitized_output": _clip(text),
        }
    return None  # thinking, images


def _typed_mid_turn(attachment: object) -> str | None:
    """The text of a message that a person typed while the agent worked, else None.

    Claude Code stores it as an `attachment` line, not as a `user` line. A task notification and
    a message from another agent have the same line type, and no person typed them.
    """
    if not isinstance(attachment, dict):
        return None
    fields = cast("dict[str, Any]", attachment)
    origin = fields.get("origin")
    human = isinstance(origin, dict) and cast("dict[str, Any]", origin).get("kind") == "human"
    prompt = fields.get("prompt")
    if fields.get("type") == "queued_command" and fields.get("humanTurn") is True and human:
        return prompt if isinstance(prompt, str) else None
    return None


def _lines(path: Path) -> Iterator[tuple[str, _Line] | None]:
    """Yield each `user` and `assistant` line, and None for each malformed line."""
    with path.open(encoding="utf-8", errors="replace") as raw_lines:
        for raw in raw_lines:
            if not raw.strip():
                continue
            try:
                line = json.loads(raw)
                kind = line["type"]
                if kind in {"user", "assistant"}:  # an import list, never a skip list
                    yield kind, _Line.model_validate(line)
                elif kind == "attachment" and (typed := _typed_mid_turn(line.get("attachment"))):
                    yield "user", _Line.model_validate(line | {"message": {"content": typed}})
            except (ValueError, KeyError, TypeError):
                yield None


def parse_session(path: Path) -> tuple[list[Entry], int]:
    """Return the entries of one session file and the count of malformed lines."""
    entries: list[Entry] = []
    calls: dict[str, Entry] = {}
    malformed = 0
    for parsed in _lines(path):
        if parsed is None:
            malformed += 1
            continue
        kind, line = parsed
        content = line.message.content
        blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
        first = True
        for block in blocks:
            fields = _fields(kind, block, is_meta=line.is_meta)
            if fields is None:
                continue
            entry = Entry(
                entry_id=line.uuid if first else f"{line.uuid}#{len(entries)}",
                session_id=line.session_id,
                step_index=len(entries),
                working_dir=line.cwd,
                tokens_in=line.message.usage.get("input_tokens"),
                tokens_out=line.message.usage.get("output_tokens"),
                timestamp=line.timestamp,
                **fields,
            )
            first = False
            entries.append(entry)
            if entry.entry_type == "tool_call":
                calls[str(block.get("id"))] = entry
            elif (call := calls.get(str(block.get("tool_use_id")))) is not None:
                # The join of ARCHITECTURE.md 3.2: the call carries its own result.
                call.exit_code, call.sanitized_output = entry.exit_code, entry.sanitized_output
    return entries, malformed


def read(paths: Iterable[Path], state: Path) -> dict[str, int]:
    """Store the entries of each session under `state`/entries and report the counts.

    `import_checkpoints.json` holds the size, the modification time, the malformed-line count,
    and the parser version of each imported file, so an unchanged file is not parsed again.
    """
    report = {"files": 0, "unchanged_files": 0, "new_entries": 0, "malformed_lines": 0}
    (state / "entries").mkdir(parents=True, exist_ok=True)
    checkpoint_file = state / "import_checkpoints.json"
    checkpoints = (
        _CHECKPOINTS.validate_json(checkpoint_file.read_bytes())
        if checkpoint_file.exists()
        else {}
    )
    try:
        for path in paths:
            report["files"] += 1
            stat = path.stat()
            seen = checkpoints.get(str(path))
            if seen and [*seen[:2], *seen[3:]] == [stat.st_size, stat.st_mtime_ns, PARSER_VERSION]:
                report["unchanged_files"] += 1
                report["malformed_lines"] += seen[2]  # still reported, never silent
                continue
            entries, malformed = parse_session(path)
            report["malformed_lines"] += malformed
            for session_id in {entry.session_id for entry in entries}:
                target = state / "entries" / f"{session_id}.json"
                stored = _ENTRIES.validate_json(target.read_bytes()) if target.exists() else []
                known = {entry.entry_id: entry for entry in stored}
                # A re-read entry replaces the stored one, so a call gets a result that came later.
                merged = known | {e.entry_id: e for e in entries if e.session_id == session_id}
                target.write_bytes(_ENTRIES.dump_json(list(merged.values())))
                report["new_entries"] += len(merged) - len(known)
            # Only now: a checkpoint before its entries would hide a failed write for ever.
            checkpoints[str(path)] = [stat.st_size, stat.st_mtime_ns, malformed, PARSER_VERSION]
    finally:
        checkpoint_file.write_bytes(_CHECKPOINTS.dump_json(checkpoints))
    return report
