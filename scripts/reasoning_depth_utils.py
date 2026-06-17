#!/usr/bin/env python3
"""
reasoning_depth_utils.py — pure classifier for the P245 rejection depth-record gate (#4).

triage_write.py already enforces a "no-silent-clear" rule for safety-net code. This module generalizes
that idea to the P244 sensitive-area list: a candidate that touches a sensitive area may not be REJECTED
unless it carries a completed depth record (source/defense anchors + attacker/impact path + state
timeline + why the defense fully covers the issue). On an incomplete record the gate REROUTES the
candidate to human review (needs_depth) — it NEVER mints, auto-submits, or relabels a finding. It is
recall-protective only.

Design mirrors gate_dos_utils.py: pure classification, no I/O. The caller (triage_write.py) only invokes
this when coverage_policy.rejection_depth_record_enforced=true (default-off).
"""
from __future__ import annotations

import re

# Sensitive areas (P244 spec). Each maps to a list of substrings; classification is conservative —
# a decision is "sensitive" only when its text matches one of these area cues OR it declares the area
# explicitly via decision["sensitive_areas"].
SENSITIVE_AREAS: dict[str, tuple[str, ...]] = {
    "callbacks/hooks": ("callback", "hook", "onerc721received", "onerc1155received", "onerc777",
                        "beforetokentransfer", "aftertokentransfer", "fallback", "receive(",
                        "reentr"),
    "permit/signature": ("permit", "signature", "ecrecover", "eip712", "eip-712", "digest",
                         "sigutil", "sign ", "signed"),
    "safe/module/guard": ("gnosis safe", "safe guard", "checktransaction", "setguard",
                          "setfallbackhandler", "enablemodule", "disablemodule", "module guard",
                          " guard ", "fallback handler"),
    "oracle freshness": ("oracle", "stale", "staleness", "heartbeat", "answeredinround",
                         "updatedat", "latestrounddata", "chainlink", "price feed", "twap"),
    "reward/emission": ("reward", "emission", "gauge", "notifyreward", "accrue", "checkpoint",
                        "ve(3,3)", "vetoken", "bribe"),
    "vault/share conversion": ("convertto", "previewredeem", "previewdeposit", "previewmint",
                               "previewwithdraw", "maxredeem", "maxwithdraw", "share price",
                               "totalassets", "erc4626", "erc-4626", "inflation attack"),
    "liquidation": ("liquidat", "seize", "bad debt", "underwater", "health factor", "collateral seiz"),
    "cross-chain settlement": ("cross-chain", "crosschain", "bridge", "l1", "l2", "xdomain",
                               "message", "consumemessage", "relayer"),
    "token settlement": ("settlement", "settle", "_settlepayment", "payout", "transfer-on-",
                         "fee-on-transfer", "blacklist", "weird token", "return false"),
    "diamond facets": ("facet", "selector", "diamond", "diamondcut", "delegatecall"),
    "lifecycle registration": ("register", "create-time", "creation", "lifecycle", "mint before",
                               "registration", "initialize", "create position"),
}

# Fields a depth record must answer before a sensitive-area candidate can be REJECTED.
DEPTH_FIELDS = (
    "source_anchors",          # file:line anchors of the relevant code
    "defense_anchors",         # exact defense location(s)
    "attacker_path",           # how the attacker reaches/triggers it
    "impact_path",             # what the resulting loss/impact would be
    "state_timeline",          # pre-state -> steps -> post-state for stateful bugs
    "defense_fully_covers_reason",  # exact reason the defense fully covers the path
)


def _haystack(decision: dict) -> str:
    return " ".join(str(decision.get(k) or "") for k in
                    ("title", "decision_reason", "vuln_type", "category", "description",
                     "follow_up_packet")).lower()


def sensitive_areas(decision: dict) -> set[str]:
    """
    Return the set of sensitive areas this decision touches.

    Prefers an explicit decision["sensitive_areas"] (list) when present; otherwise classifies
    conservatively from the decision text.
    """
    explicit = decision.get("sensitive_areas")
    if isinstance(explicit, (list, tuple, set)):
        return {a for a in explicit if a in SENSITIVE_AREAS}
    text = _haystack(decision)
    hits: set[str] = set()
    for area, cues in SENSITIVE_AREAS.items():
        if any(c in text for c in cues):
            hits.add(area)
    return hits


def _record(decision: dict) -> dict:
    """Read the depth record from decision['depth_record'] or flat keys on the decision."""
    rec = decision.get("depth_record")
    return rec if isinstance(rec, dict) else decision


def depth_record_complete(decision: dict) -> tuple[bool, list[str]]:
    """Return (complete, missing_fields). complete=True only when every DEPTH_FIELD is non-empty."""
    rec = _record(decision)
    missing = [f for f in DEPTH_FIELDS if not str(rec.get(f) or "").strip()]
    return (not missing), missing


def classify_rejection(decision: dict) -> dict:
    """
    For a candidate proposed for rejection, decide whether it may be rejected.

    Returns {status, areas, missing}:
      status = "not_sensitive"  -> ordinary rejection allowed (gate does nothing)
               "ok"             -> sensitive but depth record complete -> rejection allowed
               "needs_depth"    -> sensitive AND depth record incomplete -> reroute to human review
    """
    areas = sensitive_areas(decision)
    if not areas:
        return {"status": "not_sensitive", "areas": [], "missing": []}
    complete, missing = depth_record_complete(decision)
    if complete:
        return {"status": "ok", "areas": sorted(areas), "missing": []}
    return {"status": "needs_depth", "areas": sorted(areas), "missing": missing}


def reroute_reason(cls: dict) -> str:
    return (f"sensitive-area rejection missing depth record: {', '.join(cls['missing'])} "
            f"(areas: {', '.join(cls['areas'])}) — complete the depth record (attacker path, "
            f"defense anchors, state timeline, why the defense fully covers it) or keep investigating")
