# P129 — Decision

## Terminal state: **MEASUREMENT LOOP CLOSED (partial, directional)**

The ground-truth loop went from **0 records → 15 platform-confirmed records**, and `compute_metrics.py`
transitioned its headline rates from `unmeasured` to measured numbers — without modifying detectors,
routing, or gates, and without inventing any outcome.

## What was measured (and trust level)
- **Discovery recall (beanstalk, full pipeline):** 42.0% useful / 53.1% any-touch / 18.5% exact — *directional* (1 audit).
- **False-positive rate:** 0.143 (2/14) — *directional*, reliable labels, small n.
- **Promotion precision / valid-finding:** 0.80; **duplicate** 0.067; **over-severity** 0.267 — *directional*.
- **Lead-recall (decent/noya, earlier funnel):** 100% / 94.7% — *upper bound*, not confirmed-finding recall.
- **PoC success:** 0.857 (n=14) — carried, unchanged.

## What stays unmeasured (marked partial, not guessed)
Discovery recall on the 4 holdout denominators (77 issues, `PENDING_RUN`); robust severity accuracy;
duplicate-risk vs live platform state; gate precision.

## Biggest measured weakness
**Recall, bottlenecked at coverage/source-resolution.** 38/81 misses with `correct_contract = "no"` on
every one — bugs are lost because candidates never reach the right contract, not because reasoning is
shallow. (Secondary: a concentrated FP tax in `arithmetic` + `economic_attack` from speculative reachability.)

## Best next optimization
Recall via candidate-stage coverage/source-resolution — see `recommendations.md`. Precision is a cheap,
targeted second fix on two specialists.

## Honesty / integrity self-check
- Outcomes **transcribed** from committed verdicts (`platform_confirmed`/`contest_result`); ambiguous
  ADJACENT findings **routed to `needs_human_review.jsonl`**, never guessed. ✓
- Single writer (`ingest_ground_truth.write_outcome`) used for every ground-truth write. ✓
- No detector/config/routing/gate file modified; `rank_signal_probe --self-test` PASS + deterministic;
  the only touched control file is the active-audit pointer, **restored to quantamm-2024-12-eval**. ✓
- `compute_metrics.recall_on_valid 1.0` explicitly flagged as a precision-side artifact, **not** discovery
  recall; severity accuracy flagged **indicative**. ✓

## Is the repo closer to Tier 4 (competitive bounty assistant)?
**Marginally, and honestly.** It now *measures* FP rate and (single-audit) recall instead of reporting
"unmeasured" — a real prerequisite for Tier 4. But with **n=15 outcomes on 1 fully-measured audit**, the
numbers are *directional, not robust*, and recall (42%) is well short of competitive. **No Tier-4 claim.**
The honest status: the measurement loop is now closed enough to *drive* tuning; reaching Tier 4 requires
running the keyed holdouts and acting on the coverage bottleneck.
