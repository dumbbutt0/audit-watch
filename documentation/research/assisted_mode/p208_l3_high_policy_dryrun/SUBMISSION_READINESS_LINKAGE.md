# P208 — submission-readiness linkage (documented, NOT wired)

This maps the L3 policy onto the **existing** research-only readiness overlay `scripts/submission_readiness_review.py`
(which already never flips `submission_ready`/`routing_allowed` and uses `READINESS_STATES` incl.
`blocked_by_missing_poc`, `blocked_by_missing_impact`). No code in that module is changed by P208; this is the
intended hand-off contract only.

## Rules
| candidate state | L3 requirement | submission packaging |
|---|---|---|
| **HIGH** report package | `l3_status ∈ {PASS, HUMAN_OVERRIDE}` AND `high_promotion_allowed==true` | may prepare a **draft** package; **human review mandatory** before any submission. If not satisfied → `blocked_by_missing_poc` (or `blocked_by_missing_impact`). |
| **MEDIUM** report package | L3 PoC NOT required | may proceed if mechanism + impact are source-proven (existing checklist); L3 is optional supporting evidence. |
| **NEEDS_HARNESS_FOR_SEVERITY** | — | **cannot** be marked submission-ready *as High*; route to harness authoring or human review; may still be a valid Medium. |
| **calibrated invalid / source-refuted** | — | not submission-ready at any severity. |

## Mapping to existing `READINESS_STATES`
- `high_promotion_allowed==true` → eligible for `ready_for_submission_package` (HIGH), **pending human review**.
- blocker mentions l3_status / missing PoC / missing control → `blocked_by_missing_poc`.
- blocker mentions missing material delta/impact → `blocked_by_missing_impact`.
- calibrated_severity below report threshold → `blocked_by_severity_too_low`.

## Non-submission guarantee (unchanged)
- The L3 validator computes advisory fields only; it never sets `submission_ready` / `routing_allowed`, never
  promotes/demotes a canonical finding, never submits.
- Even a fully L3-satisfied HIGH requires the existing human readiness decision in `submission_readiness_review.py`.
- The two display labels remain distinct (per that module): an advisory "L3 satisfied / ready_for_submission_package"
  is NOT the machine-owned `submission_ready=true`.
