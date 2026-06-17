# P300 — REAL_HUNT_READINESS (GO / NO-GO bands)

## Verdict: GO for a real hunt UNDER THE SUBMISSION FILTER (human-in-the-loop)

The executed-PoC submission filter is the precision guarantee for a real hunt: across silo / revert-lend / panoptic /
beanstalk it held **confirmed-FP = 0 with 0 filter leaks**. The policy below makes a real hunt safe regardless of the
discovery layer's noise.

## GO bands (must all hold to submit)
| band | threshold | status |
|---|---|---|
| confirmed-FP (HARD) | == 0 | **0** (4 targets) ✓ |
| submission-filter leaks (HARD) | == 0 | **0** ✓ |
| range: targets with an executed confirmation | ≥ 2 | **3** (silo, panoptic, beanstalk) ✓ |
| range: bug classes confirmed | exploit AND logic | both (AC-001/AC-003 exploit; silo/panoptic/beanstalk logic) ✓ |
| high/critical-novel handling | route to human | enforced (novelty axis) ✓ |

## The real-hunt operating policy
1. **Surface wide** (open recall) — discovery noise is fine; it does not reach submission.
2. **Confirm by executed PoC** — exploit (attacker L1+L2+L3) OR logic_differential (bug-vs-corrected-control + L3 +
   assertion_map). The verifier is the SOLE judge; builder/agent claims are advisory.
3. **Submit iff `validity_confirmed`** (the submission filter) → confirmed-FP ≈ 0 by proof. Everything else
   (setup_only / needs_execution / refuted / novel-unverified) → **human review**, never auto-submitted.
4. **Submission stays human-gated** — the filter LABELS; a human submits.

## NO-GO conditions
- any confirmed-FP, or the filter ever labels `submit` without a real executed confirmation (a leak);
- a high/critical-novel finding auto-submitted without human review;
- submitting an un-confirmed (setup_only/needs_execution) finding.

## Recall context (honest)
Recall-of-confirmed is bounded by surfacing + PoC-buildability, not by precision. Per target useful-recall: silo 0.50,
revert-lend 0.03, panoptic 0.0, beanstalk 0.42. The hunt's VALUE scales with how many surfaced loci we can confirm by
PoC; its SAFETY (FP≈0) is guaranteed by the filter independent of recall.

## Before the hunt
- Human-promote the staged rejection-rule proposals (promote_learning.py) to tighten the discovery layer.
- Optionally re-blind a fresh target end-to-end under this policy as a final dry run.
