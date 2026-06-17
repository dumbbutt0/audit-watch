# P155 — Integrity Checks

P155 is a **source-only reportability review**. No production / harness / prompt / corpus / gate change.

| Claim | Verification | Result |
|---|---|---|
| Production source unchanged | md5 `LockingMultiRewards.sol` | `74937ac70403a79dff31bbc8d427e87c` (baseline) ✓ |
| P154 harness unchanged | `pocs/p154/{foundry.toml,test/*.t.sol,execution_output.txt}` not edited | ✓ |
| No harness `.py` change | `value_provenance_eval_harness.py` only executed read-only (panel/scorecard) | ✓ |
| Prompt baseline unchanged | scorecard totals = baseline (finding 3 / needs_human 1 / strong_clear 7 / useful_recall 0.8 / clean_FP 0.0); panel `prompt_corpus_unchanged:true`, `prompt_metrics_mutated_by_panel:false` | ✓ |
| Corpus unchanged | `corpus.jsonl` not touched | ✓ |
| Sidecar = data-only, in place | 7 rows (no new row); H5 enriched with `p155_*` fields; **other 6 rows byte-identical** (verified programmatically); JSONL valid; `runtime_status` of H5 still `runtime_confirmed`; conversion.outcome still `reportable_candidate_needs_human_review` | ✓ |
| Active audit symlink unchanged | `readlink output` → `audits/quantamm-2024-12-eval/output` | ✓ |
| Harness un-wired | `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty | ✓ |
| routing_allowed=false / submission_ready=false (all rows) | panel forces; integrity block confirms | ✓ |
| No detector/gate/severity/submission policy change | no such files edited | ✓ |
| Tests run / docs-only reason | **docs-only review** (no code change); runtime evidence re-cited from retained P154 `execution_output.txt`; full `pytest` run to confirm baseline | see below |
| Pre-existing failures separated | the 2 `deep_solidity` frozen-snapshot fails are pre-existing (output/ symlink coupling), unrelated to P155 | ✓ |

## Test results
- **pytest** (full): **1673 passed / 2 pre-existing deep_solidity snapshot fails / 4 skipped** — unchanged
  baseline. P155 adds **no** pytest tests (sidecar enrichment is data-only).
- **forge:** not re-run (docs-only review); the P154 PoC output stands in `pocs/p154/execution_output.txt`
  (4/4 pass).

## Files changed this phase (all docs / data — none production)
- `documentation/research/assisted_mode/p155_abracadabra_h5_review/*` (deliverables)
- `output_research/value_provenance_eval/runtime_status.jsonl` (data-only enrichment of the H5 row)
- `output_research/value_provenance_eval/{runtime_panel.json,scorecard.json}` (regenerated read-only artifacts)
