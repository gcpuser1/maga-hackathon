#!/usr/bin/env bash
# Prepare a fresh checkout: tools, the locked environment, and the git hooks.
# Safe to run again.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

need() { command -v "$1" > /dev/null 2>&1; }

need uv || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
need just || uv tool install rust-just
if ! need gitleaks; then
  if need brew; then
    brew install gitleaks
  else
    echo "Install gitleaks: https://github.com/gitleaks/gitleaks#installing" >&2
    exit 1
  fi
fi

uv sync --locked
uv run --locked pre-commit install \
  --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

echo 'Setup complete. Run "just" to list the recipes.'
