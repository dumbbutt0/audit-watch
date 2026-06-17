# P290 — REVEAL_AND_SCORE (salty-2024-01, opened AFTER pre-reveal freeze)

Answer key opened only after `outputs/pre_reveal_freeze.json`. Awarded H/M = 37 (6H/31M). Data: `outputs/reveal_score.json`.

## Awarded Highs through the funnel
| id | awarded locus | surfaced | READY | PoC | match level | P289-lens relevant? |
|---|---|---|---|---|---|---|
| H-01 | VestingWallet.release | ✗ | ✗ | ✗ | MISSED | — |
| H-02 | StakingRewards._increaseUserShare (first-LP rewards) | contract only | ✗ | ✗ | SUBSYSTEM_ONLY_RECALL | **reward_index_init (Lens 3) class — but lens did NOT fire; internal locus not surfaced** |
| H-03 | CoreSaltyFeed/PriceAggregator (spot price) | ✗ | ✗ | ✗ | OUT_OF_SCOPE (removed) | — |
| H-04 | StakingRewards._increaseUserShare (first-depositor accounting) | contract only | ✗ | ✗ | SUBSYSTEM_ONLY_RECALL | **reward_index_init (Lens 3) class — lens did NOT fire** |
| H-05 | CollateralAndLiquidity.depositCollateralAndIncreaseShare (cooldown-reset liq evasion) | contract only | ✗ | ✗ | SUBSYSTEM_ONLY_RECALL | (loss/liquidation area) |
| H-06 | CollateralAndLiquidity.repayUSDS (wrong address) | ✗ | ✗ | ✗ | OUT_OF_SCOPE (removed) | — |

## Pre-reveal candidate scoring
- **Pools.deposit (the one READY) → FALSE_POSITIVE (READY-layer)**: NOT an awarded locus; `nonReentrant` deposit with a
  standard `safeTransferFrom` and no callback; the claimed EXTERNAL_INTEGRATION callback mechanism was **PoC-REFUTED
  pre-reveal** → unsupported, never concluded/reportable. A speculative READY from the frozen P279 EXTERNAL_INTEGRATION
  template (invariant_delta NO_REFERENCE), not a P289 lens.
- The other 9 candidates: BENIGN/INCONCLUSIVE (held; none claimed READY).

## Reading
- **0 awarded exact/strong recoveries. 0 PoC-supported. 0 P289 lens firings.**
- **The one READY was a READY-layer false positive (caught pre-reveal by its own PoC).** severe concluded/reportable
  FP = 0 (nothing reached a concluded/reportable state).
- **Most striking**: salty's marquee awarded Highs (H-02/H-04) ARE reward-index/first-depositor bugs — exactly Lens 3's
  class — yet Lens 3 never fired, because the awarded internal locus `StakingRewards._increaseUserShare` was not surfaced
  as a validation candidate (only `claimAllRewards` was). The lens was starved by a RECALL gap, not refuted.
