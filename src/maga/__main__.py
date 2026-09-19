"""`python -m maga <stage>`. Exit 0 pass, 1 fail, 2 usage."""

import argparse
import json
from pathlib import Path
import sys

from pydantic_ai.exceptions import UserError

from maga import finder, reader, triage
from maga.schemas import Candidate

STATE = Path(".maga/state")


def main() -> int:
    parser = argparse.ArgumentParser(prog="maga")
    stages = parser.add_subparsers(dest="stage", required=True)
    read = stages.add_parser("read", help="import Claude Code session files")
    read.add_argument("paths", nargs="*", type=Path, help="default: ~/.claude/projects/*/*.jsonl")
    stages.add_parser("find", help="rank the repeated procedures in the stored entries")
    decide = stages.add_parser("decide", help="triage one candidate and ask for contract approval")
    decide.add_argument("candidate_id")
    args = parser.parse_args()

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
