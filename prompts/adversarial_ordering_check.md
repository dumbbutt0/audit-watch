# Adversarial state-ordering & boundary-enumeration check (P96 — advisory, research-only, UN-WIRED)

**When:** after the deep pass localizes a mechanism and the depth-trace **completes** (v3/v3.1/v3.2;
`localized_depth_trace.py`), and **before** a `REJECT` / harmless / Low is **finalized** on a localized
**accounting / withdrawal / lifecycle / role / state-order** mechanism.

**Why:** P94 guarantees a trace is *done*, not *correct*. On Wildcat (P95) a completed trace read
`executeWithdrawal`'s pro-rata `mulDiv(batch.normalizedAmountPaid, status.scaledAmount, batch.scaledTotalAmount)`
as locally correct — but never enumerated the **closed-market early-execution** ordering that breaks the
invariant `sum of executed withdrawals ≤ batch.normalizedAmountPaid`, so the last user under-withdraws (H-01, a
true High, was false-rejected). The same run dismissed `grantRole`'s provider-vs-provider expiry-replacement
rule as a "trusted control" without enumerating the **inter-principal** (provider A vs provider B) ordering that
bypasses it (M-05, a true Medium, was false-cleared). Both failures are *missing adversarial ordering
enumeration*, not incomplete traces.

## What to do
1. **State the invariant the REJECT relies on** (`relied_upon_invariant`). If you cannot name it, you cannot
   reject — reopen the trace.
2. **Try to break it** with **≥3 concrete state orderings**, drawn from these axes:
   - **Lifecycle ordering** — open vs **closed** market, active vs expired, pre/post settlement, before/after
     batch creation, before/after checkpoint, before/after role/provider expiry, before/after
     liquidation/settle/claim/forge/mint.
   - **Actor interleaving** — first vs last actor, victim before/after attacker, a third party acting between
     setup and execution, **provider A vs provider B**, an admin/keeper interleaving.
   - **Accounting boundary** — zero vs nonzero, partial vs full withdrawal, a **pro-rata denominator that
     changes** between requests, rounding accumulation, a stale snapshot, batch-total vs individual share,
     global vs scoped counter, array add vs remove order.
3. **Recovery analysis** — if a break exists, classify recovery: self-correct / privileged-only /
   migration-or-upgrade / temporary / bounded / permanent.
4. **Record** the case (schema below) and run `adversarial_ordering_check.evaluate(case)`.

## Output schema
```
proposed_reject_reason, relied_upon_invariant,
mechanism_class ∈ {accounting, lifecycle, role, state_order, guarded_control, other},
ordering_cases_tested[], boundary_cases_tested[], actor_interleavings_tested[], recovery_paths[],
counterexample_found:bool, counterexample_trace,
unresolved_ordering_dependency, inter_principal_trust_boundary:bool,
needs_execution:bool, execution_test_idea
```

## Verdicts (advisory)
- **`PASS_CANDIDATE`** — a concrete ordering breaks the invariant (counterexample with a trace). **Not a
  REJECT** — reopen as a candidate finding for human review.
- **`REOPEN_DEPTH_TRACE`** — invariant not stated; or <3 orderings on an accounting/lifecycle/role/state-order
  mechanism; or an inter-principal trust boundary dismissed without enumeration; or an unresolved ordering
  dependency; or a counterexample claimed without a trace.
- **`NEEDS_EXECUTION`** — orderings enumerated, only a runtime/execution confirmation remains; supply
  `execution_test_idea` (e.g. a Foundry test that closes the market mid-batch and asserts the last user is
  short).
- **`REJECT_CONFIRMED`** — a guarded single-principal control with no inter-principal boundary, **or** ≥3
  concrete orderings tried and none breaks the invariant. Reject-first preserved.

## Boundaries
Advisory and research-only. Emits a recommended verdict; **never** sets severity, **never** converts a REJECT
into a finding, **never** routes, and does **not** call or modify `severity_impact_gate` (frozen `193abf9f`).
A `PASS_CANDIDATE` is a request to reopen/escalate to human review — not a severity label or a submission.
