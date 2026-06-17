# Assisted-Mode Human Checklist (P98)

Use this before and during an assisted-mode validation. The point of assisted-mode is that **you** supply the
invariant — the step P97 showed the system cannot do reliably on hardened code. Audit-Watch then validates it
reject-first. RESEARCH-ONLY; nothing here auto-submits.

## Before running validation — fill the candidate intake
(`schemas/assisted_candidate_intake.schema.json`)

- [ ] **State the suspected invariant** (`candidate_invariant`) — the property that must be TRUE and that the
      bug would break. **Required, non-empty.** Be precise: not "accounting is correct" but e.g. "each buyer's
      claim schedule reflects the vesting they actually bought."
- [ ] **Name the victim** (`affected_actor`) and the **trigger actor** (`attacker_or_trigger_actor`) — who is
      harmed, and who/what causes the break (attacker, third party, sequencing).
- [ ] **Identify the entrypoint** (`entrypoint`) — the EOA-reachable function that starts the path.
- [ ] **List the state orderings to test** — supply them in `adversarial_ordering.ordering_cases_tested /
      boundary_cases_tested / actor_interleavings_tested`, or a concrete `counterexample_trace`. ≥3 orderings
      for accounting/lifecycle/role/state-order, or a counterexample.
- [ ] **List the source lines** (`source_refs`) grounding the claim (file:line).
- [ ] **Give at least one concrete failure hypothesis** (`suspected_break`) — a specific ordering/boundary that
      breaks the invariant, not a generic worry.
- [ ] Supply the `depth_trace` (5-step) and `impact_assessment` evidence blocks if you want a full validation
      (not just `TRACE_ONLY`).

## Run validation
- [ ] `python scripts/assisted/validate_candidate_invariant.py --candidate <intake>.json --out <dir>`
- [ ] Read `validation_report.md` and the decision.

## Reject-first gates — do NOT skip
- [ ] **Move to PoC only if** the decision is `VALIDATED_FOR_POC_HANDOFF` (PASS_CANDIDATE that survived depth
      trace + adversarial ordering + maximal consequence + severity gate + hygiene).
- [ ] If `REJECTED_SOURCE_PROVEN_SAFE`: the invariant holds across the orderings — **not a finding**. Re-open
      only with a *different* invariant + a concrete counterexample (this is the P97 lesson: try a different
      invariant, not more orderings on the same one).
- [ ] If `NEEDS_MORE_CONTEXT` / `NEEDS_EXECUTION`: supply the missing trace/ordering/execution and re-run.
- [ ] If `BLOCKED_UNSUPPORTED_CLAIM`: a severity FP or unsupported escalator blocks handoff — fix the claim.
- [ ] **Move to submission only after** human scope review + duplicate review (the validator returns
      `BLOCKED_SCOPE_OR_DUPLICATE_PENDING` until you clear them) — and only you decide submit / no-submit.

## Final human responsibilities (never delegated)
- [ ] Scope decision · [ ] Duplicate decision · [ ] Final severity tier · [ ] Final wording · [ ] Submit / no-submit.
