# sentiment — Phase 1: Frozen base-workflow artifact (PRE-REVEAL) — DISCLOSED-CONTAMINATED
Frozen base-workflow analogue. **#541 area (interest-distribution/asset-transfer/fee-accrual = Pool.accrue) and
p242 max*/preview* HARD-EXCLUDED.** Subtle multi-family loci elsewhere.

## Generation basis
- Surface: `audits/sentiment-v2-2024-08-fresh/output/coverage_manifest.json`.
- Checkpoints: `python scripts/{accounting,state_transition}_checkpoint_audit.py --manifest <sentiment manifest> --out .../outputs/sentiment-v2_*_checkpoint.json --quiet` (invariants re-verified).
- Base read: src/PositionManager.sol (liquidate/liquidateBadDebt/_transferAssetsToLiquidator/_process), Pool.sol (rebalanceBadDebt), SuperPool.sol (reorder queues).

## Checkpoint records (advisory)
accounting 155: SuperPool {maxWithdraw,maxRedeem(excluded),deposit,mint,_deposit}, Pool {deposit,withdraw,accrue(excluded #541),borrow,repay,rebalanceBadDebt} (A2 36/A5 34/A1 33/A4 30/A3 22). state-transition 19: PositionManager {_process,liquidate,liquidateBadDebt,_transferAssetsToLiquidator,deposit,transfer}, Pool {withdraw,borrow}, SuperPool {addPool,reorderDepositQueue,reorderWithdrawQueue} (S4 9/S3 7/S2 2/S5 1).

## Frozen base candidate set (subtle, multi-family; #541/max* excluded)
| id | sev | locus | observed |
|---|---|---|---|
| **B1** | High? | `PositionManager.liquidate`/`_transferAssetsToLiquidator` | liquidator passes `assetData` to seize vs debt repaid; health/seizure boundary |
| **B2** | Med/High? | `Pool.rebalanceBadDebt` | bad-debt socialization across pool depositors |
| **B3** | Med? | `SuperPool.reorderDepositQueue`/`reorderWithdrawQueue` | queue ordering drives allocation/withdrawal |

## Three-way tag: all BASE_BORN_INCOMPLETE; BASE_COMPLETED_CHAIN 0.
**FREEZE.** Hash in REVEAL_AND_SCORE_sentiment.md before key opened.
