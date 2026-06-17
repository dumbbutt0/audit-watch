# P270 — RANKING_AND_COMPLETION (Phase 5)

Five-op completion (STS/AAS/TSE/IDC/CCIT) on the three triage-selected, selector-preserved mechanisms. Pre-reveal,
source-grounded. (Selector KEEP_BOTH → both mechanisms in each pair available; the high-impact M1 is completed, the
easy M2 noted.)

## C-pp — PendlePowerFarmToken first-deposit / share-price manipulation (PARTIAL_RUNTIME)
- **STS:** `depositExactAmount` → `previewMintShares(amount, underlyingLpAssetsCurrent) = amount·totalSupply()/
  underlyingLpAssetsCurrent`, then `_applyMintFee`, `_mint`. Share price `_getSharePrice = previewUnderlyingLpAssets·
  1e18/totalSupply()`.
- **AAS:** attacker = permissionless depositor.
- **TSE / IDC:** classic first-depositor inflation requires inflating `underlyingLpAssetsCurrent` relative to
  totalSupply. But assets are **internally tracked** (`underlyingLpAssetsCurrent`, fed only via the controller /
  time-distributed `totalLpAssetsToDistribute`), NOT a directly-donatable `balanceOf` → no instant donation.
  `_validateSharePriceGrowth` caps share price to `timeDelta·RESTRICTION_FACTOR + 1e18` (≈1e18 early) and
  `_validateSharePrice` enforces monotonic non-decrease. Plus controller seeds initial supply.
- **CCIT:** attacker/victim distinct EOAs.
- **Status: PARTIAL_CHAIN → likely GUARDED.** The share-price-growth guard + internal asset tracking + seeded supply
  materially mitigate the inflation; a clean drain is not evident from source. Falsifier (the guard) appears to hold.
  Resolved further by the partial-runtime PoC.

## C-liq — WiseCore liquidation collateral/share misallocation (PARTIAL_RUNTIME, heavy)
- **STS/AAS/TSE/IDC:** `_withdrawPureCollateralLiquidation` / `_withdrawOrAllocateSharesLiquidation` move collateral/
  shares during liquidation; a misallocation would let a liquidator over-seize or strand collateral. Reaching it
  requires the full WiseLending+WiseSecurity+OracleHub stack (deposit→borrow→price-drop→liquidate).
- **Status: PARTIAL_CHAIN, completion needs full-stack runtime** (heavy) — routed PARTIAL_RUNTIME by triage; a
  standalone exact chain is not provable from source reading alone within scope.

## C-bd — FeeManager bad-debt payback accounting (PARTIAL_RUNTIME, heavy)
- **STS/AAS/TSE/IDC:** `paybackBadDebtForToken` / `paybackBadDebtNoReward` adjust bad-debt bookkeeping; an accounting
  error across the two paths could mis-credit/strand value. Reaching it needs a position with realized bad debt
  (full borrow→insolvency→liquidation→bad-debt flow).
- **Status: PARTIAL_CHAIN, completion needs full-stack runtime** (heavy) — routed PARTIAL_RUNTIME.

## Summary
| mechanism | selector | triage | completion |
|---|---|---|---|
| C-pp share-price | KEEP_BOTH | SELECT_FOR_PARTIAL_RUNTIME | PARTIAL → likely GUARDED (guard + internal assets) |
| C-liq liquidation | KEEP_BOTH | SELECT_FOR_PARTIAL_RUNTIME | PARTIAL (needs full-stack runtime) |
| C-bd bad-debt | KEEP_BOTH | SELECT_FOR_PARTIAL_RUNTIME | PARTIAL (needs full-stack runtime) |
The most PoC-feasible (Pendle-share math) is attempted as a partial-runtime PoC; liquidation/bad-debt are
full-stack-heavy (honest harness-weight limit). Frozen before PoC code.
