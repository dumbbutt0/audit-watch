# P211 — flag-ON rehearsal (AUDITWATCH_L3_READINESS=1, in-process only)

| candidate | target | eligible | l3_blocker | dashboard l3 | read-only |
|---|---|---|---|---|---|
| DEC-H-01 (L3 PASS) | High | **True** | none (cleared) | present | yes |
| DEC-M-03 (L3 FAIL) | High | **False** | `blocked_by_missing_l3_poc` | present | yes |
| DEC-M-03 (L3 FAIL) | Medium | True | none (L3 not applicable) | present | yes |
| DEC-STATIC (no record) | High | **False** | `blocked_by_missing_l3_poc` (fail-closed) | present | yes |

**Result:** High+PASS clears; High-without-L3 (FAIL or missing) blocked; Medium unaffected; dashboard panel present
and read-only. No route/submit side effects (the driver only reads + computes; `record_review` writes are append-only
research rows that never set `submission_ready`/`routing_allowed` — see SUBMISSION_READINESS_RESULTS.md).

Full machine output: `rehearse_output.json`.
