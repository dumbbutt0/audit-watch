# PoC run plan — LandManager.transferToUnoccupiedPlot (P85-H05) — Shared-accounting / fee-routing

Reject-first reproduction plan. The bundle is NOT reproduced until every step below is done and the test fails
on vulnerable source for the expected reason.

## Invariant under test
> order-independence / value-conservation: a user's claim proceeds must be independent of whether another sharer of the same pooled position acted first; total distributed must conserve each sharer's entitlement.

## Setup
Set up >=2 users holding internal shares of ONE shared position; accrue fees via realistic trading; compare a user's payout claiming first vs claiming after another user using vm.snapshot/vm.revertTo at the same unlock and price.

## L3 requirements for this finding type (shared_position_fee_routing)
- [ ] order_independence_invariant_broken
- [ ] fee_diversion_to_third_party_proven
- [ ] later_claim_revert_or_underpay_proven
- [ ] loss_magnitude_quantified

## Steps
1. Pin the in-scope repo at the audited commit (e9056afd7dbdc3b2c6a25602231af87da6da4bc7); `git submodule update --init --recursive`.
2. `forge build` (record solc version).
3. Implement `LandManagerTransferToUnoccupiedPlotPoC.test_P85_H05_invariant` from source behavior — L1 entry, L2 state flip (named slots /
   balances asserted), L3 outcome (the invariant above). Remove the scaffold guard only when L1–L3 are real.
4. Run: `forge test --match-test test_P85_H05_invariant -vv` → expect **FAIL** on vulnerable source for the expected reason; capture exact output.
5. Apply the minimal patch (negative control) and re-run → expect **PASS**; restore source.
   - Negative control: Collect only the per-claim amounts the caller is owed (e.g. collect(uint128(amount0), uint128(amount1)) instead of collect(max, max)), or advance each internal share's fee checkpoint, so other users' fees stay in the position. Assert the later claim pays the same as the order-independent baseline and does not revert.
6. `forge test` (full suite) → expect existing tests pass, only the PoC fails (the proof).

## On success
- Fill `evidence_bundle.md` (exact source refs, failing output, patch result, suite result, frozen hashes).
- Fill `submission_draft.md` and `reviewer_notes.md` TODOs.
- Re-run `pre_submission_gate.md` items 4–9 → only then may the funnel record advance toward
  READY_FOR_HUMAN_REVIEW, with items 2 (scope) and 3 (duplicate) still PENDING for the human.
