# P222 — Integrity checks (END)

`api_free=true`. Research-only; 0 route/submit/promote; no submit/promote controls added; no severity moved;
no fabrication (impact_type / priority derived only from L3-recorded evidence).

## Changed (intended)
| file | START → END |
|------|-------------|
| (new) scripts/human_review_priority.py | — → cbdfc7fd (pure classifier) |
| scripts/sync_hunt_findings.py | eb8c7d03 → a060a992 (hrp import + impact_type + evaluate_priority + 6 fields + CARD_INJECT) |
| scripts/finding_detail.py | 8e4ab621 → 0f57665e (read-only top_line_status banner) |
| scripts/funnel.py | d9f09981 → 89ac489a (whitelist priority fields into rows) |
| scripts/findings_overview.py | 5c6cccb5 → 01159526 (_effective_rank boost-only sort + carry fields) |
| scripts/dashboard.py | 197ac4d5 → 9de16b68 (read-only ?human_review_priority= filter; expose fields) |
| scripts/validate_hunt_sync_completion.py | 00cf5f56 → 10c492f5 (_PRIORITY_VALUES + 3 invariant checks) |
| output_research/l3_readiness/ZETA-04.json | 9fa27fa3 → 33789e21 (additive impact_type) |
| output_research/l3_readiness/ZETA-11.json | 86b92407 → b41965d9 (additive impact_type) |
| documentation/research/funnel/synced_findings.generated.json | ac8978df → bcf4c1c1 (additive priority fields + impact_type) |
| (new) tests/research/test_p222_human_review_priority.py | NEW (20 tests) |
| tests/research/test_hunt_sync_completion.py | edited: `_rec()` fixture seeds `human_review_priority="NONE"` (2 stale P218 guard tests) |
| output_research/funnel/sync_hook_metrics.json | regenerated |
| (new) documentation/research/assisted_mode/p222_human_review_priority/** | NEW (13 deliverables) |

## Byte-identical START==END (verified)
- **scripts/dashboard_sync.py 26bd7ee0** (synced-record contract + safety constants — untouched)
- **scripts/validate_p208_l3_readiness.py fe37e6ad** (decide severity authority — untouched)
- scripts/submission_readiness_review.py e4960878 · scripts/run_hunt_sync_hook.py 9e38136e ·
  output_research/l3_readiness/ZETA-10.json e6b8eeeb · config/runtime_policy.json bea43487
- **Forbidden:** prompts/deep_trace.md ef93a6c2 · scripts/min_confirm_gate.py 41dd3c96 ·
  scripts/confirm_gate.py 4fadfc5f

## Severity invariance (post-edit decide(), verified)
ZETA-04 medium/False · ZETA-10 invalid/False · ZETA-11 medium/False — identical to the START baseline.
`decide()` keys off `attacker_model`/`l3_status`/`impact_class`/material-delta/control — never off
`human_review_priority`, `reachability_class`, or `impact_type`. Test asserts this + that no priority value is
ever an `attacker_model` value.

## Mirror diff (vs START ac8978df)
Purely additive: top-level non-additive drift NONE; only the six priority keys (12 records) + `impact_type`
(ZETA-04/11) + nested `_field_provenance` gaining those keys. No existing value modified or removed.

## Sync hook
exit 0; completion guard PASS (failures/warnings/reader/card empty; 12 records; all_safety_ok True;
completeness 90%; completion_ok True).
