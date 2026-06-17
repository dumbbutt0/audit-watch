# P283 — LIMITATIONS

1. **0 newly-lifted READY.** Cross-function tracing deepens evidence (35 TRACE_FOUND) but does not lift, because the
   value-flow VIOLATION is semantic (wrong reference/epoch/recipient/accumulator), not a lexical anomaly. The named next
   repair is corrected-reference / data-flow (SSA).
2. **The div-before-mul anomaly signal is unreliable.** Both MEDIUM "anomalies" the tracer found were false
   (`(x/WEEK)*WEEK` week-rounding; `/ 2 ** 64` exponent scaling). Comment-stripping + the `**` exclusion remove two
   classes of false match, but real-code benign `(x/U)*U` rounding can still match. The lift rule never rests on the
   anomaly alone (it must also pass D1 + full readiness), which is why FP stayed 0 — but the heuristic should be treated
   as a hint, not evidence.
3. **Static, bounded, name-based resolution.** depth 2, ≤5 callees/fn, ≤8 spans/candidate; ambiguous names and external/
   dynamic dispatch are fail-closed (TRACE_UNRESOLVED / TRACE_TOO_DYNAMIC). Bugs whose path crosses an external protocol
   or a runtime-dispatched callee are out of reach by design.
4. **Manifest-bound.** A callee whose body is not in the coverage manifest (multi-file libs, generated code) is
   unresolved. Parser/manifest completeness is a separate backlog item.
5. **Supervised eval, not blind, not production.** 12 eval audits with known award keys used only to score recall; award
   titles/bodies never read by the code. No production authority; advisory/eval-only; default-off; un-wired.
6. **No PoCs generated** beyond the L2Governor regression re-run (there was no new trustworthy READY to PoC).
