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

- "Stub model" means a test double that replaces every model.
  It returns a fixed response and it records every request that it receives.
- "Model-bound payload" means the complete request that MAGA sends to a model or to the Gateway.
- "Stub agent runner" means a test double that replaces `claude -p` and `agy --print`.
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
| Transcript parsing | `TT-PAR` | 8 | `ARCHITECTURE.md` 3.2, 5; here.now architecture "Contracts at each boundary", "Discovery, ranking, and long sessions" |
| Normalisation | `TT-NRM` | 10 | `ARCHITECTURE.md` 5.1 rule 4 |
| Sequence counting | `TT-SEQ` | 7 | `ARCHITECTURE.md` 5.1 rule 1 |
| Error-and-fix detection | `TT-EFX` | 6 | `ARCHITECTURE.md` 5.1 rule 2 |
| User-correction detection | `TT-COR` | 4 | `ARCHITECTURE.md` 5.1 rule 3 |
| Chunking | `TT-CHK` | 6 | here.now architecture "Discovery, ranking, and long sessions" |
| Redactor | `TT-RDX` | 8 | `ARCHITECTURE.md` 10.1; here.now one-pager "Keep control" |
| State storage | `TT-STO` | 5 | `ARCHITECTURE.md` 7; `AGENTS.md` 2.2 |
| State machine | `TT-STM` | 5 | `ARCHITECTURE.md` 6 |
| Revision budget and fixed contract | `TT-REV` | 6 | `ARCHITECTURE.md` 2.2, 6; `AGENTS.md` 2.5 |
| Independent test synthesis | `TT-IND` | 3 | `ARCHITECTURE.md` 2.2; `AGENTS.md` 2.6 |
| Acceptance suite strength | `TT-ACC` | 7 | here.now one-pager "Prove it works"; `ARCHITECTURE.md` 7.2 |
| Gate 1 isolation | `TT-G1I` | 5 | `ARCHITECTURE.md` 9, 9.1 |
| Gate 2 reuse evaluation | `TT-G2R` | 10 | `ARCHITECTURE.md` 2.2, 9.2 |
| Publisher | `TT-PUB` | 5 | here.now architecture "Contracts at each boundary", Publisher |
| Observability | `TT-OBS` | 4 | here.now architecture "Technology choices", Pydantic Logfire |
| Resource and failure behaviour | `TT-RES` | 6 | `ARCHITECTURE.md` 7.1, 10.1; here.now architecture "Contracts at each boundary" |
| Total | | 119 | |

## Shared synthetic fixtures

All paths are relative to the repository root.
The fixture IDs that start with `FX-AG`, `FX-GOLDEN`, `FX-DEMO`, `FX-SCRIPT`, and `FX-RUNS` are defined in [FUNCTIONAL_TESTS.md](FUNCTIONAL_TESTS.md).
This file adds these fixtures.

| Fixture ID | Intended path | Content |
| :--- | :--- | :--- |
| `FX-SCHEMA-MIN` | `tests/fixtures/schemas/minimal/<model>.json` | One JSON object for each of the 7 models, with all required fields and no optional field |
| `FX-AG-MALFORMED` | `tests/fixtures/transcripts/antigravity_malformed/sess-m/` | 5 lines, of which line 3 is the text `{"step_index": 2, "source":` |
| `FX-AG-OVERSIZE` | `tests/fixtures/transcripts/antigravity_oversize/sess-o/` | One command whose `GENERIC` result has 2000 lines of the form `LINE-0001` to `LINE-2000` |
| `FX-AG-LONG` | `tests/fixtures/transcripts/antigravity_long/sess-l/` | One `USER_INPUT` step and 40 commands `echo step-01` to `echo step-40`, each with a result (81 lines) |
| `FX-SCRIPT-AUTOINC` | `tests/fixtures/scripts/variants/autoincrement.sh` | `FX-SCRIPT-REF` without strict port binding |
| `FX-SCRIPT-DUP` | `tests/fixtures/scripts/variants/duplicate_on_rerun.sh` | `FX-SCRIPT-REF` without the check for a running instance |
| `FX-SCRIPT-KILL` | `tests/fixtures/scripts/variants/kills_unrelated.sh` | `FX-SCRIPT-REF` that stops the process on a busy permitted port |
| `FX-SCRIPT-EDITCORS` | `tests/fixtures/scripts/variants/edits_cors.sh` | `FX-SCRIPT-REF` that adds `http://localhost:5175` to `apps/api/src/server.js` |
| `FX-SCRIPT-TAMPER` | `tests/fixtures/scripts/variants/tampers_with_tests.sh` | `FX-SCRIPT-NOOP` that first overwrites every file below `tests/` with a test that always passes |
| `FX-SCRIPT-NET` | `tests/fixtures/scripts/variants/needs_network.sh` | A script that sends an HTTP GET to `http://example.com/` and exits 0 only if it gets a response |
| `FX-MODEL-BADJSON` | `tests/fixtures/model_responses/contract_not_json.txt` | The text `Here is the contract you asked for` |
| `FX-MODEL-MISSING` | `tests/fixtures/model_responses/contract_missing_field.json` | `FX-GOLDEN` without the key `invariants` |
| `FX-MODEL-STRIPPED` | `tests/fixtures/model_responses/contract_stripped.json` | `FX-GOLDEN` with `invariants` set to `[]` and `acceptance_checks` reduced to Case A |

### Gate 2 run transcript fixtures

Each Gate 2 run fixture is a JSON list of `Entry` objects, plus the turn count of the run.
The sources do not define the raw output format of `claude -p` or how to count a turn (see OQ-T09).
The stub agent runner therefore returns parsed `Entry` lists and a turn count.

A successful run has these entries, in this order, and a turn count of 2.

| `step_index` | `entry_type` | Key field |
| ---: | :--- | :--- |
| 0 | `user_input` | `content`: "Start the web frontend and verify backend connectivity" |
| 1 | `tool_call` | `command_line`: `cat .agents/skills/vite-safe-dev-server/SKILL.md` |
| 2 | `tool_result` | `exit_code`: 0 |
| 3 | `tool_call` | `command_line`: `bash .agents/skills/vite-safe-dev-server/scripts/start.sh` |
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
  `Evidence`: `session_ids`, `observed_occurrences`, `baseline_turns_mean`, `baseline_tokens_mean`.
  `Candidate`: `candidate_id`, `title`, `command_sequence`, `normalized_template`, `frequency`, `evidence`.
  `Contract`: `candidate_id`, `workflow_name`, `intent`, `inputs`, `preconditions`, `permitted_changes`, `postconditions`, `invariants`, `rerun_behaviour`, `failure_behaviour`, `acceptance_checks`.
  `Package`: `candidate_id`, `script_path`, `skill_path`, `test_path`, `contract`.
  `Verdict`: `candidate_id`, `gate_number`, `outcome`, `total_revisions`, `test_results`, `stdout_log`, `stderr_log`, `execution_duration_ms`, `timestamp`.
- **Steps:**
  1. Remove the one field from the minimal object.
  2. Validate the object.
- **Expected result:** Validation raises a Pydantic `ValidationError` in all 46 cases.
  The error names the removed field.
- **What breaks this test:** A developer gives `Contract.invariants` the default `[]` to make a model response validate.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SCH-003 Entry rejects values outside its enums

- **Traces to:** `ARCHITECTURE.md` 7.1 `Entry`.
- **Purpose:** Show that `source` and `entry_type` are closed sets.
- **Fixture:** The minimal `Entry`, parametrised over 4 changes.
  `source` = `MODEL` (raw Antigravity value), `source` = `assistant`, `entry_type` = `PLANNER_RESPONSE`, `entry_type` = `message`.
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

### TT-SCH-006 Candidate rejects an unknown triage status

- **Traces to:** `ARCHITECTURE.md` 7.1 `Candidate.triage_status`.
- **Purpose:** Show that `triage_status` is a closed set of four values.
- **Fixture:** The minimal `Candidate`, parametrised over the values `fix_at_source`, `reuse`, `CONTRACTED`, and `approved`.
- **Steps:**
  1. Set `triage_status` to the value.
  2. Validate the object.
- **Expected result:** Validation fails in all 4 cases.
  The values `pending`, `accepted`, `rejected`, and `clarification_needed` validate.
- **What breaks this test:** A developer adds a fifth value without a change to `ARCHITECTURE.md`.
  This test then fails and points to OQ-T04.
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
  `Entry.args` is `{"CommandLine": "git status", "WaitMsBeforeAsync": 5000, "RunPersistent": true}`.
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

### TT-PAR-001 Map the three Antigravity step types to Entry fields

- **Traces to:** `ARCHITECTURE.md` 3.2, 7.1 `Entry`.
- **Purpose:** Show the field mapping for one step of each raw type.
- **Fixture:** The first three lines of `FX-AG-A`.
- **Steps:**
  1. Parse the three lines with the Antigravity parser of `maga.reader`.
  2. Read the three `Entry` objects.
- **Expected result:** Entry 0 has `source` `user`, `entry_type` `user_input`, and `content` "Start the web frontend."
  Entry 1 has `source` `model`, `entry_type` `tool_call`, `tool_name` `run_command`, and `working_dir` `/home/dev_a/workspace`.
  Entry 1 has `command_line` equal to the raw `CommandLine` value.
  Entry 2 has `entry_type` `tool_result` and `exit_code` 0, read from "The command exited with code 0."
  Each `timestamp` equals the raw `created_at` instant.
  The mapping of `GENERIC` to `tool_result` is an assumption (see OQ-T02).
- **What breaks this test:** The parser reads `args.command` and not `args.CommandLine`, so `command_line` is `None`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-002 Preserve the original entry identifiers

- **Traces to:** `ARCHITECTURE.md` 3.2 "monotonic integer `step_index`"; here.now architecture "Discovery, ranking, and long sessions" ("Preserve original entry IDs").
- **Purpose:** Show that the parser keeps the raw identifier and does not number the entries again.
- **Fixture:** A copy of `FX-AG-A` from which the lines with `step_index` 3 and 4 are removed.
  The remaining raw values are 0, 1, 2, 5, 6.
- **Steps:**
  1. Parse the file.
  2. Read `step_index` and `entry_id` of each entry.
- **Expected result:** The `step_index` values are 0, 1, 2, 5, 6.
  The 5 `entry_id` values are unique.
  A second parse of the same file gives the same 5 `entry_id` values.
- **What breaks this test:** The parser sets `step_index` from the line number, which gives 0 to 4.
  A random UUID for `entry_id` also breaks the test.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-003 Pair a tool call with its result

- **Traces to:** `ARCHITECTURE.md` 3.2 "Tool execution results in subsequent `GENERIC` steps"; 5.1 rule 2 (needs the exit code of a command).
- **Purpose:** Show that the exit code of a result attaches to the correct command.
- **Fixture:** A session with two commands.
  Command 1 is `vite` with the result "The command exited with code 1."
  Command 2 is `vite --port 5174` with the result "The command exited with code 0."
  One `USER_INPUT` step is between the first result and the second command.
- **Steps:**
  1. Parse the file.
  2. Request the paired view (command and result) from the reader or the finder (see OQ-T01).
- **Expected result:** `vite` pairs with `exit_code` 1.
  `vite --port 5174` pairs with `exit_code` 0.
  The `USER_INPUT` step pairs with nothing.
- **What breaks this test:** The pairing takes "the next entry", so an inserted user step shifts the results by one.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-004 A malformed line

- **Status:** `BLOCKED` by OQ-T03.
  The sources do not say if the reader skips and reports the line, or fails the import.
- **Traces to:** here.now architecture "Contracts at each boundary", Reader ("mark missing data as unknown").
- **Purpose:** Show that a malformed line never disappears without a report.
- **Fixture:** `FX-AG-MALFORMED`.
- **Steps:**
  1. Run the reader on `sess-m`.
  2. Read the import result and the stored entries.
- **Expected result:** One of two results is correct, and the sources do not select one.
  Result 1: the import fails, names line 3, and stores no checkpoint past line 2.
  Result 2: the import stores the 4 valid entries and the import result names line 3 as malformed.
  In both results the reader does not raise an unhandled exception and does not report a clean import.
- **What breaks this test:** A bare `except: continue` around the JSON parse, which drops line 3 with no report.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-005 Mark missing data as unknown

- **Traces to:** here.now architecture "Contracts at each boundary", Reader; `ARCHITECTURE.md` 7.1 `Entry` optional fields.
- **Purpose:** Show that the parser does not invent a value for absent data.
- **Fixture:** One `GENERIC` result whose `content` is "Output:\nstill running" with no exit code text.
  One `PLANNER_RESPONSE` whose `args` has `CommandLine` and no `Cwd`.
- **Steps:**
  1. Parse the two lines.
  2. Read `exit_code` of the result entry and `working_dir` of the call entry.
- **Expected result:** `exit_code` is `None`.
  `working_dir` is `None`.
- **What breaks this test:** The parser sets `exit_code` to 0 when it finds no exit code.
  That default turns an unknown result into a success for the error-and-fix rule.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-006 Import once

- **Traces to:** `ARCHITECTURE.md` 3.2, 7 (`import_checkpoints.json`); here.now architecture "Contracts at each boundary", Reader ("import each entry once").
- **Purpose:** Show idempotent import at the storage boundary.
- **Fixture:** `FX-AG-A`.
- **Steps:**
  1. Run the reader three times on `sess-a`.
  2. Read `.maga/state/entries/sess-a.json` and count the entries for each `step_index`.
- **Expected result:** The file has 7 entries.
  Each `step_index` from 0 to 6 appears one time.
  Runs 2 and 3 report 0 new entries.
- **What breaks this test:** The checkpoint is written before the entries, and the entries write then appends on each run.
- **Level and needs:** Integration. No network, no model, no container, no human.

### TT-PAR-007 Split an oversized result into linked parts

- **Status:** `BLOCKED` in part by OQ-T05.
  `Entry` has no field for a part link, and the sources define no size limit.
- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Split oversized results into linked parts rather than silently dropping content").
- **Purpose:** Show that a large result loses no content.
- **Fixture:** `FX-AG-OVERSIZE`.
  The test sets the size limit to a value that forces a minimum of 3 parts.
- **Steps:**
  1. Run the reader and the chunker on `sess-o`.
  2. Collect the parts of the result in order.
  3. Join the part texts.
- **Expected result:** The result has a minimum of 3 parts.
  The joined text contains each of `LINE-0001` to `LINE-2000` one time and in order.
  Each part refers to the same source `step_index`.
  The field that links the parts is not defined.
- **What breaks this test:** The reader truncates the result at the limit and adds "[truncated]".
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PAR-008 Parse a Claude Code transcript

- **Status:** `BLOCKED` by OQ-T02.
  The sources give no raw line schema for `~/.claude/projects/*/*.jsonl`.
- **Traces to:** `ARCHITECTURE.md` 2.2 decision 1, 5 (row 1).
- **Purpose:** Show the field mapping for the primary transcript format.
- **Fixture:** Not defined.
- **Steps:**
  1. Parse one user line, one tool-call line, and one tool-result line.
  2. Read the three `Entry` objects.
- **Expected result:** The three entries validate, with `entry_type` `user_input`, `tool_call`, and `tool_result`.
  The raw field names are not defined.
- **What breaks this test:** Only the Antigravity parser exists.
- **Level and needs:** Unit. No network, no model, no container, no human.

## Normalisation

Each test calls the normalisation function of `maga.finder` on command text.
Several tests compare two normalised results and do not assert a literal placeholder.
`ARCHITECTURE.md` 5.1 rule 4 names two placeholders only: `$REPO_ROOT` and `$PORT_LIST`.

### TT-NRM-001 Normalise an absolute path to a repository token

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 4 "File & Directory Paths".
- **Purpose:** Show the documented path example.
- **Fixture:** The command `ls /home/user/workspace/apps/web` with the working directory `/home/user/workspace`.
  The rule that finds the repository root is not defined (see OQ-T06), so the working directory equals the root.
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
- **Fixture:** `FX-AG-A`, `FX-AG-B`, `FX-AG-C`.
- **Steps:**
  1. Run the reader.
  2. Record a hash of each file in `.maga/state/entries/`.
  3. Run FIND.
  4. Record the hashes again.
  5. Read `command_line` of the entry with `step_index` 3 in `sess-b`.
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
- **Fixture:** `FX-AG-A`, `FX-AG-B`, `FX-AG-C`.
- **Steps:**
  1. Run the reader.
  2. Run the sequence counter of `maga.finder` with no model.
  3. Read the flagged sequences.
- **Expected result:** One sequence is flagged and it is the normalised P1 sequence.
  Its distinct-session count is 3.
- **What breaks this test:** The comparison is `> 3` and not `>= 3`.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-002 Two distinct sessions do not reach the threshold

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1.
- **Purpose:** Show the lower side of the threshold boundary.
- **Fixture:** `FX-AG-TWO`.
- **Steps:**
  1. Run the reader and the sequence counter.
  2. Read the flagged sequences.
- **Expected result:** No sequence is flagged.
- **What breaks this test:** The threshold constant is 2, as the diagram in `ARCHITECTURE.md` 4 states (see SC-T03).
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-003 Many repeats in one session do not reach the threshold

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1 ("distinct sessions").
- **Purpose:** Show that the counter counts sessions.
- **Fixture:** `FX-AG-ONE` (P1 five times in `sess-d`).
- **Steps:**
  1. Run the reader and the sequence counter.
  2. Read the flagged sequences.
- **Expected result:** No sequence is flagged.
- **What breaks this test:** The counter adds 1 for each occurrence and not for each session.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-004 Repeats in one session plus two other sessions

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1; 7.1 `Evidence.session_ids`.
- **Purpose:** Show that a repeat in one session does not change the session list.
- **Fixture:** `FX-AG-ONE` (5 occurrences in `sess-d`), `FX-AG-A`, and `FX-AG-B`.
- **Steps:**
  1. Run the reader and FIND with the stub model.
  2. Read the candidate.
- **Expected result:** One candidate exists.
  `evidence.session_ids` has 3 entries: `sess-a`, `sess-b`, `sess-d`, each one time.
  The values of `frequency` and `evidence.observed_occurrences` (3 or 7) are not defined (see OQ-T08).
- **What breaks this test:** `session_ids` is a list with one entry for each occurrence, so `sess-d` appears 5 times.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-SEQ-005 The same session imported from two locations counts one time

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1 ("distinct sessions"); here.now architecture "Discovery, ranking, and long sessions" ("remove duplicate evidence by source reference").
- **Purpose:** Show that a copied transcript does not create a false third session.
- **Fixture:** `FX-AG-A`, `FX-AG-B`, and a second copy of the `sess-a` directory with the same session ID in a different parent directory.
- **Steps:**
  1. Run the reader on both parent directories.
  2. Run the sequence counter.
- **Expected result:** No sequence is flagged.
  The distinct-session count for P1 is 2.
- **What breaks this test:** The counter uses the file path and not `session_id` as the session key.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-006 A different command order is a different sequence

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 1 ("identical normalised command sequence").
- **Purpose:** Show that the counter compares ordered sequences.
- **Fixture:** `FX-AG-A`, `FX-AG-B`, and a session `sess-r` with the three P1 commands in reverse order.
- **Steps:**
  1. Run the reader and the sequence counter.
  2. Read the flagged sequences.
- **Expected result:** The P1 sequence of three commands is not flagged.
- **What breaks this test:** The counter compares sorted command sets.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-SEQ-007 Sequence counting needs no model

- **Traces to:** here.now one-pager "The idea" ("Count command sequences without a model"); here.now architecture "Discovery, ranking, and long sessions".
- **Purpose:** Show that the first discovery step is deterministic and costs no tokens.
- **Fixture:** `FX-AG-A`, `FX-AG-B`, `FX-AG-C`.
  A stub model that fails the test when it receives a request.
- **Steps:**
  1. Run the reader and the sequence counter two times.
  2. Compare the two results.
- **Expected result:** The stub model receives no request.
  The two results are equal.
- **What breaks this test:** The counter asks a model to decide if two commands are "the same".
- **Level and needs:** Unit. No network, no container, no human.

## Error-and-fix pair detection

The rule is in `ARCHITECTURE.md` 5.1 rule 2.
A pair is a failed step, followed within 3 subsequent tool actions by a command with modified parameters or flags that exits 0.
Each fixture below is a list of commands with exit codes, written as one Antigravity session.

### TT-EFX-001 Detect the documented example

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2, example.
- **Purpose:** Show the positive case from the source.
- **Fixture:** `vite` (exit 1), `lsof -i :5173` (exit 0), `vite --port 5174` (exit 0).
- **Steps:**
  1. Run the reader and the error-and-fix detector.
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
  1. Run the reader and the detector.
- **Expected result:** One pair is detected: `vite` and `vite --port 5174`.
- **What breaks this test:** The window is 2 actions.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-EFX-003 The fix is the fourth subsequent action

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2.
- **Purpose:** Show the outer side of the distance boundary.
- **Fixture:** `vite` (exit 1), `lsof -i :5173` (exit 0), `cat packages/config/ports.json` (exit 0), `git status` (exit 0), `vite --port 5174` (exit 0).
- **Steps:**
  1. Run the reader and the detector.
- **Expected result:** No pair is detected.
- **What breaks this test:** The window has no upper limit.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-EFX-004 An identical retry is not a fix

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2 ("a command modifying parameters/flags").
- **Purpose:** Show that the fix must change the command.
- **Fixture:** `vite` (exit 1), `vite` (exit 0).
- **Steps:**
  1. Run the reader and the detector.
- **Expected result:** No pair is detected.
- **What breaks this test:** The detector accepts any later command with the same program name and exit code 0.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-EFX-005 A modified command that fails is not a fix

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2 ("and exiting 0").
- **Purpose:** Show that the fix must succeed.
- **Fixture:** `vite` (exit 1), `vite --port 5174` (exit 1).
  A second variant in which the result of `vite --port 5174` has no exit code text.
- **Steps:**
  1. Run the reader and the detector on each variant.
- **Expected result:** No pair is detected in either variant.
- **What breaks this test:** The detector checks `exit_code != 1`, so an unknown exit code counts as a success.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-EFX-006 An error pattern on stderr with exit code 0

- **Status:** `BLOCKED` by OQ-T10.
  The rule says "non-zero exit code or stderr error pattern", but no source lists the patterns.
- **Traces to:** `ARCHITECTURE.md` 5.1 rule 2.
- **Purpose:** Show that a failed step with exit code 0 can start a pair.
- **Fixture:** `vite` (exit 0, output "error: Port 5173 is in use"), `vite --port 5174` (exit 0).
- **Steps:**
  1. Run the reader and the detector.
- **Expected result:** Not defined until the pattern list exists.
- **What breaks this test:** When the pattern list exists: a detector that reads `exit_code` only and ignores the output text.
- **Level and needs:** Unit. No network, no model, no container, no human.

## User-correction detection

### TT-COR-001 Flag the step before a correction

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 3.
- **Purpose:** Show that the defect is the agent step before the user message.
- **Fixture:** One session of `FX-AG-CORR` (procedure P3).
  The stub model classifies the message as a correction.
- **Steps:**
  1. Run the reader and the correction detector.
  2. Read the detected corrections.
- **Expected result:** One correction is detected.
  The flagged step has `command_line` `kill -9 4242`.
  The flagged step is not `lsof -i :5173`.
- **What breaks this test:** The detector flags the step after the user message.
- **Level and needs:** Unit. Stub model. No network, no container, no human.

### TT-COR-002 An ordinary user message is not a correction

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 3 ("explicitly intervenes with a corrective instruction").
- **Purpose:** Show the negative case.
- **Fixture:** A session with `pnpm test` (exit 0), the `USER_INPUT` "Thanks. Now run the linter.", and `pnpm lint` (exit 0).
  The stub model classifies the message as not a correction.
- **Steps:**
  1. Run the reader and the correction detector.
- **Expected result:** No correction is detected and no step is flagged as a defect.
- **What breaks this test:** The detector treats every mid-session `USER_INPUT` as a correction.
- **Level and needs:** Unit. Stub model. No network, no container, no human.

### TT-COR-003 A model rejection stops the promotion

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 3 ("semantically validated using Gemini prompt classification before candidate promotion").
- **Purpose:** Show that the model classification is a gate and not a log entry.
- **Fixture:** `FX-AG-CORR` (3 sessions).
  The stub model classifies the message "don't kill that process" as not a correction.
- **Steps:**
  1. Run the reader and FIND.
  2. Read the candidates directory.
- **Expected result:** No candidate exists that has the correction as evidence.
- **What breaks this test:** FIND uses a keyword match on "don't" and ignores the classification result.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-COR-004 The correction reaches the contract as an invariant

- **Traces to:** `ARCHITECTURE.md` 5.1 rule 3 ("uses the correction to formulate negative constraints and invariants in the contract").
- **Purpose:** Show that the correction text is an input to contract synthesis.
- **Fixture:** `FX-AG-CORR` with the stub model as classifier and as contract synthesiser.
- **Steps:**
  1. Run the reader, FIND, and TRIAGE.
  2. Read the contract synthesis request that the stub model recorded.
- **Expected result:** The request contains the correction "don't kill that process" or the candidate's pitfall record of it.
- **What breaks this test:** TRIAGE sends only `command_sequence` to the synthesiser.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

## Chunking

The chunking rules come from the here.now architecture page only.
The sources define no token budget, no overlap size, and no tokeniser (see OQ-T11).
Each test sets the budget and the overlap itself.
Each test measures tokens with the token counter of the implementation.

### TT-CHK-001 No chunk exceeds the token budget

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("A chunk is a bounded group of transcript entries. Split by token budget").
- **Purpose:** Show that the budget is an upper limit.
- **Fixture:** `FX-AG-LONG`, with a budget that is about one quarter of the token count of the session.
- **Steps:**
  1. Run the reader and the chunker.
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
  1. Collect the `step_index` values of all chunks.
  2. Compare the set with the `step_index` values of the session.
- **Expected result:** The two sets are equal (81 entries: 1 user step, 40 calls, 40 results).
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
  The entries in the overlap keep their original `step_index` values.
  The content of the "short summary of unfinished tasks" is not defined (see OQ-T11).
- **What breaks this test:** The overlap setting is read but not applied.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-CHK-005 Evidence is deduplicated by source reference

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Join task fragments and remove duplicate evidence by source reference").
- **Purpose:** Show that the overlap does not count one entry two times.
- **Fixture:** `FX-AG-A`, `FX-AG-B`, and one long session in which P1 occurs one time across a chunk boundary.
  The overlap makes the P1 commands appear in two chunks of that session.
- **Steps:**
  1. Run the reader, the chunker, and FIND with the stub model.
  2. Read the candidate for P1.
- **Expected result:** `evidence.session_ids` has 3 entries.
  The long session contributes one occurrence of P1 and not two.
- **What breaks this test:** Evidence is keyed by chunk number and not by `session_id` plus `step_index`.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-CHK-006 No model request contains the whole transcript

- **Traces to:** here.now architecture "Discovery, ranking, and long sessions" ("Do not send the whole transcript in one request", "Retrieve only the source excerpts needed for each candidate").
- **Purpose:** Show that model input is bounded.
- **Fixture:** `FX-AG-LONG` three times with different session IDs, so that a candidate exists.
  Each of the 40 commands has a unique text `echo step-NN`.
- **Steps:**
  1. Run the reader and FIND with the stub model.
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
  For `args`, the secret is the value of the key `Env` inside the raw `args` object.
- **Steps:**
  1. Run the reader on the line.
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
- **Fixture:** `FX-AG-INJECT`, whose tool result contains the marker `INJECTION_CANARY`.
- **Steps:**
  1. Run the reader, FIND, and TRIAGE with the stub model.
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
  `.maga/artifacts/staged/<candidate_id>/SKILL.md`, `scripts/start.sh`, and `tests/test_start.py`.
  Each JSON file validates against its model.
  No file with the extension `.db` or `.sqlite` exists.
- **What breaks this test:** A stage keeps its records in memory and writes nothing.
- **Level and needs:** Integration. Stub model, stub agent runner. No network, no human.

### TT-STO-002 Resume from a checkpoint after an interrupted import

- **Traces to:** `ARCHITECTURE.md` 3.2 ("incremental using monotonic integer `step_index` watermarks"), 7 (`import_checkpoints.json`).
- **Purpose:** Show that an interrupted import completes on the next run with no loss and no duplicate.
- **Fixture:** `FX-AG-LONG` (81 lines).
  The test makes the entry store raise an error when it receives the entry with `step_index` 40.
- **Steps:**
  1. Run the reader and observe the error.
  2. Remove the injected error.
  3. Run the reader again.
  4. Read `.maga/state/entries/sess-l.json`.
- **Expected result:** Step 1 reports a failure and not a success.
  After step 3 the file has 81 entries.
  Each `step_index` from 0 to 80 appears one time.
- **What breaks this test:** The checkpoint is written before the entries.
  The second run then starts after `step_index` 40, and the entries from the failed batch are lost.
- **Level and needs:** Integration. No network, no model, no container, no human.

### TT-STO-003 The checkpoint is per session

- **Traces to:** `ARCHITECTURE.md` 7 ("Ingest watermarks per session").
- **Purpose:** Show that the watermark of one session does not hide entries of another session.
- **Fixture:** `FX-AG-LONG` (`step_index` up to 80) and `FX-AG-A` (`step_index` up to 6).
- **Steps:**
  1. Run the reader on `sess-l` only.
  2. Run the reader on `sess-l` and `sess-a`.
  3. Read `.maga/state/entries/sess-a.json`.
- **Expected result:** `sess-a.json` has 7 entries.
- **What breaks this test:** One global watermark of 80, which makes every `sess-a` entry look old.
- **Level and needs:** Integration. No network, no model, no container, no human.

### TT-STO-004 State is below the gitignored directory

- **Traces to:** `AGENTS.md` 2.2 ("All state is persisted as local JSON files under `.maga/state/` (gitignored)").
- **Purpose:** Show that Git cannot pick up state files.
- **Fixture:** A clone of the MAGA repository, and `FX-AG-A`.
- **Steps:**
  1. Run `git check-ignore -q .maga/state/entries/sess-a.json` in the clone.
  2. Run the reader on `sess-a` with the clone as the project directory.
  3. Run `git status --porcelain --untracked-files=all`.
  4. Compare the list of all files in the clone before and after step 2.
- **Expected result:** `git check-ignore` exits with code 0.
  `git status` prints no path that starts with `.maga/`.
  Every new file is below `.maga/`.
  The sources do not say if `.maga/artifacts/` is ignored (see OQ-T13).
- **What breaks this test:** The `.gitignore` entry is absent, or the reader writes a cache file next to the source code.
- **Level and needs:** Integration. Git. No network, no model, no container, no human.

### TT-STO-005 A corrupt state file is rejected at load

- **Traces to:** `ARCHITECTURE.md` 7.1; `AGENTS.md` 1 Beat 2 ("Enforce schema invariants with Pydantic").
- **Purpose:** Show that a stage validates what it loads.
- **Fixture:** A valid candidate file in which `evidence.session_ids` is changed to `null`.
- **Steps:**
  1. Run TRIAGE for the candidate.
- **Expected result:** TRIAGE fails with a validation error that names `evidence.session_ids`.
  The stub model receives no request.
- **What breaks this test:** The loader uses `model_construct` or a plain `json.load` with no validation.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

## Candidate state machine

`ARCHITECTURE.md` 6 defines 13 states.
The states are `DISCOVERED`, `TRIAGED`, `REJECTED`, `CLARIFICATION_REQUESTED`, `CONTRACTED`, `GENERATING`, `VALIDATING`, `REVISING`, `UNVERIFIED`, `EVALUATING_REUSE`, `PROPOSED`, `HUMAN_APPROVED`, and `MERGED`.
No schema in `ARCHITECTURE.md` 7.1 has a field for the state (see OQ-T14).

### TT-STM-001 Every legal transition is accepted

- **Traces to:** `ARCHITECTURE.md` 6, state diagram.
- **Purpose:** Show that the implementation permits each documented transition.
- **Fixture:** Parametrised over the 16 transitions between named states.
  `DISCOVERED` to `TRIAGED`.
  `TRIAGED` to `REJECTED`, `TRIAGED` to `CLARIFICATION_REQUESTED`, `TRIAGED` to `CONTRACTED`.
  `CONTRACTED` to `GENERATING`.
  `GENERATING` to `VALIDATING`.
  `VALIDATING` to `REVISING`, `VALIDATING` to `UNVERIFIED`, `VALIDATING` to `EVALUATING_REUSE`.
  `EVALUATING_REUSE` to `REVISING`, `EVALUATING_REUSE` to `UNVERIFIED`, `EVALUATING_REUSE` to `PROPOSED`.
  `REVISING` to `GENERATING`.
  `PROPOSED` to `HUMAN_APPROVED`, `PROPOSED` to `REJECTED`.
  `HUMAN_APPROVED` to `MERGED`.
- **Steps:**
  1. Create a candidate in the source state with the guard data that the transition needs.
  2. Request the transition.
  3. Read the state.
- **Expected result:** The state equals the target state in all 16 cases.
  A new candidate starts in `DISCOVERED`.
- **What breaks this test:** A transition table that omits `EVALUATING_REUSE` to `REVISING`, so a Gate 2 failure cannot use the budget.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-STM-002 Every other transition is rejected

- **Traces to:** `ARCHITECTURE.md` 6, state diagram.
- **Purpose:** Show that the documented transitions are the only transitions.
- **Fixture:** Parametrised over every ordered pair of the 13 states that is not in TT-STM-001.
  This gives 153 pairs (169 pairs minus 16 legal pairs), and it includes each state to itself.
  The test generates the pairs from the legal list and the state list.
- **Steps:**
  1. Create a candidate in the source state.
  2. Request the transition.
  3. Read the state.
- **Expected result:** Each request fails with an error that names both states.
  The state is unchanged.
  The list includes these important cases.
  `TRIAGED` to `GENERATING` (skips the contract).
  `GENERATING` to `EVALUATING_REUSE` (skips Gate 1).
  `VALIDATING` to `PROPOSED` (skips Gate 2).
  `UNVERIFIED` to `PROPOSED` and `UNVERIFIED` to `REVISING` (leaves a final state).
  `REVISING` to `VALIDATING` (tests a package that was not generated again).
- **What breaks this test:** A `set_state` function that accepts any value.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-STM-003 The final states have no exit

- **Traces to:** `ARCHITECTURE.md` 6 ("permanently terminates without creating a pull request").
- **Purpose:** Show that `REJECTED`, `UNVERIFIED`, and `MERGED` are final.
- **Fixture:** One candidate in each of the three states.
- **Steps:**
  1. Request a transition to each of the 13 states.
  2. Try to run BUILD, CHECK, and the publisher for the candidate.
- **Expected result:** Every request fails.
  No stage starts and the publisher double records no call.
  `CLARIFICATION_REQUESTED` also has no documented exit (see OQ-T14).
- **What breaks this test:** A "retry" command that moves `UNVERIFIED` back to `GENERATING` with a new budget.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-STM-004 The approval guard on CONTRACTED to GENERATING

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 2; `AGENTS.md` 2.4.
- **Purpose:** Show that the transition needs the human approval of the contract and the checks.
- **Fixture:** A `CONTRACTED` candidate with `FX-GOLDEN`.
  Parametrised over 3 cases: no approval, approval of a different contract content, and approval of the exact contract content.
- **Steps:**
  1. Request the transition to `GENERATING`.
- **Expected result:** Cases 1 and 2 fail and the state stays `CONTRACTED`.
  Case 3 succeeds.
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
  Case 4 gives `UNVERIFIED`, and the revision counter stays 0.
  Case 5 gives `EVALUATING_REUSE`, because a pass needs no budget.
- **What breaks this test:** `inconclusive` is handled as `fail`, so case 4 goes to `REVISING` and uses the budget.
- **Level and needs:** Unit. No network, no model, no container, no human.

## Revision budget and fixed contract

`MAX_TOTAL_REVISIONS = 3`.
The counter increments when a gate failure sends the candidate to `REVISING`.
A gate failure with `total_revisions >= 3` sends the candidate to `UNVERIFIED`.
These tests follow the state diagram in `ARCHITECTURE.md` 6 (see OQ-T15 for the second reading of the text).

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
  The final state is `PROPOSED` and the last verdict has `total_revisions` 1.
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
  The candidate cannot reach `PROPOSED` without a new approval.
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
  Only `scripts/start.sh` or `SKILL.md` changed.
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

- **Traces to:** here.now one-pager "Prove it works" ("The acceptance suite must reject a no-op script").
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

- **Traces to:** here.now architecture "Technology choices", Disposable containers ("Keep acceptance checks outside the agent's editable workspace").
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

- **Traces to:** here.now architecture "Worked example: start Vite" ("Cleanup: stop only that process"); `ARCHITECTURE.md` 9.1 ("Process cleanup traps").
- **Purpose:** Show that the Gate 1 cleanup does not stop processes that it did not start.
- **Fixture:** The local fallback runner.
  Before the run, the test starts its own listener on port 3000 and a second Vite process in a different directory.
- **Steps:**
  1. Run Gate 1 with `FX-SCRIPT-REF`.
  2. Wait for the end of the runner cleanup.
  3. Check the two test processes and the Vite process of the run.
- **Expected result:** Both test processes are alive.
  The Vite process that the script started is stopped.
- **What breaks this test:** A cleanup that stops processes by name or by port.
- **Level and needs:** Integration. No container (local fallback). No network, no model, no human.

### TT-G1I-005 The local fallback is labelled as unconfined

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 7 ("Local Fallback"), 9.1 ("Local Subprocess Fallback"); `AGENTS.md` 2.3.
- **Purpose:** Show that a local run does not claim isolation.
- **Fixture:** A staged package with `FX-SCRIPT-REF`, with no container runtime available.
- **Steps:**
  1. Run Gate 1 with the local fallback.
  2. Read the runner output and the working directory of the tests.
- **Expected result:** The tests run in a clean Git worktree whose path starts with `/tmp/maga_test_`.
  The runner output says that the run was unconfined developer-host execution.
  `Verdict` has no field for the runner type, so the place of this label is not defined (see OQ-T16).
- **What breaks this test:** The fallback runs in the MAGA checkout and reports the same text as the container runner.
- **Level and needs:** Integration. No container. No network, no model, no human.

## Gate 2 reuse evaluation

The run criteria come from `ARCHITECTURE.md` 9.2.
A run is successful when the agent inspects `SKILL.md`, invokes `scripts/start.sh`, and verifies the backend handshake.
The run must use 2 turns or fewer, with no human intervention and no fatal error.
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
- **Expected result:** No prompt and no argument contains `start.sh`, `scripts/`, `SKILL.md`, or `vite-safe-dev-server`.
  No call adds a system prompt that names the skill.
- **What breaks this test:** The harness adds "Use the vite-safe-dev-server skill" to the prompt to raise the pass rate.
- **Level and needs:** Integration. Stub agent runner. No network, no model, no container, no human.

### TT-G2R-003 Detect the script call in a run transcript

- **Traces to:** `ARCHITECTURE.md` 9.2 "Run Criteria" ("invoke the script (`scripts/start.sh`)").
- **Purpose:** Show the positive and negative cases of script-call detection.
- **Fixture:** Parametrised over 5 run transcripts, each based on the successful run.
  Case 1: the successful run, unchanged.
  Case 2: the `tool_call` at `step_index` 3 is `pnpm --dir apps/web exec vite --port 5173` (the agent did the work by hand).
  Case 3: the `tool_call` at `step_index` 3 is `cat .agents/skills/vite-safe-dev-server/scripts/start.sh` (the agent read the script and did not run it).
  Case 4: the script path appears only in a `generic_message` entry with the `content` "I could run scripts/start.sh".
  Case 5: the script call exists, and its `tool_result` has `exit_code` 1.
- **Steps:**
  1. Evaluate the run.
- **Expected result:** Case 1 is successful.
  Cases 2, 3, 4, and 5 are not successful.
- **What breaks this test:** A detector that searches the complete transcript text for `start.sh`.
  That detector accepts cases 3, 4, and 5.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-G2R-004 A run must inspect the skill

- **Traces to:** `ARCHITECTURE.md` 9.2 "Run Criteria" ("must inspect the skill via `SKILL.md`").
- **Purpose:** Show that a script call without a skill read is not a successful reuse.
- **Fixture:** The successful run without the entries at `step_index` 1 and 2.
  The sources do not say how a harness observes that an agent loaded a skill (see OQ-T09).
- **Steps:**
  1. Evaluate the run.
- **Expected result:** The run is not successful.
- **What breaks this test:** The evaluator checks the script call only.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-G2R-005 A run must verify the backend handshake

- **Traces to:** `ARCHITECTURE.md` 9.2 "Run Criteria" ("verify the backend handshake").
- **Purpose:** Show that a script call with a failed result is not a success.
- **Fixture:** The successful run in which the `sanitized_output` at `step_index` 4 is the documented error JSON.
  `{"status": "error", "reason": "all_permitted_ports_exhausted", "tried": [5173, 5174]}` with `exit_code` 1.
  The sources do not define the evidence that proves the handshake (see OQ-T09).
- **Steps:**
  1. Evaluate the run.
- **Expected result:** The run is not successful.
- **What breaks this test:** The evaluator ignores the result of the script call.
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

### TT-G2R-007 The rule always uses 5 runs

- **Traces to:** `ARCHITECTURE.md` 9.2 ("Evaluated across 5 fresh temporary project worktrees").
- **Purpose:** Show that the harness cannot pass with fewer runs.
- **Fixture:** A stub agent runner that returns 4 successful runs and then raises an error for run 5.
- **Steps:**
  1. Run Gate 2.
  2. Read the verdict.
- **Expected result:** The harness does not stop after the fourth success without a fifth run attempt.
  The verdict records the failed run 5.
  The `outcome` for a run that could not execute is not defined (see OQ-T17).
- **What breaks this test:** A harness that divides by the number of completed runs.
- **Level and needs:** Integration. Stub agent runner. No network, no model, no container, no human.

### TT-G2R-008 The turn limit

- **Traces to:** `ARCHITECTURE.md` 2.2 decision 8, 9.2 ("within <= 2 turns").
- **Purpose:** Show both sides of the turn boundary.
- **Fixture:** The successful run, parametrised over the turn counts 1, 2, and 3.
  The sources do not define a turn (see OQ-T09), so the fixture gives the turn count as a number.
- **Steps:**
  1. Evaluate the run.
- **Expected result:** The runs with 1 and 2 turns are successful.
  The run with 3 turns is not successful.
- **What breaks this test:** The comparison is `< 2`, or the turn count is not read.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-G2R-009 Human intervention or a fatal error fails the run

- **Traces to:** `ARCHITECTURE.md` 9.2 ("without human intervention or fatal errors").
- **Purpose:** Show the two remaining run criteria.
- **Fixture:** Parametrised over 2 variants of the successful run.
  Variant 1 has a second `user_input` entry "yes, go ahead" between `step_index` 2 and 3.
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
  3. The probe opens an HTTPS connection to a model API endpoint and to `https://example.com/`.
- **Expected result:** None of the four files is readable.
  `GH_TOKEN` is not set.
  The connection to the model API endpoint opens.
  The connection to `https://example.com/` fails.
  "Local loopback inaccessible" conflicts with the backend check on `localhost:4000` (see OQ-T18).
- **What breaks this test:** The runner mounts the home directory of the user to give the agent its login.
- **Level and needs:** End-to-end. Container and network. No model, no human.

## Publisher

The approval of the exact package comes from the here.now pages.
The sources define no hash algorithm and no approval record format (see OQ-T19).
The tests change a package and observe the result, so they need no algorithm name.

### TT-PUB-001 The approval is bound to the package content

- **Traces to:** here.now architecture "Contracts at each boundary", Publisher ("bind approval to the exact package").
- **Purpose:** Show that the approval identifies the content of all package files.
- **Fixture:** A verified package, parametrised over 5 changes after approval.
  Change 1: one byte in `scripts/start.sh`.
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
- **What breaks this test:** The hash covers `scripts/start.sh` only, so changes 2, 3, and 4 stay approved.
- **Level and needs:** Unit. No network, no model, no container, no human.

### TT-PUB-002 An approval does not move to a different package

- **Traces to:** here.now architecture "One application. Six steps.", step 06 ("Check approval for the exact package").
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

- **Traces to:** here.now architecture "Contracts at each boundary", Publisher ("Commit only approved files").
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

- **Traces to:** here.now architecture "Contracts at each boundary", Publisher ("read back the result").
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
- **Fixture:** A pipeline run for `FX-GOLDEN` from TRIAGE to the Gate 2 verdict, with stub model and stub agent runner.
- **Steps:**
  1. Capture all spans and logs.
  2. Group them by stage.
- **Expected result:** A minimum of one record exists for each of TRIAGE, BUILD, CHECK Gate 1, and CHECK Gate 2.
  Each of these records has an attribute with the value `cand_vite_strict_port_001`.
  The attribute name is not defined by the sources (see OQ-T20).
- **What breaks this test:** The candidate ID is set on the first span only and child spans of other stages do not inherit it.
- **Level and needs:** Integration. Stub model, stub agent runner. No network, no human.

### TT-OBS-002 Records contain no raw transcript text

- **Traces to:** here.now architecture "Technology choices", Pydantic Logfire ("Exclude raw transcripts, configuration contents, and secrets"); here.now one-pager "Keep control".
- **Purpose:** Show that model-call instrumentation does not export prompts that contain excerpts.
- **Fixture:** The sessions of FT-PUB-004, which contain `TRANSCRIPT_CANARY_SENTENCE_001`.
- **Steps:**
  1. Run the pipeline from the reader to the end of TRIAGE and capture all records.
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
  1. Run TRIAGE for the P1 candidate.
  2. Measure the elapsed time.
  3. Read the contracts directory and the candidate state.
- **Expected result:** TRIAGE ends in less than 10 seconds with an error that names the timeout.
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
  1. Run TRIAGE with the stub model response.
  2. Read the contracts directory and the candidate state.
- **Expected result:** No contract file exists in either case.
  The error for `FX-MODEL-MISSING` names the field `invariants`.
  The candidate state is not `CONTRACTED` and no approval request is shown.
- **What breaks this test:** TRIAGE fills a missing field with an empty list and continues.
- **Level and needs:** Integration. Stub model. No network, no container, no human.

### TT-RES-003 A schema-valid contract without the essential requirements is rejected

- **Traces to:** `ARCHITECTURE.md` 10.1 "Schema Validation vs. Semantic & Behavioral Correctness", item 1.
- **Purpose:** Show that schema validation is not the only contract check.
- **Fixture:** `FX-MODEL-STRIPPED`.
- **Steps:**
  1. Run TRIAGE with the stub model response.
  2. Read the result of the semantic completeness evaluation.
- **Expected result:** Pydantic validation succeeds.
  The semantic completeness evaluation fails.
  The failure names the absent requirements: the refusal to weaken CORS and the permitted port bounds.
  No approval request is shown.
- **What breaks this test:** TRIAGE has the schema check only.
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
- **Level and needs:** Integration. Container or local fallback. No network, no model, no human.

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

1. **OQ-T01:** The sources name the modules but no functions, no command-line interface, and no exit status values.
2. **OQ-T02:** The sources give no raw line schema for Claude Code transcripts.
   They do not state the mapping from Antigravity `type` and `source` values to `entry_type` and `source` values.
   They do not define how `session_id` and `entry_id` are made.
   This blocks TT-PAR-008.
3. **OQ-T03:** The sources do not define the reader behaviour for a malformed line.
   This blocks TT-PAR-004.
4. **OQ-T04:** `triage_status` has no value for the triage results "fix at source" and "reuse".
5. **OQ-T05:** `Entry` has no field that links the parts of a split result, and no source gives the size limit.
   This blocks part of TT-PAR-007.
6. **OQ-T06:** The sources do not define how the repository root is found for the `$REPO_ROOT` rule.
   They do not define the placeholder names for timestamps, process IDs, commit hashes, and UUIDs.
7. **OQ-T07:** No source defines a normalisation rule for ticket identifiers, pull-request numbers, branch names, or plain integers.
   This blocks TT-NRM-009 and TT-NRM-010.
8. **OQ-T08:** The sources do not define the sequence length, contiguity, or the difference between `Candidate.frequency` and `Evidence.observed_occurrences`.
   They do not say if `Candidate.command_sequence` holds the original or the normalised commands.
9. **OQ-T09:** The sources do not define a "turn", the raw output format of `claude -p`, or the evidence for "inspect the skill" and "verify the backend handshake".
10. **OQ-T10:** The sources do not list the stderr error patterns of the error-and-fix rule.
    This blocks TT-EFX-006.
11. **OQ-T11:** The sources define no token budget, overlap size, tokeniser, or content of the unfinished-task summary.
    No schema in `ARCHITECTURE.md` 7.1 describes a chunk.
12. **OQ-T12:** The three secret patterns and the placeholder are defined for the Gateway guardrail only.
    The pattern set of the reader redactor is not defined.
13. **OQ-T13:** `AGENTS.md` says `.maga/state/` is gitignored.
    No source says the same for `.maga/artifacts/`.
    The repository has no `.gitignore` file at the time of writing.
14. **OQ-T14:** No schema has a field for the state machine state.
    `CLARIFICATION_REQUESTED` has no exit.
    The states after a human refusal and after a contract change are not defined.
    The wrapper-only path and the package approval have no state.
15. **OQ-T15:** `ARCHITECTURE.md` 6 has two readings of the limit.
    The state diagram tests the third revision and ends at the fourth failure.
    The text says the pipeline goes "immediately" to `UNVERIFIED` when the count reaches 3.
    The tests follow the state diagram.
16. **OQ-T16:** `Verdict` has no field that records the runner type (container or unconfined local fallback).
17. **OQ-T17:** The sources do not define when a gate gives `inconclusive`, and they define no transition for a Gate 2 `inconclusive`.
    They do not say if a Gate 2 run that could not execute is a failed run.
18. **OQ-T18:** `ARCHITECTURE.md` 2.2 decision 7 makes local loopback inaccessible in Gate 2.
    The Gate 2 task needs the backend on `http://localhost:4000` inside the sandbox.
    The sources do not say that the rule means the loopback of the host only.
19. **OQ-T19:** The sources define no hash algorithm, no approval record format, and no approval storage path.
20. **OQ-T20:** The sources define no Logfire attribute names.
21. **OQ-T21:** The sources define no model timeout, no retry rule, and no Gate 1 or Gate 2 time limit.
    `inputs.timeout_seconds` 15 in the golden contract belongs to the generated script only.

## Source conflicts

1. **SC-T01 Stage names.**
   The here.now architecture page has six steps: READ, FIND, DECIDE, BUILD, CHECK, PROPOSE.
   `ARCHITECTURE.md` 2.1 and `AGENTS.md` have five stages: `FIND`, `TRIAGE`, `BUILD`, `CHECK`, `SHIP`.
   This file uses the five stage names.
2. **SC-T02 Storage.**
   The here.now architecture page uses SQLite for checkpoints, candidates, and results.
   `ARCHITECTURE.md` 2.2 decision 6 and 7 use local JSON files and no SQLite.
   TT-STO-001 asserts that no database file exists.
3. **SC-T03 Candidate threshold.**
   `ARCHITECTURE.md` 2.1, 5, 5.1, and 12 say `>= 3` distinct sessions.
   The diagram in `ARCHITECTURE.md` 4 says "Threshold >= 2 occurrences".
   TT-SEQ-002 follows `>= 3` distinct sessions.
4. **SC-T04 Normalisation scope.**
   `ARCHITECTURE.md` 5 (row 2) lists "ports, paths, hashes, timestamps".
   `ARCHITECTURE.md` 5.1 rule 4 adds process IDs and UUIDs.
   The here.now page says "normalise variable values" and names no type.
   No source names ticket identifiers or pull-request numbers.
5. **SC-T05 Gate 1 executor.**
   The here.now architecture page says a Gemini execution agent runs bounded tools in isolation.
   `ARCHITECTURE.md` 9.1 runs the tests in a container with no model.
   This file follows `ARCHITECTURE.md` 9.1.
6. **SC-T06 Test location.**
   The here.now page keeps the acceptance checks outside the editable workspace.
   `ARCHITECTURE.md` 7 stages `tests/` next to `scripts/` in one package directory.
   TT-G1I-003 tests the behaviour: the script under test cannot change the checks that run.
7. **SC-T07 Package approval.**
   The here.now pages bind an approval to the exact package before the commit.
   `ARCHITECTURE.md` names contract approval and maintainer review only, and its state machine has no package approval.
   The `TT-PUB` tests trace to the here.now pages.
8. **SC-T08 Model roles.**
   The here.now pages give all model work to Gemini.
   `ARCHITECTURE.md` 10.1 gives contract synthesis to an open-weight model on Modal, and 5.1 rule 3 gives correction classification to Gemini.
   The tests use a stub model for each route and do not depend on the provider.
9. **SC-T09 Gate 1 case count.**
   `ARCHITECTURE.md` 9.1 says Gate 1 verifies "all 4 acceptance cases".
   That count belongs to the Vite golden contract.
   A different contract, such as the worktree contract, can have a different count.
