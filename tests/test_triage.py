"""DECIDE against recorded model responses: one outcome, a validated contract, an approval."""

import json
from pathlib import Path

from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart, UserPromptPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
import pytest

from maga.schemas import Candidate
from maga.triage import GOLDEN, Decision, decide, existing_tools, record

CANDIDATE = Candidate.model_validate(
    {
        "candidate_id": "cand_vite_strict_port_001",
        "title": "kill -9 <PID>",
        "command_sequence": ["export API_KEY=" + "FAKE_SECRET_VALUE_001" + " && kill -9 4242"],
        "normalized_template": "kill -9 <PID>",
        "frequency": 3,
        "evidence_type": "correction",
        "evidence": {
            "session_ids": ["sess-u1", "sess-u2", "sess-u3"],
            "observed_occurrences": 3,
            "observed_turns_mean": 1.0,
            "observed_tokens_mean": 0,
            "common_pitfalls": ["don't kill that process"],
        },
    }
)
GENERATE: dict[str, object] = {
    "outcome": "generate",
    "reason": "stable procedure",
    "contract": json.loads(GOLDEN),
}


def _recorded(answer: dict[str, object], seen: list[str]) -> FunctionModel:
    def respond(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        parts = [part for message in messages for part in message.parts]
        prompts = [part.content for part in parts if isinstance(part, UserPromptPart)]
        seen.append("\n".join([str(info.instructions), *map(str, prompts)]))
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, answer)])

    return FunctionModel(respond)


def test_generate_returns_the_contract_and_the_request_is_redacted_data() -> None:
    seen: list[str] = []
    decision = decide(CANDIDATE, ["justfile recipe: check"], _recorded(GENERATE, seen))
    assert decision.contract is not None
    assert decision.contract.workflow_name == "vite-safe-dev-server"
    (request,) = seen
    assert "don't kill that process" in request  # TT-COR-004: the correction reaches DECIDE
    assert "justfile recipe: check" in request
    assert "FAKE_SECRET_VALUE_001" not in request
    assert "[REDACTED_SECRET]" in request


@pytest.mark.parametrize(
    "answer",
    [
        {"outcome": "generate", "reason": "no contract"},
        {"outcome": "rejected", "reason": "has a contract", "contract": json.loads(GOLDEN)},
        {"outcome": "automate", "reason": "unknown outcome"},
        {
            **GENERATE,
            "contract": {k: v for k, v in json.loads(GOLDEN).items() if k != "invariants"},
        },
    ],
)
def test_an_invalid_model_answer_is_an_error_not_a_decision(answer: dict[str, object]) -> None:
    with pytest.raises(UnexpectedModelBehavior):
        decide(CANDIDATE, [], _recorded(answer, []))


def test_a_contract_for_another_candidate_is_refused() -> None:
    other = CANDIDATE.model_copy(update={"candidate_id": "cand_other"})
    with pytest.raises(ValueError, match="cand_vite_strict_port_001, not cand_other"):
        decide(other, [], _recorded(GENERATE, []))


@pytest.mark.parametrize(("approved", "status"), [(True, "accepted"), (False, "rejected")])
def test_the_approval_is_recorded_and_only_an_approved_contract_is_stored(
    tmp_path: Path, *, approved: bool, status: str
) -> None:
    approval = record(tmp_path, CANDIDATE, Decision.model_validate(GENERATE), approved=approved)
    stored = json.loads(approval.read_text())
    assert approval == tmp_path / "approvals" / "cand_vite_strict_port_001.json"
    assert (stored["approved"], stored["outcome"]) == (approved, "generate")
    assert len(stored["contract_sha256"]) == 64
    assert (tmp_path / "contracts" / "cand_vite_strict_port_001.json").exists() is approved
    candidate = json.loads(
        (tmp_path / "candidates" / "cand_vite_strict_port_001.json").read_text()
    )
    assert candidate["triage_status"] == status


def test_an_outcome_with_no_contract_needs_no_approval(tmp_path: Path) -> None:
    decision = Decision(outcome="fix_at_source", reason="the port list is wrong in the config")
    record(tmp_path, CANDIDATE, decision, approved=False)
    candidate = json.loads(
        (tmp_path / "candidates" / "cand_vite_strict_port_001.json").read_text()
    )
    assert candidate["triage_status"] == "fix_at_source"
    assert not (tmp_path / "contracts").exists()


def test_existing_tools_lists_names_and_no_file_contents(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"scripts": {"dev": "vite --port 5173 --strictPort"}}')
    (tmp_path / "justfile").write_text(
        "base := 'x'\n\n[doc('Run')]\ncheck: lint\n    ruff check\n"
    )
    (tmp_path / ".claude/skills/start-web").mkdir(parents=True)
    (tmp_path / ".claude/scripts").mkdir()
    (tmp_path / ".claude/scripts/pr-loc.sh").write_text("#!/bin/sh\n")
    assert existing_tools(tmp_path, tmp_path) == [
        "package.json script: dev",
        "justfile recipe: check",
        "skill: start-web",
        "skill: start-web",
        "user script: pr-loc.sh",
    ]
