# P129 — Recommendations (tied to measured failure modes)

## Next optimization target: **RECALL — specifically coverage / source-resolution**
Not intuition — this is what the data says:
- **38/81 misses, and `correct_contract = "no"` on every one of them.** The single largest, cleanest
  signal: the pipeline loses bugs because candidates never reach the right contract, not because its
  reasoning is shallow. "wrong contract inspected" (12) + "architecture mapping failure" (2) are the
  modal explicit reasons.
- Useful recall is **42.0%** (and regressed −13.6 pp vs the prior baseline on this contest) — far more
  headroom than precision.
- FP rate (0.143) misses its <0.10 target but the absolute cost is 2 findings; recall leaves ~47 awarded
  issues on the table. **Recall dominates the expected-value gap.**

### Why not precision first
Precision is already near-acceptable (valid-finding 0.80; FP 0.143 from just 2 findings) and is
**concentrated**: `arithmetic 0/2` + `economic_attack 0.5`, cause = "speculative reachability." That's a
cheap, targeted second fix (tighten the reachability bar on those two specialists), not the headline.

### Why not severity / duplicate / PoC first
- Severity error is real (over 0.267, plus bidirectional under-rating) but **indicative only** here
  (inferred public severity); fix the *measurement* before tuning calibration.
- Duplicate-risk and PoC reproduction are **unmeasured** locally — can't optimize what isn't measured yet.

## Concrete next steps (ranked)
1. **Run the pipeline on 1–2 sealed holdouts** (e.g. munchables, predy) to expand measured recall beyond
   beanstalk and confirm the "wrong contract inspected" pattern generalizes. *Verify:* `compute_metrics`
   recall keyed via a per-public-finding match map (see #4). *Risk if skipped:* recall conclusions rest
   on a single audit.
2. **Coverage/source-resolution audit of the candidate stage** — instrument *which* in-scope contracts
   ever receive a candidate vs the awarded-bug contracts. *Verify:* contract-level recall (awarded
   contracts touched / total). *Risk if skipped:* the dominant miss cause stays invisible.
3. **Tighten reachability on `arithmetic` + `economic_attack`** (the measured FP sources). *Verify:*
   re-measure per-agent reliability after the change. *Risk if skipped:* small but persistent FP tax.
4. **Fix the measurement plumbing** (see below) so recall/severity become *robust*, not directional.

## Measurement-system fixes surfaced by P129 (do before trusting the rates)
- **`compute_metrics.recall_on_valid` cannot represent discovery recall** (many-to-one
  candidate↔public-finding; `ground_truth.jsonl` dedups by `finding_id`). Add a per-public-finding match
  table (like `match_matrix.json`) as the recall source of record; keep `recall_on_valid` labelled as a
  precision-side complement.
- **`evaluate_pipeline_accuracy.py --audit-id` is cosmetic** — `EVAL_DIR`/`TRIAGE_DIR` bind to the active
  audit at import, so the flag only relabels output. Make it actually retarget, or document that callers
  must `switch` first.
- **Severity is only as good as what the run persists.** beanstalk's per-finding severity and triage
  buckets weren't saved (triage was empty). Persist triage decisions + per-finding severity on every run
  so severity accuracy is measurable without reconstruction.
- **Close the ground-truth/output disjointness:** holdouts have keys but no run output; eval dirs have
  output but no local key. Either run the pipeline on keyed holdouts, or store answer keys alongside the
  eval dirs that already have output.
