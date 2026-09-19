# Agent Workflow for MAGA (Mining Agent Generated Automation)

This document governs coding agent development within the MAGA repository (`ufs-lab/maga-hackathon`). Every task moves through the four beats below, backed by installed agent skills (`~/.gemini/config/skills/`).

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
  - Run the unit test suite: `pytest tests/ -v` (or `uv run pytest`).
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

```bash
# Run MAGA test suite
pytest tests/ -v
# Or with uv
uv run pytest

# Check code formatting & types
ruff check .
mypy maga/

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
