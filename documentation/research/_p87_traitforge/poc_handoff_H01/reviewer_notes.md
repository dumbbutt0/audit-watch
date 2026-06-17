# Reviewer notes — TraitForgeNft.mintWithBudget (P87-H01)

For the human triager. These notes must argue severity and pre-empt the "is this real / is this just rounding"
objections from source + the executable test. Fill every TODO before treating the package as review-ready.

## Why this severity (Reward-accrual / state-lifecycle)
A validly-participating user permanently (or until an abnormal action) stops earning or cannot claim owed reward through ordinary protocol use. High when the loss is permanent/unrecoverable-by-normal-action and quantified; Medium when accrual is demonstrably halted without a permanence/quantified-loss proof. A bounded mismatch that self-corrects on the next normal claim is NOT this class (-> Low via the severity gate).

TODO — instantiate with the concrete amounts/consequences this PoC proves.

## Why it is NOT dust / rounding
This is a stuck/unrecoverable reward-state, not a transient rounding skew: the flag/checkpoint is provably never reset on the valid-state path (read the slot), the victim's accrual is 0 (or strictly below the recoverable baseline) with no normal recovery, and the one-line reset patch flips the outcome cleanly.

TODO — cite the actual magnitude from the PoC output.

## Why the impact follows (mechanism)
TODO — explain, anchored to source lines, why the harmed party loses value or is denied funds. For this type,
the invariant is:
> reward-lifecycle invariant: a validly-participating user must keep accruing; a dirty/stale flag or per-user reward checkpoint (reward debt / index) must be reset/advanced when the user returns to a valid state; reward owed must remain claimable. Set-but-never-reset breaks this permanently.

## Why the minimal patch proves the root cause
Negative control for this type:
> Reset the dirty/stale flag to false (or advance the per-user reward checkpoint / clear the reward debt) on the recovery path (e.g. inside transferToUnoccupiedPlot / on re-entry), and set lastRewardDate to block.timestamp. Assert the participant resumes accruing the recoverable baseline and can claim owed reward, with no other change.

TODO — confirm applying it flips the PoC from FAIL to PASS with no other change, isolating the defect.

## High-severity bar for this finding type
High requires proving the reward loss is permanent / not recoverable by a normal later action (only an abnormal action such as unstake+restake recovers it) AND quantifying the lost reward or the blocked claim path. Medium is proven by showing accrual is halted and the flag/checkpoint is not reset, without a permanence/quantified-loss proof. NOTE: a bounded/lazy reward mismatch that self-corrects on the next normal claim is NOT this class -> route to Low via the severity gate (P86).

## What a triager should run
1. Pinned commit 72077d0a2a86d16530020afa647ffbfe64fdddb1; `git submodule update --init --recursive`; `forge build`.
2. TODO — any RPC/fork setup needed for the harness.
3. Copy `TraitForgeNftMintWithBudgetPoC` into `test/` and run: `forge test --match-test test_P87_H01_invariant -vv` → expect FAIL for the stated reason.
4. (Optional) apply the minimal patch and re-run → expect PASS; restore source.
5. Sanity: `forge test` full suite → expect existing tests pass, only the PoC fails.

## Open items the triager owns (not resolved here)
- Confirm `TraitForgeNft` and this impact class are in the program's scope.
- Check duplicate / publicly-known status.
- Decide the program severity tier and final platform-specific wording before any submission.
