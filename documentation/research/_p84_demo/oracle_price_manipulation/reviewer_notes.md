# Reviewer notes — LendingPool.getCollateralValue (EX-ORA-01)

For the human triager. These notes must argue severity and pre-empt the "is this real / is this just rounding"
objections from source + the executable test. Fill every TODO before treating the package as review-ready.

## Why this severity (Oracle / price manipulation)
An attacker can manipulate the consumed price within a single transaction to mis-size a value decision. Medium if price inflation + balance/decision distortion is shown; High if the overstatement magnitude and attacker profit (or protocol loss) are quantified. Human sets the final tier.

TODO — instantiate with the concrete amounts/consequences this PoC proves.

## Why it is NOT dust / rounding
The manipulation is attacker-controlled and bounded only by available capital/flash-loan size, not a rounding artifact; the PoC quantifies the price move and the resulting decision delta, and the negative control (TWAP/bound) removes the manipulability.

TODO — cite the actual magnitude from the PoC output.

## Why the impact follows (mechanism)
TODO — explain, anchored to source lines, why the harmed party loses value or is denied funds. For this type,
the invariant is:
> price-integrity invariant: a value/mint/liquidation decision must not be derivable from an instantaneously manipulable price (spot slot0 / single-sided liquidity); a flash-loan-sized swap must not move the consumed price enough to change the protocol's decision.

## Why the minimal patch proves the root cause
Negative control for this type:
> TODO

TODO — confirm applying it flips the PoC from FAIL to PASS with no other change, isolating the defect.

## High-severity bar for this finding type
TODO

## What a triager should run
1. Pinned commit TODO — pin the audited commit + submodules; `git submodule update --init --recursive`; `forge build`.
2. TODO — any RPC/fork setup needed for the harness.
3. Copy `LendingPoolGetCollateralValuePoC` into `test/` and run: `forge test --match-test test_EX_ORA_01_invariant -vv` → expect FAIL for the stated reason.
4. (Optional) apply the minimal patch and re-run → expect PASS; restore source.
5. Sanity: `forge test` full suite → expect existing tests pass, only the PoC fails.

## Open items the triager owns (not resolved here)
- Confirm `LendingPool` and this impact class are in the program's scope.
- Check duplicate / publicly-known status.
- Decide the program severity tier and final platform-specific wording before any submission.
