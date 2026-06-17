# P146 — Integrity Check (requirement 7)

## Claims and how each is proven
| claim | proof |
|---|---|
| **Prompt metrics unchanged** | `test_integrity_prompt_metrics_unchanged`: build `scorecard` with an EMPTY sidecar vs a POPULATED sidecar; assert `per_arch`, `totals`, and `runs[*].totals` are **value-for-value identical** (while the panel's confirmed-count changes 0→1). Plus the live `all` run reproduces the P142 baseline `totals` exactly (`finding 3 / needs_human 1 / strong_clear 7`, `useful_recall 0.80`, `clean_FP 0.0`). |
| **Panel is supplemental only** | The panel derives solely from `corpus.jsonl` + `runtime_status.jsonl`; `per_arch`/`totals`/`runs` are computed solely from the queues + ingestion reports. The `integrity` block carries `supplemental_only:true`, `prompt_metrics_mutated_by_panel:false`. |
| **No production source changed** | Only 4 files touched, all research-only: `scripts/research/value_provenance_eval_harness.py`, `output_research/...runtime_status.jsonl`, `config/research/value_provenance_eval_harness.json`, `tests/research/...`. No file under the production tree (`run_pipeline.sh`, `config/agent_policy.json`, `scripts/*` outside `scripts/research/`, any `audits/*/contracts`) modified. |
| **routing_allowed false for all sidecar/panel rows** | `build_runtime_panel` **forces** `routing_allowed=False` + `submission_ready=False` on every row regardless of sidecar contents; `integrity.routing_allowed_all_false` / `submission_ready_all_false` computed True; `test_panel_backfill_and_forced_flags` feeds a sidecar row with `routing_allowed:true`/`submission_ready:true` and asserts they are forced False. |
| **Harness stays un-wired** | `test_no_production_wiring` + `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` → empty. |

## Live integrity block (from `runtime_panel.json`)
```json
{ "supplemental_only": true, "production_source_modified": false,
  "routing_allowed_all_false": true, "submission_ready_all_false": true,
  "prompt_metrics_keys": ["per_arch","totals","runs"], "prompt_metrics_mutated_by_panel": false,
  "backfilled": ["B1","B5"] }
```

## Panel summary (live)
`{rows: 11, by_status: {runtime_confirmed: 2, not_run: 9}}` — exactly B1 + B5 backfilled; 9 not_run.
