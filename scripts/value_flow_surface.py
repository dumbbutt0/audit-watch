#!/usr/bin/env python3
"""
value_flow_surface.py — Phase-35 RESEARCH-ONLY library-aware value-flow surfacing lane (un-wired).

P33's recall miss: the value/state overlay REFUSES view/pure functions without a value-comparison param
(value_state_recall_sample.py:110) and then class-cap-starves the rest with liquidation helpers — so
library-resident value-flow transforms (often pure/view helpers feeding mutating callers) are invisible. This lane
represents them BEFORE diversity caps eliminate them. It is a CANDIDATE-QUEUE fix: it surfaces better candidates and
feeds them to the UNCHANGED P33 enumerator + P34 parity gate. It never broadens mechanism rules and never advances a
mechanism.

Lanes (source-observable, GENERIC vocab — config/value_flow_surface.json; no subject-specific names):
  library_value_flow · bytes_decode_transform · oracle_value_derivation · accounting_utility ·
  downstream_mutation_dependency (pure/view/internal helper whose return flows into a mutating external/public caller).
Anti-starvation/flooding: reserved slots per lane + caps per file / operation-family / caller-family + exclusion of
pause/access/logging-only helpers.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: value_flow_surface.py [--manifest <p>] [--out <p>] | --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "value_flow_surface.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_audit as SFA  # _function_body  # noqa: E402
import sibling_function_parity_taxonomy as sfp  # extract_features  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}
_LANE_PRIORITY = ["bytes_decode_transform", "oracle_value_derivation", "accounting_utility",
                  "downstream_mutation_dependency", "library_value_flow"]


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _is_library(item: dict) -> bool:
    c = _cfg()
    f = (item.get("file") or "").lower()
    con = (item.get("contract") or "").lower()
    if any(p in f for p in c["library_file_patterns"]):
        return True
    return any(re.search(p, con) for p in c["library_contract_patterns"])


def _hits(terms, text) -> list:
    t = (text or "").lower()
    return [w for w in terms if w in t]


def lanes_for(item: dict, body: str, downstream_users: list) -> tuple[set, list]:
    """Return (lanes, source_signals) from generic source signals."""
    c = _cfg()
    sig = (item.get("signature") or "")
    blob = f"{item.get('contract','')} {item.get('name','')} {sig} {body or ''}".lower()
    lanes, signals = set(), []

    vf = _hits(c["value_flow_terms"], blob)
    lib = _is_library(item)
    if lib and vf:
        lanes.add("library_value_flow"); signals.append(f"library+value_flow:{vf[:4]}")
    for lane, toks in c["lane_signals"].items():
        h = _hits(toks, blob)
        if h:
            lanes.add(lane); signals.append(f"{lane}:{h[:4]}")
    if downstream_users:
        lanes.add("downstream_mutation_dependency")
        signals.append(f"downstream_mutating_callers:{downstream_users[:4]}")
    return lanes, signals


def excluded_reason(item: dict, body: str, lanes: set) -> str | None:
    """Deprioritize/exclude functions whose only semantics are pause/access/logging and that carry no value-flow lane."""
    c = _cfg()
    blob = f"{item.get('name','')} {item.get('signature','')} {body or ''}".lower()
    if lanes:
        return None
    if _hits(c["exclusion_terms"], blob):
        return "access/control/pause/logging-only (no value-flow lane)"
    return "no value-flow lane signal"


def _primary_lane(lanes: set) -> str:
    for l in _LANE_PRIORITY:
        if l in lanes:
            return l
    return "none"


def _operation_family(item: dict, lanes: set, body: str) -> str:
    if "oracle_value_derivation" in lanes:
        return "oracle"
    if "bytes_decode_transform" in lanes:
        return "bytes"
    if "accounting_utility" in lanes:
        return "accounting"
    if "liquidat" in (item.get("name", "") + body).lower():
        return "liquidation"
    return "value"


def _score(item: dict, lanes: set, signals: list, downstream_users: list) -> int:
    s = len(lanes) * 2 + len(signals)
    if _is_library(item):
        s += 2
    if downstream_users:
        s += 2
    return s


def surface(items: list, bodies: dict, reverse_index: dict) -> dict:
    """items: in-scope function manifest items; bodies: id->body; reverse_index: callee_name(lower)->[caller item]."""
    c = _cfg()
    b = c["budget"]
    cand = []
    for it in items:
        body = bodies.get(it["id"], "")
        callers = reverse_index.get((it.get("name") or "").lower(), [])
        mut_callers = [ca.get("name") for ca in callers
                       if (ca.get("visibility") in ("external", "public"))
                       and ((ca.get("mutability") not in ("view", "pure"))
                            or any(m in (ca.get("name") or "").lower() for m in c["mutating_caller_signals"]))]
        lanes, signals = lanes_for(it, body, mut_callers)
        excl = excluded_reason(it, body, lanes)
        rec = {**FLAGS, "candidate_function": {"file": it.get("file"), "function": it.get("name"),
                                               "contract": it.get("contract"),
                                               "lines": f"{(it.get('source_span') or {}).get('start_line')}-{(it.get('source_span') or {}).get('end_line')}"},
               "manifest_id": it["id"], "visibility": it.get("visibility"), "mutability": it.get("mutability"),
               "lanes": sorted(lanes), "surface_lane": _primary_lane(lanes), "source_signals": signals,
               "downstream_users": mut_callers[:8],
               "operation_family": _operation_family(it, lanes, body),
               "file_cluster": (it.get("file") or "").split("/")[-1],
               "caller_family": it.get("contract"),
               "why_selected": None, "cap_bucket": None,
               "rank_before_diversity": None, "rank_after_diversity": None,
               "excluded_reason": excl, "_score": _score(it, lanes, signals, mut_callers)}
        cand.append(rec)

    eligible = [r for r in cand if r["excluded_reason"] is None]
    eligible.sort(key=lambda r: -r["_score"])
    for i, r in enumerate(eligible):
        r["rank_before_diversity"] = i + 1

    selected, fcount, ofcount, ccount, lanecount = [], {}, {}, {}, {}

    def caps_ok(r):
        return (fcount.get(r["file_cluster"], 0) < b["cap_per_file"]
                and ofcount.get(r["operation_family"], 0) < b["cap_per_operation_family"]
                and ccount.get(r["caller_family"], 0) < b["cap_per_caller_family"])

    def take(r, why):
        selected.append(r)
        r["why_selected"] = why
        r["cap_bucket"] = f"{r['operation_family']}|{r['file_cluster']}"
        fcount[r["file_cluster"]] = fcount.get(r["file_cluster"], 0) + 1
        ofcount[r["operation_family"]] = ofcount.get(r["operation_family"], 0) + 1
        ccount[r["caller_family"]] = ccount.get(r["caller_family"], 0) + 1
        for l in r["lanes"]:
            lanecount[l] = lanecount.get(l, 0) + 1

    # PASS 1 — reserved slots per lane (anti-starvation): guarantee minimum representation
    for lane, mn in b["reserved_slots"].items():
        for r in eligible:
            if len(selected) >= b["total"]:
                break
            if lanecount.get(lane, 0) >= mn:
                break
            if r in selected or lane not in r["lanes"]:
                continue
            if fcount.get(r["file_cluster"], 0) < b["cap_per_file"]:
                take(r, f"reserved:{lane}")

    # PASS 2 — fill remaining budget by rank under all caps (anti-flooding)
    for r in eligible:
        if len(selected) >= b["total"]:
            break
        if r in selected:
            continue
        if caps_ok(r):
            take(r, "rank_fill")

    sel_ids = {id(r) for r in selected}
    for i, r in enumerate(selected):
        r["rank_after_diversity"] = i + 1
    for r in eligible:
        if id(r) not in sel_ids and r["excluded_reason"] is None:
            r["excluded_reason"] = "diversity_cap_or_budget"

    return {**FLAGS, "total_budget": b["total"], "selected_count": len(selected),
            "eligible_count": len(eligible), "selected_by_lane": lanecount,
            "selected": selected, "all_candidates": cand}


# ---- CLI helpers (build bodies + reverse-call index from a manifest) ----

def _load_manifest(p: Path) -> list:
    m = json.loads(p.read_text())
    return [i for i in m.get("items", []) if i.get("kind") == "function" and i.get("in_scope")]


def build_inputs(items: list):
    bodies, calls = {}, {}
    for it in items:
        body = SFA._function_body(it.get("file"), (it.get("source_span") or {}).get("start_line"), True)
        bodies[it["id"]] = body
        calls[it["id"]] = {c.lower() for c in sfp.extract_features(it.get("name", ""), snippet=body)["calls"]}
    reverse = {}
    by_name = {}
    for it in items:
        by_name.setdefault((it.get("name") or "").lower(), []).append(it)
    for it in items:
        for callee in calls[it["id"]]:
            if callee in by_name:
                reverse.setdefault(callee, []).append(it)
    return bodies, reverse


# --------------------------------- self-test (the 6 required cases) ---------------------------------

def _it(name, contract, file, vis="internal", mut="", sig=""):
    return {"id": f"function:{contract}:{name}", "name": name, "contract": contract, "file": file,
            "visibility": vis, "mutability": mut, "signature": sig or f"function {name}(...)",
            "source_span": {"start_line": 1, "end_line": 9}}


def _self_test():
    ok = True
    # 1 library-file inclusion: a Lib* file fn with value-flow vocab -> library_value_flow
    it1 = _it("computeFee", "LibFees", "contracts/libraries/LibFees.sol", mut="view")
    l1, s1 = lanes_for(it1, "uint fee = amount * rate / SCALE; return fee;", [])
    c1 = "library_value_flow" in l1
    print(f"  [{'PASS' if c1 else 'FAIL'}] library file inclusion ({sorted(l1)})"); ok &= c1
    # 2 bytes decode transform
    it2 = _it("readPacked", "LibBytes", "contracts/libraries/LibBytes.sol", mut="pure")
    l2, _ = lanes_for(it2, "uint x = abi.decode(data, (uint256)); y = uint88(bytesData >> 8);", [])
    c2 = "bytes_decode_transform" in l2
    print(f"  [{'PASS' if c2 else 'FAIL'}] bytes decode transform ({sorted(l2)})"); ok &= c2
    # 3 oracle/value derivation
    it3 = _it("oracleCheck", "LibOracle", "contracts/libraries/LibOracle.sol", vis="private", mut="view")
    l3, _ = lanes_for(it3, "uint p = getSafeLatestPrice(); if (stale) revert; return p / decimals;", [])
    c3 = "oracle_value_derivation" in l3
    print(f"  [{'PASS' if c3 else 'FAIL'}] oracle value derivation ({sorted(l3)})"); ok &= c3
    # 4 downstream mutating usage rescues a view helper
    it4 = _it("calcDebt", "LibSR", "contracts/libraries/LibSR.sol", mut="")
    l4, s4 = lanes_for(it4, "return debt * collateral / x;", ["liquidate", "exitShort"])
    c4 = "downstream_mutation_dependency" in l4
    print(f"  [{'PASS' if c4 else 'FAIL'}] downstream mutating usage rescue ({sorted(l4)})"); ok &= c4
    # 5 diversity cap: many liquidation helpers in one contract cannot exceed cap_per_operation_family
    items = [_it(f"_liqHelper{i}", "PrimaryLiquidationFacet", "contracts/facets/PrimaryLiquidationFacet.sol")
             for i in range(8)]
    bodies = {it["id"]: "uint take = collateral * liquidationDiscount; settle();" for it in items}
    out = surface(items, bodies, {})
    liq = sum(1 for r in out["selected"] if r["operation_family"] == "liquidation")
    cap = _cfg()["budget"]["cap_per_operation_family"]
    c5 = liq <= cap
    print(f"  [{'PASS' if c5 else 'FAIL'}] diversity cap: liquidation selected {liq} <= cap {cap}"); ok &= c5
    # 6 exclusion of access/control/logging-only helpers
    it6 = _it("setAdmin", "Gov", "contracts/Gov.sol", vis="external")
    l6, _ = lanes_for(it6, "onlyOwner; admin = newAdmin; emit AdminSet(newAdmin);", [])
    e6 = excluded_reason(it6, "onlyOwner; admin = newAdmin; emit AdminSet(newAdmin);", l6)
    c6 = e6 is not None
    print(f"  [{'PASS' if c6 else 'FAIL'}] access/logging-only excluded ({e6})"); ok &= c6
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.manifest:
        ap.error("--manifest required (or --self-test)")
    items = _load_manifest(Path(args.manifest))
    bodies, reverse = build_inputs(items)
    out = surface(items, bodies, reverse)
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"[value_flow_surface] {out['selected_count']}/{out['eligible_count']} selected | by_lane={out['selected_by_lane']}")
    for r in out["selected"]:
        print(f"  {r['surface_lane']:<28} {r['caller_family']}.{r['candidate_function']['function']} "
              f"[{r['visibility']}/{r['mutability']}] downstream={r['downstream_users'][:3]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
