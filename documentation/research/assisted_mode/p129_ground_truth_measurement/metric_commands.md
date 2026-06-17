# P129 — Metric Commands (run + result + meaning + reliability)

## 1. Ingest beanstalk verdicts (via the sanctioned single writer)
```
python3 documentation/research/assisted_mode/p129_ground_truth_measurement/ingest_beanstalk.py
```
**Result (PASS):** 15 → `ground_truth.jsonl`; 2 → `needs_human_review.jsonl`; reconstructed
`submit.jsonl` (14) + `merged.jsonl` (1).
**Meaning:** populates the calibration anchor for beanstalk from committed contest verdicts.
**Reliability:** high for outcomes (platform_confirmed); severities are *indicative* (public per-finding
severity inferred, see scorecard note).

## 2. Cross-audit metrics
```
python scripts/compute_metrics.py
```
**Result (PASS):**
```
Metrics — 42 audits, 15 ground-truth records
  FP rate:        0.143 (n=14)
  Recall:         1.0 (n=12)
  PoC success:    0.857 (n=14)
```
Full `metrics.json`: `false_positive_rate 0.143 (n=14, num=2)` · `recall_on_valid 1.0 (n=12)` ·
`valid_finding_rate 0.80 (12/15)` · `duplicate_rate 0.067 (1/15)` · `severity_downgrade_rate 0.267 (4/15)` ·
`poc_success_rate 0.857 (n=14)`.
**Meaning:** transitioned FP rate + valid-finding + duplicate + over-severity from *unmeasured* → measured.
**Reliability:**
- FP rate (0.143) — **reliable** (committed FP labels), small n=14 ⇒ directional.
- `recall_on_valid 1.0` — **NOT discovery recall**; structural artifact (only valid findings we *also*
  ingested are present; the 38 misses cannot be keyed 1:1). Use the scorecard recall instead (see scorecard.md).
- `severity_downgrade_rate 0.267` — **reliable as an over-severity signal** (claimed-vs-truth within the
  record; independent of triage); 4/15 promoted findings were over-rated by the pipeline.

## 3. Per-audit accuracy (beanstalk) — required switching the active audit
The `--audit-id` flag on `evaluate_pipeline_accuracy.py` is **cosmetic**: `EVAL_DIR`/`TRIAGE_DIR` resolve
against the *active* audit at import, so the flag only relabels output (a tool finding). The faithful run:
```
python scripts/audit_manager.py switch beanstalk-2024-05
python scripts/evaluate_pipeline_accuracy.py
python scripts/audit_manager.py switch quantamm-2024-12-eval   # restore
```
**Result (PASS):**
```
Ground truth entries: 15  (evaluated: 15, missing from pipeline: 0)
  Outcome accuracy      0.867   (> 0.80)  ✅
  Severity accuracy     0.333   (> 0.70)  ❌  (indicative)
  False positive rate   0.143   (< 0.10)  ❌
  Gate precision        n/a     (> 0.90)
  True positives: 12   False positives: 2   False negatives: 0
```
**Meaning:** outcome classification beats target; FP rate and severity miss target.
**Reliability:** outcome accuracy + FP reliable (small n); severity *indicative* (inferred public
severity + reconstructed triage); FN=0 reflects that discovery misses aren't represented here (see recall caveat).

## 4. Integrity (no code/routing change)
```
python scripts/assisted/rank_signal_probe.py --self-test   # SELF-TEST: OK + deterministic
find scripts config agents prompts schemas -type f -mmin -30   # only config/active_audit.json (pointer, restored)
```
**Reliability:** research scripts byte-identical (self-test PASS); the only touched control file is the
active-audit pointer, restored to `quantamm-2024-12-eval`.

## Not run (and why)
- `score_eval_rerun.py` — writes `output/eval_ready/*` into the **active** audit's workspace; running it
  would deposit beanstalk-derived artifacts into quantamm's output. Its committed `scorecard.json` already
  provides the numbers; recomputed independently here and they match (15/19/9/38 → 42.0% / 53.1%).
