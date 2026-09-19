# MAGA

Coding agents repeatedly pay to rediscover the same project-specific fixes. Our background agent finds those repeated corrections in session transcripts, checks the evidence, and turns them into tested scripts and skills, and proposes them for human review.

## Development

```bash
bash scripts/setup-tools.sh   # once: tools, locked environment, git hooks
just check                    # lock check, Ruff, Pyright strict, pytest
```

Read `CONTRIBUTING.md` for the hooks and the PR format, and `AGENTS.md` for the agent workflow.
`llms.txt` indexes the documentation.
