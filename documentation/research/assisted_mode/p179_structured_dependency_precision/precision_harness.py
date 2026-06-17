#!/usr/bin/env python3
"""
P179 — precision of the P178 structured guarded-downstream blocks on zaros (READ-ONLY).

Re-derives the 83 zaros clears that P178 auto-resolved into structured dependency metadata AND route to block
under the P177 rule, then classifies each block (by the cleared ITEM it re-surfaces) against the zaros answer
key: awarded_exact / awarded_adjacent / awarded_subsystem / non_awarded_resurface / unmappable. Also classifies
the P176 legacy "blunt" guarded routes (the 237 prose-detected dependency clears) the same way, for a
before/after precision comparison. Writes precision_by_block.json + metrics.json next to this file. No mutation.

Run: python documentation/research/assisted_mode/p179_structured_dependency_precision/precision_harness.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import dependency_clear_utils as dcu          # noqa: E402
import dependency_metadata as dmeta           # noqa: E402

AID = "zaros-2025-01-part-2-eval"
MM = f"audits/{AID}/output/eval_ready/eval_match_matrix.json"
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")
_CONTRACT_FN = re.compile(r"([A-Z][A-Za-z0-9]+)::([A-Za-z_][A-Za-z0-9_]*)")


def load(p):
    return json.loads((ROOT / p).read_text())


def _subsystem(item):
    f = item.get("file") or ""
    return Path(f).parent.name or (item.get("contract") or "?")


def build_awarded_index(mi, ni):
    """From the zaros answer key: awarded function names, contracts, and subsystems (resolved via manifest)."""
    rows = load(MM)["rows"]
    fn_to_contracts, contracts, subsystems = {}, set(), set()
    awarded_fn = set()
    for r in rows:
        text = f"{r.get('ak_title','')}  {r.get('note','')}"
        # contract::fn
        for m in _CONTRACT_FN.finditer(text):
            contracts.add(m.group(1))
        # any identifier that resolves to a manifest function
        for tok in _IDENT.findall(text):
            ids = ni.get(tok.lower())
            if ids:
                awarded_fn.add(tok.lower())
                for i in ids:
                    c = mi.get(i, {}).get("contract")
                    if c:
                        fn_to_contracts.setdefault(tok.lower(), set()).add(c)
                        contracts.add(c)
                    subsystems.add(_subsystem(mi.get(i, {})))
    return awarded_fn, fn_to_contracts, contracts, subsystems


def classify_block(item, awarded_fn, fn_to_contracts, awarded_contracts, awarded_subsystems):
    c = item.get("contract")
    fn = (item.get("name") or "").lower()
    if not c or not fn:
        return "unmappable"
    if fn in awarded_fn and c in fn_to_contracts.get(fn, set()):
        return "awarded_exact"
    if c in awarded_contracts:
        return "awarded_adjacent"
    if _subsystem(item) in awarded_subsystems:
        return "awarded_subsystem"
    return "non_awarded_resurface"


def derive_blocks(disp, mi, ni, di, *, structured: bool):
    """structured=True → P178 resolved-structured blocks; False → P176 legacy blunt guarded routes (all
    prose-detected dependency clears that route to block under legacy require_structured=False)."""
    out = []
    for d in disp:
        if d.get("status") != "cleared" or not dcu.is_dependency_based_clear(d):
            continue
        if structured:
            meta = dmeta.extract_dependency_metadata(dict(d), mi, ni, di)
            if not meta.get("dependency_name"):
                continue
            enr = dict(d); enr.update({k: v for k, v in meta.items() if v is not None})
            cls = dcu.classify_clear(enr, di, ni, manifest_index=mi)
            if dcu.dependency_route_decision(cls, enr, locality_on=True, require_structured=True) != "block":
                continue
            out.append((d["manifest_id"], meta, cls["status"]))
        else:
            cls = dcu.classify_clear(d, di, ni, manifest_index=mi)
            if dcu.dependency_route_decision(cls, d, locality_on=True, require_structured=False) != "block":
                continue
            out.append((d["manifest_id"], {}, cls["status"]))
    return out


def measure(disp, mi, ni, di, awarded, *, structured):
    awarded_fn, fn_to_contracts, awarded_contracts, awarded_subsystems = awarded
    blocks = derive_blocks(disp, mi, ni, di, structured=structured)
    buckets, rows = Counter(), []
    for mid, meta, status in blocks:
        it = mi.get(mid, {})
        b = classify_block(it, awarded_fn, fn_to_contracts, awarded_contracts, awarded_subsystems)
        buckets[b] += 1
        rows.append({"manifest_id": mid, "contract": it.get("contract"), "function": it.get("name"),
                     "subsystem": _subsystem(it), "bucket": b, "block_status": status,
                     "dependency_name": meta.get("dependency_name"),
                     "dependency_scope": meta.get("dependency_scope"),
                     "dependency_status": meta.get("dependency_status"),
                     "proof_status": meta.get("proof_status")})
    n = len(blocks)
    pct = lambda k: round(100 * k / n, 1) if n else 0.0  # noqa: E731
    ex = buckets.get("awarded_exact", 0)
    adj = ex + buckets.get("awarded_adjacent", 0)
    sub = adj + buckets.get("awarded_subsystem", 0)
    return {
        "n_blocks": n, "buckets": dict(buckets),
        "exact_precision_pct": pct(ex), "adjacent_cum_precision_pct": pct(adj),
        "subsystem_cum_precision_pct": pct(sub),
        "non_awarded_resurface": buckets.get("non_awarded_resurface", 0) + buckets.get("unmappable", 0),
        "rows": rows,
    }


def main():
    disp = load(f"audits/{AID}/output/coverage_dispositions.json")["dispositions"]
    man = load(f"audits/{AID}/output/coverage_manifest.json")["items"]
    mi = {i["id"]: i for i in man}; ni = dcu.build_manifest_name_index(man)
    di = {d["manifest_id"]: d for d in disp}
    awarded = build_awarded_index(mi, ni)

    p178 = measure(disp, mi, ni, di, awarded, structured=True)
    p176 = measure(disp, mi, ni, di, awarded, structured=False)

    metrics = {
        "phase": "P179", "corpus": AID, "read_only": True,
        "awarded_index": {"awarded_functions_resolved": len(awarded[0]),
                          "awarded_contracts": len(awarded[2]), "awarded_subsystems": len(awarded[3])},
        "p178_structured_blocks": {k: v for k, v in p178.items() if k != "rows"},
        "p176_blunt_guarded_routes": {k: v for k, v in p176.items() if k != "rows"},
        "precision_improvement_exact_pct_points": round(
            p178["exact_precision_pct"] - p176["exact_precision_pct"], 1),
        "precision_improvement_subsystem_pct_points": round(
            p178["subsystem_cum_precision_pct"] - p176["subsystem_cum_precision_pct"], 1),
    }
    (HERE / "precision_by_block.json").write_text(json.dumps({"p178_blocks": p178["rows"]}, indent=2))
    (HERE / "metrics.json").write_text(json.dumps(metrics, indent=2))

    print("=== P179 precision of P178 structured guarded-downstream blocks (zaros) ===")
    print(f"awarded index: {metrics['awarded_index']}")
    for label, m in (("P178 structured blocks", p178), ("P176 blunt guarded routes", p176)):
        print(f"\n{label}: n={m['n_blocks']}  buckets={m['buckets']}")
        print(f"  exact={m['exact_precision_pct']}%  adjacent(cum)={m['adjacent_cum_precision_pct']}%  "
              f"subsystem(cum)={m['subsystem_cum_precision_pct']}%  non_awarded={m['non_awarded_resurface']}")
    print(f"\nexact precision Δ (P178 - P176): {metrics['precision_improvement_exact_pct_points']} pts")
    print(f"subsystem precision Δ: {metrics['precision_improvement_subsystem_pct_points']} pts")
    # dependency_name concentration (precision red flag if one generic token dominates)
    names = Counter(r["dependency_name"] for r in p178["rows"])
    print(f"\nP178 dependency_name concentration: {dict(names)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
