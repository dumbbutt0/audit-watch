# P215 — SUBMISSION READINESS RESULTS (real submission_readiness_review.evaluate, flag on)

Human (rehearsal reviewer) answered the 13-question checklist honestly per candidate; `evaluate()` is the real gate.
Threat ceiling is kept separate from calibrated severity. No `record_review` rows were written (pure `evaluate()` only),
so the shared `submission_readiness.jsonl` ledger is untouched.

| ID | ceiling | calibrated | reviewer sev | poc_complete | ready_for_submission_package | blocking checks |
|----|---------|-----------|--------------|--------------|------------------------------|-----------------|
| ZETA-07 | Medium | Medium/Low | Low | **yes (executed)** | **True** | — |
| ZETA-04 | High | needs_harness→Medium | Medium | no | False | q4 PoC evidence complete |
| ZETA-12 | Medium | Medium | Medium | no | False | q4 PoC evidence complete |
| ZETA-10 | High | needs_harness | High | no | False | q4 PoC + **blocked_by_missing_l3_poc** |
| ZETA-03 | Critical | medium | High | no | False | q4 PoC + **blocked_by_missing_l3_poc** (attacker=privileged, no control) |
| ZETA-01/05/06/11 | High | needs_harness | (High/Med) | no | False | q4 PoC + blocked_by_missing_l3_poc |
| ZETA-08 | High | medium | (Low) | no | False | q4 PoC + blocked_by_missing_l3_poc |

## What this shows
- **Exactly one candidate reached `ready_for_submission_package`: ZETA-07** — the one with an *executed* harness. It is
  a Low/Medium (privileged precondition), so the system surfaced a fully-ready item that is **not** an inflated High.
- **Every High/Critical was blocked** by `blocked_by_missing_l3_poc` (L3) and by q4 (no PoC). The over-rating guard and
  the PoC requirement are independently enforced.
- **Source-only Mediums (ZETA-04, ZETA-12)** are human-reviewable but **not yet submission-ready** — the checklist
  demands PoC evidence (q4). Honest: a source-read is not a PoC.
- `submission_ready` / `routing_allowed` were **never** flipped; all overlay output is advisory (`research_only:true`).
