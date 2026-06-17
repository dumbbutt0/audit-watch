#!/usr/bin/env python3
"""P130 measurement (read-only): candidate-coverage proxy for a manifest.

Usage: measure.py <manifest.json> <recall_score.json|-> <label>
Reports: awarded-FUNCTION deep-pass coverage (in_scope & score>=3), internal/private fn scoring,
and total high-surface volume (regression guard). The awarded list is an EVAL yardstick only.
"""
import json, sys, statistics as st
CUT = 3

def load_awarded(p):
    if p == "-": return []
    d = json.load(open(p))
    rows = d.get("rows", d.get("awarded", []))
    out = []
    for r in rows:
        fn = r.get("awarded_function") or r.get("matched_function")
        out.append((r.get("contract"), fn, r.get("severity")))
    return out

def main():
    manifest, awarded_p, label = sys.argv[1], sys.argv[2], sys.argv[3]
    items = json.load(open(manifest))["items"]
    fns = [x for x in items if x.get("kind") == "function"]
    # index by (contract, name)
    by = {}
    for x in fns: by.setdefault((x.get("contract"), x.get("name")), []).append(x)
    bycontract = {}
    for x in fns: bycontract.setdefault(x.get("contract"), []).append(x)
    awarded = load_awarded(awarded_p)

    def hot(x): return x.get("in_scope") and x.get("attack_surface_score", 0) >= CUT
    fcov = ccov = ftot = ctot = 0
    miss_fns = []
    for c, fn, sev in awarded:
        cits = bycontract.get(c, [])
        ctot += 1
        if any(hot(x) for x in cits): ccov += 1
        if fn:
            ftot += 1
            cand = by.get((c, fn), [])
            if any(hot(x) for x in cand): fcov += 1
            elif cand: miss_fns.append(f"{c}.{fn}(present,score<3/oos)")
            else: miss_fns.append(f"{c}.{fn}(absent)")

    internal = [x for x in fns if x.get("visibility") in ("internal", "private")]
    isc = [x.get("attack_surface_score", 0) for x in internal]
    ige3 = sum(1 for s in isc if s >= CUT)
    vol = sum(1 for x in fns if hot(x))
    print(f"=== {label} ===")
    if ctot: print(f"  awarded-CONTRACT deep-pass coverage: {ccov}/{ctot} = {100*ccov/ctot:.0f}%")
    if ftot: print(f"  awarded-FUNCTION deep-pass coverage: {fcov}/{ftot} = {100*fcov/ftot:.0f}%")
    print(f"  internal/private fns: {len(internal)}  ge3={ige3} ({100*ige3/max(1,len(internal)):.0f}%)  mean={st.mean(isc) if isc else 0:.2f}")
    print(f"  VOLUME high-surface in_scope fns: {vol}  (total fns {len(fns)})")
    if miss_fns: print(f"  awarded fns NOT deep-pass-covered: {miss_fns}")
    return {"awarded_contract_cov": [ccov, ctot], "awarded_fn_cov": [fcov, ftot],
            "internal": len(internal), "internal_ge3": ige3, "volume": vol, "total_fns": len(fns)}

if __name__ == "__main__":
    r = main()
    print("JSON", json.dumps(r))
