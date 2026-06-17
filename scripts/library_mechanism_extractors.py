#!/usr/bin/env python3
"""
library_mechanism_extractors.py — Phase-36 RESEARCH-ONLY library mechanism-extraction depth (un-wired).

P35 surfaces the right library/value-flow neighborhoods; the enumerator can't yet EXPLAIN the deeper library
mechanism shapes. This module adds three source-backed extractors for exactly those shapes:
  - bytes_offset_decode_mismatch   (packed/offset/decode field mismatch)
  - oracle_value_derivation_mismatch (staleness / decimals / inversion mismatch)
  - accounting_condition_mismatch  (if-check / conditional state-update asymmetry)

NORTH STAR: "source-backed mismatch + downstream value use". A candidate SURVIVES only with exact source evidence +
>=1 downstream value-flow use + a comparand-grounded mismatch (support>=MEDIUM). Sibling-CALL-delta candidates (e.g. a
missing staleness call a sibling has) additionally pass the UNCHANGED P34 comparand_parity_gate. Otherwise ABSTAIN.
No subject names are hardcoded; answer-key fields are refused.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: library_mechanism_extractors.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "library_mechanism_extractors.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # extract_features / strip_comments  # noqa: E402
import comparand_parity_gate as PG  # P34 gate (byte-identical)  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}
_FORBIDDEN = {"awarded", "awarded_mechanisms", "expected", "expected_mechanism", "issue_id", "severity", "answer",
              "must_reject", "known_bug", "report"}
_SUPPORT = {"strong": 3, "medium": 2, "weak": 1, "none": 0}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _strip(s: str) -> str:
    return sfp.strip_comments(s or "")


def _has(sigs, text) -> list:
    t = (text or "").lower()
    return [s for s in sigs if s.lower() in t]


def _semantic_role(name_blob: str) -> str:
    c = _cfg()["semantic_role_terms"]
    t = name_blob.lower()
    for role, terms in c.items():
        if any(x in t for x in terms):
            return role
    return "unknown"


def _downstream_uses(downstream_users: list) -> list:
    roles = _cfg()["downstream_value_roles"]
    out = []
    for caller in downstream_users or []:
        cl = caller.lower()
        use = next((r for r, terms in roles.items() if any(x in cl for x in terms)), "other")
        out.append({"function": caller, "use": use})
    return out


def _ev(target, snippet, why):
    return {"file": target.get("file", ""), "lines": target.get("lines", ""),
            "snippet": (snippet or "")[:200], "why_it_matters": why}


def _cand(extractor, target, summary, evidence, field, downstream, kind, desc, support, style, omitted="", reject=None):
    conf = {"strong": "HIGH", "medium": "MEDIUM"}.get(support, "LOW")
    return {**FLAGS, "candidate_id": f"{extractor}:{target.get('name')}", "extractor": extractor,
            "target": {"file": target.get("file"), "function": target.get("name"), "lines": target.get("lines")},
            "mechanism_summary": summary, "source_evidence": evidence, "field_or_value": field,
            "downstream_uses": downstream, "mismatch": {"kind": kind, "description": desc, "support_level": support},
            "reject_if": reject or [], "pre_discrimination_confidence": conf,
            "_style": style, "_omitted_call": omitted}


# ------------------------------- extractor 1: bytes / offset / decode -------------------------------

def _extract_bytes(target, siblings, downstream, body):
    c = _cfg()["bytes_offset_decode"]
    dec = _has(c["decode_signals"], body)
    packed = _has(c["packed_source_signals"], body)
    downcast = re.search(c["downcast_re"], body, re.I)
    # REJECT: bare downcast with no packed/decode source
    if downcast and not packed:
        return [], [{"extractor": "bytes_offset_decode_mismatch", "reject_reason": "bare downcast with no bytes/calldata/packed source"}]
    if not dec or not packed:
        return [], []
    if not downstream:
        return [], [{"extractor": "bytes_offset_decode_mismatch", "reject_reason": "decoded value has no downstream value use"}]
    # field + role: first decoded/assigned identifier near a decode op
    m = re.search(r"\b([A-Za-z_]\w*)\s*=\s*[^;]*(abi\.decode|mload|calldataload|>>|<<|\.slice)", body, re.I)
    field_name = m.group(1) if m else "decoded_field"
    role = _semantic_role(field_name + " " + (m.group(0) if m else ""))
    # mismatch support: value-bearing decoded field with NO length/bounds check covering consumed offsets
    has_len = _has(c["length_check_signals"], body)
    value_bearing = role in ("amount", "price", "address", "debt", "collateral", "share", "fee", "id", "order_field")
    if value_bearing and not has_len:
        support, kind, desc = "medium", "unbounded_offset", f"decoded field '{field_name}' ({role}) used downstream with no length/offset bound covering the consumed field"
    elif value_bearing:
        support, kind, desc = "weak", "bounded_offset", f"decoded field '{field_name}' is value-bearing but a length/bounds check is present"
    else:
        support, kind, desc = "weak", "non_value_field", f"decoded field '{field_name}' role={role} not clearly value-bearing"
    ev = [_ev(target, (m.group(0) if m else dec[0]), "exact decode/slice/offset source of the field")]
    return [_cand("bytes_offset_decode_mismatch", target,
                  f"packed/offset decode of '{field_name}' ({role}) feeds downstream value flow",
                  ev, {"name": field_name, "type": "packed", "source": "decode/slice/load", "semantic_role": role},
                  downstream, kind, desc, support, "self_contained")], []


# ------------------------------- extractor 2: oracle value derivation -------------------------------

def _extract_oracle(target, siblings, downstream, body):
    c = _cfg()["oracle_value_derivation"]
    calls = _has([s for s in c["oracle_call_signals"] if s not in c["name_only_signals"]], body)
    name_only = _has(c["name_only_signals"], body)
    # REJECT: only the word oracle/price, no actual oracle call
    if name_only and not calls:
        return [], [{"extractor": "oracle_value_derivation_mismatch", "reject_reason": "oracle/price name-only, no oracle read call"}]
    if not calls:
        return [], []
    if not downstream:
        return [], [{"extractor": "oracle_value_derivation_mismatch", "reject_reason": "oracle value not used downstream"}]
    stale = _has(c["staleness_signals"], body)
    sib_stale = any(_has(c["staleness_signals"], _strip(s.get("snippet", ""))) and
                    _has([x for x in c["oracle_call_signals"] if x not in c["name_only_signals"]], _strip(s.get("snippet", "")))
                    for s in siblings)
    sib_call = ""
    if not stale and sib_stale:
        # the comparand sibling reads the oracle WITH a staleness call this path omits -> sibling-CALL-delta
        for s in siblings:
            sc = _has(c["staleness_signals"], _strip(s.get("snippet", "")))
            if sc:
                sib_call = next((x for x in ("getsafelatestprice", "getsafe", "latestrounddata") if x in _strip(s.get("snippet", "")).lower()), sc[0])
                break
        return [_cand("oracle_value_derivation_mismatch", target,
                      "oracle read without staleness check that a sibling oracle path enforces",
                      [_ev(target, calls[0], "oracle read on this path lacks the staleness/maxAge guard")],
                      {"name": "price", "type": "uint", "source": "oracle", "semantic_role": "price"},
                      downstream, "missing_staleness", "this path omits a staleness call present on a sibling oracle path",
                      "medium", "comparand_call_delta", omitted=sib_call)], []
    if not stale and not sib_stale:
        # absolute absence, no comparand -> weak (design-absence; do not advance)
        return [_cand("oracle_value_derivation_mismatch", target,
                      "oracle read with no staleness check and no comparand path",
                      [_ev(target, calls[0], "no staleness/maxAge guard, but no sibling comparand either")],
                      {"name": "price", "type": "uint", "source": "oracle", "semantic_role": "price"},
                      downstream, "staleness_design_absence", "no staleness guard; no source comparand it should exist",
                      "weak", "self_contained")], []
    # staleness present & consistent -> weak / reject-ish
    return [_cand("oracle_value_derivation_mismatch", target,
                  "oracle read with staleness check present",
                  [_ev(target, stale[0], "staleness/decimals logic present")],
                  {"name": "price", "type": "uint", "source": "oracle", "semantic_role": "price"},
                  downstream, "staleness_present", "staleness logic present & consistent", "weak", "self_contained")], []


# ------------------------------- extractor 3: accounting condition asymmetry -------------------------------

def _branch_blocks(body: str):
    """Coarse split into the if-region and else-region around the FIRST top-level 'else'."""
    idx = body.lower().find("else")
    if idx < 0:
        return body, ""
    return body[:idx], body[idx:]


def _terms_updated(text: str, terms, ops):
    t = text.lower()
    found = set()
    for term in terms:
        for op in ops:
            if re.search(re.escape(term) + r"[\w\.\[\]]*\s*" + re.escape(op.strip()), t):
                found.add(term)
    return found


def _extract_accounting(target, siblings, downstream, body):
    c = _cfg()["accounting_condition"]
    if not _has(c["branch_signals"], body) or not _has(c["accounting_state_terms"], body):
        return [], []
    if_blk, else_blk = _branch_blocks(body)
    if not else_blk:
        return [], []
    a = _terms_updated(if_blk, c["accounting_state_terms"], c["update_ops"])
    b = _terms_updated(else_blk, c["accounting_state_terms"], c["update_ops"])
    asym = (a - b) | (b - a)
    if not asym:
        return [], [{"extractor": "accounting_condition_mismatch", "reject_reason": "branches update the same accounting terms (symmetric)"}]
    # REJECT: the differing branch is access/pause/event/log/revert-only (no real accounting effect)
    diff_blk = else_blk if (a - b) else if_blk
    if _has(c["exclusion_branch_signals"], diff_blk) and not _terms_updated(diff_blk, c["accounting_state_terms"], c["update_ops"]):
        return [], [{"extractor": "accounting_condition_mismatch", "reject_reason": "branch difference is access/pause/event/revert-only, no accounting state"}]
    if not downstream and (target.get("mutability") in ("view", "pure")):
        return [], [{"extractor": "accounting_condition_mismatch", "reject_reason": "no downstream value effect (view/pure, no mutating caller)"}]
    term = sorted(asym)[0]
    role = _semantic_role(term)
    return [_cand("accounting_condition_mismatch", target,
                  f"accounting term '{term}' updated in one branch but not the parallel branch",
                  [_ev(target, f"...{term}... branch asymmetry", "one conditional branch applies the accounting update the other omits")],
                  {"name": term, "type": "state", "source": "branch", "semantic_role": role},
                  downstream or [{"function": target.get("name"), "use": "collateral_update"}],
                  "branch_asymmetry", f"'{term}' updated in one branch, omitted in the parallel branch", "medium", "self_contained")], []


_EXTRACTORS = [_extract_bytes, _extract_oracle, _extract_accounting]


def extract_all(bundle: dict) -> dict:
    if _FORBIDDEN & set(bundle.keys()):
        raise ValueError(f"extractor bundle must not carry answer-key fields: {sorted(_FORBIDDEN & set(bundle.keys()))}")
    target = bundle["target"]
    siblings = bundle.get("siblings", [])
    downstream = _downstream_uses(bundle.get("downstream_users", []))
    body = _strip(target.get("snippet", ""))
    cands, rejects = [], []
    for ex in _EXTRACTORS:
        cs, rs = ex(target, siblings, downstream, body)
        cands.extend(cs); rejects.extend(rs)
    return {**FLAGS, "candidate_id": bundle.get("candidate_id"), "candidates": cands, "rejected": rejects}


def resolve(candidate: dict, target: dict, siblings: list) -> dict:
    """Survive bar: comparand_call_delta -> P34 parity gate; self_contained -> support>=MEDIUM + exact source + downstream."""
    style = candidate["_style"]
    has_ev = bool(candidate["source_evidence"]) and any((e.get("snippet") or "").strip() for e in candidate["source_evidence"])
    has_down = bool(candidate["downstream_uses"])
    support_ok = _SUPPORT[candidate["mismatch"]["support_level"]] >= _SUPPORT[_cfg()["support_min_to_survive"]]
    if style == "comparand_call_delta":
        g = PG.gate({"name": target.get("function") or target.get("name"), "snippet": target.get("snippet", ""),
                     "visibility": target.get("visibility", "")}, siblings, candidate["_omitted_call"], "missing_call")
        survive = bool(g["parity_pass"]) and has_ev and has_down
        reason = g["rejection_reason"] if not g["parity_pass"] else ("survive (parity_pass)" if survive else "missing evidence/downstream")
        return {"survive": survive, "via": "parity_gate", "parity_pass": g["parity_pass"], "reason": reason}
    survive = support_ok and has_ev and has_down
    reason = ("survive (support+evidence+downstream)" if survive else
              f"abstain: support={candidate['mismatch']['support_level']} ev={has_ev} downstream={has_down}")
    return {"survive": survive, "via": "evidence_bar", "reason": reason}


# --------------------------------- self-test (8 required cases) ---------------------------------

def _b(name, snippet, siblings=None, downstream=None, vis="internal", mut="", file="X.sol"):
    return {"candidate_id": name, "target": {"name": name, "file": file, "lines": "1-9", "snippet": snippet,
            "visibility": vis, "mutability": mut}, "siblings": siblings or [], "downstream_users": downstream or []}


def _self_test():
    ok = True
    # 1 bytes decode WITHOUT length/offset evidence -> candidate at most medium, but self-contained survives only if value-bearing+unbounded; here no downstream -> abstain
    r1 = extract_all(_b("readField", "uint88 amt = uint88(abi.decode(data,(uint256)) >> 8);", downstream=[]))
    c1 = r1["candidates"] == [] and any("downstream" in x["reject_reason"] for x in r1["rejected"])
    print(f"  [{'PASS' if c1 else 'FAIL'}] bytes decode w/o downstream -> rejected ({[x.get('reject_reason') for x in r1['rejected']]})"); ok &= c1
    # 2 bare downcast rejected
    r2 = extract_all(_b("toU88", "return uint88(x);", downstream=["liquidate"]))
    c2 = any("bare downcast" in x["reject_reason"] for x in r2["rejected"]) and not any(c["extractor"]=="bytes_offset_decode_mismatch" for c in r2["candidates"])
    print(f"  [{'PASS' if c2 else 'FAIL'}] bare downcast rejected"); ok &= c2
    # 3 oracle staleness mismatch (sibling checks staleness, target omits) -> comparand_call_delta candidate
    sib = [{"name": "getPriceSafe", "snippet": "p = oracle.getSafeLatestPrice(maxAge); return p;"}]
    r3 = extract_all(_b("getPrice", "uint p = oracle.getLatestPrice(); return p * collateral;", siblings=sib, downstream=["liquidate"]))
    oc = [c for c in r3["candidates"] if c["extractor"]=="oracle_value_derivation_mismatch"]
    c3 = bool(oc) and oc[0]["_style"]=="comparand_call_delta" and oc[0]["mismatch"]["support_level"]=="medium"
    print(f"  [{'PASS' if c3 else 'FAIL'}] oracle staleness mismatch candidate ({oc[0]['mismatch']['kind'] if oc else None})"); ok &= c3
    # 4 oracle name-only rejected
    r4 = extract_all(_b("setOracle", "oracle = newOracle; price = 0;", downstream=["deposit"]))
    c4 = any("name-only" in x["reject_reason"] for x in r4["rejected"])
    print(f"  [{'PASS' if c4 else 'FAIL'}] oracle name-only rejected"); ok &= c4
    # 5 accounting branch asymmetry candidate
    body5 = "if (full) { collateral -= amt; ercDebt -= d; } else { collateral -= amt; }"
    r5 = extract_all(_b("settle", body5, downstream=["liquidate"], mut=""))
    ac = [c for c in r5["candidates"] if c["extractor"]=="accounting_condition_mismatch"]
    c5 = bool(ac) and ac[0]["mismatch"]["support_level"]=="medium"
    print(f"  [{'PASS' if c5 else 'FAIL'}] accounting branch asymmetry candidate ({ac[0]['field_or_value']['name'] if ac else None})"); ok &= c5
    # 6 logging/access-control branch diff rejected
    body6 = "if (x) { debt -= d; } else { emit Skipped(); }"
    r6 = extract_all(_b("upd", body6, downstream=["liquidate"]))
    c6 = any("access/pause/event" in x["reject_reason"] for x in r6["rejected"]) or not [c for c in r6["candidates"] if c["extractor"]=="accounting_condition_mismatch"]
    print(f"  [{'PASS' if c6 else 'FAIL'}] logging/access branch diff rejected"); ok &= c6
    # 7 downstream value-use required: a value-bearing decoded field WITH downstream is EMITTED with exact evidence,
    # but a MEDIUM self-contained candidate ABSTAINS at the advance bar (conservative — needs STRONG to advance).
    r7 = extract_all(_b("readAmt", "uint88 amount = uint88(abi.decode(data,(uint256)));", downstream=["liquidate"]))
    bc = [c for c in r7["candidates"] if c["extractor"] == "bytes_offset_decode_mismatch"]
    surv = resolve(bc[0], {"name": "readAmt", "snippet": "uint88 amount = uint88(abi.decode(data,(uint256)));"}, []) if bc else {"survive": True}
    c7 = bool(bc) and bool(bc[0]["downstream_uses"]) and not surv["survive"]
    print(f"  [{'PASS' if c7 else 'FAIL'}] bytes candidate EMITTED w/ downstream but MEDIUM self-contained ABSTAINS ({surv.get('reason')})"); ok &= c7
    # 8 un-wired markers present (the actual no-wiring grep runs in run_p36/freeze, not here)
    c8 = (FLAGS["research_only"] is True and FLAGS["is_gate"] is False
          and FLAGS["routes_in_production"] is False and _cfg().get("research_only") is True)
    print(f"  [{'PASS' if c8 else 'FAIL'}] research-only / un-wired markers set on module + config"); ok &= c8
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by run_p36)")


if __name__ == "__main__":
    raise SystemExit(main())
