#!/usr/bin/env python3
"""P281 — source-span guard extractor (RESEARCH-ONLY, ADVISORY, UN-WIRED).

D4 primitive for the READY-gate repair: read a coverage-manifest function item's body from `file` + `source_span`, and
detect (D1) inline caller/owner/approval/role/paused guards, (D2) state-machine status gates, (D3) value-flow signals —
each with the source-span line offsets it relied on. Reads ONLY source (the function body); never award text. Tolerates
missing/unreadable files -> returns {"body_available": False} so callers fall back to pre-P281 behavior.

Importable: extract(item, root) -> evidence dict. Also a CLI for spot checks.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/research_poc_readiness_gate.json").read_text())
GUARD = [p.lower() for p in CFG["inline_guard_patterns"]]
GERR = [p.lower() for p in CFG["guard_error_patterns"]]
SM = [p.lower() for p in CFG["state_machine_patterns"]]
VF = [p.lower() for p in CFG["value_flow_patterns"]]
BYPASS = [p.lower() for p in CFG["bypass_evidence_markers"]]

# P282 D1-gap closures: msg.sender on EITHER side of ==/!=, and modifier-based auth (onlyOwner/onlyManager/onlyRole/…)
_MSGSENDER_EITHER = re.compile(r"msg\.sender\s*[=!]=|[=!]=\s*msg\.sender")
_MODIFIER_AUTH = re.compile(r"\bonly[A-Z]\w*")  # matches the signature line in the span (e.g. external onlyManager …)
# P282 D3 value-flow structure
_STATE_WRITE = re.compile(r"\b[\w.\[\]]+\s*(?:=|\+=|-=)\s*[^=]|\.push\(|delete\s+\w")
_ASSET_MOVE = re.compile(r"\b(?:safetransferfrom|safetransfer|transferfrom|transfer|\.send\(|\.call\{|_mint|_burn|"
                         r"mint\(|burn\(|withdraw|redeem|claim)\b")
_DIV_BEFORE_MUL = re.compile(r"/[^;\n]*(?<!\*)\*(?!\*)")  # division textually before a *multiplication* (P283: the
# final `*` must be a real mul, not part of `**` exponentiation — `/ 2 ** 64` is fixed-point scaling, NOT div-before-mul)
_WRAPPER_DELEGATE = re.compile(r"return\s+_?\w+\s*\(|return\s+\w+\.\w+\(")  # `return _x(...)` / `return a.b(...)`
MAXC = int(CFG.get("max_body_chars", 20000))


_LINE_COMMENT = re.compile(r"//[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)

# ---- P285 D1 granularity: execution-gate detection + read-vs-guard context taxonomy ----
# A token counts as an inline guard ONLY when it sits in a construct that GATES EXECUTION (require / if-revert/return /
# modifier / custom-error revert). The SAME token used to compute a value/recipient is a READ, not a guard.
_RE_REQUIRE = re.compile(r"\b(?:require|assert)\s*\(")  # both revert-on-false guard calls
_RE_IF = re.compile(r"\bif\s*\(")
_RE_REVERTKW = re.compile(r"\b(revert|return|break|continue)\b")
_RE_EMIT_LINE = re.compile(r"\bemit\b")
_VALUE_SINK_TOKENS = ("transfer", "safetransfer", "transferfrom", "safetransferfrom", "claim", "distribute",
                      "mint", "_mint", "send", "redeem", "withdraw", "payout", "reward")
_RECIPIENT_NAMES = ("owner", "recipient", "beneficiary", "receiver", "dest", "nftowner", "_to", "to ", "to=", "to,",
                    "payee", "holder")
GUARD_CONTEXTS = ("EXECUTION_GUARD", "VALUE_READ", "RECIPIENT_READ", "EVENT_READ", "RETURN_READ", "ARITHMETIC_READ",
                  "UNKNOWN_READ")


def _match_close(src: str, open_idx: int, op: str, cl: str, limit: int = 4000) -> int:
    """Index just past the bracket matching the opener at/after open_idx (bounded)."""
    i = src.find(op, open_idx)
    if i < 0:
        return min(len(src), open_idx + limit)
    depth, j, end = 0, i, min(len(src), i + limit)
    while j < end:
        if src[j] == op:
            depth += 1
        elif src[j] == cl:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return end


def _gate_spans(body: str) -> list:
    """Char ranges (start, end, strength) that GATE execution: require args, and if-conditions whose tail reverts/
    returns (same-line `if(c) revert;` or block `if(c){ … revert …; }`)."""
    spans = []
    for m in _RE_REQUIRE.finditer(body):
        spans.append((m.start(), _match_close(body, m.end() - 1, "(", ")"), "STRONG"))
    for m in _RE_IF.finditer(body):
        cond_end = _match_close(body, m.end() - 1, "(", ")")
        tail = body[cond_end:cond_end + 400]
        region = body[cond_end:_match_close(body, cond_end, "{", "}")] if tail.lstrip()[:1] == "{" \
            else tail.split(";", 1)[0]
        rk = _RE_REVERTKW.search(region)
        if rk:
            spans.append((m.start(), cond_end, "STRONG" if rk.group(1) in ("revert", "return") else "MEDIUM"))
    return spans


def _read_context(body: str, off: int, tok: str) -> str:
    """Classify a non-gate token occurrence at char offset `off` by its surrounding STATEMENT (boundary = last
    ; { } before it, up to the next ;) — robust to single-line bodies."""
    ss = max(body.rfind(";", 0, off), body.rfind("{", 0, off), body.rfind("}", 0, off)) + 1
    se = body.find(";", off)
    stmt = body[ss:(se if se >= 0 else len(body))]
    low = stmt.lower()
    tokpos = off - ss
    if _RE_EMIT_LINE.search(low):
        return "EVENT_READ"
    if low.lstrip().startswith("return"):
        return "RETURN_READ"
    eqpos = stmt.find("=")
    if 0 <= eqpos < tokpos and "==" not in stmt[eqpos - 1:eqpos + 2] and "!=" not in stmt[eqpos - 1:eqpos + 1]:
        lhs = low[:eqpos]
        return "RECIPIENT_READ" if any(n in lhs for n in _RECIPIENT_NAMES) else "VALUE_READ"
    before = low[:tokpos]
    if any(s + "(" in before or s + " (" in before for s in _VALUE_SINK_TOKENS):
        return "RECIPIENT_READ" if any(n in low for n in _RECIPIENT_NAMES) else "VALUE_READ"
    if re.search(r"[+\-*/%]", stmt.replace("+=", "").replace("-=", "")) and "=" not in stmt:
        return "ARITHMETIC_READ"
    return "UNKNOWN_READ"


def classify_guard_contexts(body: str, tokens: list) -> tuple:
    """For each matched guard/auth token, decide EXECUTION_GUARD vs a READ context. Returns
    (inline_guard_detected, inline_guard_ambiguous, [context records])."""
    spans = _gate_spans(body)
    low = body.lower()
    contexts = []
    guard = False
    ambiguous = False
    for tok in tokens:
        t = tok.lower()
        occ = [m.start() for m in re.finditer(re.escape(t), low)] if t else []
        if not occ:
            continue
        in_gate = next(((s, e, st) for off in occ for (s, e, st) in spans if s <= off < e), None)
        if in_gate:
            guard = True
            ctx, strength, off = "EXECUTION_GUARD", in_gate[2], occ[0]
        else:
            off = occ[0]
            ctx = _read_context(body, off, t)
            strength = "NONE"
            if ctx == "UNKNOWN_READ":
                ambiguous = True
        snip = body[max(0, off - 30):off + 40].replace("\n", " ").strip()
        contexts.append({"token": tok, "context": ctx, "guard_strength": strength,
                         "source_snippet": snip,
                         "source_basis": f"offset {off}; in execution-gate span" if ctx == "EXECUTION_GUARD"
                         else f"offset {off}; not in any require/if-revert/modifier gate",
                         "reason": "token gates execution (require/if-revert/return/modifier)" if ctx == "EXECUTION_GUARD"
                         else f"token used as {ctx.lower().replace('_', ' ')}, not an access guard"})
    # modifier/error markers, when present, are always execution gates regardless of span math
    return guard, (ambiguous and not guard), contexts


def strip_comments(src: str) -> str:
    """Remove // line and /* */ block comments so detectors never match comment text (P283 correctness:
    a comment like `// T * (C - L) = G` must NOT register as a div-before-mul anomaly)."""
    return _LINE_COMMENT.sub("", _BLOCK_COMMENT.sub("", src or ""))


def _resolve(file_str: str, audit_id: str | None) -> Path | None:
    cands = [ROOT / file_str]
    if audit_id:
        cands.append(ROOT / "audits" / audit_id / file_str)
    cands.append(Path(file_str))
    for c in cands:
        try:
            if c.exists() and c.is_file():
                return c
        except Exception:
            continue
    return None


def extract_body(item: dict, audit_id: str | None = None) -> dict:
    f = item.get("file")
    sp = item.get("source_span") or {}
    s, e = sp.get("start_line"), sp.get("end_line")
    if not f or not s or not e:
        return {"body_available": False, "reason": "no file/source_span"}
    fp = _resolve(f, audit_id)
    if not fp:
        return {"body_available": False, "reason": "file unresolvable"}
    try:
        lines = fp.read_text(errors="ignore").splitlines()
    except Exception:
        return {"body_available": False, "reason": "unreadable"}
    body = "\n".join(lines[max(0, s - 1):e])[:MAXC]
    is_decl = body.rstrip().endswith(";") and "{" not in body  # interface / abstract declaration, no body
    return {"body_available": True, "body": body, "start_line": s, "end_line": e, "file": str(fp),
            "is_declaration_only": is_decl}


def detect(body: str) -> dict:
    body = strip_comments(body)  # P283: never let comment text register as a guard/anomaly/value signal
    b = body.lower()
    # P285 D1 granularity: token PRESENCE is not enough — a token is an inline guard only when it sits in an
    # EXECUTION-GATE construct (require / if-revert/return / modifier / custom-error revert). The same token used to
    # compute a value/recipient is a READ and must NOT refute READY.
    guard_tokens = sorted({p for p in GUARD if p in b})         # span-classified (may be reads, e.g. ownerOf(=recipient))
    gerrs = sorted({p for p in GERR if p in b})                 # custom-error revert markers — always gate actions
    msgsender_either = bool(_MSGSENDER_EITHER.search(b))
    modifier_auth = bool(_MODIFIER_AUTH.search(body))           # case-sensitive only<Capital> modifier in the signature
    classify = list(guard_tokens) + (["msg.sender"] if msgsender_either else [])
    gd_span, span_ambiguous, guard_contexts = classify_guard_contexts(body, classify)
    forced = (["modifier_auth(only*)"] if modifier_auth else []) + list(gerrs)
    for f in forced:                                            # modifier / custom-error revert: always EXECUTION_GUARD
        guard_contexts.append({"token": f, "context": "EXECUTION_GUARD", "guard_strength": "STRONG",
                               "source_snippet": "", "source_basis": "modifier or custom-error revert",
                               "reason": "modifier / custom-error revert gates execution"})
    inline_guard_detected = gd_span or bool(forced)
    inline_guard_ambiguous = span_ambiguous and not inline_guard_detected
    guard_markers = sorted(set(guard_tokens + gerrs
                               + (["msg.sender==/!= (either side)"] if msgsender_either else [])
                               + (["modifier_auth(only*)"] if modifier_auth else [])))
    sm = sorted({p for p in SM if p in b})
    vf = sorted({p for p in VF if p in b})
    # OR-state gate (e.g. `Succeeded || Defeated || Expired`) — a forbidden-state-accepting anomaly signal
    or_state_gate = ("|| status" in b or "|| state" in b or
                     (sum(x in b for x in ("succeeded", "defeated", "expired", "queued")) >= 2 and "require(" in b))
    # P282 D3 value-flow STRUCTURE (not just naming): a concrete state write / asset move in the span
    state_write = bool(_STATE_WRITE.search(body))
    asset_move = bool(_ASSET_MOVE.search(b))
    div_before_mul = bool(_DIV_BEFORE_MUL.search(b))  # a source-detectable precision-ordering anomaly
    wrapper_delegate = bool(_WRAPPER_DELEGATE.search(body)) and not state_write
    value_flow_detected = bool(vf) and (state_write or asset_move)  # naming ALONE is not value-flow
    # NOTE: bypass/satisfaction is NEVER inferred from source keywords. The gate reads an EXPLICIT package field.
    return {"inline_guard_detected": inline_guard_detected,                 # P285: refined to execution-gate only
            "inline_guard_ambiguous": inline_guard_ambiguous,              # P285: ambiguous auth READ, no gate
            "guard_contexts": guard_contexts,                              # P285: per-token read-vs-guard taxonomy
            "guard_markers": guard_markers,
            "state_machine_detected": bool(sm),
            "state_markers": sm,
            "or_state_gate": or_state_gate,
            "value_flow_detected": value_flow_detected,
            "value_markers": vf,
            "state_write": state_write,
            "asset_move": asset_move,
            "value_anomaly_div_before_mul": div_before_mul,
            "value_flow_out_of_span": wrapper_delegate}


def extract(item: dict, audit_id: str | None = None) -> dict:
    bd = extract_body(item, audit_id)
    if not bd.get("body_available"):
        return {"body_available": False, "reason": bd.get("reason")}
    if bd.get("is_declaration_only"):
        return {"body_available": True, "is_declaration_only": True, "file": bd["file"],
                "source_span": [bd["start_line"], bd["end_line"]],
                "inline_guard_detected": False, "state_machine_detected": False, "value_flow_detected": False,
                "note": "declaration-only (interface/abstract) — no body to establish attacker_path"}
    d = detect(bd["body"])
    d.update({"body_available": True, "is_declaration_only": False, "file": bd["file"],
              "source_span": [bd["start_line"], bd["end_line"]]})
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--contract-function", required=True)
    ap.add_argument("--audit-id")
    a = ap.parse_args()
    man = json.loads(Path(a.manifest).read_text())
    c, _, fn = a.contract_function.partition(".")
    item = next((i for i in man.get("items", []) if i.get("kind") == "function" and i.get("name") == fn
                 and c in (i.get("contract") or "")), None)
    print(json.dumps(extract(item or {}, a.audit_id), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
