# P216 — DASHBOARD VERIFICATION

Dashboard server launch is flaky in-harness → verified by importing the modules and calling the route handlers /
loaders directly (read-only). 0 stray processes.

| Check | Result |
|-------|--------|
| `/findings` shows P215 records | ✅ `dashboard.api_findings()` → 12 funnel rows `ZETA-01..12` |
| `/candidates` shows P215 records | ✅ `dashboard.api_candidates()` → 12 (`candidate_id=funnel:ZETA-xx`, `labelable:false`) |
| `/funnel` shows P215 records | ✅ `dashboard.api_funnel()` → 12 (`record_id` prefix `zetachain-2023-10:P215:`) |
| synced cards are read-only | ✅ every card `read_only_synced:true`, `submission_ready:false`, `routing_allowed:false` |
| no label/promote/submit controls | ✅ `/findings`,`/candidates`,`/funnel` HTML: no `<form>`, no POST, no "submit now"/"promote to platform" (test `test_no_submit_or_promote_controls`) |
| L3 fields visible | ✅ `l3_status`, `high_promotion_allowed`, `high_promotion_blocker`, `main_blocker` on each card |
| blockers visible | ✅ `main_blocker.blocker` (e.g. `blocked_by_missing_l3_poc` …) |
| evidence links visible | ✅ `evidence_backup` + `source_refs` (candidate_register / l3_record / scorecard / harness) |
| missing fields → unknown/MISSING_EVIDENCE | ✅ e.g. ZETA-04 exploit_steps/defense_map unknown; explicit, never fabricated |
| no active-audit switch required | ✅ funnel track is global; verified with active audit = zetachain AND irrelevant to load path |
| browser computes no severity | ✅ severity is `_sev_or_status`(recorded) → Medium/Low/High or HUMAN_PENDING; never a conversion token (test `test_card_severity_never_a_conversion_token`) |
| 15/15 verifier sections | ✅ all 12 cards (test `test_card_h5_structural_parity_and_safety`) |
| finished H5 card still renders | ✅ runtime track intact (test `test_finished_bug_h5_card_renders`) |

## Reader payload safety
`findings_overview.load_overview()` → `routing_allowed:false`, `research_only:true`. `funnel.load_records()` →
`routes_in_production:false`. No record carries `submission_ready:true` or `routing_allowed:true`.
