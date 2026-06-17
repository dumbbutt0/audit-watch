# P217 — DASHBOARD VERIFICATION

Verified by direct loader/handler calls (server flaky in-harness); 0 stray processes; no active-audit switch.

| Check | Result |
|-------|--------|
| `funnel.load_records()` includes generated records | ✅ 12 P215 (8 curated + 12 mirror = 20 total) |
| `findings_overview.load_overview()` includes them | ✅ 12 funnel rows `ZETA-01..12` |
| `/api/funnel` | ✅ 12 |
| `/api/findings` | ✅ 12 funnel rows; `research_only:true`, `routing_allowed:false` |
| `/api/candidates` | ✅ 12 (`candidate_id=funnel:ZETA-xx`, `labelable:false`) |
| detail view `funnel:ZETA-04` (and 07/11) | ✅ loads; 15/15 verifier sections |
| richer fields now populated | ✅ mechanism, exploit_steps, defense_map (recommended fix), attacker_model, function_map role, ZETA-07 PoC REPRODUCED |
| severity | ✅ recorded (Medium/Low/High) or HUMAN_PENDING; never a conversion token; browser computes none |
| L3 status + blockers visible | ✅ `l3_status`, `high_promotion_blocker`, `main_blocker` |
| dry-run-queue state visible | ✅ where a queue record exists |
| post-score notes visible | ✅ `last_reviewer_note` (scorecard line) |
| missing fields explicit | ✅ `novelty_duplicate` = unknown; missing-artifact warnings emitted |
| submit/promote controls | ✅ none (HTML unchanged from P216; test enforces) |
| no active-audit switch required | ✅ global funnel track; active audit = zetachain but irrelevant to load path |
