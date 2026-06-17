# PoC run plan — Cred._addCredIdPerAddress (P89-H05) — Access-control / privileged

Reject-first reproduction plan. The bundle is NOT reproduced until every step below is done and the test fails
on vulnerable source for the expected reason.

## Invariant under test
> authorization invariant: a state-mutating or value-moving function must reject callers without the required role; an unauthorized EOA/contract call must revert (and leave guarded state unchanged).

## Setup
From an unprivileged attacker account/contract, call the under-guarded entrypoint directly; assert the call succeeds when it should not, the guarded state mutated, and (for High) a downstream fund-impacting consequence follows.

## L3 requirements for this finding type (missing_auth_accounting_drift)
- [ ] unauthorized_call_succeeds
- [ ] accounting_drift_shown
- [ ] direct_fund_loss_asserted

## Steps
1. Pin the in-scope repo at the audited commit (2465e04364b759c721f1a0aebace69920411f8aa); `git submodule update --init --recursive`.
2. `forge build` (record solc version).
3. Implement `CredAddCredIdPerAddressPoC.test_P89_H05_invariant` from source behavior — L1 entry, L2 state flip (named slots /
   balances asserted), L3 outcome (the invariant above). Remove the scaffold guard only when L1–L3 are real.
4. Run: `forge test --match-test test_P89_H05_invariant -vv` → expect **FAIL** on vulnerable source for the expected reason; capture exact output.
5. Apply the minimal patch (negative control) and re-run → expect **PASS**; restore source.
   - Negative control: Add onlyRegistratorOrGovernor modifier. Assert that the attacker contract call reverts. Assert totalDepositsWei unchanged.
6. `forge test` (full suite) → expect existing tests pass, only the PoC fails (the proof).

## On success
- Fill `evidence_bundle.md` (exact source refs, failing output, patch result, suite result, frozen hashes).
- Fill `submission_draft.md` and `reviewer_notes.md` TODOs.
- Re-run `pre_submission_gate.md` items 4–9 → only then may the funnel record advance toward
  READY_FOR_HUMAN_REVIEW, with items 2 (scope) and 3 (duplicate) still PENDING for the human.
