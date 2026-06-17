# P282 — VERDICT

## Verdict: **B — VALUE_FLOW_DERIVER_PROMISING_NEEDS_REFINEMENT**

### Why B
D3 + the D1-gap closures sharply improved the funnel and held precision, but lifted **0 new candidates**:
- **Value-flow structure detection works** (state-write/asset-move/terms + div-before-mul anomaly + wrapper/delegation
  detection); NEEDS_VALUE_FLOW now carries precise subreasons (17 value-present-no-anomaly · 4 out-of-span · 10
  no-value-flow) instead of a vague block.
- **D1-gap closure** (either-side `msg.sender`, modifier-auth `only*`) raised INLINE_GUARD_REFUTED **17→36** (+19 real
  guards caught, e.g. commitCheckpoint/openPosition); the vague NEEDS_MORE_EVIDENCE bucket collapsed **43→7**.
- **No false READYs** (the anomaly-required lift rule prevented "moving value = READY"); audit found 0 hallucinated
  core evidence / 0 over-inference; **L2Governor.execute remains READY / PASS_SUPPORTED**; **severe FP = 0**.

But **0 new lifts** because the value-flow VIOLATION lives across function boundaries (wrappers/delegations) or needs a
corrected-reference comparison the span-local scan cannot do. Per the user's ladder this is exactly B ("improves block
reasons / lifts ≤1, needs refinement") — the deriver is promising and precision-correct but needs the cross-function /
data-flow refinement to actually lift accounting/math/oracle. Calling it "ready for the PoC sweep" (A) would overclaim
since D3 itself lifted nothing (the documented-supply clause technically allows A, but the honest signal is B).

### Not A / C / D
- Not **A**: D3 lifted 0; the precision gain was largely the D1-gap closure, not D3 lifting value classes.
- Not **C** (too noisy): anomaly-gated lift produced 0 false READYs; severe FP=0.
- Not **D** (aborted): research-only; only extractor/deriver/gate + test/docs changed; P260–P278 + router + forbidden 5
  byte-identical; active audit unchanged; back-compat (39 prior tests green).

### Next (named, priority order)
1. **V2 cross-function / data-flow value tracing** — follow delegated callees (the 4 out-of-span wrappers).
2. **V1 corrected-reference / data-flow derivation** — for the 17 value-present-but-no-anomaly (the actual invariant
   violation needs a reference comparison).
Then re-map; then a small PoC sweep on the trustworthy READY set; then a fresh blind target. Production authority WITHHELD.
