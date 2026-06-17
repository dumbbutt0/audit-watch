# P282 — VALUE_FLOW_REMAP_RESULTS

P281 corpus (84 candidates) re-run with D3 + the D1-gap closures. `outputs/remap_metrics.json`.

## Status distribution: P281 -> P282
| status | P281 | P282 |
|---|---|---|
| READY_FOR_POC_INTENT | 1 | 1 |
| INLINE_GUARD_REFUTED | 17 | 36 |
| NEEDS_VALUE_FLOW_EVIDENCE | 11 | 31 |
| NEEDS_STATE_MACHINE_EVIDENCE | 11 | 8 |
| NEEDS_SOURCE_SPAN | 1 | 1 |
| NEEDS_MORE_EVIDENCE | 43 | 7 |

## NEEDS_VALUE_FLOW subreasons (P282)
{"value_flow_present_but_no_anomaly": 17, "no_value_flow_in_span": 10, "value_flow_out_of_span(wrapper/delegation)": 4}

## Reading
- **Newly lifted to READY: 0.** No value-class candidate has a source-detectable in-span anomaly (no div-before-mul);
  their value-flow is either out-of-span (wrappers), absent (getters), or present-without-a-detectable-violation.
- **D1-gap closure: INLINE_GUARD_REFUTED 17 -> 36** (+19): either-side `msg.sender` and modifier-auth (only*)
  caught guarded functions (e.g. commitCheckpoint `!=msg.sender`, openPosition `onlyManager`) that previously slipped
  into NEEDS_MORE/NEEDS_VALUE_FLOW. The vague NEEDS_MORE_EVIDENCE bucket collapsed 43 -> 7.
- **NEEDS_VALUE_FLOW now carries precise subreasons:** value_flow_present_but_no_anomaly (needs data-flow/corrected-
  reference), value_flow_out_of_span (wrapper -> needs cross-function tracing), no_value_flow_in_span (getter/view).
- **L2Governor.execute remains READY / PASS_SUPPORTED** (regression preserved); **severe concluded/reportable FP = 0.**
- Precision up, recall flat (0 lifts): the value-flow VIOLATION (the actual bug) lives across function boundaries the
  span scan cannot follow -> the named next repair is cross-function/data-flow tracing.
