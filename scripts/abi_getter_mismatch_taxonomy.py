#!/usr/bin/env python3
"""
abi_getter_mismatch_taxonomy.py — pure (no-I/O) core for the cross-file interface / public-getter ABI
mismatch lens. Companion detector: abi_getter_mismatch_audit.py.

Bug shape (Hybra M-07): an interface declares e.g. `poolVote(uint) returns (address[])` while the
implementation exposes `mapping(uint256 => address[]) public poolVote`, whose Solidity auto-getter is
`poolVote(uint256, uint256) returns (address)`. Same NAME, different generated ABI/selector and return shape
— a call through the interface against the implementation address reverts or misdecodes.

This module only does string/structure work: parse a public state-variable declaration, synthesize the
getter Solidity would generate for it, parse an interface/abstract function declaration, and compare the two.
All detection of WHICH var pairs with WHICH interface (source scan, call sites, dispositions) lives in the
audit script. Keeping this layer pure makes the ABI rules unit-testable.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------- type canonicalization

_STORAGE = re.compile(r"\b(memory|calldata|storage|payable)\b")
_ALIAS = {"uint": "uint256", "int": "int256", "byte": "bytes1"}


def canon_type(t: str) -> str:
    """Canonical ABI type: strip storage/param-name noise, normalize uint→uint256, keep array suffixes."""
    t = _STORAGE.sub(" ", t or "").strip()
    # collapse internal whitespace inside e.g. "address [ ]"
    t = re.sub(r"\s+", "", t)
    # split a trailing array suffix (possibly fixed-size or multi-dim) off the base
    m = re.match(r"^([A-Za-z0-9_.]+)((?:\[[0-9]*\])*)$", t)
    if not m:
        return t
    base, arr = m.group(1), m.group(2)
    base = _ALIAS.get(base, base)
    return base + arr


def _canon_list(types: list[str]) -> list[str]:
    return [canon_type(t) for t in types if t is not None and str(t).strip()]


# ---------------------------------------------------------------- public state variable parsing

# top-level keywords that are NOT a state-variable declaration
_NON_STATEVAR = re.compile(r"\b(function|event|modifier|error|struct|enum|constructor|using|import|pragma|return)\b")
_VIS_PUBLIC = re.compile(r"\bpublic\b")
_TRAILING_KW = {"public", "override", "constant", "immutable", "virtual"}


def _split_top_arrow(inner: str) -> tuple[str, str]:
    """Split 'K => V' at the FIRST top-level '=>' (paren depth 0)."""
    depth = 0
    i = 0
    while i < len(inner) - 1:
        c = inner[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif depth == 0 and inner[i:i + 2] == "=>":
            return inner[:i].strip(), inner[i + 2:].strip()
        i += 1
    return inner.strip(), ""


def _parse_mapping(t: str) -> tuple[list[str], str, bool]:
    """mapping(K => V) → (key_types, value_base_type, value_is_array). V may itself be a mapping."""
    inner = t[t.index("(") + 1: t.rindex(")")]
    k, v = _split_top_arrow(inner)
    keys = [k.strip()]
    v = v.strip()
    if v.startswith("mapping"):
        sub_keys, val, val_arr = _parse_mapping(v)
        return keys + sub_keys, val, val_arr
    val_arr = v.endswith("[]")
    val = v[:-2].strip() if val_arr else v
    return keys, val, val_arr


def parse_public_state_var(line: str):
    """Parse a single source line into a public state-var descriptor, or None if it is not one.

    Returns {name, kind: mapping|array|scalar, key_types:[...], value_type, value_is_array, raw}.
    Only `public` declarations generate a getter; internal/private/local return None.
    """
    s = (line or "").strip()
    if "public" not in s or _NON_STATEVAR.search(s):
        return None
    s = s.split(";", 1)[0].strip()           # drop trailing ';' and anything after
    init = re.search(r"=(?![=>])", s)         # drop an initializer '=' but NOT the '=>' of a mapping
    if init:
        s = s[:init.start()].strip()
    if not _VIS_PUBLIC.search(s):
        return None
    type_part = s[:s.index("public")].strip()
    rest = s[s.index("public") + len("public"):].strip()
    # name = first identifier after `public`, skipping trailing keywords
    toks = [tk for tk in re.split(r"\s+", rest) if tk]
    name = None
    for tk in toks:
        if tk in _TRAILING_KW:
            continue
        m = re.match(r"^([A-Za-z_]\w*)", tk)
        if m:
            name = m.group(1)
            break
    if not name or not type_part:
        return None

    if type_part.startswith("mapping"):
        keys, val, val_arr = _parse_mapping(type_part)
        return {"name": name, "kind": "mapping", "key_types": keys,
                "value_type": val, "value_is_array": val_arr, "raw": s}
    if type_part.endswith("[]"):
        return {"name": name, "kind": "array", "key_types": [],
                "value_type": type_part[:-2].strip(), "value_is_array": False, "raw": s}
    # scalar (single type token only — reject multi-word noise that isn't a real type)
    if re.match(r"^[A-Za-z_][\w.]*(\[[0-9]*\])*$", type_part):
        return {"name": name, "kind": "scalar", "key_types": [],
                "value_type": type_part, "value_is_array": False, "raw": s}
    return None


# A value type we cannot expand into a flat getter return (a struct, or a mapping-valued struct member).
_ELEMENTARY = re.compile(r"^(address|bool|string|bytes\d*|u?int\d*|bytes)(\[[0-9]*\])*$")


def generated_getter_signature(parsed: dict) -> dict:
    """Synthesize the getter Solidity auto-generates for a public state var.

    scalar T            -> name() returns (T)
    T[]                 -> name(uint256) returns (T)
    mapping(K=>V)       -> name(K) returns (V)            (V[]  -> name(K,uint256) returns (V))
    mapping(K1=>K2=>V)  -> name(K1,K2) returns (V)
    A non-elementary value (struct) -> needs_context (return shape can't be inferred here).
    """
    name = parsed["name"]
    needs_context = False
    if parsed["kind"] == "scalar":
        args: list[str] = []
        ret = parsed["value_type"]
    elif parsed["kind"] == "array":
        args = ["uint256"]
        ret = parsed["value_type"]
    else:  # mapping
        args = list(parsed["key_types"])
        if parsed["value_is_array"]:
            args = args + ["uint256"]
        ret = parsed["value_type"]
    if not _ELEMENTARY.match(canon_type(ret)):
        needs_context = True  # struct / user-defined value: getter returns a tuple we can't flatten here
    return {"name": name, "arg_types": _canon_list(args),
            "return_types": _canon_list([ret]), "needs_context": needs_context}


# ---------------------------------------------------------------- interface declaration parsing

def _split_top_commas(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for c in s:
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        if c == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += c
    if cur.strip():
        out.append(cur)
    return [x.strip() for x in out if x.strip()]


def _param_type(param: str) -> str:
    """Extract the TYPE from a parameter that may or may not carry a name / storage location."""
    p = _STORAGE.sub(" ", param).strip()
    # drop a trailing identifier (the param name), keeping the leading type tokens
    toks = p.split()
    if len(toks) >= 2 and re.match(r"^[A-Za-z_]\w*$", toks[-1]):
        toks = toks[:-1]
    return canon_type(" ".join(toks))


def parse_decl_signature(sig: str) -> dict | None:
    """Parse an interface/abstract function declaration string into {name, arg_types, return_types}."""
    m = re.search(r"function\s+([A-Za-z_]\w*)\s*\(", sig or "")
    if not m:
        return None
    name = m.group(1)
    # params = balanced content of the first '(' after the name
    start = m.end() - 1
    depth, i = 0, start
    while i < len(sig):
        if sig[i] == "(":
            depth += 1
        elif sig[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    params_raw = sig[start + 1:i]
    arg_types = [_param_type(p) for p in _split_top_commas(params_raw)]
    rm = re.search(r"returns\s*\((.*)\)", sig)
    return_types: list[str] = []
    if rm:
        # returns(...) may itself contain trailing modifiers; take to the matching close already captured by regex greedily
        ret_inner = rm.group(1)
        # trim anything after a top-level ')' that belongs to the body (defensive)
        return_types = [_param_type(p) for p in _split_top_commas(ret_inner)]
    return {"name": name, "arg_types": arg_types, "return_types": return_types}


def is_declaration_only(signature: str, span_method: str = "") -> bool:
    """An interface/abstract declaration: ends in ';' (no body) or the manifest span is start-only."""
    s = (signature or "").strip()
    return s.endswith(";") or span_method == "regex_start_only"


# ---------------------------------------------------------------- mismatch classification

def _is_user_defined(t: str) -> bool:
    """A capitalized, non-elementary single type (contract / interface / struct / enum)."""
    return bool(re.match(r"^[A-Z]\w*$", t)) and not _ELEMENTARY.match(t)


def _ret_compatible(a: str, b: str) -> bool:
    """ABI return-type compatibility. address ≡ any contract/interface type (both encode as address)."""
    if a == b:
        return True
    if (a == "address" and _is_user_defined(b)) or (b == "address" and _is_user_defined(a)):
        return True
    return False


def classify_pair(decl: dict, getter: dict) -> dict:
    """Compare an interface declaration to a generated getter (same name assumed).

    Returns {mismatch: bool, mismatch_type, selector_match, detail}.
      arity_mismatch       — different parameter count (selector cannot match → call reverts)
      selector_mismatch    — same arity, different arg types (4-byte selector differs → call reverts)
      return_shape_mismatch— selector matches but return shape genuinely differs (call misdecodes)

    FP controls: a struct-valued getter (`needs_context`) is NOT flagged on return shape (Solidity expands
    its getter to a tuple that usually matches the interface). A user-defined return type that is
    address-equivalent is compatible. Return mismatch is only raised when BOTH returns are elementary.
    """
    d_args = _canon_list(decl.get("arg_types", []))
    g_args = _canon_list(getter.get("arg_types", []))
    d_ret = _canon_list(decl.get("return_types", []))
    g_ret = _canon_list(getter.get("return_types", []))
    selector_match = d_args == g_args
    detail = {"decl_args": d_args, "getter_args": g_args, "decl_returns": d_ret, "getter_returns": g_ret}
    if len(d_args) != len(g_args):
        return {"mismatch": True, "mismatch_type": "arity_mismatch", "selector_match": False, "detail": detail}
    if not selector_match:
        return {"mismatch": True, "mismatch_type": "selector_mismatch", "selector_match": False, "detail": detail}
    # selector matches → only a genuine elementary return divergence is a (lower-value) misdecode mismatch.
    if getter.get("needs_context"):
        return {"mismatch": False, "mismatch_type": None, "selector_match": True, "detail": detail}
    if (len(d_ret) == 1 and len(g_ret) == 1 and _ELEMENTARY.match(d_ret[0]) and _ELEMENTARY.match(g_ret[0])
            and not _ret_compatible(d_ret[0], g_ret[0])):
        return {"mismatch": True, "mismatch_type": "return_shape_mismatch", "selector_match": True, "detail": detail}
    return {"mismatch": False, "mismatch_type": None, "selector_match": True, "detail": detail}


def explicit_fn_resolves(decl: dict, fn_decl: dict) -> bool:
    """True if an explicit implementation function matches the interface decl (same selector + compatible
    return) — i.e. the call binds to that function, not the auto-getter, so there is no mismatch."""
    if not fn_decl:
        return False
    res = classify_pair(decl, {"name": fn_decl.get("name"), "arg_types": fn_decl.get("arg_types", []),
                               "return_types": fn_decl.get("return_types", [])})
    return not res["mismatch"]


# confidence ladder (FP controls live here; the audit feeds the flags)
def confidence(has_call_site: bool, has_name_pairing: bool, needs_context: bool) -> str:
    """A plausible interface→implementation binding (name pairing) is REQUIRED to route. Without it the
       mismatch is recorded low/context only (FP control: 'no plausible binding → do not flag/route').
         high  = name pairing + a cast-and-call site through that interface (directly reachable).
         medium= name pairing, no call site (or an uninferable proxy/struct binding).
         low   = mismatch without a plausible binding — context only, never routed."""
    if not has_name_pairing:
        return "low"
    if has_call_site and not needs_context:
        return "high"
    return "medium"


ROUTED_CONFIDENCE = {"high", "medium"}
