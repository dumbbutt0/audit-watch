# P211 — flag-OFF baseline (AUDITWATCH_L3_READINESS unset)

Driver: `rehearse.py` (calls the real `submission_readiness_review.evaluate()` + the dashboard L3 path).

| candidate | target | eligible | l3_blocker | dashboard l3 |
|---|---|---|---|---|
| DEC-H-01 | High | True | none | absent |
| DEC-M-03 | High | True | none | absent |
| DEC-M-03 | Medium | True | none | absent |
| DEC-STATIC | High | True | none | absent |

**Result:** no `l3` fields, no `blocked_by_missing_l3_poc`, no dashboard `l3` panel — output-equivalent to pre-P210.
(Existing `tests/research/test_submission_readiness.py` also stays 14/14 from P210.)
