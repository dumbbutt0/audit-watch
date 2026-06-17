#!/usr/bin/env python3
"""
spec_checklist_utils.py — anti-false-clear checklists for spec-heavy surfaces.

Revert Lend false-cleared H-01 (Permit2 received-token check) and M-14 (ERC4626 compliance) as "reviewed →
clean" with no enumerated checks. A clean clear on a known spec-heavy surface (permit/signature, ERC4626
share accounting, ERC721/1155 callbacks, oracle/liquidation) is INVALID unless the surface's checklist is
explicitly completed on the disposition. Missing → route to needs_deep_pass (strict) / warn (advisory).

Pure classification (mirrors gate_dos_utils): no I/O, no disposition writes. `classify(disp, item)` returns
the first matching surface that is incomplete.
"""
from __future__ import annotations

import re

ROUTED_STATUS = "incomplete_spec_clear"

# Each surface: (name, primary trigger regex over item name+signature+tags, required checklist fields).
# A surface's primary regex fires unconditionally. Three surfaces (reward/slippage/inflation) ALSO have a
# context-gated SECONDARY regex (see SURFACE_SECONDARY): a generic verb (transfer/_update/deposit/mint…)
# only pulls the checklist when the *run* actually has a reward layer / external markets, which keeps the
# generic-verb match FP-tight (no reward checklist demanded on a plain ERC20 transfer in a non-reward repo).
SURFACES = [
    ("permit", re.compile(r"permit2?|signature|\ballowance\b|\bapprove\b|ecrecover", re.I), [
        "token_address", "spender", "owner_signer", "nonce_deadline", "domain_separator",
        "amount_bounds", "received_vs_paid_token", "no_unintended_asset_movement",
    ]),
    ("erc4626", re.compile(r"\bdeposit\b|\bmint\b|\bwithdraw\b|\bredeem\b|preview(deposit|mint|withdraw|redeem)|"
                           r"totalassets|totalsupply|convertto(shares|assets)|max(deposit|mint|withdraw|redeem)", re.I), [
        "preview_consistency", "totalassets_supply_sync", "rounding_direction", "feeshares_order",
        "transfer_reward_accounting", "max_funcs_respected", "inflation_deflation", "zero_share",
        "nonstandard_erc20",
    ]),
    ("callback", re.compile(r"onerc721received|onerc1155received|\bcallback\b|fallback|\breceive\b", re.I), [
        "erc721_1155_path", "state_before_during_after", "collateral_config_mutation",
        "liquidation_prevention", "ownership_approval_mutation", "reentrancy_guard_scope",
        "debt_collateral_share_liquidation_impact",
    ]),
    ("oracle_liquidation", re.compile(r"\boracle\b|\btwap\b|slot0|sequencer|liquidat|\bhealth\b|\btick\b|"
                                      r"getvalue|getprice|referencepool", re.I), [
        "negative_tick_rounding", "stale_sequencer", "twap_window", "reference_pool_rounding",
        "health_boundary", "underwater_fee", "liquidator_incentive_minloan", "forced_revert_griefing",
    ]),
    # Silo M-02: reward accrual vs share mint/burn/transfer ordering on a vault/gauge/staking/incentives layer.
    # Hybra round: `claim(fees)?`/`_claimfees`/`notifyreward` added to the PRIMARY trigger so a fee-claim path
    # that can sweep the reward token (Hybra M-06 GaugeCL._claimFees) routes here. ("reward" already matches
    # notifyRewardAmount/claimRewards.)
    ("reward_accounting", re.compile(r"reward|incentive|gauge|\bstak(e|ed|ing)\b|distribut|rewarddebt|"
                                     r"rewardindex|notificationreceiver|claimreward|immediatedistribution|"
                                     r"\bclaim\b|claimfees|_claimfees|notifyreward", re.I), [
        "reward_index_update_order", "totalsupply_sync_before_accrual", "balance_snapshot_timing",
        "transfer_side_effects", "feeshares_before_after_rewards", "fee_recipient_rewards",
        "rewards_on_share_transfer", "rewards_on_mint_burn", "reward_debt_update_order",
        "incentives_loop_bounds", "totalsupply_includes_pending_feeshares",
    ]),
    # Silo M-04: missing slippage/deadline protection on deposit/withdraw/redeem/swap/router/reallocate/strategy.
    ("slippage_deadline", re.compile(r"reallocat|\bswap\b|\brouter\b|flowcap|_supply\b|supplyerc4626|"
                                     r"strateg(y|ies)?\s*(deposit|withdraw)|marketsupply", re.I), [
        "min_out_protection", "deadline_bound", "stale_quote", "market_price_movement",
        "sandwich_frontrun", "share_price_quote_exec", "market_cap_liquidity", "user_bounds_received",
        "arbitrary_route_output", "slippage_impact_attribution",
    ]),
    # Silo M-06: deflation/rounding traced beyond the user-share layer into the vault→market deposit layer.
    ("vault_market_inflation_deflation", re.compile(r"_supplyerc4626|supplytomarket|marketsupply|marketdeposit|"
                                                    r"strateg(y|ies)?\s*deposit|reallocat", re.I), [
        "user_vault_deposit_traced", "vault_market_deposit_traced", "market_rounding", "market_maxdeposit",
        "strategy_receipt_amount", "deflation_assumptions_in_scope", "donation_inflation_manipulation",
        "vault_layer_rounding_loss", "downstream_rounding_loss", "exchange_rate_premove", "loss_attribution",
    ]),
]

# Per-surface routed status (default for the 4 original surfaces is the generic ROUTED_STATUS).
SURFACE_STATUS = {
    "reward_accounting": "incomplete_reward_accounting_clear",
    "slippage_deadline": "incomplete_slippage_deadline_clear",
    "vault_market_inflation_deflation": "incomplete_vault_market_inflation_deflation_clear",
}
ROUTED_STATUSES = frozenset({ROUTED_STATUS} | set(SURFACE_STATUS.values()))

# Context-gated SECONDARY triggers: name -> (regex, context_gate_key). These fire ONLY when the run context
# flag is truthy, so a generic share-mutation / deposit verb is not enough on its own to pull a checklist.
# Hybra round: `withdraw`/`emergencywithdraw` added — a balance-zeroing exit that skips the reward checkpoint
# (Hybra M-02 GaugeV2.emergencyWithdraw) only matters in a reward-layer run, so it belongs in the gated set.
_RE_SHARE_MUT_OR_ACCRUE = re.compile(r"\baccrue|feeshares|\btransfer\b|transferfrom|\b_update\b|\b_mint\b|"
                                     r"\b_burn\b|aftertokentransfer|\bwithdraw\b|emergencywithdraw", re.I)
_RE_GENERIC_DEPOSIT = re.compile(r"\bdeposit\b|\bwithdraw\b|\bredeem\b|\bmint\b", re.I)
SURFACE_SECONDARY = {
    "reward_accounting": (_RE_SHARE_MUT_OR_ACCRUE, "has_reward_layer"),
    "slippage_deadline": (_RE_GENERIC_DEPOSIT, "has_external_markets"),
    "vault_market_inflation_deflation": (_RE_GENERIC_DEPOSIT, "has_external_markets"),
}

# Run-level context detectors (two-signal gate). A reward layer / external-market layer in the manifest is
# what licenses the secondary generic-verb triggers above.
_RE_REWARD_LAYER = re.compile(r"reward|incentive|gauge|distribut|rewarddebt|rewardindex|notificationreceiver|"
                              r"claimreward|immediatedistribution|feeshares", re.I)
_RE_EXTERNAL_MARKET = re.compile(r"market|strateg|reallocat|allocat|_supply\b|supplyerc4626|flowcap|\brouter\b|"
                                 r"\bswap\b", re.I)


def build_context(items) -> dict:
    """Detect run-level signals that license the context-gated secondary triggers. One pass over manifest
    item text (name/signature/contract/tags). `items` may be a dict's .values() or any iterable of items."""
    blob = " ".join(_item_text(i) for i in (items or []) if i)
    return {
        "has_reward_layer": bool(_RE_REWARD_LAYER.search(blob)),
        "has_external_markets": bool(_RE_EXTERNAL_MARKET.search(blob)),
    }


def _item_text(item: dict) -> str:
    parts = [item.get("name", ""), item.get("signature", "")]
    tags = item.get("tags") or []
    if isinstance(tags, (list, tuple)):
        parts += [str(t) for t in tags]
    return " ".join(parts)


# A function whose body is effectively an UNCONDITIONAL revert is disabled (e.g. a non-transferable token's
# transfer/transferFrom). Such a function may carry reward/token words but cannot move value, so it should NOT
# pull a reward checklist (the only Hybra reward FPs were RewardHYBR.transfer/transferFrom, both `revert`).
# CONSERVATIVE: we only exclude when we can SEE the body is a single revert — never on name/signature alone.
_RE_BODY = re.compile(r"\{(.*)\}", re.S)
_RE_REVERT_ONLY = re.compile(r"^\s*(revert\b[^;]*;|require\s*\(\s*(?:false|0)\b[^;]*;)\s*$", re.S)


def _body_is_unconditional_revert(src: str) -> bool:
    """True iff the function body is exactly one unconditional `revert ...;` / `require(false ...);` and
    nothing else (comments/whitespace ignored). Pure; conservative — unknown/absent body → False."""
    if not src or "{" not in src:
        return False
    m = _RE_BODY.search(src)
    if not m:
        return False
    body = re.sub(r"//.*", "", m.group(1))          # drop line comments
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)  # drop block comments
    return bool(_RE_REVERT_ONLY.match(body.strip()))


def is_disabled_revert(item: dict) -> bool:
    """A manifest item is a disabled/unconditional-revert function when explicitly flagged (`disabled_revert`)
    or when its source snippet (if the manifest carries one) is a single revert. Absent evidence → False."""
    if not item:
        return False
    if item.get("disabled_revert") is True:
        return True
    src = item.get("source") or item.get("body") or ""
    return _body_is_unconditional_revert(src)


def _field(disp: dict, surface: str, name: str):
    """Read a checklist field flat on the disposition or nested under `<surface>_checklist` / `spec_checklist`."""
    for key in (f"{surface}_checklist", "spec_checklist"):
        block = disp.get(key)
        if isinstance(block, dict) and str(block.get(name) or "").strip():
            return block.get(name)
    return disp.get(name)


def _surface_matches(name: str, rx, text: str, context: dict) -> bool:
    if rx.search(text):
        return True
    sec = SURFACE_SECONDARY.get(name)
    if sec:
        sec_rx, gate = sec
        if context.get(gate) and sec_rx.search(text):
            return True
    return False


def surfaces_for(item: dict, context: dict | None = None) -> list[str]:
    context = context or {}
    if is_disabled_revert(item):
        return []
    text = _item_text(item)
    return [name for name, rx, _ in SURFACES if _surface_matches(name, rx, text, context)]


def classify(disp: dict, item: dict, context: dict | None = None) -> dict:
    """
    Return {status, surface, missing}.
      status: no_spec_surface | ok | incomplete_spec_clear | incomplete_<surface>_clear
    Reports the FIRST matching surface that is incomplete (so one fix at a time is actionable). `context`
    (from build_context) licenses the context-gated secondary triggers for reward/slippage/inflation.
    """
    if not item:
        return {"status": "no_spec_surface", "surface": None, "missing": []}
    if is_disabled_revert(item):
        return {"status": "no_spec_surface", "surface": None, "missing": []}
    context = context or {}
    text = _item_text(item)
    matched_any = False
    for name, rx, fields in SURFACES:
        if not _surface_matches(name, rx, text, context):
            continue
        matched_any = True
        missing = [f for f in fields if not str(_field(disp, name, f) or "").strip()]
        if missing:
            return {"status": SURFACE_STATUS.get(name, ROUTED_STATUS), "surface": name, "missing": missing}
    if not matched_any:
        return {"status": "no_spec_surface", "surface": None, "missing": []}
    return {"status": "ok", "surface": None, "missing": []}


def is_routed(status: str) -> bool:
    return status in ROUTED_STATUSES


def reason(cls: dict) -> str:
    st = cls.get("status", ROUTED_STATUS)
    return (f"{st} on {cls['surface']} surface: missing checklist item(s) "
            f"{', '.join(cls['missing'])} — a 'reviewed → clean' result is invalid here without the "
            f"completed {cls['surface']} checklist; complete it or file a finding")
