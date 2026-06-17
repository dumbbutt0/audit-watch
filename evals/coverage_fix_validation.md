# Coverage-prioritization fix — structural validation on Fluid DEX v2

_2026-06-12. Eval-only. Validates the recall-lab coverage fix (price/oracle/AMM/POL ranked top) against a real
price/AMM/POL-heavy protocol (Fluid DEX v2, Sherlock contest 1225). This is the contamination-FREE part of the
Fluid test: it measures whether the new scoring reorders the manifest, which is memorization-independent (so it
is unaffected by Fluid being semi-fresh / by the H-1 leak)._

## Method
Rebuilt the coverage manifest on the live Fluid source with the new `build_coverage_manifest.py` scoring
(`amm_pol` tag + expanded `oracle` tag + the +1 value-at-risk boost), to a sandbox path; compared each item's
new `attack_surface_score` against a reconstruction of the pre-fix score.

## Result — the fix demonstrably reorders the DEX so the price machinery ranks first
- **632 in-scope items; 140 now tagged `amm_pol`, 51 `oracle`** (was 0 `amm_pol` before the fix).
- **Top of the ranking (score 6) is entirely the AMM/POL/oracle surface**: `rebalance`, `updateOracle`,
  `updateProtocolFee`, D3/D4 position-cap setters, per-pool accounting.
- **23 AMM/POL functions were RESCUED above the deep-pass cutoff** (now score ≥3; would have scored <3 under the
  old scoring → cheap-sweep tail): `_swapIn`/`_swapOut`, `_verifyLiquidityLimits`/`_verifyLiquidityChangeLimits`,
  `_getMaxLiquidityPerTick`, `_nextInitializedTickWithinOneWord`, `_setTickBitmap`, `dexV2PoolLock.lock/unlock`,
  `_updateProtocolFee`, `_stopPerPoolAccounting`, `updateProtocolFee` (→6), …
- **The leaked H-1 locus cluster** (`protocols/moneyMarket/core/operateModule/helpers.sol`) is now entirely
  score ≥3 (deep-pass): `_withdrawSettle`/`_depositSettle`, `_checkAndUpdateCapsForD3D4Liquidity`,
  `_useFeeStoredForLiquidation`, … — the cluster that held the awarded High is no longer skippable.

## Conclusion
The coverage-prioritization fix does what the Olas reveal showed was missing: on a real DEX it tags the
price/oracle/AMM/POL machinery and ranks it at the TOP of the manifest, pulling 23 swap/liquidity/tick/fee
functions out of the deprioritized tail into the deep-pass set. Had this been in place for Olas, the oracle/POL
cluster (where ~15/23 awarded findings lived) would have been examined first instead of last.

## Structural confirmation #2 — Panoptic (Uniswap-V3 options/AMM)
Rebuilt the manifest on Panoptic Next-Core `contracts/in_scope` with the new scoring:
- **472 in-scope items; 206 tagged `amm_pol`, 76 `oracle`.**
- Top-ranked functions are the AMM/oracle surface: `CollateralTracker.settleMint/settleBurn/settleLiquidation`
  (score 6/5, `amm_pol`), `PanopticPool.pokeOracle` (score 5, `amm_pol`+`oracle`), `lockSafeMode`/`delegate`/
  `revoke` (`amm_pol`). **38 VaR-tagged functions at score ≥4.**
- The fix generalizes across protocol types: a DEX (Fluid) and an options/AMM protocol (Panoptic) both get
  their price machinery tagged and top-ranked.
- NOTE: Panoptic is fully-revealed from a PRIOR strict-eval (answer key on disk) and pre-cutoff, so no recall
  number is claimed — only the (memorization-independent) structural reordering, which is the clean signal.

## Caveats on Fluid as a recall sample (NOT used here)
Fluid is semi-fresh (cold-passed once under old prompts) and finding H-1 leaked during the answer-key fetch, so a
genuine blind recall number on Fluid is not claimed. This validation is purely structural (manifest reordering),
which those caveats do not affect. A pristine generalization recall test awaits a never-seen post-cutoff
price-heavy contest with a public report.
