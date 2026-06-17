# P272 — BASE_AND_HARNESS_FREEZE (Phase 1)

Frozen BEFORE dashboard/selector/triage/completion and any answer-key access. Deterministic; no API/answer key.
init-capital source isolated at `/tmp/p272_fresh/init`.

## Commands
```
OUT=documentation/research/assisted_mode/p272_fresh_blind_lending_recovery/outputs
python scripts/build_coverage_manifest.py --contract /tmp/p272_fresh/init --out $OUT/init_coverage_manifest.json
python scripts/accounting_checkpoint_audit.py       --manifest $OUT/init_coverage_manifest.json --out $OUT/init_accounting_checkpoint.json --quiet
python scripts/state_transition_checkpoint_audit.py --manifest $OUT/init_coverage_manifest.json --out $OUT/init_state_transition_checkpoint.json --quiet
python scripts/research/recall_first_harness.py --manifest $OUT/init_coverage_manifest.json \
   --accounting $OUT/init_accounting_checkpoint.json --state-transition $OUT/init_state_transition_checkpoint.json \
   --out-dir $OUT/init_shadow --mode shadow --quiet
```

## Harness result
963 manifest functions · 72 checkpoint-hit · **20 advisory candidates** · guard **PASS** (0 violations). Frozen
hashes in metrics: P260 `d6b494bc3c0cc746`/`c61da091ad3ed21e` · P262 `a48336275cb65a4f`/`62e860199e7c51cd` ·
harness_config `e9b74687793fd110`.

## Narrow baseline (rank 0–4) vs recall-delta (rank ≥5)
**Narrow top-5:** `PosManager.removeCollateralWLpTo` (T3/T7) · `LendingPool.mint` (T3/T6/T8) ·
`LendingPool.accrueInterest` (T6) · `WLpMoeMasterChef.harvest` (T1) · `InitCore.mintTo` (T8).

**Recall-delta (15):** `MarginTradingHook.repayDebt` (T7/T8) · `LendingPool.burn` (T2/T3/T6) · `PosManager._harvest`
(T1) · `MarginTradingHook.addCollateral` (T7/T8) · **`InitCore._liquidateInternal`** (T1/T7) · `InitCore.burnTo`
(T2) · `LendingPool.borrow` (T3/T6) · `PosManager.harvestTo` (T1) · `MoneyMarketHook._handleDeposit` (T8) ·
`Config.getModeConfig` (T7) · `PosManager.removeCollateralTo` (T3/T7) · `MarginTradingHook.removeCollateral` (T7) ·
**`InitCore.getCollateralCreditCurrent_e36`** (T7) · `MarginTradingHook.coreCallback` (T3) ·
`MarginTradingHook._calculateFillOrderInfo` (T9). → the **liquidation (InitCore._liquidateInternal) + collateral-
credit/health (getCollateralCreditCurrent) + debt/share (LendingPool borrow/burn) + collateral (PosManager
removeCollateral) + margin-trading** subsystems are recall-delta; narrow surfaces the plain mint/accrue/harvest flow.

recall-delta fraction = 15/20 = 0.75.

## Freeze hashes (sha256[:16])
| artifact | hash |
|---|---|
| init_coverage_manifest.json | `482f61f7ac05e741` |
| init_accounting_checkpoint.json | `0fa6255cae2db84f` |
| init_state_transition_checkpoint.json | `fb9dc384a6052969` |
| recall_advisory_candidates.json | `000b69658811261b` |
| recall_metrics.json | `359c34febd8e38f8` |

No answer key consulted. Next: Phase 2 advisory dashboard.
