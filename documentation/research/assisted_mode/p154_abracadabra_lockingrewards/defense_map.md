# P154 — Stage 3 Defense Map

Each candidate defense is classified vs the post-expiry boost-retention mechanism:
`blocks_candidate` / `partially_covers_candidate` / `irrelevant` / `unknown`.

| Defense | Where | Classification | Reasoning |
|---|---|---|---|
| `whenNotPaused` on stake/lock | :150,:155 | irrelevant | Only blocks staking while paused; the mechanism plays out on already-staked locks. |
| `onlyOperators` on `notifyRewardAmount` | :361 | irrelevant | The attacker does not need to distribute rewards; they ride whatever rewards the operator distributes. |
| `onlyOperators` on `processExpiredLocks` | :397 | **enables, not blocks** | This is the *only* de-boost path, and it is operator-gated. The user cannot self-remediate; the boost persists until the operator acts. This gate is what makes the mechanism reachable+structural rather than user-fixable. |
| Lock time-commitment (no early user withdraw of locked) | :170-184 (withdraw only touches `unlocked`) | partially_covers_candidate | Prevents "lock → instantly leave" (the boost is genuinely committed *while active*). It does **not** cover the *post-expiry* window, which is the mechanism. |
| Reward checkpointing (`_updateRewardsForUser` before state changes) | :160,:175,:402,:467 | partially_covers_candidate | Correctly snapshots accrued rewards at each interaction, so there is no double-count. But it snapshots at the *boosted* balance during the post-expiry window, i.e. it faithfully books the *over-accrual* rather than preventing it. |
| Σ balanceOf == totalSupply invariant | :235-242 | blocks a *different* class | Guarantees no user can earn >100% of rewards in aggregate (refutes the naive "infinite reward" class). It does **not** block redistribution *between* users — the expired locker's extra share is exactly the honest stakers' loss (zero-sum). |
| Reward-lock vesting (`_getRewards` locks claimed rewards for an epoch) | :597-657 | irrelevant | Affects *when* rewards are paid out, not *how much* each user accrues. The over-accrual is in `earned`/`rewards`, upstream of vesting. |
| NatSpec "should be called once a `rewardDuration`" | :396 | partially_covers (operational) | An off-chain expectation, not an on-chain guard. Bounds the *typical* loss window to ~1 epoch but enforces nothing; a negligent/absent operator makes the window unbounded. This is the crux of the severity/scope question routed to human review. |

## Net
No on-chain defense **blocks** the mechanism. The lock time-commitment and reward checkpointing each cover
adjacent behaviors (pre-expiry boost, no double-count) but not the post-expiry window. The Σ=totalSupply
invariant rules out the naive over-100% class but not the user-to-user redistribution that this mechanism
produces. The only de-boost path is operator-gated, which the attacker cannot invoke and which the protocol
*expects* (but does not enforce) to run promptly.
