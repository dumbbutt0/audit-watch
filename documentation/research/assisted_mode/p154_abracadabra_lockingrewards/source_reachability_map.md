# P154 — Stage 1 (Mechanism) + Stage 2 (Source Reachability Map)

Target: `audits/abracadabra-2024-03-holdout/contracts/src/staking/LockingMultiRewards.sol`
(baseline md5 `74937ac70403a79dff31bbc8d427e87c`, byte-identical after this phase).

## Stage 1 — Mechanism hypothesis (one sentence)
*Because a lock's boosted reward weight (`bal.locked * lockingBoostMultiplerInBips`) is removed only by the
operator-gated `processExpiredLocks` and **not** automatically at the lock's `unlockTime`, an unprivileged
staker keeps earning boosted (e.g. 3×) reward weight after their lock has expired — over-accruing reward
tokens at honest stakers' expense for the entire window between expiry and processing.*

### Refutation condition (pre-registered)
Refuted if source/runtime shows any of: (a) reward accrual stops or de-boosts automatically at `unlockTime`
regardless of `processExpiredLocks`; (b) the boost is checkpointed out at expiry; (c) no reward
distribution can occur in the post-expiry/pre-process window; (d) a corrected reference (boost dropped at
expiry) yields the **same** payout as the real contract (zero delta).
→ **Not refuted.** Runtime shows a non-zero, zero-sum delta (see runtime_result.md).

## Stage 2 — Production call path

### Entry (unprivileged, value-bearing)
- `stake(uint256 amount, bool lock_) public whenNotPaused` (:150) → `_stakeFor` (:458)
- `lock(uint256 amount) public whenNotPaused` (:155)
- `getRewards() public` (:191) → `_getRewards` (:597) → `rewardToken.safeTransfer(user, amount)` (:637) — **value out**
- `withdrawWithRewards` / `withdraw` (:170-189)

### Caller permissions
- All of the above are **public**, gated only by `whenNotPaused`. **No role/owner/operator check.** Any EOA
  can call them with no privileged setup.

### User-controlled fields
- `amount`, `lock_` (whether to lock). The attacker fully controls both.

### Derived / state fields
- `_balances[user].locked`, `lockedSupply` — set by `_createLock` (:479); a `LockedBalance{amount, unlockTime}`
  is appended with `unlockTime = nextUnlockTime()` (:481, = `nextEpoch()+lockDuration`).
- `balanceOf(user) = unlocked + locked*mult/BIPS` (:239-242); `totalSupply = unlockedSupply +
  lockedSupply*mult/BIPS` (:235-237).
- Reward accrual: `earned = balanceOf(user) * (rewardPerToken - userRewardPerTokenPaid) + rewards[user]`
  (:288-295), where `rewardPerToken` divides by boosted `totalSupply` (:277-286).

### Trusted-role fields (NOT attacker-controlled)
- `notifyRewardAmount` (:361, `onlyOperators`) — distributes rewards.
- `processExpiredLocks` (:397, `onlyOperators`) — the **only** path that moves `locked→unlocked` and thus
  removes the boost (:441-445). There is **no user-callable** function to release an expired lock.

### Guards / modifiers
- `whenNotPaused` on stake/lock; `onlyOperators` on notify/process; `onlyOwner` on addReward/recover.

### The reachability fact
`balanceOf`/`totalSupply` boost on `bal.locked` regardless of whether each lock's `unlockTime` has passed.
After expiry, `bal.locked` stays non-zero until an operator calls `processExpiredLocks`. During that window
the expired locker keeps boosted weight in **both** the numerator (their `earned`) and the denominator
(`totalSupply`), so they capture a disproportionate share of any rewards distributed — at the expense of
honest stakers.

### Can an unprivileged actor influence the critical field through production flow?
**Yes.** A plain EOA calls `stake(amount, true)` (no privileged setup). The boost then persists past
`unlockTime` automatically; the user *cannot even opt out* (no user-side unlock), so the incorrect reward
distribution is structurally the protocol's, not the user's. The only thing the attacker "waits for" is
time + a reward distribution in the post-expiry window — both ordinary production conditions.
