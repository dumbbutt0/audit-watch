# P223 — Plan (as executed)

**Goal:** run the proven P215 full-funnel sequence, blind, on a Solidity-heavy finished contest chosen for
clean-reportable probability, to a scored result. **Target:** Size Credit 2024-06 (4H/9M focused key).
**Discovery:** key-blind deep_trace subagents. **Scope:** full hunt to scored result.

**Executed sequence (all safety invariants held):**
1. Integrity precheck — START hashes, api_free=true, witness sealed-key sha256, record active audit. →
   `INTEGRITY_PRECHECK.md`
2. Fork pristine blind workspace `size-credit-2024-06-blind` (source-only copy; answer key sealed in the
   original); switch active. → `BLINDNESS_AND_ISOLATION.md`, `TARGET_SELECTION.md`
3. Coverage manifest (source-only, sandbox-checked) — 221 items / 193 in-scope. → `COVERAGE_MANIFEST.md`
4. Key-blind discovery — 5 source-only Sonnet deep_trace subagents (liquidation/accounting/offer_market/
   custody/config_multicall) → 12 deduped candidates → `merged_findings.json`. → `CANDIDATE_REGISTER.json`
5. Triage (zero-API in-session) → 3 poc_required, 9 downgraded; review-gate (coverage override). →
   `TRIAGE_RESULTS.md`
6. Gates: min_confirm PASS, confirm_gate eval+submission PASS. → `CONFIRM_GATE_RESULTS.md`
7. L3 readiness + harness: SC-01 executed L3 PASS (3/3 on real source); SC-03/04 NEEDS_HARNESS. →
   `L3_READINESS_RESULTS.md`, `pocs/p223/`
8. Dry-run queue (local, 3 entries, 0 High-without-L3-PASS) + final_submission_pack + freeze. →
   `DRY_RUN_QUEUE_AUDIT.md`, `DASHBOARD_REVIEW.md`, `FREEZE_MANIFEST.{md,json}`
9. Score vs sealed key (post-freeze; hash re-verified) — 2 HIT + 3 PARTIAL of 13, 0 fabricated false-Highs. →
   `SCORING.md`, `metrics.json`
10. Restore active audit, unset flag, verify byte-identical START==END, regression. → `integrity_checks.md`,
    `P223_RECOMMENDATION.md`

**Decision:** `SIZE_CREDIT_HUNT_CLEAN_REPORTABLE` (see `P223_RECOMMENDATION.md`).
