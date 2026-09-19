"""TT-SCH: the seven Pydantic models of ARCHITECTURE.md 7.1 and the golden contract of 7.2."""

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError
import pytest

from maga import schemas
from maga.schemas import Candidate, Contract, Entry, Episode, Evidence, Package, Verdict

GOLDEN: dict[str, Any] = json.loads(
    (Path(schemas.__file__).parent / "fixtures" / "golden_contract.json").read_text()
)
TS = "2026-01-05T10:00:06Z"
ENTRY: dict[str, Any] = {
    "entry_id": "e1",
    "session_id": "sess-a",
    "step_index": 0,
    "source": "user",
    "entry_type": "user_input",
    "timestamp": TS,
}
EVIDENCE: dict[str, Any] = {
    "session_ids": ["sess-a", "sess-b", "sess-c"],
    "observed_occurrences": 3,
    "observed_turns_mean": 4.0,
    "observed_tokens_mean": 1200,
}
MINIMAL: dict[type[BaseModel], dict[str, Any]] = {
    Entry: ENTRY,
    Episode: {
        "episode_id": "ep1",
        "session_id": "sess-a",
        "goal": "start the web frontend",
        "entries": [ENTRY],
        "success": True,
    },
    Evidence: EVIDENCE,
    Candidate: {
        "candidate_id": "cand-1",
        "title": "Start Vite",
        "command_sequence": ["pnpm dev"],
        "normalized_template": "pnpm dev",
        "frequency": 3,
        "evidence_type": "repetition",
        "evidence": EVIDENCE,
    },
    Contract: GOLDEN,
    Package: {
        "candidate_id": "cand-1",
        "script_path": "scripts/start.py",
        "skill_path": "SKILL.md",
        "test_path": "tests/test_start.py",
        "contract": GOLDEN,
    },
    Verdict: {
        "candidate_id": "cand-1",
        "gate_number": 1,
        "outcome": "pass",
        "total_revisions": 0,
        "test_results": {},
        "stdout_log": "",
        "stderr_log": "",
        "execution_duration_ms": 10,
        "timestamp": TS,
    },
}
# Every optional field set, for the round trip (TT-SCH-014).
FULL: dict[type[BaseModel], dict[str, Any]] = {
    **MINIMAL,
    Entry: {
        **ENTRY,
        "tool_name": "Bash",
        "command_line": "git status",
        "working_dir": "/repo",
        "args": {"command": "git status", "timeout": 5000, "run_in_background": True},
        "exit_code": 0,
        "content": "text",
        "sanitized_output": "clean",
        "tokens_in": 10,
        "tokens_out": 20,
    },
    Episode: {**MINIMAL[Episode], "repair_iterations": 2, "duration_ms": 900},
    Evidence: {**EVIDENCE, "failure_traces": ["trace-1"], "common_pitfalls": ["port 5175"]},
    Candidate: {**MINIMAL[Candidate], "triage_status": "rejected", "rejection_reason": "unsafe"},
    Verdict: {**MINIMAL[Verdict], "token_delta_percent": -41.5},
}
REQUIRED = [
    (model, field)
    for model, minimal in MINIMAL.items()
    for field in minimal
    if model.model_fields[field].is_required()
]


def _fails(model: type[BaseModel], minimal: dict[str, Any], **changes: object) -> ValidationError:
    with pytest.raises(ValidationError) as caught:
        model.model_validate({**minimal, **changes})
    return caught.value


def _locations(error: ValidationError) -> list[str]:
    return [".".join(str(part) for part in item["loc"]) for item in error.errors()]


def test_sch_001_each_model_accepts_its_minimal_object() -> None:
    entry = Entry.model_validate(ENTRY)
    assert entry.model_dump(exclude={*ENTRY}) == dict.fromkeys(
        set(Entry.model_fields) - set(ENTRY)
    )
    episode = Episode.model_validate(MINIMAL[Episode])
    assert (episode.repair_iterations, episode.duration_ms) == (0, 0)
    evidence = Evidence.model_validate(EVIDENCE)
    assert (evidence.failure_traces, evidence.common_pitfalls) == ([], [])
    candidate = Candidate.model_validate(MINIMAL[Candidate])
    assert (candidate.triage_status, candidate.rejection_reason) == ("pending", None)
    assert Verdict.model_validate(MINIMAL[Verdict]).token_delta_percent is None
    Contract.model_validate(GOLDEN)
    Package.model_validate(MINIMAL[Package])


def test_sch_002_the_required_field_list_is_the_documented_one() -> None:
    assert len(REQUIRED) == 47


@pytest.mark.parametrize(("model", "field"), REQUIRED, ids=lambda v: getattr(v, "__name__", v))
def test_sch_002_each_required_field_is_required(model: type[BaseModel], field: str) -> None:
    minimal = {key: value for key, value in MINIMAL[model].items() if key != field}
    assert _locations(_fails(model, minimal)) == [field]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source", "assistant"),
        ("source", "human"),
        ("entry_type", "tool_use"),
        ("entry_type", "message"),
        ("step_index", "first"),
        ("exit_code", "ok"),
        ("timestamp", "yesterday"),
    ],
)
def test_sch_003_004_entry_rejects_bad_enums_and_types(field: str, value: str) -> None:
    assert _locations(_fails(Entry, ENTRY, **{field: value})) == [field]


def test_sch_005_evidence_list_defaults_are_not_shared() -> None:
    first, second = Evidence.model_validate(EVIDENCE), Evidence.model_validate(EVIDENCE)
    first.failure_traces.append("trace-1")
    assert second.failure_traces == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("triage_status", "reuse"),
        ("triage_status", "generate"),
        ("triage_status", "CONTRACTED"),
        ("triage_status", "approved"),
        ("evidence_type", "error-fix"),
        ("evidence_type", "user_correction"),
        ("evidence_type", "plain"),
    ],
)
def test_sch_006_candidate_rejects_unknown_enum_values(field: str, value: str) -> None:
    assert _locations(_fails(Candidate, MINIMAL[Candidate], **{field: value})) == [field]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        *[
            ("triage_status", status)
            for status in (
                "pending",
                "accepted",
                "reuse_existing",
                "fix_at_source",
                "rejected",
                "clarification_needed",
            )
        ],
        *[("evidence_type", kind) for kind in ("correction", "error_fix", "repetition")],
    ],
)
def test_sch_006_candidate_accepts_the_documented_enum_values(field: str, value: str) -> None:
    assert getattr(Candidate.model_validate({**MINIMAL[Candidate], field: value}), field) == value


def test_sch_007_candidate_validates_its_nested_evidence() -> None:
    error = _fails(Candidate, MINIMAL[Candidate], evidence={**EVIDENCE, "session_ids": "sess-a"})
    assert _locations(error) == ["evidence.session_ids"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("preconditions", "Node.js is installed"),
        ("acceptance_checks", None),
        ("inputs", ["apps/web"]),
        ("rerun_behaviour", ["return the existing PID"]),
    ],
)
def test_sch_008_contract_rejects_wrong_field_types(field: str, value: object) -> None:
    assert _locations(_fails(Contract, GOLDEN, **{field: value})) == [field]


def test_sch_009_the_golden_contract_keeps_its_values() -> None:
    contract = Contract.model_validate(GOLDEN)
    assert contract.candidate_id == "cand_vite_strict_port_001"
    assert contract.workflow_name == "vite-safe-dev-server"
    assert contract.inputs == {
        "app_dir": "apps/web",
        "permitted_ports": [5173, 5174],
        "backend_health_url": "http://localhost:4000/api/health",
        "timeout_seconds": 15,
    }
    for group in ("preconditions", "permitted_changes", "postconditions", "invariants"):
        assert len(getattr(contract, group)) == 3
    assert [check[:6] for check in contract.acceptance_checks] == [
        "Case A",
        "Case B",
        "Case C",
        "Case D",
    ]


def test_sch_010_automation_contract_is_contract() -> None:
    assert schemas.AutomationContract is Contract


def test_sch_011_package_validates_its_nested_contract() -> None:
    broken = deepcopy(GOLDEN)
    del broken["failure_behaviour"]
    error = _fails(Package, MINIMAL[Package], contract=broken)
    assert _locations(error) == ["contract.failure_behaviour"]


@pytest.mark.parametrize("gate_number", [0, 3, None])
def test_sch_012_verdict_rejects_other_gate_numbers(gate_number: int | None) -> None:
    assert _locations(_fails(Verdict, MINIMAL[Verdict], gate_number=gate_number)) == [
        "gate_number"
    ]


@pytest.mark.parametrize("outcome", ["passed", "PASS", "error", "skipped", "unverified"])
def test_sch_013_verdict_rejects_other_outcomes(outcome: str) -> None:
    assert _locations(_fails(Verdict, MINIMAL[Verdict], outcome=outcome)) == ["outcome"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("gate_number", 1),
        ("gate_number", 2),
        *[("outcome", o) for o in ("pass", "fail", "inconclusive")],
    ],
)
def test_sch_012_013_verdict_accepts_the_documented_values(field: str, value: object) -> None:
    assert getattr(Verdict.model_validate({**MINIMAL[Verdict], field: value}), field) == value


@pytest.mark.parametrize("model", list(FULL), ids=lambda m: m.__name__)
def test_sch_014_each_model_survives_a_json_round_trip(model: type[BaseModel]) -> None:
    first = model.model_validate(FULL[model])
    assert model.model_validate_json(first.model_dump_json()) == first
    assert set(FULL[model]) == set(model.model_fields)


def test_sch_014_the_round_trip_keeps_the_instant_and_the_arg_types() -> None:
    entry = Entry.model_validate_json(Entry.model_validate(FULL[Entry]).model_dump_json())
    assert entry.timestamp.utcoffset() is not None
    assert entry.timestamp.isoformat() == "2026-01-05T10:00:06+00:00"
    assert entry.args is not None
    assert entry.args["timeout"] == 5000
    assert isinstance(entry.args["timeout"], int)
    assert entry.args["run_in_background"] is True
