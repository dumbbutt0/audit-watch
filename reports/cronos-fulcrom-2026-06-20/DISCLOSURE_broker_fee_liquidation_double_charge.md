> ⚠ DRAFT — review, edit into your own words, and submit via HackenProof (the Cronos program channel).
> Per the program rules ("No vulnerability disclosure… outside of the program without express consent"),
> do NOT send this directly to the team or post it publicly — route it through HackenProof.
> This is a LATENT issue: it is NOT exploitable on the current deployment (see "Current reachability").
> Submitting it is good-faith hardening, not a claim for a Critical reward under the current state.

# Fulcrom Vault — broker fee is charged a second time at liquidation (latent permissionless `feeReserves` drain)

**Target:** Fulcrom `Vault` — proxy `0x8C7Ef34aa54210c76D6d5E475f43e0c11f876098`,
implementation `0xA66a0FEA27FB0a6f115be2B6FEcA472635594672` (Cronos EVM, Solidity 0.8.17)
**Category (HackenProof VRT):** Smart Contract › Business Logic Errors (fee accounting / fund drain)
**Severity:** Latent Critical (real permissionless loss-of-funds; **currently unreachable** — see below)
**Status:** No exploit performed. Findings derived from the verified source + read-only `eth_call` state reads only.
**Note:** This is a **Fulcrom-specific addition**, not a property of upstream GMX — the broker-fee mechanism does
not exist in canonical GMX, so this is not a "previously known GMX/fork" issue.

## Summary
Fulcrom adds a user-supplied "broker fee" to positions (`increasePositionV2` stores `position.brokerAddress`
and `position.brokerFeeBasisPoints`). The fee is correctly charged once at position open (paid from the
trader's own collateral). However, it is charged **again at liquidation**, computed on the **full
`position.size`**, transferred out to the (caller-controlled) broker address, and deducted from the global
`feeReserves`. Since a liquidated position has ~zero remaining collateral, this second payout is **unbacked** —
it is drawn from protocol fee reserves / the pool. Combined with the fact that `brokerFeeBasisPoints` is
**uncapped** and unvalidated at open, an attacker who sets `brokerAddress` to their own address can extract a
net profit from `feeReserves` on each liquidation, repeatably and permissionlessly.

## Root cause
**Second charge at liquidation** — `Vault.liquidatePosition(...)`:

```solidity
// transfer out broker fee during liquidation process
if (position.brokerAddress != address(0) && position.brokerFeeBasisPoints > 0) {
    (, uint256 brokerFeeAmount) = _chargeBrokerFee(position.size, _collateralToken,
                                                   position.brokerAddress, position.brokerFeeBasisPoints);
    // update fee reserve if transfer out since added from validateLiquidation step
    feeReserves[_collateralToken] = feeReserves[_collateralToken] - brokerFeeAmount;
}
```

`_chargeBrokerFee` does `_transferOut(_collateralToken, brokerFeeAmount, _brokerAddress)` — paying the broker
real tokens from the Vault — and `brokerFeeAmount` is computed on the **full position size**.

**No cap / no validation:**
- `VaultUtils.getBrokerFee(sizeDelta, bps)` applies `sizeDelta * bps / 10000` with **no upper bound** (only
  implicitly `bps < 10000`); the `MAX_FEE_BASIS_POINTS = 500` cap is enforced on the *other* fees in
  `setFees`, **not** on the broker fee.
- `increasePositionV2` never validates `brokerFeeBasisPoints`; the only constraint is
  `require(position.collateral >= fee)` at open, so `brokerFee_open ≤ collateral`.

## Attack scenario (when live)
Let `C` = collateral deposited, `S` = position size, `bps` = `brokerFeeBasisPoints`, broker = attacker.
1. Attacker opens a near‑max‑leverage position via `increasePositionV2` with `brokerAddress = attacker` and a
   high `bps` (e.g. ~98%), so `brokerFee_open = S·bps ≈ C` is paid straight back to the attacker at open.
   The position is left at the leverage limit (≈0 buffer).
2. Funding fees / any small adverse price move make the position liquidatable; a keeper liquidates it
   (the attacker is the **beneficiary**, not the liquidator, so private-liquidation mode does not prevent it).
3. At liquidation the broker fee is charged **again** (`brokerFee_liq = S·bps ≈ C`) and sent to the attacker
   from `feeReserves`.

Net for the attacker ≈ `−C + brokerFee_open + brokerFee_liq = −C + 2·brokerFee_open ≈ +0.96·C` per cycle,
drained from `feeReserves` (real tokens backing the pool/FLP). Repeatable until `feeReserves` is exhausted.

## Current reachability (why this is LATENT, not currently exploitable)
Read-only Cronos state (2026-06-20), Vault proxy `0x8C7E…`, live implementation `0xa66a0fea…` (== the reviewed
implementation):
- `isLeverageEnabled()` = **false** → both `increasePosition` and `increasePositionV2` revert immediately
  (`_validate(isLeverageEnabled, 28)`), so **no position (and therefore no broker position) can be opened**.
- `feeReserves(USDC)` ≈ **0.045 USDC**, `feeReserves(WCRO)` ≈ **1.84** → essentially **empty**, so even a
  pre-existing broker position could not yield a profitable/non-reverting payout (the `feeReserves -=`
  subtraction would underflow and revert).

Because perpetual trading is disabled and fee reserves are empty, there are no funds at risk on the current
mainnet state. The issue becomes a live, permissionless `feeReserves`/pool drain the moment leverage is
re-enabled and fees accrue. We are reporting it now so it can be fixed before that happens.

## Recommended fix
- **Remove the second broker-fee charge at liquidation** (the `_chargeBrokerFee(position.size, …)` block in
  `liquidatePosition`). The broker fee should be charged only once, at open/increase, from the trader's own
  collateral.
- **Cap `brokerFeeBasisPoints`** at open (e.g. `require(brokerFeeBasisPoints <= MAX_FEE_BASIS_POINTS)` in
  `increasePositionV2`) so a broker fee can never approach 100% of size.

## Notes
- No transaction was sent to mainnet or any public testnet; this is based on the verified implementation source
  and read-only `eth_call`s. A single-transaction Foundry fork PoC at a pinned Cronos block (capital well under
  $300, broker = attacker) can be provided on request — it would require a fork state where `isLeverageEnabled`
  is true and `feeReserves` is funded, which is not the case on the live deployment today.
- Coverage caveat: the in-scope `OrderBook` implementation (`0x1b0e…`) is unverified on-chain, so its
  order-authorization path could not be reviewed from source; unrelated to this issue but worth noting.
