"""BUILD against recorded responses: two independent calls, and approval before either."""

from hashlib import sha256
import json
from pathlib import Path

from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart, UserPromptPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
import pytest

from maga.generator import approved_contract, write_script, write_tests
from maga.schemas import Contract
from maga.triage import GOLDEN

CONTRACT = Contract.model_validate_json(GOLDEN)
SKILL = (
    "---\nname: vite-safe-dev-server\ndescription: Use to start the web frontend.\n---\nRun it.\n"
)
SCRIPT = {"script": "print('SCRIPT_MARKER')\n", "skill_md": SKILL}


def _recorded(answer: dict[str, str], seen: list[str]) -> FunctionModel:
    def respond(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        parts = [part for message in messages for part in message.parts]
        prompts = [str(part.content) for part in parts if isinstance(part, UserPromptPart)]
        seen.append("\n".join([str(info.instructions), *prompts]))
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, answer)])

    return FunctionModel(respond)


def test_ind_the_test_call_sees_the_contract_only_and_a_revision_keeps_the_tests(
    tmp_path: Path,
) -> None:
    test_requests: list[str] = []
    script_requests: list[str] = []
    script_model = _recorded(SCRIPT, script_requests)
    write_script(CONTRACT, tmp_path, model=script_model)  # the script exists before call A runs
    write_tests(
        CONTRACT, tmp_path, _recorded({"test_code": "def test_a(): pass\n"}, test_requests)
    )
    tests_before = (tmp_path / "tests" / "test_start.py").read_text()
    package = write_script(CONTRACT, tmp_path, "GATE_LOG: Case C failed", script_model)

    assert len(test_requests) == 1
    assert "Must NOT bind unpermitted ports" in test_requests[0]
    assert "SCRIPT_MARKER" not in test_requests[0]
    assert "GATE_LOG" not in test_requests[0]
    assert "GATE_LOG: Case C failed" in script_requests[1]
    assert "GATE_LOG" not in script_requests[0]
    assert (tmp_path / "tests" / "test_start.py").read_text() == tests_before
    assert Path(package.script_path).read_text() == SCRIPT["script"]
    assert Path(package.skill_path).read_text() == SKILL
    assert package.contract == CONTRACT


@pytest.mark.parametrize(
    "answer",
    [
        {**SCRIPT, "script": "def broken(:\n"},
        {**SCRIPT, "skill_md": "Run the script."},
        {**SCRIPT, "skill_md": "---\nname: x\n---\nno description\n"},
    ],
)
def test_a_script_answer_that_is_not_usable_is_refused(
    tmp_path: Path, answer: dict[str, str]
) -> None:
    with pytest.raises(UnexpectedModelBehavior):
        write_script(CONTRACT, tmp_path, model=_recorded(answer, []))
    assert not (tmp_path / "scripts").exists()


def _state(tmp_path: Path, *, approved: bool, text: str = GOLDEN) -> Path:
    for folder in ("approvals", "contracts"):
        (tmp_path / folder).mkdir(parents=True)
    approval = {"approved": approved, "contract_sha256": sha256(GOLDEN.encode()).hexdigest()}
    (tmp_path / "approvals" / f"{CONTRACT.candidate_id}.json").write_text(json.dumps(approval))
    (tmp_path / "contracts" / f"{CONTRACT.candidate_id}.json").write_text(text)
    return tmp_path


def test_build_needs_a_human_approval_of_this_exact_contract(tmp_path: Path) -> None:
    assert (
        approved_contract(_state(tmp_path / "a", approved=True), CONTRACT.candidate_id) == CONTRACT
    )
    with pytest.raises(PermissionError):
        approved_contract(_state(tmp_path / "b", approved=False), CONTRACT.candidate_id)
    edited = GOLDEN.replace("5175+", "5199+")
    with pytest.raises(PermissionError):
        approved_contract(
            _state(tmp_path / "c", approved=True, text=edited), CONTRACT.candidate_id
        )
