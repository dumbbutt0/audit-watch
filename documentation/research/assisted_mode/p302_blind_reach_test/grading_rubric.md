# Capability-Drive Grading Rubric — graded partial-credit (no zero-progress)

Reuses the canonical tiers from `scripts/research/blind_reach_test.py` (LEVELS) + capability-drive `DEFERRED_LEAD`.
Every iteration outcome is GRADED; every non-STRONG tier MANDATES a durable artifact (the "progress from the slight miss").
Graded credit NEVER comes from relaxing/fabricating a match — DEFERRED_LEAD is the honest home for "couldn't confirm."

| Tier | credit | MANDATORY durable artifact |
|---|---|---|
| STRONG_MECHANISM_MATCH | 1.0 | new prompt class only if novel |
| SAME_AREA_WRONG_MECHANISM | 0.5 | mechanism-fidelity note (claimed-vs-true delta) at the right agents/*.md locus |
| SUBSYSTEM_ONLY_RECALL | 0.25 | navigation hint (exact function/sub-path to open next) |
| DEFERRED_LEAD | 0.1 | resume-here pointer (files/functions + open question) |
| MISSED (file read) | 0.0 | reasoning-gap class |
| MISSED (file unread) | 0.0 | coverage-gap note (name the unread file) |
| FP / self-caught FP | n/a (precision) | FP autopsy + rejection rule + prompt guard |

## Scoring
- `iteration_progress` = Σ over findings of (this iteration's tier credit − that finding's PRIOR banked credit). Conversions (DEFERRED→STRONG, SAME_AREA→STRONG) credit only the DELTA, so a finding's lifetime contribution caps at 1.0 (no double-count).
- `progress_score` (cumulative) = running Σ of `iteration_progress`. Distinct from raw STRONG/TP count — it makes partial progress visible.

## Plateau (redefined)
STOP only when 3 consecutive iterations have `iteration_progress == 0` (no STRONG, no partial-credit artifact/conversion, no new FP rule). ANY graded partial progress holds/resets the counter → a slight miss never counts toward plateau.

## Invariant
Every non-empty iteration MUST emit ≥1 durable artifact and record `iteration_progress > 0`, OR explicitly justify a true zero (which advances the plateau counter).
