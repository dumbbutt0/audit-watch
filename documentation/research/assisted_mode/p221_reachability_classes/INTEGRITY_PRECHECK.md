# P221 — Integrity precheck (START)

`api_free=true`. Research-only; no audit switch. Same additive 2-file footprint as P219.

## START md5 (first 8)
### Edited (intended)
| md5 | file |
|-----|------|
| 87764e5e | scripts/sync_hunt_findings.py |
| 78c41bf5 | scripts/finding_detail.py |
| 33a42431 | documentation/research/funnel/synced_findings.generated.json |
| a4f5271e | output_research/l3_readiness/ZETA-04.json |
| 9cafab99 | output_research/l3_readiness/ZETA-10.json |
| 69e209c9 | output_research/l3_readiness/ZETA-11.json |

### Must stay byte-identical
| md5 | file |
|-----|------|
| 26bd7ee0 | scripts/dashboard_sync.py |
| fe37e6ad | scripts/validate_p208_l3_readiness.py (decide — severity authority) |
| 9e38136e | scripts/run_hunt_sync_hook.py |
| 00cf5f56 | scripts/validate_hunt_sync_completion.py |
| d9f09981 | scripts/funnel.py |
| 5c6cccb5 | scripts/findings_overview.py |
| 197ac4d5 | scripts/dashboard.py |
| 04211964 | run_pipeline.sh |
| ef93a6c2 | prompts/deep_trace.md |
| 41dd3c96 | scripts/min_confirm_gate.py |
| 4fadfc5f | scripts/confirm_gate.py |
| bea43487 | config/runtime_policy.json |

## Severity baseline (pre-edit decide())
ZETA-04 medium / high_allowed=False · ZETA-10 invalid / False · ZETA-11 medium / False.
END hashes + equality verdict + post-edit decide() in `integrity_checks.md`.
