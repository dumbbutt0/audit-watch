#!/usr/bin/env python3
"""
surface_recall_score.py — Phase-81b RESEARCH-ONLY lead-recall scorer (un-wired).

Measures whether the surface-recall lens (surface_recall_lens.py) generates leads on the functions where awarded bugs
actually live — the upstream that capped P81a. It scores the four pipeline stages SEPARATELY (the user's P81b rubric)
so a future miss can be attributed to the right layer:

  1. lead_recall        — is the awarded function present as a lead (DIRECT) or a directly-adjacent entrypoint (ADJ)?
  2. mechanism_naming   — does the matched lead's surface_classes intersect the awarded mechanism_class?
  3. investigation_outcome — (STRETCH, optional) did the C-arm classify it correctly? supplied externally; default n/a.
  4. promotion_safety   — (STRETCH, optional) severity-FP count from the C-run; supplied externally; default n/a.

The awarded map is an EVAL-ONLY input; the lens never sees it. is_gate:false research_only:true
routes_in_production:false routed_manifest_ids:[]. Usage: surface_recall_score.py --leads <p> --awarded <p> [--out <p>]
                                                          [--required <fn,fn>] | --self-test
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}


def _leads_index(leads: List[Dict[str, Any]]):
    by_fn = {}
    by_contract = {}
    for l in leads:
        c = l.get("trigger_contract") or l.get("contract")
        f = l.get("trigger_function") or l.get("function")
        by_fn[(c, f)] = l
        by_contract.setdefault(c, []).append(l)
    return by_fn, by_contract


def score(leads: List[Dict[str, Any]], awarded: List[Dict[str, Any]],
          required_functions: List[str] | None = None) -> Dict[str, Any]:
    by_fn, by_contract = _leads_index(leads)
    rows = []
    direct = adj = miss = mech_ok = 0
    for a in awarded:
        c = a["contract"]
        candidates = [a["function"], *a.get("alt_functions", [])]
        matched = next(((c, f) for f in candidates if (c, f) in by_fn), None)
        if matched:
            recall = "DIRECT"
            direct += 1
            lead = by_fn[matched]
        elif c in by_contract:
            recall = "ADJ"
            adj += 1
            lead = by_contract[c][0]  # contract present as a flagged flow, function not directly led
        else:
            recall = "MISS"
            miss += 1
            lead = None
        # mechanism naming (coarse): scored ONLY on DIRECT hits — an ADJ match is a different function, so it
        # cannot honestly claim to have named the awarded function's mechanism.
        mech = "n/a"
        if recall == "DIRECT" and lead is not None:
            lead_classes = set(lead.get("surface_classes", []))
            want = set(a.get("mechanism_class", []))
            mech = "MATCH" if (lead_classes & want) else "MISS"
            if mech == "MATCH":
                mech_ok += 1
        rows.append({"id": a["id"], "severity": a["severity"], "contract": c,
                     "awarded_function": a["function"], "recall": recall,
                     "matched_function": (matched[1] if matched else None),
                     "mechanism_naming": mech,
                     "lead_surface_classes": (lead.get("surface_classes") if lead else None),
                     "awarded_mechanism_class": a.get("mechanism_class")})
    total = len(awarded)
    covered = direct + adj
    # required-function gate (the user's named must-haves)
    req = required_functions or []
    req_status = {}
    for rf in req:
        # rf may be "Contract.fn" or just "fn"
        if "." in rf:
            cc, ff = rf.split(".", 1)
            req_status[rf] = any((l.get("trigger_contract") == cc and l.get("trigger_function") == ff) for l in leads)
        else:
            req_status[rf] = any(l.get("trigger_function") == rf for l in leads)
    return {
        **FLAGS, "phase": "P81b", "review_only": True,
        "totals": {"awarded": total, "direct": direct, "adjacent": adj, "miss": miss,
                   "covered": covered, "lead_recall_pct": round(100 * covered / total, 1) if total else 0.0,
                   "direct_pct": round(100 * direct / total, 1) if total else 0.0,
                   "mechanism_naming_match": mech_ok},
        "required_functions": req_status,
        "rows": rows,
        "stretch": {"investigation_outcome": "n/a (supply via C-run)", "promotion_safety_severity_fp": "n/a (supply via C-run)"},
    }


def _self_test() -> int:
    leads = [
        {"trigger_contract": "A", "trigger_function": "setRouter", "surface_classes": ["admin_config_setter", "auth_boundary"]},
        {"trigger_contract": "B", "trigger_function": "execute", "surface_classes": ["external_executor", "refund_path"]},
        {"trigger_contract": "C", "trigger_function": "other", "surface_classes": ["value_exit"]},
    ]
    awarded = [
        {"id": "X-1", "severity": "High", "contract": "A", "function": "setRouter", "mechanism_class": ["admin_config_setter"]},
        {"id": "X-2", "severity": "High", "contract": "B", "function": "execute", "mechanism_class": ["refund_path"]},
        {"id": "X-3", "severity": "Medium", "contract": "C", "function": "missingFn", "alt_functions": [], "mechanism_class": ["value_exit"]},
        {"id": "X-4", "severity": "Medium", "contract": "Z", "function": "gone", "mechanism_class": ["fee_path"]},
    ]
    r = score(leads, awarded, required_functions=["A.setRouter", "B.execute"])
    ok = True
    def chk(c, m):
        nonlocal ok; ok &= c; print(f"  [{'PASS' if c else 'FAIL'}] {m}")
    t = r["totals"]
    chk(t["direct"] == 2, f"direct==2 (got {t['direct']})")
    chk(t["adjacent"] == 1, f"adjacent==1 for C.other vs C.missingFn (got {t['adjacent']})")
    chk(t["miss"] == 1, f"miss==1 for Z (got {t['miss']})")
    chk(t["mechanism_naming_match"] == 2, f"mech match==2 (got {t['mechanism_naming_match']})")
    chk(all(r["required_functions"].values()), "required functions present")
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leads")
    ap.add_argument("--awarded")
    ap.add_argument("--out")
    ap.add_argument("--required", default="")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not (args.leads and args.awarded):
        ap.error("--leads and --awarded required (or --self-test)")
    leads = json.loads(Path(args.leads).read_text())["leads"]
    awarded = json.loads(Path(args.awarded).read_text())["awarded"]
    req = [x for x in args.required.split(",") if x]
    r = score(leads, awarded, required_functions=req)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(r, indent=2))
    print(json.dumps({"totals": r["totals"], "required_functions": r["required_functions"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
