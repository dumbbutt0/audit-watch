#!/usr/bin/env python3
"""
erc4626_limit_fidelity_taxonomy.py — pure (no-I/O) helpers + classifier for the ERC4626 LIMIT-FIDELITY research lens.

Generalized CLASS of the P302 pooltogether M-02/M-03/M-07 misses: an ERC4626 wrapper's max*/limit function is not
faithful to the action it bounds. Two sub-shapes:
  (i) LIMIT-vs-ACTION primitive mismatch:
      (a) a max{Deposit,Mint,Withdraw,Redeem} bounds via the underlying max{X} but the paired action calls a
          DIFFERENT underlying primitive (e.g. maxDeposit uses yieldVault.maxDeposit, deposit path uses
          yieldVault.mint) -> advertised max not fulfillable (M-03).
      (b) a max-withdraw/redeem bounds via a vault convertToAssets/convertToShares wrapping a vault maxRedeem/
          maxWithdraw -> cross-basis estimate that may not match the action's redemption rounding (M-02).
  (ii) CAP omits accrued claimable: a deposit/mint cap is computed from a base supply but a separately-accrued
       mintable balance (yieldFeeBalance/accruedFees/pendingRewards) that also consumes that cap is not subtracted
       -> cap over-reports (M-07).

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes. High precision over
recall. The cross-function correlation is performed by the audit runner; this module is pure (per-limit classify
+ small helpers). Sub-shape (i) uses the helper-resolved body; sub-shape (ii) uses the limit fn's OWN body.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "erc4626_limit_fidelity_patterns.json"
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
# the M-02 shape: a vault convertTo* whose ARGUMENT contains a vault max* (cross-basis estimate of the max),
# e.g. yieldVault.convertToAssets(yieldVault.maxRedeem(...)). Co-occurrence alone (e.g. totalAssets'
# convertToAssets(balanceOf(...)) next to an unrelated maxDeposit) must NOT match.
_CONVERTED_MAX_RE = re.compile(r"convertto(?:assets|shares)\s*\(\s*[a-z0-9_.]*max(?:redeem|withdraw|deposit|mint)\b")


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key: str, default):
    return _cfg().get(key, default)


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def vault_primitives(body: str) -> set:
    """Return the set of ERC4626 primitives called on a VAULT ref (`yieldVault.maxDeposit(` etc.) in `body`.
    Requires a vault-ref prefix so the wrapper's OWN convertToAssets/previewDeposit are not counted."""
    b = strip_comments(body or "").lower()
    refs = _t("vault_refs", [])
    prims = list(_t("estimate_primitives", [])) + list(_t("action_primitives", []))
    found = set()
    for ref in refs:
        for p in prims:
            if ref + p + "(" in b:
                found.add(p)
    return found


def reads_supply_cap(body: str) -> bool:
    b = strip_comments(body or "").lower()
    return any(t in b for t in _t("supply_cap_terms", []))


def reads_claimable(body: str) -> bool:
    b = strip_comments(body or "").lower()
    return any(t in b for t in _t("claimable_terms", []))


def classify_limit(name: str, contract: str, own_body: str, resolved_body: str,
                   deposit_actions: set, withdraw_actions: set, contract_has_claimable: bool) -> list:
    """Return 0..N candidates for one max*/limit function. Pure."""
    nlow = (name or "").lower()
    if nlow not in _t("limit_fns", []):
        return []
    rb = strip_comments(resolved_body or "").lower()
    rprims = vault_primitives(rb)
    out = []

    # ---- (i)-b: converted cross-basis max estimate — a vault convertTo* WRAPPING a vault max* ----
    if _CONVERTED_MAX_RE.search(rb):
        out.append({
            "finding_shape": "erc4626_limit_converted_max_estimate",
            "sub_shape": "i_b_converted_basis", "confidence": "high",
            "explanation": (f"{name} bounds the limit via a vault convertToAssets/convertToShares wrapping a vault "
                            f"max-redeem/withdraw — a cross-basis (asset<->share) estimate that need not match the "
                            f"action's actual redemption rounding, so the advertised max can over-report / revert "
                            f"at the boundary (pooltogether M-02 class)."),
            "signals": {"vault_primitives": sorted(rprims)},
            "suppression_status": "none",
        })

    # ---- (i)-a: limit uses underlying max{verb} but the paired action uses a different underlying primitive ----
    cp = _t("verb_counterpart", {}).get(nlow)          # maxdeposit -> deposit
    if cp and nlow in rprims:                            # the limit genuinely calls the underlying max{verb}
        actions = deposit_actions if cp in ("deposit", "mint") else withdraw_actions
        if actions and cp not in actions:
            other = sorted(a for a in actions if a in ("deposit", "mint", "redeem", "withdraw"))
            out.append({
                "finding_shape": "erc4626_limit_action_primitive_mismatch",
                "sub_shape": "i_a_primitive_mismatch", "confidence": "high",
                "explanation": (f"{name} bounds via underlying {nlow}() (expects the action to use {cp}()), but the "
                                f"paired action path uses underlying {other or 'a different primitive'} instead — the "
                                f"advertised max is computed against a primitive the action never uses, so it is not "
                                f"actually fulfillable (pooltogether M-03 class)."),
                "signals": {"limit_primitive": nlow, "expected_action": cp, "action_primitives": sorted(actions)},
                "suppression_status": "none",
            })

    # ---- (ii): deposit/mint cap omits a separately-accrued claimable that also consumes the cap ----
    if nlow in ("maxdeposit", "maxmint") and contract_has_claimable:
        ob = strip_comments(own_body or "").lower()
        if reads_supply_cap(ob) and not reads_claimable(ob):
            out.append({
                "finding_shape": "erc4626_cap_omits_accrued_claimable",
                "sub_shape": "ii_cap_omits_claimable", "confidence": "medium",
                "explanation": (f"{name} computes a deposit/mint supply cap from a base supply but the contract has a "
                                f"separately-accrued mintable claimable (fee/reward) balance that also consumes the "
                                f"same cap and is not subtracted, so the cap over-reports (pooltogether M-07 class)."),
                "signals": {"supply_cap_in_body": True, "claimable_referenced": False},
                "suppression_status": "none",
            })

    return out
