"""`python -m maga <stage>`. Exit 0 pass, 1 fail, 2 usage."""

import argparse
import json
from pathlib import Path
import sys

from maga import finder, reader

STATE = Path(".maga/state")


def main() -> int:
    parser = argparse.ArgumentParser(prog="maga")
    stages = parser.add_subparsers(dest="stage", required=True)
    read = stages.add_parser("read", help="import Claude Code session files")
    read.add_argument("paths", nargs="*", type=Path, help="default: ~/.claude/projects/*/*.jsonl")
    stages.add_parser("find", help="rank the repeated procedures in the stored entries")
    args = parser.parse_args()

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


if __name__ == "__main__":
    sys.exit(main())
