# Deep-Pass Depth-Trace v3 (Phase-92, RESEARCH-ONLY, experimental/off)

Composes ON TOP OF `deep_pass_depth_trace_v2.md`. v2's §1 (exploitable-as-deployed) + §2 (mechanism-match) tell
you *whether* and *which* mechanism to localize. **v3 governs what happens AFTER a suspicious mechanism is
localized:** you must run a concrete execution trace **before** concluding `NEEDS_CONTEXT`, harmless, or Low.

Why v3 exists: across five blind runs the dominant recall loss is **conversion depth**, not lead selection or
the (frozen) severity gate. P91 made it concrete — the system *localized* the calldata index/length mechanism
(M-02) and flagged `NEEDS_CONTEXT`, but never traced `length = endIndex - startIndex` (missing `+1`) to its
concrete revert. v3 forces that trace.

> **Hard rule: `NEEDS_CONTEXT` is NOT a substitute for tracing.** It is allowed only after the trace reaches a
> *specific* unknown external dependency/fixture/runtime value, you *name* the missing evidence, and you state
> the *next* command/file/function to resolve it. A generic "needs more context" or "looks fine" is rejected.
> This does **not** weaken reject-first: a *traced* bounded/harmless outcome is still a valid `REJECT`.

## The mandatory 5-step concrete trace (run on every localized mechanism)

**1. Inputs** — attacker/user-controlled inputs; their bounds; caller permissions; the reachable entrypoint(s);
preconditions to reach this code on the live in-scope deployment.

**2. State-before** — the exact storage that matters: values, counters, balances, mappings, indexes, flags,
lifecycle phase. Name the variables.

**3. Operation** — write the **exact** expression(s) and trace them:
- arithmetic / validation expression (copy it),
- off-by-one boundaries (`<` vs `<=`, length = `end - start` vs `end - start + 1`),
- array length ↔ index relationships,
- calldata slicing / decoding length,
- rounding / precision / rate transformation,
- state-mutation order, external-call order, loop bounds.
Pick the **boundary/edge case** that stresses it (max value, full-width param, empty array, first actor, equal
indices, zero, overflow edge) and compute the result by hand.

**4. State-after** — what changed, what did NOT; who can still recover; whether later calls fail; whether
funds/rewards/rights become inaccessible; whether the protocol self-corrects.

**5. Concrete outcome** — one of:
- **PASS** — bug path proven (the boundary case yields a concrete revert / loss / corruption / unauthorized
  effect). Carry it to v2's §8 finding schema.
- **REJECT** — the trace proves harmless/bounded (e.g. bounded skew that self-corrects next settle, no concrete
  material consequence). Requires the boundary-case + state-after trace — not a generic "looks standard."
- **NEEDS_CONTEXT** — only with `{named_dependency, missing_value, next_step}` after a real trace attempt.

## Target miss classes (localize → trace → conclude)
calldata index/length/offset arithmetic (P91 M-02) · counter-scope global-vs-local (P87 H-01) ·
self-inflicted-vs-involuntary race (P89 M-07, P87 M-18) · admin-footgun-vs-externally-triggerable user harm
(P87 H-03) · precision/rounding/rate · stale-flag/lifecycle reset (P85 H-05) · array/index corruption
(P89 H-05) · state-mutation before/after validation · missing negative-space function or cleanup path.

## Output schema (append per localized mechanism)
```json
{
  "localized_mechanism": "Contract.fn — the exact suspicious expression",
  "controlled_inputs": "attacker/user inputs + bounds + caller perms + entrypoint + preconditions",
  "pre_state": "named storage/counters/indexes/flags/phase before",
  "operation_trace": "the exact expression(s) traced; off-by-one / length / order / loop bounds",
  "boundary_cases": "the edge case stressed (full-width param / equal indices / first actor / max) + hand result",
  "post_state": "what changed/didn't; later-call failure; recoverability; self-correction",
  "recovery_paths": "who can recover and how, or 'none'",
  "concrete_outcome": "PASS | REJECT | NEEDS_CONTEXT",
  "missing_evidence_if_any": {"named_dependency": "...", "missing_value": "...", "next_step": "..."},
  "recommended_verdict": "PASS | REJECT | NEEDS_CONTEXT"
}
```

## Mechanized completeness check
`scripts/investigation/localized_depth_trace.py` `evaluate(trace)` validates this trace and returns a
`recommended_verdict`, downgrading to **`INSUFFICIENT_TRACE`** when: a required field is empty; a `PASS` lacks a
concrete operation+boundary+post-state; a `REJECT` lacks a boundary+post-state trace; or a `NEEDS_CONTEXT` lacks
`{named_dependency, missing_value, next_step}` + a real trace attempt. It is **advisory and un-wired** — it
never sets severity, never calls/changes `severity_impact_gate` (frozen `193abf9f`), and never converts a
REJECT into a finding. Severity labelling stays with the maximal-consequence check (P90-C) + the gate.

## v3.1 completion addendum (P94) — resolve in-scope next-steps before freezing
P93 showed v3 can stop one step short: it named the right next-step ("read `flash` body") or localized a
mechanism behind an in-scope staticcall, then **abstained instead of completing the in-scope read/trace**
(missing `pFees0 = paid0 / feeProtocol`, and the pool's `periodCumulativesInside` skipped-period case). So:

> **A `NEEDS_CONTEXT` / harmless / `REJECT` / `Low` conclusion cannot be frozen while a next-step is resolvable
> from in-scope source.** If `next_step` is an in-scope function-body read, file read, in-scope
> staticcall/external-call target, in-scope library call, or a direct arithmetic/validation expression in
> source — **go read it and re-trace.** `NEEDS_CONTEXT` is allowed only for genuinely out-of-scope state,
> unavailable runtime/deployment/oracle values, un-vendored external behavior, missing fork/fixture data, or
> ambiguity that requires execution rather than a source read.

Record the completion fields: `next_step_type` (`IN_SCOPE_READ` · `IN_SCOPE_CALL_TRACE` ·
`OUT_OF_SCOPE_DEPENDENCY` · `RUNTIME_VALUE` · `EXECUTION_REQUIRED`), `next_step_resolved`,
`resolved_evidence_ref` (if true), `unresolved_reason` (if false), `callee_in_scope`, and
`final_trace_after_resolution`. `localized_depth_trace.evaluate(...)` enforces it: an
`IN_SCOPE_READ`/`IN_SCOPE_CALL_TRACE` (or `callee_in_scope=true`) that is **unresolved** → `INSUFFICIENT_TRACE`;
a resolved one must carry `resolved_evidence_ref` + `final_trace_after_resolution`; an in-scope dependency may
**not** end in `NEEDS_CONTEXT` (conclude PASS/REJECT after reading it). A **completion** rule, never an
escalation — a completed bounded trace still `REJECT`s; a completed bug-path `PASS`es.

## v3.2 — adversarial ordering before a final REJECT (P96, advisory)
A *completed* trace (P94) is **done**, not necessarily **correct**: P95 traced `executeWithdrawal`'s pro-rata
`mulDiv` as locally correct yet missed the **closed-market early-execution** ordering that breaks
`sum ≤ batch.normalizedAmountPaid`, and dismissed `grantRole`'s provider-vs-provider expiry rule as a "trusted
control." So **before finalizing a REJECT/harmless/Low on a localized accounting / withdrawal / role /
state-order mechanism**, run `adversarial_ordering_check`: state the `relied_upon_invariant`, then actively try
to break it with **≥3 concrete orderings** (lifecycle + actor-interleaving + accounting-boundary) and a recovery
analysis. The REJECT is honored only on `REJECT_CONFIRMED`; a found counterexample → `PASS_CANDIDATE` (not a
REJECT); `REOPEN_DEPTH_TRACE` when <3 orderings or an inter-principal boundary was dismissed as trusted;
`NEEDS_EXECUTION` (with a test idea) when only runtime confirmation remains. Advisory/research-only — never sets
severity, never converts a REJECT into a finding, never routes.

## Discipline
- Localize (v2 §1+§2) → trace (v3 1–5) → **resolve in-scope next-steps (v3.1)** → **enumerate adversarial
  orderings before a REJECT (v3.2)** → conclude. No `NEEDS_CONTEXT`/harmless without the trace, none while a
  resolvable in-scope dependency remains, and no finalized REJECT on an accounting/lifecycle/role/state-order
  mechanism without ≥3 orderings tried.
- Reject-first preserved: a *traced + adversarially-enumerated* bounded outcome is a valid `REJECT`; "more
  findings" is still a liability.
- Research-only: emits a hypothesis + recommended verdict; no severity/submission/routing.
