# P266 — BASE_AND_HARNESS_FREEZE (Phase 1)

Frozen BEFORE the dashboard surface, triage, and any answer-key access. All commands are deterministic and need no
API key / no answer key.

## Commands
```
MAN=audits/phi-2024-08-fresh/output/coverage_manifest.json
OUT=documentation/research/assisted_mode/p266_full_production_path_test/outputs
python scripts/accounting_checkpoint_audit.py        --manifest $MAN --out $OUT/phi_accounting_checkpoint.json --quiet
python scripts/state_transition_checkpoint_audit.py  --manifest $MAN --out $OUT/phi_state_transition_checkpoint.json --quiet
python scripts/research/recall_first_harness.py --manifest $MAN \
   --accounting $OUT/phi_accounting_checkpoint.json --state-transition $OUT/phi_state_transition_checkpoint.json \
   --out-dir $OUT/phi_shadow --mode shadow --quiet
```

## Harness result
- 257 in-scope manifest functions · 45 checkpoint-hit functions · **18 advisory candidates** · guard **PASS**
  (0 violations) · all promotion flags false.
- forced-by-clause: top_n_overall 10 · t7t8_within_top 10 · checkpoint_hit_name_keyword 13 ·
  checkpoint_hit_evidence_marker 4 · t9_math_name 1.
- frozen module hashes recorded in metrics: P260 `d6b494bc3c0cc746`/`c61da091ad3ed21e` · P262
  `a48336275cb65a4f`/`62e860199e7c51cd` · harness_config `e9b74687793fd110`.

## Narrow baseline (P260 rank 0–4) vs recall-delta (rank ≥5 or null)
**Narrow top-5 (the old pre-P262 path would examine these):**
`PhiFactory.signatureClaim` (T2/T5/T8) · `PhiFactory.merkleClaim` (T2/T5/T8) ·
`CuratorRewardsDistributor.distribute` (T6) · `PhiFactory._validateAndUpdateClaimState` (T2/T8) ·
`PhiNFT1155.claimFromFactory` (T2/T5/T8). → claim-flow + one reward-distribute locus.

**Recall-delta (13, forced in beyond narrow top-5):**
`Cred._handleTrade` (T5) · `Cred._executeBatchTrade` (T5) · `Cred._updateCuratorShareBalance` (T1) ·
`PhiNFT1155.mint` (T8) · `PhiFactory._processClaim` (T2/T8) · `RewardControl.depositBatch` (T8) ·
`RewardControl.withdrawWithSig` (T2) · `RewardControl.deposit` (T8) · `CuratorRewardsDistributor.deposit` (T8) ·
`PhiRewards.depositRewards` (T8/T9) · `PhiRewards.handleRewardsAndGetValueSent` (T8) ·
`Cred._validateAndCalculateBatch` (T9) · `Claimable._decodeMerkleClaimData` (T2/T8/T9).
→ the entire **Cred bonding-curve trade + curator-share + RewardControl/PhiRewards reward-accounting subsystem** is
recall-delta; the narrow path surfaces only `distribute` from the reward side and otherwise the claim flow.

recall-delta fraction = 13/18 = 0.72 (consistent with the P265 pooled 72.7%).

## Freeze hashes (sha256[:16])
| artifact | hash |
|---|---|
| phi coverage_manifest.json | `4961a240698e61fe` |
| phi_accounting_checkpoint.json | `f1041827b9704975` |
| phi_state_transition_checkpoint.json | `356aa3775db311a7` |
| recall_advisory_candidates.json | `18f3d80f2b3c5dfa` |
| recall_metrics.json | `cb3c5a81e603611a` |
| recall_guard_report.json | `bccd48cb6fe53c3f` |

No answer key consulted. Next: Phase 2 standalone advisory dashboard surface (freeze before triage).
