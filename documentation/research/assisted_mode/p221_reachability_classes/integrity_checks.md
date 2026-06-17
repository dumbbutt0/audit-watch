# P221 — Integrity checks (END)

`api_free=true`. Research-only; 0 route/submit/promote; no fabrication (granular fields populated only from L3 artifacts).

## Changed (intended)
| file | START → END |
|------|-------------|
| scripts/sync_hunt_findings.py | 87764e5e → eb8c7d03 (additive: `_REACH_CLASS`, class+structured-field extraction, CARD_INJECT) |
| scripts/finding_detail.py | 78c41bf5 → 8e4ab621 (additive: inline-preferred attacker fields, `reachability_class`, hardened `unpriv`) |
| documentation/research/funnel/synced_findings.generated.json | 33a42431 → ac8978df (additive `reachability_class` on all 12; granular fields on ZETA-04/10/11) |
| output_research/l3_readiness/ZETA-04.json | a4f5271e → 9fa27fa3 (additive reachability fields) |
| output_research/l3_readiness/ZETA-10.json | 9cafab99 → e6b8eeeb (additive reachability fields) |
| output_research/l3_readiness/ZETA-11.json | 69e209c9 → 86b92407 (additive reachability fields) |
| tests/research/test_evidence_extraction.py | edited: `test_reachability_from_confirm` ZETA-04 → ZETA-03 (ZETA-04 now supersedes confirm with its L3 verdict) |
| output_research/funnel/sync_hook_metrics.json | regenerated |
| (new) tests/research/test_p221_reachability_taxonomy.py | NEW |
| (new) documentation/research/assisted_mode/p221_reachability_classes/** | NEW (9 deliverables) |

## Byte-identical START==END (verified)
dashboard_sync.py 26bd7ee0 · **validate_p208_l3_readiness.py fe37e6ad (decide severity authority — untouched)** ·
run_hunt_sync_hook.py 9e38136e · validate_hunt_sync_completion.py 00cf5f56 · funnel.py d9f09981 ·
findings_overview.py 5c6cccb5 · dashboard.py 197ac4d5 · run_pipeline.sh 04211964 ·
prompts/deep_trace.md ef93a6c2 · scripts/min_confirm_gate.py 41dd3c96 · scripts/confirm_gate.py 4fadfc5f ·
config/runtime_policy.json bea43487.

## Severity invariance (post-edit decide(), verified)
ZETA-04 medium/False · ZETA-10 invalid/False · ZETA-11 medium/False — identical to the pre-edit baseline.
`attacker_model` enums unchanged; `reachability_class` never read by decide().

## Sync hook
exit 0; completion guard PASS (failures/warnings/reader/card empty; 12 records; all_safety_ok true; completeness 90%).
Mirror diff: all 12 gained the additive derived `reachability_class`; only ZETA-04/10/11 gained granular fields;
no severity/safety/attacker_model change on any record.
