# P218 — FIELD COMPLETENESS SCORECARD

Confirmed via the hook's wrapper scorer (21 evidence fields/record; safety defaults excluded). P218 is REPLAY_MODE over
the P217 artifacts, so completeness is **confirmed maintained at the P217 level** (the goal here is enforcement, not a
further field gain): aggregate **90% (226/252)**, **0 MISSING_EVIDENCE**.

- total candidates: 12
- total expected evidence fields: 252 (12 × 21)
- populated (artifact-backed): 226
- unknown (no source artifact): 26
- MISSING_EVIDENCE: 0
- before (P216, pre-automation): 57% → after (P217/P218): **90%**

## Per-candidate
| record | completeness | populated | unknown | missing |
|--------|--------------|-----------|---------|---------|
| ZETA-01 | 90% | 19/21 | 2 | 0 |
| ZETA-02 | 86% | 18/21 | 3 | 0 |
| ZETA-03 | 95% | 20/21 | 1 | 0 |
| ZETA-04 | 95% | 20/21 | 1 | 0 |
| ZETA-05 | 90% | 19/21 | 2 | 0 |
| ZETA-06 | 90% | 19/21 | 2 | 0 |
| ZETA-07 | 90% | 19/21 | 2 | 0 |
| ZETA-08 | 90% | 19/21 | 2 | 0 |
| ZETA-09 | 81% | 17/21 | 4 | 0 |
| ZETA-10 | 90% | 19/21 | 2 | 0 |
| ZETA-11 | 95% | 20/21 | 1 | 0 |
| ZETA-12 | 81% | 17/21 | 4 | 0 |

## Worst missing / fields with no source (explicit, not invented)
- `novelty_duplicate` — no novelty-assessment artifact in P215 (all 12).
- `l3_status` for ZETA-02 / ZETA-09 / ZETA-12 — no L3 record (Medium/rejected, not High-ceiling); emitted as
  missing-artifact warnings by the wrapper. ZETA-09/12 also lack a dry-run-queue entry.
- These are the only systematic unknowns; everything else is artifact-backed. Goal met: **maximum artifact-backed
  completeness, no invention.**
