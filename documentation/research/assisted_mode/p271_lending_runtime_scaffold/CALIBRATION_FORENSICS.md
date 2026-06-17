# P271 — CALIBRATION_FORENSICS (post-reveal; CALIBRATION, not fresh recovery)

Wise H-03/H-04 awarded mechanisms (from the public findings `report.md`, opened in P270) vs the P270 family-level
hypotheses, and the missing exact step / required runtime each needs.

## H-03 — incorrect bad-debt accounting (FeeManager)
- **Awarded mechanism:** `WiseSecurity.checkBadDebtLiquidation` **increments** global `totalBadDebtETH` (via
  `FeeManager.increaseTotalBadDebtLiquidation` → `_increaseTotalBadDebt`: `+=`) but **sets/overwrites** the
  position's `badDebtPosition[nftId]` (via `setBadDebtUserLiquidation` → `_setBadDebtPosition`: `=`). Across multiple
  partial liquidations the global accumulates while the position holds only the latest; on payback only the position
  amount is deducted → "fake debt" stuck in `totalBadDebtETH` → `claimFeesBeneficial`/`claimWiseFees` (gated on
  `totalBadDebtETH == 0`) are bricked.
- **P270 family-level hypothesis:** "bad-debt payback bookkeeping error across paths" (right subsystem+locus, family).
- **Missing exact step:** the **increment-vs-set asymmetry** between global and position across ≥2 partial
  liquidations (the position must be OVERWRITTEN, not incremented, while the global is incremented).
- **Required runtime state:** a position bad-debt'd by ≥2 partial liquidations (d1, d2), then repaid.
- **Mocks/fixtures:** only `POSITION_NFTS.FEE_MANAGER_NFT()` (ctor); the bad-debt helpers touch storage only.
- **Invariant to prove:** after full payback of a position, `totalBadDebtETH` returns to its pre-bad-debt value (0).
- **Minimum acceptable evidence:** runtime execution of the real `_increaseTotalBadDebt`/`_setBadDebtPosition`/
  `_decreaseTotalBadDebt` showing residual `totalBadDebtETH > 0`. → **achieved (Tier B, real production code).**

## H-04 — liquidators pay less for uncollateralized positions (WiseCore)
- **Awarded mechanism:** `WiseCore._calculateReceiveAmount` computes `potentialPureExtraCashout =
  _calculatePotentialPureExtraCashout(userShares, removePct)` = `removePct * userShares / 1e18` — sized by the
  position's **normal deposit shares** — and pays it out **before** the `unCollateralized == true` early-return
  (line ~592). So liquidating an uncollateralized position extracts extra value beyond the private collateral %.
- **P270 family-level hypothesis:** "liquidation collateral/share misallocation" (right subsystem+locus, family).
- **Missing exact step:** the **branch ordering** — the normal-share-sized cashout is granted *before* the
  uncollateralized check; the fix is an early-return on uncollateralized right after pure-collateral processing.
- **Required runtime state:** an uncollateralized position with pure collateral > 0 and normal shares > 0; a
  liquidation at a given percentage.
- **Mocks/fixtures:** the full deployed `_calculateReceiveAmount` (private) needs the entire WiseLending stack
  (pureCollateralAmount/userLendingData/pool state + WISE_SECURITY) — heavy. → modeled as a faithful Tier-C
  reproduction of the exact control flow + the real cashout formula.
- **Invariant to prove:** for an uncollateralized position, the liquidator receives only the private-collateral
  percentage (normal deposits not extractable).
- **Minimum acceptable evidence:** runtime showing buggy receive > corrected receive by exactly the normal-share-
  sized cashout. → **achieved (Tier C faithful reproduction).**
