set shell := ["bash", "-euo", "pipefail", "-c"]

# One command surface. The git hooks call these same recipes.

py_paths := "src tests"
base := env("PREFLIGHT_BASE", "origin/main")
suppression := '#\s*(type:\s*ignore|pyright:|ruff:\s*noqa|noqa\b)'

[doc("List the recipes")]
default:
    @just --list --unsorted

[doc("Prepare a fresh checkout: tools, locked environment, git hooks")]
setup:
    bash scripts/setup-tools.sh

[doc("Apply every automatic lint fix, then format")]
fix:
    uv run --locked ruff check --fix {{ py_paths }}
    uv run --locked ruff format {{ py_paths }}

[doc("Fail on formatter drift or a lint finding (ruff, all rules)")]
lint:
    uv run --locked ruff format --check {{ py_paths }}
    uv run --locked ruff check {{ py_paths }}

[doc("Type-check (pyright strict)")]
typecheck:
    uv run --locked pyright

# pytest exits 5 when it collects no test, so an empty suite fails.
[doc("Run the tests")]
test:
    uv run --locked pytest -q

# A suppression belongs in pyproject.toml with a reason, where a reviewer sees it.
# `diff_args` is `--cached` for the staged changes, or a range such as `origin/main...HEAD`.
[doc("Fail on a new suppression comment (noqa, type: ignore, pyright:) in Python files")]
suppressions diff_args="--cached":
    @diff="$(git diff -U0 {{ diff_args }} -- '*.py')" && ! grep -nE '^\+[^+].*{{ suppression }}' <<< "$diff"

[doc("Scan the staged changes for secrets")]
secrets-staged:
    gitleaks protect --staged --redact --no-banner

[doc("Every gate that reads the working tree. The pre-commit hook runs it.")]
check:
    uv lock --check
    just lint typecheck test

# The pre-push hook. The gates read files and the push sends commits, so a dirty tree
# is refused before and after: a pass on uncommitted files describes nothing you push.
# ponytail: the gates describe HEAD only. `git push origin other-branch` is not
# detected; read PRE_COMMIT_TO_REF here if that ever matters.
[doc("Every gate, on a clean checkout of HEAD. The pre-push hook runs it.")]
preflight: _clean-tree
    git fetch --quiet origin "{{ trim_start_match(base, 'origin/') }}"
    just check
    just suppressions "{{ base }}...HEAD"
    gitleaks detect --redact --no-banner --log-opts "{{ base }}..HEAD"
    just _clean-tree
    @echo "✅ preflight green: HEAD passed every gate against {{ base }}."

# Untracked files count: a test can pass because of a module that was never added.
[private]
_clean-tree:
    @test -z "$(git status --porcelain)" || { git status --short; echo "preflight: commit or stash first, so the gates describe HEAD." >&2; exit 1; }
