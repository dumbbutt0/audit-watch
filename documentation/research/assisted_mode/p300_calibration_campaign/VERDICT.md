# P300 — VERDICT

## A — CALIBRATION_CAMPAIGN_TIGHTENS_PRECISION_AND_RANGE_REAL_HUNT_GO

The campaign ran across 3 answer-keyed targets + beanstalk, held confirmed-FP = 0 corpus-wide, confirmed awarded loci
across multiple targets and bug classes, defined the real-hunt GO bands, and staged precision proposals.

### A-criteria — all met
- **Cross-target scorecard**: recall (silo 0.50 / revert-lend 0.03 / panoptic 0.0 / beanstalk 0.42) + novelty (mostly
  known classes) + executed-PoC validity.
- **confirmed-FP = 0 corpus-wide**; submission filter **0 leaks**.
- **Range**: confirmations on **3 targets** (silo, panoptic, beanstalk) across **exploit AND logic** bug classes;
  +3 new loci this campaign (silo M-05/M-06, panoptic M-01) → 23 cumulative executed-confirmed.
- **Honesty/FP guard**: revert-lend H-03 REFUTED by execution (per-token approval gates it) → needs_human, not
  confirmed.
- **GO bands defined** (REAL_HUNT_READINESS.md) + **rejection-rule proposals staged** (not promoted; human-only loop).
- Answer keys + ground_truth + promoted rules + contest source unchanged; verifier + forbidden 5 byte-identical.

### What this buys for a real hunt
Precision is GUARANTEED by the submission filter (submit iff executed-confirmed → FP≈0 by proof), validated across a
spread of targets. Range was widened by the logic-differential mode (now confirming reward/rounding/correctness bugs,
not just exploits). The project is **GO for a real hunt under the human-in-the-loop submission filter**.

### Next
Human-promote the staged proposals; (optional) one fresh blind dry-run under the filter; then hunt — surface wide,
confirm by executed PoC, submit only confirmed, route the rest to human review.
