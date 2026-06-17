# P282 — VALUE_FLOW_REPAIR_BACKLOG

| id | blocked subreason (count) | class | missing source-derived fact | next repair | priority | FP risk |
|---|---|---|---|---|---|---|
| **V1** | value_flow_present_but_no_anomaly (17) | accounting/share/oracle/reward | the actual INVARIANT VIOLATION (a transfer/write is not a bug); needs before/after value reasoning | **data-flow + corrected-reference derivation** (compare against a conservation/rounding reference) | **1** | medium (must stay anomaly-gated) |
| **V2** | value_flow_out_of_span / wrapper (4) | accounting/reward | value-flow lives in the delegated callee (`_x()`, `.compact()`, per-pool loop) | **cross-function / data-flow value tracing** (follow delegated callees into their spans) | **1** | low |
| V3 | no_value_flow_in_span (10) | getter/view | not an attacker entry / no state change | recall/scope re-screen (these are likely true negatives) | 4 | none |
| V4 | NEEDS_STATE_MACHINE_EVIDENCE (8) | state/order | a forbidden-state-accepting transition not detected by the OR-gate heuristic | state-machine refinement (enum reachability) | 3 | low |
| V5 | oracle-specific | oracle | stale/manipulable price + dependent valuation path | oracle-specific derivation (feed source + consumer) | 2 | medium |

**Headline:** the two priority-1 items — **cross-function value tracing (V2)** and **data-flow/corrected-reference
derivation (V1)** — are what actually lift accounting/math/oracle. The source-span scan establishes value-flow
STRUCTURE but the VIOLATION lives across function boundaries / requires a reference comparison the span cannot give.
