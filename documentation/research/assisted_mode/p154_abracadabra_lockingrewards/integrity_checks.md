# P154 — Integrity Checks

| Claim | Verification | Result |
|---|---|---|
| Production source unchanged | md5 of `LockingMultiRewards.sol` before/after | `74937ac70403a79dff31bbc8d427e87c` == baseline ✓ |
| No harness `.py` change | only `value_provenance_eval_harness.py` *executed* read-only (runtime-panel/scorecard); no edit | ✓ |
| Prompt baseline unchanged | `scorecard` totals = P138 baseline (finding 3 / needs_human 1 / strong_clear 7 / useful_recall 0.8 / clean_FP 0.0); panel integrity `prompt_corpus_unchanged:true`, `prompt_metrics_mutated_by_panel:false` | ✓ |
| Corpus unchanged | `corpus.jsonl` not touched (only the sidecar appended) | ✓ |
| Sidecar append-only | `runtime_status.jsonl` 6 → 7 rows; H1–H4 + B1/B5 byte-identical; H5 appended; JSONL parses | ✓ |
| PoC isolated | all PoC under `audits/abracadabra-2024-03-holdout/pocs/p154/`; `lib/out/cache` removed; only `foundry.toml` + `test/*.t.sol` + `execution_output.txt` retained | ✓ |
| Harness un-wired | `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty | ✓ |
| Active audit symlink unchanged | `readlink output` → `audits/quantamm-2024-12-eval/output` | ✓ |
| routing_allowed=false (all rows) | panel forces it; integrity `routing_allowed_all_false:true` | ✓ |
| submission_ready=false (all rows) | H5 + every row; integrity `submission_ready_all_false:true` | ✓ |
| No detector/gate/severity/submission policy change | no files under those trees edited | ✓ |
| Tests run + recorded | `forge test` 4/4 pass (execution_output.txt); full `pytest` recorded below | see below |
| Pre-existing failures separated | the 2 `deep_solidity` frozen-snapshot fails are pre-existing (output/ symlink coupling), distinct from this phase | ✓ |

## Test results
- **forge** (`pocs/p154`): `4 passed; 0 failed; 0 skipped`.
- **pytest** (full): expected unchanged baseline **1673 passed / 2 pre-existing deep_solidity snapshot
  fails / 4 skipped** — P154 adds **no** pytest tests (sidecar is data-only). Final count recorded in the
  phase memory and closeout.

## Files changed this phase (all research/PoC/docs — none production)
- `documentation/research/assisted_mode/p154_abracadabra_lockingrewards/*` (deliverables)
- `audits/abracadabra-2024-03-holdout/pocs/p154/{foundry.toml,test/*.t.sol,execution_output.txt}` (isolated PoC)
- `output_research/value_provenance_eval/runtime_status.jsonl` (one data-only appended row)
- `output_research/value_provenance_eval/{runtime_panel.json,scorecard.json}` (regenerated read-only research artifacts)
