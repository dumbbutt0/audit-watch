#!/usr/bin/env python3
"""
constant_offset_resolver.py — Phase-38 RESEARCH-ONLY named-constant offset resolution (un-wired).

P37's bytes consumer-layout extractor only read NUMERIC offsets; real decoders use NAMED constants
(`mload(add(ptr, FIELD_OFFSET))`). This module resolves Solidity layout constants + constant arithmetic from source so
the consumer layout can be extracted when offsets are named. Resolution ENABLES layout extraction only — it never
lowers the STRONG survival bar (that stays in P36/P37). If a constant cannot be resolved, the offset stays unresolved
and the consumer abstains. Generic Solidity vocab only — no subject names.

is_gate:false research_only:true routes_in_production:false routed_manifest_ids:[].
Usage: constant_offset_resolver.py --self-test
"""
from __future__ import annotations
import argparse, ast, json, re, sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "constant_offset_resolver.json"
sys.path.insert(0, str(ROOT / "scripts"))
import sibling_function_parity_taxonomy as sfp  # strip_comments  # noqa: E402
import bytes_layout_comparand as BLC  # reuse P37 numeric consumer_layout (unchanged)  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


# ---- safe arithmetic evaluator (whitelist; mirrors scripts/math_formula_diff_harness.py) ----

def resolve_expr(expr: str, env: dict):
    e = (expr or "").strip()
    low = e.lower()
    if any(tok in low for tok in _cfg()["runtime_reject_tokens"]):
        return None
    try:
        tree = ast.parse(e, mode="eval")
    except SyntaxError:
        return None
    return _eval(tree.body, env)


def _eval(n, env):
    if isinstance(n, ast.Constant):
        return n.value if isinstance(n.value, int) and not isinstance(n.value, bool) else None
    if isinstance(n, ast.Name):
        return env.get(n.id)
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
        v = _eval(n.operand, env)
        if v is None:
            return None
        return -v if isinstance(n.op, ast.USub) else v
    if isinstance(n, ast.BinOp):
        a, b = _eval(n.left, env), _eval(n.right, env)
        if a is None or b is None:
            return None
        if isinstance(n.op, ast.Add):
            return a + b
        if isinstance(n.op, ast.Sub):
            return a - b
        if isinstance(n.op, ast.Mult):
            return a * b
        if isinstance(n.op, (ast.Div, ast.FloorDiv)):
            return a // b if (b != 0 and a % b == 0) else None  # exact division only
        return None
    return None


# ---- constant collection (generic decl scan + fixpoint resolution) ----

def collect_constants(sources: list[str]) -> tuple[dict, dict]:
    decl = re.compile(_cfg()["constant_decl_re"])
    raw: dict[str, set] = {}
    for src in sources:
        for m in decl.finditer(sfp.strip_comments(src or "")):
            raw.setdefault(m.group(1), set()).add(m.group(2).strip())
    env, entries = {}, {}
    changed = True
    while changed:
        changed = False
        for name, exprs in raw.items():
            if name in env or name in entries:
                continue
            vals = {v for ex in exprs if (v := resolve_expr(ex, env)) is not None}
            if len(vals) == 1 and len(exprs) == 1:
                env[name] = next(iter(vals)); changed = True
            elif len(vals) > 1:
                entries[name] = {**FLAGS, "name": name, "value": None,
                                 "reject_reason": f"ambiguous conflicting constant values {sorted(vals)}",
                                 "confidence": "LOW"}
            elif len(vals) == 1 and len(exprs) > 1:
                # same name declared twice; conflicting only if the OTHER expr resolves differently
                if all(resolve_expr(ex, env) in (None, next(iter(vals))) for ex in exprs):
                    env[name] = next(iter(vals)); changed = True
                else:
                    entries[name] = {**FLAGS, "name": name, "value": None,
                                     "reject_reason": "ambiguous duplicate constant", "confidence": "LOW"}
    for name, exprs in raw.items():
        if name in env:
            entries[name] = {**FLAGS, "constant_id": name, "name": name, "value": env[name],
                             "value_hex": hex(env[name]), "unit": _unit(name), "expr": sorted(exprs)[0],
                             "confidence": "HIGH", "reject_reason": None}
        elif name not in entries:
            entries[name] = {**FLAGS, "name": name, "value": None,
                             "reject_reason": "unresolved (runtime/non-constant/non-integer)", "confidence": "LOW"}
    return env, entries


def _unit(name: str) -> str:
    nl = name.lower()
    for unit, hints in _cfg()["unit_hints"].items():
        if any(h in nl for h in hints):
            return unit
    return "bytes"


# ---- constant-aware consumer layout (falls back to P37 numeric extractor) ----

def _balanced_from(s: str, paren_open: int) -> tuple[str, int]:
    depth, i = 0, paren_open
    while i < len(s):
        if s[i] == "(":
            depth += 1
        elif s[i] == ")":
            depth -= 1
            if depth == 0:
                return s[paren_open + 1:i], i
        i += 1
    return s[paren_open + 1:], len(s)


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


def _offset_of_add(content: str, env: dict) -> tuple[int | None, list]:
    """Sum resolvable constant/numeric terms in an add(...) expression; the pointer base contributes 0.
    Returns (offset|None, symbols). offset is None when NO constant/numeric term resolves."""
    parts = _split_top(content)
    total, syms, any_resolved = 0, [], False
    for t in parts:
        ts = t.strip()
        am = re.match(r"add\s*\(", ts)
        if am:
            inner, _ = _balanced_from(ts, am.end() - 1)
            v, s = _offset_of_add(inner, env)
            if v is not None:
                total += v; syms += s; any_resolved = True
            continue
        v = resolve_expr(ts, env)
        if v is not None:
            total += v; any_resolved = True
            syms += [w for w in re.findall(r"[A-Za-z_]\w*", ts) if w in env]
    return (total if any_resolved else None), syms


def consumer_layout_with_constants(body: str, env: dict) -> tuple[list, str]:
    # 1) P37 numeric path (abi.decode type tuple + numeric mload/slice/shift) — unchanged behavior
    layout, pat = BLC.consumer_layout(body)
    if layout:
        for f in layout:
            f.setdefault("offset_source", "numeric")
        return layout, pat
    b = sfp.strip_comments(body or "")
    fields = []
    # 2) mload(add(...)) with named-constant offsets
    for m in re.finditer(r"mload\s*\(\s*add\s*\(", b):
        add_open = b.index("(", m.start() + len("mload"))
        content, _ = _balanced_from(b, add_open)
        off, syms = _offset_of_add(content, env)
        if off is not None and syms:  # require >=1 resolved CONSTANT symbol (not pure pointer)
            fields.append({"field_name": f"f{len(fields)}", "type": None, "width_bytes": None, "offset": off,
                           "offset_source": "named_constant", "offset_symbol": syms[0],
                           "offset_resolution": {"expression": content.strip()[:60], "value": off, "source_lines": "mload(add)"},
                           "source_lines": "mload(add)"})
    if fields:
        return fields, "assembly_mload_const"
    # 3) slice(START, LEN) with constants
    for m in re.finditer(r"\.?slice\s*\(", b):
        content, _ = _balanced_from(b, b.index("(", m.start()))
        args = _split_top(content)
        cand = args[-2:] if len(args) >= 2 else []
        if len(cand) == 2:
            o, L = resolve_expr(cand[0], env), resolve_expr(cand[1], env)
            if o is not None and (re.search(r"[A-Za-z_]", cand[0]) or re.search(r"[A-Za-z_]", cand[1])):
                fields.append({"field_name": f"f{len(fields)}", "type": None, "width_bytes": L, "offset": o,
                               "offset_source": "named_constant", "offset_symbol": cand[0],
                               "offset_resolution": {"expression": f"{cand[0]},{cand[1]}", "value": o, "source_lines": "slice"},
                               "source_lines": "slice"})
    if fields:
        return fields, "slice_const"
    # 4) shift by named constant
    for m in re.finditer(r">>\s*([A-Za-z_]\w*)", b):
        v = resolve_expr(m.group(1), env)
        if v is not None:
            fields.append({"field_name": f"f{len(fields)}", "type": None, "width_bytes": None, "offset": v // 8,
                           "offset_source": "named_constant", "offset_symbol": m.group(1),
                           "offset_resolution": {"expression": m.group(1), "value": v, "source_lines": "shift"},
                           "source_lines": "shift"})
    return (fields, "shift_const") if fields else ([], "none")


# --------------------------------- self-test (11 required cases) ---------------------------------

def _self_test():
    ok = True
    env, ent = collect_constants(["uint256 constant OFF = 32;"])
    c1 = env.get("OFF") == 32
    print(f"  [{'PASS' if c1 else 'FAIL'}] decimal constant -> {env.get('OFF')}"); ok &= c1
    env2, _ = collect_constants(["uint256 private constant OFF = 0x20;"])
    c2 = env2.get("OFF") == 32
    print(f"  [{'PASS' if c2 else 'FAIL'}] hex constant -> {env2.get('OFF')}"); ok &= c2
    env3, _ = collect_constants(["uint256 constant A = 32;", "uint256 constant B = A + 32;"])
    c3 = env3.get("B") == 64
    print(f"  [{'PASS' if c3 else 'FAIL'}] arithmetic expr -> B={env3.get('B')}"); ok &= c3
    env4, _ = collect_constants(["uint256 constant X = 32;", "uint256 constant Y = X;"])
    c4 = env4.get("Y") == 32
    print(f"  [{'PASS' if c4 else 'FAIL'}] alias -> Y={env4.get('Y')}"); ok &= c4
    env5, ent5 = collect_constants(["uint256 constant DUP = 32;", "uint256 constant DUP = 64;"])
    c5 = "DUP" not in env5 and ent5.get("DUP", {}).get("reject_reason", "").startswith("ambiguous")
    print(f"  [{'PASS' if c5 else 'FAIL'}] ambiguous conflicting -> rejected ({ent5.get('DUP',{}).get('reject_reason')})"); ok &= c5
    c6 = resolve_expr("msg.value + 32", {}) is None and resolve_expr("runtimeVar", {}) is None
    print(f"  [{'PASS' if c6 else 'FAIL'}] runtime var rejected"); ok &= c6
    env7 = {"OFF": 32}
    l7, p7 = consumer_layout_with_constants("x := mload(add(ptr, OFF));", env7)
    c7 = l7 and l7[0]["offset"] == 32 and l7[0]["offset_source"] == "named_constant"
    print(f"  [{'PASS' if c7 else 'FAIL'}] mload(add(ptr,CONST)) -> offset {l7[0]['offset'] if l7 else None}"); ok &= c7
    env8 = {"BASE": 32, "FIELD": 32}
    l8, _ = consumer_layout_with_constants("y := mload(add(add(ptr, BASE), FIELD));", env8)
    c8 = l8 and l8[0]["offset"] == 64
    print(f"  [{'PASS' if c8 else 'FAIL'}] mload(add(add(ptr,BASE),FIELD)) -> offset {l8[0]['offset'] if l8 else None}"); ok &= c8
    env9 = {"START": 4, "LEN": 32}
    l9, _ = consumer_layout_with_constants("v = data.slice(START, LEN);", env9)
    c9 = l9 and l9[0]["offset"] == 4 and l9[0]["width_bytes"] == 32
    print(f"  [{'PASS' if c9 else 'FAIL'}] slice(CONST,LEN) -> off {l9[0]['offset'] if l9 else None} w {l9[0]['width_bytes'] if l9 else None}"); ok &= c9
    l10, p10 = consumer_layout_with_constants("z := mload(add(ptr, UNRESOLVED_CONST));", {})
    c10 = l10 == [] and p10 == "none"
    print(f"  [{'PASS' if c10 else 'FAIL'}] unresolved constant -> abstain ({p10})"); ok &= c10
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
    ap.error("--self-test only (module is a library used by run_p38)")


if __name__ == "__main__":
    raise SystemExit(main())
