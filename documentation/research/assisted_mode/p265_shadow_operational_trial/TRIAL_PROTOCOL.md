# P265 — TRIAL_PROTOCOL

Measurement-only. The harness performs candidate *discovery* (recall); it does NOT run B/C ranking or the five
completion operations (those are downstream/manual) — so completion_status/refutation_status are `null` by design.

## Steps executed
1. **Freeze check.** `sha256sum` on harness/P260/P262 modules + configs + schema + the 5 forbidden files; confirm
   they match the recorded baselines (SETUP.md). Confirm `output` symlink still → `audits/size-credit-2024-06-blind`.
2. **Shadow runs (×13).** For each contest:
   `recall_first_harness.py --manifest <frozen> --accounting <frozen> --state-transition <frozen>
   --out-dir outputs/<contest> --mode shadow --quiet`.
   Each emits `recall_advisory_candidates.json(+.md)`, `recall_metrics.json`, `recall_guard_report.json`.
   Confirm rc=0 and `recall_guard_report.json.result == PASS` (0 violations) per contest.
3. **Aggregate (analysis-only).** `p265_aggregate.py` reads the 13 frozen outputs and computes the 8 metrics
   per-contest + pooled into `outputs/p265_aggregate_metrics.json`. It reads only already-emitted advisory outputs;
   it generates nothing, uses no answer key, and sets no severity/routing.
4. **Recall-delta (#8).** Narrow baseline = P260 rank 0–4 (`prioritizer_score < 5`); recall-delta = rank ≥5 OR
   rank `null` (forced into the sweep by a recall-first clause beyond the narrow top-5). Deterministic from outputs.
5. **Scored layer (#3/#4/#5).** Computed only where awards are known, from the P254–263 reveal records, flagged
   retrospective/contaminated — **benddao reported separately as the clean anchor** (P263 REVEAL_AND_SCORE).
6. **Operator layer (#2/#7).** Transparent triage *proxy* (rubric in OPERATOR_USEFULNESS.md), applied
   deterministically in the aggregator so it is reproducible; explicitly not a human time-and-motion study.
7. **Decision.** Map the metrics onto the operator's decision tree → one decision + one trial verdict (VERDICT.md).

## Invariants asserted by the run + guard test
- Every advisory candidate: `severity=null`, `reportable=submission_ready=concluded=emits_finding=
  production_routing=False`, `status=ADVISORY_RECALL_CANDIDATE`.
- Every contest: guard `result=PASS`, `guard_violations=0`, bounded output (≤ caps), and
  `version_hashes` equal to the frozen baseline.
- `frozen_inputs_identical_across_runs=true` in the aggregate (no tuning between runs).
