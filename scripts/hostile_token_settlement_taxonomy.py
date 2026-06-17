#!/usr/bin/env python3
"""
hostile_token_settlement_taxonomy.py — pure (no-I/O) classifier for the HOSTILE-TOKEN SETTLEMENT research prototype.

Flags a MUST-SUCCEED settlement/cleanup flow (stop/reclaim/close/settle/liquidate/withdraw/refund/finalize/resolve/
claim/...) that pushes an attacker- or user-SELECTED token whose revert / blacklist / false-return / reentrancy can
BLOCK the cleanup step (permanent lock / DoS of another user), with NO containment (try/catch, pull-payment,
allowlist). Five-signal gate:
  S1 cleanup-verb function  AND  S2 must-succeed token push (not in try/catch)  AND  S4 missing containment  AND
  S5 counterparty recipient; S3 order/array-sourced token -> high (a bare attacker-token param -> medium).

Reject: caller's-own-asset only (recipient == msg.sender); try/catch / pull-payment / allowlist containment;
token bound to an immutable/allowlisted asset; admin-only -> downgrade to low.

RESEARCH-ONLY: the audit that uses this is read-only, is_gate:false, routes_in_production:false — never mints or
routes. High precision over recall. Scope = settlement-path hostile-token DoS ONLY (not a generic token audit).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "hostile_token_settlement_patterns.json"
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _any(text: str, terms) -> list:
    return [w for w in terms if w in text]


def classify(contract: str, name: str, signature: str, body: str, *, context: dict | None = None) -> list:
    """Return 0 or 1 hostile-token-settlement candidate for one (helper-resolved) function body. Pure."""
    cfg = _cfg()
    context = context or {}
    b = strip_comments(body or "").lower()
    sig = strip_comments(signature or "").lower()
    nlow = (name or "").lower()
    blob = b + " " + sig

    # ---- S1: cleanup / settlement flow (function name) ----
    verbs = _any(nlow, cfg.get("cleanup_verbs", []))
    if not verbs:
        return []

    # ---- S2: a must-succeed token PUSH ----
    transfers = _any(b, cfg.get("transfer_primitives", []))
    if not transfers:
        return []

    # ---- containment suppression: try/catch isolation, pull-payment, or allowlist ----
    has_trycatch = bool(_any(b, cfg.get("containment_trycatch", [])))
    has_pull = bool(_any(b, cfg.get("pull_payment_markers", [])))
    has_allowlist = bool(_any(b, cfg.get("allowlist_markers", [])))
    if has_trycatch or has_pull or has_allowlist:
        return []

    # ---- S5: must push to a genuine EXTERNAL settlement counterparty (lender/renter/recipient/to/...). If the
    # only recipient is the caller or an admin/owner (e.g. `require(msg.sender == owner); transfer(msg.sender/owner)`
    # token rescue, or a per-caller withdraw), a transfer failure harms only the caller/admin -> suppressed.
    # NOTE: `owner` is an access-control word, NOT a settlement counterparty, so it is deliberately not in the list.
    has_counterparty = bool(_any(blob, cfg.get("counterparty_terms", [])))
    if not has_counterparty:
        return []

    # ---- S3: attacker/user-selected token ----
    attacker_sourced = bool(_any(blob, cfg.get("attacker_source_markers", [])))
    immutable_asset = bool(_any(blob, cfg.get("immutable_asset_markers", [])))
    param_token = bool(_any(sig, cfg.get("param_token_markers", []))) or bool(
        re.search(r"address\s+\w*token", sig)
    )

    if immutable_asset and not attacker_sourced:
        # token bound to a trusted protocol asset, not order-selected -> not hostile-selectable
        return []

    if attacker_sourced:
        confidence = "high"
        token_source = "order/array/struct-selected token (item.token / consideration / items[])"
    elif param_token:
        confidence = "medium"
        token_source = "untrusted token parameter"
    else:
        return []

    # ---- admin-only downgrade ----
    admin_only = bool(context.get("admin_only")) or bool(_any(b, cfg.get("admin_only_terms", [])))
    if admin_only:
        confidence = "low"

    return [{
        "finding_shape": "hostile_token_settlement_dos",
        "confidence": confidence,
        "cleanup_verb": verbs[0],
        "transfer_primitive": transfers[0],
        "token_source": token_source,
        "explanation": (
            f"{contract}.{name} is a must-succeed {verbs[0]} settlement/cleanup flow that pushes a {token_source} "
            f"via {transfers[0]} to a counterparty with NO containment (no try/catch, pull-payment, or allowlist). "
            f"A hostile token (revert / blacklist / false-return / reentrancy) blocks the cleanup, permanently "
            f"locking assets or denying service to another user (reNFT H-01 / #64 / #605 class)."),
        "signals": {"S1_cleanup_verb": verbs[:3], "S2_transfer": transfers[:4],
                    "S3_attacker_sourced": attacker_sourced, "S3_param_token": param_token,
                    "S4_no_containment": True, "S5_counterparty": True},
    }]


if __name__ == "__main__":  # tiny manual smoke
    import sys
    print(json.dumps(classify("PaymentEscrow", sys.argv[1] if len(sys.argv) > 1 else "settle", "",
                              sys.stdin.read()), indent=2))
