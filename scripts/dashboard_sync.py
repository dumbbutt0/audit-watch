#!/usr/bin/env python3
"""dashboard_sync.py — P216 unified dashboard routing contract (research-only, read-only).

Converts a candidate bundle from ANY source (audit workspace / funnel / runtime / detector / campaign / L3 /
dry-run queue / future live hunt) into ONE canonical synced-finding record (schema "synced-1") that is also a
valid funnel-1 record, so the existing readers (funnel.load_records → /funnel, findings_overview.load_overview →
/findings + /candidates) and the detail card (finding_detail.build_verifier_evidence) render it with the full
H5-style verifier checklist.

HARD INVARIANTS (mirror the finished Abracadabra H5 semantics):
  * research_only:true, review_only:true, routes_in_production:false, routing_allowed:false.
  * submission_ready ALWAYS false here — canonical submission_ready is machine-owned by the real submission gate.
  * NEVER infers severity. severity_recommendation echoes a RECORDED value or stays None (the card's _sev_or_status
    then shows HUMAN_PENDING). The browser computes no severity.
  * Missing inputs become "unknown" / MISSING_EVIDENCE explicitly — never fabricated.
  * Pure: no file writes, no routing, no network. (The generator build_synced_findings.py does I/O.)
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = "synced-1"
UNKNOWN = "unknown"
MISSING = "MISSING_EVIDENCE"

# funnel-1 validated enums (must match scripts/funnel.py)
CONVERSION_RESULT = {"CLEAN_HIT", "STRONG_PARTIAL", "ADJACENT", "REJECTED", "ABSTAINED", "NONE"}
POC_STATUS = {"NOT_STARTED", "IN_PROGRESS", "REPRODUCED", "PARTIAL_REPRO", "NOT_REPRODUCED"}
SUBMISSION_STATUS = {"NOT_STARTED", "DRAFTING", "READY_FOR_HUMAN_REVIEW", "BLOCKED", "SUBMITTED"}
SOURCE_TRACKS = {"audit_workspace", "funnel", "runtime", "detector", "campaign", "l3", "dry_run_queue"}

# severities the card may echo (recorded only). Conversion/decision tokens are NOT severities and are never placed here.
_SEVERITIES = {"critical", "high", "medium", "low", "informational", "info", "qa", "no_security_impact", "none", "design"}


def _present(v: Any) -> bool:
    return v is not None and str(v).strip().lower() not in ("", "none", "n/a", "na", "unknown", "unspecified")


def _clamp(v: Optional[str], allowed: set, default: str) -> str:
    return v if (isinstance(v, str) and v in allowed) else default


def _recorded_severity(*vals: Any) -> Optional[str]:
    """Return the first value that is a RECORDED severity label; else None. Never infers, never accepts a
    conversion/decision token (CLEAN_HIT, REPRODUCED, ...)."""
    for v in vals:
        if v is None:
            continue
        s = str(v).strip().lower()
        if s in _SEVERITIES:
            return str(v)
    return None


def _or_unknown(v: Any) -> Any:
    return v if _present(v) else UNKNOWN


def _list_or_missing(v: Any) -> List[Any]:
    if isinstance(v, list) and v:
        return v
    return [MISSING]


def to_synced_finding(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Map a candidate bundle to one canonical synced-finding record. See module docstring for invariants."""
    b = bundle or {}
    cid = str(b.get("candidate_id") or b.get("finding_id") or "UNKNOWN")
    track = _clamp(b.get("source_track"), SOURCE_TRACKS, "funnel")
    contract = b.get("contract")
    function = b.get("function")
    cf = b.get("contract_function") or (f"{contract}.{function}" if contract and function else (contract or None))
    subject = b.get("subject") or b.get("workspace_or_audit")

    l3 = b.get("l3") or {}
    triage = b.get("triage") or {}
    poc = b.get("poc") or {}
    drq = b.get("dry_run_queue") or {}

    # severity: recorded only (triage recommended / L3 calibrated / claimed ceiling) — never inferred.
    severity_rec = _recorded_severity(triage.get("recommended_severity"),
                                      l3.get("calibrated_severity_after_l3"),
                                      b.get("severity_recommendation"))
    claimed = b.get("claimed_severity") or b.get("threat_ceiling")

    conversion = _clamp(b.get("conversion"), CONVERSION_RESULT, "NONE")
    poc_status = _clamp(b.get("poc_status") or poc.get("poc_status"), POC_STATUS, "NOT_STARTED")

    main_blocker = b.get("blocker_reason") or l3.get("high_promotion_blocker") or b.get("main_blocker")
    summary = b.get("summary") or b.get("impact") or b.get("title")

    rec: Dict[str, Any] = {
        # ---- identity / provenance
        "schema": SCHEMA_VERSION,
        "record_id": b.get("record_id") or f"{subject or 'unknown'}:{cid}:{cf or ''}",
        "candidate_id": cid,
        "finding_id": cid,
        "source_track": track,
        "workspace_or_audit": subject,
        "subject": subject,
        "phase_discovered": b.get("phase_discovered"),

        # ---- SAFETY (constant; mirror H5) ----
        "research_only": True,
        "review_only": True,
        "routes_in_production": False,
        "routing_allowed": False,
        "submission_ready": False,
        "canonical_submission_ready_source": "scripts/submission/gates/submission_gate.py (machine-owned; human_approval_required=true)",
        "human_review_required": True,
        "no_submit_controls": True,
        "browser_computes_severity": False,

        # ---- L3 ----
        "l3_status": l3.get("l3_status") or b.get("l3_status"),
        "high_promotion_allowed": l3.get("high_promotion_allowed"),
        "high_promotion_blocker": l3.get("high_promotion_blocker"),

        # ---- conversion / readiness ----
        "conversion": conversion,
        "conversion_outcome": b.get("conversion_outcome") or conversion,
        "conversion_classification": b.get("conversion_classification") or conversion,
        "severity_recommendation": severity_rec,          # None => card shows HUMAN_PENDING
        "novelty_status": b.get("novelty_status") or UNKNOWN,
        "novelty_duplicate": b.get("novelty_duplicate") or b.get("novelty_status") or UNKNOWN,
        "readiness_state": drq.get("readiness_state") or b.get("readiness_state") or "not_reviewed",
        "submission_package_status_derived": b.get("submission_package_status_derived") or "NOT_READY",
        "last_reviewer_note": b.get("last_reviewer_note") or (b.get("scoring_note") or None),

        # ---- checklist sections (inline; renderer prefers these) ----
        "title": b.get("title") or _or_unknown(cf),
        "summary": _or_unknown(summary),
        "affected_contracts": [contract] if contract else [],
        "affected_functions": [function] if function else [],
        "mechanism": _or_unknown(b.get("mechanism") or b.get("suspected_mechanism") or b.get("impact")),
        "root_cause": _or_unknown(b.get("root_cause")),
        "attacker_model": _or_unknown(b.get("attacker_model")),
        "exploit_steps": _list_or_missing(b.get("exploit_steps")),
        "function_map": b.get("function_map") if isinstance(b.get("function_map"), list) else [],
        "defense_map": b.get("defense_map") if isinstance(b.get("defense_map"), list) else [],
        "poc_verification": {
            "poc_status": poc_status,
            "test_file": poc.get("test_file"),
            "test_command": poc.get("test_command"),
            "result": poc.get("vulnerable_result") or poc.get("result") or MISSING,
        },
        "impact_and_severity": {
            "impact": _or_unknown(summary),
            "claimed_ceiling": claimed or UNKNOWN,
            "severity_recommendation": severity_rec or "HUMAN_PENDING",
        },
        "intent_scope_operator_assumptions": _or_unknown(b.get("intent_scope_operator_assumptions")),
        "main_blocker": _or_unknown(main_blocker),
        "final_triager_decision": _or_unknown(triage.get("triage_status") or b.get("final_triager_decision")),
        "red_flags": b.get("red_flags") if isinstance(b.get("red_flags"), list) else [],
        "evidence_backup": b.get("evidence_backup") if isinstance(b.get("evidence_backup"), list) else [],
        "source_refs": b.get("source_refs") or {},
        "raw_fields": b.get("raw_fields") or {k: v for k, v in b.items() if k not in ("raw_fields",)},

        # ---- funnel-1 fields the existing readers + build_verifier_evidence consume ----
        "contract": contract,
        "function": function,
        "contract_function": cf,
        "surface_function": b.get("surface_function") or cf,
        "target": cf,
        "suspected_mechanism": b.get("suspected_mechanism") or b.get("mechanism") or b.get("impact"),
        "mechanism_correctness": b.get("mechanism_correctness"),
        "severity_gate": b.get("severity_gate") or "n/a",
        "claimed_severity": claimed,
        "impact": summary,
        "vulnerable_output": b.get("vulnerable_output"),
        "reachability_verdict": b.get("reachability_verdict"),
        "limitations": b.get("limitations"),
        "blocker_reason": main_blocker,
        "novelty_clear": b.get("novelty_clear") or UNKNOWN,
        "artifact_links": b.get("artifact_links") or b.get("source_refs") or {},
        "p155_gate1_source_intent": b.get("p155_gate1_source_intent") or b.get("intent_scope_operator_assumptions"),
        "p155_gate2_attacker_model": b.get("p155_gate2_attacker_model") or b.get("attacker_model"),
        "poc": {
            "poc_status": poc_status,
            "test_file": poc.get("test_file"),
            "test_command": poc.get("test_command"),
            "vulnerable_result": poc.get("vulnerable_result"),
            "human_submission_ready": False,
        },
        "submission": {
            "submission_status": _clamp(b.get("submission_status"), SUBMISSION_STATUS, "NOT_STARTED"),
            "duplicate_check_status": "PENDING",
            "scope_check_status": "PENDING",
            "severity_check_status": "PENDING",
            "final_human_gate": "PENDING",
        },
        "safety": {"source_false": bool(b.get("source_false", False)), "unsupported_ready": False, "hard_fail": False},
        "blind_rank": b.get("blind_rank"),
        "surface_score": b.get("surface_score"),
    }
    return rec


# downshape helper: a synced record IS already funnel-1-valid, so this is identity (kept for the contract API).
def to_funnel_record(synced: Dict[str, Any]) -> Dict[str, Any]:
    return synced


def validate_synced(rec: Dict[str, Any]) -> List[str]:
    """Lightweight structural + safety validation. Returns list of problems ([] == OK)."""
    p: List[str] = []
    if not isinstance(rec, dict):
        return ["not a dict"]
    if rec.get("schema") != SCHEMA_VERSION:
        p.append(f"schema != {SCHEMA_VERSION}")
    for k in ("record_id", "candidate_id", "source_track"):
        if not _present(rec.get(k)):
            p.append(f"missing {k}")
    if rec.get("source_track") not in SOURCE_TRACKS:
        p.append(f"bad source_track={rec.get('source_track')}")
    if rec.get("conversion") not in CONVERSION_RESULT:
        p.append(f"bad conversion={rec.get('conversion')}")
    if (rec.get("poc") or {}).get("poc_status") not in POC_STATUS:
        p.append("bad poc.poc_status")
    if (rec.get("submission") or {}).get("submission_status") not in SUBMISSION_STATUS:
        p.append("bad submission.submission_status")
    # SAFETY constants (the heart of the contract)
    for k, want in (("research_only", True), ("review_only", True), ("routes_in_production", False),
                    ("routing_allowed", False), ("submission_ready", False), ("human_review_required", True),
                    ("no_submit_controls", True), ("browser_computes_severity", False)):
        if rec.get(k) is not want:
            p.append(f"safety flag {k} must be {want}")
    # severity must never be a conversion/decision token
    sr = rec.get("severity_recommendation")
    if sr is not None and str(sr).strip().lower() not in _SEVERITIES and str(sr) != "HUMAN_PENDING":
        p.append(f"severity_recommendation is not a recorded severity: {sr!r}")
    return p
