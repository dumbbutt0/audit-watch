# astaria — Phase 1: Frozen base-workflow artifact (PRE-REVEAL)

Frozen base-workflow analogue. Sealed key not read. Subtle multi-family loci.

## Generation basis
- Surface: `audits/astaria-2023-01-fresh/output/coverage_manifest.json` (~375 fns).
- Checkpoints: `python scripts/{accounting,state_transition}_checkpoint_audit.py --manifest <astaria manifest> --out .../outputs/astaria_*_checkpoint.json --quiet` (invariants re-verified).
- Base read: `_src/src/PublicVault.sol` (processEpoch, transferWithdrawReserve, redeem/redeemFutureEpoch, _accrue/slope/yIntercept, _beforeCommitToLien), `_src/src/LienToken.sol` (_buyoutLien, makePayment, _payDebt).

## Checkpoint records (advisory)
accounting 81: PublicVault {processEpoch,_beforeCommitToLien,redeem,withdraw,redeemFutureEpoch,beforePayment},
LienToken {_buyoutLien,createLien,_payDebt,makePayment} (A5 32/A2 23/A1 10/A4 10/A3 6). state-transition 16:
AstariaRouter.commitToLiens, LienToken.stopLiens, PublicVault {redeem,redeemFutureEpoch,processEpoch,
transferWithdrawReserve,updateVaultAfterLiquidation} (S3 10/S4 6).

## Frozen base candidate set (subtle, multi-family)
| id | sev(blind) | locus | observed |
|---|---|---|---|
| **B1** | High? | `PublicVault` epoch/withdrawReserve/slope | epoch state-machine: `processEpoch` increments epoch + decrements `yIntercept` by `liquidationWithdrawRatio`; `transferWithdrawReserve` transfers + `drain`s across epochs; `_accrue`/slope temporal interest |
| **B2** | Med/High? | `LienToken._buyoutLien` | buyout transfers debt/interest between lienholders; accrual timing + recipient identity |
| **B3** | Med? | `PublicVault.redeem`/`redeemFutureEpoch` | LP redemption queued to future epoch via withdrawProxy; share/asset across-epoch accounting |

## Three-way tag
| id | tag |
|---|---|
| B1 | BASE_BORN_INCOMPLETE (epoch/withdrawReserve/slope seen; exact drift/exploit not computed) |
| B2 | BASE_BORN_INCOMPLETE (buyout transfer seen; accrual/identity not traced) |
| B3 | BASE_BORN_INCOMPLETE (future-epoch redemption seen; across-epoch accounting not traced) |
| (none) | BASE_COMPLETED_CHAIN: 0 |

**FREEZE:** before selection/reveal. Hash in REVEAL_AND_SCORE_astaria.md before key opened.
