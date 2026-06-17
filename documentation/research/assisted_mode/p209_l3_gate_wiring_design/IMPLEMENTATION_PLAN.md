# P209 — implementation plan for P210 (written, NOT executed here)

Minimal, additive, override/default-safe changes to wire the layered design. Each item is fail-open except the
High-readiness check (fail-closed). No gate ordering or discovery change.

1. **L3 fields on the readiness record.** Extend the readiness record (the append-only row written by
   `submission_readiness_review.py`) with the P208 output fields: `l3_status`, `poc_tier`,
   `calibrated_severity_after_l3`, `high_promotion_allowed`, `submission_blocker_codes`, `human_override_required`,
   `human_override_reason`, `evidence_summary`, `severity_target`. Additive; old rows valid.

2. **Call P208 `decide()` from `submission_readiness_review.py` ONLY.** Import
   `scripts/validate_p208_l3_readiness.decide`; when `severity_target==High`, compute readiness; map
   `high_promotion_allowed==false` → new state `blocked_by_missing_l3_poc`. Do NOT call it from any gate or discovery.
   Keep the module research-only/append-only; never flip `submission_ready`/`routing_allowed`.

3. **Add blocker code `blocked_by_missing_l3_poc`** to `READINESS_STATES` (+ map into `DISPLAY_SUBMISSION_STATUS` as a
   blocked label). For source-refuted/insufficient-impact reuse `blocked_by_missing_impact` or add
   `blocked_by_source_refutation`.

4. **Read-only dashboard panel.** In `dashboard.py` (and/or `finding_detail.py`) render: threat_ceiling ·
   calibrated_severity_after_l3 · l3_status/poc_tier · high_promotion_allowed · blocker · submission_state. Display
   only — flip no flags. Records lacking L3 → show `NEEDS_L3_HARNESS`.

5. **Tests / fixtures.** Reuse P208 `backtest/` + `regression/` fixtures as readiness inputs; add a
   `submission_readiness_review` test asserting: High+no-L3 → `blocked_by_missing_l3_poc`; High+L3_PASS → ready;
   Medium+no-L3 → unaffected; source-refuted → blocked. Add a state-machine transition test (forbidden transitions
   raise).

6. **Explicit no-submit guard.** Assert in tests + at call site that the L3 path never sets
   `submission_ready`/`routing_allowed=true` and never calls `final_submission_pack`/any router. Keep
   `api_free` untouched.

7. **Migration / defaults for old records.** Read-time defaulting only (High+missing → NEEDS_L3_HARNESS;
   Medium+missing → no effect). No backfill, no rewrite of stored findings.

8. **Rollout safety.** Gate the new behavior behind a default-safe flag (e.g. `AUDITWATCH_L3_READINESS=1`) so P210 can
   land dark; document the override (`l3_status=HUMAN_OVERRIDE` + reason) and an emergency disable.

**Out of scope for P210 too:** any change to `min_confirm_gate`/`confirm_gate` logic, deep-trace, routing, or
auto-submit. Human review stays mandatory for every High package.
