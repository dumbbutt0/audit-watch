# P300 — LIMITATIONS

- **Precision-loop is human-only.** AI can't write ground_truth / promote learning, so the discovery-layer FP
  tightening is STAGED (proposals in _proposed/), not applied. The delivered precision is the executed-PoC submission
  filter (FP=0 by proof), which is independent of discovery noise.
- **Thin discovery-FP signal locally.** The strict-eval match_matrices recorded `false_positives: []`, so there was
  little pipeline-only FP to autopsy; the staged proposals come mainly from the H-03 refutation, not a broad FP sweep.
- **Validity is a tractable batch** (the matched/surfaced loci), not every awarded locus. Recall-of-confirmed is a
  floor, not a ceiling; the needs_execution / un-built loci remain future waves.
- **Two confirmations carry design-intent caveats** (panoptic M-01 rounding-up-may-be-intended; silo M-06 direction)
  → MEDIUM, human-review tier — verifier-confirmed by execution, but awarded-mechanism fidelity warrants human sign-off.
- **GO is conditional on the human-in-the-loop submission filter**, not on the discovery layer being clean.
