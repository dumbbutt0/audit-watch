# PoC run plan — LendingPool.getCollateralValue (EX-ORA-01) — Oracle / price manipulation

Reject-first reproduction plan. The bundle is NOT reproduced until every step below is done and the test fails
on vulnerable source for the expected reason.

## Invariant under test
> price-integrity invariant: a value/mint/liquidation decision must not be derivable from an instantaneously manipulable price (spot slot0 / single-sided liquidity); a flash-loan-sized swap must not move the consumed price enough to change the protocol's decision.

## Setup
Manipulate the consumed price source within one transaction (large swap / single-sided liquidity / flash loan), then call the function that reads it; assert the inflated/deflated price changed the protocol's computed amount or decision, and quantify the resulting overstatement/attacker profit for High.

## L3 requirements for this finding type (oracle_slot0_manipulation)
- [ ] oracle_price_inflated_proven
- [ ] balance_overstatement_shown
- [ ] overstatement_magnitude_quantified
- [ ] attacker_profit_quantified

## Steps
1. Pin the in-scope repo at the audited commit (TODO — pin the audited commit + submodules); `git submodule update --init --recursive`.
2. `forge build` (record solc version).
3. Implement `LendingPoolGetCollateralValuePoC.test_EX_ORA_01_invariant` from source behavior — L1 entry, L2 state flip (named slots /
   balances asserted), L3 outcome (the invariant above). Remove the scaffold guard only when L1–L3 are real.
4. Run: `forge test --match-test test_EX_ORA_01_invariant -vv` → expect **FAIL** on vulnerable source for the expected reason; capture exact output.
5. Apply the minimal patch (negative control) and re-run → expect **PASS**; restore source.
   - Negative control: TODO
6. `forge test` (full suite) → expect existing tests pass, only the PoC fails (the proof).

## On success
- Fill `evidence_bundle.md` (exact source refs, failing output, patch result, suite result, frozen hashes).
- Fill `submission_draft.md` and `reviewer_notes.md` TODOs.
- Re-run `pre_submission_gate.md` items 4–9 → only then may the funnel record advance toward
  READY_FOR_HUMAN_REVIEW, with items 2 (scope) and 3 (duplicate) still PENDING for the human.
