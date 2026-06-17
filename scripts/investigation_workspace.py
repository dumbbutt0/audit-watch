"""
Investigation Workspace — pure logic for the research-track investigation environment.

Extends the Human Validation Console (`human_validation.py`) across the next workflow steps:
    Human Validation → Promotion Checklist → Chain Analysis Workspace → (future) PoC Investigation

Layer invariants (each enforced by structure + the shared forbidden-field guard):
  - Promotion Checklist : "prioritize, don't verify"  — records a human's checklist + chosen outcome; never
                          auto-decides promotion, never assigns severity/validity.
  - Chain Analysis      : "explain, don't conclude"    — editable bug-chain sections of hypotheses + evidence
                          refs + open questions; impact stays a hypothesis.
  - Investigation Track : "organize, don't adjudicate" — status + Chain Confidence Evolution (qualitative,
                          manual; not a verdict/severity/validity).

Every row is research_only:true / routing_allowed:false, runs through `human_validation.assert_no_forbidden_fields`,
and writes ONLY to append-only research JSONLs. No bundle / detector / normalization / human-label file is modified.
No FastAPI here (unit-testable core).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import human_validation as hv
from human_validation import LabelValidationError, assert_no_forbidden_fields

PROMOTION_SCHEMA = "promo-1"
CHAIN_SCHEMA = "chain-1"
STATUS_SCHEMA = "status-1"

# --- promotion checklist ------------------------------------------------------
PROMOTION_CATEGORIES = [
    "evidence_coherence", "attacker_reachability", "affected_asset_function", "state_or_invariant",
    "missing_validation", "concrete_impact_hypothesis", "counter_signals_reviewed", "poc_feasibility",
    "scope_relevance", "duplicate_known_issue_risk", "next_step_confidence", "chain_completeness",
]
CATEGORY_STATES = {"met", "partial", "unmet", "unknown"}
_CATEGORY_SCORE = {"met": 1.0, "partial": 0.5, "unmet": 0.0, "unknown": 0.0}
OUTCOMES = {
    "PROMOTE_TO_CHAIN_ANALYSIS", "NEEDS_MORE_EVIDENCE", "HOLD_AS_WEAK_SIGNAL", "ARCHIVE_AS_NOISE",
}

# --- bug-chain builder --------------------------------------------------------
CHAIN_SECTIONS = [
    "Title / Finding Hypothesis", "System Context", "Attacker Preconditions", "Entry Point",
    "Trust Assumption", "Broken Check", "Exploit Path", "State Change", "Impact Hypothesis",
    "PoC Plan", "Counter Signals", "Evidence Inventory", "Open Questions",
]  # index 0 -> section_id 1 ... index 12 -> section_id 13
OPEN_QUESTIONS_SECTION_ID = 13
EVIDENCE_SOURCES = {"bundle", "human_observation", "external_note"}

# --- investigation status -----------------------------------------------------
STATUS_STATES = {
    "not_started", "researching", "chain_mapping", "poc_planning", "blocked", "archived",
}

_PROMO_KEYS = {
    "label_schema_version", "timestamp", "reviewer_alias", "candidate_id", "source_corpus_hash",
    "detector", "candidate_surface", "categories", "outcome", "rationale", "progress_score",
    "completion_status", "routing_allowed", "research_only",
}
_CHAIN_KEYS = {
    "label_schema_version", "timestamp", "reviewer_alias", "candidate_id", "section_id", "section_title",
    "notes", "code_references", "evidence_references", "evidence_attached", "routing_allowed", "research_only",
}
_STATUS_KEYS = {
    "label_schema_version", "timestamp", "reviewer_alias", "candidate_id", "status", "note",
    "initial_confidence", "current_confidence", "reason_for_change", "routing_allowed", "research_only",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_alias(reviewer_alias: str) -> str:
    if not reviewer_alias or not str(reviewer_alias).strip():
        raise LabelValidationError("reviewer_alias is required")
    return str(reviewer_alias).strip()


# ============================================================ promotion checklist
def promotion_progress(categories: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    score = sum(_CATEGORY_SCORE.get(categories.get(c, {}).get("status"), 0.0) for c in PROMOTION_CATEGORIES)
    pct = round(100.0 * score / len(PROMOTION_CATEGORIES), 1)
    addressed = sum(1 for c in PROMOTION_CATEGORIES if categories.get(c, {}).get("status") in CATEGORY_STATES)
    return {"progress_score": pct, "completion_status": "complete" if addressed == len(PROMOTION_CATEGORIES) else "incomplete"}


def build_promotion_row(bundle: Dict[str, Any], reviewer_alias: str, categories: Dict[str, Dict[str, Any]],
                        outcome: str, rationale: str, corpus_hash: str) -> Dict[str, Any]:
    alias = _require_alias(reviewer_alias)
    if outcome not in OUTCOMES:
        raise LabelValidationError(f"invalid outcome {outcome!r}; allowed: {sorted(OUTCOMES)}")
    norm: Dict[str, Dict[str, Any]] = {}
    for cat in PROMOTION_CATEGORIES:
        entry = categories.get(cat) or {}
        bad = hv.FORBIDDEN_KEYS & set(entry.keys())
        if bad:
            raise LabelValidationError(f"forbidden field in category {cat}: {sorted(bad)}")
        status = entry.get("status")
        if status not in CATEGORY_STATES:
            raise LabelValidationError(f"category {cat}: invalid/missing status {status!r}; allowed {sorted(CATEGORY_STATES)}")
        norm[cat] = {
            "status": status,
            "evidence_ref": str(entry.get("evidence_ref") or ""),
            "notes": str(entry.get("notes") or ""),
        }
    prog = promotion_progress(norm)
    row = {
        "label_schema_version": PROMOTION_SCHEMA,
        "timestamp": _now(),
        "reviewer_alias": alias,
        "candidate_id": bundle.get("candidate_id"),
        "source_corpus_hash": corpus_hash,
        "detector": bundle.get("detector"),
        "candidate_surface": bundle.get("candidate_surface"),
        "categories": norm,
        "outcome": outcome,                 # human-chosen; NEVER auto-derived from the score
        "rationale": str(rationale or ""),
        "progress_score": prog["progress_score"],
        "completion_status": prog["completion_status"],
        "routing_allowed": False,
        "research_only": True,
    }
    _assert_keys(row, _PROMO_KEYS)
    assert_no_forbidden_fields_deep(row)
    return row


# ================================================================ chain sections
def build_chain_section_row(candidate_id: str, reviewer_alias: str, section_id: int, notes: str = "",
                            code_references: Optional[List[str]] = None,
                            evidence_references: Optional[List[Dict[str, str]]] = None,
                            evidence_attached: bool = False) -> Dict[str, Any]:
    alias = _require_alias(reviewer_alias)
    if not isinstance(section_id, int) or not (1 <= section_id <= len(CHAIN_SECTIONS)):
        raise LabelValidationError(f"section_id must be 1..{len(CHAIN_SECTIONS)}")
    refs: List[Dict[str, str]] = []
    for r in (evidence_references or []):
        src = (r or {}).get("source")
        if src not in EVIDENCE_SOURCES:
            raise LabelValidationError(f"evidence source {src!r} invalid; allowed {sorted(EVIDENCE_SOURCES)}")
        refs.append({"source": src, "ref": str(r.get("ref") or "")})
    row = {
        "label_schema_version": CHAIN_SCHEMA,
        "timestamp": _now(),
        "reviewer_alias": alias,
        "candidate_id": candidate_id,
        "section_id": section_id,
        "section_title": CHAIN_SECTIONS[section_id - 1],
        "notes": str(notes or ""),
        "code_references": [str(c) for c in (code_references or [])],
        "evidence_references": refs,
        "evidence_attached": bool(evidence_attached),
        "routing_allowed": False,
        "research_only": True,
    }
    _assert_keys(row, _CHAIN_KEYS)
    assert_no_forbidden_fields_deep(row)
    return row


# ================================================================ status + confidence
def build_status_row(candidate_id: str, reviewer_alias: str, status: str, note: str = "",
                     initial_confidence: str = "", current_confidence: str = "",
                     reason_for_change: str = "") -> Dict[str, Any]:
    """Investigation status transition + Chain Confidence Evolution. The three confidence fields are manual,
    qualitative FREE TEXT — the reviewer's confidence in the *hypothesis* over time. NOT a verdict, severity, or
    validity score."""
    alias = _require_alias(reviewer_alias)
    if status not in STATUS_STATES:
        raise LabelValidationError(f"invalid status {status!r}; allowed {sorted(STATUS_STATES)}")
    row = {
        "label_schema_version": STATUS_SCHEMA,
        "timestamp": _now(),
        "reviewer_alias": alias,
        "candidate_id": candidate_id,
        "status": status,
        "note": str(note or ""),
        "initial_confidence": str(initial_confidence or ""),
        "current_confidence": str(current_confidence or ""),
        "reason_for_change": str(reason_for_change or ""),
        "routing_allowed": False,
        "research_only": True,
    }
    _assert_keys(row, _STATUS_KEYS)
    assert_no_forbidden_fields_deep(row)
    return row


# ===================================================================== guards/io
def _assert_keys(row: Dict[str, Any], allowed: set) -> None:
    extra = set(row.keys()) - allowed
    if extra:
        raise LabelValidationError(f"non-allowlisted keys present: {sorted(extra)}")


def assert_no_forbidden_fields_deep(row: Dict[str, Any]) -> None:
    """Forbidden verdict/routing-key guard (shares human_validation.FORBIDDEN_KEYS) applied at the top level
    and one level into the nested promotion `categories` map. Per-schema key allowlists are enforced separately
    by `_assert_keys`, so we deliberately do NOT call hv.assert_no_forbidden_fields here (its hv-1 allowlist
    would reject these schemas' keys)."""
    bad = hv.FORBIDDEN_KEYS & set(row.keys())
    if bad:
        raise LabelValidationError(f"forbidden verdict/routing fields present: {sorted(bad)}")
    for cat, entry in (row.get("categories") or {}).items():
        if cat in hv.FORBIDDEN_KEYS:
            raise LabelValidationError(f"forbidden category key: {cat}")
        if isinstance(entry, dict):
            bad = hv.FORBIDDEN_KEYS & set(entry.keys())
            if bad:
                raise LabelValidationError(f"forbidden field in category {cat}: {sorted(bad)}")


def append_row(row: Dict[str, Any], path: Union[str, Path]) -> None:
    """Append one row as a JSONL line. Never rewrites/overwrites. Creates file + parent if absent."""
    assert_no_forbidden_fields_deep(row)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def read_rows(path: Union[str, Path]) -> List[Dict[str, Any]]:
    return hv._read_jsonl(Path(path))


def latest_promotion_by_candidate(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for r in sorted(rows, key=lambda x: str(x.get("timestamp", ""))):
        cid = r.get("candidate_id")
        if cid is not None:
            out[cid] = r
    return out


def latest_status_by_candidate(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return latest_promotion_by_candidate(rows)  # same "newest-per-candidate" reduction


def latest_sections_by_candidate(rows: List[Dict[str, Any]], candidate_id: str) -> Dict[int, Dict[str, Any]]:
    out: Dict[int, Dict[str, Any]] = {}
    for r in sorted((x for x in rows if x.get("candidate_id") == candidate_id),
                    key=lambda x: str(x.get("timestamp", ""))):
        sid = r.get("section_id")
        if isinstance(sid, int):
            out[sid] = r
    return out


# ===================================================================== overview
def investigation_overview(bundles: List[Dict[str, Any]], promotions: List[Dict[str, Any]],
                           sections: List[Dict[str, Any]], statuses: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_cand_promo = latest_promotion_by_candidate(promotions)
    by_cand_status = latest_status_by_candidate(statuses)
    bundle_by_id = {b.get("candidate_id"): b for b in bundles}

    promoted = [cid for cid, p in by_cand_promo.items() if p.get("outcome") == "PROMOTE_TO_CHAIN_ANALYSIS"]

    def _count(d: Dict[str, str]) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for v in d.values():
            out[v] = out.get(v, 0) + 1
        return out

    status_of = {cid: by_cand_status.get(cid, {}).get("status", "not_started") for cid in promoted}
    in_progress = sum(1 for s in status_of.values() if s in {"researching", "chain_mapping", "poc_planning"})
    blocked = sum(1 for s in status_of.values() if s == "blocked")
    archived = sum(1 for s in status_of.values() if s == "archived")
    poc_planning = sum(1 for s in status_of.values() if s == "poc_planning")

    # average completion across promoted candidates' chains (% of 13 sections with evidence_attached)
    completions = []
    open_q = 0
    for cid in promoted:
        secs = latest_sections_by_candidate(sections, cid)
        attached = sum(1 for s in secs.values() if s.get("evidence_attached"))
        completions.append(100.0 * attached / len(CHAIN_SECTIONS))
        oq = secs.get(OPEN_QUESTIONS_SECTION_ID)
        if oq and (oq.get("notes") or oq.get("evidence_references")):
            open_q += 1
    avg_completion = round(sum(completions) / len(completions), 1) if completions else 0.0

    return {
        "promoted_chains": len(promoted),
        "chains_in_progress": in_progress,
        "chains_blocked": blocked,
        "chains_archived": archived,
        "by_detector": _count({cid: (bundle_by_id.get(cid, {}).get("detector", "?")) for cid in promoted}),
        "by_confidence": _count({cid: (bundle_by_id.get(cid, {}).get("confidence", "?")) for cid in promoted}),
        "by_promotion_outcome": _count({cid: p.get("outcome", "?") for cid, p in by_cand_promo.items()}),
        "by_investigation_status": _count(status_of),
        "average_completion": avg_completion,
        "open_questions_count": open_q,
        "poc_planning_count": poc_planning,
    }


# ===================================================================== export
SAFETY_BANNER = (
    "Research Investigation — Not Validated — Not Severity Rated — Not Submission Ready"
)


def export_investigation_packet_md(bundle: Dict[str, Any], label: Optional[Dict[str, Any]],
                                    promotion: Dict[str, Any], sections: Dict[int, Dict[str, Any]],
                                    status: Optional[Dict[str, Any]]) -> str:
    if promotion.get("outcome") != "PROMOTE_TO_CHAIN_ANALYSIS":
        raise LabelValidationError("export is available only for PROMOTE_TO_CHAIN_ANALYSIS candidates")
    cid = bundle.get("candidate_id")
    L: List[str] = []
    L.append(f"> ⚠ **{SAFETY_BANNER}**")
    L.append("> research_only:true · routing_allowed:false\n")
    L.append(f"# Investigation Packet — {bundle.get('candidate_surface')}")
    L.append(f"`{cid}`\n")

    L.append("## Bundle")
    loc = bundle.get("location") or {}
    L.append(f"- detector: `{bundle.get('detector')}` ({bundle.get('detector_version','')})")
    L.append(f"- signal_type: `{bundle.get('signal_type')}`")
    L.append(f"- carried confidence (detector): `{bundle.get('confidence')}`")
    L.append(f"- declared_severity_potential (carried hint, not a rating): `{bundle.get('declared_severity_potential')}`")
    L.append(f"- location: `{loc.get('file')}:{loc.get('start_line')}`")
    L.append(f"- source_audit_path: `{bundle.get('source_audit_path')}`\n")
    L.append("```solidity")
    L.append(str(bundle.get("code_snippet") or "(no snippet)"))
    L.append("```\n")
    L.append(f"_rationale:_ {bundle.get('rationale','')}\n")

    L.append("## Human Labels")
    if label:
        for k in ("coherence", "investigation_worthiness", "poc_followup_worthiness",
                  "expected_review_effort", "reviewer_confidence"):
            L.append(f"- {k}: `{label.get(k)}`")
        L.append(f"- missing_information: {label.get('missing_information')}")
        L.append(f"- counter_signals: {label.get('counter_signals')}")
        L.append(f"- reviewer_notes: {label.get('reviewer_notes','')}\n")
    else:
        L.append("_(no hv-1 label recorded)_\n")

    L.append("## Promotion Checklist")
    L.append(f"- outcome (human-chosen): **{promotion.get('outcome')}**")
    L.append(f"- progress_score: {promotion.get('progress_score')}% · {promotion.get('completion_status')}")
    L.append(f"- reviewer: `{promotion.get('reviewer_alias')}`")
    L.append("")
    L.append("| category | status | evidence_ref | notes |")
    L.append("|---|---|---|---|")
    for cat in PROMOTION_CATEGORIES:
        e = (promotion.get("categories") or {}).get(cat, {})
        L.append(f"| {cat} | {e.get('status','')} | {e.get('evidence_ref','')} | {e.get('notes','')} |")
    L.append(f"\n_rationale:_ {promotion.get('rationale','')}\n")

    L.append("## Chain Sections")
    for sid in range(1, len(CHAIN_SECTIONS) + 1):
        s = sections.get(sid)
        L.append(f"### {sid}. {CHAIN_SECTIONS[sid-1]}")
        if not s:
            L.append("_⟦UNKNOWN⟧ — not yet authored_\n")
            continue
        L.append(f"- Evidence Attached? **{'Yes' if s.get('evidence_attached') else 'No'}**")
        if s.get("notes"):
            L.append(f"\n{s.get('notes')}\n")
        for c in s.get("code_references") or []:
            L.append(f"- code: `{c}`")
        for r in s.get("evidence_references") or []:
            L.append(f"- evidence [{r.get('source')}]: {r.get('ref')}")
        L.append("")

    L.append("## Chain Confidence Evolution _(qualitative, manual — not a verdict / not a severity)_")
    if status:
        L.append(f"- initial_confidence: {status.get('initial_confidence','') or '⟦UNKNOWN⟧'}")
        L.append(f"- current_confidence: {status.get('current_confidence','') or '⟦UNKNOWN⟧'}")
        L.append(f"- reason_for_change: {status.get('reason_for_change','') or '⟦UNKNOWN⟧'}")
        L.append(f"- investigation status: `{status.get('status')}`\n")
    else:
        L.append("_(no status / confidence recorded)_\n")

    oq = sections.get(OPEN_QUESTIONS_SECTION_ID)
    L.append("## Open Questions")
    if oq and oq.get("notes"):
        L.append(oq.get("notes"))
    else:
        L.append("_⟦UNKNOWN⟧ — open questions not yet recorded_")
    L.append("")
    return "\n".join(L)
