# P270 — POC_INTENT (Phase 6, frozen BEFORE PoC code)

Mechanism claims for the routed candidates. Frozen pre-code; consolidated from the queue/selector/triage docs (all
written before any PoC). No answer key.

## C-pp — PendlePowerFarmToken share math (PARTIAL_RUNTIME, attempted)
- **Target:** `PendlePowerFarmToken.previewMintShares` / `depositExactAmount` share accounting.
- **Mechanism hypothesis:** first-deposit / share-price-rounding inflation: a victim deposit rounds to fewer/0 shares
  when share price is inflated.
- **Attacker model:** permissionless depositor.
- **Setup (partial runtime):** deploy the token via its clone-init with **mocked** Pendle controller/market (the
  deposit→mint→withdraw share path is internal — external Pendle calls live only in the reward functions); seed
  `totalSupply` + `underlyingLpAssetsCurrent`; have a victim deposit.
- **Expected delta / assertion:** if guarded → victim receives fair, non-zero shares and `_validateSharePriceGrowth`
  bounds the price (the falsifier holds → REFUTED); if exploitable → victim rounds to 0 / loses value.
- **Refutation condition (pre-stated):** the share-price-growth guard + internally-tracked assets (no instant
  donation) + controller-seeded supply prevent inflation.
- **Expectation:** likely REFUTED/GUARDED (per completion), to be confirmed by runtime.

## C-liq — WiseCore liquidation (PARTIAL_RUNTIME, heavy)
- **Target:** `_withdrawPureCollateralLiquidation` / `_withdrawOrAllocateSharesLiquidation`.
- **Mechanism:** liquidation collateral/share misallocation (over-seize / strand).
- **Setup:** full WiseLending+WiseSecurity+OracleHub deposit→borrow→price-drop→liquidate stack (heavy fork/scaffold).
- **Status:** harness-weight heavy → `NEEDS_MORE_RUNTIME` if a runnable partial isn't achievable in scope; recorded honestly.

## C-bd — FeeManager bad-debt (PARTIAL_RUNTIME, heavy)
- **Target:** `paybackBadDebtForToken` / `paybackBadDebtNoReward`.
- **Mechanism:** bad-debt payback bookkeeping error across the two paths.
- **Setup:** full borrow→insolvency→liquidation→bad-debt flow (heavy).
- **Status:** harness-weight heavy → `NEEDS_MORE_RUNTIME` if not runnable in scope; recorded honestly.

Frozen before code; hashes in POC_RESULTS.
