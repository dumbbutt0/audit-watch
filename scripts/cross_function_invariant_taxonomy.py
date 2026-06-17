#!/usr/bin/env python3
"""
cross_function_invariant_taxonomy.py — per-function feature extraction for the cross-function / boundary
invariant lens. classify() reports the key-deriving calls, counter/limit signals, external calls,
reentrancy-guard presence, queue ops, and validation a single function contains. The audit runner
(cross_function_invariant_audit.py) PAIRS these per contract to flag candidate writer/reader invariant
mismatches and routes them to needs_deep_pass. Two-signal, FP-tight; never asserts a definite bug.

Mirrors recipient_custody_taxonomy / griefing_dos_taxonomy. Derived from Recall H-03/H-04/H-06.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "cross_function_invariant_patterns.json"


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", " ", text)


def _matches(text: str, patterns: list[str]) -> list[str]:
    out = []
    for p in patterns or []:
        try:
            if re.search(p, text, re.IGNORECASE):
                out.append(p)
        except re.error:
            if p.lower() in text.lower():
                out.append(p)
    return out


_KEY_NAME_RE = re.compile(r"\b(toHash|toTracingId|toId|keccak256)\s*\(", re.IGNORECASE)


def key_calls(text: str) -> set[str]:
    """The distinct key/hash-deriving call names used in this body (lowercased)."""
    return {m.group(1).lower() for m in _KEY_NAME_RE.finditer(text)}


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    return {
        "name": name, "contract": contract, "file": file,
        "key_calls": sorted(key_calls(body)),
        "has_shared_state": bool(_matches(body, tax.get("shared_state_signals", []))),
        "has_counter_increment": bool(_matches(body, tax.get("counter_increment_signals", []))),
        "has_limit_check": bool(_matches(body, tax.get("limit_check_signals", []))),
        "has_external_call": bool(_matches(body, tax.get("external_call_signals", []))),
        "has_reentrancy_guard": bool(_matches(body, tax.get("reentrancy_guard_signals", []))),
        "has_queue_op": bool(_matches(body, tax.get("queue_op_signals", []))),
        "has_validation": bool(_matches(body, tax.get("validation_signals", []))),
        "_body_len": len(body),
    }
