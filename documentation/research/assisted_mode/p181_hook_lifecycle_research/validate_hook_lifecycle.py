#!/usr/bin/env python3
"""
P181 validation (READ-ONLY) — evaluate the research F3 hook_lifecycle selector on quantamm, with a baseline
(unique vs F1/math_estimator), exact/contract/subsystem specificity, and a cross-corpus leakage check on
zaros + revert-lend. Writes ONLY metrics.json here. No production wiring; no corpus/answer-key mutation.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "research"))

import hook_lifecycle_selector as f3           # noqa: E402
import dynamic_weight_lifecycle_taxonomy as f1  # noqa: E402  (shipped F1)
import math_estimator_taxonomy as me            # noqa: E402  (shipped math-estimator)

# The 7 hook_lifecycle answer-key misses → their quantamm hook function (contract, function).
TARGETS = {
    "H-07": ("UpliftOnlyExample", "onAfterRemoveLiquidity"),
    "M-03": ("UpliftOnlyExample", "afterUpdate"),
    "M-05": ("UpliftOnlyExample", "onAfterRemoveLiquidity"),
    "M-10": ("LPNFT", "_update"),
    "M-11": ("UpliftOnlyExample", "onRegister"),
    "M-15": ("UpliftOnlyExample", "onAfterRemoveLiquidity"),
    "M-18": ("UpliftOnlyExample", "afterUpdate"),
}


def load_manifest(aid):
    items = json.loads((ROOT / f"audits/{aid}/output/coverage_manifest.json").read_text())["items"]
    return [i for i in items if i.get("in_scope")]


def surfaced_set(items):
    """{(contract, function_lower)} re-surfaced by F3, + the list of surfaced (contract, name) for reporting."""
    out, names = set(), []
    for it in items:
        if f3.classify_manifest_item(it).get("hook_lifecycle_sensitive"):
            out.add((it.get("contract"), (it.get("name") or "").lower()))
            names.append(f"{it.get('contract')}.{it.get('name')}")
    return out, names


def quantamm_eval():
    aid = "quantamm-2024-12-eval"
    items = load_manifest(aid)
    by_cf = {}
    for it in items:
        by_cf.setdefault((it.get("contract"), (it.get("name") or "").lower()), it)
    surf, surf_names = surfaced_set(items)

    rows, recovered, unique = [], 0, 0
    for fid, (contract, fn) in TARGETS.items():
        key = (contract, fn.lower())
        it = by_cf.get(key)
        f3_hit = key in surf
        # baseline: would the SHIPPED lenses already surface this exact function?
        f1_hit = bool(it and f1.classify_manifest_item(it).get("lifecycle_sensitive"))
        me_hit = bool(it and me.classify_manifest_item(it).get("math_estimator_sensitive"))
        is_unique = f3_hit and not (f1_hit or me_hit)
        if f3_hit:
            recovered += 1
        if is_unique:
            unique += 1
        rows.append({"finding": fid, "contract": contract, "function": fn,
                     "f1_already": f1_hit, "math_estimator_already": me_hit,
                     "f3_newly_surfaced": f3_hit, "unique_f3_recovery": is_unique,
                     "match_level": "exact_function" if f3_hit else "missed"})

    # FP examples + function-level precision (distinct surfaced functions on a target site / all surfaced)
    target_cf = {(c, f.lower()) for c, f in TARGETS.values()}
    on_target_fns = {cf for cf in surf if cf in target_cf}
    fp = [n for n in surf_names if (n.split(".")[0], n.split(".")[1].lower()) not in target_cf]
    n_surf = len(surf)
    return {
        "corpus": aid, "targets": len(TARGETS),
        "recovered_total": recovered, "recovered_unique_vs_shipped": unique,
        "re_surface_count": n_surf, "surfaced_functions": sorted(surf_names),
        "on_target_functions": sorted(f"{c}.{f}" for c, f in on_target_fns),
        "precision_function_pct": round(100 * len(on_target_fns) / n_surf, 1) if n_surf else 0.0,
        "fp_count": len(set(fp)), "fp_examples": sorted(set(fp)),
        "per_finding": rows,
    }


def leakage(aid):
    items = load_manifest(aid)
    surf, names = surfaced_set(items)
    return {"corpus": aid, "in_scope_items": len(items), "surfaced_count": len(surf),
            "surfaced_pct": round(100 * len(surf) / max(1, len(items)), 1),
            "surfaced_functions": sorted(names)[:25]}


def main():
    q = quantamm_eval()
    leak = {c: leakage(c) for c in ("zaros-2025-01-part-2-eval", "revert-lend-2024-03-strict-eval")}
    leak["quantamm-2024-12-eval"] = leakage("quantamm-2024-12-eval")

    out = {"phase": "P181", "type": "research_hook_lifecycle_selector_eval", "read_only": True,
           "flags": f3._FLAGS, "quantamm": q, "cross_corpus_leakage": leak}
    (HERE / "metrics.json").write_text(json.dumps(out, indent=2))

    print("=== P181 research F3 hook_lifecycle selector — quantamm ===")
    print(f"recovered total: {q['recovered_total']}/7   unique vs shipped F1/math_estimator: "
          f"{q['recovered_unique_vs_shipped']}/7")
    print(f"re-surface count: {q['re_surface_count']}   function precision: {q['precision_function_pct']}%   "
          f"FP funcs: {q['fp_count']}")
    print(f"surfaced: {q['surfaced_functions']}")
    print(f"FP examples: {q['fp_examples']}")
    print("\nper-finding (exact-function) + baseline:")
    print(f"  {'find':5} {'fn':32} {'F1?':4} {'ME?':4} {'F3new?':7} {'unique?':7}")
    for r in q["per_finding"]:
        print(f"  {r['finding']:5} {(r['contract']+'.'+r['function'])[:32]:32} "
              f"{str(r['f1_already']):4} {str(r['math_estimator_already']):4} "
              f"{str(r['f3_newly_surfaced']):7} {str(r['unique_f3_recovery']):7}")
    print("\n=== cross-corpus leakage (architecture transfer) ===")
    for c, l in leak.items():
        print(f"  {c:34} surfaced {l['surfaced_count']}/{l['in_scope_items']} ({l['surfaced_pct']}%)")

    # self-checks
    assert q["recovered_unique_vs_shipped"] <= q["recovered_total"] <= q["targets"]
    assert all(r["f3_newly_surfaced"] for r in q["per_finding"] if r["unique_f3_recovery"])
    print("\n[OK] read-only; wrote metrics.json only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
