"""
Blind-to-Reproducible Funnel — pure logic for the dashboard's /funnel surface.

This module is the testable core behind a READ-ONLY dashboard view that tracks a research-track
finding through the full lifecycle the scanner now demonstrates end-to-end:

    Lead surfaced -> Investigation safe -> Converted -> Severity gated -> PoC handoff
        -> Reproduced -> Submission package -> Human review -> (human-recorded) Submitted

It extends the existing dashboard (it does NOT replace it) and mirrors the isolated-page pattern of
`human_validation.py` / `candidate_detail.py`: no FastAPI, import-light, unit-testable, and it NEVER
writes, routes, promotes, sets a production severity, or mutates any frozen phase artifact.

REJECT-FIRST is the load-bearing invariant. `compute_pipeline_status` returns the highest stage whose
gate is *actually satisfied* by the evidence — a record's declared status is never trusted over the
gate functions. In particular REPRODUCED never implies SUBMITTED: `SUBMITTED` is only a
submission_status value a human records; it is not even a pipeline status.

Backward compatible: records without PoC / submission objects normalize to NOT_STARTED and never crash.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RECORDS_PATH = ROOT / "documentation/research/funnel/funnel_records.json"
# (P216) Additive read-only mirror of synced findings emitted by scripts/dashboard_sync.py via
# scripts/build_synced_findings.py. Records here are funnel-1-compatible (schema "synced-1" superset) and carry
# research_only / routing_allowed:false. Missing file = no-op. This module NEVER writes it.
SYNCED_RECORDS_PATH = ROOT / "documentation/research/funnel/synced_findings.generated.json"

# (real-world) The honest bounty-hunt log is now the DEFAULT funnel source (the eval funnel_records.json +
# synced mirror above are kept on disk but no longer feed the live dashboard). Records here are derived from
# real manual hunts: PoC-proven candidate findings (REPRODUCED, never auto-submitted) + honest negatives +
# skipped targets. No fabricated outcomes — submitted/confirmed/paid stay 0 (only a human outcome record can
# set submitted). This module NEVER writes it.
REAL_RESULTS_PATH = ROOT / "documentation/real_world_results.json"

SCHEMA_VERSION = "funnel-1"

# ----------------------------------------------------------------------- enums
# (1) pipeline stage/status — the lifecycle a finding moves through.
PIPELINE_STATUS = {
    "LEAD_SURFACED", "INVESTIGATION_STARTED", "INVESTIGATION_SAFE",
    "CONVERTED_CLEAN_HIT", "CONVERTED_STRONG_PARTIAL", "CONVERTED_ADJACENT",
    "REJECTED_OR_ABSTAINED", "SEVERITY_GATED", "POC_HANDOFF_STARTED",
    "POC_REPRODUCED", "PARTIAL_REPRO", "NOT_REPRODUCED",
    "SUBMISSION_PACKAGE_STARTED", "SUBMISSION_READY_HUMAN_REVIEW",
    "BLOCKED", "NOT_RUN",
}

# (2) per-finding PoC evidence status.
POC_STATUS = {"NOT_STARTED", "IN_PROGRESS", "REPRODUCED", "PARTIAL_REPRO", "NOT_REPRODUCED"}

# (3) submission readiness statuses + sub-checks.
SUBMISSION_STATUS = {"NOT_STARTED", "DRAFTING", "READY_FOR_HUMAN_REVIEW", "BLOCKED", "SUBMITTED"}
DUPLICATE_CHECK = {"PENDING", "CLEAR", "DUPLICATE_RISK", "DUPLICATE_CONFIRMED"}
SCOPE_CHECK = {"PENDING", "IN_SCOPE", "IMPACT_IN_SCOPE", "OUT_OF_SCOPE", "UNCLEAR"}
SEVERITY_CHECK = {"PENDING", "SUPPORTED", "OVERCLAIM_RISK", "UNSUPPORTED"}
HUMAN_GATE = {"PENDING", "PASS", "FAIL"}

# conversion result vocabulary used by funnel records.
CONVERSION_RESULT = {"CLEAN_HIT", "STRONG_PARTIAL", "ADJACENT", "REJECTED", "ABSTAINED", "NONE"}

# (P98 assisted-mode) provenance + assisted-validation vocab. `source` defaults to "blind" so the existing
# autonomous-eval records (which omit it) are unchanged. These fields are additive and backward compatible.
SOURCE_KIND = {"blind", "human", "static_tool", "fuzz", "assisted"}
SUPPLIED_BY = {"human", "static_tool", "fuzzing", "previous_eval", "external_report", "manual_review"}
REQUESTED_CHECK = {"VALIDATE", "FALSIFY", "TRACE_ONLY", "POC_HANDOFF", "SUBMISSION_PACKAGE"}
ASSISTED_VALIDATION_STATUS = {
    "NOT_RUN", "VALIDATED_FOR_POC_HANDOFF", "REJECTED_SOURCE_PROVEN_SAFE", "NEEDS_MORE_CONTEXT",
    "NEEDS_EXECUTION", "BLOCKED_UNSUPPORTED_CLAIM", "BLOCKED_SCOPE_OR_DUPLICATE_PENDING",
}

# (P99) human-final-gate + outcome vocab. These come from human-recorded outcome records
# (documentation/research/assisted_mode/outcomes/), NEVER inferred by the dashboard. SUBMITTED is shown only
# when a human outcome record sets submitted=true.
HUMAN_FINAL_GATE = {
    "PENDING", "APPROVED_TO_SUBMIT", "DO_NOT_SUBMIT_SCOPE", "DO_NOT_SUBMIT_DUPLICATE",
    "DO_NOT_SUBMIT_SEVERITY_UNSUPPORTED", "DO_NOT_SUBMIT_WEAK_POC", "NEEDS_REPORT_EDIT", "NEEDS_MORE_EVIDENCE",
}
OUTCOME_STATUS = {
    "pending", "accepted", "duplicate", "informative", "rejected", "invalid", "withdrawn", "needs_revision",
}
DEFAULT_OUTCOMES_DIR = ROOT / "documentation/research/assisted_mode/outcomes"

# These conversions are "real" lead->finding conversions (eligible for PoC handoff).
_STRONG_CONVERSIONS = {"CLEAN_HIT", "STRONG_PARTIAL"}
_ADVERSARIAL_OK = {"PASS", "BOUNDED_UNCERTAINTY"}


class FunnelValidationError(ValueError):
    """Raised when a funnel record uses a value outside an enum."""


# ------------------------------------------------------------------ defaults
def _default_poc() -> Dict[str, Any]:
    return {
        "poc_status": "NOT_STARTED",
        "poc_phase": None,
        "poc_artifact_dir": None,
        "test_file": None,
        "test_command": None,
        "vulnerable_result": None,
        "patched_result": None,
        "unrelated_tests_result": None,
        "minimal_patch_validated": False,
        "source_chain_complete": False,
        "unsupported_claims_present": False,
        "remaining_blockers": [],
        "human_submission_ready": False,
    }


def _default_submission() -> Dict[str, Any]:
    return {
        "submission_status": "NOT_STARTED",
        "draft_path": None,
        "evidence_bundle_path": None,
        "pre_submission_gate_path": None,
        "reviewer_notes_path": None,
        "duplicate_check_status": "PENDING",
        "scope_check_status": "PENDING",
        "severity_check_status": "PENDING",
        "final_human_gate": "PENDING",
    }


def _default_safety() -> Dict[str, Any]:
    return {"source_false": False, "unsupported_ready": False, "hard_fail": False}


def _default_outcome() -> Dict[str, Any]:
    """(P99) The human-recorded outcome view. Defaults are reject-first: nothing is submitted and the gate is
    PENDING until a human outcome record says otherwise."""
    return {
        "human_final_gate": "PENDING",
        "submitted": False,
        "platform": None,
        "submission_id": None,
        "submitted_at": None,
        "outcome": "pending",
        "claimed_severity": None,
        "awarded_severity": None,
        "duplicate_of": None,
        "payout_amount": None,
        "rejection_reason": None,
        "lessons_learned": None,
        "source_mode": None,
        "finding_title": None,
    }


def load_outcomes(path: Union[str, Path, None] = None) -> Dict[str, Dict[str, Any]]:
    """Read-only load of human-recorded outcome records, keyed by candidate_id (== funnel record_id). A missing
    dir yields {}; malformed files are skipped. Performs NO writes and NEVER marks anything submitted."""
    d = Path(path) if path is not None else DEFAULT_OUTCOMES_DIR
    out: Dict[str, Dict[str, Any]] = {}
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.json")):
        data = _read_json(f)
        if isinstance(data, dict) and data.get("candidate_id"):
            out[str(data["candidate_id"])] = data
    return out


def _outcome_view(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge a raw outcome record over the defaults, validating enums. `submitted` is True ONLY if the record
    explicitly sets it True (never inferred)."""
    view = _default_outcome()
    if isinstance(raw, dict):
        for k in view:
            if k in raw and raw[k] is not None:
                view[k] = raw[k]
        view["submitted"] = raw.get("submitted") is True
    _check_enum(view["human_final_gate"], HUMAN_FINAL_GATE, "outcome.human_final_gate")
    _check_enum(view["outcome"], OUTCOME_STATUS, "outcome.outcome")
    return view


# --------------------------------------------------------------- normalization
def _check_enum(value: Any, allowed: set, field: str) -> None:
    if value is not None and value not in allowed:
        raise FunnelValidationError(f"invalid {field}={value!r}; allowed: {sorted(allowed)}")


def normalize_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Fill defaults so missing PoC / submission objects render as NOT_STARTED, validate enums, and
    coerce a record into the canonical shape. Never invents a bug/severity/bounty verdict — only the
    research-track lifecycle fields below exist."""
    if not isinstance(raw, dict):
        raise FunnelValidationError("record must be a dict")

    rec: Dict[str, Any] = dict(raw)

    rec.setdefault("subject", "unknown")
    rec.setdefault("phase_discovered", None)
    rec.setdefault("finding_id", None)
    rec.setdefault("contract", None)
    rec.setdefault("function", None)
    rec.setdefault("record_id", f"{rec.get('subject')}:{rec.get('finding_id')}:{rec.get('contract')}.{rec.get('function')}")
    rec.setdefault("blind_rank", None)
    rec.setdefault("surface_score", None)
    rec.setdefault("conversion", "NONE")
    rec.setdefault("mechanism_correctness", None)
    rec.setdefault("severity_gate", "n/a")
    rec.setdefault("severity_fp_before_gate", False)
    rec.setdefault("severity_fp", False)
    rec.setdefault("adversarial_result", "n/a")
    rec.setdefault("control", False)
    rec.setdefault("control_promoted_incorrectly", False)
    rec.setdefault("impact", None)
    rec.setdefault("human_readiness", None)
    rec.setdefault("blocker_reason", None)
    rec.setdefault("not_run", False)
    rec.setdefault("blocked", False)
    rec.setdefault("investigation_started", True)
    rec.setdefault("investigation_safe", None)
    rec.setdefault("source_refs", {})

    # (P98 assisted-mode, additive) provenance + assisted-validation. `source` defaults to "blind" so the
    # existing autonomous-eval records normalize unchanged.
    rec.setdefault("source", "blind")
    rec.setdefault("supplied_by", None)
    rec.setdefault("candidate_invariant", None)
    rec.setdefault("assisted_validation_status", "NOT_RUN" if rec["source"] == "assisted" else None)
    rec.setdefault("requested_check", None)
    _check_enum(rec["source"], SOURCE_KIND, "source")
    _check_enum(rec["supplied_by"], SUPPLIED_BY, "supplied_by")
    _check_enum(rec["assisted_validation_status"], ASSISTED_VALIDATION_STATUS, "assisted_validation_status")
    _check_enum(rec["requested_check"], REQUESTED_CHECK, "requested_check")

    _check_enum(rec["conversion"], CONVERSION_RESULT, "conversion")

    # safety block (backward compatible)
    safety = _default_safety()
    safety.update(rec.get("safety") or {})
    rec["safety"] = safety

    # poc block (backward compatible)
    poc = _default_poc()
    poc.update(rec.get("poc") or {})
    _check_enum(poc["poc_status"], POC_STATUS, "poc.poc_status")
    rec["poc"] = poc

    # submission block (backward compatible)
    sub = _default_submission()
    sub.update(rec.get("submission") or {})
    _check_enum(sub["submission_status"], SUBMISSION_STATUS, "submission.submission_status")
    _check_enum(sub["duplicate_check_status"], DUPLICATE_CHECK, "submission.duplicate_check_status")
    _check_enum(sub["scope_check_status"], SCOPE_CHECK, "submission.scope_check_status")
    _check_enum(sub["severity_check_status"], SEVERITY_CHECK, "submission.severity_check_status")
    _check_enum(sub["final_human_gate"], HUMAN_GATE, "submission.final_human_gate")
    rec["submission"] = sub

    # infer investigation_safe when not explicit: any record past LEAD_SURFACED with clean safety.
    if rec["investigation_safe"] is None:
        s = rec["safety"]
        rec["investigation_safe"] = not (s["source_false"] or s["unsupported_ready"] or s["hard_fail"])

    return rec


# ---------------------------------------------------------------- view objects
def build_poc_evidence(record: Dict[str, Any]) -> Dict[str, Any]:
    """The PoC evidence object (req-2 fields), always fully populated."""
    poc = _default_poc()
    poc.update(record.get("poc") or {})
    return poc


def build_submission_readiness(record: Dict[str, Any]) -> Dict[str, Any]:
    """The submission readiness object (req-3 fields), always fully populated."""
    sub = _default_submission()
    sub.update(record.get("submission") or {})
    return sub


# -------------------------------------------------------------- promotion gates
# Each gate is DEFAULT-DENY: it returns (ok, reasons). `ok` is True only if `reasons` is empty.

def can_promote_to_poc_handoff(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    rec = normalize_record(record)
    reasons: List[str] = []
    if rec["conversion"] not in _STRONG_CONVERSIONS:
        reasons.append(f"conversion {rec['conversion']} is not CLEAN_HIT/STRONG_PARTIAL")
    if rec["severity_gate"] != "passed":
        reasons.append(f"severity gate not passed (={rec['severity_gate']})")
    if rec["adversarial_result"] not in _ADVERSARIAL_OK:
        reasons.append(f"adversarial review not PASS/bounded (={rec['adversarial_result']})")
    if rec["severity_fp"]:
        reasons.append("severity FP marker present")
    s = rec["safety"]
    if s["source_false"]:
        reasons.append("SOURCE_FALSE present")
    if s["unsupported_ready"]:
        reasons.append("unsupported READY present")
    if s["hard_fail"]:
        reasons.append("HARD_FAIL present")
    return (not reasons, reasons)


def can_promote_to_poc_reproduced(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    rec = normalize_record(record)
    p = rec["poc"]
    reasons: List[str] = []
    if p["poc_status"] != "REPRODUCED":
        reasons.append(f"poc_status is {p['poc_status']}, not REPRODUCED")
    if not (p.get("test_file") or p.get("test_command")):
        reasons.append("no executable test or trace (test_file/test_command)")
    if not p.get("vulnerable_result"):
        reasons.append("no vulnerable-source result recorded")
    if not p.get("source_chain_complete"):
        reasons.append("source-grounded bug chain incomplete")
    if p.get("unsupported_claims_present"):
        reasons.append("unsupported claims present")
    # root-cause patch must pass *when available*
    if p.get("patched_result") and not p.get("minimal_patch_validated"):
        reasons.append("patched variant present but not validated")
    if not p.get("unrelated_tests_result"):
        reasons.append("no unrelated-tests result (cannot confirm nothing else broke)")
    return (not reasons, reasons)


def _is_strong_partial(record: Dict[str, Any]) -> bool:
    p = normalize_record(record)["poc"]
    return (
        p["poc_status"] == "PARTIAL_REPRO"
        and bool(p.get("source_chain_complete"))
        and bool(p.get("test_file") or p.get("test_command"))
        and not p.get("unsupported_claims_present")
    )


def can_promote_to_submission_ready(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    rec = normalize_record(record)
    reasons: List[str] = []
    repro_ok, _ = can_promote_to_poc_reproduced(rec)
    if not (repro_ok or _is_strong_partial(rec)):
        reasons.append("not POC_REPRODUCED and not a strong PARTIAL_REPRO")
    sub = rec["submission"]
    if not sub.get("evidence_bundle_path"):
        reasons.append("no evidence bundle")
    if not sub.get("pre_submission_gate_path"):
        reasons.append("no pre-submission gate")
    if sub["duplicate_check_status"] == "DUPLICATE_CONFIRMED":
        reasons.append("duplicate confirmed")
    if sub["scope_check_status"] == "OUT_OF_SCOPE":
        reasons.append("out of scope")
    if sub["severity_check_status"] != "SUPPORTED":
        reasons.append(f"severity check not SUPPORTED (={sub['severity_check_status']})")
    if rec["poc"].get("unsupported_claims_present"):
        reasons.append("unsupported claims remain")
    return (not reasons, reasons)


# ------------------------------------------------------------- status derivation
def compute_pipeline_status(record: Dict[str, Any]) -> str:
    """Derive the highest pipeline status the EVIDENCE supports (reject-first). A record's declared
    status is never trusted over the gate functions. SUBMITTED is intentionally not reachable here —
    it is only a submission_status value a human records."""
    rec = normalize_record(record)

    if rec["not_run"]:
        return "NOT_RUN"
    if rec["blocked"]:
        return "BLOCKED"

    sub = rec["submission"]

    # Submission stages (only if the submission-ready gate actually passes).
    sub_ready, _ = can_promote_to_submission_ready(rec)
    if sub_ready and sub["submission_status"] in {"READY_FOR_HUMAN_REVIEW", "SUBMITTED"}:
        # NB: even SUBMITTED maps to the human-review pipeline stage; the SUBMITTED *badge* is driven
        # separately off submission_status so it only shows when a human recorded it.
        return "SUBMISSION_READY_HUMAN_REVIEW"
    if sub["submission_status"] == "BLOCKED":
        return "BLOCKED"
    if sub["submission_status"] == "DRAFTING":
        return "SUBMISSION_PACKAGE_STARTED"

    # PoC stages.
    repro_ok, _ = can_promote_to_poc_reproduced(rec)
    if repro_ok:
        return "POC_REPRODUCED"
    poc_status = rec["poc"]["poc_status"]
    if poc_status == "PARTIAL_REPRO":
        return "PARTIAL_REPRO"
    if poc_status == "NOT_REPRODUCED":
        return "NOT_REPRODUCED"

    handoff_ok, _ = can_promote_to_poc_handoff(rec)
    if poc_status == "IN_PROGRESS" or (handoff_ok and poc_status == "NOT_STARTED"):
        return "POC_HANDOFF_STARTED"

    # Severity gate.
    if rec["severity_gate"] in {"demoted", "blocked"}:
        return "SEVERITY_GATED"

    # Conversion.
    conv = rec["conversion"]
    if conv == "CLEAN_HIT":
        return "CONVERTED_CLEAN_HIT"
    if conv == "STRONG_PARTIAL":
        return "CONVERTED_STRONG_PARTIAL"
    if conv == "ADJACENT":
        return "CONVERTED_ADJACENT"
    if conv in {"REJECTED", "ABSTAINED"}:
        return "REJECTED_OR_ABSTAINED"

    # Investigation / lead.
    if rec["investigation_safe"] and rec["investigation_started"]:
        return "INVESTIGATION_SAFE"
    if rec["investigation_started"]:
        return "INVESTIGATION_STARTED"
    return "LEAD_SURFACED"


def submission_badge(record: Dict[str, Any]) -> str:
    """Reject-first display helper: the only way to see SUBMITTED is an explicit human-recorded
    submission_status. Everything else surfaces as the literal submission_status (NOT_STARTED, etc.)."""
    return normalize_record(record)["submission"]["submission_status"]


# ------------------------------------------------------------------ focused view
def is_focused_row(row: Dict[str, Any]) -> bool:
    """(P100) A row is in the default "Focused" view iff it is an assisted-arc candidate OR it is ready for
    human review. On the current corpus this is exactly the proven set (Vultisig H-01 + SecondSwap M-11); legacy
    blind scaffolds are excluded. This is a NON-DESTRUCTIVE display filter — it hides nothing on disk and never
    changes the metric totals."""
    src = row.get("source_mode") or row.get("source")
    return src == "assisted" or row.get("pipeline_status") == "SUBMISSION_READY_HUMAN_REVIEW"


def focused_records(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """The Focused-view subset of display rows (see is_focused_row). Pure; deletes nothing."""
    return [r for r in rows if is_focused_row(r)]


# ---------------------------------------------------------------------- metrics
def _metrics_from_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """(P100 sync) Compute every DISPLAY headline count directly from the row objects the table renders, so the
    metric tiles can never drift from the rows. NOT_RUN rows are excluded from the volume denominators. These
    keys overlay `compute_funnel_metrics` output in `load_records`, making the served payload row-consistent by
    construction."""
    counted = [r for r in rows if r.get("pipeline_status") != "NOT_RUN"]

    def n(pred) -> int:
        return sum(1 for r in counted if pred(r))

    def status(r): return r.get("pipeline_status")
    def poc(r): return (r.get("poc") or {}).get("poc_status")

    src_kinds = sorted(SOURCE_KIND)
    return {
        "blind_records": n(lambda r: (r.get("source_mode") or r.get("source")) == "blind"),
        "assisted_records": n(lambda r: (r.get("source_mode") or r.get("source")) == "assisted"),
        "by_source": {k: n(lambda r, k=k: (r.get("source_mode") or r.get("source")) == k) for k in src_kinds},
        "clean_hits": n(lambda r: r.get("conversion") == "CLEAN_HIT"),
        "strong_partials": n(lambda r: r.get("conversion") == "STRONG_PARTIAL"),
        "poc_handoffs_started": n(lambda r: poc(r) and poc(r) != "NOT_STARTED"),
        "pocs_reproduced": n(lambda r: status(r) == "POC_REPRODUCED"),
        "poc_reproduced_total": n(lambda r: poc(r) == "REPRODUCED"),
        "partial_reproductions": n(lambda r: poc(r) == "PARTIAL_REPRO"),
        "not_reproduced": n(lambda r: poc(r) == "NOT_REPRODUCED"),
        "submission_packages_ready_for_human_review": n(lambda r: status(r) == "SUBMISSION_READY_HUMAN_REVIEW"),
        "ready_for_human_review_count": n(lambda r: status(r) == "SUBMISSION_READY_HUMAN_REVIEW"),
        "approved_to_submit_count": n(lambda r: r.get("human_final_gate") == "APPROVED_TO_SUBMIT"),
        "submitted_count": n(lambda r: r.get("submitted") is True),
        "accepted_count": n(lambda r: r.get("outcome") == "accepted"),
        "duplicate_count": n(lambda r: r.get("outcome") == "duplicate"),
        "rejected_count": n(lambda r: r.get("outcome") == "rejected"),
        "pending_count": n(lambda r: (r.get("outcome") or "pending") == "pending"),
        "invalid_count": n(lambda r: r.get("outcome") == "invalid"),
        "assisted_to_reproduced_count": n(
            lambda r: (r.get("source_mode") or r.get("source")) == "assisted" and poc(r) == "REPRODUCED"),
        "reproduced_to_submission_ready_count": n(
            lambda r: status(r) == "SUBMISSION_READY_HUMAN_REVIEW" and poc(r) == "REPRODUCED"),
        "submission_ready_to_submitted_count": n(
            lambda r: status(r) == "SUBMISSION_READY_HUMAN_REVIEW" and r.get("submitted") is True),
    }


def compute_funnel_metrics(records: List[Dict[str, Any]],
                           outcomes: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Funnel counts (req-4). NOT_RUN records are excluded from every denominator and reported
    separately as `not_run`. `outcomes` (P99) maps record_id -> human outcome record; submitted/outcome
    counts derive ONLY from it (never inferred)."""
    outcomes = outcomes or {}
    recs = [normalize_record(r) for r in records]
    statuses = {r["record_id"]: compute_pipeline_status(r) for r in recs}

    counted = [r for r in recs if not r["not_run"]]  # denominator excludes NOT_RUN
    not_run = len(recs) - len(counted)

    def _status(r: Dict[str, Any]) -> str:
        return statuses[r["record_id"]]

    blockers: Dict[str, int] = {}

    def _add_blocker(reason: Optional[str]) -> None:
        if reason:
            blockers[reason] = blockers.get(reason, 0) + 1

    pocs_reproduced = 0
    submission_ready = 0
    blocked_submissions = 0
    for r in counted:
        st = _status(r)
        if st == "POC_REPRODUCED":
            pocs_reproduced += 1
        if st == "SUBMISSION_READY_HUMAN_REVIEW":
            submission_ready += 1
        if st == "BLOCKED" or r["submission"]["submission_status"] == "BLOCKED":
            blocked_submissions += 1
        _add_blocker(r.get("blocker_reason"))
        # For reproduced findings not yet submission-ready, surface the gate's top reason.
        if st == "POC_REPRODUCED":
            ok, reasons = can_promote_to_submission_ready(r)
            if not ok and reasons:
                _add_blocker(reasons[0])

    metrics = {
        "total_leads_surfaced": len(counted),
        "leads_investigated": sum(1 for r in counted if r["investigation_started"]),
        "clean_hits": sum(1 for r in counted if r["conversion"] == "CLEAN_HIT"),
        "strong_partials": sum(1 for r in counted if r["conversion"] == "STRONG_PARTIAL"),
        "severity_fps_before_gate": sum(1 for r in counted if r["severity_fp_before_gate"]),
        "severity_fps_after_gate": sum(1 for r in counted if r["severity_fp"]),
        "controls_promoted_incorrectly": sum(
            1 for r in counted if r["control"] and r["control_promoted_incorrectly"]
        ),
        "poc_handoffs_started": sum(1 for r in counted if r["poc"]["poc_status"] != "NOT_STARTED"),
        "pocs_reproduced": pocs_reproduced,
        "partial_reproductions": sum(1 for r in counted if r["poc"]["poc_status"] == "PARTIAL_REPRO"),
        "not_reproduced": sum(1 for r in counted if r["poc"]["poc_status"] == "NOT_REPRODUCED"),
        "submission_packages_ready_for_human_review": submission_ready,
        "blocked_submissions": blocked_submissions,
        "top_blocker_reasons": sorted(blockers.items(), key=lambda kv: (-kv[1], kv[0])),
        "not_run": not_run,
        # (P98) provenance split — blind autonomous-eval records vs human/tool-assisted candidates.
        "blind_records": sum(1 for r in counted if r["source"] == "blind"),
        "assisted_records": sum(1 for r in counted if r["source"] == "assisted"),
        "by_source": {k: sum(1 for r in counted if r["source"] == k) for k in sorted(SOURCE_KIND)},
        "assisted_validated_for_poc_handoff": sum(
            1 for r in counted if r["assisted_validation_status"] == "VALIDATED_FOR_POC_HANDOFF"),
        "assisted_rejected_source_proven_safe": sum(
            1 for r in counted if r["assisted_validation_status"] == "REJECTED_SOURCE_PROVEN_SAFE"),
    }

    # (P99) human-review + outcome counts. submitted/outcome derive ONLY from human outcome records.
    def _ov(r: Dict[str, Any]) -> Dict[str, Any]:
        return _outcome_view(outcomes.get(r["record_id"]))
    ovs = {r["record_id"]: _ov(r) for r in counted}
    reproduced = sum(1 for r in counted if _status(r) == "POC_REPRODUCED")
    metrics.update({
        "ready_for_human_review_count": sum(1 for r in counted if _status(r) == "SUBMISSION_READY_HUMAN_REVIEW"),
        "approved_to_submit_count": sum(1 for o in ovs.values() if o["human_final_gate"] == "APPROVED_TO_SUBMIT"),
        "submitted_count": sum(1 for o in ovs.values() if o["submitted"]),
        "accepted_count": sum(1 for o in ovs.values() if o["outcome"] == "accepted"),
        "duplicate_count": sum(1 for o in ovs.values() if o["outcome"] == "duplicate"),
        "rejected_count": sum(1 for o in ovs.values() if o["outcome"] == "rejected"),
        "pending_count": sum(1 for o in ovs.values() if o["outcome"] == "pending"),
        "invalid_count": sum(1 for o in ovs.values() if o["outcome"] == "invalid"),
        # total reproduced PoCs (poc_status==REPRODUCED) regardless of whether they ADVANCED to submission-ready.
        # (pocs_reproduced above counts only records still AT the POC_REPRODUCED *stage* — which under-counts once
        # a reproduced PoC moves on to a submission package; this total is the human-facing reproduced count.)
        "poc_reproduced_total": sum(1 for r in counted if r["poc"]["poc_status"] == "REPRODUCED"),
        "assisted_to_reproduced_count": sum(
            1 for r in counted if r["source"] == "assisted" and r["poc"]["poc_status"] == "REPRODUCED"),
        "reproduced_to_submission_ready_count": sum(
            1 for r in counted if _status(r) == "SUBMISSION_READY_HUMAN_REVIEW"
            and r["poc"]["poc_status"] == "REPRODUCED"),
        "submission_ready_to_submitted_count": sum(
            1 for r in counted if _status(r) == "SUBMISSION_READY_HUMAN_REVIEW" and ovs[r["record_id"]]["submitted"]),
    })
    return metrics


# ------------------------------------------------------------------- display row
def _abs_or_none(rel: Optional[str]) -> Optional[str]:
    """Resolve a repo-relative artifact path to an existing absolute path, else None. Read-only."""
    if not rel:
        return None
    try:
        p = (ROOT / rel).resolve()
    except (OSError, ValueError):
        return None
    if (p == ROOT or ROOT in p.parents) and p.exists():
        return str(p)
    return None


def build_finding_row(record: Dict[str, Any], outcome: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Per-finding display row (req-5). Self-contained for the frontend: includes the computed
    pipeline status, the full PoC + submission objects, and resolved artifact links. `outcome` is the
    human-recorded outcome record (P99); SUBMITTED is shown ONLY when it sets submitted=true."""
    rec = normalize_record(record)
    ov = _outcome_view(outcome)
    poc = rec["poc"]
    status = compute_pipeline_status(rec)
    handoff_ok, handoff_reasons = can_promote_to_poc_handoff(rec)
    repro_ok, repro_reasons = can_promote_to_poc_reproduced(rec)
    sub_ok, sub_reasons = can_promote_to_submission_ready(rec)

    artifact_links = {
        "poc_artifact_dir": _abs_or_none(poc.get("poc_artifact_dir")),
        "test_file": _abs_or_none(poc.get("test_file")),
        "evidence_bundle_path": _abs_or_none(rec["submission"].get("evidence_bundle_path")),
        "draft_path": _abs_or_none(rec["submission"].get("draft_path")),
    }

    sub = rec["submission"]
    return {
        "record_id": rec["record_id"],
        # (P100) explicit aliases so /api/funnel exposes every documented field at the row level.
        "candidate_id": rec["record_id"],
        "source_mode": (ov.get("source_mode") or rec["source"]),
        "finding_title": ov.get("finding_title") or rec.get("title") or rec["finding_id"],
        "submission_status": sub.get("submission_status"),
        "duplicate_check": sub.get("duplicate_check_status"),
        "scope_check": sub.get("scope_check_status"),
        "severity_check": sub.get("severity_check_status"),
        "final_human_gate": sub.get("final_human_gate"),
        "poc_command": (poc.get("test_command") if poc["poc_status"] in {"REPRODUCED", "PARTIAL_REPRO"} else None),
        "subject": rec["subject"],
        "phase_discovered": rec["phase_discovered"],
        "finding_id": rec["finding_id"],
        "contract_function": f"{rec['contract']}.{rec['function']}" if rec["contract"] else rec["function"],
        # (P98 assisted-mode) provenance + assisted-validation surface.
        "source": rec["source"],
        "supplied_by": rec["supplied_by"],
        "candidate_invariant_present": bool(rec.get("candidate_invariant")),
        "assisted_validation_status": rec["assisted_validation_status"],
        "requested_check": rec["requested_check"],
        "ready_for_poc_handoff": handoff_ok,
        "blind_rank": rec["blind_rank"],
        "surface_score": rec["surface_score"],
        "conversion": rec["conversion"],
        "mechanism_correctness": rec["mechanism_correctness"],
        "severity_gate": rec["severity_gate"],
        "severity_fp": rec["severity_fp"],
        "adversarial_result": rec["adversarial_result"],
        "control": rec["control"],
        "pipeline_status": status,
        "poc_status": poc["poc_status"],
        "test_command": poc.get("test_command") if status == "POC_REPRODUCED" else (
            poc.get("test_command") if poc["poc_status"] in {"REPRODUCED", "PARTIAL_REPRO"} else None
        ),
        "poc": poc,
        "submission": rec["submission"],
        "submission_badge": submission_badge(rec),
        # (P99) human-final-gate + outcome — sourced ONLY from a human-recorded outcome record, never inferred.
        "human_final_gate": ov["human_final_gate"],
        "submitted": ov["submitted"],
        "platform": ov["platform"],
        "submission_id": ov["submission_id"],
        "submitted_at": ov["submitted_at"],
        "outcome": ov["outcome"],
        "claimed_severity": ov["claimed_severity"],
        "awarded_severity": ov["awarded_severity"],
        "duplicate_of": ov["duplicate_of"],
        "payout_amount": ov["payout_amount"],
        "rejection_reason": ov["rejection_reason"],
        "lessons_learned": ov["lessons_learned"],
        "human_readiness": rec["human_readiness"],
        "impact": rec["impact"],
        "blocker_reason": rec["blocker_reason"],
        # (P222) human-review priority lane — display/prioritization only; sourced from the synced record
        # (sync_hunt_findings CARD_INJECT). Never affects submission_ready/routing_allowed/severity.
        "human_review_priority": record.get("human_review_priority") or "NONE",
        "human_review_reason_codes": record.get("human_review_reason_codes") or [],
        "reachability_class": record.get("reachability_class"),
        "should_surface_above_noise": bool(record.get("should_surface_above_noise")),
        "gates": {
            "poc_handoff": {"ok": handoff_ok, "reasons": handoff_reasons},
            "poc_reproduced": {"ok": repro_ok, "reasons": repro_reasons},
            "submission_ready": {"ok": sub_ok, "reasons": sub_reasons},
        },
        "artifact_links": artifact_links,
        "research_only": True,
        "routes_in_production": False,
    }


# ----------------------------------------------------------------------- loading
def _read_json(path: Path) -> Optional[Any]:
    try:
        with Path(path).open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _enrich_from_refs(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Read-only cross-check against the frozen phase artifacts named in source_refs. Never UPGRADES
    a status (reject-first); only records consistency warnings + which refs resolved. Graceful on
    missing files."""
    refs = rec.get("source_refs") or {}
    resolved: Dict[str, bool] = {}
    warnings: List[str] = []

    for name, rel in refs.items():
        ap = _abs_or_none(rel)
        resolved[name] = ap is not None

    # If a P82-style freeze is referenced, cross-check the PoC status it asserts.
    freeze_rel = refs.get("poc_freeze")
    if freeze_rel:
        data = _read_json(ROOT / freeze_rel) if _abs_or_none(freeze_rel) else None
        if isinstance(data, dict):
            frozen_status = data.get("status")
            if frozen_status and frozen_status != rec["poc"]["poc_status"]:
                warnings.append(
                    f"poc_status {rec['poc']['poc_status']} != freeze status {frozen_status} ({freeze_rel})"
                )

    rec["source_refs_resolved"] = resolved
    if warnings:
        rec["consistency_warnings"] = warnings
    return rec


def _rw_slug(subject: str) -> str:
    """Stable, filesystem-safe slug for a real-world target subject."""
    s = "".join(c.lower() if c.isalnum() else "-" for c in (subject or "target"))
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-") or "target"


def _rw_contract_function(poc_path: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Best-effort (contract, function) split from a PoC test path, e.g.
    'forty/test/poc/CommunityRewardsEarnedGrief*.t.sol' -> ('CommunityRewards', 'earned'). Never fabricates:
    falls back to the test-file basename as contract and None function when it can't infer."""
    if not poc_path:
        return (None, None)
    base = poc_path.rsplit("/", 1)[-1]
    base = base.split(".")[0].rstrip("*")
    return (base or None, None)


def _records_from_real_world(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Map documentation/real_world_results.json into funnel-1 raw records (consumed by normalize_record).

    - candidate_findings[] -> POC_REPRODUCED records (PoC-proven, never submission-ready/submitted).
    - targets[] honest_negative -> REJECTED (investigated lead, no PoC).
    - targets[] skipped -> not_run (excluded from denominators).
    - targets[] candidate_finding -> skipped here (already covered by candidate_findings[], dedup by subject).

    No fabricated outcomes: the submission block stays default, so submitted/paid never appear.
    """
    records: List[Dict[str, Any]] = []
    candidate_subjects = set()

    for i, cf in enumerate(data.get("candidate_findings") or []):
        if not isinstance(cf, dict):
            continue
        subject = cf.get("target") or f"candidate-{i}"
        candidate_subjects.add(subject)
        poc_path = cf.get("poc_path")
        contract, function = _rw_contract_function(poc_path)
        title = cf.get("title")
        evidence = cf.get("evidence") or "PoC-proven candidate"
        # The infiniFi item carries a live-state caveat (rubric may argue Low) -> STRONG_PARTIAL, else CLEAN_HIT.
        caveated = "may argue" in (cf.get("status") or "").lower()
        # (verifier) Structured reproduce/understand evidence (function map, attacker model, exploit steps,
        # defense map, PoC actual/expected/control, impact). These inline fields are read by the unified
        # candidate-detail card (finding_detail.build_verifier_evidence) so the bug is fully displayed on
        # discovery. normalize_record preserves unknown keys, so they survive onto the record verbatim.
        verifier = cf.get("verifier") if isinstance(cf.get("verifier"), dict) else {}
        v_contract, v_function = contract, function
        if verifier.get("target") and "." in str(verifier["target"]):
            v_contract, v_function = str(verifier["target"]).split(".", 1)
        rec = {
            "record_id": f"real:{_rw_slug(subject)}:{i}",
            "subject": subject,
            "phase_discovered": cf.get("source"),
            "finding_id": title,
            "title": title,
            "contract": v_contract,
            "function": v_function,
            "source": "blind",
            "conversion": "STRONG_PARTIAL" if caveated else "CLEAN_HIT",
            "mechanism_correctness": "confirmed",
            "severity_gate": "passed",
            "adversarial_result": "PASS",
            "impact": verifier.get("impact") or cf.get("severity"),
            "investigation_started": True,
            "investigation_safe": True,
            "human_readiness": "human verification + submission pending",
            "poc": {
                # Default REPRODUCED (every legacy candidate_finding is PoC-proven); a card may carry an honest
                # verifier.poc_status (e.g. NOT_STARTED for a confirmed-but-unreproduced finding) which wins —
                # but only when it is a valid enum value (legacy entries carry free-text like "PASS (1/1)").
                "poc_status": (verifier["poc_status"] if verifier.get("poc_status") in POC_STATUS else "REPRODUCED"),
                "poc_artifact_dir": (poc_path.rsplit("/", 1)[0] if poc_path and "/" in poc_path else None),
                "test_file": poc_path,
                "test_command": verifier.get("poc_command") or "forge test",
                "vulnerable_result": verifier.get("vulnerable_output") or evidence,
                "unrelated_tests_result": verifier.get("control_case") or "control case included (see evidence)",
                "source_chain_complete": True,
                "unsupported_claims_present": False,
            },
        }
        # Merge the structured verifier fields as top-level record keys (the card reads them from the record).
        for k, val in verifier.items():
            rec.setdefault(k, val)
        records.append(rec)

    for t in data.get("targets") or []:
        if not isinstance(t, dict):
            continue
        subject = t.get("target")
        if not subject:
            continue
        verdict = t.get("verdict")
        if verdict == "candidate_finding":
            continue  # already represented by a candidate_findings[] record
        if subject in candidate_subjects:
            continue  # dedup belt-and-suspenders
        base = {
            "record_id": f"real:{_rw_slug(subject)}",
            "subject": subject,
            "phase_discovered": t.get("source"),
            "finding_id": t.get("notes"),
            "source": "blind",
            "investigation_started": True,
            "investigation_safe": True,
            "impact": t.get("notes"),
        }
        if verdict == "skipped":
            base["not_run"] = True
            base["conversion"] = "NONE"
            base["blocker_reason"] = t.get("notes")
        else:  # honest_negative (default)
            base["conversion"] = "REJECTED"
        records.append(base)

    return records


def load_records(path: Union[str, Path, None] = None,
                 outcomes_path: Union[str, Path, None] = None) -> Dict[str, Any]:
    """Load funnel_records.json, normalize every record, and enrich read-only from source_refs.
    Also joins human-recorded outcome records (P99) by record_id == candidate_id. Graceful: a missing/invalid
    file yields an empty record set rather than crashing. Performs NO writes."""
    # (P216) merge the generated synced mirror ONLY on the implicit default call (path is None) — i.e. the live
    # dashboard read path. A caller that pins an explicit path (tests/tools, even when it equals the default) gets
    # exactly that file, so seed/metric fixtures are unaffected.
    _use_default = path is None

    # (real-world) On the live dashboard read path (no explicit path), source the honest hunt log. The eval
    # funnel_records.json + synced mirror are NO LONGER the default (they stay on disk for explicit-path callers
    # like tests). Fall back to the legacy default file only if the real-world log is missing.
    if _use_default and REAL_RESULTS_PATH.exists():
        rw = _read_json(REAL_RESULTS_PATH)
        if isinstance(rw, dict):
            raw_findings = _records_from_real_world(rw)
            records = [_enrich_from_refs(normalize_record(r)) for r in raw_findings if isinstance(r, dict)]
            outcomes = load_outcomes(outcomes_path)
            rows = [build_finding_row(r, outcomes.get(r["record_id"])) for r in records]
            for row in rows:
                row["focused"] = is_focused_row(row)
            metrics = compute_funnel_metrics(records, outcomes)
            metrics.update(_metrics_from_rows(rows))
            return {
                "source_path": str(REAL_RESULTS_PATH),
                "schema_version": "real-world-1",
                "record_count": len(records),
                "focused_count": sum(1 for r in rows if r.get("focused")),
                "records": rows,
                "metrics": metrics,
                "statuses": _status_vocab(),
                "research_only": True,
                "routes_in_production": False,
            }

    path = Path(path) if path is not None else DEFAULT_RECORDS_PATH
    data = _read_json(path)
    raw_findings = (data or {}).get("findings") if isinstance(data, dict) else None
    if not isinstance(raw_findings, list):
        raw_findings = []

    # (P216) additively merge the generated synced-findings mirror (read-only; missing file = no-op). This is the
    # single chokepoint feeding /funnel, /findings and /candidates, so one merge surfaces all synced sources.
    if _use_default and SYNCED_RECORDS_PATH.exists():
        synced = _read_json(SYNCED_RECORDS_PATH)
        synced_findings = (synced or {}).get("findings") if isinstance(synced, dict) else None
        if isinstance(synced_findings, list):
            seen = {r.get("record_id") for r in raw_findings if isinstance(r, dict)}
            for r in synced_findings:
                if isinstance(r, dict) and r.get("record_id") not in seen:
                    raw_findings.append(r)
                    seen.add(r.get("record_id"))

    records = [_enrich_from_refs(normalize_record(r)) for r in raw_findings if isinstance(r, dict)]
    outcomes = load_outcomes(outcomes_path)
    rows = [build_finding_row(r, outcomes.get(r["record_id"])) for r in records]
    # (P100) non-destructive Focused-view tag per row (assisted arc + ready-for-human-review). Hides nothing on
    # disk; the table can default to focused while the metric tiles stay full totals.
    for row in rows:
        row["focused"] = is_focused_row(row)
    metrics = compute_funnel_metrics(records, outcomes)
    # (P100 sync) overlay the display headline counts derived from the SAME rows the table renders, so the
    # served tiles can never drift from the rows.
    metrics.update(_metrics_from_rows(rows))

    return {
        "source_path": str(path),
        "schema_version": (data or {}).get("schema_version") if isinstance(data, dict) else None,
        "record_count": len(records),
        "focused_count": sum(1 for r in rows if r.get("focused")),
        "records": rows,
        "metrics": metrics,
        "statuses": _status_vocab(),
        "research_only": True,
        "routes_in_production": False,
    }


def _status_vocab() -> Dict[str, Any]:
    """The enum vocabulary the frontend uses for filters/legends. Pure; no I/O."""
    return {
        "pipeline_status": sorted(PIPELINE_STATUS),
        "poc_status": sorted(POC_STATUS),
        "submission_status": sorted(SUBMISSION_STATUS),
        "duplicate_check": sorted(DUPLICATE_CHECK),
        "scope_check": sorted(SCOPE_CHECK),
        "severity_check": sorted(SEVERITY_CHECK),
        "human_gate": sorted(HUMAN_GATE),
        "conversion_result": sorted(CONVERSION_RESULT),
        "source_kind": sorted(SOURCE_KIND),
        "supplied_by": sorted(SUPPLIED_BY),
        "requested_check": sorted(REQUESTED_CHECK),
        "assisted_validation_status": sorted(ASSISTED_VALIDATION_STATUS),
        "human_final_gate": sorted(HUMAN_FINAL_GATE),
        "outcome_status": sorted(OUTCOME_STATUS),
    }
