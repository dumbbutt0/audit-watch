# P283 — TRACE_REMAP_RESULTS

P282 corpus (84 candidates · 12 eval audits) re-run with V2 cross-function tracing + comment-stripping + the `**`
exponent exclusion. Source: `outputs/remap_metrics.json`, `outputs/trace_evidence.json`.

## Status distribution: P282 → P283
| status | P282 | P283 |
|---|---|---|
| READY_FOR_POC_INTENT | 1 | 1 |
| INLINE_GUARD_REFUTED | 36 | 36 |
| NEEDS_VALUE_FLOW_EVIDENCE | 31 | 32 |
| NEEDS_STATE_MACHINE_EVIDENCE | 8 | 8 |
| NEEDS_SOURCE_SPAN | 1 | 1 |
| NEEDS_MORE_EVIDENCE | 7 | 6 |

**Newly lifted to READY: 0.** The only delta is a **precision gain**: one candidate (`PanopticPool:_burnOptions`) moved
NEEDS_MORE_EVIDENCE → NEEDS_VALUE_FLOW_EVIDENCE because its cross-function "anomaly" (`_getPremia` `/ 2 ** 64`) was a
false `**`-exponent match now correctly rejected. No candidate gained READY; one stopped passing the value-flow gate on
a false anomaly.

## Trace outcome over the value-class candidates (81 traced)
| trace_status | count | meaning |
|---|---|---|
| TRACE_FOUND | 35 | a resolvable callee body was reached and value-flow detected (evidence depth genuinely improved) |
| TRACE_PARTIAL | 10 | callee edges resolved but no value-flow/anomaly reached within bounds |
| TRACE_UNRESOLVED | 17 | root/callee body unavailable or ambiguous |
| TRACE_TOO_DYNAMIC | 19 | external/dynamic dispatch encountered → fail-closed, not traced |

Per-class TRACE_FOUND: SHARE_ROUNDING 11 · ACCOUNTING/BAD_DEBT 8 · STATE_MACHINE 8 · REWARDS 5 · others 3.

## Cross-function anomalies found
The tracer surfaced exactly **2** candidates with a div-before-mul cross-function anomaly at MEDIUM confidence — and on
inspection **both were false positives**:
- `VotingEscrow._checkpoint`: `(last_checkpoint / WEEK) * WEEK` — intentional week-boundary rounding, not a precision
  bug. (Held at INLINE_GUARD_REFUTED by D1; also a state-machine class, so V2 never applied.)
- `PanopticPool._getPremia`: `/ 2 ** 64` — fixed-point scaling; the `*` is exponentiation. (Removed by the `**` fix.)

After the `**` fix, **value-class V2-anomaly-eligible candidates = 0**. No value-class candidate lifts on an anomaly.

## Subreasons (NEEDS_VALUE_FLOW carriers)
`value_flow_present_but_no_anomaly` dominates → the value-flow is real but the *violation* is not a lexical anomaly; it
is a wrong epoch/recipient/reference/accumulator relationship → needs corrected-reference / data-flow reasoning.

## Regression & safety
- **L2Governor.execute remains READY_FOR_POC_INTENT** (PoC re-run PASS_SUPPORTED — `outputs/l2governor_regression_log.txt`).
  Its decision is carried by D2 state-machine evidence; its own trace is TRACE_PARTIAL (correct separation).
- **severe concluded/reportable FP = 0.** No false READY introduced.
