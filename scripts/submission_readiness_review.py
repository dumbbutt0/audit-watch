"""submission_readiness_review — human-owned submission-readiness overlay (research-only, append-only).

A finding can be `reportable_candidate_needs_human_review` WITHOUT being submission-ready. This module records
a human's readiness decision into ONE new append-only file and **never** flips `submission_ready` /
`routing_allowed`, never auto-promotes, never mutates the canonical finding (runtime sidecar / campaign ledger
/ detector corpus are read-only here). Readiness is an OVERLAY, separate from the candidate's state badge.

INVARIANTS: writes only `output_research/human_submission_review/submission_readiness.jsonl`; every row is
`research_only=true` / `routing_allowed=false` and never carries `submission_ready=true`; un-wired; fail-open
on reads; a `ready_for_submission_package` decision is gated by authoritative finding facts + the checklist.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "output_research/human_submission_review/submission_readiness.jsonl"
CHECKLIST_VERSION = "v1"

READINESS_STATES = {
    "not_reviewed", "not_ready", "ready_for_submission_package", "blocked_by_duplicate", "blocked_by_scope",
    "blocked_by_severity_too_low", "blocked_by_missing_poc", "blocked_by_missing_reachability",
    "blocked_by_missing_impact", "blocked_by_missing_novelty", "needs_more_context",
    # P210 L3 dark-wiring (only ever produced when AUDITWATCH_L3_READINESS is enabled; see l3_evaluate)
    "blocked_by_missing_l3_poc",
}
_REPORTABLE = "reportable_candidate_needs_human_review"
_SEVERITIES = {"High", "Medium", "Low", "QA", "no_security_impact"}

# Derived, read-only DISPLAY status for the human packaging-review state. This is a separate concept from the
# canonical machine-owned `submission_ready` flag — it is computed from `readiness_state` and NEVER flips the
# canonical flag (which stays false). Resolves the "readiness_state=ready_for_submission_package vs
# submission_ready=false" UI contradiction by presenting the two as distinct labels.
DISPLAY_SUBMISSION_STATUS = {
    "ready_for_submission_package": "SUBMISSION_READY",
    "not_reviewed": "NOT_REVIEWED",
    "needs_more_context": "REVIEW_REQUIRED",
    "not_ready": "NOT_READY",
    "blocked_by_missing_l3_poc": "BLOCKED_L3",
}


def display_submission_status(state: Optional[str]) -> str:
    if state in DISPLAY_SUBMISSION_STATUS:
        return DISPLAY_SUBMISSION_STATUS[state]
    return "BLOCKED" if str(state or "").startswith("blocked_by_") else "NOT_READY"


def effective_submission_ready(state: Optional[str]) -> bool:
    """Display-only: a human marked the package ready. Does NOT imply the canonical submission gate passed."""
    return state == "ready_for_submission_package"


# ------------------------------------------------------------------ P210: L3 HIGH readiness (dark, default-off)
# Enforced ONLY when AUDITWATCH_L3_READINESS is enabled. Flag-off, none of this runs and behavior is unchanged.
# Advisory/readiness-only: never flips submission_ready/routing_allowed, never submits/routes/promotes/demotes.
L3_DIR = ROOT / "output_research/l3_readiness"
_L3_HIGH_TARGETS = {"High", "Critical"}


def _l3_enabled() -> bool:
    return os.environ.get("AUDITWATCH_L3_READINESS") in ("1", "true", "True", "yes", "on")


def _load_l3_record(candidate_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Read the per-candidate L3 readiness record (research-only). Missing/malformed -> None (fail-closed for High)."""
    if not candidate_id:
        return None
    p = L3_DIR / f"{candidate_id}.json"
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
        return rec if isinstance(rec, dict) else None
    except Exception:  # noqa: BLE001 - missing file / malformed JSON -> fail closed
        return None


def l3_evaluate(l3_record: Optional[Dict[str, Any]], severity_target: Optional[str]) -> Dict[str, Any]:
    """PURE: apply the P208 L3 policy for a High/Critical target. No I/O, no side effects.

    Returns {"applies": False} for non-High targets (L3 not required). For High/Critical, runs the imported P208
    decide() over the record ({} if missing/malformed -> fails closed) and returns advisory readiness fields.
    """
    if severity_target not in _L3_HIGH_TARGETS:
        return {"applies": False, "research_only": True, "routing_allowed": False}
    from validate_p208_l3_readiness import decide  # lazy import; decide() is pure + side-effect-free
    d = decide(l3_record or {})
    rec = l3_record or {}
    return {
        "applies": True,
        "high_promotion_allowed": bool(d.get("high_promotion_allowed")),
        "high_promotion_blocker": d.get("high_promotion_blocker", ""),
        "l3_status": rec.get("l3_status", "NOT_ATTEMPTED"),
        "poc_tier": rec.get("poc_tier", "NONE"),
        "calibrated_severity_after_l3": d.get("calibrated_severity"),
        "l3_blocker_codes": ([] if d.get("high_promotion_allowed") else ["blocked_by_missing_l3_poc"]),
        "human_override_required": (rec.get("l3_status") not in ("PASS", "HUMAN_OVERRIDE")),
        "human_override_reason": (rec.get("source_validity_notes", "") if rec.get("l3_status") == "HUMAN_OVERRIDE" else ""),
        "l3_evidence_summary": " | ".join(x for x in [rec.get("poc_path", ""), rec.get("actual_delta", ""),
                                                       rec.get("expected_delta_or_control", "")] if x),
        "record_present": bool(l3_record),
        # P214: pass through DoS carve-out fields when decide() evaluated them (flag-on); absent flag-off.
        "dos_carveout_evaluated": d.get("dos_carveout_evaluated", False),
        "dos_carveout_applied": d.get("dos_carveout_applied", False),
        "dos_carveout_blocker": d.get("dos_carveout_blocker", ""),
        "dos_carveout_missing_criteria": d.get("dos_carveout_missing_criteria", []),
        "research_only": True,
        "routing_allowed": False,
    }


# ------------------------------------------------------------------ read helpers (fail-open)
def _read_rows() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not LEDGER.exists():
        return rows
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:  # noqa: BLE001
            continue
    return rows


def latest_row(candidate_id: str) -> Optional[Dict[str, Any]]:
    out = None
    for r in _read_rows():
        if r.get("candidate_id") == candidate_id:
            out = r  # append-only → last wins
    return out


def latest_state(candidate_id: str) -> str:
    r = latest_row(candidate_id)
    return (r or {}).get("new_readiness_state", "not_reviewed")


def overlay() -> Dict[str, str]:
    """{candidate_id (unified key): latest readiness_state} for dashboard badges."""
    out: Dict[str, str] = {}
    for r in _read_rows():
        cid = r.get("candidate_id")
        if cid:
            out[cid] = r.get("new_readiness_state", "not_reviewed")
    return out


def _md5(p: Path) -> Optional[str]:
    try:
        return hashlib.md5(p.read_bytes()).hexdigest()
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------------ authoritative facts + gate
def _facts(candidate_id: str) -> Dict[str, Any]:
    """Gate facts from the canonical finding (read-only). Lazy imports to avoid any cycle."""
    try:
        import finding_detail as fd
        import findings_overview as fo
        d = fd.load_unified_detail(candidate_id)
    except Exception:  # noqa: BLE001
        return {"exists": False}
    if not isinstance(d, dict) or d.get("state") == "NOT_FOUND":
        return {"exists": False}
    conv = (d.get("verifier_evidence") or {}).get("conversion") or {}
    raw = d.get("raw_row") or d.get("raw_record") or {}
    co = d.get("conversion_outcome") or raw.get("conversion_outcome")
    return {
        "exists": True,
        "candidate_id": candidate_id,
        "track": d.get("track"),
        "conversion_outcome": co,
        "valid_finding": raw.get("valid_finding") is True,
        "mechanism_confirmed": conv.get("mechanism_confirmed") is True,
        "attacker_reachable": conv.get("attacker_reachable") is True,
        "severity_bearing": conv.get("severity_bearing") is True,
        "reportable": bool(fo.is_reportable_candidate(raw)) or (co == _REPORTABLE),
        "submission_ready": bool(d.get("submission_ready", False)),
        "routing_allowed": bool(d.get("routing_allowed", False)),
    }


def evaluate(answers: Dict[str, Any], facts: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Required-logic gate for ready_for_submission_package. Returns (eligible, failed_checks)."""
    a = answers or {}
    failed: List[str] = []
    # authoritative finding facts (cannot be overridden by the form)
    if not (facts.get("reportable") or facts.get("valid_finding")):
        failed.append("finding is not reportable_candidate / valid_finding")
    if not facts.get("mechanism_confirmed"):
        failed.append("mechanism_confirmed is not true (canonical)")
    if not facts.get("attacker_reachable"):
        failed.append("attacker_reachable is not true (canonical)")
    if not facts.get("severity_bearing"):
        failed.append("severity_bearing is not true (canonical)")
    # human checklist answers
    if a.get("mechanism_confirmed") != "yes":
        failed.append("q1 mechanism confirmed")
    if a.get("reachability_confirmed") != "yes":
        failed.append("q2 attacker reachability confirmed")
    if a.get("severity_bearing") != "yes":
        failed.append("q3 severity-bearing impact shown")
    if a.get("poc_complete") != "yes":
        failed.append("q4 PoC evidence complete")
    if a.get("impact_not_overclaimed") != "yes":
        failed.append("q5 impact wording not overclaimed")
    if a.get("severity_recommendation") not in _SEVERITIES:
        failed.append("q6 severity recommendation chosen (not unknown)")
    if a.get("scope_caveats_reviewed") != "yes":
        failed.append("q7 scope caveats reviewed")
    nov = a.get("novelty")
    if nov == "duplicate_found":
        failed.append("q8 novelty: duplicate_found blocks")
    elif nov in ("duplicate_unknown", "cannot_assess") and not str(a.get("novelty_override_note") or "").strip():
        failed.append("q8 novelty unknown/cannot_assess requires an override note")
    elif nov not in ("novelty_clear", "public_known_but_not_duplicate", "duplicate_unknown", "cannot_assess"):
        failed.append("q8 novelty not assessed")
    if a.get("report_draft_exists") != "yes":
        failed.append("q9 report draft exists")
    if a.get("mitigation_included") != "yes":
        failed.append("q10 recommended mitigation included")
    if a.get("assumptions_included") != "yes":
        failed.append("q11 assumptions and limitations included")
    if not str(a.get("notes") or "").strip():
        failed.append("q13 reviewer notes are non-empty")
    # P210: L3 HIGH readiness gate — dark, default-off. Only High/Critical targets, only when flag enabled.
    if _l3_enabled():
        target = a.get("severity_recommendation")
        if target in _L3_HIGH_TARGETS:
            l3 = l3_evaluate(_load_l3_record(facts.get("candidate_id")), target)
            if not l3.get("high_promotion_allowed"):
                failed.append("blocked_by_missing_l3_poc: " + (l3.get("high_promotion_blocker") or "L3 PASS/override required"))
    return (len(failed) == 0, failed)


def _unified_keys() -> set:
    try:
        import findings_overview as fo
        return {r.get("key") for r in fo.load_overview().get("rows", [])} | \
               {r.get("id") for r in fo.load_overview().get("rows", [])}
    except Exception:  # noqa: BLE001
        return set()


# ------------------------------------------------------------------ write (append-only; never flips flags)
def record_review(candidate_id: str, reviewer: str, answers: Dict[str, Any],
                  decision: str, notes: str = "") -> Dict[str, Any]:
    if candidate_id not in _unified_keys():
        raise ValueError(f"unknown candidate_id: {candidate_id}")
    if decision not in READINESS_STATES or decision == "not_reviewed":
        raise ValueError(f"invalid decision: {decision}")
    facts = _facts(candidate_id)
    answers = dict(answers or {})
    if notes and not answers.get("notes"):
        answers["notes"] = notes

    if decision == "ready_for_submission_package":
        eligible, failed = evaluate(answers, facts)
        if not eligible:
            # never persist a false "ready"
            return {"saved": False, "blocked": True, "readiness_state": latest_state(candidate_id),
                    "failed_checks": failed, "facts": facts, "research_only": True, "routing_allowed": False}
        new_state = "ready_for_submission_package"
    else:
        new_state = decision  # a human-chosen blocked / not_ready / needs_context state

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reviewer": reviewer or "anonymous",
        "candidate_id": candidate_id,
        "track": facts.get("track"),
        "previous_readiness_state": latest_state(candidate_id),
        "new_readiness_state": new_state,
        "checklist_version": CHECKLIST_VERSION,
        "checklist": answers,
        "notes": notes or answers.get("notes", ""),
        "source_hashes": {
            "runtime_sidecar": _md5(ROOT / "output_research/value_provenance_eval/runtime_status.jsonl"),
            "campaign_ledger": _md5(ROOT / "output_research/option_a_campaign/ledger.jsonl"),
            "frozen_corpus": _md5(ROOT / "documentation/evals/judge_corpus/frozen_corpus.json"),
        },
        "research_only": True,
        "routing_allowed": False,
        # NB: submission_ready is intentionally never set true by this overlay.
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return {"saved": True, "readiness_state": new_state, "row": row,
            "research_only": True, "routing_allowed": False}


def detail_overlay(candidate_id: str) -> Dict[str, Any]:
    """Read-only overlay block for a candidate detail page. Carries a DERIVED display status separate from the
    canonical `submission_ready` flag (which lives on the finding and stays false)."""
    r = latest_row(candidate_id)
    state = (r or {}).get("new_readiness_state", "not_reviewed")
    out = {
        "readiness_state": state,
        # derived, display-only — NOT the canonical submission_ready flag
        "submission_package_status": display_submission_status(state),
        "effective_submission_ready": effective_submission_ready(state),
        "last_row": r,
        "last_note": (r or {}).get("notes") or None,
        "facts": _facts(candidate_id),
        "research_only": True, "routing_allowed": False,
    }
    # P210: read-only L3 readiness block, dark/default-off.
    if _l3_enabled():
        target = ((r or {}).get("checklist") or {}).get("severity_recommendation")
        out["l3"] = l3_evaluate(_load_l3_record(candidate_id), target)
    return out
