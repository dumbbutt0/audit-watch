# P281 — READY_NOISE_REPORT

## READY precision proxy: 0/3 -> 1/1
- Before (P280): 3 READY, 0 PoC-supported (2 inline-guard refuted, 1 benign/mis-framed).
- After (P281): 1 READY, 1 PoC-supported (state-machine, correctly framed).

## Inline-guard false-READY reduction
**17** candidates corpus-wide downgraded to INLINE_GUARD_REFUTED (the dominant P280 failure mode) — the manifest
`modifiers` blind spot is closed by reading the body.

## State-machine framing improvement
L2Governor.execute reframed from a (wrong) ACCESS "unauthorized" claim to a (correct, supported) state-machine anomaly;
11 other candidates correctly held at NEEDS_STATE_MACHINE_EVIDENCE (state class, no detected state gate).

## Value-flow
11 candidates held at NEEDS_VALUE_FLOW_EVIDENCE (accounting/math/oracle/reward classes without a concrete delta) — the
next repair (D3 value-flow derivation) targets these.

## Severe concluded/reportable FP: 0. Unresolved weakness: value-flow classes remain blocked (by design) until D3.
