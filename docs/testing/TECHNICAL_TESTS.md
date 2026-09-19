# MAGA Technical Test Specification

This file specifies the technical tests for MAGA.
A technical test checks an internal rule or a non-functional guarantee.
A coding agent implements these tests later.
This file contains specifications only.
It contains no test code and no product code.

The companion file is [FUNCTIONAL_TESTS.md](FUNCTIONAL_TESTS.md).
It covers the behaviour that a user or the demo audience can observe.

## Sources and precedence

The tests trace to these sources.

| Short name | Source |
| :--- | :--- |
| `ARCHITECTURE.md` | `docs/architecture/ARCHITECTURE.md` in this repository |
| `AGENTS.md` | `AGENTS.md` in this repository |
| here.now one-pager | `https://from-session-transcripts-to-tested-tools.ledger-rocket.here.now/one-pager.html` |
| here.now architecture | `https://from-session-transcripts-to-tested-tools.ledger-rocket.here.now/` |

`ARCHITECTURE.md` and `AGENTS.md` win when the sources disagree.
The section "Source conflicts" at the end of this file records each disagreement.
A test that has no defined expected result has the status `BLOCKED`.
A `BLOCKED` test names the open question that blocks it.

## Conventions

- "The model" means the model (Gemini) that MAGA calls when a stage needs a model to read transcript excerpts.
- "Stub model" means a test double that replaces the model.
  It returns a fixed response and it records every request that it receives.
- "Model-bound payload" means the complete request that MAGA sends to a model or to the Gateway.
- "Stub agent runner" means a test double that replaces `claude -p`.
- The six stages are `READ`, `FIND`, `DECIDE`, `BUILD`, `CHECK`, and `PROPOSE`.
- "Parametrised" means one test that runs one time for each listed case.
  Each case must report its own pass or fail result.
- The sources name the modules `maga.reader`, `maga.finder`, `maga.triage`, `maga.generator`, `maga.verifier`, `maga.publisher`, and `maga.schemas`.
  The sources name no function inside these modules (see OQ-T01).
- All field names and enum values come from `ARCHITECTURE.md` 7.1.
- The fixtures of [FUNCTIONAL_TESTS.md](FUNCTIONAL_TESTS.md) are reused by their fixture ID.
- All fixtures are synthetic.

## Coverage

| Area | ID prefix | Tests | Source sections |
| :--- | :--- | ---: | :--- |
| Pydantic schemas | `TT-SCH` | 14 | `ARCHITECTURE.md` 7.1, 7.2 |
| Transcript parsing | `TT-PAR` | 8 | `ARCHITECTURE.md` 2.1, 3.2, 5; here.now architecture "Contracts at each boundary", "Discovery, ranking, and long sessions" |
| Normalisation | `TT-NRM` | 10 | `ARCHITECTURE.md` 5.1 rule 4 |
| Sequence counting and ranking | `TT-SEQ` | 8 | `ARCHITECTURE.md` 5.1 rules 1 and 5 |
| Error-and-fix detection | `TT-EFX` | 6 | `ARCHITECTURE.md` 5.1 rule 2 |
| User-correction detection | `TT-COR` | 5 | `ARCHITECTURE.md` 3.2, 5.1 rule 3 |
| Chunking | `TT-CHK` | 6 | here.now architecture "Discovery, ranking, and long sessions" |
| Redactor | `TT-RDX` | 8 | `ARCHITECTURE.md` 10.1; here.now one-pager "Keep control" |
| State storage | `TT-STO` | 5 | `ARCHITECTURE.md` 7; `AGENTS.md` 2.2 |
| State machine | `TT-STM` | 5 | `ARCHITECTURE.md` 6 |
| Revision budget and fixed contract | `TT-REV` | 6 | `ARCHITECTURE.md` 2.2, 6; `AGENTS.md` 2.5 |
| Independent test synthesis | `TT-IND` | 3 | `ARCHITECTURE.md` 2.2; `AGENTS.md` 2.6 |
| Acceptance suite strength | `TT-ACC` | 7 | here.now one-pager "Prove it works"; `ARCHITECTURE.md` 7.2 |
| Gate 1 isolation | `TT-G1I` | 5 | `ARCHITECTURE.md` 9, 9.1 |
| Gate 2 reuse evaluation | `TT-G2R` | 9 | `ARCHITECTURE.md` 2.2, 6, 9.2 |
| Publisher | `TT-PUB` | 5 | `ARCHITECTURE.md` 2.1, 2.2 decision 2, 5 (row 6) |
| Observability | `TT-OBS` | 4 | here.now architecture "Technology choices", Pydantic Logfire |
| Resource and failure behaviour | `TT-RES` | 6 | `ARCHITECTURE.md` 7.1, 10.1; here.now architecture "Contracts at each boundary" |
| Total | | 120 | |

Five tests have the status `BLOCKED`, in full or in part: TT-PAR-004, TT-PAR-007, TT-NRM-009, TT-NRM-010, and TT-EFX-006.

## Shared synthetic fixtures

All paths are relative to the repository root.
The fixture IDs that start with `FX-CC`, `FX-GOLDEN`, `FX-DEMO`, `FX-SCRIPT`, and `FX-RUNS` are defined in [FUNCTIONAL_TESTS.md](FUNCTIONAL_TESTS.md).
This file adds these fixtures.

| Fixture ID | Intended path | Content |
| :--- | :--- | :--- |
| `FX-SCHEMA-MIN` | `tests/fixtures/schemas/minimal/<model>.json` | One JSON object for each of the 7 models, with all required fields and no optional field |
| `FX-CC-MALFORMED` | `tests/fixtures/transcripts/claude_code/malformed/sess-m.jsonl` | 5 lines, of which line 3 is the text `{"type": "assistant", "sessionId":` |
| `FX-CC-OVERSIZE` | `tests/fixtures/transcripts/claude_code/oversize/sess-o.jsonl` | One command whose `tool_result` content has 2000 lines of the form `LINE-0001` to `LINE-2000` |
| `FX-CC-LONG` | `tests/fixtures/transcripts/claude_code/long/sess-l.jsonl` | One human message and 40 commands `echo step-01` to `echo step-40`, each with a result (81 lines) |
| `FX-SCRIPT-AUTOINC` | `tests/fixtures/scripts/variants/autoincrement.py` | `FX-SCRIPT-REF` without strict port binding |
| `FX-SCRIPT-DUP` | `tests/fixtures/scripts/variants/duplicate_on_rerun.py` | `FX-SCRIPT-REF` without the check for a running instance |
| `FX-SCRIPT-KILL` | `tests/fixtures/scripts/variants/kills_unrelated.py` | `FX-SCRIPT-REF` that stops the process on a busy permitted port |
| `FX-SCRIPT-EDITCORS` | `tests/fixtures/scripts/variants/edits_cors.py` | `FX-SCRIPT-REF` that adds `http://localhost:5175` to `apps/api/src/server.js` |
| `FX-SCRIPT-TAMPER` | `tests/fixtures/scripts/variants/tampers_with_tests.py` | `FX-SCRIPT-NOOP` that first overwrites every file below `tests/` with a test that always passes |
| `FX-SCRIPT-NET` | `tests/fixtures/scripts/variants/needs_network.py` | A script that sends an HTTP GET to `http://example.com/` and exits 0 only if it gets a response |
| `FX-MODEL-BADJSON` | `tests/fixtures/model_responses/contract_not_json.txt` | The text `Here is the contract you asked for` |
| `FX-MODEL-MISSING` | `tests/fixtures/model_responses/contract_missing_field.json` | `FX-GOLDEN` without the key `invariants` |
| `FX-MODEL-STRIPPED` | `tests/fixtures/model_responses/contract_stripped.json` | `FX-GOLDEN` with `invariants` set to `[]` and `acceptance_checks` reduced to Case A |

### Gate 2 run transcript fixtures

A Gate 2 run is a Claude Code session, so READ can parse its transcript into `Entry` records.
Each Gate 2 run fixture is a JSON list of `Entry` objects that the stub agent runner returns.
The first version has no turn limit (`ARCHITECTURE.md` 9.2).

A successful run has these entries, in this order.

| `step_index` | `entry_type` | Key field |
| ---: | :--- | :--- |
| 0 | `user_input` | `content`: "Start the web frontend and verify backend connectivity" |
| 1 | `tool_call` | `command_line`: `cat .claude/skills/vite-safe-dev-server/SKILL.md` |
| 2 | `tool_result` | `exit_code`: 0 |
| 3 | `tool_call` | `command_line`: `python .claude/skills/vite-safe-dev-server/scripts/start.py` |
| 4 | `tool_result` | `exit_code`: 0, `sanitized_output`: `{"status": "ready", "port": 5173, "pid": 4321}` |

## Pydantic schemas

### TT-SCH-001 Each model accepts its minimal valid object

- **Traces to:** `ARCHITECTURE.md` 7.1.
- **Purpose:** Show that each of the 7 models accepts an object with only the required fields.
- **Fixture:** `FX-SCHEMA-MIN`.
  Parametrised over `Entry`, `Episode`, `Evidence`, `Candidate`, `Contract`, `Package`, `Verdict`.
- **Steps:**
  1. Load the JSON object for the model.
  2. Validate it with the model.
- **Expected result:** Validation succeeds for all 7 models.
  `Entry` optional fields are `None`.
  `Episode.repair_iterations` is 0 and `Episode.duration_ms` is 0.
  `Evidence.failure_traces` and `Evidence.common_pitfalls` are empty lists.
  `Candidate.triage_status` is `pending` and `Candidate.rejection_reason` is `None`.
  `Verdict.token_delta_percent` is `None`.
- **What breaks this test:** A developer makes `Entry.exit_code` required, so a `user_input` entry cannot validate.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-002 Each model rejects an object without a required field

- **Traces to:** `ARCHITECTURE.md` 7.1.
- **Purpose:** Show that each required field is required.
- **Fixture:** `FX-SCHEMA-MIN`.
  Parametrised over each required field of each model.
  The required fields are these.
  `Entry`: `entry_id`, `session_id`, `step_index`, `source`, `entry_type`, `timestamp`.
  `Episode`: `episode_id`, `session_id`, `goal`, `entries`, `success`.
  `Evidence`: `session_ids`, `observed_occurrences`, `observed_turns_mean`, `observed_tokens_mean`.
  `Candidate`: `candidate_id`, `title`, `command_sequence`, `normalized_template`, `frequency`, `evidence_type`, `evidence`.
  `Contract`: `candidate_id`, `workflow_name`, `intent`, `inputs`, `preconditions`, `permitted_changes`, `postconditions`, `invariants`, `rerun_behaviour`, `failure_behaviour`, `acceptance_checks`.
  `Package`: `candidate_id`, `script_path`, `skill_path`, `test_path`, `contract`.
  `Verdict`: `candidate_id`, `gate_number`, `outcome`, `total_revisions`, `test_results`, `stdout_log`, `stderr_log`, `execution_duration_ms`, `timestamp`.
- **Steps:**
  1. Remove the one field from the minimal object.
  2. Validate the object.
- **Expected result:** Validation raises a Pydantic `ValidationError` in all 47 cases.
  The error names the removed field.
- **What breaks this test:** A developer gives `Contract.invariants` the default `[]` to make a model response validate.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-003 Entry rejects values outside its enums

- **Traces to:** `ARCHITECTURE.md` 7.1 `Entry`.
- **Purpose:** Show that `source` and `entry_type` are closed sets.
- **Fixture:** The minimal `Entry`, parametrised over 4 changes.
  `source` = `assistant` (raw Claude Code value), `source` = `human`, `entry_type` = `tool_use` (raw block type), `entry_type` = `message`.
- **Steps:**
  1. Apply the change.
  2. Validate the object.
- **Expected result:** Validation fails in all 4 cases.
  The accepted `source` values are `user`, `model`, `system` only.
  The accepted `entry_type` values are `user_input`, `tool_call`, `tool_result`, `generic_message` only.
- **What breaks this test:** The field type becomes `str`, so the reader can store raw values without a mapping.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-004 Entry rejects wrong field types

- **Traces to:** `ARCHITECTURE.md` 7.1 `Entry`.
- **Purpose:** Show that numeric and time fields reject text.
- **Fixture:** The minimal `Entry`, parametrised over 3 changes.
  `step_index` = `"first"`, `exit_code` = `"ok"`, `timestamp` = `"yesterday"`.
- **Steps:**
  1. Apply the change.
  2. Validate the object.
- **Expected result:** Validation fails in all 3 cases and the error names the field.
- **What breaks this test:** The model config sets arbitrary types or the fields become `Any`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-005 Evidence list defaults are not shared between objects

- **Traces to:** `ARCHITECTURE.md` 7.1 `Evidence` (`Field(default_factory=list)`).
- **Purpose:** Show that two `Evidence` objects do not share one default list.
- **Fixture:** Two minimal `Evidence` objects.
- **Steps:**
  1. Create the two objects.
  2. Append `trace-1` to `failure_traces` of the first object.
  3. Read `failure_traces` of the second object.
- **Expected result:** The second list is empty.
- **What breaks this test:** A refactor to a plain class or dataclass with the default `[]`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-006 Candidate rejects unknown enum values

- **Traces to:** `ARCHITECTURE.md` 7.1 `Candidate.triage_status`, `Candidate.evidence_type`.
- **Purpose:** Show that `triage_status` has six values and `evidence_type` has three values.
- **Fixture:** The minimal `Candidate`, parametrised over 7 changes.
  `triage_status` = `reuse`, `generate`, `CONTRACTED`, or `approved`.
  `evidence_type` = `error-fix`, `user_correction`, or `plain`.
- **Steps:**
  1. Apply the change.
  2. Validate the object.
- **Expected result:** Validation fails in all 7 cases.
  The `triage_status` values `pending`, `accepted`, `reuse_existing`, `fix_at_source`, `rejected`, and `clarification_needed` validate.
  The `evidence_type` values `correction`, `error_fix`, and `repetition` validate.
- **What breaks this test:** A field type changes to `str`, so FIND can store a value that the ranking does not know.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-007 Candidate validates its nested Evidence

- **Traces to:** `ARCHITECTURE.md` 7.1 `Candidate.evidence`.
- **Purpose:** Show that an invalid nested object fails the parent.
- **Fixture:** The minimal `Candidate` with `evidence.session_ids` set to the text `sess-a`.
- **Steps:**
  1. Validate the object.
- **Expected result:** Validation fails and the error location is `evidence.session_ids`.
- **What breaks this test:** `Candidate.evidence` becomes `Dict[str, Any]`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-008 Contract rejects wrong field types

- **Traces to:** `ARCHITECTURE.md` 7.1 `Contract`.
- **Purpose:** Show that the list fields and the text fields keep their types.
- **Fixture:** `FX-GOLDEN`, parametrised over 4 changes.
  `preconditions` = one text value, `acceptance_checks` = `null`, `inputs` = a list, `rerun_behaviour` = a list of texts.
- **Steps:**
  1. Apply the change.
  2. Validate the object.
- **Expected result:** Validation fails in all 4 cases and the error names the field.
- **What breaks this test:** A validator that wraps one text value into a list with one item.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-009 The golden contract fixture validates and keeps its values

- **Traces to:** `ARCHITECTURE.md` 7.2.
- **Purpose:** Show that the golden fixture is schema-valid and equals the documented contract.
- **Fixture:** `FX-GOLDEN`.
- **Steps:**
  1. Load `maga/fixtures/golden_contract.json`.
  2. Validate it with `Contract`.
  3. Read the fields.
- **Expected result:** Validation succeeds.
  `candidate_id` is `cand_vite_strict_port_001` and `workflow_name` is `vite-safe-dev-server`.
  `inputs.permitted_ports` is `[5173, 5174]`, `inputs.backend_health_url` is `http://localhost:4000/api/health`, and `inputs.timeout_seconds` is 15.
  `inputs.app_dir` is `apps/web`.
  `preconditions`, `permitted_changes`, `postconditions`, and `invariants` have 3 entries each.
  `acceptance_checks` has 4 entries, which start with `Case A`, `Case B`, `Case C`, and `Case D`.
- **What breaks this test:** Someone removes Case C from the fixture to make a weak script pass Gate 1.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-010 AutomationContract is the same class as Contract

- **Traces to:** `ARCHITECTURE.md` 7.1 "Alias for backwards compatibility".
- **Purpose:** Show that the alias does not become a second schema.
- **Fixture:** None.
- **Steps:**
  1. Import `Contract` and `AutomationContract` from `maga.schemas`.
  2. Compare the two objects by identity.
- **Expected result:** `AutomationContract is Contract` is true.
- **What breaks this test:** A developer defines `AutomationContract` as a subclass with one more field.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-011 Package validates its nested Contract

- **Traces to:** `ARCHITECTURE.md` 7.1 `Package`.
- **Purpose:** Show that a package cannot carry an invalid contract.
- **Fixture:** The minimal `Package` whose `contract` is `FX-GOLDEN` without `failure_behaviour`.
- **Steps:**
  1. Validate the object.
- **Expected result:** Validation fails and the error location is `contract.failure_behaviour`.
- **What breaks this test:** `Package.contract` stores a path to the contract file and not the contract.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-012 Verdict accepts gate numbers 1 and 2 only

- **Traces to:** `ARCHITECTURE.md` 7.1 `Verdict.gate_number`.
- **Purpose:** Show the closed set of gate numbers.
- **Fixture:** The minimal `Verdict`, parametrised over `gate_number` values 0, 3, and `null`.
- **Steps:**
  1. Set `gate_number`.
  2. Validate the object.
- **Expected result:** Validation fails in all 3 cases.
  The values 1 and 2 validate.
- **What breaks this test:** The field type becomes `int`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-013 Verdict accepts three outcomes only

- **Traces to:** `ARCHITECTURE.md` 7.1 `Verdict.outcome`.
- **Purpose:** Show the closed set of outcomes.
- **Fixture:** The minimal `Verdict`, parametrised over `outcome` values `passed`, `PASS`, `error`, `skipped`, and `unverified`.
- **Steps:**
  1. Set `outcome`.
  2. Validate the object.
- **Expected result:** Validation fails in all 5 cases.
  The values `pass`, `fail`, and `inconclusive` validate.
- **What breaks this test:** The verifier adds the value `error` for a runner failure.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-014 Each model survives a JSON round trip

- **Traces to:** `ARCHITECTURE.md` 7 (state is stored as JSON files), 7.1.
- **Purpose:** Show that a stored object loads back as an equal object.
- **Fixture:** One full object for each of the 7 models, with every optional field set.
  `Entry.timestamp` and `Verdict.timestamp` are `2026-01-05T10:00:06Z`.
  `Entry.args` is `{"command": "git status", "timeout": 5000, "run_in_background": true}`.
  `Verdict.token_delta_percent` is `-41.5`.
  Parametrised over the 7 models.
- **Steps:**
  1. Validate the object into model instance A.
  2. Serialise A to a JSON text.
  3. Validate the JSON text into model instance B.
  4. Compare A and B.
- **Expected result:** A equals B for all 7 models.
  `timestamp` in B is timezone-aware and equals the input instant.
  `args` keeps the integer 5000 as an integer and `true` as a boolean.
- **What breaks this test:** A custom serialiser writes `timestamp` as a local time with no offset.
- **Level and needs:** Unit. No network, no model, no container, no human.

## Transcript parsing

The raw format is in `ARCHITECTURE.md` 3.2 and in "Claude Code transcript fixture format" of [FUNCTIONAL_TESTS.md](FUNCTIONAL_TESTS.md).
`uuid` gives `entry_id` and `sessionId` gives `session_id`.
The sources do not say how `step_index` is made (see OQ-T02), so the tests identify an entry by `entry_id`.

### TT-PAR-001 Map the Claude Code line types and content blocks to Entry fields

- **Traces to:** `ARCHITECTURE.md` 3.2, 7.1 `Entry`.
- **Purpose:** Show the field mapping for a human message, a tool call, a tool result, and model prose.
- **Fixture:** Lines 1, 4, and 5 of `FX-CC-A`, plus one `assistant` line `sess-a-L10` with one `text` block "The frontend is ready."
- **Steps:**
  1. Parse the four lines with the parser of `maga.reader`.
  2. Read the four `Entry` objects.
- **Expected result:** Entry `sess-a-L01` has `source` `user`, `entry_type` `user_input`, and `content` "Start the web frontend."
  Entry `sess-a-L04` has `source` `model`, `entry_type` `tool_call`, and `tool_name` `Bash`.
  Entry `sess-a-L04` has `command_line` equal to the raw `input.command` value and `working_dir` `/home/dev_a/workspace`.
  Entry `sess-a-L05` has `entry_type` `tool_result` and `exit_code` 0.
  Entry `sess-a-L10` has `source` `model` and `entry_type` `generic_message`.
  Every entry has `session_id` `sess-a`, and each `timestamp` equals the raw `timestamp` instant.
  The `source` value of a `tool_result` entry is not defined (see OQ-T02).
- **What breaks this test:** The parser reads `message.content` as text only, so a line with content blocks gives no `command_line`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-002 Preserve the original entry identifiers

- **Traces to:** `ARCHITECTURE.md` 3.2 (`uuid` gives `Entry.entry_id`); here.now architecture "Discovery, ranking, and long sessions" ("Preserve original entry IDs").
- **Purpose:** Show that the parser keeps the raw identifier and does not make a new one.
- **Fixture:** `FX-CC-A`.
- **Steps:**
  1. Parse the file two times.
  2. Read `entry_id` and `step_index` of each entry.
- **Expected result:** The 7 `entry_id` values equal the raw `uuid` values of the 7 imported lines.
  Both parses give the same `entry_id` values.
  The `step_index` values are unique, and they increase in file order.
- **What breaks this test:** The parser makes a random UUID for `entry_id`.
  A parser that uses the line number as `entry_id` also breaks the test.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-003 Join a tool call with its result by tool_use_id

- **Traces to:** `ARCHITECTURE.md` 3.2 ("`maga.reader` joins them by `tool_use_id`"); 5.1 rule 2 (needs the exit code of a command).
- **Purpose:** Show that the exit code of a result attaches to the correct command.
- **Fixture:** A session with two commands whose results arrive in the reverse order.
  Line 2 is the `tool_use` `toolu_x_01` with the command `vite`.
  Line 3 is the `tool_use` `toolu_x_02` with the command `vite --port 5174`.
  Line 4 is the `tool_result` for `toolu_x_02` with `is_error` `false`.
  Line 5 is a human message "continue".
  Line 6 is the `tool_result` for `toolu_x_01` with `is_error` `true` and the content "Exit code 1\nPort 5173 is in use".
- **Steps:**
  1. Parse the file.
  2. Request the paired view (command and result) from the reader or the finder (see OQ-T01).
- **Expected result:** `vite` pairs with `exit_code` 1.
  `vite --port 5174` pairs with `exit_code` 0.
  The human message pairs with nothing.
- **What breaks this test:** The pairing takes "the next `tool_result` line" and ignores `tool_use_id`.
  That pairing gives `vite` the exit code 0.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-004 A malformed line

- **Status:** `BLOCKED` by OQ-T03.
  The sources do not say if the reader skips and reports the line, or fails the import.
- **Traces to:** `ARCHITECTURE.md` 5 (row 1: "marks missing data as unknown").
- **Purpose:** Show that a malformed line never disappears without a report.
- **Fixture:** `FX-CC-MALFORMED`.
- **Steps:**
  1. Run READ on `sess-m.jsonl`.
  2. Read the import result and the stored entries.
- **Expected result:** One of two results is correct, and the sources do not select one.
  Result 1: the import fails, names line 3, and stores no checkpoint past line 2.
  Result 2: the import stores the 4 valid entries and the import result names line 3 as malformed.
  In both results the reader does not raise an unhandled exception and does not report a clean import.
- **What breaks this test:** A bare `except: continue` around the JSON parse, which drops line 3 with no report.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-005 Parse the exit code and mark missing data as unknown

- **Traces to:** `ARCHITECTURE.md` 3.2 (`tool_result`: "`is_error` marks a failure"), 5 (row 1: "marks missing data as unknown"), 7.1 `Entry` optional fields.
- **Purpose:** Show the exit-code rule and show that the parser does not invent a value for absent data.
- **Fixture:** Parametrised over 5 `tool_result` cases, each with its `tool_use` line.
  Case 1: `is_error` `false`, content "Done".
  Case 2: `is_error` `true`, content "Exit code 1\nPort 5173 is in use".
  Case 3: `is_error` `true`, content "Exit code 127\ncommand not found".
  Case 4: `is_error` `true`, content "Command timed out" with no `Exit code` text.
  Case 5: a `tool_use` line with no `tool_result` line in the file, and with no `cwd` field.
- **Steps:**
  1. Parse the lines.
  2. Read `exit_code` of the result, or of the paired view for case 5.
  3. Read `working_dir` of the call entry in case 5.
- **Expected result:** The exit codes are 0, 1, and 127 for cases 1, 2, and 3.
  The exit code is `None` for cases 4 and 5.
  `working_dir` is `None` in case 5.
- **What breaks this test:** The parser sets `exit_code` to 0 when it finds no exit code.
  That default turns an unknown result into a success for the error-and-fix rule.
  A parser that sets 1 for every `is_error` result fails case 3.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-006 Import once

- **Traces to:** `ARCHITECTURE.md` 2.1 (`READ`: "Reads new transcript entries once"), 7 (`import_checkpoints.json`).
- **Purpose:** Show idempotent import at the storage boundary.
- **Fixture:** `FX-CC-A`.
- **Steps:**
  1. Run READ three times on `sess-a.jsonl`.
  2. Read `.maga/state/entries/sess-a.json` and count the entries for each `entry_id`.
- **Expected result:** The file has 7 entries.
  Each of the 7 `entry_id` values appears one time.
  Runs 2 and 3 report 0 new entries.
- **What breaks this test:** The checkpoint is written before the entries, and the entries write then appends on each run.
- **Level and needs:** Integration. No network, no model, no container, no human.

### TT-PAR-007 Split an oversized result into linked parts

- **Status:** `BLOCKED` in part by OQ-T05.
  `Entry` has no field for a part link, and the sources define no size limit.
- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Split oversized results into linked parts rather than silently dropping content").
- **Purpose:** Show that a large result loses no content.
- **Fixture:** `FX-CC-OVERSIZE`.
  The test sets the size limit to a value that forces a minimum of 3 parts.
- **Steps:**
  1. Run READ and the chunker on `sess-o.jsonl`.
  2. Collect the parts of the result in order.
  3. Join the part texts.
- **Expected result:** The result has a minimum of 3 parts.
  The joined text contains each of `LINE-0001` to `LINE-2000` one time and in order.
  Each part refers to the `entry_id` of the source line.
  The field that links the parts is not defined.
- **What breaks this test:** The reader truncates the result at the limit and adds "[truncated]".
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-008 Skip bookkeeping lines and thinking blocks

- **Traces to:** `ARCHITECTURE.md` 3.2 (line schema table; `thinking`: "`maga.reader` drops it").
- **Purpose:** Show that the reader imports `user` and `assistant` lines only, and no model reasoning.
- **Fixture:** `FX-CC-A`, plus one line of each of these types, each with the marker `BOOKKEEPING_MARKER_002` in a text field.
  The types are `attachment`, `file-history-snapshot`, `queue-operation`, `mode`, and `ai-title`.
- **Steps:**
  1. Run READ.
  2. Read the stored entries and search all stored text for the markers.
- **Expected result:** The file has 7 entries.
  No entry has the `entry_id` of the `system` line, of the `thinking` line, or of an added line.
  No stored text contains `BOOKKEEPING_MARKER_001`, `BOOKKEEPING_MARKER_002`, or `THINKING_MARKER_001`.
- **What breaks this test:** The reader has a list of types to skip and not a list of types to import.
  A type that is not in the skip list, such as `ai-title`, then becomes an entry.
- **Level and needs:** Unit. No network, no model, no container, no human.

## Normalisation

Each test calls the normalisation function of `maga.finder` on command text.
Several tests compare two normalised results and do not assert a literal placeholder.
`ARCHITECTURE.md` 5.1 rule 4 names two placeholders only: `$REPO_ROOT` and `$PORT_LIST`.

### TT-NRM-001 Normalise an absolute path to a repository token

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 4 "File & Directory Paths"; 3.2 (`cwd` "gives `$REPO_ROOT` for path normalisation").
- **Purpose:** Show the documented path example.
- **Fixture:** The command `ls /home/user/workspace/apps/web` on a line whose `cwd` is `/home/user/workspace`.
- **Steps:**
  1. Normalise the command.
- **Expected result:** The result is `ls $REPO_ROOT/apps/web`.
- **What breaks this test:** The rule replaces the complete path with `$REPO_ROOT` and drops `/apps/web`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-NRM-002 Two repository roots give the same normalised command

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 4 "File & Directory Paths".
- **Purpose:** Show that different checkout locations do not split one procedure.
- **Fixture:** `pnpm --dir /home/dev_a/workspace/apps/web install` with the root `/home/dev_a/workspace`.
  `pnpm --dir /home/dev_b/projects/repo/apps/web install` with the root `/home/dev_b/projects/repo`.
- **Steps:**
  1. Normalise both commands.
  2. Compare the results.
- **Expected result:** The two results are equal.
  Both contain `$REPO_ROOT/apps/web`.
- **What breaks this test:** A rule with a fixed prefix pattern such as `/home/<name>/workspace`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-NRM-003 Normalise port numbers to the port list parameter

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 4 "Port Numbers".
- **Purpose:** Show that a port value does not split one procedure.
- **Fixture:** `vite --port 5173 --strictPort` and `vite --port 5174 --strictPort`.
- **Steps:**
  1. Normalise both commands.
  2. Compare the results.
- **Expected result:** The two results are equal.
  The result contains `$PORT_LIST` and contains neither `5173` nor `5174`.
  The result contains `--strictPort`.
- **What breaks this test:** The port rule is absent, so the two sessions give two sequences.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-NRM-004 Normalise a port inside a URL

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 4 "Port Numbers" ("Specific port occurrences").
- **Purpose:** Show that the `Origin` check command normalises across sessions.
- **Fixture:** `curl -s -H "Origin: http://localhost:5173" http://localhost:4000/api/health`.
  The same command with `5174` in the `Origin` value.
- **Steps:**
  1. Normalise both commands.
  2. Compare the results.
- **Expected result:** The two results are equal.
  The result still contains `/api/health` and `Origin:`.
- **What breaks this test:** The port rule matches only the `--port <n>` flag form.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-NRM-005 Normalise ephemeral tokens

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 4 "Ephemeral Tokens".
- **Purpose:** Show each of the four documented token types.
- **Fixture:** Parametrised over 4 command pairs.
  Timestamp: `tar -czf backup-2026-01-05T10:00:00Z.tgz dist` and `tar -czf backup-2026-02-09T18:30:00Z.tgz dist`.
  Process ID: `kill 4242` and `kill 17001`.
  Commit hash: `git show 3f9a1c2` and `git show b7e44d0a9c1f5e6d7a8b9c0d1e2f3a4b5c6d7e8f`.
  UUID: `cat logs/0b9d6c2e-1f4a-4b7c-9d3e-5a6f7b8c9d0e.log` and `cat logs/7c1e2d3f-4a5b-4c6d-8e7f-9a0b1c2d3e4f.log`.
- **Steps:**
  1. Normalise both commands of the pair.
  2. Compare the results.
- **Expected result:** The two results are equal in all 4 cases.
  Neither result contains its original token.
  The command name (`tar`, `kill`, `git show`, `cat`) is unchanged.
- **What breaks this test:** The hash rule matches 40-character hashes only, so the short hash `3f9a1c2` stays.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-NRM-006 Normalisation must not merge two different commands

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("normalisation cannot hide meaningful differences"); `ARCHITECTURE.md` 5.1 rule 1 ("identical").
- **Purpose:** Show that normalisation removes variable values only.
- **Fixture:** Parametrised over 4 command pairs that differ in meaning.
  Pair 1: `vite --port 5173 --strictPort` and `vite --port 5173`.
  Pair 2: `git worktree add /home/dev_a/workspace-wt demo` and `git worktree remove /home/dev_a/workspace-wt`.
  Pair 3: `rm -rf /home/dev_a/workspace/dist` and `rm -rf /home/dev_a/workspace/src`.
  Pair 4: `git reset --hard 3f9a1c2` and `git revert 3f9a1c2`.
- **Steps:**
  1. Normalise both commands of the pair.
  2. Compare the results.
- **Expected result:** The two results are different in all 4 cases.
- **What breaks this test:** A rule that replaces every token after the program name with a placeholder.
  A rule that replaces the complete path in pair 3 also breaks the test.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-NRM-007 Normalisation keeps the original entry

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Keep original entries").
- **Purpose:** Show that normalisation produces a new value and does not change stored data.
- **Fixture:** `FX-CC-A`, `FX-CC-B`, `FX-CC-C`.
- **Steps:**
  1. Run READ.
  2. Record a hash of each file in `.maga/state/entries/`.
  3. Run FIND.
  4. Record the hashes again.
  5. Read `command_line` of the entry `sess-b-L06`.
- **Expected result:** The hashes are equal before and after FIND.
  `command_line` contains `/home/dev_b/projects/repo/apps/web` and `5174`.
- **What breaks this test:** FIND normalises in place and writes the entries back.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-NRM-008 Normalisation is idempotent

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 4.
- **Purpose:** Show that a normalised command is stable.
- **Fixture:** The three P1 commands of `sess-a`.
- **Steps:**
  1. Normalise each command to result R1.
  2. Normalise R1 to result R2.
- **Expected result:** R2 equals R1 for each command.
- **What breaks this test:** The path rule treats `$REPO_ROOT/apps/web` as a new absolute path and wraps it again.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-NRM-009 Ticket identifiers

- **Status:** `BLOCKED` by OQ-T07.
  No source defines a rule for ticket identifiers.
- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("normalise variable values"), which names no value types.
- **Purpose:** Show that a ticket identifier in a command does not split one procedure.
- **Fixture:** `git checkout -b fix/DEMO-101-login` and `git checkout -b fix/DEMO-202-login`.
- **Steps:**
  1. Normalise both commands.
  2. Compare the results.
- **Expected result:** Not defined.
  `ARCHITECTURE.md` 5.1 rule 4 lists paths, ports, timestamps, process IDs, commit hashes, and UUIDs only.
- **What breaks this test:** The mutation depends on the decision.
  If the rule merges the two commands, the mutation is the removal of the ticket rule.
  If the rule keeps them apart, the mutation is a generic replacement of every `LETTERS-DIGITS` token.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-NRM-010 Pull-request numbers and other plain numbers

- **Status:** `BLOCKED` by OQ-T07.
  No source defines a rule for pull-request numbers or for numbers that are not ports or process IDs.
- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("normalise variable values").
- **Purpose:** Show the treatment of a number that is not a port.
- **Fixture:** `gh pr view 12` and `gh pr view 345`.
  `git log -n 5 --oneline` and `git log -n 50 --oneline`.
- **Steps:**
  1. Normalise both commands of each pair.
  2. Compare the results.
- **Expected result:** Not defined.
  The sources also do not say how the rule separates a process ID from another integer.
- **What breaks this test:** The mutation depends on the decision.
  A rule that replaces every integer merges `git log -n 5` with `git log -n 50`.
  The test must fail for that rule if the decision keeps plain integers.
- **Level and needs:** Unit. No network, no model, no container, no human.

## Sequence counting across sessions

The sources say "identical normalised command sequence".
They do not define the sequence length or whether the commands must be contiguous (see OQ-T08).
The fixtures use contiguous sequences of three commands, so both readings give the same result.

### TT-SEQ-001 Three distinct sessions reach the threshold

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1.
- **Purpose:** Show the upper side of the threshold boundary.
- **Fixture:** `FX-CC-A`, `FX-CC-B`, `FX-CC-C`.
- **Steps:**
  1. Run READ.
  2. Run the sequence counter of `maga.finder` with no model.
  3. Read the flagged sequences.
- **Expected result:** One sequence is flagged and it is the normalised P1 sequence.
  Its distinct-session count is 3.
- **What breaks this test:** The comparison is `> 3` and not `>= 3`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-002 Two distinct sessions do not reach the threshold

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1.
- **Purpose:** Show the lower side of the threshold boundary.
- **Fixture:** `FX-CC-TWO`.
- **Steps:**
  1. Run READ and the sequence counter.
  2. Read the flagged sequences.
- **Expected result:** No sequence is flagged.
- **What breaks this test:** The threshold constant is 2 and not 3.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-003 Many repeats in one session do not reach the threshold

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1 ("distinct sessions").
- **Purpose:** Show that the counter counts sessions.
- **Fixture:** `FX-CC-ONE` (P1 five times in `sess-d`).
- **Steps:**
  1. Run READ and the sequence counter.
  2. Read the flagged sequences.
- **Expected result:** No sequence is flagged.
- **What breaks this test:** The counter adds 1 for each occurrence and not for each session.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-004 Repeats in one session plus two other sessions

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1; 7.1 `Evidence.session_ids`, `Candidate.frequency` ("Distinct sessions").
- **Purpose:** Show that a repeat in one session does not change the session list.
- **Fixture:** `FX-CC-ONE` (5 occurrences in `sess-d`), `FX-CC-A`, and `FX-CC-B`.
- **Steps:**
  1. Run READ and FIND with the stub model.
  2. Read the candidate.
- **Expected result:** One candidate exists.
  `evidence.session_ids` has 3 entries: `sess-a`, `sess-b`, `sess-d`, each one time.
  `frequency` is 3, because `frequency` counts distinct sessions.
  The value of `evidence.observed_occurrences` (3 or 7) is not defined (see OQ-T08).
- **What breaks this test:** `session_ids` is a list with one entry for each occurrence, so `sess-d` appears 5 times.
  A `frequency` that counts occurrences gives 7.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-SEQ-005 The same session imported from two locations counts one time

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1 ("distinct sessions"); here.now architecture "Discovery, ranking, and long sessions" ("remove duplicate evidence by source reference").
- **Purpose:** Show that a copied transcript does not create a false third session.
- **Fixture:** `FX-CC-A`, `FX-CC-B`, and a second copy of `sess-a.jsonl` with the same `sessionId` in a different project directory.
- **Steps:**
  1. Run READ on both project directories.
  2. Run the sequence counter.
- **Expected result:** No sequence is flagged.
  The distinct-session count for P1 is 2.
- **What breaks this test:** The counter uses the file path and not `session_id` as the session key.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-006 A different command order is a different sequence

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1 ("identical normalised command sequence").
- **Purpose:** Show that the counter compares ordered sequences.
- **Fixture:** `FX-CC-A`, `FX-CC-B`, and a session `sess-r` with the three P1 commands in reverse order.
- **Steps:**
  1. Run READ and the sequence counter.
  2. Read the flagged sequences.
- **Expected result:** The P1 sequence of three commands is not flagged.
- **What breaks this test:** The counter compares sorted command sets.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-007 Sequence counting needs no model

- **Traces to:** here.now one-pager "The idea" ("Count command sequences without a model"); here.now architecture "Discovery, ranking, and long sessions".
- **Purpose:** Show that the first discovery step is deterministic and costs no tokens.
- **Fixture:** `FX-CC-A`, `FX-CC-B`, `FX-CC-C`.
  A stub model that fails the test when it receives a request.
- **Steps:**
  1. Run READ and the sequence counter two times.
  2. Compare the two results.
- **Expected result:** The stub model receives no request.
  The two results are equal.
- **What breaks this test:** The counter asks a model to decide if two commands are "the same".
- **Level and needs:** Unit. No network, no container, no human.

### TT-SEQ-008 Ranking order and tie-break

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 5; 7.1 `Candidate.evidence_type`, `Candidate.frequency`.
- **Purpose:** Show the three sort keys of the ranking function.
- **Fixture:** Six minimal `Candidate` objects, given to the ranking function in this order.
  `cand_f` (`repetition`, `frequency` 9), `cand_e` (`repetition`, `frequency` 3), `cand_d` (`error_fix`, `frequency` 3).
  `cand_c` (`error_fix`, `frequency` 4), `cand_b` (`correction`, `frequency` 3), `cand_a` (`correction`, `frequency` 3).
- **Steps:**
  1. Rank the six candidates.
  2. Rank the same candidates again in the reverse input order.
- **Expected result:** Both results are `cand_a`, `cand_b`, `cand_c`, `cand_d`, `cand_f`, `cand_e`.
- **What breaks this test:** A sort by `frequency` first puts `cand_f` at the top.
  A sort with no `candidate_id` key keeps the input order of `cand_a` and `cand_b`, so the two results differ.
  An ascending `frequency` key puts `cand_d` before `cand_c`.
- **Level and needs:** Unit. No network, no model, no container, no human.

## Error-and-fix pair detection

The rule is in `ARCHITECTURE.md` 5.1 rule 2.
A pair is a failed step, followed within 3 subsequent tool actions by a command with modified parameters or flags that exits 0.
Each fixture below is a list of commands with exit codes, written as one Claude Code session.
A command with a non-zero exit code has `is_error` `true` and the content "Exit code N".

### TT-EFX-001 Detect the documented example

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2, example.
- **Purpose:** Show the positive case from the source.
- **Fixture:** `vite` (exit 1), `lsof -i :5173` (exit 0), `vite --port 5174` (exit 0).
- **Steps:**
  1. Run READ and the error-and-fix detector.
  2. Read the detected pairs.
- **Expected result:** One pair is detected.
  The error step is `vite` and the fix step is `vite --port 5174`.
- **What breaks this test:** The detector requires the fix to be the next action after the error.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-EFX-002 The fix is the third subsequent action

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2 ("within <= 3 subsequent tool actions").
- **Purpose:** Show the inner side of the distance boundary.
- **Fixture:** `vite` (exit 1), `lsof -i :5173` (exit 0), `cat packages/config/ports.json` (exit 0), `vite --port 5174` (exit 0).
- **Steps:**
  1. Run READ and the detector.
- **Expected result:** One pair is detected: `vite` and `vite --port 5174`.
- **What breaks this test:** The window is 2 actions.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-EFX-003 The fix is the fourth subsequent action

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2.
- **Purpose:** Show the outer side of the distance boundary.
- **Fixture:** `vite` (exit 1), `lsof -i :5173` (exit 0), `cat packages/config/ports.json` (exit 0), `git status` (exit 0), `vite --port 5174` (exit 0).
- **Steps:**
  1. Run READ and the detector.
- **Expected result:** No pair is detected.
- **What breaks this test:** The window has no upper limit.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-EFX-004 An identical retry is not a fix

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2 ("a command modifying parameters/flags").
- **Purpose:** Show that the fix must change the command.
- **Fixture:** `vite` (exit 1), `vite` (exit 0).
- **Steps:**
  1. Run READ and the detector.
- **Expected result:** No pair is detected.
- **What breaks this test:** The detector accepts any later command with the same program name and exit code 0.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-EFX-005 A modified command that fails is not a fix

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2 ("and exiting 0").
- **Purpose:** Show that the fix must succeed.
- **Fixture:** `vite` (exit 1), `vite --port 5174` (exit 1).
  A second variant in which the result of `vite --port 5174` has `is_error` `true` and no `Exit code` text.
- **Steps:**
  1. Run READ and the detector on each variant.
- **Expected result:** No pair is detected in either variant.
- **What breaks this test:** The detector checks `exit_code != 1`, so an unknown exit code counts as a success.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-EFX-006 An error pattern on stderr with exit code 0

- **Status:** `BLOCKED` by OQ-T10.
  The rule says "non-zero exit code or stderr error pattern", but no source lists the patterns.
- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2.
- **Purpose:** Show that a failed step with exit code 0 can start a pair.
- **Fixture:** `vite` (`is_error` `false`, content "error: Port 5173 is in use"), `vite --port 5174` (exit 0).
- **Steps:**
  1. Run READ and the detector.
- **Expected result:** Not defined until the pattern list exists.
- **What breaks this test:** When the pattern list exists: a detector that reads `exit_code` only and ignores the output text.
- **Level and needs:** Unit. No network, no model, no container, no human.

## User-correction detection

### TT-COR-001 Flag the step before a correction

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 3.
- **Purpose:** Show that the defect is the agent step before the user message.
- **Fixture:** One session of `FX-CC-CORR` (procedure P3).
  The stub model classifies the message as a correction.
- **Steps:**
  1. Run READ and the correction detector.
  2. Read the detected corrections.
- **Expected result:** One correction is detected.
  The flagged step has `command_line` `kill -9 4242`.
  The flagged step is not `lsof -i :5173`.
- **What breaks this test:** The detector flags the step after the user message.
- **Level and needs:** Unit. Stub model. No network, no container, no human.

### TT-COR-002 An ordinary user message is not a correction

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 3 ("explicitly intervenes with a corrective instruction").
- **Purpose:** Show the negative case.
- **Fixture:** A session with `pnpm test` (exit 0), the human message "Thanks. Now run the linter.", and `pnpm lint` (exit 0).
  The stub model classifies the message as not a correction.
- **Steps:**
  1. Run READ and the correction detector.
- **Expected result:** No correction is detected and no step is flagged as a defect.
- **What breaks this test:** The detector treats every mid-session human message as a correction.
- **Level and needs:** Unit. Stub model. No network, no container, no human.

### TT-COR-003 A model rejection stops the promotion

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 3 ("semantically validated using Gemini prompt classification before candidate promotion").
- **Purpose:** Show that the model classification is a gate and not a log entry.
- **Fixture:** `FX-CC-CORR` (3 sessions).
  The stub model classifies the message "don't kill that process" as not a correction.
- **Steps:**
  1. Run READ and FIND.
  2. Read the candidates directory.
- **Expected result:** No candidate exists that has the correction as evidence.
- **What breaks this test:** FIND uses a keyword match on "don't" and ignores the classification result.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-COR-004 The correction reaches the contract as an invariant

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 3 ("uses the correction to formulate negative constraints and invariants in the contract").
- **Purpose:** Show that the correction text is an input to contract synthesis.
- **Fixture:** `FX-CC-CORR` with the stub model as classifier and as contract synthesiser.
- **Steps:**
  1. Run READ, FIND, and DECIDE.
  2. Read the contract synthesis request that the stub model recorded.
- **Expected result:** The request contains the correction "don't kill that process" or the candidate's pitfall record of it.
- **What breaks this test:** DECIDE sends only `command_sequence` to the synthesiser.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-COR-005 A tool-result line is never a correction candidate

- **Traces to:** `ARCHITECTURE.md` 3.2 ("A `user` line whose content is only `tool_result` blocks is not a human message, so it is never a correction candidate").
- **Purpose:** Show that the detector reads human messages only.
- **Fixture:** A session with `kill -9 4242` and its `tool_result`, and then `lsof -i :5173` and its `tool_result`.
  The content of the first `tool_result` is "don't kill that process".
  The session has no human message after line 1.
  A stub model that classifies every text as a correction.
- **Steps:**
  1. Run READ and the correction detector.
  2. Read the detected corrections and the requests that the stub model recorded.
- **Expected result:** No correction is detected and no step is flagged as a defect.
  The stub model received no request that contains "don't kill that process".
  The entry of that line has `entry_type` `tool_result`.
- **What breaks this test:** The detector selects lines by `type` `user` or by `message.role` `user`.
- **Level and needs:** Unit. Stub model. No network, no container, no human.

## Chunking

The chunking rules come from the here.now architecture page only.
The sources define no token budget, no overlap size, and no tokeniser (see OQ-T11).
Each test sets the budget and the overlap itself.
Each test measures tokens with the token counter of the implementation.

### TT-CHK-001 No chunk exceeds the token budget

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("A chunk is a bounded group of transcript entries. Split by token budget").
- **Purpose:** Show that the budget is an upper limit.
- **Fixture:** `FX-CC-LONG`, with a budget that is about one quarter of the token count of the session.
- **Steps:**
  1. Run READ and the chunker.
  2. Count the tokens of each chunk.
- **Expected result:** The chunker returns a minimum of 4 chunks.
  The token count of each chunk is less than or equal to the budget.
- **What breaks this test:** The chunker splits by entry count and ignores the entry size.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-CHK-002 Chunks lose no entry

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("rather than silently dropping content").
- **Purpose:** Show that the union of the chunks equals the session.
- **Fixture:** As TT-CHK-001.
- **Steps:**
  1. Collect the `entry_id` values of all chunks.
  2. Compare the set with the `entry_id` values of the session.
- **Expected result:** The two sets are equal (81 entries: 1 human message, 40 calls, 40 results).
- **What breaks this test:** The chunker drops the entry that crosses a budget boundary.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-CHK-003 A tool call stays with its result

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Keep tool calls with their results where possible").
- **Purpose:** Show that a chunk boundary does not separate a call from its result.
- **Fixture:** As TT-CHK-001.
  Every call and result pair is smaller than the budget, so the rule is always possible.
- **Steps:**
  1. For each `tool_call` entry, find the chunks that contain it.
  2. Find the chunks that contain its `tool_result` entry.
- **Expected result:** For each of the 40 pairs, a minimum of one chunk contains both entries.
- **What breaks this test:** The chunker closes a chunk as soon as the budget is reached, between a call and its result.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-CHK-004 Adjacent chunks overlap

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Carry a short summary of unfinished tasks and a small overlap into the next chunk").
- **Purpose:** Show that the configured overlap exists.
- **Fixture:** As TT-CHK-001, with the overlap set to one call and result pair.
- **Steps:**
  1. For each chunk after the first, read its first entries.
  2. Compare them with the last entries of the chunk before.
- **Expected result:** Each chunk after the first starts with the last call and result pair of the chunk before.
  The entries in the overlap keep their original `entry_id` values.
  The content of the "short summary of unfinished tasks" is not defined (see OQ-T11).
- **What breaks this test:** The overlap setting is read but not applied.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-CHK-005 Evidence is deduplicated by source reference

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Join task fragments and remove duplicate evidence by source reference").
- **Purpose:** Show that the overlap does not count one entry two times.
- **Fixture:** `FX-CC-A`, `FX-CC-B`, and one long session in which P1 occurs one time across a chunk boundary.
  The overlap makes the P1 commands appear in two chunks of that session.
- **Steps:**
  1. Run READ, the chunker, and FIND with the stub model.
  2. Read the candidate for P1.
- **Expected result:** `evidence.session_ids` has 3 entries.
  The long session contributes one occurrence of P1 and not two.
- **What breaks this test:** Evidence is keyed by chunk number and not by `entry_id`.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-CHK-006 No model request contains the whole transcript

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Do not send the whole transcript in one request", "Retrieve only the source excerpts needed for each candidate").
- **Purpose:** Show that model input is bounded.
- **Fixture:** `FX-CC-LONG` three times with different session IDs, so that a candidate exists.
  Each of the 40 commands has a unique text `echo step-NN`.
- **Steps:**
  1. Run READ and FIND with the stub model.
  2. For each recorded request, count how many of the 40 unique texts of one session it contains.
- **Expected result:** No request contains all 40 texts of one session.
  The token count of each request is less than or equal to the budget that the test set.
- **What breaks this test:** FIND reads `entries/<session_id>.json` and sends the file content as one message.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

## Redactor

The only documented secret patterns are in `ARCHITECTURE.md` 10.1: `API_KEY=.*`, `Bearer .*`, and `ghp_.*`.
The documented placeholder is `[REDACTED_SECRET]`.
`ARCHITECTURE.md` 10.1 defines them for the Gateway guardrail.
The sources list no separate pattern set for the redactor in `maga.reader` (see OQ-T12).
The tests build each secret at runtime, as FT-RED-001 describes.
No test file contains a complete secret-shaped literal.

### TT-RDX-001 Redact each documented pattern

- **Traces to:** `ARCHITECTURE.md` 10.1 "Gateway Guardrail"; 5 (row 1).
- **Purpose:** Show that the reader redactor covers the three documented patterns.
- **Fixture:** Parametrised over the three runtime secrets of FT-RED-001.
  Each secret is inside the text `export <secret> && pnpm dev`.
- **Steps:**
  1. Call the redactor on the text.
- **Expected result:** The result does not contain the secret value (`FAKE_SECRET_VALUE_001`, `FAKE_SECRET_VALUE_002`, or the repeated `FAKE` text).
  The result contains `[REDACTED_SECRET]`.
- **What breaks this test:** One of the three patterns is removed from the pattern list.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-RDX-002 Redaction covers every text field of an Entry

- **Traces to:** `ARCHITECTURE.md` 7.1 `Entry`; `AGENTS.md` 2.2 ("Sanitize all tokens before passing transcript entries to model gateways").
- **Purpose:** Show that no field is a bypass.
- **Fixture:** Parametrised over the fields `command_line`, `content`, `sanitized_output`, and `args`.
  The raw line places the `API_KEY=` secret so that it lands in the one field.
  For `args`, the secret is the value of the key `description` inside the raw `input` object of the `tool_use` block.
- **Steps:**
  1. Run READ on the line.
  2. Serialise the stored `Entry` to JSON text.
- **Expected result:** The JSON text does not contain `FAKE_SECRET_VALUE_001` in any of the 4 cases.
- **What breaks this test:** The redactor handles text fields only, and `args` is a dictionary that it does not walk.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-RDX-003 No secret in any model-bound payload

- **Traces to:** here.now one-pager "Keep control" ("Redact known secret patterns before model calls"); `AGENTS.md` 2.2.
- **Purpose:** Show the guarantee at the model boundary for every stage that calls a model.
- **Fixture:** The three secret sessions of FT-RED-001.
  A stub model on every model route: correction classification, candidate analysis, contract synthesis, test generation, script generation, and revision.
- **Steps:**
  1. Run the pipeline from the reader to the end of one revision round.
  2. Search every recorded payload for the three secret values.
  3. Count the recorded payloads for each route.
- **Expected result:** Each route recorded a minimum of one payload.
  No payload contains a secret value.
- **What breaks this test:** The revision route sends raw Gate 1 logs, and the failed script printed its environment.
  The route count protects the test from a pipeline that calls no model.
- **Level and needs:** Integration. Stub model, stub agent runner. No network, no human.

### TT-RDX-004 Redaction does not remove non-secret text

- **Traces to:** `ARCHITECTURE.md` 10.1 patterns; 5.1 rule 1 (mining needs the command text).
- **Purpose:** Show that redaction keeps the commands that FIND needs.
- **Fixture:** The text `pnpm --dir /home/dev_a/workspace/apps/web exec vite --port 5173 --strictPort`.
  The text `echo Bearing load is fine`.
- **Steps:**
  1. Call the redactor on each text.
- **Expected result:** Each result equals its input.
- **What breaks this test:** A pattern without case or word rules, such as `bear.*`, which also removes "Bearing load".
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-RDX-005 Redaction is idempotent

- **Traces to:** `ARCHITECTURE.md` 10.1 placeholder `[REDACTED_SECRET]`.
- **Purpose:** Show that a second pass does not change a redacted text.
- **Fixture:** The three redacted results of TT-RDX-001.
- **Steps:**
  1. Call the redactor on each redacted result.
- **Expected result:** Each second result equals the first result.
- **What breaks this test:** The `API_KEY=.*` pattern matches `API_KEY=[REDACTED_SECRET]` and nests a second placeholder.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-RDX-006 Document a pattern that the redactor does not catch

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Pattern matching is incomplete protection"); here.now one-pager "Keep control" ("known secret patterns").
- **Purpose:** Record one known limit of the redactor so that nobody reads the redactor as complete protection.
- **Fixture:** The text `the database password is` plus a space, joined at runtime with `FAKE_SECRET_VALUE_003`.
  This text matches none of the three documented patterns.
- **Steps:**
  1. Call the redactor on the text.
- **Expected result:** The result still contains `FAKE_SECRET_VALUE_003`.
  The test name and its message say that this is a known limit and not a wanted behaviour.
- **What breaks this test:** A developer adds a pattern for prose passwords.
  The test then fails, and the developer must move this case to TT-RDX-001 and select a new uncaught case.
  The list of known limits therefore stays current.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-RDX-007 Gateway guardrail echo test

- **Traces to:** `ARCHITECTURE.md` 10.1 "Echo Test".
- **Purpose:** Show that the hosted model receives the placeholder and not the secret.
- **Fixture:** A prompt built at runtime: "Repeat this text exactly:" plus the `API_KEY=` secret.
  The test sends the prompt through the Gateway with the MAGA redactor switched off.
- **Steps:**
  1. Send the prompt to the Modal-hosted model through the Pydantic AI Gateway.
  2. Read the model response and the Logfire trace of the request.
- **Expected result:** The response contains `[REDACTED_SECRET]`.
  The response and the trace do not contain `FAKE_SECRET_VALUE_001`.
- **What breaks this test:** The guardrail rule is set to the action "log" and not to `Redact`.
- **Level and needs:** End-to-end. Network, model on Modal, Gateway account. No container, no human.

### TT-RDX-008 Transcript text is in the data part of a model request only

- **Traces to:** here.now one-pager "Keep control" ("Treat transcripts as data, never as instructions").
- **Purpose:** Show the deterministic part of the prompt-injection defence.
- **Fixture:** `FX-CC-INJECT`, whose tool result contains the marker `INJECTION_CANARY`.
- **Steps:**
  1. Run READ, FIND, and DECIDE with the stub model.
  2. For each recorded request, separate the instruction part from the user-content part.
  3. Search the instruction part for `INJECTION_CANARY`.
- **Expected result:** No instruction part contains `INJECTION_CANARY`.
- **What breaks this test:** A prompt template that formats the excerpt into the system prompt string.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

## State storage

### TT-STO-001 Each record type is stored at its documented path

- **Traces to:** `ARCHITECTURE.md` 7 (directory tree).
- **Purpose:** Show the storage layout.
- **Fixture:** A full pipeline run for `FX-GOLDEN` with stub model and stub agent runner.
- **Steps:**
  1. Run the pipeline to the Gate 2 verdict.
  2. List the files below `.maga/`.
- **Expected result:** These files exist.
  `.maga/state/import_checkpoints.json`.
  `.maga/state/entries/<session_id>.json` for each session.
  `.maga/state/episodes/<session_id>_episodes.json` for each session.
  `.maga/state/candidates/<candidate_id>.json`.
  `.maga/state/contracts/<candidate_id>.json`.
  `.maga/state/verification/<candidate_id>_verdict.json`.
  `.maga/artifacts/staged/<candidate_id>/SKILL.md`, `scripts/start.py`, and `tests/test_start.py`.
  Each JSON file validates against its model.
  No file with the extension `.db` or `.sqlite` exists.
- **What breaks this test:** A stage keeps its records in memory and writes nothing.
- **Level and needs:** Integration. Stub model, stub agent runner. No network, no human.

### TT-STO-002 Resume from a checkpoint after an interrupted import

- **Traces to:** `ARCHITECTURE.md` 5 (row 1: "tracks incremental session watermarks"), 7 (`import_checkpoints.json`).
- **Purpose:** Show that an interrupted import completes on the next run with no loss and no duplicate.
- **Fixture:** `FX-CC-LONG` (81 lines).
  The test makes the entry store raise an error when it receives the entry `sess-l-L41`.
- **Steps:**
  1. Run READ and observe the error.
  2. Remove the injected error.
  3. Run READ again.
  4. Read `.maga/state/entries/sess-l.json`.
- **Expected result:** Step 1 reports a failure and not a success.
  After step 3 the file has 81 entries.
  Each `entry_id` from `sess-l-L01` to `sess-l-L81` appears one time.
- **What breaks this test:** The checkpoint is written before the entries.
  The second run then starts after the failed entry, and the entries from the failed batch are lost.
- **Level and needs:** Integration. No network, no model, no container, no human.

### TT-STO-003 The checkpoint is per session

- **Traces to:** `ARCHITECTURE.md` 7 ("Ingest watermarks per session").
- **Purpose:** Show that the watermark of one session does not hide entries of another session.
- **Fixture:** `FX-CC-LONG` (81 lines) and `FX-CC-A` (9 lines).
- **Steps:**
  1. Run READ on `sess-l` only.
  2. Run READ on `sess-l` and `sess-a`.
  3. Read `.maga/state/entries/sess-a.json`.
- **Expected result:** `sess-a.json` has 7 entries.
- **What breaks this test:** One global watermark, which makes every `sess-a` line look old after the import of `sess-l`.
- **Level and needs:** Integration. No network, no model, no container, no human.

### TT-STO-004 State is below the gitignored directory

- **Traces to:** `ARCHITECTURE.md` 7 ("`.maga/` is gitignored"); `AGENTS.md` 2.2.
- **Purpose:** Show that Git cannot pick up state files.
- **Fixture:** A clone of the MAGA repository, and `FX-CC-A`.
- **Steps:**
  1. Run `git check-ignore -q` for `.maga/state/entries/sess-a.json` and for `.maga/artifacts/staged/x/SKILL.md` in the clone.
  2. Run READ on `sess-a` with the clone as the project directory.
  3. Run `git status --porcelain --untracked-files=all`.
  4. Compare the list of all files in the clone before and after step 2.
- **Expected result:** `git check-ignore` exits with code 0 for both paths.
  `git status` prints no path that starts with `.maga/`.
  Every new file is below `.maga/`.
- **What breaks this test:** The `.gitignore` entry is absent, or the reader writes a cache file next to the source code.
- **Level and needs:** Integration. Git. No network, no model, no container, no human.

### TT-STO-005 A corrupt state file is rejected at load

- **Traces to:** `ARCHITECTURE.md` 7.1; `AGENTS.md` 1 Beat 2 ("Enforce schema invariants with Pydantic").
- **Purpose:** Show that a stage validates what it loads.
- **Fixture:** A valid candidate file in which `evidence.session_ids` is changed to `null`.
- **Steps:**
  1. Run DECIDE for the candidate.
- **Expected result:** DECIDE fails with a validation error that names `evidence.session_ids`.
  The stub model receives no request.
- **What breaks this test:** The loader uses `model_construct` or a plain `json.load` with no validation.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

## Candidate state machine

`ARCHITECTURE.md` 6 defines 18 states.
The states are `DISCOVERED`, `DECIDED`, `REJECTED`, `CLARIFICATION_REQUESTED`, `FIX_AT_SOURCE`, `REUSE_EXISTING`, `CONTRACTED`, `APPROVED`, `GENERATING`, `VALIDATING`, `REVISING`, `UNVERIFIED`, `INCONCLUSIVE`, `EVALUATING_REUSE`, `PACKAGE_APPROVAL`, `PROPOSED`, `HUMAN_APPROVED`, and `MERGED`.
No schema in `ARCHITECTURE.md` 7.1 has a field for the state (see OQ-T14).

### TT-STM-001 Every legal transition is accepted

- **Traces to:** `ARCHITECTURE.md` 6, state diagram.
- **Purpose:** Show that the implementation permits each documented transition.
- **Fixture:** Parametrised over the 25 transitions between named states.
  `DISCOVERED` to `DECIDED`.
  `DECIDED` to `REJECTED`, `CLARIFICATION_REQUESTED`, `FIX_AT_SOURCE`, `REUSE_EXISTING`, and `CONTRACTED`.
  `REUSE_EXISTING` to `CONTRACTED`.
  `CONTRACTED` to `APPROVED` and `REJECTED`.
  `APPROVED` to `GENERATING`.
  `GENERATING` to `VALIDATING`.
  `VALIDATING` to `REVISING`, `UNVERIFIED`, `INCONCLUSIVE`, and `EVALUATING_REUSE`.
  `EVALUATING_REUSE` to `REVISING`, `UNVERIFIED`, `INCONCLUSIVE`, and `PACKAGE_APPROVAL`.
  `REVISING` to `GENERATING`.
  `PACKAGE_APPROVAL` to `PROPOSED` and `REJECTED`.
  `PROPOSED` to `HUMAN_APPROVED` and `REJECTED`.
  `HUMAN_APPROVED` to `MERGED`.
- **Steps:**
  1. Create a candidate in the source state with the guard data that the transition needs.
  2. Request the transition.
  3. Read the state.
- **Expected result:** The state equals the target state in all 25 cases.
  A new candidate starts in `DISCOVERED`.
- **What breaks this test:** A transition table that omits `EVALUATING_REUSE` to `REVISING`, so a Gate 2 failure cannot use the budget.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-STM-002 Every other transition is rejected

- **Traces to:** `ARCHITECTURE.md` 6, state diagram.
- **Purpose:** Show that the documented transitions are the only transitions.
- **Fixture:** Parametrised over every ordered pair of the 18 states that is not in TT-STM-001.
  This gives 299 pairs (324 pairs minus 25 legal pairs), and it includes each state to itself.
  The test generates the pairs from the legal list and the state list.
- **Steps:**
  1. Create a candidate in the source state.
  2. Request the transition.
  3. Read the state.
- **Expected result:** Each request fails with an error that names both states.
  The state is unchanged.
  The list includes these important cases.
  `DECIDED` to `GENERATING` (skips the contract).
  `CONTRACTED` to `GENERATING` (skips the contract approval).
  `GENERATING` to `EVALUATING_REUSE` (skips Gate 1).
  `VALIDATING` to `PACKAGE_APPROVAL` (skips Gate 2).
  `EVALUATING_REUSE` to `PROPOSED` (skips the package approval).
  `UNVERIFIED` to `REVISING` and `INCONCLUSIVE` to `PROPOSED` (leaves a final state).
  `REVISING` to `VALIDATING` (tests a package that was not generated again).
- **What breaks this test:** A `set_state` function that accepts any value.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-STM-003 The final states have no exit

- **Traces to:** `ARCHITECTURE.md` 6 ("permanently terminates without creating a pull request").
- **Purpose:** Show that `REJECTED`, `UNVERIFIED`, `INCONCLUSIVE`, `FIX_AT_SOURCE`, and `MERGED` are final.
- **Fixture:** One candidate in each of the five states.
- **Steps:**
  1. Request a transition to each of the 18 states.
  2. Try to run BUILD, CHECK, and the publisher for the candidate.
- **Expected result:** Every request fails.
  No stage starts and the publisher double records no call.
  `CLARIFICATION_REQUESTED` also has no documented exit (see OQ-T14).
- **What breaks this test:** A "retry" command that moves `UNVERIFIED` back to `GENERATING` with a new budget.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-STM-004 The approval guards

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 2; 6 (`CONTRACTED` to `APPROVED`, `PACKAGE_APPROVAL` to `PROPOSED`); `AGENTS.md` 2.4.
- **Purpose:** Show that each approval transition needs a human approval of the exact content.
- **Fixture:** Parametrised over the 2 approval transitions and over 3 cases.
  Case 1: no approval record.
  Case 2: an approval of a different content (one changed byte in the contract or in the package).
  Case 3: an approval of the exact content.
- **Steps:**
  1. Request the transition `CONTRACTED` to `APPROVED`, or `PACKAGE_APPROVAL` to `PROPOSED`.
- **Expected result:** Cases 1 and 2 fail and the state is unchanged, for both transitions.
  Case 3 succeeds for both transitions.
- **What breaks this test:** The guard checks that an approval record exists and does not compare the content.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-STM-005 The outcome of Gate 1 selects the transition

- **Traces to:** `ARCHITECTURE.md` 6, transitions from `VALIDATING`.
- **Purpose:** Show the mapping from a Gate 1 `Verdict` to the next state.
- **Fixture:** A `VALIDATING` candidate, parametrised over 5 Gate 1 verdicts.
  Case 1: `pass`, `total_revisions` 0.
  Case 2: `fail`, `total_revisions` 0.
  Case 3: `fail`, `total_revisions` 3.
  Case 4: `inconclusive`, `total_revisions` 0.
  Case 5: `pass`, `total_revisions` 3.
- **Steps:**
  1. Apply the verdict.
  2. Read the state and the revision counter.
- **Expected result:** Case 1 gives `EVALUATING_REUSE`.
  Case 2 gives `REVISING`.
  Case 3 gives `UNVERIFIED`.
  Case 4 gives `INCONCLUSIVE`, and the revision counter stays 0.
  Case 5 gives `EVALUATING_REUSE`, because a pass needs no budget.
- **What breaks this test:** `inconclusive` is handled as `fail`, so case 4 goes to `REVISING` and uses the budget.
  The mapping of the earlier design, `inconclusive` to `UNVERIFIED`, also breaks the test.
- **Level and needs:** Unit. No network, no model, no container, no human.

## Revision budget and fixed contract

`MAX_TOTAL_REVISIONS = 3`.
The counter increments when a gate failure sends the candidate to `REVISING`.
The budget is one first attempt plus three revisions, and `total_revisions` counts the revisions already made.
The fourth failure (`total_revisions >= 3`) sends the candidate to `UNVERIFIED`.

### TT-REV-001 The budget boundary

- **Traces to:** `ARCHITECTURE.md` 6 (`total_revisions < 3` and `total_revisions >= 3`).
- **Purpose:** Show both sides of the boundary for both gates.
- **Fixture:** Parametrised over the gate (`VALIDATING` with a Gate 1 `fail`, `EVALUATING_REUSE` with a Gate 2 `fail`) and over `total_revisions` 0, 1, 2, 3.
- **Steps:**
  1. Apply the failed verdict.
  2. Read the state and the counter.
- **Expected result:** For 0, 1, and 2 the state is `REVISING` and the counter is 1, 2, and 3.
  For 3 the state is `UNVERIFIED` and the counter stays 3.
  The results are the same for both gates.
- **What breaks this test:** The comparison is `<= 3`, which permits a fourth revision.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-REV-002 Both gates share one counter

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 9; 6; `AGENTS.md` 2.5.
- **Purpose:** Show that failures of Gate 1 and Gate 2 use the same budget.
- **Fixture:** A stub verifier that returns this verdict sequence.
  Gate 1 `fail`, Gate 1 `pass`, Gate 2 `fail`, Gate 1 `fail`, Gate 1 `pass`, Gate 2 `fail`.
  A generator double that counts its calls, and a publisher double.
- **Steps:**
  1. Run CHECK to completion.
  2. Read each stored verdict, the state, and the call counts.
- **Expected result:** The counter after each failure is 1, 2, 3.
  The fourth failure (Gate 2, counter 3) gives `UNVERIFIED`.
  The generator double recorded 4 calls.
  The last verdict has `gate_number` 2, `outcome` `fail`, and `total_revisions` 3.
  The publisher double recorded no call.
- **What breaks this test:** One counter for each gate.
  The sequence has 2 Gate 1 failures and 2 Gate 2 failures, so neither separate counter reaches 3.
- **Level and needs:** Integration. Stub verifier, stub model. No network, no container, no human.

### TT-REV-003 A revised package goes through Gate 1 again

- **Traces to:** `ARCHITECTURE.md` 6 (`REVISING` to `GENERATING` to `VALIDATING`).
- **Purpose:** Show that a repair after a Gate 2 failure cannot skip the execution checks.
- **Fixture:** A stub verifier that returns Gate 1 `pass`, Gate 2 `fail`, Gate 1 `pass`, Gate 2 `pass`.
  The stub verifier records the order of its calls.
- **Steps:**
  1. Run CHECK to completion.
  2. Read the recorded call order.
- **Expected result:** The call order is Gate 1, Gate 2, Gate 1, Gate 2.
  The final state is `PACKAGE_APPROVAL` and the last verdict has `total_revisions` 1.
- **What breaks this test:** After a Gate 2 failure the loop returns directly to Gate 2.
  A revision of the script then reaches publication with no Gate 1 run.
- **Level and needs:** Integration. Stub verifier, stub model. No network, no container, no human.

### TT-REV-004 The contract is not changed during repair

- **Traces to:** `ARCHITECTURE.md` 6 ("It never weakens or refines the acceptance contract"); `AGENTS.md` 2.5.
- **Purpose:** Show that the repair step has no write path to the contract.
- **Fixture:** Approved `FX-GOLDEN`.
  A stub model whose revision response also contains a full contract JSON with `acceptance_checks` reduced to Case A.
- **Steps:**
  1. Record the hash of `.maga/state/contracts/cand_vite_strict_port_001.json`.
  2. Run one revision round.
  3. Record the hash again, and read `Package.contract`.
- **Expected result:** The two hashes are equal.
  `Package.contract.acceptance_checks` has 4 entries.
  Gate 1 of the next round runs the same 4 cases.
- **What breaks this test:** The revision handler parses the complete model response into a `Package`, which includes the weaker contract.
- **Level and needs:** Integration. Stub model, stub verifier. No network, no container, no human.

### TT-REV-005 A contract change ends the repair loop

- **Traces to:** `ARCHITECTURE.md` 6 ("Modifying the contract itself invalidates the candidate and terminates the autonomous repair loop, requiring fresh human/triage review").
- **Purpose:** Show that the loop detects a change to the approved contract.
- **Fixture:** A candidate in `REVISING` with `total_revisions` 1.
  The test changes the text of `invariants[0]` in the contract file.
- **Steps:**
  1. Request the transition `REVISING` to `GENERATING`.
  2. Read the state and the generator call count.
- **Expected result:** The transition fails with an error that reports a contract change.
  The generator double records no call.
  The candidate cannot reach `PACKAGE_APPROVAL` without a new approval.
  The state that the candidate enters is not defined (see OQ-T14).
- **What breaks this test:** The loop compares the contract with the approved contract only at the first BUILD.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-REV-006 The revision request contains the failure logs and not the tests

- **Traces to:** `ARCHITECTURE.md` 6 (`REVISING` to `GENERATING`: "Self-correction prompt with failure logs (script/skill only; contract fixed)").
- **Purpose:** Show what the revision request contains and what it changes.
- **Fixture:** A Gate 1 `fail` verdict with `stderr_log` `FAILLOG_MARKER_001 Case C: listener found on 5175`.
  Staged tests that contain the marker `TESTFILE_MARKER_001`.
- **Steps:**
  1. Run one revision round with the stub model.
  2. Read the recorded revision request.
  3. Compare the staged files before and after.
- **Expected result:** The request contains `FAILLOG_MARKER_001`.
  Only `scripts/start.py` or `SKILL.md` changed.
  `tests/test_start.py` is unchanged.
- **What breaks this test:** The revision request omits the verdict logs.
  A revision step that writes all three package files also breaks the test.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

## Independent test synthesis

### TT-IND-001 The test-generator request never contains the script

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 3; `AGENTS.md` 2.6.
- **Purpose:** Show that the test generator sees the contract and the repository constraints only.
- **Fixture:** Approved `FX-GOLDEN`.
  The stub model returns a script that contains the marker `SCRIPT_MARKER_001` for a script request.
  The stub model tags each request by route.
- **Steps:**
  1. Run BUILD.
  2. Read every request on the test-generator route.
- **Expected result:** A minimum of one test-generator request exists.
  No test-generator request contains `SCRIPT_MARKER_001`.
  Each test-generator request contains the 4 `acceptance_checks` entries.
- **What breaks this test:** BUILD generates the script first and adds it to the test request "for context".
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-IND-002 BUILD uses two separate model calls

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 3 ("Two separate model calls are dispatched from the approved `Contract`").
- **Purpose:** Show that one model response cannot produce both the script and its tests.
- **Fixture:** As TT-IND-001.
- **Steps:**
  1. Run BUILD.
  2. Count the requests for each route.
  3. Compare the message history of the two requests.
- **Expected result:** One test-generator request and one script-generator request exist.
  Neither request contains the response of the other request.
- **What breaks this test:** One agent conversation produces the script and then the tests in a later turn of the same history.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-IND-003 The script is absent from the test route during repair

- **Traces to:** `AGENTS.md` 2.6 ("never the generated script"); `ARCHITECTURE.md` 6.
- **Purpose:** Show that the separation holds in revision rounds.
- **Fixture:** As TT-IND-001, with a stub verifier that returns Gate 1 `fail` two times and then `pass`.
  Each revised script contains `SCRIPT_MARKER_002` or `SCRIPT_MARKER_003`.
- **Steps:**
  1. Run BUILD and CHECK.
  2. Read every request on the test-generator route for the complete run.
- **Expected result:** No test-generator request contains a script marker.
  The count of test-generator requests is 1, because the tests stay fixed during repair.
- **What breaks this test:** The revision round generates the tests again with the failed script in the request.
- **Level and needs:** Integration. Stub model, stub verifier. No network, no container, no human.

## Acceptance suite strength

These tests check the acceptance suite and not the script.
The suite under test is the reference suite for `FX-GOLDEN`, and later each generated suite.
A suite must pass the reference script and fail each broken variant.
Run these tests in a container, because they bind the ports 5173, 5174, and 4000.

### TT-ACC-001 The suite passes the reference script

- **Traces to:** `ARCHITECTURE.md` 7.2 `acceptance_checks`; 9.1 "Objective".
- **Purpose:** Positive control: show that the suite can pass.
- **Fixture:** `FX-SCRIPT-REF`, `FX-DEMO`.
- **Steps:**
  1. Run the suite against the script.
- **Expected result:** All tests pass.
  The results name the cases A, B, C, and D.
- **What breaks this test:** A suite that needs network access or a fixed process ID, and therefore fails for every script.
  Without this control, the six tests below pass for a suite that always fails.
- **Level and needs:** Integration. Container. No network, no model, no human.

### TT-ACC-002 The suite fails a no-op script

- **Traces to:** `ARCHITECTURE.md` 9.1 "Suite Validity"; here.now one-pager "Prove it works".
- **Purpose:** Show that the suite inspects real outcomes.
- **Fixture:** `FX-SCRIPT-NOOP`.
- **Steps:**
  1. Run the suite against the script.
- **Expected result:** The suite fails.
  Case A, Case B, and Case D fail.
- **What breaks this test:** A suite that asserts only "the exit code is 0".
- **Level and needs:** Integration. Container. No network, no model, no human.

### TT-ACC-003 The suite fails a script that moves to port 5175

- **Traces to:** `ARCHITECTURE.md` 7.2 Case C and `invariants` (first entry); 1.1 empirical evidence.
- **Purpose:** Show that the suite detects the recorded defect: a bind outside the permitted ports.
- **Fixture:** `FX-SCRIPT-AUTOINC`.
- **Steps:**
  1. Run the suite against the script.
- **Expected result:** The suite fails and Case C is in the failed results.
- **What breaks this test:** A Case C test that checks only the stdout JSON and not the listener on port 5175.
- **Level and needs:** Integration. Container. No network, no model, no human.

### TT-ACC-004 The suite fails a script that omits the origin check

- **Traces to:** here.now architecture "Contracts at each boundary", Verifier ("including the observed omission"); `ARCHITECTURE.md` 7.2 `postconditions` (second entry), 8.2 Comparison 1.
- **Purpose:** Show that the suite detects the observed omission.
- **Fixture:** `FX-SCRIPT-SKIPORIGIN`.
  The suite needs a case in which the backend rejects the selected origin, as in FT-VIT-006.
- **Steps:**
  1. Run the suite against the script.
- **Expected result:** The suite fails.
  The failed test is the test that uses the rejecting backend.
- **What breaks this test:** A suite whose backend stub accepts every origin, so the omitted check has no visible effect.
- **Level and needs:** Integration. Container. No network, no model, no human.

### TT-ACC-005 The suite fails a script that starts a duplicate process

- **Traces to:** `ARCHITECTURE.md` 7.2 Case D, `rerun_behaviour`.
- **Purpose:** Show that the suite detects a non-idempotent rerun.
- **Fixture:** `FX-SCRIPT-DUP`.
- **Steps:**
  1. Run the suite against the script.
- **Expected result:** The suite fails and Case D is in the failed results.
- **What breaks this test:** A Case D test that checks only that the second run exits 0.
- **Level and needs:** Integration. Container. No network, no model, no human.

### TT-ACC-006 The suite fails a script that stops an unrelated process

- **Traces to:** `ARCHITECTURE.md` 7.2 `invariants` (third entry); 8.2 Comparison 2.
- **Purpose:** Show that the suite checks an invariant and not only the four cases.
- **Fixture:** `FX-SCRIPT-KILL`.
- **Steps:**
  1. Run the suite against the script.
- **Expected result:** The suite fails.
  The failed test reports that the listener of the test on port 5173 is not alive.
- **What breaks this test:** A Case B test that does not check its own listener after the script ends.
- **Level and needs:** Integration. Container. No network, no model, no human.

### TT-ACC-007 The suite fails a script that edits the CORS allow-list

- **Traces to:** `ARCHITECTURE.md` 7.2 `invariants` (second entry); here.now architecture "What does CORS mean?".
- **Purpose:** Show that the suite detects a weakened security control.
- **Fixture:** `FX-SCRIPT-EDITCORS`.
- **Steps:**
  1. Run the suite against the script.
- **Expected result:** The suite fails.
  The failed test reports a change to `apps/api/src/server.js`.
- **What breaks this test:** A suite that checks only ports and processes and records no file hash.
- **Level and needs:** Integration. Container. No network, no model, no human.

## Gate 1 isolation

### TT-G1I-001 No network is reachable in Gate 1

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 7, 9.1 ("Zero external network access (`--network none`)"); `AGENTS.md` 2.3.
- **Purpose:** Show that the Gate 1 container has no external network.
- **Fixture:** A staged package with `FX-SCRIPT-NET` and a test that asserts exit code 0.
- **Steps:**
  1. Run Gate 1 in the container runner.
  2. Read the verdict.
  3. Inspect the container configuration that the runner used.
- **Expected result:** `outcome` is `fail`, because the script cannot reach `http://example.com/`.
  The container configuration has the network mode `none`.
- **What breaks this test:** The runner starts the container with the default bridge network.
- **Level and needs:** Integration. Container. Network available on the host, so that the test can fail. No model, no human.

### TT-G1I-002 Gate 1 runs offline with baked-in dependencies

- **Traces to:** `ARCHITECTURE.md` 9.1 ("Test fixtures and dependencies are baked in or mounted ephemerally; scripts must execute deterministically offline").
- **Purpose:** Show that a correct package passes with no network.
- **Fixture:** A staged package with `FX-SCRIPT-REF`, and `FX-DEMO`.
- **Steps:**
  1. Disconnect the host from the network, or run on a host with no route.
  2. Run Gate 1 two times.
  3. Compare the two verdicts.
- **Expected result:** Both verdicts have `outcome` `pass`.
  The `test_results` of the two runs name the same cases with the same results.
- **What breaks this test:** The container runs `pnpm install` at the start of each Gate 1 run.
- **Level and needs:** Integration. Container. No network (by design), no model, no human.

### TT-G1I-003 The acceptance checks are outside the editable workspace

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 3, 7, 9.1 "Check Placement".
- **Purpose:** Show that the code under test cannot change its own checks.
- **Fixture:** A staged package with `FX-SCRIPT-TAMPER`.
- **Steps:**
  1. Record the hash of the approved test file.
  2. Run Gate 1.
  3. Read the verdict.
- **Expected result:** `outcome` is `fail`.
  The tests that ran have the recorded hash.
- **What breaks this test:** The runner mounts the complete staging directory as writable and runs the tests from that mount.
- **Level and needs:** Integration. Container. No network, no model, no human.

### TT-G1I-004 Cleanup stops only the owned process

- **Traces to:** here.now architecture "Worked example: start Vite" ("Cleanup: stop only that process"); `ARCHITECTURE.md` 9.1 ("Process cleanup traps provide hygiene").
- **Purpose:** Show that the Gate 1 cleanup does not stop processes that it did not start.
- **Fixture:** The host worktree run.
  Before the run, the test starts its own listener on port 3000 and a second Vite process in a different directory.
- **Steps:**
  1. Run Gate 1 with `FX-SCRIPT-REF`.
  2. Wait for the end of the runner cleanup.
  3. Check the two test processes and the Vite process of the run.
- **Expected result:** Both test processes are alive.
  The Vite process that the script started is stopped.
- **What breaks this test:** A cleanup that stops processes by name or by port.
- **Level and needs:** Integration. No container (host worktree run). No network, no model, no human.

### TT-G1I-005 A host worktree run never counts as a formal Gate 1 result

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 7 ("Host Worktree Run"), 9.1 ("This run never counts as a formal Gate 1 result"); `AGENTS.md` 2.3.
- **Purpose:** Show that an unconfined run cannot move a candidate forward.
- **Fixture:** A candidate in `VALIDATING` with a staged package that contains `FX-SCRIPT-REF`.
- **Steps:**
  1. Run the tests as a host worktree run.
  2. Read the runner output, the working directory of the tests, the verification directory, and the candidate state.
- **Expected result:** The tests run in a clean Git worktree whose path starts with `/tmp/maga_test_`.
  The runner output says that the run was unconfined developer-host execution.
  All tests pass, and the candidate state stays `VALIDATING`.
  No Gate 1 verdict with `outcome` `pass` is stored for this run.
- **What breaks this test:** The host run writes a normal `Verdict`, so the candidate moves to `EVALUATING_REUSE` with no container run.
- **Level and needs:** Integration. No container. No network, no model, no human.

## Gate 2 reuse evaluation

The run criteria come from `ARCHITECTURE.md` 9.2.
A run passes when its transcript contains a call to the script path (`scripts/start.py`) and no direct launch of `vite`.
The run must have no human intervention and no fatal error.
The first version has no turn limit.
The tests use the run transcript format from "Gate 2 run transcript fixtures".

### TT-G2R-001 Each of the 5 runs uses a fresh worktree and a fresh agent

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 8, 9.2 ("5 fresh temporary project worktrees").
- **Purpose:** Show that no run can see the result of another run.
- **Fixture:** `FX-RUNS-5OF5` with the stub agent runner.
  The runner records the working directory, the command line, and the environment of each call.
  In run 1 the runner writes the file `RUN1_LEFTOVER` into its working directory.
- **Steps:**
  1. Run Gate 2.
  2. Read the 5 recorded calls.
- **Expected result:** The runner recorded 5 calls.
  The 5 working directories are different.
  No working directory of runs 2 to 5 contains `RUN1_LEFTOVER`.
  No command line contains a flag that continues or resumes an earlier session.
- **What breaks this test:** The harness creates one worktree and calls the agent 5 times in it.
- **Level and needs:** Integration. Stub agent runner. No network, no model, no container, no human.

### TT-G2R-002 The request does not contain the script name

- **Traces to:** `ARCHITECTURE.md` 9.2 ("without being handed the script name").
- **Purpose:** Show that the agent must discover the skill.
- **Fixture:** `FX-RUNS-5OF5` with the stub agent runner, for the package of `FX-GOLDEN`.
- **Steps:**
  1. Run Gate 2.
  2. Read the prompt and every other argument of the 5 recorded calls.
- **Expected result:** No prompt and no argument contains `start.py`, `scripts/`, `SKILL.md`, or `vite-safe-dev-server`.
  No call adds a system prompt that names the skill.
- **What breaks this test:** The harness adds "Use the vite-safe-dev-server skill" to the prompt to raise the pass rate.
- **Level and needs:** Integration. Stub agent runner. No network, no model, no container, no human.

### TT-G2R-003 Detect the script call in a run transcript

- **Traces to:** `ARCHITECTURE.md` 9.2 "Run Criteria" ("contains a call to the script path (`scripts/start.py`)").
- **Purpose:** Show the positive and negative cases of script-call detection.
- **Fixture:** Parametrised over 4 run transcripts, each based on the successful run.
  Case 1: the successful run, unchanged.
  Case 2: the `tool_call` at `step_index` 3 is `git status`, so the run has no script call.
  Case 3: the `tool_call` at `step_index` 3 is `cat .claude/skills/vite-safe-dev-server/scripts/start.py` (the agent read the script and did not run it).
  Case 4: the script path appears only in a `generic_message` entry with the `content` "I could run scripts/start.py".
- **Steps:**
  1. Evaluate the run.
- **Expected result:** Case 1 is successful.
  Cases 2, 3, and 4 are not successful.
- **What breaks this test:** A detector that searches the complete transcript text for `start.py`.
  That detector accepts cases 3 and 4.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-G2R-006 The 4-of-5 rule and its boundaries

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 8, 9.2 "Pass Threshold".
- **Purpose:** Show the pass rule on both sides of the boundary.
- **Fixture:** Parametrised over the number of successful runs in a set of 5: 0, 3, 4, and 5.
  `FX-RUNS-3OF5`, `FX-RUNS-4OF5`, and `FX-RUNS-5OF5` give the cases 3, 4, and 5.
- **Steps:**
  1. Run Gate 2 with the stub agent runner.
  2. Read the verdict.
- **Expected result:** 0 and 3 successful runs give `outcome` `fail`.
  4 and 5 successful runs give `outcome` `pass`.
  `gate_number` is 2 in each verdict, and `test_results` records all 5 runs.
- **What breaks this test:** The rule `successes / runs > 0.5`, which passes 3 of 5.
  The rule `successes == 5` fails the 4 case.
- **Level and needs:** Integration. Stub agent runner. No network, no model, no container, no human.

### TT-G2R-007 A run that cannot execute is run again once and is not counted

- **Traces to:** `ARCHITECTURE.md` 6 ("A Gate 2 run that could not execute is run again once, and it is not one of the five counted runs"); 9.2.
- **Purpose:** Show that the rule always uses 5 counted runs.
- **Fixture:** A stub agent runner that returns 4 successful runs.
  It raises an API error for the first attempt of run 5, and returns a run with no script call for the second attempt.
- **Steps:**
  1. Run Gate 2.
  2. Read the verdict and the number of runner calls.
- **Expected result:** The runner receives 6 calls.
  `test_results` records 5 counted runs: 4 successful and 1 not successful.
  `outcome` is `pass`.
  The failed attempt is recorded, and it is not one of the 5 counted runs.
- **What breaks this test:** A harness that stops after the fourth success and reports `pass` with 4 of 4.
  A harness that counts the failed attempt gives 4 of 6 or never runs the second attempt.
- **Level and needs:** Integration. Stub agent runner. No network, no model, no container, no human.

### TT-G2R-009 Human intervention or a fatal error fails the run

- **Traces to:** `ARCHITECTURE.md` 9.2 "Run Criteria" ("with no human intervention and no fatal error").
- **Purpose:** Show the two remaining run criteria.
- **Fixture:** Parametrised over 2 variants of the successful run.
  Variant 1 has a second `user_input` entry "yes, go ahead" between `step_index` 2 and 3.
  This entry is a human message and not a tool result.
  Variant 2 has the agent runner exit code 1 after the script call.
- **Steps:**
  1. Evaluate the run.
- **Expected result:** Both variants are not successful.
- **What breaks this test:** The evaluator reads `tool_call` entries only.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-G2R-010 The Gate 2 runner has model API access only and no credentials

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 7, 9.2 "Network Policy"; `AGENTS.md` 2.3.
- **Purpose:** Show the Gate 2 sandbox boundary.
- **Fixture:** A Gate 2 container run in which the agent is replaced by a probe script.
  The host has the files `~/.ssh/PROBE_KEY`, `~/.config/gh/PROBE_HOSTS`, `~/.aws/PROBE_CREDENTIALS`, and `~/.netrc`, all with synthetic content.
  The host environment has the variable `GH_TOKEN` with the value `FAKE_SECRET_VALUE_004`.
- **Steps:**
  1. The probe tries to read each of the four files.
  2. The probe reads the environment variable `GH_TOKEN`.
  3. The probe opens an HTTPS connection to the Anthropic API endpoint and to `https://example.com/`.
  4. The probe starts a listener on the host at port 4100, and tries to connect to it from the container.
  5. The probe sends an HTTP GET to `http://localhost:4000/api/health` inside the container.
- **Expected result:** None of the four files is readable.
  `GH_TOKEN` is not set.
  The connection to the Anthropic API endpoint opens.
  The connection to `https://example.com/` fails.
  The connection to the host listener on port 4100 fails.
  The stub backend inside the container answers on `localhost:4000`.
- **What breaks this test:** The runner mounts the home directory of the user to give the agent its login.
- **Level and needs:** End-to-end. Container and network. No model, no human.

### TT-G2R-011 A direct launch of vite fails the run

- **Traces to:** `ARCHITECTURE.md` 9.2 "Run Criteria" ("and no direct launch of `vite`").
- **Purpose:** Show that a run fails when the agent starts Vite by hand, even if it also calls the script.
- **Fixture:** Parametrised over 3 variants of the successful run.
  Variant 1 adds the `tool_call` `pnpm --dir apps/web exec vite --port 5173` before the script call.
  Variant 2 adds the `tool_call` `npx vite --port 5175` after the script call.
  Variant 3 adds the `tool_call` `cat apps/web/vite.config.ts`, which names Vite and starts nothing.
  The sources do not define the rule that recognises a direct launch (see OQ-T09).
- **Steps:**
  1. Evaluate the run.
- **Expected result:** Variants 1 and 2 are not successful.
  Variant 3 is successful.
- **What breaks this test:** The evaluator returns success as soon as it finds the script call.
  An evaluator that fails every command with the text `vite` fails variant 3.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-G2R-012 Two failed attempts of one run give inconclusive

- **Traces to:** `ARCHITECTURE.md` 6 ("The outcome `inconclusive` means an infrastructure failure only"; `EVALUATING_REUSE` to `INCONCLUSIVE`).
- **Purpose:** Show that an infrastructure failure in Gate 2 is not a fail and uses no revision.
- **Fixture:** A stub agent runner that returns 2 successful runs and then an API error for both attempts of run 3.
  The candidate has `total_revisions` 1.
- **Steps:**
  1. Run Gate 2.
  2. Read the verdict, the candidate state, and the publisher double.
- **Expected result:** `gate_number` is 2 and `outcome` is `inconclusive`.
  `total_revisions` is still 1.
  The candidate state is `INCONCLUSIVE`.
  No revision request occurs and the publisher double records no call.
- **What breaks this test:** The harness records the run as not successful and continues, so the outcome is `fail` or `pass`.
  Both results hide an infrastructure fault behind a verdict about the skill.
- **Level and needs:** Integration. Stub agent runner. No network, no model, no container, no human.

## Publisher

`ARCHITECTURE.md` 2.2 decision 2 binds the package approval to the package hash.
The sources define no hash algorithm and no approval record format (see OQ-T19).
The tests change a package and observe the result, so they need no algorithm name.

### TT-PUB-001 The approval is bound to the package content

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 2 ("binds that approval to the package hash"), 5 (row 6).
- **Purpose:** Show that the approval identifies the content of all package files.
- **Fixture:** A verified package, parametrised over 5 changes after approval.
  Change 1: one byte in `scripts/start.py`.
  Change 2: one byte in `SKILL.md`.
  Change 3: one byte in `tests/test_start.py`.
  Change 4: a new file `scripts/extra.sh`.
  Change 5: no change (control).
- **Steps:**
  1. Approve the package.
  2. Apply the change.
  3. Ask the publisher if the approval is valid.
- **Expected result:** The approval is not valid for changes 1 to 4.
  The approval is valid for change 5.
- **What breaks this test:** The hash covers `scripts/start.py` only, so changes 2, 3, and 4 stay approved.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PUB-002 An approval does not move to a different package

- **Traces to:** `ARCHITECTURE.md` 2.1 (`PROPOSE`: "Checks human approval bound to the exact package"), 5 (row 6).
- **Purpose:** Show that an approval belongs to one candidate and one content.
- **Fixture:** Two verified packages for the candidates `cand_a` and `cand_b`.
  Only `cand_a` is approved.
- **Steps:**
  1. Copy the approval record of `cand_a` to `cand_b`.
  2. Run the publisher for `cand_b`.
- **Expected result:** The publisher refuses to publish `cand_b`.
- **What breaks this test:** The publisher checks that an approval record exists and does not compare its content binding.
- **Level and needs:** Integration. Local Git. No network, no model, no container, no human.

### TT-PUB-003 Only approved files are committed

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 2 ("commits only approved files"), 5 (row 6).
- **Purpose:** Show that the commit contains the approved package and nothing else.
- **Fixture:** An approved package.
  The target repository working tree also has an untracked file `notes.txt` and a modified tracked file `README.md`.
  `.maga/state/` exists and the target repository has no `.gitignore`.
- **Steps:**
  1. Run the publisher with a local bare remote and a stub pull-request service.
  2. List the paths in the commit with `git show --name-only`.
- **Expected result:** The commit contains the approved package files and the documented evidence files only.
  The commit does not contain `notes.txt`, `README.md`, or a path below `.maga/state/`.
  The content of each committed package file equals the approved content.
- **What breaks this test:** The publisher stages files with `git add -A` or `git commit -a`.
- **Level and needs:** Integration. Local Git. No network, no model, no container, no human.

### TT-PUB-004 The read-back detects a difference

- **Traces to:** `ARCHITECTURE.md` 2.1 (`PROPOSE`: "reads back the result"), 5 (row 6).
- **Purpose:** Show that the read-back is a check and not a log line.
- **Fixture:** An approved package.
  A stub pull-request service, parametrised over 3 read-back responses.
  Response 1: the pull request with the same files and head commit.
  Response 2: a pull request whose head commit differs from the pushed commit.
  Response 3: an HTTP 404 error.
- **Steps:**
  1. Run the publisher.
  2. Read the publisher result.
- **Expected result:** Response 1 gives success and the pull-request URL.
  Responses 2 and 3 give a failure that names the difference.
  The candidate is not reported as published for responses 2 and 3.
- **What breaks this test:** The publisher ignores the read-back response.
- **Level and needs:** Integration. Local Git. No network, no model, no container, no human.

### TT-PUB-005 The publisher requires a Gate 2 pass verdict for the same package

- **Traces to:** `ARCHITECTURE.md` 5 (row 6: inputs "Verified `Package` + `Verdict`"), 6; here.now architecture "One application. Six steps." ("Publish only after a pass and approval").
- **Purpose:** Show that the publisher checks the verdict itself.
- **Fixture:** An approved package, parametrised over 4 verdict states.
  State 1: no verdict file.
  State 2: Gate 1 `pass` only.
  State 3: Gate 2 `fail`.
  State 4: Gate 2 `pass`.
- **Steps:**
  1. Run the publisher.
- **Expected result:** States 1, 2, and 3 give a refusal and no branch.
  State 4 gives a publication.
- **What breaks this test:** The publisher trusts its caller and does not read the verdict.
- **Level and needs:** Integration. Local Git. No network, no model, no container, no human.

## Observability

These tests capture Logfire records in memory with a test exporter.
They need no Logfire account and no network.

### TT-OBS-001 Records carry the candidate ID

- **Traces to:** here.now architecture "Technology choices", Pydantic Logfire ("Link records by candidate ID").
- **Purpose:** Show that one candidate can be traced across the stages.
- **Fixture:** A pipeline run for `FX-GOLDEN` from DECIDE to the Gate 2 verdict, with stub model and stub agent runner.
- **Steps:**
  1. Capture all spans and logs.
  2. Group them by stage.
- **Expected result:** A minimum of one record exists for each of DECIDE, BUILD, CHECK Gate 1, and CHECK Gate 2.
  Each of these records has an attribute with the value `cand_vite_strict_port_001`.
  The attribute name is not defined by the sources (see OQ-T20).
- **What breaks this test:** The candidate ID is set on the first span only and child spans of other stages do not inherit it.
- **Level and needs:** Integration. Stub model, stub agent runner. No network, no human.

### TT-OBS-002 Records contain no raw transcript text

- **Traces to:** here.now architecture "Technology choices", Pydantic Logfire ("Exclude raw transcripts, configuration contents, and secrets"); here.now one-pager "Keep control".
- **Purpose:** Show that model-call instrumentation does not export prompts that contain excerpts.
- **Fixture:** The sessions of FT-PUB-004, which contain `TRANSCRIPT_CANARY_SENTENCE_001`.
- **Steps:**
  1. Run the pipeline from the reader to the end of DECIDE and capture all records.
  2. Serialise each record with all attributes to text.
  3. Search for `TRANSCRIPT_CANARY_SENTENCE_001`.
- **Expected result:** The stub model received the sentence, which shows that the pipeline processed it.
  No captured record contains the sentence.
- **What breaks this test:** The default model instrumentation records the full prompt and the full response.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-OBS-003 Records contain no secret and no configuration content

- **Traces to:** here.now architecture "Technology choices", Pydantic Logfire.
- **Purpose:** Show the same guarantee for secrets and configuration.
- **Fixture:** The secret sessions of FT-RED-001 and the configuration fixture of FT-RED-002.
  The test also makes one stage raise an exception whose message contains a `command_line`.
- **Steps:**
  1. Run the pipeline and capture all records, which include the exception record.
  2. Search the serialised records for the three secret values and for `CONFIG_CANARY_VALUE_001`.
- **Expected result:** No record contains a searched value.
- **What breaks this test:** An exception handler that logs the raw line that it could not parse.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-OBS-004 Records contain timing, token use, and failures

- **Traces to:** here.now architecture "Technology choices", Pydantic Logfire ("Trace stages, model calls, tool calls, timing, token use, and failures").
- **Purpose:** Show that a failure is visible in the trace.
- **Fixture:** A BUILD run in which the stub model reports 120 input tokens and 45 output tokens.
  A second run in which the stub model raises a timeout.
- **Steps:**
  1. Capture the records of both runs.
- **Expected result:** Run 1 has a model-call record with the token counts 120 and 45 and a duration.
  Run 2 has a record with an error status that names the timeout.
- **What breaks this test:** The timeout is caught and logged at debug level with no error status.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

## Resource and failure behaviour

### TT-RES-001 A model timeout is a reported failure

- **Traces to:** here.now architecture "Contracts at each boundary", Verifier ("partial failure"); `ARCHITECTURE.md` 11 (Gateway latency risk).
- **Purpose:** Show that a stage does not wait without limit and does not invent a result.
- **Fixture:** A stub model that never answers the contract synthesis request.
  The test sets the model timeout to 1 second.
  The sources define no default timeout (see OQ-T21).
- **Steps:**
  1. Run DECIDE for the P1 candidate.
  2. Measure the elapsed time.
  3. Read the contracts directory and the candidate state.
- **Expected result:** DECIDE ends in less than 10 seconds with an error that names the timeout.
  No contract file exists.
  The candidate state is not `CONTRACTED`.
- **What breaks this test:** The model call has no timeout.
  A fallback that writes the golden contract when the model fails also breaks the test.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-RES-002 Malformed model output is rejected by Pydantic

- **Traces to:** `ARCHITECTURE.md` 10.1 (`maga.contract`: "Pydantic Schema Validation"); 7.1 `Contract`.
- **Purpose:** Show that an invalid contract never enters the state store.
- **Fixture:** Parametrised over `FX-MODEL-BADJSON` and `FX-MODEL-MISSING`.
- **Steps:**
  1. Run DECIDE with the stub model response.
  2. Read the contracts directory and the candidate state.
- **Expected result:** No contract file exists in either case.
  The error for `FX-MODEL-MISSING` names the field `invariants`.
  The candidate state is not `CONTRACTED` and no approval request is shown.
- **What breaks this test:** DECIDE fills a missing field with an empty list and continues.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-RES-003 A schema-valid contract without the essential requirements is rejected

- **Traces to:** `ARCHITECTURE.md` 10.1 "Schema Validation vs. Semantic & Behavioral Correctness", item 1.
- **Purpose:** Show that schema validation is not the only contract check.
- **Fixture:** `FX-MODEL-STRIPPED`.
- **Steps:**
  1. Run DECIDE with the stub model response.
  2. Read the result of the semantic completeness evaluation.
- **Expected result:** Pydantic validation succeeds.
  The semantic completeness evaluation fails.
  The failure names the absent requirements: the refusal to weaken CORS and the permitted port bounds.
  No approval request is shown.
- **What breaks this test:** DECIDE has the schema check only.
  The terse-output Gateway rule can then remove the invariants with no visible effect.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-RES-004 A partial package is never reported as built

- **Traces to:** here.now architecture "Contracts at each boundary", Verifier ("partial failure"); `ARCHITECTURE.md` 7.1 `Package` (three required paths).
- **Purpose:** Show that BUILD completes fully or reports a failure.
- **Fixture:** Approved `FX-GOLDEN`.
  The stub model answers the script request and raises an error for the test request.
- **Steps:**
  1. Run BUILD.
  2. Read the BUILD result, the candidate state, and the staging directory.
- **Expected result:** BUILD reports a failure.
  No `Package` record exists.
  The candidate state is not `VALIDATING`.
  Gate 1 does not start.
- **What breaks this test:** BUILD returns a `Package` whose `test_path` names a file that does not exist.
  Gate 1 then collects zero tests.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-RES-005 Zero collected tests is not a pass

- **Traces to:** `ARCHITECTURE.md` 9.1 "Objective" ("satisfies all 4 acceptance cases"); 7.1 `Verdict.outcome`.
- **Purpose:** Show that Gate 1 cannot pass when it exercises nothing.
- **Fixture:** A staged package with `FX-SCRIPT-REF`, parametrised over 2 test files.
  File 1 is empty.
  File 2 has 4 tests that are all marked as skipped.
- **Steps:**
  1. Run Gate 1.
  2. Read the verdict.
- **Expected result:** `outcome` is not `pass` in either case.
  The candidate state is not `EVALUATING_REUSE`.
- **What breaks this test:** The verifier maps the pytest exit code "no tests collected" or "all skipped" to `pass`.
- **Level and needs:** Integration. Container. No network, no model, no human.

### TT-RES-006 A failed stage does not report success for the pipeline

- **Traces to:** here.now one-pager "The idea" ("The script performs the required steps or reports where it stopped"); `ARCHITECTURE.md` 6.
- **Purpose:** Show that the pipeline result reflects the worst stage result.
- **Fixture:** A corpus with two candidates.
  Candidate 1 reaches `PROPOSED`.
  Candidate 2 fails in BUILD because the stub model raises an error.
- **Steps:**
  1. Run the full pipeline for the corpus.
  2. Read the pipeline result and its exit status.
- **Expected result:** The result lists candidate 1 as `PROPOSED` and candidate 2 as failed, with the stage name `BUILD`.
  The pipeline does not report complete success.
  The exit status value is not defined (see OQ-T01).
- **What breaks this test:** A loop that catches the exception, logs it, and continues, and then prints "done".
- **Level and needs:** Integration. Stub model, stub agent runner. No network, no human.

## Open questions

Each open question blocks a test or forces an assumption.
The identifiers are stable, so the list has gaps where the sources closed a question.

1. **OQ-T01:** The sources name the modules but no functions, no command-line interface, and no exit status values.
2. **OQ-T02:** `ARCHITECTURE.md` 3.2 maps `sessionId` to `session_id` and `uuid` to `entry_id`.
   It does not say how `step_index` is made, because a Claude Code line has no index.
   It does not give the `source` value of a `tool_result` entry.
   It does not say how one line with several content blocks becomes entries, because `uuid` is one value for the line.
   It does not say if READ imports subagent lines (`isSidechain` `true`).
3. **OQ-T03:** The sources do not define the reader behaviour for a malformed line.
   This blocks TT-PAR-004.
4. **OQ-T05:** `Entry` has no field that links the parts of a split result, and no source gives the size limit.
   This blocks part of TT-PAR-007.
5. **OQ-T06:** The sources do not define the placeholder names for timestamps, process IDs, commit hashes, and UUIDs.
6. **OQ-T07:** No source defines a normalisation rule for ticket identifiers, pull-request numbers, branch names, or plain integers.
   This blocks TT-NRM-009 and TT-NRM-010.
7. **OQ-T08:** The sources do not define the sequence length or contiguity.
   They do not define `Evidence.observed_occurrences` for repeats inside one session.
   They do not say if `Candidate.command_sequence` holds the original or the normalised commands.
   `ARCHITECTURE.md` 11 leaves open if the threshold of 3 sessions applies to corrections and error-and-fix pairs.
8. **OQ-T09:** The sources do not define the rule that recognises "a direct launch of `vite`" or "a fatal error" in a run transcript.
9. **OQ-T10:** The sources do not list the stderr error patterns of the error-and-fix rule.
   This blocks TT-EFX-006.
10. **OQ-T11:** The sources define no token budget, overlap size, tokeniser, or content of the unfinished-task summary.
    No schema in `ARCHITECTURE.md` 7.1 describes a chunk.
11. **OQ-T12:** The three secret patterns and the placeholder are defined for the Gateway guardrail only.
    The pattern set of the reader redactor is not defined.
12. **OQ-T14:** No schema has a field for the state machine state.
    `CLARIFICATION_REQUESTED` and `FIX_AT_SOURCE` have no exit.
    The state after a contract change during repair is not defined.
13. **OQ-T19:** The sources define no hash algorithm, no approval record format, and no approval storage path.
14. **OQ-T20:** The sources define no Logfire attribute names.
15. **OQ-T21:** The sources define no model timeout, no retry rule for a model call, and no Gate 1 or Gate 2 time limit.
    `inputs.timeout_seconds` 15 in the golden contract belongs to the generated script only.

## Source conflicts

The identifiers are stable, so the list has gaps where the sources closed a conflict.

1. **SC-T02 Storage.**
   The here.now architecture page uses SQLite for checkpoints, candidates, and results.
   `ARCHITECTURE.md` 2.2 decision 6 and 7 use local JSON files and no SQLite.
   TT-STO-001 asserts that no database file exists.
2. **SC-T04 Normalisation scope.**
   `ARCHITECTURE.md` 5 (row 2) lists "ports, paths, hashes, timestamps".
   `ARCHITECTURE.md` 5.1 rule 4 adds process IDs and UUIDs.
   The here.now page says "normalise variable values" and names no type.
   No source names ticket identifiers or pull-request numbers.
3. **SC-T05 Gate 1 executor.**
   The here.now architecture page says a model execution agent runs bounded tools in isolation.
   `ARCHITECTURE.md` 2.2 decision 7 and 9.1 say that Gate 1 is model-free.
   This file follows `ARCHITECTURE.md`.
4. **SC-T09 Gate 1 case count.**
   `ARCHITECTURE.md` 9.1 says Gate 1 verifies "all 4 acceptance cases".
   That count belongs to the Vite golden contract.
   A different contract, such as the worktree contract, can have a different count.
