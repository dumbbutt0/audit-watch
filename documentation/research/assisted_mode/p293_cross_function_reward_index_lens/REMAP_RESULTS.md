# P293 — REMAP_RESULTS

Driver: `remap_driver.py` (p276_corpus_replay → expanded_validation_queue → completion_evidence_deriver → gate).
8 targets + 1 control (revert-lend). Research-only; severity never set.

- **severe concluded/reportable FP: 0**
- **Lens-3 firings: 2** · **Lens-3 lifts to READY: 1** (coverage_manifest:StakingRewards:_increaseUserShare:int0)
- **`_increaseUserShare`: READY_FOR_POC_INTENT** (lens3 LENS3_READY, pattern FIRST_DEPOSITOR_ZERO_SUPPLY)

## Per-target

| target | queue tally | READY | lens3 fired |
|---|---|---|---|
| salty-2024-01-holdout | {'NEEDS_STATE_MACHINE_EVIDENCE': 1, 'NEEDS_VALUE_FLOW_EVIDENCE': 3, 'INLINE_GUARD_REFUTED': 5, 'NEEDS_INTEGRATION_DEVIATION_EVIDENCE': 1, 'READY_FOR_POC_INTENT': 1} | ['coverage_manifest:StakingRewards:_increaseUserShare:int0'] | ['coverage_manifest:CollateralAndLiquidity:liquidateUser:10', 'coverage_manifest:StakingRewards:_increaseUserShare:int0'] |
| ecg-2023-12-holdout | {'READY_FOR_POC_INTENT': 1, 'NEEDS_VALUE_FLOW_EVIDENCE': 6, 'INLINE_GUARD_REFUTED': 1, 'NEEDS_STATE_MACHINE_EVIDENCE': 1} | ['coverage_manifest:SurplusGuildMinter:stake:5'] | [] |
| kelp-2023-11-holdout | {'NEEDS_MORE_EVIDENCE': 1, 'READY_FOR_POC_INTENT': 1, 'INLINE_GUARD_REFUTED': 4} | ['coverage_manifest:LRTDepositPool:getRsETHAmountToMint:6'] | [] |
| blackhole-2025-05-eval | {'INLINE_GUARD_REFUTED': 3, 'READY_FOR_POC_INTENT': 2, 'NEEDS_MORE_EVIDENCE': 1, 'NEEDS_SOURCE_SPAN': 1, 'NEEDS_VALUE_FLOW_EVIDENCE': 3} | ['coverage_manifest:RewardsDistributor:claim_many:7', 'coverage_manifest:L2Governor:execute:20'] | [] |
| panoptic-2025-12-strict-eval | {'NEEDS_VALUE_FLOW_EVIDENCE': 4, 'NEEDS_MORE_EVIDENCE': 2, 'NEEDS_GUARD_CONTEXT': 1} | [] | [] |
| silo-finance-2025-03-strict-eval | {'NEEDS_VALUE_FLOW_EVIDENCE': 7, 'NEEDS_MORE_EVIDENCE': 1, 'NEEDS_INTEGRATION_DEVIATION_EVIDENCE': 1, 'NEEDS_STATE_MACHINE_EVIDENCE': 2} | [] | [] |
| revert-lend-2024-03-strict-eval | {'NEEDS_VALUE_FLOW_EVIDENCE': 5, 'NEEDS_STATE_MACHINE_EVIDENCE': 1, 'INLINE_GUARD_REFUTED': 3, 'NEEDS_MORE_EVIDENCE': 1} | [] | [] |
| hybra-finance-2025-10-strict-eval | {'NEEDS_INTEGRATION_DEVIATION_EVIDENCE': 1, 'NEEDS_STATE_MACHINE_EVIDENCE': 2, 'INLINE_GUARD_REFUTED': 3, 'NEEDS_VALUE_FLOW_EVIDENCE': 4} | [] | [] |

## Lens-3 firings (all)

- salty-2024-01-holdout · `coverage_manifest:CollateralAndLiquidity:liquidateUser:10` · LENS3_READY / GLOBAL_INDEX_NOT_PAIRED · gate=INLINE_GUARD_REFUTED
- salty-2024-01-holdout · `coverage_manifest:StakingRewards:_increaseUserShare:int0` · LENS3_READY / FIRST_DEPOSITOR_ZERO_SUPPLY · gate=READY_FOR_POC_INTENT

## Regressions (all stable)

- kelp_getRsETHAmountToMint: **READY**
- blackhole_claim_many: **READY**
- L2Governor_execute: **READY**
- ecg_stake: **READY**
- salty_Pools_deposit: **NEEDS_INTEGRATION_DEVIATION_EVIDENCE**

## New READY vs P292 baseline

Exactly **1** genuinely-new READY locus across the corpus: salty `StakingRewards:_increaseUserShare` (the awarded H-02/H-04 locus). All other READY sets unchanged; control + all strict-eval targets remain at 0.

Note: `CollateralAndLiquidity:liquidateUser` also fires the lens (LENS3_READY/GLOBAL_INDEX_NOT_PAIRED) but the gate's D1 holds it `INLINE_GUARD_REFUTED` — fail-closed, not a READY, not a false positive.
