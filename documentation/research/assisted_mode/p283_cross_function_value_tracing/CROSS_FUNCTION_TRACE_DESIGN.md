# P283 — CROSS_FUNCTION_TRACE_DESIGN

## 1. P282 diagnosis (why span-local lifted 0)
The D3 span-local scan answered "is there a value-flow violation *in this function's own lines*?" For the eval corpus
the answer was almost always no: 31 candidates sat at NEEDS_VALUE_FLOW_EVIDENCE with subreasons
`value_flow_present_but_no_anomaly` (17), `no_value_flow_in_span` (10), `value_flow_out_of_span(wrapper)` (4). The entry
function is a thin wrapper/dispatcher; the value math lives one call deeper (`_claimFees`, `_updateFor`, `_checkpoint`,
a library). A span-local scan structurally cannot see it.

## 2. Edge types the tracer FOLLOWS (resolvable, deterministic)
- **same-contract internal call** — `_g()` where `C._g` is in the manifest.
- **inherited internal/public** — resolves to a unique manifest item by name.
- **library call resolvable locally** — `Lib.compute()` resolving to a single manifest function.
- **wrapper / delegation** where the callee name + args are visible (`return _impl(x)`).
- **self-call** resolving to the same source unit.

## 3. Edges the tracer REFUSES (fail-closed; never traced into)
- unbounded dynamic dispatch / arbitrary external protocols — `IGauge(x).claimFees()` → `too_dynamic`, not resolved.
- unknown delegatecall, proxy discovery, runtime storage-dependent dispatch.
- **ambiguous** names (resolve to >1 manifest item across contracts) → unresolved (conservative).
- callee with no resolvable body (declaration-only / outside manifest) → unresolved.

## 4. Bounds (config `research_cross_function_value_tracer.json`)
`max_depth = 2` · `max_callees_per_function = 5` · `max_total_spans_per_candidate = 8`. BFS from the candidate body;
each visited callee body is **comment-stripped** then run through the value-flow/anomaly detectors.

## 5. Per-candidate emission
`trace_status` ∈ {TRACE_FOUND, TRACE_PARTIAL, TRACE_UNRESOLVED, TRACE_TOO_DYNAMIC} · `trace_path`
(caller/callee/edge/source_span/state_write/asset_move/anomaly per edge) · `value_flow_path`
(attacker_input → callee value-move/anomaly → affected → invariant → poc_assertion) · `value_flow_confidence`
(MEDIUM only when a concrete cross-function div-before-mul anomaly is found; else LOW) · `unresolved_callees` ·
`unresolved_assumptions` · `source_basis`.

## 6. Class-specific trace goals
- accounting/liquidation/bad-debt → position vs global accumulator writes in the callee.
- share/rounding → share-conversion + div-before-mul ordering in the math callee.
- oracle/pricing → price helper + staleness/decimals path.
- rewards/claims → accumulator/snapshot update in the claim callee.

## 7. Confidence & comment-stripping (correctness)
All detectors run on **comment-stripped** callee bodies. Without it, math-explanation comments like `// T * (C - L) = G`
register as div-before-mul anomalies → false MEDIUM confidence → false READY (verdict C). Comment-stripping can only
*remove* false flags, never add lifts, so it is safe for P282's 0-lift result. (See IMPLEMENTATION_NOTES for the
additional `**` exponent exclusion.)

## 8. READY lift rule (earn it; don't loosen)
A value-class candidate (ACCOUNTING_LIQUIDATION_BAD_DEBT / SHARE_ROUNDING_PRECISION / ORACLE_PRICING / REWARDS_CLAIMS)
lifts past NEEDS_VALUE_FLOW_EVIDENCE **only** when ALL hold: trace_status == TRACE_FOUND · a concrete (comment-stripped)
cross-function div-before-mul anomaly · value_flow_confidence ∈ {HIGH, MEDIUM} · D1 inline guard does not refute · not
declaration-only. Even then it must still pass the full readiness dimensions (attacker_path/impact/invariant/assertion).
**Never** lifts on: unresolved/external/dynamic trace · generic value movement · generic invariant · a comment-only or
`**`-exponent "anomaly". *Tracing improves evidence quality; it must not create bugs by association.*

## 9. Valid-lift vs forbidden-over-inference examples
- VALID: `claim() → _claimImpl()` where `_claimImpl` does `total / supply * shares` (real div-before-mul) → MEDIUM →
  eligible (still must pass full readiness).
- FORBIDDEN: `f() → _move()` where `_move` only does `token.transfer(...)` → generic movement, no anomaly → stays
  NEEDS_VALUE_FLOW_EVIDENCE.
- FORBIDDEN: callee with `// a / b * c` comment, or `(a*b) / 2 ** 64` (exponent) → no anomaly.
