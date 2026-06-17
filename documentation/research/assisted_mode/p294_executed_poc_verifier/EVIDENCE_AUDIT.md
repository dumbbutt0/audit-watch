# P294 — EVIDENCE_AUDIT

Per-record audit. "real run?" = a captured forge log with [PASS]/[FAIL] for the named test under
`output/poc_validation/raw/p294_*`.

## blackhole-M-04-claim_many — confirmed_by_execution (awarded)
- real run? YES — `test_claim_many_misroutes_to_ownerOf_PASS_SUPPORTED` [PASS] (re-runs live, 3/3 in the suite).
- L1? attacker/EOA path calls the real claim_many control-flow (verbatim from RewardsDistributor). YES.
- L2? named before/after recipient balances asserted to diverge (avmHolder vs originalOwner). YES.
- L3? outcome asserted (reward stranded at ownerOf; original owner 0). YES.
- polarity correct? exploit test (not control/reference). YES. → confirmed is honest (awarded locus, proven).

## salty-H-increaseUserShare-first-depositor — confirmed_by_execution (P293-recovered, net-new PoC)
- real run? YES — `test_first_depositor_captures_pool_rewards_PASS_SUPPORTED` [PASS].
- source faithful? the virtualRewards control-flow is copied verbatim (the `if(existingTotalShares!=0)` guard, the
  ceilDiv snapshot, and `userRewardForPool = global*share/total - virtualRewards`). Only SALT transfer is mocked.
- L1? attacker first-deposits at totalShares==0 (vm.prank). YES.
- L2? named virtualRewards before/after — stays 0 because the snapshot is skipped. YES (the state flip is the
  ABSENCE of the snapshot, asserted).
- L3? `userRewardForPool == 100e18` unearned vs a checkpointed control owed 0, asserted. YES.
- exploit real, not a tautology? the control contract proves the corrected checkpoint yields 0 — the divergence is
  the bug, not a test artifact. YES.

## salty-Pools-deposit-callback — refuted_by_execution (false hypothesis; the FP guard)
- real run? YES — `test_callback_reentrancy_is_refuted_PASS_REFUTED` [PASS], but it asserts SAFETY (userDeposits
  uncorrupted; deposit is nonReentrant).
- declared exploit test? NONE (manifest exploit_tests=[]). So even though forge passes, attacker_verified=False.
- genuine refutation, not a setup error? YES — the standard-deposit control also passes; the refutation test
  exercises the claimed callback path and shows no corruption.

## Cross-cutting guards
- any confirmation WITHOUT a real executed PASS? NONE (guard_report `every_confirmation_has_a_real_log=true`).
- anti-fabrication (synthetic): a manifest naming an exploit test that fails → refuted_by_execution (test proves it).
- setup_only (synthetic): an exploit test that passes but lacks L2 → setup_only, not confirmed (test proves it).
- confirmed-false-positive count = 0 (every confirmed record is an awarded locus).
