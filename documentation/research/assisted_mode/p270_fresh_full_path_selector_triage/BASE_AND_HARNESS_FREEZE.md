# P270 — BASE_AND_HARNESS_FREEZE (Phase 1)

Frozen BEFORE dashboard/selector/triage and any answer-key access. Deterministic; no API/answer key. wise-lending
source isolated at `/tmp/p270_fresh/wise` (never under `audits/`).

## Commands
```
OUT=documentation/research/assisted_mode/p270_fresh_full_path_selector_triage/outputs
python scripts/build_coverage_manifest.py --contract /tmp/p270_fresh/wise --out $OUT/wise_coverage_manifest.json
python scripts/accounting_checkpoint_audit.py       --manifest $OUT/wise_coverage_manifest.json --out $OUT/wise_accounting_checkpoint.json --quiet
python scripts/state_transition_checkpoint_audit.py --manifest $OUT/wise_coverage_manifest.json --out $OUT/wise_state_transition_checkpoint.json --quiet
python scripts/research/recall_first_harness.py --manifest $OUT/wise_coverage_manifest.json \
   --accounting $OUT/wise_accounting_checkpoint.json --state-transition $OUT/wise_state_transition_checkpoint.json \
   --out-dir $OUT/wise_shadow --mode shadow --quiet
```

## Harness result
- 769 in-scope functions · 167 checkpoint-hit functions · **24 advisory candidates** · guard **PASS** (0 violations).
- frozen hashes recorded in metrics: P260 `d6b494bc3c0cc746`/`c61da091ad3ed21e` · P262 `a48336275cb65a4f`/
  `62e860199e7c51cd` · harness_config `e9b74687793fd110`.

## Narrow baseline (rank 0–4) vs recall-delta (rank ≥5)
**Narrow top-5:** `PendlePowerFarmToken.withdrawExactShares` · `WiseLending.withdrawExactShares` (T2/T7) ·
`PendlePowerFarmToken.depositExactAmount` (T8) · `WiseLending.withdrawOnBehalfExactShares` (T2/T7) ·
`WiseLending.borrowExactAmount` (T7). → deposit/withdraw/borrow share flow.

**Recall-delta (19):** PositionNFTs mint{,ForUser,_ForUser,approveMint} (T8) · `WiseLending.depositExactAmountMint` /
`solelyDepositMint` (T8) · `WiseCore._handleDeposit`/`_checkDeposit`/`_checkMaxDepositValue` (T8) ·
**`WiseCore._withdrawPureCollateralLiquidation`** / **`_withdrawOrAllocateSharesLiquidation`** (T2/T7 liquidation) ·
`WiseLending.withdrawExactSharesETH` (T2/T7) · `WiseSecurityHelper._getPossibleWithdrawAmount` (T2) ·
`PendlePowerFarmController.withdrawLock` (T2) · **`PendlePowerFarmToken._calculateRewardsClaimedOutside`** (T2/T9) ·
**`FeeManager.paybackBadDebtForToken`** / **`paybackBadDebtNoReward`** (T7 bad debt) · `PoolManager.setPoolParameters`
(T7/T8). → the **liquidation (WiseCore) + bad-debt (FeeManager) + Pendle-power-farm reward/share + deposit-mint
subsystems** are recall-delta; narrow surfaces only the plain deposit/withdraw/borrow flow.

recall-delta fraction = 19/24 = 0.79.

## Freeze hashes (sha256[:16])
| artifact | hash |
|---|---|
| wise_coverage_manifest.json | `77af095527f45bcc` |
| wise_accounting_checkpoint.json | `431ed033c5fe7e6d` |
| wise_state_transition_checkpoint.json | `45661c4e026a4088` |
| recall_advisory_candidates.json | `090d10d12e099355` |
| recall_metrics.json | `a8e0bddd99e4d2ba` |

No answer key consulted. Next: Phase 2 advisory dashboard.
