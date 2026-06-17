# P262 — RECALL_REGRESSION_DIAGNOSIS
Recall decomposed across 4 gates (prior-phase evidence):
1. **LOCUS_RECALL — THE LEAK.** P259: award loci were checkpoint-VISIBLE but SKIPPED (hybra GrowthHYBR.deposit;
   sentiment bad-debt right-shape-wrong-locus). Manual selection narrowed to 2–5 loci BEFORE shape discovery ran on
   the award-carrying surface. P260 backtest confirmed the prioritizer CAN surface skipped loci. => primary bottleneck.
2. **MECHANISM_RECALL — adequate once locus reached.** P258 manual widening missed some; P259 showed the shape
   vocabulary (T1–T8) generates the awarded classes WHEN the locus is reached. Gap was math/units (Basin) = add T9.
3. **RANKING_RECALL — secondary.** P256/P257: B/C ranking corrects the tidy-bias mis-ranking WHEN the mechanism is
   enumerated (notional #886). Helps, but only after the locus+mechanism are present.
4. **COMPLETION_RECALL — works when selected.** P254/P255: the five ops complete chains once the right mechanism is
   selected (loopfi #399).

## Conclusion
Primary bottleneck = **early locus pruning** (LOCUS_RECALL). Secondary = ranking. The simplest fix is **NOT**
template-expansion / ranking / completion refinement (all adequate once the locus is reached) — it is to **force
shape discovery on a bounded high-risk surface BEFORE narrow selection**, plus a lower-priority **T9** to restore
math/units recall. That is exactly what P262 implements.
