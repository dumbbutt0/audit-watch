# P262 — LIMITATIONS
1. Backtest is necessary-not-sufficient: the sweep is scored against loci its own signal-set tends to surface; real
   proof needs a fresh-contest end-to-end run (deferred, as in P261 — monetrix findings still private).
2. Sibling-locus misses: collectFees/initiateWithdraw (notional), getCreateAmount (plaza) not individually forced;
   only the mechanism-area locus (_accrueFees, _create) is. Downstream must generalize from the area locus.
3. Template precision unchanged from P260: bakerfi harvest routed T1 (external-dep) not the exact fee/T6 mechanism.
4. T9 recall vs precision: T9 widens to math/units loci (bounded ≤8); on math-heavy AMMs this adds candidates that
   are mostly benign — acceptable under the advisory/FP-guard, but it is recall-not-precision.
5. Caps can truncate: 4 contests hit the 30-mech total cap (truncated:true). A real award mechanism could in
   principle be dropped by the cap; mitigated by keeping P260-rank order + recording truncation, but it is a risk.
6. No completion/ranking is actually executed here — the sweep only PREPARES bounded B/C-ranking input.
