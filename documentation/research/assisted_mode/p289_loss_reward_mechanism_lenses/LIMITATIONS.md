# P289 — LIMITATIONS

1. **Only Lens 1 has a confirmed positive lift** (ECG H-04). Lenses 2 (bad-debt contagion), 3 (reward-index init), 4
   (share-transfer theft) are implemented + fail-closed but matched nothing liftable in this corpus sample — proven
   FP-safe, NOT proven on a positive. Their generalization is unverified until a target with those confirmed award
   classes is run.
2. **Coupling heuristics, MEDIUM ceiling.** The lenses detect source-signal co-occurrence + refutation, not a proven
   exploit. A lift means "evidence complete enough to attempt a PoC," not "is a bug." The audit confirmed the one lift is
   source-faithful to H-04.
3. **Span-local.** Lens 2 missed H-03 (onBid) because the bad-debt global write is in a callee, not the candidate span;
   extending over the P283 trace path is the named next repair.
4. **Lens 4 marginal over-match** (hybra GaugeCL.withdraw) — held (state class), 0 FP, but flags that the
   transfer-detection should require an actual from/to balance move, not a withdraw. Backlogged.
5. **Supervised, advisory, not production.** ECG used as eval only; no ECG names/award text in runtime. No production
   authority / submission / severity. Only the L2Governor + kelp + claim_many regressions and a PoC-intent (no new full
   PoC) this phase.
