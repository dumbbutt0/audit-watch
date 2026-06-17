# P211 — submission readiness results (flag on, real functions)

Six cases via `evaluate()` / `l3_evaluate()` / `record_review()` (the write path exercised with `_unified_keys`
monkeypatched to admit rehearsal ids — proving the append-only write flips no canonical flags).

| case | path | result |
|---|---|---|
| High candidate, no L3 record (DEC-STATIC) | evaluate | **blocked** `blocked_by_missing_l3_poc` (fail-closed) |
| High candidate, L3 PASS (DEC-H-01) | record_review ready | **saved=ready_for_submission_package**, `routing_allowed=false`, `submission_ready` NEVER set; other human checks still apply |
| High candidate, L3 FAIL (DEC-M-03) | record_review ready | **saved=False, blocked=True**, `routing_allowed=false`, no `submission_ready` in row |
| Medium candidate, no L3 (DEC-M-03 @Medium) | evaluate | **unaffected** (eligible, no L3 blocker) |
| Malformed L3 on High (`{l3_status:GARBAGE}`) | l3_evaluate | **fail-closed** (high_promotion_allowed=false) |
| Human override + reason | l3_evaluate | **allowed**, override reason visible, no auto-submit |
| Human override, no reason | l3_evaluate | **blocked** |

**Invariant confirmed:** every `record_review` result carries `routing_allowed:false` and never `submission_ready:true`
(the overlay's "never set true" guarantee holds with the gate enabled). Rehearsal rows were removed from the shared
research ledger afterwards (left as-was).
