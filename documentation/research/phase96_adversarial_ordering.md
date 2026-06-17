# Phase 96 — Adversarial state-ordering & boundary-enumeration check

**Status:** RESEARCH-ONLY, advisory, UN-WIRED. No blind eval. No machinery change.
**Date:** 2026-06-03.

## What P95 exposed
P95 (Wildcat 2024-08, a higher-density 9 H/M subject) was a SAFETY-only pass but a **negative conversion
result** — and, for the first time across seven blind runs, a *completed* depth-trace produced a
**confident-but-wrong REJECT** of a true High:

- **H-01 `executeWithdrawal`** — the depth-trace (v3.1, in-scope read resolved) concluded the pro-rata
  `mulDiv(batch.normalizedAmountPaid, status.scaledAmount, batch.scaledTotalAmount)` was "locally correct;
  accounting consistent" → REJECT. It was **wrong**: under the **closed-market early-execution** ordering
  (withdrawals execute before all requests are batched, plus small-request rounding), the invariant
  `sum of executed withdrawals ≤ batch.normalizedAmountPaid` breaks and the last user under-withdraws. The
  trace was *done*, not adversarially complete.
- **M-05 `grantRole`** — the provider-vs-provider expiry-replacement rule was localized and dismissed as a
  "trusted-provider control." The awarded finding is exactly that rule being bypassable **provider A vs
  provider B** — an *inter-principal* boundary the trace never enumerated.

P92/P94 guarantee a localized trace is **done** (5-step concrete trace, in-scope next-steps resolved). They do
**not** guarantee it is **correct**: neither forces the analyst to try to *break* the invariant the REJECT
relies on. P96 adds exactly that, as a second advisory gate.

## The check
`scripts/investigation/adversarial_ordering_check.py` + `config/adversarial_ordering_check.json` +
`prompts/adversarial_ordering_check.md`, plus a one-paragraph **v3.2** hook in
`prompts/deep_pass_depth_trace_v3.md`. Same advisory pattern as `maximal_consequence_check` (P90-C) and
`localized_depth_trace` (P92/P94): a NamedTuple `evaluate(case)`, `FLAGS`, `--self-test`.

Before a localized, completed REJECT/harmless/Low may be **finalized**, the analyst must state the
`relied_upon_invariant` and try to break it with **≥3 concrete orderings** across three axes (lifecycle,
actor-interleaving, accounting-boundary) plus a recovery analysis.

**Decision precedence** (`evaluate(case)`):
1. invariant not stated → `REOPEN_DEPTH_TRACE`
2. counterexample found → `PASS_CANDIDATE` (with trace) / `REOPEN_DEPTH_TRACE` (without)
3. unresolved ordering dependency → `REOPEN_DEPTH_TRACE`
4. inter-principal trust boundary AND <3 orderings → `REOPEN_DEPTH_TRACE` (fixes M-05)
5. mechanism ∈ {accounting, lifecycle, role, state_order} AND <3 orderings → `REOPEN_DEPTH_TRACE` (fixes H-01)
6. only execution remains → `NEEDS_EXECUTION` (with a test idea) / `REOPEN_DEPTH_TRACE` (without)
7. else (guarded single-principal control, or ≥3 orderings no counterexample) → `REJECT_CONFIRMED`

`relevant orderings = len(ordering_cases_tested) + len(boundary_cases_tested) + len(actor_interleavings_tested)`.

It does **not** call or modify `severity_impact_gate` (frozen `193abf9f`), never sets severity, never converts a
REJECT into a finding, never routes. It only decides **finalize vs reopen**. A `PASS_CANDIDATE` is a request to
reopen/escalate to human review — not a severity label or a submission.

## Regression anchors (in the self-test + `tests/investigation/test_adversarial_ordering_check.py`)
| Anchor | Input shape | Verdict |
|---|---|---|
| P95 H-01 `executeWithdrawal`, local pro-rata, no closed-market ordering | accounting, <3 orderings | `REOPEN_DEPTH_TRACE` |
| P95 H-01 with closed-market early-execution counterexample | accounting, counterexample + trace | `PASS_CANDIDATE` |
| P95 M-05 `grantRole`, inter-principal dismissed as trusted control | role, inter_principal, <3 | `REOPEN_DEPTH_TRACE` |
| P95 M-05 with provider-B-lowers-expiry counterexample | role, counterexample + trace | `PASS_CANDIDATE` |
| P85 `updateTaxRate`, ≥3 orderings, bounded eventual correction | accounting, 6 orderings, no cex | `REJECT_CONFIRMED` |
| P81e H-01 fee-routing, claimant-order dependence | accounting, counterexample + trace | `PASS_CANDIDATE` |
| P87 M-18 `forgeWithListed`, third-party race | state_order, counterexample + trace | `PASS_CANDIDATE` |
| Guarded `onlyOwner` control, no inter-principal boundary | guarded_control, no cex | `REJECT_CONFIRMED` |

## Ceiling note
This is the honest framing carried forward from P95. **Audit-Watch is a strong safety / triage / handoff
harness:** across seven blind runs it has held 0 severity false-positives, rejected privileged controls cleanly,
produced 0 depth-trace false escalations, and converted one blind hit end-to-end into an executable PoC handoff
(P81e→P82 Vultisig H-01). **Autonomous blind conversion on well-engineered, hardened code remains
capability-bound:** four consecutive depth-equipped blind runs (P91, P93, P95, Kleidi) produced 0 conversion,
and P95 showed the residual bottleneck is *blind reasoning correctness* — specifically, completed local traces
that never enumerate the adversarial state ordering that breaks an invariant. **P96 addresses exactly that one
narrow failure** and nothing more; it does not claim to close the capability gap. It makes a confident-but-wrong
REJECT *harder to finalize* (reopen, or surface as a PASS_CANDIDATE for human review) without weakening
reject-first on bounded/guarded negatives.

## Next
**P97** = one final fresh sealed-key confirmation run. If P97 still shows 0 conversion or completed-but-wrong
rejects, **formally pivot the tool's positioning to assisted triage / handoff rather than autonomous blind
discovery.**
