"""`python -m maga <stage>`. Exit 0 pass, 1 fail, 2 usage."""

import argparse
import json
from pathlib import Path
import sys

from pydantic_ai.exceptions import UserError

from maga import finder, gate2, generator, reader, triage, verifier
from maga.schemas import Candidate, Package, Verdict

STATE = Path(".maga/state")
STAGED = Path(".maga/artifacts/staged")


def main() -> int:
    parser = argparse.ArgumentParser(prog="maga")
    stages = parser.add_subparsers(dest="stage", required=True)
    read = stages.add_parser("read", help="import Claude Code session files")
    read.add_argument("paths", nargs="*", type=Path, help="default: ~/.claude/projects/*/*.jsonl")
    stages.add_parser("find", help="rank the repeated procedures in the stored entries")
    decide = stages.add_parser("decide", help="triage one candidate and ask for contract approval")
    decide.add_argument("candidate_id")
    build = stages.add_parser("build", help="generate tests, script, and skill from the contract")
    build.add_argument("candidate_id")
    check = stages.add_parser("check", help="Gate 1: acceptance tests in a container, no network")
    check.add_argument("candidate_id")
    reuse = stages.add_parser(
        "gate2", help="Gate 2: 5 fresh agent runs must find and use the skill"
    )
    reuse.add_argument("candidate_id")
    reuse.add_argument("demo_repo", type=Path, nargs="?", default=Path("fixtures/demo-monorepo"))
    args = parser.parse_args()

    if args.stage == "gate2":
        return _gate2(args.candidate_id, args.demo_repo)

    if args.stage == "check":
        return _check(args.candidate_id)

    if args.stage == "build":
        return _build(args.candidate_id)

    if args.stage == "decide":
        return _decide(args.candidate_id)

    if args.stage == "find":
        candidates = finder.run(STATE)
        for place, c in enumerate(candidates[:10], 1):
            sys.stdout.write(
                f"{place:>2}. {c.evidence_type:<10} sessions={c.frequency:<3} "
                f"occurrences={c.evidence.observed_occurrences:<4} {c.candidate_id}\n"
                + "".join(f"      {line[:150]}\n" for line in c.normalized_template.splitlines())
            )
        sys.stdout.write(f"{len(candidates)} candidates in {STATE / 'candidates'}\n")
        return 0 if candidates else 1
    paths = args.paths or sorted((Path.home() / ".claude/projects").glob("*/*.jsonl"))
    report = reader.read(paths, STATE)
    sys.stdout.write(json.dumps(report) + "\n")
    return 0 if report["files"] else 1


def _build(candidate_id: str) -> int:
    try:
        contract = generator.approved_contract(STATE, candidate_id)
        generator.write_tests(contract, STAGED / candidate_id)
        package = generator.write_script(contract, STAGED / candidate_id)
    except (FileNotFoundError, PermissionError, UserError) as error:
        sys.stderr.write(f"{error}\n")
        return 1
    sys.stdout.write(package.model_dump_json(indent=2, exclude={"contract"}) + "\n")
    return 0


def _check(candidate_id: str) -> int:
    staged = STAGED / candidate_id

    def revise(gate_failure: str) -> Package:
        # The approval is read again for each revision, so an edited contract ends the loop.
        contract = generator.approved_contract(STATE, candidate_id)
        return generator.write_script(contract, staged, gate_failure)

    try:
        verdict = verifier.check(_package(candidate_id), STATE, revise)
    except (FileNotFoundError, PermissionError, UserError) as error:
        sys.stderr.write(f"{error}\n")
        return 1
    sys.stdout.write(verdict.model_dump_json(indent=2, exclude={"stdout_log"}) + "\n")
    if verdict.outcome != "pass":
        sys.stdout.write(verdict.stdout_log[-2000:] + "\n")
    return 0 if verdict.outcome == "pass" else 1


def _package(candidate_id: str) -> Package:
    staged = STAGED / candidate_id
    return Package(
        candidate_id=candidate_id,
        script_path=str(staged / "scripts" / "start.py"),
        skill_path=str(staged / "SKILL.md"),
        test_path=str(staged / "tests" / "test_start.py"),
        contract=generator.approved_contract(STATE, candidate_id),
    )


def _gate2(candidate_id: str, demo_repo: Path) -> int:
    gate1 = STATE / "verification" / f"{candidate_id}_verdict.json"
    if not gate1.exists() or Verdict.model_validate_json(gate1.read_bytes()).outcome != "pass":
        sys.stderr.write(
            f"Gate 2 needs a Gate 1 pass in {gate1}; run `python -m maga check` first\n"
        )
        return 1
    try:
        verdict = gate2.gate2_verdict(_package(candidate_id), demo_repo, gate2.claude_runner, 0)
    except (FileNotFoundError, PermissionError) as error:
        sys.stderr.write(f"{error}\n")
        return 1
    target = STATE / "verification" / f"{candidate_id}_gate2_verdict.json"
    target.write_text(verdict.model_dump_json(indent=2))
    sys.stdout.write(verdict.model_dump_json(indent=2) + "\n")
    return 0 if verdict.outcome == "pass" else 1


def _decide(candidate_id: str) -> int:
    path = STATE / "candidates" / f"{candidate_id}.json"
    if not path.exists():
        sys.stderr.write(f"no candidate at {path}; run `python -m maga find` first\n")
        return 2
    candidate = Candidate.model_validate_json(path.read_bytes())
    try:
        decision = triage.decide(candidate, triage.existing_tools(Path.cwd(), Path.home()))
    except UserError as error:  # no API key: Pydantic AI names the variable it needs
        sys.stderr.write(f"{error}\n")
        return 1
    sys.stdout.write(f"outcome: {decision.outcome}\nreason: {decision.reason}\n")
    approved = False
    if decision.contract:
        sys.stdout.write(decision.contract.model_dump_json(indent=2) + "\n")
        answer = input("Approve this contract and its acceptance checks? [y/N] ")
        approved = answer.strip().lower() == "y"
    approval = triage.record(STATE, candidate, decision, approved=approved)
    sys.stdout.write(f"recorded in {approval}\n")
    return 0 if approved else 1


if __name__ == "__main__":
    sys.exit(main())
