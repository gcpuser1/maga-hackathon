"""BUILD: two independent model calls from one approved Contract.

Call A writes the acceptance tests and sees the contract only.
Call B writes the script and the skill. A revision repeats call B only, so the tests stay fixed.
"""

from hashlib import sha256
import json
from pathlib import Path

from pydantic import BaseModel, field_validator
from pydantic_ai.models import Model

from maga import llm
from maga.schemas import Contract, Package

# The repository constraints that both calls receive. Gate 1 provides exactly this harness.
CONSTRAINTS = """
Repository constraints:
- The script is `scripts/start.py`: Python 3.13, standard library only, no network beyond localhost.
- `python scripts/start.py` starts the workflow. `python scripts/start.py stop` stops only the
  process that the script started, by the PID in the tracking file of the contract.
- The working directory is the repository root. `packages/config/ports.json` holds
  {"frontend_ports": [...]}. The frontend is in `apps/web`. `vite` is on PATH; start it in
  `apps/web` as `vite --port <port> --strictPort`.
- The last line of stdout is one JSON object. Error reasons: all_permitted_ports_exhausted,
  cors_origin_rejected, precondition_failed.
Test harness (pytest fixtures that Gate 1 provides; a test must not define them):
- `repo`: Path of a fresh repository root with the files above.
- `backend`: the backend stub on http://localhost:4000. `backend.origins` lists each Origin
  header that `/api/health` received. It answers 200 for a permitted Origin and 403 otherwise.
- `occupy(port)`: binds the port with an unrelated listener and returns its socket.
- `run(*args)`: runs the script under test in `repo` and returns subprocess.CompletedProcess
  with text stdout and stderr. Never import the script and never read its source.
"""
_TESTS = (
    "Write one pytest module of acceptance tests for the contract in the data. "
    "Write one test for each acceptance check, and one for each invariant that a test can observe. "
    "A script that does nothing, and a script that skips a postcondition, must fail the module. "
    "Test the contract only, never an implementation detail." + CONSTRAINTS
)
_SCRIPT = (
    "Write the script and the SKILL.md for the contract in the data. "
    "SKILL.md starts with YAML front matter that has `name` and `description`; the description says "
    "when an agent must use the skill, and the body tells the agent to run the script and never "
    "to start the tool directly. If the data has a `gate_failure`, repair the script or the skill. "
    "The contract is fixed." + CONSTRAINTS
)


def _python(code: str) -> str:
    try:
        compile(code, "<generated>", "exec")
    except SyntaxError as error:
        message = f"the generated code is not Python: {error}"
        raise ValueError(message) from error
    return code


class Tests(BaseModel):
    test_code: str
    _is_python = field_validator("test_code")(_python)


class Script(BaseModel):
    script: str
    skill_md: str
    _is_python = field_validator("script")(_python)

    @field_validator("skill_md")
    @classmethod
    def _has_front_matter(cls, text: str) -> str:
        head = text.split("---")[1] if text.startswith("---") and text.count("---") > 1 else ""
        if "name:" not in head or "description:" not in head:
            message = "SKILL.md needs front matter with name and description"
            raise ValueError(message)
        return text


def approved_contract(state: Path, candidate_id: str) -> Contract:
    """The contract, only when a person approved exactly this text (AGENTS.md 2.4)."""
    approval = json.loads((state / "approvals" / f"{candidate_id}.json").read_text())
    text = (state / "contracts" / f"{candidate_id}.json").read_text()
    if (
        not approval["approved"]
        or approval["contract_sha256"] != sha256(text.encode()).hexdigest()
    ):
        message = f"no human approval for this exact contract of {candidate_id}"
        raise PermissionError(message)
    return Contract.model_validate_json(text)


def write_tests(contract: Contract, staged: Path, model: Model | str = llm.MODEL) -> None:
    answer = llm.ask(Tests, _TESTS, contract.model_dump_json(), model)
    (staged / "tests").mkdir(parents=True, exist_ok=True)
    (staged / "tests" / "test_start.py").write_text(answer.test_code)


def write_script(
    contract: Contract, staged: Path, gate_failure: str = "", model: Model | str = llm.MODEL
) -> Package:
    data = {"contract": contract.model_dump(mode="json")} | (
        {"gate_failure": gate_failure} if gate_failure else {}
    )
    answer = llm.ask(Script, _SCRIPT, json.dumps(data), model)
    (staged / "scripts").mkdir(parents=True, exist_ok=True)
    (staged / "scripts" / "start.py").write_text(answer.script)
    (staged / "SKILL.md").write_text(answer.skill_md)
    return Package(
        candidate_id=contract.candidate_id,
        script_path=str(staged / "scripts" / "start.py"),
        skill_path=str(staged / "SKILL.md"),
        test_path=str(staged / "tests" / "test_start.py"),
        contract=contract,
    )
