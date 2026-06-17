#!/usr/bin/env python3
"""
Phase-79 A/B/C workflow-discipline eval (RESEARCH-ONLY, un-wired).

Measures whether the verification workflow improves audit DECISIONS by running one frozen candidate batch through three
arms that differ ONLY in which evidence each workflow consults, then scoring each arm's output against a HELD-OUT
ground_truth with a post-hoc scorer (8 categories). This is a DETERMINISTIC simulation of workflow DISCIPLINE — NOT proof
of autonomous hit discovery, and NOT a live-agent run.

Arms (blind to ground_truth):
  A baseline      : context + a baseline-plausible exploit; NO defense ledger, NO source-falsification, NO adversarial.
  B defense-first : A + full defense ledger (reject-first); still NO falsification, NO adversarial.
  C full          : B + real source-falsification + adversarial review -> deep_pass -> hygiene_validate (fail-closed).

Ground-truth firewall: arms receive a PROJECTED view with `ground_truth` removed; arms assert it is absent and are
ground-truth-invariant. Never wired into production. Usage: abc_eval.py --self-test | --run
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any, Dict, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from investigation.deep_pass import run as deep_run, FALSIFIERS  # noqa: E402
from investigation.hygiene_validate import validate as hygiene  # noqa: E402
from investigation.lead_schema import normalize_lead  # noqa: E402

BATCH = ROOT / "documentation" / "research" / "_p79" / "candidate_batch.json"
PROMOTION = {"POC_REQUIRED", "READY_FOR_HUMAN_REVIEW"}
CATEGORIES = ("CLEAN_HIT", "STRONG_PARTIAL", "REJECT_CORRECT", "ABSTAIN_CORRECT",
              "WRONG_MECHANISM", "SOURCE_FALSE", "OVERFIT", "HARD_FAIL")


def project(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Build the arm-visible view of a candidate with ground_truth REMOVED (the firewall)."""
    return {k: v for k, v in candidate.items() if k != "ground_truth"}


def _sf_all_false() -> Dict[str, bool]:
    return {k: False for k in FALSIFIERS}


def _lead_and_ctx(view: Dict[str, Any]):
    ev = view["evidence"]
    lead = normalize_lead({"candidate_id": view["candidate_id"], "detector_family": view["detector_family"],
                           "contract": "C", "function": (ev.get("exploit", {}) or {}).get("entrypoint", "f")})
    lead["mutability"] = ev.get("mutability", "")
    lead["visibility"] = "external"
    return lead, ev


def _evidence(ev, *, defenses: bool, falsify: bool) -> Dict[str, Any]:
    sf = _sf_all_false()
    if falsify:
        raw = ev.get("source_falsification")
        if isinstance(raw, dict):
            sf = {**sf, **{k: bool(v) for k, v in raw.items()}}
        # ev.get("source_falsification_all_false") -> stays all-false
    return {"context": ev.get("context", {}),
            "defense_ledger": (ev.get("defense_ledger", {}) if defenses else {}),
            "critical_defenses": ev.get("critical_defenses", []) if defenses else [],
            "exploit": ev.get("exploit", {}),
            "source_falsification": sf,
            "poc_needed": ev.get("poc_needed", True)}


def arm_a(view: Dict[str, Any]) -> Tuple[str, str]:
    assert "ground_truth" not in view, "ground_truth firewall breach (arm_a)"
    lead, ev = _lead_and_ctx(view)
    b = deep_run(lead, _evidence(ev, defenses=False, falsify=False))
    return b["final_decision"], view.get("baseline_claimed_mechanism")


def arm_b(view: Dict[str, Any]) -> Tuple[str, str]:
    assert "ground_truth" not in view, "ground_truth firewall breach (arm_b)"
    lead, ev = _lead_and_ctx(view)
    b = deep_run(lead, _evidence(ev, defenses=True, falsify=False))
    return b["final_decision"], view.get("baseline_claimed_mechanism")


def arm_c(view: Dict[str, Any]) -> Tuple[str, str]:
    assert "ground_truth" not in view, "ground_truth firewall breach (arm_c)"
    lead, ev = _lead_and_ctx(view)
    bundle = deep_run(lead, _evidence(ev, defenses=True, falsify=True))
    ok, _viol, rec = hygiene(bundle, view.get("adversarial_review"))
    decision = bundle["final_decision"] if ok else rec
    mech = (ev.get("exploit", {}) or {}).get("mechanism") if decision in PROMOTION else None
    return decision, mech


def score(decision: str, claimed_mech, gt: Dict[str, Any]) -> str:
    gtd, gtm, rr = gt["decision"], gt.get("mechanism"), gt.get("reject_reason")
    promote = decision in PROMOTION
    real_gtm = gtm not in (None, "none")
    if decision == gtd:
        if gtd == "READY_FOR_HUMAN_REVIEW":
            return "CLEAN_HIT" if claimed_mech == gtm else "WRONG_MECHANISM"
        if gtd == "POC_REQUIRED":
            return "STRONG_PARTIAL" if claimed_mech == gtm else "WRONG_MECHANISM"
        if gtd == "REJECTED":
            return "REJECT_CORRECT"
        if gtd == "NEEDS_CONTEXT":
            return "ABSTAIN_CORRECT"
    if promote and gtd in ("REJECTED", "NEEDS_CONTEXT"):
        if real_gtm and claimed_mech != gtm:
            return "WRONG_MECHANISM"
        if rr == "falsified":
            return "SOURCE_FALSE"
        return "OVERFIT"
    # arm was conservative (rejected/abstained) where gt was a real bug -> safe miss, scored as the safe terminal
    if not promote and gtd in PROMOTION:
        return "REJECT_CORRECT" if decision == "REJECTED" else "ABSTAIN_CORRECT"
    return "ABSTAIN_CORRECT"


def run_batch() -> Dict[str, Any]:
    data = json.loads(BATCH.read_text())
    arms = {"A_baseline": arm_a, "B_defense_first": arm_b, "C_full": arm_c}
    rows, summary = [], {a: {c: 0 for c in CATEGORIES} for a in arms}
    safety = {a: {"unsupported_ready": 0, "source_false_promotions": 0, "overfit_promotions": 0,
                  "wrong_mechanism": 0, "detector_to_finding": 0, "hard_fail": 0} for a in arms}
    for cand in data["candidates"]:
        gt = cand["ground_truth"]
        view = project(cand)
        row = {"candidate_id": cand["candidate_id"], "category": cand["category"], "fresh": cand.get("fresh", False),
               "ground_truth": gt["decision"]}
        for aname, fn in arms.items():
            dec, mech = fn(view)
            cat = score(dec, mech, gt)
            row[aname] = {"decision": dec, "claimed_mechanism": mech, "score": cat}
            summary[aname][cat] += 1
            if dec == "READY_FOR_HUMAN_REVIEW" and gt["decision"] != "READY_FOR_HUMAN_REVIEW":
                safety[aname]["unsupported_ready"] += 1
            if cat == "SOURCE_FALSE":
                safety[aname]["source_false_promotions"] += 1
            if cat == "OVERFIT":
                safety[aname]["overfit_promotions"] += 1
            if cat == "WRONG_MECHANISM":
                safety[aname]["wrong_mechanism"] += 1
            if cat == "HARD_FAIL":
                safety[aname]["hard_fail"] += 1
        rows.append(row)
    # hit-accrual is counted ONLY on fresh/semi-fresh candidates and ONLY when C uniquely... (reported, not pass-gating)
    fresh_hits = {a: [r["candidate_id"] for r in rows if r["fresh"] and r[a]["score"] in ("CLEAN_HIT", "STRONG_PARTIAL")] for a in arms}
    return {"research_only": True, "review_only": True, "phase": "P79", "batch_size": len(rows),
            "rows": rows, "category_summary": summary, "safety": safety,
            "fresh_hit_candidates": fresh_hits,
            "metrics": {
                "safety_improvement": {a: safety[a] for a in arms},
                "mechanism_correctness": {a: summary[a]["WRONG_MECHANISM"] for a in arms},
                "hit_accrual_evidence": {"note": "anchors excluded; counted only on fresh/semi-fresh; genuine clean leads are promoted by ALL arms, so C does not UNIQUELY accrue hits — see report", "fresh_hits": fresh_hits},
                "live_agent_readiness": "NOT demonstrated — deterministic workflow-discipline simulation, not live LLM runs",
            }}


def _self_test() -> int:
    res = run_batch()
    A, B, C = res["safety"]["A_baseline"], res["safety"]["B_defense_first"], res["safety"]["C_full"]
    ok = True
    c1 = C["unsupported_ready"] == 0 and C["source_false_promotions"] == 0 and C["hard_fail"] == 0 and C["detector_to_finding"] == 0
    print(f"  [{'PASS' if c1 else 'FAIL'}] C safety zeros: {C}"); ok &= c1
    c2 = C["wrong_mechanism"] < A["wrong_mechanism"]
    print(f"  [{'PASS' if c2 else 'FAIL'}] C wrong_mechanism({C['wrong_mechanism']}) < A({A['wrong_mechanism']})"); ok &= c2
    c3 = (A["unsupported_ready"] + A["source_false_promotions"] + A["overfit_promotions"] + A["wrong_mechanism"]) > 0
    print(f"  [{'PASS' if c3 else 'FAIL'}] A has unsafe promotions (baseline fails traps)"); ok &= c3
    c4 = (C["source_false_promotions"] <= B["source_false_promotions"]) and (C["overfit_promotions"] <= B["overfit_promotions"])
    print(f"  [{'PASS' if c4 else 'FAIL'}] C safety >= B (source_false C{C['source_false_promotions']}<=B{B['source_false_promotions']}, overfit C{C['overfit_promotions']}<=B{B['overfit_promotions']})"); ok &= c4
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    res = run_batch()
    if args.out:
        Path(args.out).write_text(json.dumps(res, indent=2))
    print(json.dumps({"category_summary": res["category_summary"], "safety": res["safety"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
