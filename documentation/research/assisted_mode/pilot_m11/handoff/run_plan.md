# PoC run plan — SecondSwap_VestingManager.listVesting (ASSISTED-M11) — Validation-liveness / counter-scope

Reject-first reproduction plan. The bundle is NOT reproduced until every step below is done and the test fails
on vulnerable source for the expected reason.

## Invariant under test
> validation-domain invariant: a capacity/eligibility check must use the CORRECT scope (per-generation / per-user / per-listing), not a global or wrong-domain counter; a user-facing mint/claim/withdraw/settle/forge/buy/sell path must remain usable while the correct-scope condition holds. A wrong-scope check that permanently blocks the path is a liveness failure.

## Setup
Drive the system to the boundary where the wrong-domain check trips (e.g. global token count reaches the per-generation cap); call the user-facing path as a normal user; assert it is blocked (mints 0 / reverts / full refund); then show no self-recovery (no setter, counter never reset) so the brick is permanent from that point.

## L3 requirements for this finding type (validation_liveness_counter_scope)
- [ ] wrong_validation_scope_proven
- [ ] user_facing_path_blocked_proven
- [ ] permanent_or_indefinite_brick_proven
- [ ] core_phase_or_many_users_affected_proven

## Steps
1. Pin the in-scope repo at the audited commit (6693d9e4f03a37919a52626de64b1cadf632fd29); `git submodule update --init --recursive`.
2. `forge build` (record solc version).
3. Implement `SecondSwapVestingManagerListVestingPoC.test_ASSISTED_M11_invariant` from source behavior — L1 entry, L2 state flip (named slots /
   balances asserted), L3 outcome (the invariant above). Remove the scaffold guard only when L1–L3 are real.
4. Run: `forge test --match-test test_ASSISTED_M11_invariant -vv` → expect **FAIL** on vulnerable source for the expected reason; capture exact output.
5. Apply the minimal patch (negative control) and re-run → expect **PASS**; restore source.
   - Negative control: Replace the wrong-domain check with the correct scope (e.g. `generationMintCounts[currentGeneration] < maxTokensPerGen` instead of `_tokenIds < maxTokensPerGen`, or the per-user/per-scope counter). Assert the user-facing path works again at and beyond the boundary, with no other change.
6. `forge test` (full suite) → expect existing tests pass, only the PoC fails (the proof).

## On success
- Fill `evidence_bundle.md` (exact source refs, failing output, patch result, suite result, frozen hashes).
- Fill `submission_draft.md` and `reviewer_notes.md` TODOs.
- Re-run `pre_submission_gate.md` items 4–9 → only then may the funnel record advance toward
  READY_FOR_HUMAN_REVIEW, with items 2 (scope) and 3 (duplicate) still PENDING for the human.
