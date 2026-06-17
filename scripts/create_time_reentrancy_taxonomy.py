#!/usr/bin/env python3
"""
create_time_reentrancy_taxonomy.py — pure (no-I/O) classifier for the CREATE-TIME / REGISTRATION-TIME REENTRANCY
research family. Detects a create/mint/register/list/deposit/stake flow that performs a callback-yielding external
interaction (safeMint / ERC721-1155 receiver callback / external hook / low-level call) BEFORE committing the
registration/limit/accounting state, with NO reentrancy guard — so a reentrant call sees partially-initialized state
and bypasses the invariant.

4-signal gate: S1 create-verb fn + S2 callback-yielding interaction + S3 a state-commit AFTER the callback (CEI
violation, ordering-based) + S4 no nonReentrant. Anchor: nextgen H-01 (NextGenCore.mint -> _mintProcessing ->
_safeMint before tokensMintedPerAddress += 1, no guard).

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints/routes. High precision over recall.
Scope: callback-before-commit in create flows ONLY (not generic/cross-contract/read-only reentrancy).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "create_time_reentrancy_patterns.json"
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _first_index(text: str, terms) -> int:
    idxs = [text.find(t) for t in terms if t in text]
    return min(idxs) if idxs else -1


def classify(contract: str, name: str, signature: str, body: str, *, modifiers=None, context=None) -> list:
    """Return 0 or 1 create-time-reentrancy candidate for one (+1-helper-resolved) function. Pure."""
    cfg = _cfg()
    context = context or {}
    b = strip_comments(body or "").lower()
    nlow = (name or "").lower()
    sig = strip_comments(signature or "").lower()
    mods = " ".join(modifiers or []).lower() + " " + sig

    # ---- S1: create/register verb in the function name ----
    verbs = [v for v in cfg.get("create_verbs", []) if v in nlow]
    if not verbs:
        return []

    # ---- S4: reentrancy guard present anywhere (modifiers/sig/body) -> suppress ----
    guard_terms = cfg.get("reentrancy_guard_markers", [])
    if any(g in mods for g in guard_terms) or any(g in b for g in guard_terms):
        return []

    # ---- S2: a callback-yielding external interaction ----
    cb_terms = cfg.get("callback_interactions", [])
    cb_idx = _first_index(b, cb_terms)
    if cb_idx < 0:
        return []
    cb_hit = next((t for t in cb_terms if t in b and b.find(t) == cb_idx), cb_terms[0])

    # ---- S3: a state-commit that appears AFTER the callback (CEI violation, ordering-based) ----
    tail = b[cb_idx + len(cb_hit):]
    commit_terms = cfg.get("state_commit_markers", [])
    post_commits = [m for m in commit_terms if m in tail]
    if not post_commits:
        return []

    confidence = "high" if (context.get("guard_known", True)) else "medium"

    return [{
        "finding_shape": "create_time_reentrancy",
        "confidence": confidence,
        "create_verb": verbs[0],
        "callback": cb_hit,
        "post_callback_commit": post_commits[:4],
        "explanation": (
            f"{contract}.{name} is a '{verbs[0]}' create/registration flow that performs a callback-yielding "
            f"interaction ({cb_hit}) BEFORE committing state ({', '.join(post_commits[:3])}) and has no reentrancy "
            f"guard. A reentrant call via the callback observes partially-initialized state (e.g. a stale per-address "
            f"limit counter) and can bypass the invariant (nextgen H-01 class)."),
        "signals": {"S1_create_verb": verbs[:3], "S2_callback": cb_hit, "S3_post_commit": post_commits[:4],
                    "S4_no_guard": True},
    }]


if __name__ == "__main__":  # tiny manual smoke
    import sys
    print(json.dumps(classify("C", sys.argv[1] if len(sys.argv) > 1 else "mint", "", sys.stdin.read()), indent=2))
