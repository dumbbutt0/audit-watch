# Phase 94 — v3 depth-completion refinement (resolve in-scope next-steps)

Closes the two P93 misses where the v3 depth-trace stopped one step short. No fresh blind eval; no machinery
change; severity gate frozen at `193abf9f`.

## Why
P93 (SAFETY-ONLY PASS) showed v3's discipline held (0 severity FP, 0 false escalations, 7/7 NEEDS_CONTEXT
well-formed, 0 bare abstains) but conversion was 0 because v3 abstained on resolvable **in-scope** next-steps:
- **M-02** (`RamsesV3Pool.flash`): named next-step "read flash body" but did **not** execute the in-scope read
  → missed `pFees0 = paid0 / feeProtocol` (protocol gets 1/80 not 80%).
- **M-01** (GaugeV3): the trace stopped at the **in-scope** staticcall boundary `positionPeriodSecondsInRange`
  instead of tracing into the pool's `periodCumulativesInside` skipped-period case.

## The completion gate (P94)
Added to `localized_depth_trace.evaluate(...)` (advisory, un-wired) + `config/localized_depth_trace.json` +
`prompts/deep_pass_depth_trace_v3.md` (v3.1 addendum). New optional trace fields: `next_step_type`
(`IN_SCOPE_READ` · `IN_SCOPE_CALL_TRACE` · `OUT_OF_SCOPE_DEPENDENCY` · `RUNTIME_VALUE` · `EXECUTION_REQUIRED`),
`next_step_resolved`, `resolved_evidence_ref`, `unresolved_reason`, `callee_in_scope`,
`final_trace_after_resolution`.

Rules (enforced only when an in-scope next-step / in-scope callee is declared — **legacy P92 traces are
unaffected**):
- An `IN_SCOPE_READ`/`IN_SCOPE_CALL_TRACE`, or `callee_in_scope=true`, that is **unresolved** → blocks **any**
  conclusion → `INSUFFICIENT_TRACE`.
- `next_step_resolved=true` for an in-scope step must carry `resolved_evidence_ref` + `final_trace_after_resolution`.
- An in-scope dependency may **not** end in `NEEDS_CONTEXT` (read it, then conclude PASS/REJECT).
- `NEEDS_CONTEXT` remains valid for genuinely out-of-scope/runtime/execution dependencies.
- **Completion, not escalation:** never forces a positive verdict — a completed bounded trace still `REJECT`s; a
  completed bug-path `PASS`es.

## Regression anchors (all pass)
| # | Case | Verdict |
|---|---|---|
| 1 | P93 M-02 next_step "read flash body" IN_SCOPE_READ unresolved | **INSUFFICIENT_TRACE** |
| 1' | P93 M-02 resolved read → `paid0/feeProtocol` | **PASS** |
| 2 | P93 M-01 in-scope staticcall boundary (callee_in_scope) unresolved | **INSUFFICIENT_TRACE** |
| 2' | P93 M-01 cross-contract trace into `periodCumulativesInside` | **PASS** |
| 3 | P91 M-02 calldata arithmetic (no new field) | **PASS** (still concrete) |
| 4 | P85 updateTaxRate completed bounded | **REJECT** (no forced positive) |
| 5 | P81e H-01 completed cross-function fee-routing | **PASS** |
| 6 | genuine OUT_OF_SCOPE dependency (+ named dep/value/next) | **NEEDS_CONTEXT** (still allowed) |
| — | resolved without evidence / invalid next_step_type / legacy P92 trace | INSUFFICIENT / INSUFFICIENT / unchanged |

## Integrity
- `severity_impact_gate.py` **unchanged** (`193abf9f`); deep_pass / hygiene / lens / funnel / handoff_generator /
  maximal_consequence_check byte-identical. Only `localized_depth_trace.py` + its config + the v3 prompt
  addendum + tests changed (the P92 module is the only thing refined; it is advisory/un-wired).
- No frozen-artifact mutation; no historical re-score; no production wiring (`localized_depth_trace` un-wired).

## Next
P95 = fresh sealed-key blind run on a **higher-density** subject using P91 selection + v3 + the P94 completion
rule + maximal_consequence_check, measuring whether conversion improves while holding 0 severity FP — and this
time executing the in-scope next-steps the completion gate now forces.
