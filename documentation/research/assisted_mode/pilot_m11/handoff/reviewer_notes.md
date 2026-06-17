# Reviewer notes — SecondSwap_VestingManager.listVesting (ASSISTED-M11)

For the human triager. These notes must argue severity and pre-empt the "is this real / is this just rounding"
objections from source + the executable test. Fill every TODO before treating the package as review-ready.

## Why this severity (Validation-liveness / counter-scope)
A user-facing path (mint/claim/withdraw/settle/forge/buy/sell) is materially blocked by an incorrect validation scope. This is a LIVENESS / denial-of-asset-movement class — it must not be under-rated below Medium when source-backed (P88). High when the brick is permanent/indefinite, affects a core lifecycle phase or many/all users, and recovers only via privileged intervention / migration / upgrade.

TODO — instantiate with the concrete amounts/consequences this PoC proves.

## Why it is NOT dust / rounding
This is not a bounded/lazy accounting skew: the path is provably unusable for normal users (0 minted / revert / full refund), the brick is permanent (no setter, counter never reset), and the one-line scope-fix restores it cleanly. It denies intended asset movement / mint rights, not a rounding remainder.

TODO — cite the actual magnitude from the PoC output.

## Why the impact follows (mechanism)
TODO — explain, anchored to source lines, why the harmed party loses value or is denied funds. For this type,
the invariant is:
> validation-domain invariant: a capacity/eligibility check must use the CORRECT scope (per-generation / per-user / per-listing), not a global or wrong-domain counter; a user-facing mint/claim/withdraw/settle/forge/buy/sell path must remain usable while the correct-scope condition holds. A wrong-scope check that permanently blocks the path is a liveness failure.

## Why the minimal patch proves the root cause
Negative control for this type:
> Replace the wrong-domain check with the correct scope (e.g. `generationMintCounts[currentGeneration] < maxTokensPerGen` instead of `_tokenIds < maxTokensPerGen`, or the per-user/per-scope counter). Assert the user-facing path works again at and beyond the boundary, with no other change.

TODO — confirm applying it flips the PoC from FAIL to PASS with no other change, isolating the defect.

## High-severity bar for this finding type
High requires proving the wrong-scope validation PERMANENTLY/indefinitely bricks a CORE user-facing path for many/all users with no self-recovery (recovers only via privileged intervention / migration / upgrade). Medium is proven by showing the validation scope is wrong and a user-facing path is materially blocked, without a permanence + core/all-users proof. This is a LIVENESS / denial-of-asset-movement class -> per the P88 severity gate it must NOT be under-rated below Medium when source-backed; it is NOT a bounded/lazy accounting issue.

## What a triager should run
1. Pinned commit 6693d9e4f03a37919a52626de64b1cadf632fd29; `git submodule update --init --recursive`; `forge build`.
2. TODO — any RPC/fork setup needed for the harness.
3. Copy `SecondSwapVestingManagerListVestingPoC` into `test/` and run: `forge test --match-test test_ASSISTED_M11_invariant -vv` → expect FAIL for the stated reason.
4. (Optional) apply the minimal patch and re-run → expect PASS; restore source.
5. Sanity: `forge test` full suite → expect existing tests pass, only the PoC fails.

## Open items the triager owns (not resolved here)
- Confirm `SecondSwap_VestingManager` and this impact class are in the program's scope.
- Check duplicate / publicly-known status.
- Decide the program severity tier and final platform-specific wording before any submission.
