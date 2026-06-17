# P291 — REMAP_RESULTS

Sources: `outputs/remap_metrics.json`, `outputs/integration_precision_report.json`, `outputs/internal_locus_candidates.json`.

## Part A — EXTERNAL_INTEGRATION precision
- **salty `Pools.deposit`: READY → NEEDS_INTEGRATION_DEVIATION_EVIDENCE** (the P290 false READY is eliminated).
- EXTERNAL_INTEGRATION READY count across the remap: **0** (no generic-template READY remains).
- Demoted generic integration candidate: Pools.deposit (no low-level call / callback / reentrancy-ordering; nonReentrant
  + safeTransferFrom). severe concluded/reportable FP: **0**.
- Unit fixtures: actual low-level-call/callback deviation → deviation_present True (can lift); explicit fee-on-transfer →
  True; plain safeTransferFrom / nonReentrant transfer → False (blocked).

## Part B — internal accounting/reward locus recall
- Internal-locus candidates surfaced: **5** (salty: `StakingRewards._increaseUserShare`, `Liquidity._dualZapInLiquidity`,
  `Liquidity._withdrawLiquidityAndClaim`; ECG: `ERC20Gauges._decrementWeightUntilFree`,
  `ERC20RebaseDistributor.updateTotalRebasingShares`). Avg expansions/contest ≈ 2.5 (cap 3/entry, 15/contest).
- **`StakingRewards._increaseUserShare` IS NOW SURFACED** (the exact P290-missing awarded-H02/H04 locus), reached from
  `Liquidity._depositLiquidityAndIncreaseShare`. The recall gap at the advisory layer is fixed.
- **BUT it does not reach the validation queue / Lens 3**: the P273 coverage router labels it
  `COVERAGE_DEFER_DUPLICATE_CLASS` (its SHARE_ROUNDING class slot is already filled), so it is dropped before the queue.
  Lens 3 never receives it. This is a NEW localized blocker at the coverage/queue layer (P273/P278 — out of P291 scope).
- severe concluded/reportable FP: **0**. No internal-locus candidate became a READY (advisory-only + dedup).

## Regressions (all stable, via frozen evidence_packages)
ECG H-04 SurplusGuildMinter.stake → READY · kelp H-01 getRsETHAmountToMint → READY · blackhole claim_many → READY ·
L2Governor.execute → READY. severe FP total across remap+regressions: **0**.
