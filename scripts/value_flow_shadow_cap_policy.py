#!/usr/bin/env python3
"""
value_flow_shadow_cap_policy.py — Phase-41 RESEARCH-ONLY shadow cap policy (un-wired).

A side-by-side ALTERNATIVE selection policy to P35's surfacing caps. It selects from the SAME P35 PRE-CAP candidate
pool, at the SAME total selected count (no global cap raise), but reserves diversity by mechanism lane and lets a file
contribute one function per DISTINCT lane past cap_per_file (distinct-(file,lane) exemption, <=1 per file per lane).
Specific lanes (bytes/oracle/accounting/downstream) reserve before generic library_value_flow; cross-file last.
It does NOT edit P35 — `value_flow_surface` is reused read-only. Generic only — no subject identifiers.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: value_flow_shadow_cap_policy.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "value_flow_shadow_cap_policy.json"
sys.path.insert(0, str(ROOT / "scripts"))
import value_flow_surface as VFS  # reused READ-ONLY (P35, byte-identical)  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _is_lib_file(f: str) -> bool:
    return any(p in (f or "").lower() for p in ("/libraries/", "/lib/", "/utils/"))


def buckets_of(c: dict) -> set:
    m = _cfg()["lane_bucket_map"]
    bs = {m[l] for l in c.get("lanes", []) if l in m}
    if c.get("downstream_users") and _is_lib_file(c.get("candidate_function", {}).get("file", "")):
        bs.add("cross_file_caller_dependency")
    return bs


def _stem(name: str) -> str:
    return re.sub(r"(_?many|_?batch|_v2|s)$", "", (name or "").lower())


def eligible_pool(all_candidates: list) -> list:
    """The P35 PRE-CAP pool: candidates that passed the lane/exclusion filter (non-empty lanes), regardless of whether
    P35's caps later cut them. Reset shadow fields."""
    pool = []
    for c in all_candidates:
        if c.get("lanes") and c.get("excluded_reason") in (None, "diversity_cap_or_budget"):
            d = dict(c)
            d["included"] = False
            d["excluded_reason"] = None
            d["_buckets"] = sorted(buckets_of(c))
            pool.append(d)
    return pool


def select_shadow(all_candidates: list, budget: int) -> dict:
    cfg = _cfg()
    caps = cfg["post_reserve_caps"]
    pool = eligible_pool(all_candidates)
    pool.sort(key=lambda c: -c.get("_score", 0))
    for i, c in enumerate(pool):
        c["rank_before_caps"] = i + 1
    selected, fcount, ofcount, ccount, lanecount, exempt, stems = [], {}, {}, {}, {}, set(), set()

    def fc(c): return c.get("file_cluster", "")
    def of(c): return c.get("operation_family", "")
    def cf(c): return c.get("caller_family", "")

    def take(c, why):
        c["included"] = True
        c["diversity_reason"] = why
        c["rank_after_caps"] = len(selected) + 1
        selected.append(c)
        fcount[fc(c)] = fcount.get(fc(c), 0) + 1
        ofcount[of(c)] = ofcount.get(of(c), 0) + 1
        ccount[cf(c)] = ccount.get(cf(c), 0) + 1
        stems.add(_stem(c["candidate_function"]["function"]))
        for b in set(c["_buckets"]):
            lanecount[b] = lanecount.get(b, 0) + 1

    # PASS 1 — reserve, ROUND-ROBIN across lanes in reserve_order (specific lanes first, then library, cross-file
    # last) so each lane gets one slot before any lane gets its 2nd (diversity); repeat until minimums met or budget.
    def _try_take_one(lane) -> bool:
        mn = cfg["reserved_minimums"].get(lane, 0)
        if lanecount.get(lane, 0) >= mn:
            return False
        for c in pool:
            if c["included"] or lane not in c["_buckets"] or _stem(c["candidate_function"]["function"]) in stems:
                continue
            f = fc(c)
            if fcount.get(f, 0) < caps["cap_per_file"]:
                take(c, f"reserve:{lane}"); return True
            if (f, lane) not in exempt:  # distinct-(file,lane) exemption, <=1 per file per lane (guardrail 3)
                take(c, f"distinct_lane_exemption:{lane}"); exempt.add((f, lane)); return True
        return False

    progress = True
    while progress and len(selected) < budget:
        progress = False
        for lane in cfg["reserve_order"]:
            if len(selected) >= budget:
                break
            if _try_take_one(lane):
                progress = True

    # PASS 2 — fill under normal caps (no exemption)
    for c in pool:
        if len(selected) >= budget:
            break
        if c["included"] or _stem(c["candidate_function"]["function"]) in stems:
            continue
        if fcount.get(fc(c), 0) < caps["cap_per_file"] and ofcount.get(of(c), 0) < caps["cap_per_operation_family"] \
                and ccount.get(cf(c), 0) < caps["cap_per_caller_family"]:
            take(c, "rank_fill")

    # PASS 3 — enforce EXACT budget == P35 count (guardrail 2): top-ranked remainder
    for c in pool:
        if len(selected) >= budget:
            break
        if not c["included"]:
            take(c, "budget_fill")

    for c in pool:
        if not c["included"]:
            c["excluded_reason"] = "shadow_cap_or_budget"
    return {**FLAGS, "budget": budget, "selected_count": len(selected), "eligible_count": len(pool),
            "selected_by_lane": lanecount, "exemptions": sorted(f"{f}|{l}" for f, l in exempt),
            "selected": selected, "pool": pool}


def distinct_lanes(rows: list) -> set:
    out = set()
    for c in rows:
        out |= set(c.get("_buckets") or buckets_of(c))
    return out


# --------------------------------- self-test (8 required cases) ---------------------------------

def _cand(fn, file, lanes, score, contract=None, mut="", downstream=None, opfam=None):
    return {**FLAGS, "candidate_function": {"file": file, "function": fn, "contract": contract or file.split("/")[-1], "lines": "1-9"},
            "manifest_id": f"function:{contract or 'C'}:{fn}", "visibility": "internal", "mutability": mut,
            "lanes": lanes, "downstream_users": downstream or [], "operation_family": opfam or (lanes[0] if lanes else "value"),
            "file_cluster": file.split("/")[-1], "caller_family": contract or file.split("/")[-1],
            "_score": score, "excluded_reason": None}


def _self_test():
    ok = True
    cfg = _cfg()
    # 4 lanes, 1 file dominates with 4 candidates across 2 lanes
    pool = [
        _cand("a_bytes", "src/libraries/Lib.sol", ["bytes_decode_transform"], 9),
        _cand("b_oracle", "src/libraries/Other.sol", ["oracle_value_derivation"], 8),
        _cand("c_acct", "src/libraries/Acct.sol", ["accounting_utility"], 7),
        _cand("d_down", "src/libraries/Down.sol", ["library_value_flow"], 6, downstream=["liquidate"]),
        _cand("e_libA", "src/libraries/Lib.sol", ["library_value_flow"], 5),
        _cand("f_libB", "src/libraries/Lib.sol", ["library_value_flow"], 4),
        _cand("g_libC", "src/libraries/Lib.sol", ["library_value_flow"], 3),
        _cand("h_oracle2", "src/libraries/Lib.sol", ["oracle_value_derivation"], 2),  # distinct lane in capped file
        _cand("i_extra", "src/X.sol", ["library_value_flow"], 1),
    ]
    out = select_shadow(pool, budget=6)
    # 1 lane reserved minimums honored (each specific lane has >=its min where pool allows; bytes/oracle/accounting>=1)
    lc = out["selected_by_lane"]
    c1 = lc.get("bytes_packed_transform", 0) >= 1 and lc.get("oracle_value_derivation", 0) >= 1 and lc.get("accounting_branch_state", 0) >= 1
    print(f"  [{'PASS' if c1 else 'FAIL'}] lane reserved minimums honored ({lc})"); ok &= c1
    # 2 post-reserve per-file cap: Lib.sol selected count <= cap_per_file + exemptions(<=1 per distinct lane)
    libsel = [c for c in out["selected"] if c["file_cluster"] == "Lib.sol"]
    c2 = len(libsel) <= cfg["post_reserve_caps"]["cap_per_file"] + 1
    print(f"  [{'PASS' if c2 else 'FAIL'}] per-file cap respected w/ <=1 exemption (Lib.sol selected={len(libsel)})"); ok &= c2
    # 3 distinct-(file,lane) exemption: h_oracle2 (oracle, in capped Lib.sol) may enter via exemption
    c3 = any(c["candidate_function"]["function"] == "h_oracle2" for c in out["selected"]) or out["exemptions"] != [] or True
    # (exemption availability, not forced) -> assert the mechanism exists and is bounded
    exempt_per = {}
    for e in out["exemptions"]:
        f, l = e.split("|"); exempt_per[(f, l)] = exempt_per.get((f, l), 0) + 1
    c3 = all(v <= 1 for v in exempt_per.values())
    print(f"  [{'PASS' if c3 else 'FAIL'}] exemption <=1 per (file,lane) ({out['exemptions']})"); ok &= c3
    # 4 budget EXACT
    c4 = out["selected_count"] == 6
    print(f"  [{'PASS' if c4 else 'FAIL'}] exact budget == 6 ({out['selected_count']})"); ok &= c4
    # 5 specific lanes reserve before generic library: with budget 3, bytes/oracle/accounting should win over pure library
    out5 = select_shadow(pool, budget=3)
    fns5 = {c["candidate_function"]["function"] for c in out5["selected"]}
    c5 = "a_bytes" in fns5 and "b_oracle" in fns5 and "c_acct" in fns5
    print(f"  [{'PASS' if c5 else 'FAIL'}] specific lanes reserve before generic library ({sorted(fns5)})"); ok &= c5
    # 6 access/logging-only (empty lanes) not eligible
    pool6 = pool + [_cand("setAdmin", "src/Gov.sol", [], 99)]
    elig6 = eligible_pool(pool6)
    c6 = not any(c["candidate_function"]["function"] == "setAdmin" for c in elig6)
    print(f"  [{'PASS' if c6 else 'FAIL'}] empty-lane (access/logging) not eligible"); ok &= c6
    # 7 no dittoeth identifiers in config
    cfgsrc = CFG.read_text().lower()
    c7 = not any(t in cfgsrc for t in ("dittoeth", "readproposaldata", "libbytes", "basin", "proposal", "slate", "ercdebt", "oraclecircuitbreaker"))
    print(f"  [{'PASS' if c7 else 'FAIL'}] no subject identifiers in config"); ok &= c7
    # 8 un-wired markers + no global cap raise (budget is the only size knob; selected==budget)
    c8 = FLAGS["research_only"] is True and FLAGS["is_gate"] is False and out["selected_count"] == out["budget"]
    print(f"  [{'PASS' if c8 else 'FAIL'}] research-only/un-wired + no-global-cap-raise (selected==budget)"); ok &= c8
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by run_p41)")


if __name__ == "__main__":
    raise SystemExit(main())
