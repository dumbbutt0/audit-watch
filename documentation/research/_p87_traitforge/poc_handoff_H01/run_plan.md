# PoC run plan — TraitForgeNft.mintWithBudget (P87-H01) — Reward-accrual / state-lifecycle

Reject-first reproduction plan. The bundle is NOT reproduced until every step below is done and the test fails
on vulnerable source for the expected reason.

## Invariant under test
> reward-lifecycle invariant: a validly-participating user must keep accruing; a dirty/stale flag or per-user reward checkpoint (reward debt / index) must be reset/advanced when the user returns to a valid state; reward owed must remain claimable. Set-but-never-reset breaks this permanently.

## Setup
Put a user in a valid reward-earning state; trigger the path that sets the dirty/stale flag or skips the checkpoint update; restore the valid state (re-enter / move to a valid slot / re-lock); read the flag/checkpoint storage slot before/after to show it is NOT reset; then show the user accrues 0 / cannot claim owed reward and that no normal later action recovers it.

## L3 requirements for this finding type (reward_accrual_state_lifecycle)
- [ ] reward_accrual_halted_proven
- [ ] state_flag_or_checkpoint_not_reset_proven
- [ ] permanent_or_unrecoverable_reward_loss_proven
- [ ] loss_or_blocked_path_quantified

## Steps
1. Pin the in-scope repo at the audited commit (72077d0a2a86d16530020afa647ffbfe64fdddb1); `git submodule update --init --recursive`.
2. `forge build` (record solc version).
3. Implement `TraitForgeNftMintWithBudgetPoC.test_P87_H01_invariant` from source behavior — L1 entry, L2 state flip (named slots /
   balances asserted), L3 outcome (the invariant above). Remove the scaffold guard only when L1–L3 are real.
4. Run: `forge test --match-test test_P87_H01_invariant -vv` → expect **FAIL** on vulnerable source for the expected reason; capture exact output.
5. Apply the minimal patch (negative control) and re-run → expect **PASS**; restore source.
   - Negative control: Reset the dirty/stale flag to false (or advance the per-user reward checkpoint / clear the reward debt) on the recovery path (e.g. inside transferToUnoccupiedPlot / on re-entry), and set lastRewardDate to block.timestamp. Assert the participant resumes accruing the recoverable baseline and can claim owed reward, with no other change.
6. `forge test` (full suite) → expect existing tests pass, only the PoC fails (the proof).

## On success
- Fill `evidence_bundle.md` (exact source refs, failing output, patch result, suite result, frozen hashes).
- Fill `submission_draft.md` and `reviewer_notes.md` TODOs.
- Re-run `pre_submission_gate.md` items 4–9 → only then may the funnel record advance toward
  READY_FOR_HUMAN_REVIEW, with items 2 (scope) and 3 (duplicate) still PENDING for the human.
