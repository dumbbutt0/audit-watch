# P271 — POC_RESULTS (CALIBRATION)

`cd pocs/p271/wise && forge test -vv` → **3 passed** (solc 0.8.24, evm shanghai; forge-std v1.9.6, OZ v4.9.6).

| case | tier | test | result | observed |
|---|---|---|---|---|
| **H-03** bad-debt global-vs-position | **B (real production code)** | `H03_GlobalVsPositionBadDebt.t.sol` | **PASS** | buggy path: after 2 partial liquidations (d1=100e15, d2=50e15) + payback, `totalBadDebtETH` = **100e15 stuck** (fake debt = d1); corrected reference clears to **0** |
| **H-04** uncollateralized over-extraction | **C (faithful reproduction)** | `H04_PrivateVsPublicCollateralMisallocation.t.sol` | **PASS** | uncollateralized position (private 100, normal shares 100, 50% liq): buggy receive **100** vs fixed **50** → over-extraction = **50** = `removePct × userShares` |

## H-03 — exact mechanism, runtime-proven on REAL code
A `BadDebtHarness is FeeManagerHelper` executes the real `_increaseTotalBadDebt` (`totalBadDebtETH += diff`) and
`_setBadDebtPosition` (`badDebtPosition[nftId] = diff`, overwrite) exactly as `checkBadDebtLiquidation` calls them,
then the real `_decreaseTotalBadDebt`/`_eraseBadDebtUser` payback. Two partial liquidations → global=150e15 but
position overwritten to 50e15 → payback removes only 50e15 → **100e15 fake debt permanently stuck → bricks
claimFeesBeneficial** (gated on `totalBadDebtETH == 0`). The corrected reference (track cumulative / diff, like
`_updateUserBadDebt`) clears the global to 0. **L1/L2/L3:** L1 liquidation-equivalent calls; L2 `totalBadDebtETH`/
`badDebtPosition` asserted pre/post; L3 residual global > 0 → bricked invariant.

## H-04 — exact mechanism, runtime-proven via faithful reproduction
The harness faithfully reproduces `WiseCore._calculateReceiveAmount` L552-600 control flow + the real
`_calculatePotentialPureExtraCashout` formula (`removePct * userShares / 1e18`). It proves the **branch-ordering
bug**: the normal-share-sized `potentialPureExtraCashout` is granted **before** the `unCollateralized == true`
early-return, so an uncollateralized liquidation over-extracts by exactly `removePct × userShares` (50). The
corrected version (early-return after pure collateral) yields only the private-collateral % (50). Limitation: Tier C
(the conversion helper modeled 1:1; the proven bug is purely the faithful branch ordering).

## Honest tiering
H-03 = Tier B (real production accounting code). H-04 = Tier C (faithful control-flow reproduction; the deployed
private function needs the full WiseLending stack). Both **sharpen the P270 family-level hits to EXACT** with runtime
evidence. CALIBRATION (post-reveal) — NOT a fresh/blind recovery claim. Hashes: H03 `4eec99ea561da7a7` · H04
`fdc6a0b37fb8dca6` · foundry.toml `be38d45283896234`.
