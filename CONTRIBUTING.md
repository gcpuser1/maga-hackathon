# Contributing

This is a hackathon repository.
The rules here are short on purpose.
They keep the demo code small, tested, and free of secrets.

## Setup, once

```bash
bash scripts/setup-tools.sh
```

The script installs `uv`, `just`, and `gitleaks` when they are absent.
It installs the locked Python environment and the git hooks.
Run `just` to list the recipes.

## Commands

| Command | What it does |
| --- | --- |
| `just fix` | Apply the automatic lint fixes, then format. |
| `just lint` | Fail on formatter drift or a Ruff finding. All Ruff rules are on. |
| `just typecheck` | Pyright in strict mode. |
| `just test` | pytest. An empty suite fails. |
| `just check` | The lock check, then `lint`, `typecheck`, and `test`. |
| `just preflight` | `check`, the suppression gate, and the secret scan, on a clean checkout of `HEAD`. |

Each command runs through `uv run --locked`, so each person runs the same tool versions.

## Git hooks

The hooks call the same `just` recipes.

- **On commit:** `just fix`, `just check`, `just suppressions`, and `just secrets-staged`.
- **On commit message:** the message must be a conventional commit.
- **On push:** `just preflight`.

`just preflight` runs all tests and all linting on the commit that you push.
It refuses a dirty working tree, before the gates and again after them.
The gates read files, and the push sends commits.
A pass on uncommitted files says nothing about the pushed commit.
Commit or stash first, then push.

Never use `--no-verify`.
Fix the finding.

## Suppressions

Do not add `# noqa`, `# type: ignore`, or `# pyright:` comments.
The `suppressions` gate rejects each new one in a Python file.
Fix the finding.
If a rule is wrong for a whole directory, add a per-file ignore with a reason to `pyproject.toml`.
A reviewer sees it there.

## What never enters this repository

This repository is public.

- Raw session transcripts. `.gitignore` excludes `*.jsonl`, `transcripts/`, `data/`, and `.maga/`.
- Credentials, tokens, and `.env` files. gitleaks scans each commit and each push.
- Text copied from a private repository.

Test fixtures are synthetic.
Only `tests/fixtures/` and `src/maga/fixtures/` can hold a `.jsonl` file.

## Commit format

```text
<type>: <description>
```

The types are `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`, `style`, and `revert`.
A scope is optional.

```text
feat: count repeated command sequences across sessions
fix: keep a tool call with its result at a chunk boundary
```

## Pull request format

A PR title follows the commit format.
A PR body has these headings, in this order, with nothing above `## Problem`.
The PR template supplies them.

- `## Problem`: what is wrong now, with the evidence. Not "improve X".
- `## Change`: what the branch delivers, and the reason for each decision that is not obvious.
- `## Verification`: the commands you ran and what they printed.
  Include before and after evidence.
  A claim with no observed result is not verification.

Report only what you observed.
If a gate did not run, say so.
State what you left out and why.

### Write the PR description in the present tense

A PR description tells the reader what the branch delivers.
Write it as if the code was always in this state.
Do not write the history of the branch.
Remove phase numbers, progress tables, and the words "now", "no longer", and "previously".
Update the description when the branch changes.

### Write plainly

- Use the active voice and short sentences.
- Give one instruction in each sentence.
- Do not use an em dash.
- Do not change technical names: write file paths, field names, and commands as they are.
