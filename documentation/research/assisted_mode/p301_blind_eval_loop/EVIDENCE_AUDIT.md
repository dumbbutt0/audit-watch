# P301 — EVIDENCE_AUDIT

## Recall-gap mining (the missed awarded findings)
- The match_matrix MISS/ADJACENT/PARTIAL rows are, by the prior eval's own scoring, the awarded findings the pipeline
  missed or only partially caught. The loop extracts them verbatim (read-only): revert-lend 31 (27 MISS + 4 under),
  panoptic 22 (19 MISS + 3 ADJ), silo 5 (1 MISS + 4 under) = 58 staged. No re-derivation, no answer-key write.

## Recoveries (executed-PoC; gates tight)
- **panoptic M-01** (under-recalled, ADJACENT) → recovered via the P300 logic_differential PoC (getLiquidationBonus
  opposite-direction rounding); verifier confirmed_by_logic_differential; submission filter `submit`; FP=0.
- **silo M-06** (under-recalled, PARTIAL) → recovered via the P300 logic_differential PoC (_accruedFeeShares Floor
  rounding); verifier confirmed; `submit`; FP=0.
- All other gap loci → needs_execution (PoCs to build over subsequent iterations). No recovery is counted without a
  real executed pass (verifier = sole judge).

## Gate-tightness + authority
- confirmed-FP = 0; submission filter 0 leaks; nothing auto-submitted.
- The 58 recall-gap items + recoveries are STAGED to `data/learning/_proposed/recall_gap_backlog.jsonl`
  (promoted=false). ground_truth.jsonl + rejection_rules.jsonl byte-identical (read-only honored). The loop never
  opens ground_truth / promoted rules for writing (the 3 mentions are docstring/notes). Contest source untouched
  (recovery PoCs under pocs/p301/ copy control-flow into mocks). Verifier (1a005811) + forbidden 5 byte-identical;
  symlink unchanged; un-wired from confirm gates.

## Resumability
loop_state.json holds per-target status (pending→scored→recovered→needs_key_ingestion); re-running `/loop` continues
from the next pending target.
