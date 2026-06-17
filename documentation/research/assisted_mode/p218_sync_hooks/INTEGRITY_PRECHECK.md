# P218 — INTEGRITY PRECHECK (START)

md5 first-8, captured before any change. api_free=true; active audit = zetachain-2023-10-holdout (restorable; P218 does
not switch it).

| File | START | expected END |
|------|-------|--------------|
| `scripts/sync_hunt_findings.py` | `8d8a3203` | unchanged |
| `scripts/dashboard_sync.py` | `26bd7ee0` | unchanged |
| `scripts/build_synced_findings.py` | `2fb00b0e` | unchanged |
| `scripts/funnel.py` | `d9f09981` | unchanged |
| `scripts/finding_detail.py` | `f12aa8d3` | unchanged |
| `scripts/findings_overview.py` | `5c6cccb5` | unchanged |
| `scripts/dashboard.py` | `197ac4d5` | unchanged |
| `scripts/submission_readiness_review.py` | `e4960878` | unchanged |
| `scripts/final_submission_pack.py` | `57cba16d` | unchanged |
| `run_pipeline.sh` | `04211964` | unchanged (NOT edited — shared across all audits) |
| `scripts/audit_manager.py` | `1fca3bcb` | unchanged |
| `documentation/research/funnel/synced_findings.generated.json` | `d578cd87` | unchanged or byte-identical (hook re-writes from same artifacts) |
| `documentation/research/funnel/funnel_records.json` | `b3278eed` | unchanged |
| `config/runtime_policy.json` | `bea43487` | unchanged (`api_free:true`) |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | unchanged |
| `prompts/deep_trace.md` | `ef93a6c2` | unchanged (forbidden) |
| `scripts/min_confirm_gate.py` | `41dd3c96` | unchanged (forbidden) |
| `scripts/confirm_gate.py` | `4fadfc5f` | unchanged (forbidden) |

New files only: `scripts/validate_hunt_sync_completion.py`, `scripts/run_hunt_sync_hook.py`,
`tests/research/test_hunt_sync_completion.py`, `output_research/funnel/sync_hook_metrics.json`, the P218 deliverables.
Confirmed: no live submit route; no dashboard submit/promote controls (P216/P217-verified, HTML unchanged).
