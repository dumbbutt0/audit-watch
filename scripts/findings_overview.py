"""findings_overview — read-only unified "Findings at a glance" aggregator (research-only).

Aggregates the project's three research tracks into ONE normalized, glanceable list:

  1. runtime   — value-provenance runtime findings (B1, B5, H1..H5 incl. abracadabra H5),
                 read DIRECTLY from output_research/value_provenance_eval/runtime_status.jsonl.
                 (We never import value_provenance_eval_harness — it stays un-wired.)
  2. funnel    — blind/assisted PoC arc, via funnel.load_records() (Vultisig, secondswap, ...).
  3. detector  — detector leads, via human_validation.load_corpus() (multicall_invariant, permit_asset_binding).

HARD INVARIANTS (this module is display-only):
  * Read-only. It opens files for reading and never writes/mutates any sidecar, corpus, panel, or symlink.
  * It NEVER routes, sets severity, or marks anything submittable. It only surfaces labels that already exist.
  * Every payload is stamped research_only=True / routing_allowed=False.
  * Defensive: if any one track fails to load, the others still render (the page never crashes).
"""

from __future__ import annotations

import json
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional


def finding_key(track: str, fid: str) -> str:
    """Stable, track-qualified candidate_id key used to deep-link every finding to its detail page.

    detector → raw candidate_id (back-compatible); runtime → 'runtime:<id>'; funnel → 'funnel:<id>'.
    """
    if track == "runtime":
        return f"runtime:{fid}"
    if track == "funnel":
        return f"funnel:{fid}"
    if track == "option_a_campaign":
        return f"campaign:{fid}"
    return str(fid)  # detector: the raw candidate_id (already detector-prefixed by construction)

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_SIDECAR = ROOT / "output_research/value_provenance_eval/runtime_status.jsonl"
CAMPAIGN_LEDGER = ROOT / "output_research/option_a_campaign/ledger.jsonl"
JUDGE_CORPUS = ROOT / "documentation/evals/judge_corpus/frozen_corpus.json"

# Glance ordering: lower rank = stronger signal = sorts to the top.
_STATE_RANK = {
    "REPORTABLE_CANDIDATE": 0,
    "READY_FOR_HUMAN_REVIEW": 1,
    "REPRODUCED": 2,
    "CONFIRMED_NEEDS_POC": 3,
    "RUNTIME_CONFIRMED": 3,
    "PRIVILEGED_ONLY": 4,
    "NEEDS_CONTEXT": 5,
    "LEAD": 6,
    "INVESTIGATED": 6,
    "NOT_RUN": 7,
    "NOT_RUN_TOO_HEAVY": 7,
    "RUNTIME_REFUTED": 8,
    "STATIC_FALSE_POSITIVE": 8,
}
_DEFAULT_RANK = 6


def _rank(state: str) -> int:
    return _STATE_RANK.get(state, _DEFAULT_RANK)


# (P222) Effective sort rank: human-review priority surfaces a not-auto-reportable finding above ordinary
# mid-rank noise, but NEVER above a genuinely reportable-ready candidate (glance_rank <= 1) and NEVER below
# refuted/false-positive rows (which the priority helper only ever marks NONE/LOW). Display ordering only.
def _effective_rank(row: Dict[str, Any]) -> float:
    base = float(row.get("glance_rank", _DEFAULT_RANK))
    if base <= 1:                       # reportable-ready / ready-for-human-review stay on top
        return base
    prio = row.get("human_review_priority") or "NONE"
    # priority only ever BOOSTS (min), never demotes a row below its natural pipeline rank.
    if prio in ("HIGH", "CRITICAL_HUMAN_REVIEW"):
        return min(base, 1.5)           # just below reportable-ready, above everything ordinary
    if prio == "MEDIUM":
        return min(base, 4.5)
    return base


_REPORTABLE = "reportable_candidate_needs_human_review"


def is_reportable_candidate(row: Dict[str, Any]) -> bool:
    """Canonical, candidate-scoped predicate (EXACT field equality — never substring). A finding is a
    reportable candidate iff any recorded reportable signal holds. Display-only: callers must keep
    submission_ready/routing_allowed false; this never flips those."""
    if not isinstance(row, dict):
        return False
    if row.get("conversion_outcome") == _REPORTABLE:
        return True
    conv = row.get("conversion")
    if isinstance(conv, dict) and conv.get("outcome") == _REPORTABLE:
        return True
    if row.get("p155_gate7_final_outcome") == "remains_" + _REPORTABLE:
        return True
    if row.get("valid_finding") is True and row.get("human_review_required") is True:
        return True
    return False


def _rel(p: Optional[str]) -> Optional[str]:
    if not p:
        return None
    try:
        pp = Path(p)
        return str(pp.relative_to(ROOT)) if pp.is_absolute() and ROOT in pp.parents else str(p)
    except Exception:  # noqa: BLE001
        return str(p)


# --------------------------------------------------------------------------- runtime track
def _runtime_state(row: Dict[str, Any]) -> str:
    if is_reportable_candidate(row):
        return "REPORTABLE_CANDIDATE"
    conv = row.get("conversion") or {}
    outcome = conv.get("outcome")
    mapping = {
        "reportable_candidate_needs_human_review": "REPORTABLE_CANDIDATE",
        "runtime_confirmed_but_privileged_only": "PRIVILEGED_ONLY",
        "runtime_refuted": "RUNTIME_REFUTED",
        "needs_context": "NEEDS_CONTEXT",
    }
    if outcome in mapping:
        return mapping[outcome]
    rs = (row.get("runtime_status") or "").lower()
    if rs == "runtime_confirmed":
        return "RUNTIME_CONFIRMED"
    if rs == "runtime_refuted":
        return "RUNTIME_REFUTED"
    if rs == "not_run":
        return "NOT_RUN"
    return "INVESTIGATED"


def _load_runtime() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not RUNTIME_SIDECAR.exists():
        return rows
    for line in RUNTIME_SIDECAR.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        state = _runtime_state(r)
        conv = r.get("conversion") or {}
        sev = (r.get("final_severity_recommendation") or r.get("severity_recommendation")
               or r.get("severity_class") or r.get("runtime_confidence"))
        rows.append({
            "track": "runtime",
            "id": r.get("item_id") or r.get("bug_id"),
            "subject": r.get("target") or r.get("bug_id"),
            "location": _rel(r.get("harness_path") or r.get("test_path")),
            "workspace": r.get("architecture") or "—",
            "state": state,
            "status_detail": r.get("runtime_status"),
            "severity_or_conversion": sev,
            "conversion_outcome": conv.get("outcome"),
            "duplicate_status": r.get("duplicate_status"),
            "summary": r.get("divergence_summary"),
            # display-only mirrors of the source flags; this module forces nothing submittable.
            "submission_ready": bool(r.get("submission_ready", False)),
            "routing_allowed": False,
            "glance_rank": _rank(state),
        })
    return rows


# --------------------------------------------------------------------------- funnel track
def _funnel_state(rec: Dict[str, Any]) -> str:
    if is_reportable_candidate(rec):
        return "REPORTABLE_CANDIDATE"
    if rec.get("submitted"):
        return "SUBMITTED"
    pipe = (rec.get("pipeline_status") or "").upper()
    poc = (rec.get("poc_status") or "").upper()
    if "HUMAN_REVIEW" in pipe or rec.get("human_readiness") in ("READY_FOR_HUMAN_REVIEW",):
        return "READY_FOR_HUMAN_REVIEW"
    if poc == "REPRODUCED":
        return "REPRODUCED"
    # system-confirmed (multi-pass) + testable candidate, but no PoC yet — a real card, NOT noise. The sync only
    # emits a NOT_STARTED/IN_PROGRESS candidate_finding when it is confidently real + testable (weak findings stay
    # target notes), so a clean-hit candidate with no PoC maps to CONFIRMED_NEEDS_POC (honest: not reproduced).
    if poc in ("NOT_STARTED", "IN_PROGRESS") and rec.get("conversion") in ("CLEAN_HIT", "STRONG_PARTIAL"):
        return "CONFIRMED_NEEDS_POC"
    if rec.get("conversion") in ("CLEAN_HIT", "STRONG_PARTIAL"):
        return "INVESTIGATED"
    return pipe or "INVESTIGATED"


def _load_funnel() -> List[Dict[str, Any]]:
    try:
        import funnel  # read-only loader (already used by /api/funnel)
        payload = funnel.load_records()
    except Exception:  # noqa: BLE001
        return []
    rows: List[Dict[str, Any]] = []
    for rec in payload.get("records", []):
        state = _funnel_state(rec)
        links = rec.get("artifact_links") or {}
        rows.append({
            "track": "funnel",
            "id": rec.get("finding_id") or rec.get("record_id") or rec.get("candidate_id"),
            "subject": rec.get("finding_title") or rec.get("contract_function") or rec.get("subject"),
            "location": rec.get("contract_function"),
            "workspace": rec.get("subject") or "—",
            "state": state,
            "status_detail": rec.get("pipeline_status"),
            "severity_or_conversion": rec.get("conversion") or rec.get("claimed_severity"),
            "conversion_outcome": rec.get("conversion"),
            "duplicate_status": (rec.get("submission") or {}).get("duplicate_check_status")
            or rec.get("duplicate_check"),
            "summary": rec.get("blocker_reason") or rec.get("impact"),
            "submission_ready": False,
            "routing_allowed": False,
            "link": _rel(links.get("test") or links.get("bundle") or links.get("dir")),
            "glance_rank": _rank(state),
            # (P222) human-review priority lane — display/prioritization only (from the synced row).
            "human_review_priority": rec.get("human_review_priority") or "NONE",
            "human_review_reason_codes": rec.get("human_review_reason_codes") or [],
            "reachability_class": rec.get("reachability_class"),
            "should_surface_above_noise": bool(rec.get("should_surface_above_noise")),
        })
    return rows


# --------------------------------------------------------------------------- detector track
def _load_detector() -> List[Dict[str, Any]]:
    try:
        import human_validation as hv  # read-only corpus loader (already used by /api/validation)
        c = hv.load_corpus(JUDGE_CORPUS)
    except Exception:  # noqa: BLE001
        return []
    rows: List[Dict[str, Any]] = []
    for b in c.get("bundles", []):
        loc = b.get("location") or {}
        rows.append({
            "track": "detector",
            "id": b.get("candidate_id"),
            "subject": b.get("candidate_surface"),
            "location": (f"{loc.get('file')}:{loc.get('start_line')}" if loc.get("file") else None),
            "workspace": b.get("workspace") or "—",
            "state": "LEAD",
            "status_detail": b.get("bundle_status"),
            "severity_or_conversion": b.get("declared_severity_potential"),
            "conversion_outcome": None,
            "duplicate_status": None,
            "detector": b.get("detector"),
            "confidence": b.get("confidence"),
            "summary": (b.get("rationale") or "")[:200] or None,
            "submission_ready": False,
            "routing_allowed": False,
            "glance_rank": _rank("LEAD"),
        })
    return rows


# --------------------------------------------------------------------------- option-A campaign track
def _campaign_state(row: Dict[str, Any]) -> str:
    if is_reportable_candidate(row):
        return "REPORTABLE_CANDIDATE"
    outcome = (row.get("conversion_outcome") or "").lower()
    mapping = {
        "reportable_candidate_needs_human_review": "REPORTABLE_CANDIDATE",
        "runtime_confirmed_but_privileged_only": "PRIVILEGED_ONLY",
        "runtime_refuted": "RUNTIME_REFUTED",
        "static_false_positive": "STATIC_FALSE_POSITIVE",
        "needs_context": "NEEDS_CONTEXT",
    }
    if outcome in mapping:
        return mapping[outcome]
    rs = (row.get("runtime_status") or "").lower()
    if rs == "not_run":
        blob = f"{row.get('deploy_complexity','')} {row.get('primary_blocker','')}".lower()
        return "NOT_RUN_TOO_HEAVY" if "too_heavy" in blob or "deploy_too_heavy" in blob else "NOT_RUN"
    return {"runtime_confirmed": "RUNTIME_CONFIRMED", "runtime_refuted": "RUNTIME_REFUTED"}.get(rs, "INVESTIGATED")


def _load_campaign(runtime_ids: set) -> List[Dict[str, Any]]:
    """Option-A campaign ledger (read-only). Emits only rows NOT already present as a runtime row
    (de-dup: the runtime sidecar stays canonical; H5 is surfaced from runtime, badged campaign_member)."""
    rows: List[Dict[str, Any]] = []
    if not CAMPAIGN_LEDGER.exists():
        return rows
    for line in CAMPAIGN_LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        cid = r.get("candidate_id")
        if not cid or cid in runtime_ids:
            continue  # de-dup: already shown as a canonical runtime row
        state = _campaign_state(r)
        rows.append({
            "track": "option_a_campaign",
            "id": cid,
            "subject": r.get("mechanism_class") or r.get("surface_function") or cid,
            "location": r.get("audit"),
            "workspace": r.get("architecture") or r.get("audit") or "—",
            "state": state,
            "status_detail": r.get("runtime_status"),
            "severity_or_conversion": r.get("severity_recommendation") or r.get("severity_ceiling_estimate"),
            "conversion_outcome": r.get("conversion_outcome"),
            "duplicate_status": r.get("duplicate_status"),
            "novelty_status": r.get("novelty_status"),
            "summary": r.get("why"),
            "submission_ready": False,
            "routing_allowed": False,
            "glance_rank": _rank(state),
        })
    return rows


def _campaign_ids() -> set:
    ids: set = set()
    if not CAMPAIGN_LEDGER.exists():
        return ids
    for line in CAMPAIGN_LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ids.add(json.loads(line).get("candidate_id"))
        except Exception:  # noqa: BLE001
            continue
    return ids


# --------------------------------------------------------------------------- public API
def load_overview() -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    runtime_rows = _load_runtime()
    rows.extend(runtime_rows)
    rows.extend(_load_funnel())
    rows.extend(_load_detector())
    # de-dup: campaign rows already present as a runtime row are badged on the runtime row, not duplicated
    runtime_ids = {r.get("id") for r in runtime_rows}
    campaign_ids = _campaign_ids()
    for r in runtime_rows:
        if r.get("id") in campaign_ids:
            r["campaign_member"] = True
    rows.extend(_load_campaign(runtime_ids))
    # Attach the stable detail key + deep-link + labelability to every row (display-only).
    for r in rows:
        key = finding_key(r["track"], r.get("id") or "")
        r["key"] = key
        r["detail_href"] = "/candidates?candidate_id=" + urllib.parse.quote(key, safe="")
        r["labelable"] = (r["track"] == "detector")  # only detector corpus candidates are labelable
    # Stable sort: effective_rank (P222 priority-aware), then glance_rank, then track, then subject — strongest
    # signals on top. effective_rank only re-ranks not-auto-reportable rows that carry a human-review priority.
    rows.sort(key=lambda r: (_effective_rank(r), r.get("glance_rank", _DEFAULT_RANK),
                             r.get("track", ""), str(r.get("subject") or "")))

    by_track: Dict[str, int] = {}
    by_state: Dict[str, int] = {}
    for r in rows:
        by_track[r["track"]] = by_track.get(r["track"], 0) + 1
        by_state[r["state"]] = by_state.get(r["state"], 0) + 1

    return {
        "summary": {
            "total": len(rows),
            "by_track": by_track,
            "by_state": by_state,
            "reportable_candidates": by_state.get("REPORTABLE_CANDIDATE", 0),
            "submission_ready": 0,  # display-only board; nothing is marked submittable here
        },
        "rows": rows,
        "research_only": True,
        "routing_allowed": False,
        "routes_in_production": False,
        "note": "Display-only board. States mirror labels already recorded by each track; this page never "
                "routes, sets severity, or marks anything submittable.",
    }
