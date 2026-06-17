#!/usr/bin/env python3
"""
waiver_utils.py — waiver risk discipline.

Revert Lend waived 7 transformer/automator clusters as whole clusters; they held H-04 (V3Utils.execute,
an external-call entrypoint) + ~6 Mediums. A cluster-level waiver is a recall hole when the cluster contains
high-risk surfaces. This module classifies the risk class of a manifest item and validates that a high-risk
item is waived PER-FUNCTION/PER-SINK (with a real no-impact justification + an answer-independent reviewer +
a follow-up marker), not swept under a broad cluster waiver.

Pure classification + validation; no I/O, no disposition writes (mirrors dependency_clear_utils / gate_dos_utils).
"""
from __future__ import annotations

import re

# A manifest item is high-risk to waive if its surface is any of these classes. Ordered: first match wins.
RISK_CLASS_PATTERNS = [
    ("callback",        re.compile(r"onerc(721|1155)received|\bcallback\b|fallback|uniswapv3(swap|mint|flash)callback", re.I)),
    ("permit_signature",re.compile(r"permit2?|signature|\becrecover\b|\ballowance\b", re.I)),
    ("transformer_exec",re.compile(r"\btransform\b|\bexecute\b|executewith", re.I)),
    ("liquidation",     re.compile(r"liquidat|\bseize\b|\bhealth\b|\bsolven", re.I)),
    ("oracle_read",     re.compile(r"\boracle\b|getvalue|getprice|slot0|\btwap\b|observe|referencepool", re.I)),
    ("vault_accounting",re.compile(r"\bdeposit\b|\bwithdraw\b|\bmint\b|\bredeem\b|\bborrow\b|\brepay\b|share|exchangerate|totalassets|globalinterest|"
                                   r"reallocat|allocat|flowcap|flow\s*cap|supply\s*cap|maxdeposit|market\s*cap|marketcap", re.I)),
    ("token_transfer",  re.compile(r"safetransfer|\btransfer\b|transferfrom|sendvalue|\.call\b", re.I)),
    ("access_init",     re.compile(r"\binit\b|initialize|\bowner\b|\badmin\b|\brole\b|setoperator|setwithdrawer|onlyowner", re.I)),
]
HIGH_RISK_CLASSES = {c for c, _ in RISK_CLASS_PATTERNS}

# Per-sink waiver must answer all of these (a high-risk item is not waived on a one-line note).
REQUIRED_WAIVER_FIELDS = [
    "function",                    # which function/sink
    "sink",                        # the concrete external call / state mutation being waived
    "risk_class",                  # one of HIGH_RISK_CLASSES
    "reason",                      # why it is being deferred
    "no_impact_justification",     # why no user funds / protocol liveness / privilege boundary can be affected
    "answer_independent_reviewer", # who reviewed it without the answer key
    "follow_up",                   # expiration date or follow-up marker
]

BLOCKED_STATUS = "high_risk_waiver_blocked"
INCOMPLETE_STATUS = "waiver_requires_per_sink_justification"
RECALL_RISK_STATUS = "waiver_recall_risk"


def risk_class(item: dict) -> str:
    """Return the high-risk waiver class for a manifest item, or 'none'."""
    if not item:
        return "none"
    kind = item.get("kind")
    # constants/immutables are config values, not high-risk sinks
    if kind in ("constant", "immutable", "address", "magic_number"):
        return "none"
    if item.get("external_calls"):
        # an external-call entrypoint is always high-risk regardless of name
        text = _item_text(item)
        for cls, rx in RISK_CLASS_PATTERNS:
            if rx.search(text):
                return cls
        return "external_call"
    text = _item_text(item)
    for cls, rx in RISK_CLASS_PATTERNS:
        if rx.search(text):
            return cls
    return "none"


def is_high_risk(item: dict) -> bool:
    return risk_class(item) != "none"


def _item_text(item: dict) -> str:
    parts = [item.get("name", ""), item.get("signature", ""), item.get("contract", "")]
    tags = item.get("tags") or []
    if isinstance(tags, (list, tuple)):
        parts += [str(t) for t in tags]
    return " ".join(parts)


def validate_per_sink_waiver(w: dict) -> tuple[bool, list[str]]:
    """A per-sink waiver must answer every REQUIRED_WAIVER_FIELD. Returns (ok, missing_fields)."""
    if not isinstance(w, dict):
        return False, list(REQUIRED_WAIVER_FIELDS)
    missing = [f for f in REQUIRED_WAIVER_FIELDS if not str(w.get(f) or "").strip()]
    return (not missing), missing
