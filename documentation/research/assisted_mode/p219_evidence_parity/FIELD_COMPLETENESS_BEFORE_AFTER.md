# P219 — FIELD COMPLETENESS BEFORE / AFTER

The spec warns against cosmetic completeness — the real win is artifact-backed DEPTH.

## A. 21-field evidence aggregate (legacy P217 scorer)
P217: 90% (226/252) -> P219: **90% (226/252)** — unchanged; those 21 fields were already populated. P219 adds depth
on dimensions this scorer does not track.

## B. H5-parity DEPTH (8 dims: reachability, PoC actual/expected/control/value-delta, who_loses, asset, loss_type)
P217: **0/96 (0%)** (not emitted) -> P219: **48/96 (50%)**, all artifact-backed. ZETA-07 (executed) = **8/8**;
NEEDS_HARNESS / no-L3 candidates lower by design (explicit unknowns).

## Per-candidate (21-field % | depth /8 | unknown | MISSING_EVIDENCE)
| record | 21-field | depth | unknown | MISSING_EVIDENCE |
|--------|----------|-------|---------|------------------|
| ZETA-01 | 90% | 5/8 | 2 | 0 |
| ZETA-02 | 86% | 2/8 | 3 | 0 |
| ZETA-03 | 95% | 5/8 | 1 | 0 |
| ZETA-04 | 95% | 3/8 | 1 | 0 |
| ZETA-05 | 90% | 3/8 | 2 | 0 |
| ZETA-06 | 90% | 3/8 | 2 | 0 |
| ZETA-07 | 90% | 8/8 | 2 | 0 |
| ZETA-08 | 90% | 5/8 | 2 | 0 |
| ZETA-09 | 81% | 2/8 | 4 | 0 |
| ZETA-10 | 90% | 5/8 | 2 | 0 |
| ZETA-11 | 95% | 5/8 | 1 | 0 |
| ZETA-12 | 81% | 2/8 | 4 | 0 |

## Counts
- Artifact-backed: every populated evidence field carries a _field_provenance entry (path + blind_evidence:true).
- Human-judgment-only / not populated (no artifact): novelty_duplicate (all 12); who_gains (all 12 — no beneficiary
  named in any artifact); executed-PoC actual/value-delta for NEEDS_HARNESS candidates lacking an L3 actual.
- MISSING_EVIDENCE count: 0 (executed-PoC absences render as an explicit "unknown" slot).
- HARD RULE: no field is populated without a specific artifact path.
