# P218 — HOOK FAILURE TESTS

`tests/research/test_hunt_sync_completion.py` — 13/13 PASS (0.05s; pure `run_checks` + injectable card loaders).
Each proves completion FAILS (or warns→strict-fails) on a specific violation:

| Test | Violation | Expected |
|------|-----------|----------|
| test_missing_candidate_fails | candidate absent from mirror | FAIL |
| test_unsafe_flags_fail | `routing_allowed:true` | FAIL |
| test_high_without_l3_pass_or_blocker_fails | High + high_promotion_allowed without L3 PASS | FAIL |
| test_high_blocked_without_blocker_fails | High blocked but no blocker recorded | FAIL |
| test_dry_run_queue_without_synced_record_fails | **dry-run-queue entry, no synced record** (reviewer-added) | FAIL |
| test_duplicate_record_ids_fail | duplicate `record_id` | FAIL |
| test_malformed_record_fails | record missing schema/safety fields | FAIL |
| test_missing_package_link_warns_and_strict_fails_hook_level | queued candidate, no package/queue link | WARN → strict FAIL |
| test_stale_extra_record_fails | phase record not in register | FAIL |
| test_detail_card_cannot_load_fails | detail card raises | FAIL |
| test_detail_card_missing_sections_fails | card missing verifier sections | FAIL |
| test_happy_path_passes | all good | PASS |
| test_live_real_p215_passes | real P215 mirror | PASS (12/12) |

Live demonstration (CLI): a mirror with ZETA-04 removed →
`failures:["ZETA-04: missing from synced mirror","dry-run-queue entry ZETA-04 has no synced dashboard record"]`,
exit 1.
