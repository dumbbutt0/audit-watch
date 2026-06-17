# P264 — ROLLBACK_PLAN
## Disable (instant)
Default is already disabled. Ensure no caller passes --mode shadow/research_eval. config default_mode=disabled.
## Full removal (if desired)
Delete: scripts/research/recall_first_harness.py · config/research_recall_first_harness.json ·
schemas/recall_first_advisory.schema.json · tests/research/test_p264_production_grade_staging.py · this docs dir.
Nothing else imports the harness (un-wired) → removal cannot affect the pipeline.
## Verify production pipeline unchanged (hash checks)
sha256 must be unchanged: P260 d6b494bc · P262 a48336275cb65a4f · their configs c61da091 / 62e860199e7c51cd;
forbidden c1af70e1 dashboard_sync / c095c426 deep_trace / 2a15169a min_confirm_gate / afc481c9 confirm_gate /
ae55eb80 validate_p208. Active audit: output → audits/size-credit-2024-06-blind/output (unchanged). Harness is
un-wired: `grep -rn recall_first_harness run_pipeline.sh config/agent_policy.json` → no matches expected.
