#!/usr/bin/env python3
"""
severity_impact_gate.py — Phase-81c RESEARCH-ONLY promotion severity/impact gate (un-wired).

Closes the P81a D2 gap. D2 (`swapNoPath`) was SOURCE-TRUE (the function genuinely lacked the access modifier) yet its
real impact was transient/dust — Low/QA, not an awarded H/M — but the workflow still promoted it to POC_REQUIRED.
Source-true is NOT the same as H/M-worthy. This gate is the missing layer: among PROMOTION-status decisions it DEMOTES
those whose proven impact is dust / low / qa / informational below POC_REQUIRED, and FAIL-CLOSES when impact is
unproven (prefer NEEDS_CONTEXT over a thin promotion). It KEEPS material critical/high/medium fund-loss /
broken-invariant / significant-griefing promotions.

It is an advisory post-layer (same shape as hygiene_validate.validate) the orchestrator applies AFTER deep_pass +
hygiene. It NEVER edits deep_pass/hygiene/transitions, NEVER sets production severity, and routes nothing.

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
Usage: severity_impact_gate.py --decision <status> --impact-class <c> [--magnitude <m>] | --self-test
"""
from __future__ import annotations
import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, NamedTuple, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
CFG = ROOT / "config" / "severity_impact_gate.json"
FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


class GateResult(NamedTuple):
    kept: bool
    recommended_status: str
    reason: str
    impact_class: str


def gate(decision: str, impact_assessment: Optional[Dict[str, Any]] = None) -> GateResult:
    """Apply the severity/impact gate to one decision.

    impact_assessment = {impact_class, proven_magnitude, rationale, source_true}. Missing -> treated as UNPROVEN.
    """
    cfg = _cfg()
    ia = impact_assessment or {}
    ic = str(ia.get("impact_class", "") or "").lower()
    mag = str(ia.get("proven_magnitude", "") or "").lower()
    demote_to = cfg["demote_to"]
    src_true = bool(ia.get("source_true", True))
    raw_mc = ia.get("material_consequence", [])
    if isinstance(raw_mc, bool):
        mc_tags = ["material_consequence"] if raw_mc else []
    else:
        mc_tags = [str(t).lower() for t in (raw_mc or [])]
    markers = [str(m).lower() for m in (ia.get("bounded_markers", []) or [])]
    involuntary_in = [str(m).lower() for m in (ia.get("involuntary", []) or ia.get("involuntary_markers", []) or [])]
    liveness_in = [str(m).lower() for m in (ia.get("liveness_markers", []) or [])]

    # P86 tiering: only CONCRETE consequences justify a keep; bounded/non-material ones do not.
    concrete_set = set(cfg.get("concrete_material_consequences", []))
    bounded_tags = set(cfg.get("bounded_nonmaterial_consequences", []))
    bounded_markers_cfg = set(cfg.get("bounded_lazy_markers", []))
    concrete = src_true and any(t in concrete_set for t in mc_tags)
    # bounded/lazy-settlement accounting candidate: an explicit bounded marker, OR consequence tags that are
    # present but ALL bounded/non-material (e.g. only `misrouted_funds`/`stale_parameter`).
    bounded = (any(m in bounded_markers_cfg for m in markers)
               or (bool(mc_tags) and not concrete and any(t in bounded_tags for t in mc_tags)))
    # P88 elevation signals.
    liveness_set = set(cfg.get("liveness_consequences", []))
    involuntary_cfg = set(cfg.get("involuntary_markers", []))
    high_liveness_cfg = set(cfg.get("high_liveness_markers", []))
    liveness = src_true and any(t in liveness_set for t in mc_tags)
    involuntary = any(m in involuntary_cfg for m in involuntary_in)
    high_liveness = any(m in high_liveness_cfg for m in liveness_in)

    if decision not in cfg["promotion_statuses"]:
        return GateResult(True, decision, "non-promotion decision passes through unchanged", ic or "n/a")

    # (2) non-material impact CLASS floor -> demote regardless (preserves D2 even if a material tag is mis-attached)
    NONMATERIAL = {"dust", "qa", "informational", "gas", "none", "negligible"}
    if ic in NONMATERIAL:
        return GateResult(False, demote_to, f"non-material impact class ({ic})", ic)
    # (3) dust/transient MAGNITUDE with NO concrete consequence -> demote (preserves the P81a D2 fix)
    if mag in cfg["demote_proven_magnitudes"] and not concrete:
        return GateResult(False, demote_to,
                          f"impact below H/M review threshold (proven_magnitude={mag or '?'}, no concrete consequence)",
                          ic or "dust")
    # (4) P88 ELEVATION: a source-backed LIVENESS consequence, or an INVOLUNTARY harm with a concrete consequence,
    #     is KEPT and never demoted by the bounded rule. Reported `high` when high_liveness_markers prove a
    #     core/all-users/unrecoverable brick, else `medium`. (Runs AFTER the class/dust floors so D2 still demotes.)
    if liveness or (involuntary and concrete):
        why = "source-backed liveness/function-brick" if liveness else "involuntary harm with concrete consequence"
        return GateResult(True, decision,
                          f"{why} — not under-rated (P88 calibration; impact >= Medium)",
                          "high" if (high_liveness and liveness) else "medium")
    # (5) P86: bounded/lazy-settlement accounting with NO source-backed concrete consequence -> demote.
    #     Fires regardless of declared impact_class, so a declared High/Medium cannot save weak (bounded) evidence.
    if bounded and not concrete:
        return GateResult(False, demote_to,
                          "bounded/lazy-settlement accounting issue with no source-backed concrete material "
                          "consequence (P86 calibration)", ic or "low")
    # (6) 'low' label: KEEP only if a source-backed CONCRETE consequence is asserted, else demote
    if ic == "low":
        if concrete:
            return GateResult(True, decision,
                              f"low-labelled but source-backed concrete material consequence "
                              f"({', '.join(t for t in mc_tags if t in concrete_set)}) — not auto-demoted", "medium")
        return GateResult(False, demote_to, "low impact with no source-backed concrete material consequence", ic)
    # (7) material classes (reached only after the bounded check) -> keep
    if ic in cfg["material_impact_classes"]:
        return GateResult(True, decision, f"material impact ({ic}) — promotion preserved", ic)
    # (8) impact unproven / unknown -> fail-closed
    return GateResult(False, demote_to,
                      "impact unproven; cannot confirm H/M materiality (supply impact_class/proven_magnitude)",
                      ic or "unproven")


def gate_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience wrapper: read bundle.final_decision + bundle.impact_assessment, return a result dict."""
    res = gate(bundle.get("final_decision", ""), bundle.get("impact_assessment"))
    return {**FLAGS, "candidate_id": bundle.get("candidate_id"), "input_decision": bundle.get("final_decision"),
            "kept": res.kept, "recommended_status": res.recommended_status,
            "reason": res.reason, "impact_class": res.impact_class}


def _self_test() -> int:
    ok = True
    def chk(c, m):
        nonlocal ok; ok &= c; print(f"  [{'PASS' if c else 'FAIL'}] {m}")
    # P81a D2: source-true but dust -> demote
    d2 = gate("POC_REQUIRED", {"impact_class": "dust", "proven_magnitude": "transient", "source_true": True})
    chk(not d2.kept and d2.recommended_status == "NEEDS_CONTEXT", f"D2 dust promotion demoted -> {d2.recommended_status}")
    # material high -> keep
    hi = gate("POC_REQUIRED", {"impact_class": "high", "proven_magnitude": "material", "source_true": True})
    chk(hi.kept and hi.recommended_status == "POC_REQUIRED", "material high promotion kept")
    # medium griefing -> keep
    md = gate("POC_REQUIRED", {"impact_class": "medium", "proven_magnitude": "significant"})
    chk(md.kept, "medium promotion kept")
    # low impact -> demote
    lo = gate("READY_FOR_HUMAN_REVIEW", {"impact_class": "low"})
    chk(not lo.kept and lo.recommended_status == "NEEDS_CONTEXT", "low READY demoted")
    # unproven impact -> fail-closed demote
    un = gate("POC_REQUIRED", {})
    chk(not un.kept and un.recommended_status == "NEEDS_CONTEXT", "unproven impact fail-closed")
    # P81f calibration: low-labelled but source-backed material consequence -> KEPT (not auto-demoted)
    m4 = gate("POC_REQUIRED", {"impact_class": "low", "source_true": True, "material_consequence": ["denial_of_asset_movement", "failed_settlement"]})
    chk(m4.kept and m4.recommended_status == "POC_REQUIRED", "low+material-consequence kept (P81f M-04/M-01 calibration)")
    # low with only conservative wording, no material tag -> still demote
    lw = gate("POC_REQUIRED", {"impact_class": "low", "material_consequence": []})
    chk(not lw.kept, "low with no material consequence still demoted")
    # material consequence but not source_true -> demote (source_true gates it)
    ns = gate("POC_REQUIRED", {"impact_class": "low", "source_true": False, "material_consequence": ["fund_loss"]})
    chk(not ns.kept, "material consequence not source-true -> demoted")
    # dust with a (spurious) material tag still demotes via magnitude rule unless material -> dust magnitude + tag: tag lifts? guard: dust class is non-material regardless
    du = gate("POC_REQUIRED", {"impact_class": "dust", "proven_magnitude": "transient", "material_consequence": ["fund_loss"]})
    chk(not du.kept, "dust class demotes even if a material tag is mis-attached (D2 preserved)")
    # P86: bounded/lazy-settlement accounting (updateTaxRate-style) -> demote even when labelled Medium + material
    utr = gate("POC_REQUIRED", {"impact_class": "medium", "proven_magnitude": "material", "source_true": True,
                                "material_consequence": ["misrouted_funds"]})
    chk(not utr.kept and utr.recommended_status == "NEEDS_CONTEXT", "P85 updateTaxRate (medium+misrouted_funds) demoted")
    # P86: a declared HIGH whose only consequence is bounded/non-material -> demote (declared-High can't save weak evidence)
    hb = gate("POC_REQUIRED", {"impact_class": "high", "material_consequence": ["stale_parameter"]})
    chk(not hb.kept, "declared high with only a bounded consequence (stale_parameter) demoted")
    # P86: explicit bounded marker with no concrete consequence -> demote
    bm = gate("POC_REQUIRED", {"impact_class": "medium", "bounded_markers": ["bounded_rate_mismatch"], "material_consequence": []})
    chk(not bm.kept, "bounded marker + no concrete consequence demoted")
    # P86: bounded + concrete both present -> concrete wins, KEEP
    bc = gate("POC_REQUIRED", {"impact_class": "medium", "material_consequence": ["misrouted_funds", "stuck_funds"]})
    chk(bc.kept, "bounded tag + concrete tag -> concrete wins, kept")
    # P86: H-05 reward-loss class -> kept
    h05 = gate("POC_REQUIRED", {"impact_class": "high", "source_true": True, "material_consequence": ["reward_loss_not_recoverable"]})
    chk(h05.kept and h05.recommended_status == "POC_REQUIRED", "H-05 reward_loss_not_recoverable kept")
    # P88 A: liveness / permanent function brick -> kept; high_liveness markers -> impact reported high
    h01 = gate("POC_REQUIRED", {"impact_class": "medium", "source_true": True, "material_consequence": ["permanent_function_brick", "blocked_mint_path"],
                                "liveness_markers": ["bricks_major_phase_or_generation", "many_or_all_users_affected"]})
    chk(h01.kept and h01.impact_class == "high", "P87 H-01 liveness brick kept + elevated to high rationale")
    # P88 A': liveness even if under-labelled 'low' -> kept, not under-rated below medium
    liv_low = gate("POC_REQUIRED", {"impact_class": "low", "source_true": True, "material_consequence": ["denial_of_asset_movement"]})
    chk(liv_low.kept and liv_low.impact_class in ("medium", "high"), "liveness under-labelled low -> kept >= medium")
    # P88 B: involuntary race + concrete stuck funds -> kept (even with a bounded marker attached)
    m18 = gate("POC_REQUIRED", {"impact_class": "medium", "source_true": True, "material_consequence": ["stuck_funds"],
                                "involuntary": ["race_condition"], "bounded_markers": ["no_blocked_claim_withdraw_settlement_path"]})
    chk(m18.kept, "P87 M-18 involuntary race + concrete stuck_funds kept (not self-inflicted-demoted)")
    # P88 B': voluntary / self-inflicted with no concrete loss -> still demote
    selfinf = gate("POC_REQUIRED", {"impact_class": "low", "source_true": True, "material_consequence": [],
                                    "bounded_markers": ["no_quantified_user_loss", "avoidable_by_normal_action_no_race"]})
    chk(not selfinf.kept, "voluntary/self-inflicted no-loss still demoted")
    # P88 C: involuntary marker WITHOUT concrete consequence does NOT save a bounded issue (no free pass)
    inv_only = gate("POC_REQUIRED", {"impact_class": "high", "source_true": True, "material_consequence": ["misrouted_funds"],
                                     "involuntary": ["race_condition"]})
    chk(not inv_only.kept, "involuntary marker + only bounded misrouted_funds (no concrete) still demotes")
    # non-promotion decision -> unchanged
    nc = gate("NEEDS_CONTEXT", {"impact_class": "dust"})
    chk(nc.kept and nc.recommended_status == "NEEDS_CONTEXT", "non-promotion passes through")
    rj = gate("REJECTED", {"impact_class": "high"})
    chk(rj.kept and rj.recommended_status == "REJECTED", "REJECTED passes through (gate never re-promotes)")
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decision")
    ap.add_argument("--impact-class", default="")
    ap.add_argument("--magnitude", default="")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.decision:
        ap.error("--decision required (or --self-test)")
    res = gate(args.decision, {"impact_class": args.impact_class, "proven_magnitude": args.magnitude})
    print(json.dumps(res._asdict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
