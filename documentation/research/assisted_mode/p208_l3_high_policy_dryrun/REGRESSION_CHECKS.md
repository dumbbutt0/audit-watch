# P208 — regression checks

All blocked from HIGH as required (advisory only). `regression/*.json`.

| case | input | calibrated | high_allowed | expected | match |
|---|---|---|---|---|---|
| static HIGH_THREAD, no PoC | l3=NOT_ATTEMPTED, tier=L1_STATIC_TRACE, no magnitude | needs_harness_for_severity | false | block | ✅ |
| DoS/griefing Medium | impact=dos, recoverable, no L3 permanent-loss | medium | false | block | ✅ |
| precision/rounding, no magnitude | impact=precision, magnitude_basis empty | needs_harness_for_severity | false | block | ✅ |
| source-refuted | l3=FAIL, notes="source refutes…guard present" | invalid | false | block | ✅ |
| decent-06 swapNoPath (false High) | l3=FAIL, no valuable residual to drain | medium | false | block | ✅ |
| decent-12 double-withdrawal | l3=NEEDS_HARNESS, no source-valid path | needs_harness_for_severity | false | block | ✅ |

**6/6 regression rows blocked correctly.** Key guarantees demonstrated:
- A static HIGH_THREAD with only an L1 trace **cannot** become reportable High (capability ≠ realized impact).
- DoS/griefing stays Medium unless an L3 PoC proves permanent material loss/insolvency.
- Unproven magnitude → `NEEDS_HARNESS_FOR_SEVERITY`, never auto-High.
- Source-refuted → `invalid`, blocked.
- 0 false-allows across the full set.
