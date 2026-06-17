#!/usr/bin/env python3
"""
special_focus_terms.py — shared "special-focus" vocabulary + helpers for the deep-Solidity reasoning upgrade.

A manifest item is SPECIAL-FOCUS when it touches a high-value protocol surface (gateway / checkpoint /
cross-message / subnet / collateral / signature / queue / value-transfer …). Such an item may NOT be
cleared with a thin one-line local explanation (coverage_sweep_write special-focus strong-clear rule), and
a high-risk advisory-lens hit on such a surface is routed to needs_deep_pass (advisory_escalation_gate).

This mirrors scripts/bridge_terms.py. See documentation/deep_solidity_reasoning_policy.md.

Derived from the Recall 2025-02 miss classes (depth, not language): the misses clustered on
checkpoint/quorum/collateral/queue/value-transfer functions that were examined and thin-cleared.
"""
from __future__ import annotations

import re

# High-risk protocol surfaces. Whole-word matched against name/contract/signature/tags.
SPECIAL_FOCUS_TERMS = frozenset({
    "bridge", "gateway", "checkpoint", "crossmessage", "crossmsg", "xnet", "subnet", "register",
    "leave", "release", "lock", "collateral", "signature", "signatories", "quorum", "batch",
    "queue", "withdraw", "deposit", "refund", "retry", "actor", "supply", "circulating",
    "circsupply", "custody", "stake", "unstake", "validator", "commit", "membership", "finality",
})

# A subset that, when hit HIGH-RISK by an advisory lens, must escalate to needs_deep_pass
# (advisory_escalation_gate). Intentionally the same high-value surface as the task spec.
HIGH_RISK_ESCALATION_TERMS = frozenset({
    "gateway", "checkpoint", "crossmessage", "crossmsg", "xnet", "subnet", "register", "leave",
    "release", "lock", "collateral", "signature", "quorum", "batch", "queue", "withdraw",
    "deposit", "refund", "retry", "actor", "supply", "circulating", "circsupply", "custody",
    "valuetransfer", "stake", "unstake", "bridge",
})

_WORD_RE = re.compile(r"[a-z0-9]+")
# split camelCase / PascalCase so identifiers like "commitCheckpoint" or "collateralSource" tokenize
# into whole words ({commit, checkpoint} / {collateral, source}) — avoids substring hits like lock⊂block.
_CAMEL_RE = re.compile(r"([a-z0-9])([A-Z])")


def _tokens(text: str) -> set[str]:
    split = _CAMEL_RE.sub(r"\1 \2", text or "")
    return set(_WORD_RE.findall(split.lower()))


def item_text(item: dict) -> str:
    """Concatenate the fields that describe a manifest item's surface."""
    parts = [item.get("name", ""), item.get("contract", ""), item.get("signature", "")]
    tags = item.get("tags") or []
    if isinstance(tags, (list, tuple)):
        parts += [str(t) for t in tags]
    return " ".join(parts)


def matched_terms(text: str, terms: frozenset = SPECIAL_FOCUS_TERMS) -> list[str]:
    """A term matches a token exactly, or as a token PREFIX (so 'checkpoint' matches 'checkpointing'/
    'checkpoints', 'release' matches 'released'). Prefix is anchored at the token start, so short noise
    like block⊄lock / mistake⊄stake is avoided. All terms are >=4 chars."""
    toks = _tokens(text)
    out = set()
    for t in terms:
        if t in toks:
            out.add(t)
        elif len(t) >= 4 and any(tok.startswith(t) for tok in toks):
            out.add(t)
    return sorted(out)


def is_special_focus(item: dict, high_score_threshold: int = 3,
                     advisory_high_risk_ids: set | None = None) -> bool:
    """An item is special-focus if a term matches its surface, OR its attack-surface score is high,
    OR it appears in any advisory lens's high-risk set."""
    if matched_terms(item_text(item)):
        return True
    if (item.get("attack_surface_score") or 0) >= high_score_threshold:
        return True
    if advisory_high_risk_ids and item.get("id") in advisory_high_risk_ids:
        return True
    return False


def special_focus_reason(item: dict, high_score_threshold: int = 3,
                         advisory_high_risk_ids: set | None = None) -> str:
    m = matched_terms(item_text(item))
    if m:
        return f"special-focus term(s): {', '.join(m)}"
    if (item.get("attack_surface_score") or 0) >= high_score_threshold:
        return f"high attack-surface score ({item.get('attack_surface_score')})"
    if advisory_high_risk_ids and item.get("id") in advisory_high_risk_ids:
        return "advisory lens high-risk hit"
    return ""


def is_high_risk_surface(text: str) -> bool:
    """Does this surface match the high-risk escalation term set?"""
    return bool(matched_terms(text, HIGH_RISK_ESCALATION_TERMS))
