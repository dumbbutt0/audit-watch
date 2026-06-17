#!/usr/bin/env python3
"""
value_state_shadow_ranker.py — Phase-42 RESEARCH-ONLY shadow value/state ranking (un-wired).

Re-scores P35's pre-cap candidate pool with GENERIC value-flow-relevance signals (computed from the existing P35
candidate features + a light branch scan), then re-selects under P35's UNCHANGED caps/budget ordered by shadow_score.
Tests whether genuinely value-flow-relevant library functions lift without increasing noisy advances. Does NOT edit
P35 — `value_flow_surface` + its cap config are reused read-only. Generic only — no subject identifiers.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: value_state_shadow_ranker.py --self-test
"""
from __future__ import annotations
import argparse, json, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "value_state_shadow_ranker.json"
P35_CFG = ROOT / "config" / "value_flow_surface.json"
sys.path.insert(0, str(ROOT / "scripts"))
import value_flow_shadow_cap_policy as P41  # reuse eligible_pool (pre-cap pool)  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


@lru_cache(maxsize=1)
def _p35_budget() -> dict:
    return json.loads(P35_CFG.read_text())["budget"]


def shadow_score(rec: dict, body: str = "") -> tuple[float, dict]:
    cfg = _cfg(); w = cfg["weights"]
    s = 0.0
    sig = {"downstream_mutating_caller": [], "accounting_branch_density": [], "oracle_value_derivation": [],
           "return_to_mutation_dependency": [], "library_criticality": [], "anti_noise_penalties": []}
    du = rec.get("downstream_users") or []
    lanes = set(rec.get("lanes") or [])
    b = (body or "").lower()

    if du:
        s += w["downstream_mutating_caller"]; sig["downstream_mutating_caller"] = du[:4]
        if any(any(t in (c or "").lower() for t in cfg["value_caller_role_terms"]) for c in du):
            s += w["downstream_value_caller_bonus"]
            sig["downstream_mutating_caller"].append("value_role_caller")
        if rec.get("visibility") in ("internal", "private") or rec.get("mutability") in ("view", "pure"):
            s += w["return_to_mutation_dependency"]; sig["return_to_mutation_dependency"] = ["helper_return_feeds_mutation"]

    if cfg["accounting_lane_name"] in lanes:
        branches = sum(b.count(t) for t in cfg["branch_tokens"])
        if branches >= 1 and any(t in b for t in cfg["accounting_terms"]):
            s += w["accounting_branch_density"]; sig["accounting_branch_density"] = [f"branches~{branches}"]

    if cfg["oracle_lane_name"] in lanes:
        s += w["oracle_value_derivation"]; sig["oracle_value_derivation"] = ["oracle_lane"]

    is_lib = any(p in (rec.get("candidate_function", {}).get("file") or "").lower() for p in cfg["library_file_patterns"])
    if is_lib and du:
        s += w["library_criticality_with_downstream"]; sig["library_criticality"] = ["library+downstream"]

    s += w["lane_breadth"] * max(0, len(lanes) - 1)

    blob = ((rec.get("candidate_function", {}).get("function") or "") + " " + b).lower()
    if any(t in blob for t in cfg["anti_noise_terms"]):
        s += w["anti_noise_penalty"]; sig["anti_noise_penalties"] = ["access/pause/logging"]
    return s, sig


def _diversity_order(eligible: list) -> list:
    """Sort by -shadow_score, with a tie-break (within epsilon) preferring a candidate that adds a not-yet-seen lane."""
    eps = _cfg()["diversity_tiebreak_epsilon"]
    pool = sorted(eligible, key=lambda c: -c["shadow_score"])
    out, seen = [], set()
    i = 0
    while i < len(pool):
        # gather the epsilon-close group starting at i
        j = i
        while j + 1 < len(pool) and (pool[i]["shadow_score"] - pool[j + 1]["shadow_score"]) < eps:
            j += 1
        remaining = pool[i:j + 1]  # already score-descending
        # greedy within the close group: repeatedly take the highest-score candidate that adds a NEW lane
        # relative to what's already committed (seen); else take the highest-score remaining.
        while remaining:
            k = next((idx for idx, c in enumerate(remaining) if set(c.get("lanes") or []) - seen), 0)
            c = remaining.pop(k)
            out.append(c); seen |= set(c.get("lanes") or [])
        i = j + 1
    return out


def select_shadow(all_candidates: list, bodies: dict) -> dict:
    b = _p35_budget()  # P35 caps/budget — UNCHANGED
    eligible = P41.eligible_pool(all_candidates)  # P35 pre-cap pool
    for c in eligible:
        c["shadow_score"], c["ranking_signals"] = shadow_score(c, bodies.get(c.get("manifest_id"), ""))
    ordered = _diversity_order(eligible)
    for i, c in enumerate(ordered):
        c["shadow_rank"] = i + 1
    selected, fcount, ofcount, ccount, lanecount = [], {}, {}, {}, {}

    def caps_ok(c):
        return (fcount.get(c["file_cluster"], 0) < b["cap_per_file"]
                and ofcount.get(c["operation_family"], 0) < b["cap_per_operation_family"]
                and ccount.get(c["caller_family"], 0) < b["cap_per_caller_family"])

    def take(c, why):
        c["selected_by_shadow"] = True; c["selected_reason"] = why
        selected.append(c)
        fcount[c["file_cluster"]] = fcount.get(c["file_cluster"], 0) + 1
        ofcount[c["operation_family"]] = ofcount.get(c["operation_family"], 0) + 1
        ccount[c["caller_family"]] = ccount.get(c["caller_family"], 0) + 1
        for l in c.get("lanes", []):
            lanecount[l] = lanecount.get(l, 0) + 1

    # PASS 1 — P35 reserved slots (same lane names/minimums), ordered by shadow_score
    for lane, mn in b["reserved_slots"].items():
        for c in ordered:
            if len(selected) >= b["total"] or lanecount.get(lane, 0) >= mn:
                break
            if c.get("selected_by_shadow") or lane not in c.get("lanes", []):
                continue
            if fcount.get(c["file_cluster"], 0) < b["cap_per_file"]:
                take(c, f"reserved:{lane}")
    # PASS 2 — fill under P35 caps, ordered by shadow_score
    for c in ordered:
        if len(selected) >= b["total"]:
            break
        if c.get("selected_by_shadow"):
            continue
        if caps_ok(c):
            take(c, "rank_fill")
    for c in ordered:
        c.setdefault("selected_by_shadow", False)
        if not c["selected_by_shadow"]:
            c["excluded_reason"] = "shadow_rank_or_cap"
    return {**FLAGS, "budget": b["total"], "selected_count": len(selected),
            "selected_by_lane": lanecount, "selected": selected, "pool": ordered}


# --------------------------------- self-test (9 required cases) ---------------------------------

def _rec(fn, file, lanes, vis="internal", mut="", downstream=None, contract=None):
    return {**FLAGS, "candidate_function": {"file": file, "function": fn, "contract": contract or "C", "lines": "1-9"},
            "manifest_id": f"function:C:{fn}", "visibility": vis, "mutability": mut, "lanes": lanes,
            "downstream_users": downstream or [], "operation_family": (lanes[0] if lanes else "value"),
            "file_cluster": file.split("/")[-1], "caller_family": contract or "C", "_score": 1, "excluded_reason": None}


def _self_test():
    ok = True
    base, _ = shadow_score(_rec("f", "src/X.sol", ["library_value_flow"]))
    # 1 downstream mutating caller boost
    s1, sig1 = shadow_score(_rec("calc", "src/libraries/Lib.sol", ["library_value_flow"], downstream=["liquidate"]))
    c1 = s1 > base and bool(sig1["downstream_mutating_caller"])
    print(f"  [{'PASS' if c1 else 'FAIL'}] downstream mutating caller boost ({s1} > {base})"); ok &= c1
    # 2 accounting branch density boost
    s2, sig2 = shadow_score(_rec("upd", "src/libraries/Lib.sol", ["accounting_utility"]), "if (x) { debt -= d; } else { debt += d; }")
    s2b, _ = shadow_score(_rec("upd", "src/libraries/Lib.sol", ["accounting_utility"]), "return debt;")
    c2 = s2 > s2b and bool(sig2["accounting_branch_density"])
    print(f"  [{'PASS' if c2 else 'FAIL'}] accounting branch density boost ({s2} > {s2b})"); ok &= c2
    # 3 oracle derivation boost
    s3, sig3 = shadow_score(_rec("px", "src/libraries/Oracle.sol", ["oracle_value_derivation"]))
    c3 = s3 > base and bool(sig3["oracle_value_derivation"])
    print(f"  [{'PASS' if c3 else 'FAIL'}] oracle derivation boost"); ok &= c3
    # 4 return-to-mutation dependency boost (view helper + downstream)
    s4, sig4 = shadow_score(_rec("calc", "src/libraries/Lib.sol", ["library_value_flow"], mut="view", downstream=["mint"]))
    c4 = sig4["return_to_mutation_dependency"] != []
    print(f"  [{'PASS' if c4 else 'FAIL'}] return-to-mutation dependency boost"); ok &= c4
    # 5 library-only WITHOUT downstream -> no library_criticality boost
    s5, sig5 = shadow_score(_rec("util", "src/libraries/Lib.sol", ["library_value_flow"]))
    c5 = sig5["library_criticality"] == []
    print(f"  [{'PASS' if c5 else 'FAIL'}] library-only w/o downstream -> no boost"); ok &= c5
    # 6 access/logging penalty
    s6, sig6 = shadow_score(_rec("setAdmin", "src/Gov.sol", ["library_value_flow"]), "onlyOwner; emit AdminSet();")
    c6 = sig6["anti_noise_penalties"] != [] and s6 < base
    print(f"  [{'PASS' if c6 else 'FAIL'}] access/logging penalty ({s6} < {base})"); ok &= c6
    # 7 diversity tie-break only within close scores
    a = _rec("a", "src/A.sol", ["bytes_decode_transform"]); a["shadow_score"] = 10.0
    bb = _rec("b", "src/B.sol", ["bytes_decode_transform"]); bb["shadow_score"] = 9.9  # close, same lane
    cc = _rec("c", "src/C.sol", ["oracle_value_derivation"]); cc["shadow_score"] = 9.8  # close, NEW lane
    dd = _rec("d", "src/D.sol", ["accounting_utility"]); dd["shadow_score"] = 2.0       # far, new lane
    order = [x["candidate_function"]["function"] for x in _diversity_order([a, bb, cc, dd])]
    c7 = order.index("c") < order.index("b") and order[-1] == "d"  # new-lane c promoted above b within epsilon; far d stays last
    print(f"  [{'PASS' if c7 else 'FAIL'}] diversity tie-break only within epsilon ({order})"); ok &= c7
    # 8 no subject identifiers in config
    cfgsrc = CFG.read_text().lower()
    c8 = not any(t in cfgsrc for t in ("dittoeth", "readproposaldata", "libbytes", "basin", "proposal", "slate", "ercdebt", "oraclecircuit"))
    print(f"  [{'PASS' if c8 else 'FAIL'}] no subject identifiers in config"); ok &= c8
    # 9 un-wired markers
    c9 = FLAGS["research_only"] is True and FLAGS["is_gate"] is False and _cfg().get("research_only") is True
    print(f"  [{'PASS' if c9 else 'FAIL'}] research-only / un-wired markers"); ok &= c9
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by run_p42)")


if __name__ == "__main__":
    raise SystemExit(main())
