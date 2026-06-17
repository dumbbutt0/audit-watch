#!/usr/bin/env python3
"""
erc4626_share_accounting_taxonomy.py — pure (no-I/O) classifier for the EIP-4626 SHARE-ACCOUNTING research family
(NARROW). In an ERC-4626 vault context, flags a max/limit/preview function that uses an APPROXIMATE
convertToAssets/convertToShares (or wraps an external maxRedeem/maxDeposit in convertTo*) instead of the
EIP-4626-mandated exact preview* — so max*/preview* over/under-reports (4626 non-compliance / integration breakage).

Two-signal gate: S1 is-4626 context (passed by the runner per contract) + S2 convertTo*-in-max/limit/preview misuse.
Anchor: PoolTogether M-02 (PrizeVault._maxYieldVaultWithdraw = yieldVault.convertToAssets(maxRedeem())).

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false. Precision over recall; narrow scope.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "erc4626_share_accounting_patterns.json"
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


def is_4626_contract(contract_blob: str) -> bool:
    """S1: does the contract look like an ERC-4626 vault? (computed from the whole contract by the runner)."""
    b = strip_comments(contract_blob or "").lower()
    cfg = _cfg()
    if "ierc4626" in b:
        return True
    if all(t in b for t in cfg.get("is4626_pair_a", [])):
        return True
    if all(t in b for t in cfg.get("is4626_pair_b", [])):
        return True
    return False


def classify(contract: str, name: str, signature: str, body: str, *, is4626: bool = False, context=None) -> list:
    """Return 0 or 1 ERC-4626 share-accounting candidate for one function. Pure. `is4626` supplied by the runner."""
    cfg = _cfg()
    context = context or {}
    if not is4626:
        return []
    raw = (body or "").lower()  # keep comments for documented-behavior (NatSpec) suppression
    b = strip_comments(body or "").lower()
    nlow = (name or "").lower()

    # ---- function must be a max / limit / preview function ----
    if not any(k in nlow for k in cfg.get("max_limit_preview_fn", [])):
        return []

    # ---- documented-behavior suppression (checked on raw body incl. comments) ----
    if _any(raw, cfg.get("suppress_documented", [])):
        return []

    # ---- S2: approximate convertTo* used where preview* is mandated ----
    convert_hits = _any(b, cfg.get("approx_convert_calls", []))
    if not convert_hits:
        return []

    # P242 fix (precision): require the EXTERNAL-max wrapper pattern (the M-02 anchor shape:
    # externalVault.convertToAssets(externalVault.maxRedeem())). A bare preview*/max* that uses its OWN convertTo*
    # is the common, usually-compliant 4626 pattern -> broad noise across every vault -> suppressed.
    wraps_external_max = bool(_any(b, cfg.get("external_max_calls", [])))
    if not wraps_external_max:
        return []
    confidence = "high"
    fn_kind = ("max/limit" if any(k in nlow for k in ("max", "limit")) else "preview")

    return [{
        "finding_shape": "erc4626_convert_in_max_misuse",
        "confidence": confidence,
        "function_kind": fn_kind,
        "approx_call": convert_hits[0],
        "wraps_external_max": wraps_external_max,
        "explanation": (
            f"{contract}.{name} is an ERC-4626 {fn_kind} function that uses the APPROXIMATE {convert_hits[0]} "
            f"{'wrapping an external max* redemption ' if wraps_external_max else ''}instead of the EIP-4626-mandated "
            f"exact preview* — so it may over/under-report, breaking 4626 compliance and downstream integrations "
            f"(PoolTogether M-02 class)."),
        "signals": {"S1_is4626": True, "S2_approx_convert": convert_hits[:2],
                    "S2_wraps_external_max": wraps_external_max, "fn": name},
    }]


if __name__ == "__main__":  # tiny manual smoke
    import sys
    print(json.dumps(classify("V", sys.argv[1] if len(sys.argv) > 1 else "maxWithdraw", "", sys.stdin.read(),
                              is4626=True), indent=2))
