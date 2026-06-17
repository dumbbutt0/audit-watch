#!/usr/bin/env python3
"""
bytes_layout_comparand.py — Phase-37 RESEARCH-ONLY producer/consumer bytes-layout comparand discovery (un-wired).

A P36 bytes_offset_decode_mismatch candidate stays WEAK without a PRODUCER (encode/pack-site) layout to compare the
CONSUMER (decode-site) layout against. This module discovers that producer↔consumer relationship from GENERIC source
patterns (never name-only), extracts both field layouts, and reports a concrete layout_mismatch. A candidate may reach
STRONG only when BOTH layouts are concretely extracted AND they conflict. Generic Solidity vocab only — no subject names.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: bytes_layout_comparand.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "bytes_layout_comparand.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # extract_features / strip_comments  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _strip(s: str) -> str:
    return sfp.strip_comments(s or "")


def _balanced(s: str, open_idx: int) -> str:
    depth, i = 0, open_idx
    while i < len(s):
        if s[i] == "(":
            depth += 1
        elif s[i] == ")":
            depth -= 1
            if depth == 0:
                return s[open_idx + 1:i]
        i += 1
    return s[open_idx + 1:]


def _split_top(s: str) -> list:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def _width(t: str):
    return _cfg()["abi_type_width"].get(t.strip().split()[0] if t.strip() else "", None)


# ----- consumer (decode-site) layout -----

def consumer_layout(body: str) -> tuple[list, str]:
    b = _strip(body)
    cp = _cfg()["consumer_patterns"]
    # abi.decode(x, (T1,T2,...))
    m = re.search(r"abi\.decode\s*\(", b)
    if m:
        args = _balanced(b, m.end() - 1)
        parts = _split_top(args)
        if len(parts) >= 2 and parts[-1].startswith("("):
            types = _split_top(parts[-1].strip("()"))
            off, layout = 0, []
            for i, t in enumerate(types):
                w = _width(t)
                layout.append({"field_name": f"f{i}", "type": t.strip(), "width_bytes": w, "offset": off, "source_lines": "abi.decode"})
                off = (off + w) if (w and off is not None) else None
            return layout, "abi_decode"
    # assembly mload(add(ptr, N)) offsets
    offs = re.findall(r"mload\s*\(\s*add\s*\([^,]+,\s*(0x[0-9a-fA-F]+|\d+)\s*\)", b)
    if offs:
        layout = [{"field_name": f"f{i}", "type": None, "width_bytes": None, "offset": int(o, 0), "source_lines": "mload(add)"}
                  for i, o in enumerate(offs)]
        return layout, "assembly_mload"
    # slice(start,len)
    sl = re.findall(r"\.slice\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", b)
    if sl:
        return [{"field_name": f"f{i}", "type": None, "width_bytes": int(L), "offset": int(s0), "source_lines": "slice"}
                for i, (s0, L) in enumerate(sl)], "slice"
    # shift extracts
    sh = re.findall(r">>\s*(\d+)", b)
    if sh:
        return [{"field_name": f"f{i}", "type": None, "width_bytes": None, "offset": int(s0) // 8, "source_lines": "shift"}
                for i, s0 in enumerate(sh)], "shift_mask"
    return [], "none"


# ----- producer (encode-site) layout -----

def producer_layout(body: str) -> tuple[list, str]:
    b = _strip(body)
    m = re.search(r"abi\.encodePacked\s*\(", b)
    pat = "abi_encodePacked"
    if not m:
        m = re.search(r"abi\.encode\s*\(", b); pat = "abi_encode"
    if not m:
        m = re.search(r"bytes\.concat\s*\(", b); pat = "bytes_concat"
    if m:
        args = _split_top(_balanced(b, m.end() - 1))
        off, layout = 0, []
        for i, a in enumerate(args):
            cm = re.match(r"(uint\d+|address|bool|bytes32)\s*\(", a)
            t = cm.group(1) if cm else None
            w = _width(t) if t else None
            layout.append({"field_name": re.sub(r"^\w+\(|\)$", "", a)[:24] or f"a{i}", "type": t,
                           "width_bytes": w, "offset": off if pat == "abi_encodePacked" else None, "source_lines": pat})
            off = (off + w) if (w and off is not None and pat == "abi_encodePacked") else (None if pat == "abi_encodePacked" else off)
        return layout, pat
    # assembly mstore(add(ptr, N), v)
    offs = re.findall(r"mstore\s*\(\s*add\s*\([^,]+,\s*(0x[0-9a-fA-F]+|\d+)\s*\)", b)
    if offs:
        return [{"field_name": f"a{i}", "type": None, "width_bytes": None, "offset": int(o, 0), "source_lines": "mstore(add)"}
                for i, o in enumerate(offs)], "assembly_mstore"
    return [], "none"


# ----- relationship discovery (NOT name-only) -----

def _stems(text: str) -> set:
    return {w.lower() for w in re.findall(r"[A-Za-z_]\w{3,}", text or "")}


def _bytes_vars(text: str) -> set:
    return {m.lower() for m in re.findall(r"\bbytes\s+(?:memory|calldata|storage)?\s*([A-Za-z_]\w+)", text or "")}


def relationship(consumer: dict, producer: dict, prod_layout: list, cons_layout: list) -> list:
    """Generic producer/consumer link evidence. NOT name-only: a real comparand needs >=1 strong structural signal
    (caller<->callee or a shared struct/type) OR >=2 weak signals (shared payload stem / domain word / field count).
    'Both touch bytes' is deliberately NOT a signal — it is true of every encode/decode pair."""
    c = _cfg()["relationship"]
    cb, pb = _strip(consumer.get("body", "")), _strip(producer.get("body", ""))
    cf = {x.lower() for x in sfp.extract_features(consumer.get("name", ""), snippet=cb)["calls"]}
    pf = {x.lower() for x in sfp.extract_features(producer.get("name", ""), snippet=pb)["calls"]}
    ev = []
    # strong
    if producer.get("name", "").lower() in cf or consumer.get("name", "").lower() in pf:
        ev.append({"kind": "caller_callee", "detail": "one function calls the other"})
    structs_c = set(re.findall(r"\b([A-Z]\w+)\s+(?:memory|storage|calldata)\b", consumer.get("signature", "") + cb))
    structs_p = set(re.findall(r"\b([A-Z]\w+)\s+(?:memory|storage|calldata)\b", producer.get("signature", "") + pb))
    if structs_c & structs_p:
        ev.append({"kind": "shared_struct", "detail": f"shared struct/type {sorted(structs_c & structs_p)[:2]}"})
    # weak
    shared_stem = _bytes_vars(consumer.get("signature", "") + cb) & _bytes_vars(producer.get("signature", "") + pb)
    if shared_stem:
        ev.append({"kind": "shared_stem", "detail": f"shared bytes payload var {sorted(shared_stem)[:2]}"})
    dom = [w for w in c["domain_words"] if w in cb.lower() and w in pb.lower()]
    if dom:
        ev.append({"kind": "domain_word", "detail": f"shared domain words {dom[:3]}"})
    if prod_layout and cons_layout and len(prod_layout) == len(cons_layout):
        ev.append({"kind": "field_count", "detail": f"both layouts have {len(prod_layout)} fields"})
    return ev


def _rel_ok(ev: list) -> bool:
    c = _cfg()["relationship"]
    strong = sum(1 for e in ev if e["kind"] in c["strong_signals"])
    weak = sum(1 for e in ev if e["kind"] in c["weak_signals"])
    return strong >= c["min_strong"] or weak >= c["min_weak"]


# ----- mismatch -----

def layout_mismatch(prod: list, cons: list) -> dict:
    if not prod or not cons:
        return {"kind": "none", "description": "a layout could not be extracted", "support_level": "weak"}
    if len(prod) != len(cons):
        return {"kind": "field_count", "description": f"producer packs {len(prod)} fields, consumer reads {len(cons)}",
                "support_level": "strong"}
    # offset conflict where both numeric
    for i, (p, c) in enumerate(zip(prod, cons)):
        if p["offset"] is not None and c["offset"] is not None and p["offset"] != c["offset"]:
            return {"kind": "offset", "description": f"field {i}: producer offset {p['offset']} != consumer offset {c['offset']}",
                    "support_level": "strong"}
    for i, (p, c) in enumerate(zip(prod, cons)):
        if p["width_bytes"] and c["width_bytes"] and p["width_bytes"] != c["width_bytes"]:
            return {"kind": "width", "description": f"field {i}: producer width {p['width_bytes']} != consumer width {c['width_bytes']}",
                    "support_level": "strong"}
        if p["type"] and c["type"] and p["type"] != c["type"]:
            return {"kind": "type", "description": f"field {i}: producer type {p['type']} != consumer type {c['type']}",
                    "support_level": "strong"}
    return {"kind": "none", "description": "producer and consumer layouts are consistent", "support_level": "none"}


def discover(consumer: dict, all_functions: list) -> dict | None:
    cons_layout, dec = consumer_layout(consumer.get("body", ""))
    if dec == "none":
        return None  # not actually a bytes consumer
    best = None
    for p in all_functions:
        if p.get("name") == consumer.get("name"):
            continue
        prod_layout, enc = producer_layout(p.get("body", ""))
        if enc == "none":
            continue
        ev = relationship(consumer, p, prod_layout, cons_layout)
        if not _rel_ok(ev):
            continue
        mm = layout_mismatch(prod_layout, cons_layout)
        score = (3 if mm["support_level"] == "strong" else 1) + len(ev)
        cand = {**FLAGS, "comparand_id": f"{p.get('name')}->{consumer.get('name')}",
                "consumer": {"file": consumer.get("file"), "function": consumer.get("name"),
                             "lines": consumer.get("lines"), "payload_name": consumer.get("payload", ""), "decode_pattern": dec},
                "producer": {"file": p.get("file"), "function": p.get("name"), "lines": p.get("lines"),
                             "payload_name": p.get("payload", ""), "encode_pattern": enc},
                "relationship_evidence": ev, "producer_layout": prod_layout, "consumer_layout": cons_layout,
                "layout_mismatch": mm, "downstream_value_use": [], "reject_if": []}
        if best is None or score > best[0]:
            best = (score, cand)
    return best[1] if best else None


def is_strong(comparand: dict | None) -> bool:
    """STRONG layout proof: both layouts concretely extracted AND a concrete conflict."""
    if not comparand:
        return False
    return (bool(comparand["producer_layout"]) and bool(comparand["consumer_layout"])
            and comparand["layout_mismatch"]["kind"] != "none"
            and comparand["layout_mismatch"]["support_level"] == "strong")


# --------------------------------- self-test (8 required cases) ---------------------------------

def _fn(name, body, sig="", file="X.sol"):
    return {"name": name, "body": body, "signature": sig, "file": file, "lines": "1-9"}


def _self_test():
    ok = True
    # 1 abi.encode producer -> abi.decode consumer, MATCHING layout -> mismatch none (abstain)
    prod = _fn("packOrder", "return abi.encode(amount, recipient);", "function packOrder(Order memory o) returns (bytes memory)")
    cons = _fn("readOrder", "(uint256 amount, address recipient) = abi.decode(orderData, (uint256, address));",
               "function readOrder(bytes memory orderData, Order memory o)")
    cmp1 = discover(cons, [prod])
    c1 = cmp1 and cmp1["layout_mismatch"]["kind"] == "none" and not is_strong(cmp1)
    print(f"  [{'PASS' if c1 else 'FAIL'}] encode->decode matching layout -> no mismatch ({cmp1['layout_mismatch']['kind'] if cmp1 else None})"); ok &= c1
    # 2 encodePacked producer -> mload consumer, FIELD COUNT mismatch -> strong
    prod2 = _fn("packShort", "return abi.encodePacked(uint88(collateral), uint88(ercDebt), uint88(price));",
                "function packShort(Short memory s) returns (bytes memory)")
    cons2 = _fn("readShort", "x := mload(add(shortData, 0x20)); y := mload(add(shortData, 0x40));",
                "function readShort(bytes memory shortData, Short memory s)")
    cmp2 = discover(cons2, [prod2])
    c2 = cmp2 and cmp2["layout_mismatch"]["kind"] in ("field_count", "offset", "width") and cmp2["layout_mismatch"]["support_level"] == "strong"
    print(f"  [{'PASS' if c2 else 'FAIL'}] encodePacked->mload layout mismatch -> strong ({cmp2['layout_mismatch']['kind'] if cmp2 else None})"); ok &= c2
    # 3 name-only relation rejected (no shared struct/return/caller, only 1 weak domain word)
    prodN = _fn("buildThing", "return abi.encode(a, b);", "function buildThing() returns (bytes memory)")
    consN = _fn("parseOther", "(uint256 a, uint256 b) = abi.decode(blob, (uint256, uint256));", "function parseOther(bytes memory blob)")
    cmp3 = discover(consN, [prodN])
    c3 = cmp3 is None  # no relationship signal meets threshold (no caller/return-bytes-arg/struct; <2 weak)
    print(f"  [{'PASS' if c3 else 'FAIL'}] name-only / no-relationship -> no comparand ({cmp3 is None})"); ok &= c3
    # 4 bare cast only -> not a consumer (no decode pattern)
    cmp4 = discover(_fn("toU88", "return uint88(x);"), [prod2])
    c4 = cmp4 is None
    print(f"  [{'PASS' if c4 else 'FAIL'}] bare cast -> not a bytes consumer ({cmp4 is None})"); ok &= c4
    # 5 missing downstream is enforced at integration; here verify is_strong is False when no mismatch
    c5 = not is_strong(cmp1)
    print(f"  [{'PASS' if c5 else 'FAIL'}] consistent layout not strong"); ok &= c5
    # 6 concrete offset mismatch reaches strong (matching field count, conflicting numeric offsets)
    prod6 = _fn("packA", "mstore(add(p, 0x20), col); mstore(add(p, 0x40), debt);", "function packA() returns (bytes memory)",)
    cons6 = _fn("readA", "c := mload(add(p, 0x20)); d := mload(add(p, 0x60));", "function readA(bytes memory p)")
    # add a structural relationship: shared struct in signatures
    prod6["signature"] += " Order memory o"; cons6["signature"] += " Order memory o"
    cmp6 = discover(cons6, [prod6])
    c6 = cmp6 and cmp6["layout_mismatch"]["kind"] == "offset" and is_strong(cmp6)
    print(f"  [{'PASS' if c6 else 'FAIL'}] concrete offset mismatch -> strong ({cmp6['layout_mismatch'] if cmp6 else None})"); ok &= c6
    # 7 consistent layout abstains (offsets equal)
    cons7 = _fn("readB", "c := mload(add(p, 0x20)); d := mload(add(p, 0x40));", "function readB(bytes memory p) Order memory o")
    prod7 = _fn("packB", "mstore(add(p, 0x20), col); mstore(add(p, 0x40), debt);", "function packB() returns (bytes memory) Order memory o")
    cmp7 = discover(cons7, [prod7])
    c7 = cmp7 and cmp7["layout_mismatch"]["kind"] == "none" and not is_strong(cmp7)
    print(f"  [{'PASS' if c7 else 'FAIL'}] consistent offsets -> abstain ({cmp7['layout_mismatch']['kind'] if cmp7 else None})"); ok &= c7
    # 8 un-wired markers
    c8 = FLAGS["research_only"] is True and FLAGS["is_gate"] is False and _cfg().get("research_only") is True
    print(f"  [{'PASS' if c8 else 'FAIL'}] research-only / un-wired markers"); ok &= c8
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by run_p37)")


if __name__ == "__main__":
    raise SystemExit(main())
