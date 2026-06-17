# ethos — Phase 1: Frozen base-workflow artifact (PRE-REVEAL)

Frozen base-workflow analogue. Sealed key not read. Subtle multi-family loci.

## Generation basis
- Surface: `audits/ethos-reserve-2023-02-liquidation-health/output/coverage_manifest.json` (~784 fns; subtle core focused).
- Checkpoints: `python scripts/{accounting,state_transition}_checkpoint_audit.py --manifest <ethos manifest> --out .../outputs/ethos-reserve_*_checkpoint.json --quiet` (invariants re-verified).
- Base read: `contracts/2023-02-ethos/contracts/ActivePool.sol` (_rebalance/sendCollateral/profit-split),
  `StabilityPool.sol` (offset), `RedemptionHelper.sol` (redeemCollateral), `SortedTroves.sol` (reInsert).

## Checkpoint records (advisory)
accounting 71: StabilityPool.offset, ActivePool {sendCollateral,_rebalance,manualRebalance,
pullCollateralFromBorrowerOperationsOrDefaultPool}, BorrowerOperations {openTrove,_adjustTrove,closeTrove,
_withdrawLUSD,_repayLUSD}, LUSDToken {mint,burn} (A4 34/A5 17/A2 14/A1 6). state-transition 42: BorrowerOperations
._adjustTrove, RedemptionHelper.redeemCollateral, SortedTroves.reInsert, LQTYStaking {stake,unstake} (S1 20/S3 11/S2 8/S4 3).

## Frozen base candidate set (subtle, multi-family)
| id | sev(blind) | locus | observed |
|---|---|---|---|
| **B1** | High? | `ActivePool._rebalance` (Ethos-specific) | collateral→ERC4626 yieldGenerator; `profit = convertToAssets(shares) − yieldingAmount`; deposit/withdraw `netAssetMovement`; profit recalc `bal+yieldingAmount−collAmount`; split treasury/staking/SP |
| **B2** | Med/High? | `StabilityPool.offset` | Liquity P/S product compounding-stake reward accounting on liquidation offset |
| **B3** | Med? | `RedemptionHelper.redeemCollateral` + `SortedTroves.reInsert` | redemption walks sorted troves, partial-redemption reinsert, base-rate |

## Three-way tag
| id | tag |
|---|---|
| B1 | BASE_BORN_INCOMPLETE (ERC4626 yield/profit accounting seen; conversion/loss path not traced) |
| B2 | BASE_BORN_INCOMPLETE (P/S product seen; scale/epoch drift not traced) |
| B3 | BASE_BORN_INCOMPLETE (redemption/reInsert seen; ordering/identity not traced) |
| (none) | BASE_COMPLETED_CHAIN: 0 |

**FREEZE:** before selection/reveal. Hash in REVEAL_AND_SCORE_ethos.md before key opened.
