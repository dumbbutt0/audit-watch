# P273 — LIMITATIONS

1. **Coverage ≠ recovery.** "Routed the awarded class" means a representative of that class reaches the P269 handoff —
   NOT that the exact awarded mechanism is recovered. P273 fixes the objective-mismatch *routing* (the P272 failure);
   whether completion+PoC then recover the exact bug is downstream (P274's job).

2. **Signal-keyword classification is heuristic.** Classes are assigned by keyword matches over the candidate's
   locus/signals/templates. A mis-signalled or jargon-named candidate misclassifies (e.g. Karak "slashing" landed in
   STATE_MACHINE_LIFECYCLE because "slash" isn't a keyword — the candidate is still routed, but the class label is
   approximate). Keyword sets are a first cut, config-exposed for later calibration.

3. **Anti-drama depends on the `impact_supported` input.** The negative control worked because the gated-admin was
   marked `impact_supported=false`. If an operator mislabels a properly-gated admin function as supported, the router
   could route it. The router enforces "signal + plausibility," not an independent verification of the mechanism.

4. **Recall depth is upstream and unchanged.** P273 can only route classes whose candidates were SURFACED by recall.
   In P272, the exact awarded loci (updateOrder/fillOrder) were not all in the top-20 — coverage routes the order
   *class* via adjacent candidates (coreCallback/_calculateFillOrderInfo), but a recall-depth miss of the exact locus
   is a separate gap P273 does not fix.

5. **Backtest necessary-not-sufficient.** Fixtures are hand-encoded from frozen reveals; the router is scored on
   signal text I summarized. Decisive proof is a fresh full-path run (P274) with signals assigned blind, pre-reveal.

6. **Budget/round-2 heuristic.** The anti-monoculture rule (no 2nd slot while a guard class has 0) is a reasonable
   default but not tuned against many labeled contests; with many classes the budget choice matters.

7. **Advisory only.** Outputs are `ADVISORY_COVERAGE_DECISION`, all promotion flags false (guard-enforced) — a
   containment guarantee, not a claim the class assignments or routing are optimal.
