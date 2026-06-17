#!/usr/bin/env python3
"""
nonstandard_permit_taxonomy.py — pure (no-I/O) classifier for the NON-STANDARD PERMIT research lens.

Generalized CLASS of the P302 pooltogether M-08 miss: a contract hard-codes the EIP-2612 7-arg
`permit(owner,spender,value,deadline,v,r,s)` interface against a CONFIGURABLE/external asset and provides NO
resilience (no try/catch, no Permit2 / DAI-allowed fallback). Such a permit path REVERTS for non-2612 assets
(DAI allowed/nonce-based, no-permit tokens) -> deposit/permit DoS.

Three-signal AND gate:  S1 EIP-2612 permit consumption  AND  S2 configurable/external permitted asset  AND
S3 missing resilience.  Then suppressions (self/own-share-token · router/param-token · permit-primitive library).

RESEARCH-ONLY: the audit that uses this is read-only, is_gate:false, routes_in_production:false — never mints or
routes. High precision over recall (false negatives accepted; high-confidence FPs not). Anchored on
PrizeVault.depositWithPermit (PrizeVault.sol:524-546). Does NOT detect permit replay / front-run / asset-binding
(see permit_asset_binding) / signature malleability.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "nonstandard_permit_patterns.json"
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key: str, default: list) -> tuple:
    return tuple(_cfg().get(key, default))


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _any(text: str, terms) -> list:
    return [w for w in terms if w in text]


def has_permit_consumption(text: str) -> bool:
    """True iff the text genuinely CONSUMES a permit (.permit( call or an IERC20Permit wrap), used by the audit to
    gate S1 on a function's OWN body so a non-consuming caller of a permit helper is not flagged."""
    t = strip_comments(text or "").lower()
    return ".permit(" in t or "ierc20permit(" in t


def classify(name: str, signature: str, file: str, contract: str, snippet: str = "",
             kind: str = "function", tags=None) -> list:
    """Return a LIST with 0 or 1 non-standard-permit candidate. Pure; snippet is the (helper-resolved) body."""
    body = strip_comments(snippet or "").lower()
    sig = strip_comments(signature or "").lower()
    clow = (contract or "").lower()
    flow = (file or "").lower()
    blob = body + " " + sig

    # ---- S1: EIP-2612 permit consumption (a .permit( call / IERC20Permit wrap) + the 2612 7-arg fingerprint ----
    if ".permit(" not in blob and "ierc20permit(" not in blob:
        return []
    fingerprint = _any(blob, _t("s1_2612_fingerprint", []))
    # require either an IERC20Permit wrap OR the value+deadline+v/r/s shape so we don't fire on Permit2-only flows
    if "ierc20permit(" not in blob and len(fingerprint) < 2:
        return []

    # ---- suppression: the permit primitive itself (library / primitive-named contract) ----
    lib_names = _t("suppress_library_contracts", [])
    if kind == "library" or any(clow == n or clow.endswith(n) for n in lib_names):
        return []

    # ---- suppression: router / aggregator / caller-supplied token param (asset-agnostic) ----
    router_by_name = any(r in clow for r in _t("suppress_router_names", [])) \
        or any(r in flow for r in _t("suppress_router_names", []))
    param_token = any(p in sig for p in _t("suppress_param_token_terms", []))
    if router_by_name or param_token:
        return []

    # ---- suppression: permit on the contract's OWN 2612 share token (self) ----
    if any(s in blob for s in _t("suppress_self_token", [])):
        return []

    # ---- S2: the permitted token is a configurable / external asset (not a fixed own token) ----
    asset_terms = _t("s2_external_asset", [])
    s2_hits = [a for a in asset_terms if a in blob]
    if not s2_hits:
        return []
    strong_asset = bool(_any(blob, _t("s2_strong_external_asset", [])))

    # ---- S3: resilience present? (try/catch, Permit2 fallback, DAI-allowed path) -> suppress ----
    if _any(blob, _t("s3_resilience_present", [])):
        return []

    # ---- confidence: high when the permit explicitly wraps the configurable asset (IERC20Permit(address(_asset))) ----
    explicit_wrap = "ierc20permit(address(_asset" in blob or "ierc20permit(address(asset" in blob \
        or "ierc20permit(address(underlying" in blob
    confidence = "high" if explicit_wrap else ("medium" if strong_asset else "low")

    asset_src = ("IERC20Permit(address(asset))" if explicit_wrap
                 else "immutable/external asset ref" if strong_asset
                 else f"external-asset ref ({s2_hits[0]})")
    explanation = (f"{name} hard-codes the EIP-2612 permit(owner,spender,value,deadline,v,r,s) interface on a "
                   f"configurable/external asset ({asset_src}) with no try/catch and no Permit2 / DAI-allowed "
                   f"fallback. A non-standard-permit asset (DAI allowed/nonce-based, or a no-permit token) makes "
                   f"this revert, blocking the permit/deposit path (pooltogether M-08 class).")

    return [{
        "finding_shape": "nonstandard_permit_hardcoded",
        "confidence": confidence,
        "permitted_asset_source": asset_src,
        "missing_resilience_explanation": explanation,
        "suppression_status": "none",
        "signals": {"S1_2612_fingerprint": (["IERC20Permit"] if "ierc20permit(" in blob else []) + fingerprint[:4],
                    "S2_external_asset": s2_hits[:4], "S3_resilience_present": False},
    }]


if __name__ == "__main__":  # tiny manual smoke
    import sys
    print(json.dumps(classify(sys.argv[1] if len(sys.argv) > 1 else "depositWithPermit", "", "f.sol", "Vault",
                              snippet=sys.stdin.read()), indent=2))
