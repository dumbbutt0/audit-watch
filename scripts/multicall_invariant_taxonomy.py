#!/usr/bin/env python3
"""
multicall_invariant_taxonomy.py — pure (no-I/O) classifier for the MULTICALL / BATCH-INVARIANT research
prototype. Seeded on Size Credit M-01 (Multicall.multicall validates the borrow-aToken cap with
balanceOf(address(this)) instead of totalSupply() — a per-call invariant that a *batch* can break).

Detects batch / multicall / delegatecall-loop executors where an accounting invariant (balanceOf / totalSupply
/ supply-cap / credit / debt) can be bypassed or broken across a sequence of sub-calls.

RESEARCH-ONLY: the audit that uses this is read-only, is_gate:false, routes_in_production:false — never mints
or routes. Self-contained. TWO-SIGNAL gate is the primary FP control: every candidate requires a
BATCH-EXECUTOR signal (name-gate OR a call/delegatecall loop) AND an ACCOUNTING-INVARIANT signal (supply / cap
/ credit / debt terms). Pure-view aggregates, admin setters, thin wrappers, and non-executing loops are
suppressed.

Shapes:
  1. pre_post_supply_invariant   (Size M-01) — before/after supply capture + a cross-batch validate
  2. per_call_check_batch_bypass — a cap/limit check applied per sub-call inside the loop
  3. same_tx_state_reuse         — an in-batch flag (isMulticall) + reusable same-tx state
  4. delegatecall_self_context   — delegatecall-to-self loop over bytes[] under preserved msg.sender/context
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "multicall_invariant_patterns.json"

ROUTED_CONFIDENCE = frozenset({"high", "medium"})
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
_LOOP_RE = re.compile(r"\b(for|while)\s*\(")


def _loop_body(blob: str) -> str:
    """Return the brace-matched body of the first for/while loop (lowercased blob), or '' if none."""
    m = _LOOP_RE.search(blob)
    if not m:
        return ""
    i = blob.find("{", m.end())
    if i < 0:
        return ""
    depth, k = 0, i
    while k < len(blob):
        if blob[k] == "{":
            depth += 1
        elif blob[k] == "}":
            depth -= 1
            if depth == 0:
                return blob[i:k + 1]
        k += 1
    return blob[i:]


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _terms(key: str, default: list) -> tuple:
    return tuple(_cfg().get(key, default))


NAME_GATE = lambda: _terms("name_gate", [
    "multicall", "batch", "aggregate", "executebatch", "batchcall", "multidelegatecall",
    "multisend", "multiexecute", "batchexecute"])
EXCLUDE_NAMES = lambda: _terms("exclude_names", ["initialize", "setconfig", "configparams", "setter"])
EXEC_CALLS = lambda: _terms("batch_executor_calls", ["functiondelegatecall", "delegatecall", "functioncall", ".call("])
SUPPLY = lambda: _terms("supply_terms", ["balanceof", "totalsupply", "supplycap"])
CAP_WORD = lambda: _terms("cap_word_terms", ["cap", "limit", "ceiling"])
ACCT = lambda: _terms("accounting_terms", ["credit", "debt", "collateral", "shares", "balance", "supply", "borrow"])
STATE_REUSE = lambda: _terms("state_reuse_terms",
                             ["nonce", "shares", "debt", "credit", "position", "balance", "supply", "reserve"])
BATCH_FLAG = lambda: _terms("batch_flag_terms", ["ismulticall", "inbatch", "isbatch", "batching", "_inmulticall"])
CHECK = lambda: _terms("check_terms", ["validate", "require", "check", "invariant", "assert"])
VIEW = lambda: _terms("view_terms", ["staticcall", ".staticcall(", "view returns", "pure returns"])
SETTER_RE = lambda: re.compile(_cfg().get("setter_call_re", r"\b_?set[A-Z]"))


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _has(text: str, terms) -> list:
    return [w for w in terms if w in text]


def _word(text: str, terms) -> list:
    return [w for w in terms if re.search(r"\b" + re.escape(w) + r"\b", text)]


def classify(name: str, signature: str, file: str, contract: str, snippet: str = "", tags=None) -> list:
    """Return a LIST of shape candidates (possibly empty). Pure; snippet is the (helper-resolved) body."""
    nlow = (name or "").lower()
    body = strip_comments(snippet or "")
    sig = strip_comments(signature or "")
    blob = (nlow + " " + body + " " + sig).lower()

    # config/admin setter exclusion (name level) — but keep real batch executors named "batch*"
    if any(x in nlow for x in EXCLUDE_NAMES()) and not any(g in nlow for g in NAME_GATE()):
        return []

    # ---- signal A: batch-executor ----
    name_batch = any(g in nlow for g in NAME_GATE())
    has_loop = bool(_LOOP_RE.search(blob))
    exec_call = any(c in blob for c in EXEC_CALLS())
    call_loop = has_loop and exec_call
    bytes_array = "bytes[]" in blob
    self_delegate = (("functiondelegatecall" in blob) or ("delegatecall" in blob)) and \
        ("address(this)" in blob or "address (this)" in blob)
    external_opaque = call_loop and not self_delegate  # .call(target)/functionCall to a non-self address
    batch_signal = name_batch or call_loop or self_delegate
    if not batch_signal:
        return []

    # ---- signal B: accounting invariant ----
    supply = _has(blob, SUPPLY())
    cap = _word(blob, CAP_WORD())
    acct = _word(blob, ACCT())
    invariant_terms = sorted(set(supply + cap + acct))
    has_invariant = bool(supply or cap or acct)

    # ---- FP suppression ----
    is_view = any(v in blob for v in VIEW())
    mutates = bool(re.search(r"\b(mint|burn|transfer|deposit|withdraw|delegatecall|functiondelegatecall)\b", blob)) \
        or "=" in body
    # pure-view aggregate: read-only + no invariant + not a self-delegatecall
    if is_view and not has_invariant and not self_delegate:
        return []
    # admin batch setter: setX-dominated, no supply read, no before/after capture
    setter_hits = len(SETTER_RE().findall(body))
    before = "before" in blob
    after = "after" in blob
    reads_supply = bool(supply)
    if setter_hits and not reads_supply and not (before and after):
        return []
    # two-signal gate: a name-only batch with no executor loop AND no invariant is a thin wrapper / noise
    if not has_invariant and not self_delegate:
        return []
    # a name-gated batch with neither an executing loop nor a self-delegatecall and no invariant terms -> thin
    if name_batch and not call_loop and not self_delegate and not has_invariant:
        return []

    # ---- resolvability ----
    mutator_resolvable = self_delegate or (call_loop and not external_opaque)
    batch_flag = any(f in blob for f in BATCH_FLAG())
    has_check = any(c in blob for c in CHECK())
    before_after = before and after
    loop_blob = _loop_body(blob)
    check_in_loop = any(c in loop_blob for c in CHECK()) and (any(w in loop_blob for w in CAP_WORD())
                                                              or any(s in loop_blob for s in SUPPLY()))

    out = []

    def add(shape, confidence, check_location, reason, missing=""):
        out.append({
            "finding_shape": shape, "confidence": confidence,
            "multicall_function": name,
            "callable_state_mutators": ("self_delegatecall_loop" if self_delegate
                                        else "external_opaque_call_loop" if external_opaque
                                        else "local"),
            "invariant_terms": invariant_terms,
            "check_location": check_location,
            "evidence_terms": sorted(set(supply + cap + acct +
                                         (["self_delegatecall"] if self_delegate else []) +
                                         (["batch_loop"] if call_loop else []) +
                                         (["isMulticall_flag"] if batch_flag else [])))[:12],
            "reason": reason, "missing_context": missing,
        })

    # 1. pre_post_supply_invariant (Size M-01) — needs an invariant term + (before/after OR a validate)
    if (supply or cap) and (before_after or has_check):
        if not mutator_resolvable:
            add("pre_post_supply_invariant", "needs_context", "unresolved_helper",
                f"{name} batches sub-calls over OPAQUE/external targets while reading a supply/cap invariant "
                f"({sorted(set(supply+cap))[:4]}) — mutators are not statically resolvable; the batch could "
                f"break the per-call invariant, verify across the whole batch",
                missing="sub-call targets are not address(this); resolve the callable mutators")
        elif len(set(supply)) >= 2 and before_after:
            add("pre_post_supply_invariant", "high", "after_batch",
                f"{name} captures supply BEFORE and AFTER a self-delegatecall batch ({sorted(set(supply))}) and "
                f"validates across it — verify the invariant uses the CORRECT accounting basis (e.g. totalSupply "
                f"vs balanceOf) and holds for every interleaving of sub-calls (Size M-01 class)")
        elif before_after:
            add("pre_post_supply_invariant", "high" if ("supplycap" in supply or cap) else "medium", "after_batch",
                f"{name} captures a supply/cap invariant before/after a batch ({invariant_terms[:4]}) — verify "
                f"the basis is correct and the bound holds across the batch, not just per call")
        else:
            add("pre_post_supply_invariant", "needs_context", "unresolved_helper",
                f"{name} runs a batch and calls a validate/check helper touching a supply/cap invariant "
                f"({invariant_terms[:4]}) but captures no local before/after state — confirm the invariant is "
                f"enforced across the batch",
                missing="invariant check is in a shared helper; no local before/after capture")

    # 2. per_call_check_batch_bypass — a cap/limit check applied INSIDE the loop (per sub-call), not across it
    if call_loop and check_in_loop:
        add("per_call_check_batch_bypass", "high" if self_delegate else "medium", "in_loop",
            f"{name} applies a {sorted(set(cap+supply))[:3]} check per sub-call inside the batch loop — an "
            f"earlier sub-call can move state so a later sub-call passes the check under stale assumptions; "
            f"verify the limit holds for the cumulative batch effect")

    # 3. same_tx_state_reuse — an in-batch flag + reusable same-tx state
    if batch_flag and _word(blob, STATE_REUSE()):
        add("same_tx_state_reuse", "high" if (self_delegate and (supply or cap)) else "medium", "after_batch",
            f"{name} sets an in-batch flag ({[f for f in BATCH_FLAG() if f in blob][:2]}) and reuses same-tx "
            f"{_word(blob, STATE_REUSE())[:4]} — verify a sub-call cannot reuse intra-batch state to bypass a "
            f"one-call assumption (e.g. a check skipped while isMulticall is set)")

    # 4. delegatecall_self_context — delegatecall-to-self loop over bytes[] under preserved context
    if self_delegate and bytes_array:
        ctx = ("payable" in blob) or ("msg.sender" in blob) or batch_flag or has_invariant
        add("delegatecall_self_context", "high" if (call_loop and ctx) else "medium" if call_loop else "low",
            "after_batch" if before_after else "in_loop",
            f"{name} delegatecalls address(this) over bytes[] sub-calls preserving msg.sender/context — verify "
            f"each callable selector is safe under batched execution (no msg.value reuse, no assumption of "
            f"standalone execution, no invariant only valid per single call)")

    return out


if __name__ == "__main__":  # tiny manual smoke
    import sys
    print(json.dumps(classify(sys.argv[1] if len(sys.argv) > 1 else "multicall", "", "f.sol", "C",
                              snippet=sys.stdin.read()), indent=2))
