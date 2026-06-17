# P289 — LOSS_REWARD_REMAP_RESULTS

Supervised re-map with the 4 new lenses. Sources: `outputs/remap_metrics.json`, `outputs/lens_evidence.json`.

## ECG (the repair target): READY 0 → 1
| candidate | P288 | P289 |
|---|---|---|
| **SurplusGuildMinter.stake** | NEEDS_VALUE_FLOW_EVIDENCE | **READY_FOR_POC_INTENT** (LOSS_ON_STAKE_FOUND) |
| ERC20RebaseDistributor._burn / distribute · ProfitManager.claimRewards · LendingTerm.borrow/_borrow | NEEDS_VALUE_FLOW | unchanged (no lens match / precise block) |
| LendingTerm.onBid | INLINE_GUARD_REFUTED | unchanged (non-value class + D1 — precise non-lens block) |
| SimplePSM.redeem | NEEDS_STATE_MACHINE | unchanged |

`SurplusGuildMinter.stake` is the exact awarded **H-04** locus; lens 1 matched the incomplete same-block-only loss guard.

## Lens matches across the full sample (ECG + kelp + blackhole + panoptic + silo + revert-lend + hybra)
- **2 lens matches total**: ECG `SurplusGuildMinter.stake` (loss_on_stake → **READY**) and hybra `GaugeCL.withdraw`
  (share_transfer_theft → **held at NEEDS_STATE_MACHINE**, not lifted — state class). Lenses 2 (bad_debt_contagion) and
  3 (reward_index_init) matched nothing in this sample.
- **Lens lifts to READY: 1** (the awarded ECG locus). **false READY: 0.** severe concluded/reportable FP: **0**.

## Regressions (all stable)
- kelp **getRsETHAmountToMint** → READY (D4.6 oracle; no lens interference).
- blackhole **claim_many** → READY (sibling; no lens interference).
- **L2Governor.execute** → READY (state-machine; no lens interference).
- panoptic/silo/revert-lend prior samples: 0 new READY, 0 lens lift, severe FP=0.
