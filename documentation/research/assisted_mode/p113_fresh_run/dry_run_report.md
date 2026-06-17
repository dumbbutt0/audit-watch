# P113 — Fresh discovery run: report

**Candidate:** `ramses-2024-10 :: RamsesV3Pool.swap` (recommended #1).
**Terminal state: NEEDS_CONTEXT**  ·  research-only, un-wired.

## Stage path
- A intake — invariant supplied (mechanically selected candidate)
- B validation — `NEEDS_MORE_CONTEXT` (analyst evidence supplied: False)
  - reason: no depth_trace evidence supplied — provide the 5-step localized trace (localized_mechanism, controlled_inputs, pre_state, operation_trace, boundary_cases, post_state, concrete_outcome)
- C.0 harness prep — `HARNESS_COMPLEX` (scaffold inert: True)
- C runtime — attempted: False; state: NOT_ATTEMPTED
  - 

## Analyst rationale (honest source reading)

Read RamsesV3Pool.swap (the 973-line core UniV3-fork AMM swap). It is the canonical concentrated-liquidity swap loop plus Ramses' period/secondsPerLiquidity accounting. Observations: (1) the period-rollover writes (periods[], endSecondsPerLiquidityPeriodX128, lastTick) execute BEFORE the reentrancy lock check and `slot0.unlocked=false` — unusual vs canonical UniV3 where the lock is first — but the block only writes period METADATA from a memory snapshot, guarded by `period != lastPeriod`, with no fund movement; (2) the protocol-fee and feeGrowth math follow the standard pattern; (3) the period machinery this function maintains is exactly what underlies the real awarded P93 finding (GaugeV3 skipped-period reward inflation), whose IMPACT materializes cross-contract in GaugeV3's reward computation, not in swap itself. I could NOT form a source-provable exploit counterexample on swap alone, and could NOT prove it safe: establishing or refuting the reward-inflation path requires tracing across the in-scope pool->gauge boundary plus runtime evidence (the exact P93 source-only ceiling). I did not fabricate a trace. Truthful terminal: NEEDS_CONTEXT — high rank (max value/external-call/state signals on the busiest function) did not, and must not, become a finding.

## Safety boundaries
- no_auto_submit: True
- no_severity_inflation: True
- no_package_without_runtime: True
- no_ready_without_runtime: True
- advanced_only_on_evidence_not_rank: True

**Overall truthful: True** — terminal in the allowed set, no safety boundary violated. No submission package, no human-review-ready state, no auto-submit, no severity assigned.

_The #1 evidence-free-ranked function was investigated and honestly NOT promoted to a finding — ranking chose the order, not the verdict._

