# P129 — Ground-Truth Measurement Plan

## Problem
`compute_metrics.py` reported **42 audits, 0 ground-truth records → FP rate unmeasured, recall
unmeasured** (only PoC success measured: 0.857, n=14). The measurement loop was built but starved.
This phase populates it with **evidence-traceable, platform-confirmed** outcomes so the existing metric
scripts produce real numbers — without touching detectors, routing, or gates, and without inventing any
outcome.

## What the repo already had (read-only inspection)
- `scripts/compute_metrics.py` — cross-audit aggregator. Keys FP/recall off `finding_id` appearing in
  `audits/<id>/data/triage/{submit,poc_required}.jsonl` (accepted). Reports `unmeasured` when n=0.
- `scripts/ingest_ground_truth.py` — **the single write path**; provenance-gated (`evidence_class`,
  `source_file`, `evidence_summary`); routes missing-provenance records to `needs_human_review.jsonl`.
  `write_outcome(record, eval_dir=…)` can target a specific audit without switching the active one.
- `scripts/evaluate_pipeline_accuracy.py` — single-audit precision/recall/FP/severity vs ground truth.
- `scripts/score_eval_rerun.py` — beanstalk-wired semantic judge scorer.
- Pre-built closed loops: `evals/beanstalk_finale/` (match_matrix + scorecard) and
  `documentation/research/_p81b/{decent,noya}/` (awarded_map + recall_score).

## Decisive structural constraints (and how they shaped the plan)
1. **No `ground_truth.jsonl` existed anywhere.** `metrics.json` existed but read unmeasured.
2. **Ground truth and pipeline output are disjoint.** The 9 `-holdout` audits hold sealed answer keys
   but no `merged_findings.json`; the eval/strict-eval dirs hold pipeline output but no local key. ⇒ no
   audit has both → end-to-end recall on a holdout would require a pipeline RUN (out of scope here).
3. **beanstalk's `data/triage/` was empty** — the eval ran via the independent path (producing
   match_matrix + merged_findings), not the triage buckets `compute_metrics` keys on.
4. **Two measurement directions are not interchangeable:**
   - *Discovery recall* (denominator = awarded issues; "of known bugs, how many surfaced?") — the
     many-to-one candidate↔public-finding mapping means **`compute_metrics.recall_on_valid` cannot
     represent it**. Authoritative source = the match-matrix/scorecard.
   - *Precision / FP / severity* (denominator = our promoted findings) — this is what `compute_metrics`
     + `evaluate_pipeline_accuracy` measure well once ground truth + pipeline decisions exist.

## Approach executed (scope: "closable-now + denominators")
- **A — Recall** on the 3 pre-classified audits from committed artifacts (no pipeline run): beanstalk
  (full-pipeline match), decent + noya (earlier-funnel *lead*-recall).
- **B — Precision/FP/severity**: ingest 15 committed beanstalk verdicts via the sanctioned writer
  (`evidence_class=platform_confirmed`, `recorded_by=contest_result`, `source_file=match_matrix.json`),
  and **faithfully reconstruct** beanstalk's triage decisions from `merged_findings.json` (the pipeline's
  actual promoted set) so decisions resolve instead of emitting a misleading 0.0.
- **C — Run** `compute_metrics.py` + `evaluate_pipeline_accuracy.py`, capturing output verbatim.
- **D — Denominators**: transcribe awarded-issue inventories from 4 diverse holdout answer keys
  (recall = `PENDING_RUN`, no pipeline output to match).
- **E — Scorecard / failure modes / recommendation / decision**.

## Honesty guardrails honored (CLAUDE.md non-negotiables)
- Outcomes are **transcribed** from committed verdicts, never invented. Ambiguous (ADJACENT near-miss)
  findings were **routed to `needs_human_review.jsonl`**, not guessed.
- The single writer (`ingest_ground_truth.write_outcome`) was used for every ground-truth write.
- No detector / config / routing / gate file modified; research self-test (`rank_signal_probe
  --self-test`) PASS + deterministic. Only data/metrics artifacts and this report dir were written; the
  active-audit pointer was switched to beanstalk for the per-audit run and **restored to quantamm**.
