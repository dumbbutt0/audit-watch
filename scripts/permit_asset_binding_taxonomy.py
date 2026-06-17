#!/usr/bin/env python3
"""
permit_asset_binding_taxonomy.py — pure (no-I/O) classifier for the PERMIT2 ASSET-BINDING research prototype
(Shape A only). Seeded/anchored on Revert Lend H-01 (#368): V3Vault consumes permit2.permitTransferFrom but never
asserts permit.permitted.token == asset, so a Permit2 signature for a worthless ERC-20 is credited as the vault
asset.

Shape A: a permit/Permit2-authorized transfer is consumed by protocol logic that has a SINGLE expected asset, and
NO equality binding between the permit's token and that expected asset is observed. Three-signal AND gate:
  S1 permit-consume  AND  S2 single bound-asset  AND  S3 missing-binding
then suppressions (router / library-primitive / explicit-validation / asset-agnostic param-token).

RESEARCH-ONLY: the audit that uses this is read-only, is_gate:false, routes_in_production:false — never mints or
routes. High precision over recall (false negatives accepted; high-confidence FPs not). This detector does NOT
detect replay / front-running / recipient / witness / approval-reuse / ERC2771 / msg.value / multicall.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "permit_asset_binding_patterns.json"
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
    """True iff the text contains a genuine permit/Permit2 *consumption* call (not just a type/ref). Used by the
    audit to gate S1 on a function's OWN body so non-consuming callers of a permit helper are not flagged."""
    t = strip_comments(text or "").lower()
    return bool(_any(t, _t("s1_permit_consume", [])))


def classify(name: str, signature: str, file: str, contract: str, snippet: str = "",
             kind: str = "function", tags=None) -> list:
    """Return a LIST with 0 or 1 Shape-A candidate. Pure; snippet is the (helper-resolved) body."""
    body = strip_comments(snippet or "").lower()
    sig = strip_comments(signature or "").lower()
    nlow = (name or "").lower()
    clow = (contract or "").lower()
    flow = (file or "").lower()
    blob = body + " " + sig

    # ---- S1: permit / Permit2 consumption ----
    s1_terms = _any(blob, _t("s1_permit_consume", []))
    if not s1_terms:
        return []

    # ---- suppression: generic permit primitive / helper library (not an integrator) ----
    lib_names = _t("suppress_library_contracts", [])
    if kind == "library" or clow in lib_names or any(clow == n for n in lib_names):
        return []
    # a contract whose name *is* a permit primitive (SelfPermit/ERC20Permit/Permit2…) is the primitive, not a user
    if any(clow == n or clow.endswith(n) for n in lib_names):
        return []

    # ---- suppression: multi-asset router / aggregator / bridge (by name) ----
    router_names = _t("suppress_router_names", [])
    router_by_name = any(r in clow for r in router_names) or any(r in flow for r in router_names)

    # ---- suppression: asset-agnostic — transferred token comes from a caller-supplied token/path param ----
    param_token = any(p in sig for p in _t("suppress_param_token_terms", []))

    # ---- S2: single protocol-bound expected asset present in scope ----
    asset_terms = _t("s2_bound_asset", [])
    # word-boundary match so 'asset' matches but not e.g. random substrings; allow asset()/_asset/i_asset
    s2_hits = [a for a in asset_terms if re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", blob)
               or a in ("asset()", "_asset", "i_asset") and a in blob]
    has_bound_asset = bool(s2_hits)
    strong_asset = bool(_any(blob, _t("s2_strong_asset", []))) or "asset()" in blob or "immutable" in blob \
        or "ierc20(asset" in blob
    # an explicit ERC20()/IERC20(asset) wrap or asset() getter is a strong single-asset signal
    if "ierc20(asset" in blob or "asset()" in blob:
        strong_asset = True

    if router_by_name or param_token or not has_bound_asset:
        # asset-agnostic / router / no bound asset -> not Shape A
        return []

    # ---- S3: is a permit-token == asset binding present? (presence -> suppress) ----
    binding_present = bool(_any(blob, _t("s3_binding_present", [])))
    # also treat a comparison mentioning permitted token near 'asset' as a binding
    if "permitted.token" in blob and re.search(r"permitted\.token\s*[!=]=", blob):
        binding_present = True
    if binding_present:
        return []   # explicit validation -> safe, no candidate

    # ---- confidence ----
    if strong_asset:
        confidence = "high"
    elif has_bound_asset:
        confidence = "medium"
    else:
        confidence = "low"

    permit_source = s1_terms[0]
    expected_asset_source = ("asset() getter" if "asset()" in blob
                             else "IERC20(asset)" if "ierc20(asset" in blob
                             else "immutable/state asset var" if "immutable" in blob
                             else f"bound-asset ref ({s2_hits[0]})")
    explanation = (f"{name} consumes a permit/Permit2 transfer ({permit_source}) into a protocol with a single "
                   f"expected asset ({expected_asset_source}) but never asserts the permit's token equals that "
                   f"asset (no permitted.token == asset / InvalidToken check) — a Permit2 signature for a "
                   f"different ERC-20 could be credited as the protocol asset (Shape A, Revert Lend #368 class).")

    return [{
        "finding_shape": "permit_asset_binding_missing",
        "confidence": confidence,
        "permit_source": permit_source,
        "expected_asset_source": expected_asset_source,
        "missing_binding_explanation": explanation,
        "suppression_status": "none",
        "signals": {"S1_permit_consume": s1_terms[:4], "S2_bound_asset": s2_hits[:4],
                    "S3_binding_present": False},
    }]


if __name__ == "__main__":  # tiny manual smoke
    import sys
    print(json.dumps(classify(sys.argv[1] if len(sys.argv) > 1 else "deposit", "", "f.sol", "Vault",
                              snippet=sys.stdin.read()), indent=2))
