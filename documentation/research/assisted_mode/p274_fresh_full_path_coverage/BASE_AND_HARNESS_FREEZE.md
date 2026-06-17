# P274 — BASE_AND_HARNESS_FREEZE (Phase 1)

Frozen BEFORE dashboard/selector/coverage/triage/completion and any answer-key access. Deterministic; no API/answer
key. gondi source isolated at `/tmp/p274_fresh/gondi`.

## Commands
```
OUT=documentation/research/assisted_mode/p274_fresh_full_path_coverage/outputs
python scripts/build_coverage_manifest.py --contract /tmp/p274_fresh/gondi --out $OUT/gondi_coverage_manifest.json
python scripts/accounting_checkpoint_audit.py       --manifest $OUT/gondi_coverage_manifest.json --out $OUT/gondi_accounting_checkpoint.json --quiet
python scripts/state_transition_checkpoint_audit.py --manifest $OUT/gondi_coverage_manifest.json --out $OUT/gondi_state_transition_checkpoint.json --quiet
python scripts/research/recall_first_harness.py --manifest $OUT/gondi_coverage_manifest.json \
   --accounting $OUT/gondi_accounting_checkpoint.json --state-transition $OUT/gondi_state_transition_checkpoint.json \
   --out-dir $OUT/gondi_shadow --mode shadow --quiet
```

## Harness result
711 manifest functions · 77 checkpoint-hit · **15 advisory candidates** · guard **PASS** (0 violations). Frozen
hashes in metrics: P260 `d6b494bc3c0cc746` · P262 `a48336275cb65a4f` · harness_config `e9b74687793fd110`.

## Narrow baseline (rank 0–4) vs recall-delta (rank ≥5)
**Narrow top-5:** `MultiSourceLoan._processOffersFromExecutionData` (T3/T7) · `Pool.withdraw` (T2/T3) · `Pool.redeem`
(T1/T2/T3) · `Pool.mint` (T3/T8) · `WithdrawalQueue.mint` (T8).
**Recall-delta (10):** `WithdrawalQueue.withdraw` (T2) · `MultiSourceLoan.mergeTranches`/`_mergeTranches` (T4/T8) ·
`Pool.constructor`/`deployWithdrawalQueue`/`_queueClaimAll`/`_withdraw` (T2/T5/T6) · `LiquidationDistributor.distribute`
(T6) · `UserVault.burnAndWithdraw` (T2) · `AuctionWithBuyoutLoanLiquidator.settleWithBuyout` (T1/T2/T4/T5).
→ candidate pool spans **order/offer** (`_processOffersFromExecutionData`, `mergeTranches`), **accounting** (Pool
mint/withdraw/redeem, LiquidationDistributor), **DoS/liveness** (WithdrawalQueue, `_queueClaimAll`, distribute loop),
**state-machine/auction** (Pool.constructor/deploy, `settleWithBuyout`) — a genuinely multi-class pool.

recall-delta fraction = 10/15 = 0.67.

## Freeze hashes (sha256[:16])
| artifact | hash |
|---|---|
| gondi_coverage_manifest.json | `361197b387ae86da` |
| gondi_accounting_checkpoint.json | `71b76622bef25f8c` |
| gondi_state_transition_checkpoint.json | `7f529de1afa860fd` |
| recall_advisory_candidates.json | `7d47d8c1690bc793` |
| recall_metrics.json | `96e7946ef7bb642e` |

No answer key consulted. Next: Phase 2 advisory dashboard.
