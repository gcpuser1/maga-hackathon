"""The seven records that cross a stage boundary (ARCHITECTURE.md 7.1)."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Entry(BaseModel):
    """Normalized single interaction step of a Claude Code transcript."""

    entry_id: str
    session_id: str
    step_index: int
    source: Literal["user", "model", "system"]
    entry_type: Literal["user_input", "tool_call", "tool_result", "generic_message"]
    tool_name: str | None = None
    command_line: str | None = None
    working_dir: str | None = None
    args: dict[str, Any] | None = None
    exit_code: int | None = None
    content: str | None = None
    sanitized_output: str | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    timestamp: datetime


class Episode(BaseModel):
    """Extracted sequence of related actions aiming at a specific sub-task or goal."""

    episode_id: str
    session_id: str
    goal: str
    entries: list[Entry]
    success: bool
    repair_iterations: int = 0
    duration_ms: int = 0


class Evidence(BaseModel):
    """Empirical observations justifying automation candidate synthesis."""

    session_ids: list[str]
    observed_occurrences: int
    observed_turns_mean: float  # From historical transcripts: context, not the controlled baseline
    observed_tokens_mean: int
    failure_traces: list[str] = Field(default_factory=list)
    common_pitfalls: list[str] = Field(default_factory=list)


class Candidate(BaseModel):
    """Mined procedure pattern proposed for automation triage."""

    candidate_id: str
    title: str
    command_sequence: list[str]
    normalized_template: str
    frequency: int  # Distinct sessions
    evidence_type: Literal["correction", "error_fix", "repetition"]
    evidence: Evidence
    triage_status: Literal[
        "pending",
        "accepted",
        "reuse_existing",
        "fix_at_source",
        "rejected",
        "clarification_needed",
    ] = "pending"
    rejection_reason: str | None = None


class Contract(BaseModel):
    """Formal specification governing script implementation and independent test synthesis."""

    candidate_id: str
    workflow_name: str
    intent: str = Field(..., description="High-level goal and human summary")
    inputs: dict[str, Any] = Field(..., description="Parameters, defaults, and validation bounds")
    preconditions: list[str] = Field(
        ..., description="Environmental requirements prior to execution"
    )
    permitted_changes: list[str] = Field(
        ..., description="Bounded filesystem/process effects allowed"
    )
    postconditions: list[str] = Field(
        ..., description="Verifiable state upon successful execution"
    )
    invariants: list[str] = Field(
        ..., description="Strict negative constraints (e.g. do not weaken CORS)"
    )
    rerun_behaviour: str = Field(
        ..., description="Idempotent handling when already running/configured"
    )
    failure_behaviour: str = Field(
        ..., description="Safe termination, cleanup traps, and error reporting"
    )
    acceptance_checks: list[str] = Field(..., description="Deterministic test cases for Gate 1")


AutomationContract = Contract


class Package(BaseModel):
    """Staged automation bundle ready for verification and proposal."""

    candidate_id: str
    script_path: str
    skill_path: str
    test_path: str
    contract: Contract


class Verdict(BaseModel):
    """Evaluation outcome for Gate 1 and Gate 2 verification."""

    candidate_id: str
    gate_number: Literal[1, 2]
    outcome: Literal["pass", "fail", "inconclusive"]
    total_revisions: int
    test_results: dict[str, Any]  # Includes no-op and broken-variant rejection results
    stdout_log: str
    stderr_log: str
    token_delta_percent: float | None = None  # Controlled pair only: with and without the skill
    execution_duration_ms: int
    timestamp: datetime
