# Reviewer notes — Cred._addCredIdPerAddress (P89-H05)

For the human triager. These notes must argue severity and pre-empt the "is this real / is this just rounding"
objections from source + the executable test. Fill every TODO before treating the package as review-ready.

## Why this severity (Access-control / privileged)
An unprivileged caller can drive a state change intended to be privileged. Severity depends on the downstream consequence: Medium if it causes accounting drift/incorrect state; High if it leads to direct fund loss or a broken core invariant. Final tier mapping is the human's.

TODO — instantiate with the concrete amounts/consequences this PoC proves.

## Why it is NOT dust / rounding
This is a missing trust boundary, not a cosmetic issue: the unauthorized call succeeds outright (a binary auth failure), and the PoC asserts the guarded state actually changed; the negative control (adding the modifier) makes the same call revert.

TODO — cite the actual magnitude from the PoC output.

## Why the impact follows (mechanism)
TODO — explain, anchored to source lines, why the harmed party loses value or is denied funds. For this type,
the invariant is:
> authorization invariant: a state-mutating or value-moving function must reject callers without the required role; an unauthorized EOA/contract call must revert (and leave guarded state unchanged).

## Why the minimal patch proves the root cause
Negative control for this type:
> Add onlyRegistratorOrGovernor modifier. Assert that the attacker contract call reverts. Assert totalDepositsWei unchanged.

TODO — confirm applying it flips the PoC from FAIL to PASS with no other change, isolating the defect.

## High-severity bar for this finding type
High requires proving vault makes incorrect allocation decisions leading to direct fund loss. Medium is proven by unauthorized state mutation causing accounting drift.

## What a triager should run
1. Pinned commit 2465e04364b759c721f1a0aebace69920411f8aa; `git submodule update --init --recursive`; `forge build`.
2. TODO — any RPC/fork setup needed for the harness.
3. Copy `CredAddCredIdPerAddressPoC` into `test/` and run: `forge test --match-test test_P89_H05_invariant -vv` → expect FAIL for the stated reason.
4. (Optional) apply the minimal patch and re-run → expect PASS; restore source.
5. Sanity: `forge test` full suite → expect existing tests pass, only the PoC fails.

## Open items the triager owns (not resolved here)
- Confirm `Cred` and this impact class are in the program's scope.
- Check duplicate / publicly-known status.
- Decide the program severity tier and final platform-specific wording before any submission.
