# P267 — LIMITATIONS

1. **Only ranking/selection, only top-2.** The selector acts on a pair of already-enumerated mechanisms. It cannot
   recover an awarded mechanism that was never enumerated (P255 BakerFi L5 = INCONCLUSIVE by construction). Discovery/
   enumeration is a different layer (P259/P262 territory), explicitly out of P267 scope.

2. **KEEP_BOTH is a "don't drop it," not a "got it."** The A/B/C wins are KEEP_BOTH — the selector preserves the
   awarded mechanism into completion/PoC. Whether that yields **exact recovery** depends on the completion + PoC
   layers on a fresh full-path run. P267 removes the P266 drop; it does not by itself prove exact recovery.

3. **Garbage-in:** dimension signals are operator-assigned. A mis-scored input (e.g. a true permanent DoS mislabeled
   `griefing_minor`, or a refuted mechanism marked `survives`) would mislead the selector. It formalizes and enforces
   the impact comparison; it does not independently verify the source claims behind each dimension.

4. **Backtest is necessary-not-sufficient.** Inputs were hand-encoded from already-scored frozen artifacts, so the
   selector is scored on cases whose impact structure I summarized. The real proof is a **fresh full-path run** where
   the dimensions are assigned blind, before reveal (the verdict only claims READY-for-that, not validated).

5. **Pairwise only.** It compares two mechanisms; a locus with 3+ live mechanisms must be reduced to pairs by the
   caller. KEEP_BOTH does not currently express "keep all three."

6. **Weights are a first cut.** The impact/validity weights in the config are reasonable but not tuned against a
   large labeled set; `min_impact_gap=2` is a judgment call. They are config-exposed for later calibration — which
   must itself be done without answer-key contamination.

7. **No severity / no authority.** Outputs are advisory (`ADVISORY_SELECTOR_DECISION`, all promotion flags false).
   "Advisory-only by construction" is enforced by the guard; it is not a claim that the selector's impact judgments
   are correct — only that they cannot leak into findings/severity/submission.
