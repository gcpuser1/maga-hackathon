"""DECIDE: one outcome for a candidate and, for `generate`, a human-approved Contract."""

from datetime import UTC, datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Literal, Self

from pydantic import BaseModel, model_validator
from pydantic_ai.models import Model

from maga import llm, schemas
from maga.schemas import Candidate, Contract

GOLDEN = (Path(schemas.__file__).parent / "fixtures" / "golden_contract.json").read_text()
_STATUS = {
    "reuse_existing": "reuse_existing",
    "generate": "accepted",
    "fix_at_source": "fix_at_source",
    "clarify": "clarification_needed",
    "rejected": "rejected",
}
_INSTRUCTIONS = f"""You triage one repeated procedure that was mined from coding-agent sessions.
Return exactly one outcome:
- reuse_existing: a listed existing tool already does the procedure.
- fix_at_source: the repetition shows a defect to repair, not a procedure to automate.
- clarify: a safety-critical fact is missing.
- rejected: the procedure is trivial, interactive, unbounded, judgment-heavy, or unsafe to automate.
- generate: a script can do the procedure. Only then, write the contract.
A contract has verifiable postconditions, negative invariants taken from the corrections and
the failures in the evidence, and deterministic acceptance checks that run with no network.
Use the candidate_id of the candidate. This is an example of a complete contract:
{GOLDEN}"""


class Decision(BaseModel):
    outcome: Literal["reuse_existing", "generate", "fix_at_source", "clarify", "rejected"]
    reason: str
    contract: Contract | None = None

    @model_validator(mode="after")
    def _generate_needs_a_contract(self) -> Self:
        if (self.outcome == "generate") != (self.contract is not None):
            message = "a contract is required for generate, and for no other outcome"
            raise ValueError(message)
        return self


def existing_tools(repo: Path, home: Path) -> list[str]:
    """Names only: the contents of configuration files stay out of model input."""
    found: list[str] = []
    package = repo / "package.json"
    if package.exists():
        found += [
            f"package.json script: {name}"
            for name in json.loads(package.read_text()).get("scripts", {})
        ]
    for name in ("justfile", "Makefile"):
        if (repo / name).exists():
            recipes = re.findall(
                r"^([A-Za-z][\w-]*)\b[^:=\n]*:(?!=)", (repo / name).read_text(), re.MULTILINE
            )
            found += [f"{name} recipe: {recipe}" for recipe in recipes]
    for skills in (repo / ".claude/skills", home / ".claude/skills"):
        found += [f"skill: {path.name}" for path in sorted(skills.glob("*")) if path.is_dir()]
    found += [f"user script: {path.name}" for path in sorted((home / ".claude/scripts").glob("*"))]
    return found


def decide(candidate: Candidate, tools: list[str], model: Model | str = llm.MODEL) -> Decision:
    data = json.dumps({"candidate": candidate.model_dump(mode="json"), "existing_tools": tools})
    decision = llm.ask(Decision, _INSTRUCTIONS, data, model)
    if decision.contract and decision.contract.candidate_id != candidate.candidate_id:
        message = (
            f"the contract names {decision.contract.candidate_id}, not {candidate.candidate_id}"
        )
        raise ValueError(message)
    return decision


def record(
    state: Path,
    candidate: Candidate,
    decision: Decision,
    *,
    approved: bool,
    approved_by: Literal["person", "automatic"] = "person",
) -> Path:
    """Store the outcome, the approval, and (only when approved) the contract.

    `approved_by` tells the truth about the approval: `automatic` means that no person saw it.
    """
    contract_json = decision.contract.model_dump_json(indent=2) if decision.contract else None
    status = _STATUS[decision.outcome] if approved or not decision.contract else "rejected"
    reason = decision.reason if approved or not decision.contract else "contract not approved"
    updated = candidate.model_copy(update={"triage_status": status, "rejection_reason": reason})
    (state / "candidates").mkdir(parents=True, exist_ok=True)
    (state / "candidates" / f"{candidate.candidate_id}.json").write_text(
        updated.model_dump_json(indent=2)
    )
    approval = state / "approvals" / f"{candidate.candidate_id}.json"
    approval.parent.mkdir(parents=True, exist_ok=True)
    approval.write_text(
        json.dumps(
            {
                "candidate_id": candidate.candidate_id,
                "outcome": decision.outcome,
                "approved": approved,
                "approved_by": approved_by,
                "contract_sha256": sha256(contract_json.encode()).hexdigest()
                if contract_json
                else None,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )
    )
    if approved and contract_json:
        (state / "contracts").mkdir(parents=True, exist_ok=True)
        (state / "contracts" / f"{candidate.candidate_id}.json").write_text(contract_json)
    return approval
