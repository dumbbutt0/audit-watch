# Reviewer notes — LandManager.transferToUnoccupiedPlot (P85-H05)

For the human triager. These notes must argue severity and pre-empt the "is this real / is this just rounding"
objections from source + the executable test. Fill every TODO before treating the package as review-ready.

## Why this severity (Shared-accounting / fee-routing)
Two fund-impacting consequences reachable permissionlessly: (1) direct misallocation of other sharers' accrued value to a third party; (2) denial of vested funds once the diverted amount is material (later settlement reverts -> principal-class funds locked). Either is serious; together and order-dependent, this is High-band pending program-tier mapping by a human.

TODO — instantiate with the concrete amounts/consequences this PoC proves.

## Why it is NOT dust / rounding
The affected amount is the other sharers' entire accrued value on the shared position, not a rounding remainder, and scales with volume and number of sharers; the second consequence is a hard revert (funds locked), not an off-by-wei discrepancy; the minimal patch flips the outcome cleanly.

TODO — cite the actual magnitude from the PoC output.

## Why the impact follows (mechanism)
TODO — explain, anchored to source lines, why the harmed party loses value or is denied funds. For this type,
the invariant is:
> order-independence / value-conservation: a user's claim proceeds must be independent of whether another sharer of the same pooled position acted first; total distributed must conserve each sharer's entitlement.

## Why the minimal patch proves the root cause
Negative control for this type:
> Collect only the per-claim amounts the caller is owed (e.g. collect(uint128(amount0), uint128(amount1)) instead of collect(max, max)), or advance each internal share's fee checkpoint, so other users' fees stay in the position. Assert the later claim pays the same as the order-independent baseline and does not revert.

TODO — confirm applying it flips the PoC from FAIL to PASS with no other change, isolating the defect.

## High-severity bar for this finding type
High requires proving that a non-first claimant either cannot withdraw their vested position (claim reverts -> funds locked) or is paid strictly less than the order-independent baseline, AND that the missing value is diverted to a third party. Medium is proven by showing the order-independence invariant is broken and fees are diverted, without a quantified principal-class loss.

## What a triager should run
1. Pinned commit e9056afd7dbdc3b2c6a25602231af87da6da4bc7; `git submodule update --init --recursive`; `forge build`.
2. TODO — any RPC/fork setup needed for the harness.
3. Copy `LandManagerTransferToUnoccupiedPlotPoC` into `test/` and run: `forge test --match-test test_P85_H05_invariant -vv` → expect FAIL for the stated reason.
4. (Optional) apply the minimal patch and re-run → expect PASS; restore source.
5. Sanity: `forge test` full suite → expect existing tests pass, only the PoC fails.

## Open items the triager owns (not resolved here)
- Confirm `LandManager` and this impact class are in the program's scope.
- Check duplicate / publicly-known status.
- Decide the program severity tier and final platform-specific wording before any submission.
