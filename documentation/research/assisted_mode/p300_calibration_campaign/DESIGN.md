# P300 — DESIGN

## Goal
Calibrate the stack against several locally answer-keyed targets to (1) measure recall + recall-of-confirmed +
novelty, (2) tighten precision via the executed-PoC SUBMISSION FILTER (confirmed-FP=0 by proof), (3) define real-hunt
GO/NO-GO bands. Targets: silo / revert-lend / panoptic (+ beanstalk reuse).

## Constraint that shaped the precision approach
The precision-tuning loop is HUMAN-ONLY (ground_truth.jsonl / record_outcome.py / promote_learning.py — AI must not
write them). So precision tightening = (a) the executed-PoC submission filter (FP=0 by proof, deliverable end-to-end)
+ (b) FP rejection-rule proposals STAGED to data/learning/_proposed/ for human promotion (never auto-promoted).

## Components (new files only; reuse P294 verifier + P299 logic mode; verifier byte-identical)
- `eval_campaign.py` — per target: recall (read-only match_matrix) + novelty (KB chroma) + executed-PoC validity
  (verifier over pocs/p300/<slug>__<id>/, exploit OR logic_differential) -> per-target + aggregate scorecard.
- `submission_filter.py` — `submit` iff `validity_confirmed` (executed exploit OR logic confirmation), else
  `needs_human`. Defense-in-depth: also requires a real confirmed STATUS (a fabricated validity flag without a real
  pass -> needs_human). Labels only; never submits; un-wired from confirm gates.
- Validity batch: spawned `general-purpose` builders for the matched/surfaced awarded loci (Tier-C; logic_differential
  where the bug is a value/correctness divergence; exploit where there is an attacker). Verifier = sole judge.

## Real-hunt GO bands (defined in REAL_HUNT_READINESS.md)
- HARD: confirmed-FP = 0 (submission filter holds; 0 filter leaks).
- Range: ≥2 targets with an executed confirmation across bug classes (exploit + logic).
- Novelty: high/critical-novel (KB sim < 0.4) routed to human review, never auto-submitted.
- Submission policy: submit iff executed-confirmed; everything else -> human review.
