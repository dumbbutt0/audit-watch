#!/usr/bin/env python3
"""
_common.py — shared primitives for the submission-readiness gate.

This module is deliberately self-contained: it imports nothing from the
detection pipeline (no audit_context, no output/, no data/triage/). The
submission layer only ever consumes submission_candidate.json files it is
explicitly pointed at.

Verdict model
-------------
Each gate emits one of four verdict levels (precedence high -> low):

    FAIL        fatally unfit                 -> DO_NOT_SUBMIT
    NEEDS_PROOF salvageable but under-proven  -> NEEDS_MORE_PROOF
    WARN        residual uncertainty          -> READY_FOR_HUMAN_REVIEW
    PASS        clean                         -> READY_TO_SUBMIT_AFTER_APPROVAL

The aggregated status is the highest-precedence verdict across all gates.
human_approval_required is ALWAYS true; the layer has no auto-submit path.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# --- verdict vocabulary -----------------------------------------------------

PASS = "PASS"
WARN = "WARN"
NEEDS_PROOF = "NEEDS_PROOF"
FAIL = "FAIL"

# higher number = more severe / higher precedence
_VERDICT_RANK = {PASS: 0, WARN: 1, NEEDS_PROOF: 2, FAIL: 3}

# gate verdict -> overall recommended status
_STATUS_FOR_VERDICT = {
    PASS: "READY_TO_SUBMIT_AFTER_APPROVAL",
    WARN: "READY_FOR_HUMAN_REVIEW",
    NEEDS_PROOF: "NEEDS_MORE_PROOF",
    FAIL: "DO_NOT_SUBMIT",
}

STATUSES = (
    "DO_NOT_SUBMIT",
    "NEEDS_MORE_PROOF",
    "READY_FOR_HUMAN_REVIEW",
    "READY_TO_SUBMIT_AFTER_APPROVAL",
)

ROOT = Path(__file__).resolve().parent.parent  # the submission/ directory
SCHEMA_PATH = ROOT / "schemas" / "submission_candidate.schema.json"

# --- severity / impact model ------------------------------------------------

SEVERITY_RANK = {
    "Informational": 0,
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4,
}

# Maximum severity an impact category can support WITHOUT a runnable, passing
# PoC. A runnable+passing PoC plus a quantified asset_delta can lift the
# ceiling by one notch (handled in the impact/severity gate). Anchored to
# Immunefi v2.2: insolvency/MEV=Critical, temp freeze=High, DoS=Medium.
IMPACT_SEVERITY_CEILING = {
    "fund_loss": "Critical",
    "governance_takeover": "Critical",
    "accounting_corruption": "High",
    "reward_extraction": "High",
    "fund_freeze": "High",
    "liveness_failure": "Medium",
    "dos": "Medium",
    "info": "Informational",
}

# --- gate result ------------------------------------------------------------


@dataclass
class GateResult:
    gate: int
    name: str
    verdict: str
    reason: str = ""
    tag: str | None = None
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "gate": self.gate,
            "name": self.name,
            "verdict": self.verdict,
            "reason": self.reason,
            "tag": self.tag,
            "detail": self.detail,
        }


def aggregate(results: list[GateResult]) -> dict:
    """Collapse per-gate verdicts into a single recommended status.

    The overall verdict is the highest-precedence gate verdict; the status is
    derived from it. Bias is conservative: a single FAIL blocks, and any
    NEEDS_PROOF outranks a WARN so we favor NEEDS_MORE_PROOF over a risky
    READY_FOR_HUMAN_REVIEW.
    """
    if not results:
        # Nothing evaluated -> never assume good.
        return {
            "recommended_status": "NEEDS_MORE_PROOF",
            "overall_verdict": NEEDS_PROOF,
            "human_approval_required": True,
            "blockers": ["no gates evaluated"],
            "warnings": [],
            "needs_proof": [],
            "gates": [],
        }

    worst = max(results, key=lambda r: _VERDICT_RANK[r.verdict]).verdict
    status = _STATUS_FOR_VERDICT[worst]

    blockers = [r.reason for r in results if r.verdict == FAIL]
    needs_proof = [r.reason for r in results if r.verdict == NEEDS_PROOF]
    warnings = [r.reason for r in results if r.verdict == WARN]

    return {
        "recommended_status": status,
        "overall_verdict": worst,
        # invariant: human approval is mandatory regardless of status.
        "human_approval_required": True,
        "blockers": blockers,
        "needs_proof": needs_proof,
        "warnings": warnings,
        "gates": [r.to_dict() for r in results],
    }


# --- candidate / schema loading --------------------------------------------


def load_candidate(path: str | Path) -> dict:
    """Load a submission_candidate.json file."""
    p = Path(path)
    return json.loads(p.read_text())


def load_schema() -> dict:
    """Load the candidate JSON schema. Returns {} if unreadable (non-fatal)."""
    try:
        return json.loads(SCHEMA_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def required_nonempty_fields() -> list[str]:
    """Fields the evidence gate enforces as non-empty (shared with schema)."""
    schema = load_schema()
    return schema.get("x_gate_required_nonempty") or [
        "root_cause",
        "affected_contracts",
        "affected_functions",
        "call_trace",
        "evidence_links",
    ]


def validate_schema(candidate: dict) -> list[str]:
    """Validate candidate against the Draft-07 schema.

    Returns a list of human-readable error strings ([] = valid). Degrades
    gracefully (returns []) with a printed note if jsonschema is unavailable,
    mirroring the rest of the codebase.
    """
    schema = load_schema()
    if not schema:
        return ["schema file missing or unreadable: " + str(SCHEMA_PATH)]
    try:
        import jsonschema  # type: ignore
    except ImportError:
        print("[submission_gate] jsonschema not installed; skipping schema validation")
        return []
    # Guard against a broken / stub jsonschema (e.g. the placeholder 0.0.0 that
    # exposes no Draft7Validator): degrade gracefully rather than crash.
    if not hasattr(jsonschema, "Draft7Validator"):
        print("[submission_gate] jsonschema is a stub/broken install (no Draft7Validator); "
              "skipping schema validation")
        return []
    try:
        validator = jsonschema.Draft7Validator(schema)
        errors = []
        for err in sorted(validator.iter_errors(candidate), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.path) or "(root)"
            errors.append(f"{loc}: {err.message}")
        return errors
    except Exception as e:  # broken validator backend — do not block on tooling failure
        print(f"[submission_gate] schema validation unavailable ({e}); skipping")
        return []


# --- small text helpers shared by gates ------------------------------------


def is_empty(value) -> bool:
    """True if value is None, empty string/whitespace, empty list/dict, or a
    dict whose every value is itself empty."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, set)):
        return len(value) == 0
    if isinstance(value, dict):
        return all(is_empty(v) for v in value.values())
    return False


def text_blob(*values) -> str:
    """Flatten arbitrary values into one lowercase string for keyword search."""
    parts: list[str] = []

    def _walk(v):
        if v is None:
            return
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                _walk(x)
        elif isinstance(v, (list, tuple, set)):
            for x in v:
                _walk(x)
        else:
            parts.append(str(v))

    for val in values:
        _walk(val)
    return " ".join(parts).lower()


def contains_any(blob: str, keywords: list[str]) -> list[str]:
    """Return the keywords present in blob."""
    return [k for k in keywords if k in blob]
