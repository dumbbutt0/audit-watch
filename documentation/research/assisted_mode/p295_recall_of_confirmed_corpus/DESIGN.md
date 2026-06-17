# P295 — DESIGN

## The funnel
Per subset audit: **awarded → surfaced (recall ceiling) → confirmed-by-execution**. Awarded set + per-locus
surfacing come from existing read-only artifacts; confirmation is overlaid by the P294 executed-PoC verifier
(`verify_poc`) over each awarded locus's mapped `pocs/<id>` dir. A locus is **confirmed only by a real exploit-test
forge PASS (L1+L2+L3)** → confirmed-FP = 0 by construction.

## Surfacing source (read-only)
- kelp/ecg/salty: `reveal_score.json` `awarded_findings`/`awarded_findings_scored`/`awarded_highs` — each row carries
  `locus` + `surfaced` (+ `match_level`). `surfaced` = truthy or a descriptive non-miss string.
- beanstalk: `ground_truth.jsonl` accepted entries are SYSTEM findings confirmed to match an awarded bug
  (`recorded_by: contest_result`, `evidence_class: platform_confirmed`) → surfaced by definition; finding-level
  (prose title, no clean contract.fn); confirmed requires a PoC (none yet → PoC backlog).
- blackhole: no reveal artifact → `denominator: partial_local`, awarded loci listed inline for the two we have
  evidence for (claim_many, L2Governor) — counted as additional confirmed, not in the full-local recall denominator.

## Metrics
- **recall_of_surfaced** = surfaced / awarded (the ceiling).
- **recall_of_confirmed** = confirmed / awarded (the metric we drive to 100%).
- **confirmation_yield_on_surfaced** = confirmed / surfaced (how much of the ceiling is proven).
- **confirmed_false_positive_count** = refutation controls that confirmed (must be 0).
- aggregate over `full_local` denominators only; `partial_local` (blackhole) reported separately.

## Backlog = the climb worklist
- **surfaced_unconfirmed_poc_worklist** — surfaced awarded loci with no passing PoC (the verification-agent loop's queue).
- **missed_surfacing_worklist** — awarded loci not surfaced (the surfacing-improvement queue).

## Authority
Read-only of answer keys; advisory-stamped; no severity/submission; un-wired from confirm_gate/min_confirm_gate.
