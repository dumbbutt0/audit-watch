# Invariant-enumeration regression examples (P101)

These are **examples**, not rescoring — each is a past wrong-invariant miss, now asserted to be **covered by the
enumerator's candidate set** (see `tests/assisted/test_enumerate_candidate_invariants.py` +
`test_auto_validate_invariants.py`). The point: the relevant invariant is always *among* the generated
hypotheses, so the system can no longer test only a true-but-irrelevant one. Historical scores are unchanged.

| Subject (phase) | What the autonomous run got wrong before | Invariant category that must be generated now |
|---|---|---|
| **SecondSwap M-11 / H-01–H-02 (P97)** | tested only token-sum conservation (true but irrelevant) | `per_user_accounting` (buyer claim schedule) **+** `cap_limit` (maxSellPercent) — not only `value_conservation` |
| **Wildcat H-01 (P95)** | local pro-rata math looked correct; missed the closed-market ordering | `ordering_race` (closed-market withdrawal) + `recovery_availability` (last-user withdrawal) |
| **Ramses M-02 (P93)** | did not read the exact flash-fee arithmetic across the boundary | `cross_contract_consistency` / `reward_fee_distribution` (suspected_break = read exact `paid0/feeProtocol`) |
| **Phi H-05 (P89)** | missed public index mutation | `index_array_integrity` + `role_access` |
| **TraitForge H-01 (P87)** | global counter vs per-generation cap | `cap_limit` (global-counter-vs-scoped) |
| **Munchables H-05 (P85)** | dirty flag never reset | `lifecycle_state_transition` / `negative_space_missing_update` |

## Worked example — SecondSwap M-11 (autonomous, no human invariant selection)
`auto_validate_invariants` on `SecondSwap_VestingManager.listVesting` (see `lab_report.md`):
- **6 invariants generated** (recall) incl. `value_conservation`, `per_user_accounting`, `cap_limit`,
  `role_access`, `lifecycle_state_transition`, `recovery_availability` — all `HYPOTHESIS_ONLY`.
- The **`cap_limit`** invariant (maxSellPercent) had source-backed evidence (self-purchase `bought`-inflation
  counterexample) → it alone reached **`VALIDATED_FOR_POC_HANDOFF`** and ranks #1 human-actionable.
- The other 5 (incl. the token-sum `value_conservation` decoy) stalled at `NEEDS_CONTEXT` — **no human picked the
  invariant; the gates selected it.** That is the P97 fix demonstrated end-to-end.
