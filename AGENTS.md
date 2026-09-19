# Agent Workflow for MAGA (Mining Agent Generated Automation)

This document governs coding agent development within the MAGA repository (`ufs-lab/maga-hackathon`). Every task moves through the four beats below, backed by installed agent skills (`~/.gemini/config/skills/`).

---

## 0. This Is a Hackathon: Write Less Code

This repository exists for one demo at a hackathon.
It is not enterprise code.
Nobody operates it, extends it, or migrates it after the demo.
The best code is the code that you do not write.

Do not build these unless a person asks for them by name:

* Configuration systems, plugin systems, registries, or feature flags.
* An interface with one implementation, a factory for one product, or a base class with one child.
* Retry layers, caches, connection pools, metrics, or a logging framework.
* Backwards compatibility, migrations, deprecation paths, or versioned schemas.
* Scaffolding "for later", CLI options nobody requested, or a wrapper around a library that already fits.
* CI pipelines, packaging, releases, or Docker images for the product itself.

### The ladder

Understand the task and the code it touches first.
Then stop at the first rung that holds:

1. **Does this need to exist at all?** A speculative need means skip it, and say so in one line.
2. **Is it already in this repository?** Reuse the helper, type, or pattern.
3. **Does the standard library do it?** Use it.
4. **Does an installed dependency do it?** Use it. Pydantic validates, `pathlib` walks, `subprocess` runs.
   Never add a dependency for what a few lines can do.
5. **Can it be one line?** Write one line.
6. **Only then:** the minimum code that works.

### Rules for small code

* The shortest working diff wins, in the fewest files.
* Deletion over addition. Boring over clever.
* A bug fix goes in the shared function, once, at the root cause. It does not go in each caller.
* Non-trivial logic leaves one small test behind: the smallest check that fails when the logic breaks.
  A trivial one-liner needs no test.
* Mark a deliberate shortcut that has a known ceiling with a `ponytail:` comment.
  Name the ceiling and the upgrade path: `# ponytail: scans every session on each run; add a checkpoint if it gets slow`.
* After the code, write at most three short lines: what you skipped, and when to add it.
  If the explanation is longer than the code, delete the explanation.

### Where not to be lazy

Never simplify away these things:

* Secret redaction before a model call, and the rule that transcripts never enter Git.
* Pydantic validation at each boundary: transcript input, model output, and the `Contract`.
* A failure that reports itself. Never report a partial result as success.
* The hard invariants in section 2.
* Anything a person explicitly requested.

The ladder shortens the solution.
It never shortens the reading.

This section adapts the `ponytail` skill by Dietrich Gebert (MIT): <https://github.com/DietrichGebert/ponytail>.

---

## 1. The Four-Beat Workflow

```text
1. ISOLATE (/new-feature) ──> 2. BUILD (/code-structure) ──> 3. PROVE (/evidence-driven-testing) ──> 4. SHIP (/before-and-after + review)
```

### Beat 1: Isolate (`/new-feature`)
* Every feature, fix, or task starts in a clean Git worktree or task branch created from the latest `origin/main`.
* **Never build directly on `main`**.
* **Scope check:** Before writing code, inspect open pull requests (`gh pr list`) and remote branches to verify no overlapping team work.

### Beat 2: Build (`/code-structure`)
* Write modular, service-layer code conforming to the 5 MAGA pipeline stages:
  1. `maga.reader` & `maga.finder` (`FIND`): Ingestion for Claude Code (`~/.claude/projects/*/*.jsonl`) and Antigravity (`~/.gemini/.../transcript*.jsonl`), secret scrubbing, procedure repetition mining ($\ge 3$ distinct sessions), error-and-fix detection, user correction classification, and tool lookup (`package.json`, `justfile`, `~/.claude/skills/`).
  2. `maga.triage` (`TRIAGE`): Suitability assessment, contract synthesis via Pydantic AI Gateway in Logfire, and **human sign-off on Contract + acceptance checks before generation**.
  3. `maga.generator` (`BUILD`): Independent test synthesis (contract-only prompt) and parameterized script + `SKILL.md` synthesis into `.maga/artifacts/staged/`.
  4. `maga.verifier` (`CHECK`): Two-gate verification (Gate 1 zero-network contract checks + Gate 2 fresh agent reuse across 5 runs, pass $\ge 4/5$ in $\le 2$ turns).
  5. `maga.publisher` (`SHIP`): Evidence PR creation against target repositories with trace URLs and token metrics.
* Maintain strict separation: orchestration logic (triage/contract decisions) remains separated from operational mechanics (subprocesses, CLI drivers).
* Enforce schema invariants with Pydantic (`Contract`, `Entry`, `Episode`, `Candidate`, `Evidence`, `Package`, `Verdict`).
* **Independent Test Synthesis:** Test generation must be strictly decoupled from script synthesis. Acceptance checks and tests are synthesized directly from the approved `Contract` without inspecting the generated script implementation.

### Beat 3: Prove (`/evidence-driven-testing`)
* Never make unsupported claims of correctness. Back all pull requests with verifiable runtime logs:
  - Run every gate: `just check`. The pre-push hook runs `just preflight`.
  - Capture **before** evidence (reproducing a failure or unautomated baseline) and **after** evidence (verified execution output).
  - Test edge cases: missing prerequisites, resource contention, exhaustion handling, and idempotent re-runs.

### Beat 4: Ship (`/before-and-after`, then Review Loop)
* Open the pull request against `ufs-lab/maga-hackathon` (or your task fork).
* Embed concrete before/after proof in the PR description:
  - CLI execution outputs, measured latency/tokens, or Logfire trace URLs.
* When Greptile review integration is active, run `/greploop` (or `/greploop-apps` for large diffs) until resolved. If automated review bots are unavailable, execute the manual reviewer-and-correction self-audit checklist before requesting human merge.
* Present the PR URL upon completion. A human maintainer makes the final merge decision.

---

## 2. Hard Invariants & Security Rules

1. **Repository Role Separation:**
   - `ufs-lab/maga-hackathon` contains the MAGA product, evaluation harness, and documentation.
   - Demonstration subjects live in `fixtures/demo-monorepo` or designated target repos.
   - **Never submit unsolicited PRs to upstream demonstration repositories.**
2. **Secrets & State Hygiene:**
   - Raw transcripts, credentials, and local environment tokens must never be committed to Git.
   - All state is persisted as local JSON files under `.maga/state/` (gitignored).
   - Sanitize all tokens before passing transcript entries to model gateways.
3. **Execution Sandboxing Reality:**
   - Local temporary directories and worktrees provide clean checkouts, **not** OS security boundaries.
   - Local execution is unconfined host execution.
   - Formal evaluation runs inside container sandboxes: Gate 1 enforces zero external network (`--network none`); Gate 2 enforces model-API-only access without repository credentials.
4. **Human Approval Before BUILD:**
   - The candidate `Contract` and acceptance checks require explicit human approval before script generation starts.
5. **Immutable Acceptance Contracts During Repair:**
   - In automated repair loops, the acceptance contract is strictly fixed.
   - The repair loop refines the **script implementation or skill prompt**, never the contract itself.
   - A shared budget of `MAX_TOTAL_REVISIONS = 3` applies across both Gate 1 and Gate 2.
6. **Independent Test Generation:**
   - Acceptance tests evaluate contract compliance, never script idiosyncrasies.
   - Test generator prompts receive only the `Contract` and repo constraints, never the generated script.
7. **Multi-Agent Git Protocol:**
   - The active development account (`gcpuser1`) operates on fork `gcpuser1/maga-hackathon`.
   - Create PRs using `gh pr create --repo ufs-lab/maga-hackathon --head gcpuser1:<branch>`.
   - Never force-push with plain `--force`; use `--force-with-lease` only on your own branch.

---

## 3. Writing for Humans (`/unslop`)

Apply `/unslop` to all human-facing text before committing or posting:
* Commit messages, PR titles, and PR descriptions.
* Documentation, README updates, and code comments.
* Strip AI tells: em dashes, conversational filler, hedging, bold-label lists, puffery, and excessive emoji.
* Replace passive voice with direct, active phrasing.

---

## 4. Commands & Checks Reference

`just` is the only command surface, and the git hooks call the same recipes.
`CONTRIBUTING.md` has the full rules: hooks, suppressions, commit format, and PR format.

```bash
# Once, on a fresh checkout: tools, locked environment, git hooks
bash scripts/setup-tools.sh

# Apply lint fixes and format
just fix

# Lock check, Ruff (all rules), Pyright strict, pytest
just check

# Everything the pre-push hook runs, on a clean checkout of HEAD
just preflight

# Verify Antigravity CLI and discovery
agy --version
agy --help

# Pydantic Logfire authentication (when testing Gateway)
logfire auth
```

---

## 5. Skill Sources & Attribution

The development workflow skills are installed in the agent runtime environment (`~/.gemini/config/skills/`):

| Skill | Description | Upstream Source / Attribution |
| :--- | :--- | :--- |
| `new-feature` | Fresh worktree and task isolation from `origin/main` | Vendored from [michaelshimeles/skills](https://github.com/michaelshimeles/skills) |
| `code-structure` | Two-layer service architecture guidance | Vendored from [michaelshimeles/skills](https://github.com/michaelshimeles/skills) |
| `evidence-driven-testing` | Runtime evidence capture and assertion reporting | Vendored from [michaelshimeles/skills](https://github.com/michaelshimeles/skills) |
| `before-and-after` | Before/after comparison table generator | Vendored from [vercel-labs/before-and-after](https://github.com/vercel-labs/before-and-after) (PolyForm Shield 1.0.0) |
| `greploop` | Automated iterative review and fix loop | Vendored from [greptileai/skills](https://github.com/greptileai/skills) (MIT) |
| `greploop-apps` | Review loop for large PRs exceeding file limits | Vendored from [michaelshimeles/skills](https://github.com/michaelshimeles/skills) (MIT) |
| `unslop` | Edits prose to cut AI patterns and restore human register | Vendored from [cursor/plugins (pstack)](https://github.com/cursor/plugins/tree/main/pstack/skills/unslop) (MIT) |
