# P268 — BASE_AND_HARNESS_FREEZE (Phase 2)

Frozen BEFORE the dashboard surface, triage, selector, and any answer-key access. Deterministic; no API key / no
answer key. Karak source isolated at `/tmp/p268_fresh/karak` (never under `audits/`).

## Commands
```
OUT=documentation/research/assisted_mode/p268_fresh_full_path_with_selector/outputs
python scripts/build_coverage_manifest.py --contract /tmp/p268_fresh/karak --out $OUT/karak_coverage_manifest.json
python scripts/accounting_checkpoint_audit.py       --manifest $OUT/karak_coverage_manifest.json --out $OUT/karak_accounting_checkpoint.json --quiet
python scripts/state_transition_checkpoint_audit.py --manifest $OUT/karak_coverage_manifest.json --out $OUT/karak_state_transition_checkpoint.json --quiet
python scripts/research/recall_first_harness.py --manifest $OUT/karak_coverage_manifest.json \
   --accounting $OUT/karak_accounting_checkpoint.json --state-transition $OUT/karak_state_transition_checkpoint.json \
   --out-dir $OUT/karak_shadow --mode shadow --quiet
```

## Harness result
- manifest: 225 in-scope items (199 in-scope functions) · 36 checkpoint-hit functions · **20 advisory candidates** ·
  guard **PASS** (0 violations) · all promotion flags false.
- frozen module hashes recorded in metrics: P260 `d6b494bc3c0cc746`/`c61da091ad3ed21e` · P262 `a48336275cb65a4f`/
  `62e860199e7c51cd` · harness_config `e9b74687793fd110`.

## Narrow baseline (rank 0–4) vs recall-delta (rank ≥5 or null)
**Narrow top-5:** `NativeVault.validateWithdrawalCredentials` (T2/T5) · `NativeVault.finishWithdrawal` (T2/T5) ·
`NativeVault._startSnapshot` (T6) · `NativeVault.startWithdrawal` (T2/T5) · `SlasherLib.requestSlashing` (T5).
→ native-ETH withdrawal flow + slashing request.

**Recall-delta (15, forced beyond narrow top-5):**
`Vault.mint` (T5/T8) · `Vault.startRedeem` (T1/T2/T5) · `NativeVault.validateSnapshotProofs` (T5/T6) ·
`NativeVault.withdrawableWei` (T2) · `Vault.finishRedeem` (T1/T2/T5) · `NativeVaultLib.validateWithdrawalCredentials`
(T2) · `SlasherLib.finalizeSlashing` (T5) · `SlasherLib.cancelSlashing` (T5) · `BeaconProofs.validateBalance` (T6) ·
`BeaconProofs.validateValidatorProof` (T6) · `Merkle.verifyInclusion{Keccak,Sha256}` (T6) ·
`Merkle.processInclusionProof{Keccak,Sha256}` (T6) · `NativeVaultLib.calculateWithdrawKey` (T2/T9).
→ the **ERC4626-style Vault share/redemption subsystem** (mint/startRedeem/finishRedeem) + slashing state machine +
beacon/merkle proof verification are recall-delta; the narrow path surfaces only the native-ETH withdrawal flow.

recall-delta fraction = 15/20 = 0.75 (consistent with the P265 pooled 72.7%).

## Freeze hashes (sha256[:16])
| artifact | hash |
|---|---|
| karak_coverage_manifest.json | `cb7bd086e9ec99fc` |
| karak_accounting_checkpoint.json | `50c014b221c6a4d8` |
| karak_state_transition_checkpoint.json | `82d45e222e62a46d` |
| recall_advisory_candidates.json | `7138129294930f7e` |
| recall_metrics.json | `1b326bfeb2e2f4e3` |

No answer key consulted. Next: Phase 3 advisory dashboard surface.
