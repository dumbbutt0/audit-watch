#!/usr/bin/env python3
"""
packed_field_mask_opcode_lens.py — Phase-40 RESEARCH-ONLY packed-field mask-opcode anomaly lens (un-wired).

Detects the mechanism shape P39 exposed: a field extracted via `shr`/`shl`/slice that is then combined with a MASK
constant using `add`/`or`/`xor` (or infix `+`/`|`/`^`) where `and` (masking) is the required idiom. High-precision:
a candidate is emitted only with an exact packed extraction + a mask-like constant + an operator mismatch + a
downstream value/authority role + >=1 source corroborator; it SURVIVES (STRONG) only with all of those AND no
source-backed justification. NOT a generic 'suspicious bitwise math' detector. Generic Solidity vocab only — no
subject identifiers.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: packed_field_mask_opcode_lens.py --self-test
"""
from __future__ import annotations
import argparse, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "packed_field_mask_opcode_lens.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # strip_comments  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _balanced(s: str, popen: int):
    depth, i = 0, popen
    while i < len(s):
        if s[i] == "(":
            depth += 1
        elif s[i] == ")":
            depth -= 1
            if depth == 0:
                return s[popen + 1:i], i
        i += 1
    return s[popen + 1:], len(s)


def _split_top(s: str):
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


def _is_contiguous_low(v: int) -> bool:
    return v > 0 and (v & (v + 1)) == 0  # 0b111... form


def _mask_info(arg: str):
    """Return (is_mask, literal, value, width_bits, contiguous) for a mask-like arg, else None."""
    c = _cfg()
    a = arg.strip()
    m = re.search(r"0x[0-9a-fA-F]+", a)
    if m and re.fullmatch(r"0x[fF]{2,}", m.group(0)):
        v = int(m.group(0), 16)
        return {"literal": m.group(0), "value": v, "width_bits": v.bit_length(), "is_contiguous_low_bits": _is_contiguous_low(v)}
    if re.search(c["mask_width_minus_one_re"], a):
        return {"literal": a[:32], "value": None, "width_bits": None, "is_contiguous_low_bits": True}
    if any(t in a.lower() for t in c["mask_name_tokens"]) and not re.search(r"\bshr|shl\b", a):
        return {"literal": a[:32], "value": None, "width_bits": None, "is_contiguous_low_bits": True}
    return None


def _has_extract(arg: str) -> bool:
    return bool(re.search(r"\b(shr|shl)\s*\(", arg) or re.search(r">>|<<", arg))


def _role_of(name: str) -> str:
    roles = _cfg()["value_authority_roles"]
    nl = (name or "").lower()
    for role, toks in roles.items():
        if any(t in nl for t in toks):
            return role
    return "unknown"


def _lhs_before(body: str, idx: int) -> str:
    """The assignment target ('x :=' / 'x =' / 'let x :=') immediately preceding position idx, if any."""
    pre = body[:idx]
    m = re.search(r"(?:let\s+)?([A-Za-z_]\w*)\s*:?=\s*$", pre.rstrip()[-80:].split("\n")[-1])
    return m.group(1) if m else ""


def detect_in_function(name: str, body_raw: str, file: str = "", lines: str = "") -> list:
    c = _cfg()
    raw = body_raw or ""
    body = sfp.strip_comments(raw)
    cands = []
    # nearby 'and(...mask...)' anywhere in the function => masking was intended elsewhere (corroborator)
    has_and_mask = bool(re.search(r"\band\s*\(", body) and re.search(c["mask_literal_re"], body))
    comment_corrob = [t for t in c["corroborator_comment_tokens"] if t in raw.lower()]
    intentional = any(mk in raw.lower() for mk in c["intentional_bitset_markers"])

    seen = set()
    for op in c["suspicious_ops_asm"]:
        for m in re.finditer(r"\b" + op + r"\s*\(", body):
            content, end = _balanced(body, m.end() - 1)
            args = _split_top(content)
            if len(args) != 2:
                continue
            mask = next((_mask_info(a) for a in args if _mask_info(a)), None)
            shift_arg = next((a for a in args if _has_extract(a)), None)
            if not mask or not shift_arg:
                continue
            lhs = _lhs_before(body, m.start())
            role = _role_of(lhs) if lhs else "unknown"
            key = (op, content[:40])
            if key in seen:
                continue
            seen.add(key)
            corrob = []
            if comment_corrob:
                corrob.append({"kind": "comment_mask_language", "evidence": comment_corrob[:3]})
            if has_and_mask:
                corrob.append({"kind": "sibling_and_mask", "evidence": "an and(.., mask) masking appears elsewhere in this function"})
            if lhs and re.search(r"\buint(8|16|24|32|40|48|56|64|72|80|88|96|104|112|120|128|160)\b[^;]*\b" + re.escape(lhs) + r"\b", raw):
                corrob.append({"kind": "downcast_width", "evidence": f"'{lhs}' is a narrow uintN field"})
            if not mask["is_contiguous_low_bits"] and not corrob:
                continue  # non-contiguous mask with no corroborator -> not a field mask
            cand = {**FLAGS, "candidate_id": f"mask_opcode:{name}:{op}",
                    "target": {"file": file, "function": name, "lines": lines},
                    "mechanism_class": "packed_field_mask_opcode_anomaly",
                    "packed_expression": f"{op}({content.strip()[:80]})", "extracted_field": lhs or "(unnamed)",
                    "suspicious_operator": op,
                    "mask_constant": {"literal": mask["literal"], "value": mask["value"],
                                      "width_bits": mask["width_bits"], "is_contiguous_low_bits": mask["is_contiguous_low_bits"]},
                    "corroborators": corrob, "downstream_uses": ([{"file": file, "function": name, "lines": lines,
                                       "semantic_role": role, "use": "accounting_update" if role != "unknown" else "other"}] if role != "unknown" else []),
                    "mismatch": {"kind": "mask_operator_mismatch",
                                 "description": f"field extracted via shift is combined with a mask constant using '{op}' instead of 'and'",
                                 "support_level": "LOW"}, "reject_if": [], "decision": "ABSTAIN", "decision_reason": ""}
            # survival bar (STRONG): operator mismatch + mask-like + downstream role + >=1 corroborator + not intentional bit-set
            if intentional:
                cand["decision_reason"] = "intentional bit-setting context (flag/compose) — not a masking error"
            elif not corrob:
                cand["decision_reason"] = "no source corroborator that masking was intended"
            elif role == "unknown":
                cand["decision_reason"] = "no downstream value/authority role for the extracted field"
            else:
                cand["mismatch"]["support_level"] = "STRONG"
                cand["decision"] = "SURVIVE"
                cand["decision_reason"] = "shift-extracted value combined with a contiguous mask via wrong combinator; corroborated; value-bearing"
            cands.append(cand)
    return cands


def run_on_sources(functions: list) -> list:
    """functions: [{name, body, file, lines}] -> all candidates."""
    out = []
    for f in functions:
        out.extend(detect_in_function(f.get("name", ""), f.get("body", ""), f.get("file", ""), f.get("lines", "")))
    return out


# --------------------------------- self-test (11 required cases) ---------------------------------

def _c(name, body):
    return detect_in_function(name, body, "X.sol", "1-9")


def _self_test():
    ok = True
    # 1 add(mask, shr(...)) + mask-language comment + value role -> STRONG SURVIVE
    s1 = "uint88 colRedeemed; // mask of bytes11 = 0xff * 11\n colRedeemed := add(0xffffffffffffffffffffff, shr(80, fullWord))"
    r1 = _c("readRec", s1)
    c1 = r1 and r1[0]["decision"] == "SURVIVE" and r1[0]["mismatch"]["support_level"] == "STRONG"
    print(f"  [{'PASS' if c1 else 'FAIL'}] add(mask,shr)+comment+value -> STRONG SURVIVE ({r1[0]['decision'] if r1 else None})"); ok &= c1
    # 2 or(extracted, mask) intentional bit-set -> abstain
    s2 = "// set flag bit\n packed := or(shr(8, word), 0xff)"
    r2 = _c("setFlag", s2)
    c2 = all(x["decision"] == "ABSTAIN" for x in r2)
    print(f"  [{'PASS' if c2 else 'FAIL'}] intentional bit-set -> abstain"); ok &= c2
    # 3 and(shr(...), mask) correct masking -> no candidate (and is not a suspicious op)
    r3 = _c("good", "amount := and(shr(80, word), 0xffffffffffffffffffffff)")
    c3 = r3 == []
    print(f"  [{'PASS' if c3 else 'FAIL'}] and(shr,mask) correct -> no candidate"); ok &= c3
    # 4 plain arithmetic, no packed extraction -> no candidate
    r4 = _c("calc", "total := add(fee, amount)")
    c4 = r4 == []
    print(f"  [{'PASS' if c4 else 'FAIL'}] plain arithmetic -> no candidate"); ok &= c4
    # 5 contiguous low-bit mask recognized
    mi = _mask_info("0xffffff")
    c5 = mi and mi["is_contiguous_low_bits"]
    print(f"  [{'PASS' if c5 else 'FAIL'}] contiguous low-bit mask recognized"); ok &= c5
    # 6 non-contiguous constant not treated as mask unless corroborated (no comment, no and-mask) -> abstain/no candidate
    r6 = _c("f6", "uint64 x; x := add(0xff00, shr(8, word))")  # 0xff00 non-contiguous, no corroborator
    c6 = all(x["decision"] == "ABSTAIN" for x in r6) and not any(x["decision"] == "SURVIVE" for x in r6)
    print(f"  [{'PASS' if c6 else 'FAIL'}] non-contiguous mask, no corroborator -> not survive"); ok &= c6
    # 7 named MASK constant treated as mask
    mi7 = _mask_info("FIELD_MASK")
    c7 = mi7 is not None
    print(f"  [{'PASS' if c7 else 'FAIL'}] named MASK constant recognized"); ok &= c7
    # 8 downstream value role required: same as #1 but field name has no value role -> abstain
    s8 = "uint256 tmp; // mask bytes11\n tmp := add(0xffffffffffffffffffffff, shr(80, word))"
    r8 = _c("f8", s8)
    c8 = r8 and r8[0]["decision"] == "ABSTAIN" and "value/authority role" in r8[0]["decision_reason"]
    print(f"  [{'PASS' if c8 else 'FAIL'}] no value role -> abstain ({r8[0]['decision_reason'] if r8 else None})"); ok &= c8
    # 9 comment-only issue (no suspicious code op) -> no candidate
    r9 = _c("f9", "// TODO: should mask with and here\n amount := shr(80, word)")
    c9 = r9 == []
    print(f"  [{'PASS' if c9 else 'FAIL'}] comment-only, no suspicious op -> no candidate"); ok &= c9
    # 10 no subject identifiers in the CONFIG (pure data — where hardcoding would matter; the module's only
    # occurrences are these self-test assertion literals, so scanning the module would be self-referential)
    cfgsrc = CFG.read_text().lower()
    c10 = not any(t in cfgsrc for t in ("dittoeth", "readproposaldata", "libbytes", "basin", "proposal", "slate"))
    print(f"  [{'PASS' if c10 else 'FAIL'}] no subject identifiers in config"); ok &= c10
    # 11 un-wired markers
    c11 = FLAGS["research_only"] is True and FLAGS["is_gate"] is False and _cfg().get("research_only") is True
    print(f"  [{'PASS' if c11 else 'FAIL'}] research-only / un-wired markers"); ok &= c11
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ap.error("--self-test only (module is a library used by run_p40)")


if __name__ == "__main__":
    raise SystemExit(main())
