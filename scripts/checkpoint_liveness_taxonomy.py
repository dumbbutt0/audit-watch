#!/usr/bin/env python3
"""
checkpoint_liveness_taxonomy.py — classify checkpoint / queue / returndata LIVENESS risk in one function:
can one malicious item block a checkpoint/batch, is returndata unbounded, can a compaction loop skip
entries, or is confirmation state floodable. Two-signal, FP-tight. Mirrors griefing_dos_taxonomy (which
stays cost-asymmetry); this lens is checkpoint/queue-liveness-specific. Derived from Recall H-07/H-09/M-04.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "checkpoint_liveness_patterns.json"


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


def _hit(text: str, patterns: list[str]) -> bool:
    for p in patterns or []:
        try:
            if re.search(p, text, re.IGNORECASE):
                return True
        except re.error:
            if p.lower() in text.lower():
                return True
    return False


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    ctx_text = " ".join([name or "", contract or "", body])
    in_ctx = _hit(ctx_text, tax.get("liveness_context_signals", []))
    has_loop = _hit(body, tax.get("loop_signals", []))
    has_ext = _hit(body, tax.get("external_call_signals", []))
    has_ret = _hit(body, tax.get("returndata_signals", []))
    is_compact = _hit(name or "", tax.get("compaction_signals", [])) or _hit(body, tax.get("compaction_signals", []))
    has_append = _hit(body, tax.get("append_signals", []))
    has_bound = _hit(body, tax.get("bound_signals", []))

    category = None
    if in_ctx and has_loop and has_ext:
        category = "recipient_blocks_checkpoint"
    elif has_ret and has_ext:
        category = "unbounded_returndata"
    elif is_compact and has_loop:
        category = "compaction_skip"
    elif in_ctx and has_append and not has_bound:
        category = "floodable_state"

    sensitive = category is not None
    meta = tax.get("categories", {}).get(category or "", {})
    return {
        "liveness_sensitive": sensitive, "category": category,
        "in_context": in_ctx, "has_loop": has_loop, "has_external_call": has_ext,
        "has_returndata_load": has_ret, "is_compaction": is_compact,
        "has_append": has_append, "has_bound": has_bound,
        "severity_ceiling_hint": meta.get("severity_ceiling_hint", "Medium") if sensitive else None,
    }


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    """High-risk = a liveness category whose ceiling is High (recipient-blocks-checkpoint, unbounded
    returndata, compaction-skip). Floodable_state is Medium and reported but not auto-escalated High."""
    if not classification.get("liveness_sensitive"):
        return False
    return classification.get("category") in {"recipient_blocks_checkpoint", "unbounded_returndata", "compaction_skip"}
