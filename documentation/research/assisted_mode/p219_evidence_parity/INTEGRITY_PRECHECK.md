# P219 — INTEGRITY PRECHECK (START)

md5 first-8. api_free=true; active audit zetachain (not switched).

| File | START | expected END |
|------|-------|--------------|
| scripts/dashboard_sync.py | 26bd7ee0 | unchanged |
| scripts/sync_hunt_findings.py | 8d8a3203 | **CHANGE** (richer extraction + provenance) |
| scripts/validate_hunt_sync_completion.py | 00cf5f56 | unchanged |
| scripts/run_hunt_sync_hook.py | 9e38136e | unchanged |
| scripts/funnel.py | d9f09981 | unchanged |
| scripts/finding_detail.py | f12aa8d3 | **CHANGE** (additive inline impact preference) |
| scripts/findings_overview.py | 5c6cccb5 | unchanged |
| scripts/dashboard.py | 197ac4d5 | unchanged |
| scripts/submission_readiness_review.py | e4960878 | unchanged |
| documentation/research/funnel/synced_findings.generated.json | d578cd87 | **CHANGE** (richer; same 12 ids) |
| documentation/research/funnel/funnel_records.json | b3278eed | unchanged |
| config/runtime_policy.json | bea43487 | unchanged (api_free) |
| ledger | e23c5bc9 | unchanged |
| prompts/deep_trace.md | ef93a6c2 | unchanged (forbidden) |
| scripts/min_confirm_gate.py | 41dd3c96 | unchanged (forbidden) |
| scripts/confirm_gate.py | 4fadfc5f | unchanged (forbidden) |

Confirmed: no live submit route; no dashboard submit/promote controls; dashboard_sync.py NOT edited (injection done in the
wrapper). HARD RULE active: a field is populated only if tied to a specific artifact path; else unknown/MISSING_EVIDENCE.
