# P207 — failure cases & honest limitations

1. **Faithful pool mock, not the canonical V3 pool.** `FaithfulV3Pool` implements canonical single-position
   mint/burn-poke/positions/collect + fee-growth, but is not the full `UniswapV3Pool` deployed via a real factory with
   a real swap. Mitigation: the single-investor **control test** passes (sole holder is made whole, feeTaker=0),
   isolating the loss to ILOPool's cross-user accounting rather than the mock; the mock has no per-user logic and no
   injected bug. A real-pool variant is the gold-standard follow-up but was unnecessary for an executed verdict.

2. **Simplified principal composition.** Fees and principal are modeled in token0 only (token1 flows are 0). This is
   conservative — it does not create the fee-misattribution bug (which is about `feeGrowthInside`/`collect(max)` across
   users), and keeps the harness legible.

3. **ManagerStub stands in for ILOManager.** It returns the source-valid `Project` and drives `initialize`/`launch`
   as the real manager would. The real `ILOPool` (and its inherited `ILOManager` interface) bytecode runs unmodified;
   no vulnerable logic lives in the stub.

4. **Scope: two controls only.** H-01 (positive) + M-03 (negative). Other src/ awarded findings (H-03 launch DoS, M-02
   claim slippage) were not harnessed — out of the two-control validation scope, not required for the decision.

5. **Orchestrator answer-aware.** P207 reuses P205's post-freeze mapping (no new blind run); the H-01/M-03 verdicts are
   objective EVM executions with pre-registered, source-justified setups (`L3_TARGET_MATRIX.md`), so contamination
   does not affect the measured results. `fabrication_rate=0`.
