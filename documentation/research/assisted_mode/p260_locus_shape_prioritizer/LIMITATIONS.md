# P260 — LIMITATIONS
1. **Shape-vocabulary coverage gap (math/units/convergence):** basin decodeWellData (copy-paste decimals) and
   calcReserveAtRatio (silent non-convergence) are NOT routed by any of T1–T8 → not prioritized. The 8 templates
   model accounting/state/solvency/share-price/state-machine shapes, not pure-math/units/numerical-convergence.
   Fresh targets in that class would be missed; a future template (T9 numerical/units/convergence) may be needed.
2. **Template precision:** routing is keyword/marker-based, so a locus can get the right *family area* but a
   slightly-off template (bakerfi harvest → T1 external-dep rather than the awarded fee/newDeployedAmount T6/accounting).
3. **Ranking is breadth-not-precision:** loopfi liquidatePosition surfaced but at #13/15; notional fee only 1/3 loci.
   Top-N=15 captures it but a tighter N would drop it. Tuning weights/N is future work.
4. **Backtest ≠ validation:** the module's signal-set partly determines which loci it surfaces, so backtest recall
   is optimistic. Live proof requires a fresh unseen contest (P261).
5. **No deep mechanism reasoning:** hypotheses are interrogative scaffolds; correctness of the *mechanism* still
   depends on downstream B/C ranking + five-operation completion (unchanged).
6. **Determinism vs nuance:** no LLM-in-loop, so cross-contract/identity and reentrancy-ordering signals are coarse
   (name/marker heuristics), not full dataflow.
