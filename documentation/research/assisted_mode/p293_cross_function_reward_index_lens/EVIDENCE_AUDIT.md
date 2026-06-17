# P293 — EVIDENCE_AUDIT

Per-candidate audit of every Lens-3 firing, the awarded locus, 5 normal updates that did NOT lift, and the 5 key
regressions. "source-backed?" = the cited variable/branch exists verbatim in the contract source.

## `StakingRewards._increaseUserShare` (salty; awarded H-02/H-04) — LENS3_READY / FIRST_DEPOSITOR_ZERO_SUPPLY → READY
- trace path real? The P283 downward trace is empty (callees `ceilDiv/dao/isWhitelisted/modificationCooldown` are
  external/library) — the lens used the SAME-CONTRACT sibling path instead. Correct.
- share mutation real? YES — `user.userShare += uint128(increaseShareAmount)` / `totalShares[poolID] = ... +` (L88-89).
- global index real? YES — `totalRewards[poolID]` read in `ceilDiv(totalRewards[poolID]*increaseShareAmount, existingTotalShares)` and written `+=` (L81-84).
- user snapshot real? YES — `user.virtualRewards += uint128(virtualRewardsToAdd)` (L83); the reward-debt analog.
- ordering/zero-supply real? YES — `if (existingTotalShares != 0)` (L78) conditionally skips the snapshot on the
  first-depositor (zero-supply) edge.
- missing/incorrect snapshot source-backed? YES — first depositor (totalShares==0) gets virtualRewards=0.
- pending formula real? YES — sibling `userRewardForPool() = totalRewards*userShare/totalShares - virtualRewards`
  (L243-251). Resolved via `_l3_sibling_pending`.
- PoC assertion implementable? YES — seed pool rewards, first-deposit at zero supply, second deposit, compare
  claimable to a checkpointed control (see poc_intent record).
- generic staking false lift? NO — anchored to the real reward-debt mechanism.
- hallucinated context? NO — every cited symbol is verbatim source.

## `CollateralAndLiquidity.liquidateUser` (salty) — LENS3_READY / GLOBAL_INDEX_NOT_PAIRED → gate INLINE_GUARD_REFUTED
- The lens fires (the function touches share + reward/index accounting), but the gate's D1 detects an access guard on
  the path and holds it `INLINE_GUARD_REFUTED`. Net: NOT READY, NOT a false positive. This is the intended
  layering — the lens signals, the gate's independent guard analysis fail-closes. Flagged in REPAIR_BACKLOG as a
  lens-precision item (a liquidation entry is a weaker reward-index candidate than a stake entry).

## 5 normal staking/reward updates that did NOT lift (FP controls; from fixtures + corpus)
1. plain `_balances[msg.sender] += a;` — relevance gate → silent (None). Correct.
2. `updateReward(u); balance += a;` (checkpoint-then-mutate) — `LENS3_REFUTED_NORMAL_CHECKPOINT`. Correct.
3. `userRewardPerTokenPaid[u] = rewardPerToken; balance += a;` (atomic init) — refuted. Correct.
4. salty `_decreaseUserShare` — symmetric to increase, snapshot removed proportionally; no zero-supply skip → not a
   FIRST_DEPOSITOR lift; held. Correct.
5. all panoptic/silo/revert-lend(control)/hybra functions — 0 firings (no staking/reward-debt subsystem). Correct.

## Regressions (all via the same chain; unchanged)
- kelp `LRTDepositPool.getRsETHAmountToMint` — READY via D4.6 oracle lens (unchanged; not a reward-index match).
- blackhole `RewardsDistributor.claim_many` — READY via D4.3 sibling parity (unchanged).
- blackhole `L2Governor.execute` — READY (state-machine; unchanged).
- ecg `SurplusGuildMinter.stake` — READY via P289 loss_on_stake lens (unchanged; span-local).
- salty `Pools.deposit` — `NEEDS_INTEGRATION_DEVIATION_EVIDENCE` (P291 EXTERNAL_INTEGRATION precision held).
All five carry pre-existing `root_cause`/`runner_up_mechanism`, so the P293 fill-if-missing is a no-op for them.
