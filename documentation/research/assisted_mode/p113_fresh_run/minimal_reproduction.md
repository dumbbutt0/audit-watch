# Minimal reproduction hypothesis

Candidate: `ramses-2024-10 :: RamsesV3Pool.swap`.

## Source-backed hypothesis attempt

Read RamsesV3Pool.swap (the 973-line core UniV3-fork AMM swap). It is the canonical concentrated-liquidity swap loop plus Ramses' period/secondsPerLiquidity accounting. Observations: (1) the period-rollover writes (periods[], endSecondsPerLiquidityPeriodX128, lastTick) execute BEFORE the reentrancy lock check and `slot0.unlocked=false` — unusual vs canonical UniV3 where the lock is first — but the block only writes period METADATA from a memory snapshot, guarded by `period != lastPeriod`, with no fund movement; (2) the protocol-fee and feeGrowth math follow the standard pattern; (3) the period machinery this function maintains is exactly what underlies the real awarded P93 finding (GaugeV3 skipped-period reward inflation), whose IMPACT materializes cross-contract in GaugeV3's reward computation, not in swap itself. I could NOT form a source-provable exploit counterexample on swap alone, and could NOT prove it safe: establishing or refuting the reward-inflation path requires tracing across the in-scope pool->gauge boundary plus runtime evidence (the exact P93 source-only ceiling). I did not fabricate a trace. Truthful terminal: NEEDS_CONTEXT — high rank (max value/external-call/state signals on the busiest function) did not, and must not, become a finding.

## What runtime evidence would be required

A falsifiable runtime check could not be specified from source alone for this candidate (see rationale). Resolving it would require execution-backed evidence — e.g. a fork/local deployment plus a differential or invariant test across the cross-contract boundary named above — not further source reasoning. Absent that, the truthful terminal is `NEEDS_CONTEXT`; no exploit is claimed and no finding is promoted.
