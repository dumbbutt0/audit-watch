#!/usr/bin/env python3
"""
maximal_consequence_check.py — P90 ADVISORY impact-escalation aid (RESEARCH-ONLY, UN-WIRED).

Targets the recurring UNDER-labelling miss surfaced by the blind runs (P87 H-01 mintWithBudget and P89 H-05
public-helpers were converted but rated Medium vs awarded High), plus admin-footgun misclassification (P87 H-03)
and self-inflicted-vs-involuntary misread (P87 M-18, P85 M-01).

It does NOT modify or call `severity_impact_gate`. It only RECOMMENDS, before severity labelling, whether a
Medium-looking mechanism should be escalated to High and which gate markers to attach — the SAME
`high_liveness_markers` / `involuntary` / liveness consequence tags the existing P88 gate already consumes. The
investigator attaches the recommended markers to the impact_assessment; the unchanged gate then decides.

REJECT-FIRST: escalation REQUIRES `source_backed=True`. A bounded/lazy issue with no concrete consequence is
NEVER escalated (it defers to the gate's bounded-demote). The check never demotes and never sets production
severity.

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
"""
from __future__ import annotations
import argparse
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
CFG = ROOT / "config" / "maximal_consequence_check.json"
FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


class ConsequenceAssessment(NamedTuple):
    recommended_impact_class: str   # advisory only; gate still decides keep/demote
    escalate: bool
    attach_high_markers: List[str]  # high_liveness_markers to attach for the gate's P88 elevation
    attach_involuntary: bool
    footgun_flag: bool
    reason: str


def assess(impact_assessment: Optional[Dict[str, Any]] = None) -> ConsequenceAssessment:
    cfg = _cfg()
    ia = impact_assessment or {}
    base = str(ia.get("base_impact_class") or ia.get("impact_class") or "").lower()
    source = bool(ia.get("source_backed", False))
    escalators = cfg["high_escalators"]
    asserted = [q for q in escalators if ia.get(q) is True]

    concrete = bool(ia.get("concrete")) or bool(ia.get("material_consequence"))
    involuntary = bool(ia.get("involuntary_third_party_or_race")) or bool(ia.get("involuntary"))
    admin_initiated = bool(ia.get("admin_initiated"))
    external_user_harm = bool(ia.get("externally_triggerable_user_harm"))

    # (1) reject-first: escalation requires source-backed evidence.
    if asserted and not source:
        return ConsequenceAssessment(base or "medium", False, [], False, False,
            f"escalators asserted {asserted} but NOT source_backed -> NO escalation (reject-first); "
            "supply source evidence before raising to High")

    # (2) source-backed High escalator(s) -> recommend High + attach the mapped gate markers.
    if asserted and source:
        markers = sorted({escalators[q] for q in asserted})
        return ConsequenceAssessment("high", True, markers, involuntary, False,
            f"maximal-consequence escalation: source-backed {asserted} -> recommend High; "
            f"attach high_liveness_markers {markers} (+ involuntary) for the gate")

    # (3) involuntary harm with a concrete consequence -> keep, mark involuntary (not self-inflicted).
    if involuntary and concrete:
        return ConsequenceAssessment(base or "medium", False, [], True, False,
            "involuntary third-party/race harm WITH a concrete consequence -> NOT self-inflicted; "
            "keep >= Medium and attach an involuntary marker for the gate")

    # (4) admin-footgun vs user harm.
    if admin_initiated and not external_user_harm and not concrete:
        return ConsequenceAssessment(base or "low", False, [], False, True,
            "admin-only, no external trigger, no user funds at risk -> admin footgun; do not promote as user harm")
    if admin_initiated and external_user_harm:
        # a normal admin action with a user-facing consequence is NOT a mere footgun
        return ConsequenceAssessment(base or "medium", False, [], False, False,
            "admin-initiated but USER-FACING consequence -> NOT a mere footgun; assess on consequence (>= Medium)")

    # (5) nothing to escalate -> base unchanged (the gate still applies P86 bounded-demote etc.)
    return ConsequenceAssessment(base or "", False, [], False, False,
        "no source-backed maximal-consequence escalator -> base impact unchanged (gate decides)")


def _self_test() -> int:
    ok = True
    def chk(c, m):
        nonlocal ok; ok &= c; print(f"  [{'PASS' if c else 'FAIL'}] {m}")
    # P89 H-05: medium base, source-backed, all-users + permanent corruption -> escalate High
    h05 = assess({"base_impact_class": "medium", "source_backed": True,
                  "many_or_all_users_affected": True, "mass_dos_or_permanent_state_corruption": True,
                  "material_consequence": ["unauthorized_execution"]})
    chk(h05.escalate and h05.recommended_impact_class == "high" and bool(h05.attach_high_markers),
        "P89 H-05 -> escalate High + markers")
    # P87 H-01: medium base, source-backed, core function permanently bricked + all users -> High
    h01 = assess({"base_impact_class": "medium", "source_backed": True,
                  "core_protocol_lifecycle_function": True, "permanent_unrecoverable_without_privileged": True,
                  "many_or_all_users_affected": True})
    chk(h01.escalate and h01.recommended_impact_class == "high", "P87 H-01 -> escalate High")
    # reject-first: escalators claimed but NOT source-backed -> NO escalation
    weak = assess({"base_impact_class": "medium", "source_backed": False, "many_or_all_users_affected": True})
    chk(not weak.escalate and weak.recommended_impact_class == "medium", "escalator without source -> no escalation (reject-first)")
    # P87 M-18: involuntary race + concrete -> keep, not self-inflicted
    m18 = assess({"base_impact_class": "medium", "source_backed": True, "involuntary": True,
                  "material_consequence": ["stuck_funds"]})
    chk(not m18.escalate and m18.attach_involuntary, "P87 M-18 involuntary+concrete -> keep, mark involuntary")
    # P87 H-03: admin-initiated but user-facing consequence -> NOT a footgun
    h03 = assess({"base_impact_class": "medium", "source_backed": True, "admin_initiated": True,
                  "externally_triggerable_user_harm": True})
    chk(not h03.footgun_flag, "P87 H-03 admin+user-harm -> not a footgun")
    # true admin footgun -> flagged, not promoted
    fg = assess({"base_impact_class": "low", "admin_initiated": True})
    chk(fg.footgun_flag and not fg.escalate, "true admin footgun flagged, not promoted")
    # P86 preservation: bounded/lazy, no escalator, no concrete -> base unchanged (gate demotes)
    bnd = assess({"base_impact_class": "medium", "source_backed": True, "material_consequence": ["misrouted_funds"]})
    chk(not bnd.escalate, "bounded misrouted_funds, no escalator -> no escalation (gate still demotes)")
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", help="impact_assessment JSON")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ia = json.loads(args.json) if args.json else {}
    print(json.dumps(assess(ia)._asdict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
