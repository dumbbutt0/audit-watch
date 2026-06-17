# P295 — EVIDENCE_AUDIT

## Each confirmed locus = a real forge exploit PASS (L1+L2+L3) mapped to a true awarded finding
| locus | audit | awarded id | poc dir | exploit test (real PASS) |
|---|---|---|---|---|
| RewardsDistributor.claim_many | blackhole | M-04 | pocs/p286 | test_claim_many_misroutes_to_ownerOf_PASS_SUPPORTED |
| StakingRewards._increaseUserShare | salty | H-02/H-04 | pocs/p294/salty_increaseUserShare | test_first_depositor_captures_pool_rewards_PASS_SUPPORTED |
| LRTDepositPool.getRsETHAmountToMint | kelp | H-01 | pocs/p287/kelp/getRsETHAmountToMint | test_stale_price_silently_misvalues_mint_PASS_SUPPORTED |
| L2Governor.execute | blackhole | L2Gov | pocs/p281 | test_state_machine_defeated_proposal_executes_PASS_SUPPORTED |
| SurplusGuildMinter.stake | ecg | H-04 | pocs/p295/ecg_stake | test_prior_block_loss_slashes_new_stake_PASS_SUPPORTED (NEW this phase) |

For each: the verifier re-runs forge and requires [PASS] of the named exploit test + L1 (attacker prank entry) +
L2 (named before/after state flip) + L3 (outcome assert). Backed by a captured log under output/poc_validation/raw/.

## Surfacing claims trace to read-only artifacts
recall_of_surfaced per locus is read from the audit's `reveal_score.json` (`surfaced` field) or beanstalk
`ground_truth.jsonl` (accepted = system finding matched). The harness never writes these.

## No confirmed false positive
- The salty `Pools.deposit` refutation control runs through the same verifier → `refuted_by_execution`,
  attacker_verified=False → not counted as confirmed. `confirmed_false_positive_count = 0`.
- Every confirmed record maps to an awarded id AND has a real passing exploit run + log
  (guard_report `every_confirmed_has_real_log`).

## Climb PoC faithfulness (ecg H-04)
The `SurplusGuildMinter.stake` model copies the incomplete-guard shape: `require(lastGaugeLoss != block.timestamp)`
(same-block only) WITHOUT checkpointing `user.lastGaugeLoss`; exit slashes when `lastGaugeLoss != user.lastGaugeLoss`.
Exploit: loss at block T, stake at T+1 (passes guard, user index uninitialized = 0) → exit slashes the new stake for
the prior loss (100e18 → 0). Control checkpoints the user index → not slashed (keeps 100e18). The divergence is the
bug, proven by the control, not a test artifact.
