#!/usr/bin/env python3
"""
griefing_dos_taxonomy.py — Classifier for Field-DoS / griefing surfaces, modeling attacker-controlled COST
ASYMMETRY (cheap state creation/fragmentation -> expensive/reverting later path). Used by
griefing_dos_audit.py. Mirrors the prior lens taxonomies (snippet-aware, like units/migration).

The question is NOT "is there a loop". It is "can an attacker cheaply create state that makes someone else's
later required path expensive, reverting, or unusable?" — the class behind #379 (plot-spam transfer DoS),
#485 (duplicate plotIndexes via sow), #491 (transferDeposit amount==0 recipient DoS).

FP backbone (the spec's controls):
  * a LOOP is a signal only when bounded by user-input/storage-length/external-array (loop_patterns require a
    `.length`/array-param shape; a bare `for(uint i;i<3;...)` constant loop or a pure helper is NOT enough);
  * a STORAGE WRITE is a signal only when repeatable-cheap/fragmenting (`.push(` / per-id entry), not a single
    balance update;
  * admin/owner-only cleanup/config NOT tagged unless attacker-influenced (caller modifiers checked);
  * a category needs a real signal (name + body), bare names alone don't fire the growth/loop categories.
HIGH-RISK requires a creation/growth signal AND a consumer (loop/recipient-revert) signal — the asymmetry.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "griefing_dos_patterns.json"

_ADMIN_HINTS = ("onlyowner", "onlyrole", "enforceisownerorcontract", "enforceiscontractowner", "ownableupgradeable")
_PURE_HELPER_HINTS = ("pure returns", " pure ", "internal pure")


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"categories": {}, "high_risk_categories": [], "creation_signals": [], "consumer_signals": []}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", " ", text)


def _name_len(name_l: str, patterns: list[str]) -> int:
    best = 0
    for p in patterns:
        pl = p.lower()
        if pl and pl in name_l:
            best = max(best, len(pl))
    return best


def _any(text: str, patterns: list[str]) -> bool:
    return any(p.lower() in text for p in patterns)


def _regex_any(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        try:
            if re.search(p, text, re.IGNORECASE):
                return True
        except re.error:
            continue
    return False


def has_creation_signal(body: str, tax: dict) -> bool:
    return _any(body.lower(), tax.get("creation_signals", []))


def has_consumer_signal(body: str, tax: dict) -> bool:
    bl = body.lower()
    # a consumer signal = a loop bounded by a .length / array param, or a recipient external call
    if re.search(r"for\s*\([^;]*;[^;{]*\.length", body, re.IGNORECASE) or re.search(r"while\s*\(", body, re.IGNORECASE):
        return True
    return _any(bl, [".call(", "safetransfer", "onerc1155received", "onerc721received", "sendvalue"])


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    cats = tax.get("categories", {})
    name_l = (name or "").lower()
    raw = " ".join([signature or "", snippet or ""])
    body = _strip_comments(raw)
    body_l = body.lower()
    file_l = (file or "").lower()

    # PRIMITIVE GATE (the FP backbone): an item is griefing-sensitive ONLY if its body contains a concrete
    # griefing primitive — an array .push, a .length-bounded loop, a recipient external call, a zero-amount
    # guard, or a specific growable state var. This is what stops the lens from tagging every function that
    # merely touches s.accts[ / does a division / writes a mapping (the flag-all-arithmetic failure mode).
    if not _regex_any(body, tax.get("griefing_primitive_patterns", [])):
        return _neg()

    # FP control: admin/owner-only path is not attacker-griefing (unless it has a creation signal the
    # attacker can drive). The migration/other lenses cover privileged paths.
    if _any(body_l, _ADMIN_HINTS) and not has_creation_signal(body, tax):
        return _neg()

    create = has_creation_signal(body, tax)
    consume = has_consumer_signal(body, tax)

    hr = set(tax.get("high_risk_categories", []))
    best = None
    for cat, meta in cats.items():
        nlen = _name_len(name_l, meta.get("name_patterns", []))
        name_hit = nlen > 0
        file_hit = _any(file_l, meta.get("file_patterns", []))
        call_hit = _any(body_l, [c.lower() for c in meta.get("call_patterns", [])])
        sv_hit = _any(body_l, [s.lower() for s in meta.get("state_var_patterns", [])])
        loop_hit = _regex_any(body, meta.get("loop_patterns", []))
        arith_hit = _regex_any(body, meta.get("arithmetic_patterns", []))
        body_sig = call_hit or sv_hit or loop_hit or arith_hit
        # A category fires only with a BODY signal (push/loop/state-var/arith/call) — a bare name is not
        # enough (keeps 'add'/'transfer'/'claim' names from firing without the actual growth/loop shape).
        if not body_sig:
            continue
        role = meta.get("role", "both")
        # zero_amount_edge is special: it fires on the (missing/present) amount guard arith on a create path.
        sig_rank = 3 if (loop_hit or arith_hit) else 2
        key = (sig_rank, nlen, 1 if file_hit else 0, 1 if cat in hr else 0)
        matched_on = ("arith" if arith_hit else "loop" if loop_hit else "state_var" if sv_hit
                      else "call" if call_hit else "name")
        if best is None or key > best[0]:
            best = (key, cat, meta, matched_on, role)

    if best is None:
        return _neg()
    _, cat, meta, matched_on, role = best
    # read-only getter? (declared view/pure) — relevant for the consumer-enumeration surface but NOT
    # high-risk on its own (the state-changing path that iterates the grown state carries the risk).
    sig_head = (signature or "").split("{", 1)[0].lower()
    read_only = bool(re.search(r"\b(view|pure)\b", sig_head))
    return {
        "griefing_sensitive": True, "category": cat, "risk_tags": list(meta.get("risk_tags", [])),
        "state_growth_surface": meta.get("state_growth_surface", "generic"), "role": role,
        "review_hint": meta.get("review_hint", ""), "severity_ceiling_hint": meta.get("severity_ceiling_hint"),
        "matched_on": matched_on, "_has_create": create, "_has_consume": consume, "_read_only": read_only,
    }


def _neg() -> dict:
    return {"griefing_sensitive": False, "category": None, "risk_tags": [], "state_growth_surface": None,
            "role": None, "review_hint": "", "severity_ceiling_hint": None, "matched_on": None,
            "_has_create": False, "_has_consume": False}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    """High-risk = high-risk category AND the cost-asymmetry is present: the item itself has BOTH a creation
    and a consumer signal, OR it is a consumer-role loop over growable state, OR a creator with a clear
    fragmentation/zero-amount primitive. (A lone creator with no consumer anywhere stays Medium/Low.)"""
    tax = taxonomy or load_taxonomy()
    if not classification.get("griefing_sensitive"):
        return False
    if classification.get("category") not in tax.get("high_risk_categories", []):
        return False
    # FP control: a read-only (view/pure) getter is not high-risk on its own (spec: pure/read-only loops
    # are not high-risk unless on a state-changing/required path — which the state-changing consumer carries).
    if classification.get("_read_only"):
        return False
    role = classification.get("role")
    if classification.get("_has_create") and classification.get("_has_consume"):
        return True  # same function both grows and iterates -> direct asymmetry
    if role == "consumer" and classification.get("_has_consume"):
        return True  # iterates growable state on a required path
    if role in ("creator", "both") and classification.get("category") in (
            "plot_spam", "deposit_fragmentation", "zero_amount_edge", "pod_fragmentation",
            "storage_growth", "array_bloat", "state_cleanup_missing"):
        return True  # a concrete cheap-creation/fragmentation primitive
    return False
