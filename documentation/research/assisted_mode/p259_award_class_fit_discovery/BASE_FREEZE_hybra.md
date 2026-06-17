# hybra — Phase 1: Frozen base-workflow artifact (PRE-REVEAL)
Frozen base-workflow analogue. Sealed key not read. Subtle multi-family loci. claimMany-parity (p161) excluded.

## Generation basis
- Surface: `audits/hybra-finance-2025-10-strict-eval/output/coverage_manifest.json`.
- Checkpoints: `python scripts/{accounting,state_transition}_checkpoint_audit.py --manifest <hybra manifest> --out .../outputs/hybra-finance_*_checkpoint.json --quiet` (invariants re-verified).
- Base read: ve33/contracts/VotingEscrow.sol (multiSplit/_createSplitNFT/merge), GaugeManager.sol (_distribute).

## Checkpoint records (advisory)
accounting 181: VotingEscrow {multiSplit,_create_lock,withdraw,merge,_createSplitNFT}, IRewarder.onReward, GrowthHYBR {deposit,withdraw}, CLPool.swap, GaugeManager {_distribute,_updateForAfterDistribution} (A4 51/A3 50/A1 32/A2 30/A5 18). state-transition 48: GrowthHYBR.deposit, CLPool.swap, VotingEscrow {merge,multiSplit}, GaugeCL/GaugeManager (S3 21/S4 10/S2 9/S1 7/S5 1).

## Frozen base candidate set (subtle, multi-family)
| id | sev | locus | observed |
|---|---|---|---|
| **B1** | Med/High? | `VotingEscrow.multiSplit` | splits veNFT into N: `amount_i = orig*amounts[i]/totalWeight` (rounding-down each); burns original; `permanentLockBalance` NOT adjusted for permanent splits |
| **B2** | Med? | `VotingEscrow.merge` | permanent-lock accounting (`permanentLockBalance += value0` only if source !permanent); end = max |
| **B3** | Med? | `GaugeManager._distribute`/`_updateForAfterDistribution` | reward/gauge distribution accounting across periods |

## Three-way tag
| id | tag |
|---|---|
| B1 | BASE_BORN_INCOMPLETE (split rounding + permanent desync seen; exploit/loss not computed) |
| B2 | BASE_BORN_INCOMPLETE (merge permanent edge seen; not traced) |
| B3 | BASE_BORN_INCOMPLETE (distribution seen; drift not traced) |
| (none) | BASE_COMPLETED_CHAIN: 0 |

**FREEZE.** Hash in REVEAL_AND_SCORE_hybra.md before key opened.
