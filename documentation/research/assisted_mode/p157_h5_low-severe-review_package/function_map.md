# Function Map

Contract: `audits/abracadabra-2024-03-holdout/contracts/src/staking/LockingMultiRewards.sol`

| Role | Function | Permission | Why it matters |
|---|---|---|---|
| User entrypoint (setup) | `stake` / `lock` | `public`, `whenNotPaused` | Unprivileged way to obtain the boosted reward weight; attacker fully controls `amount` and `lock_`. |
| Critical accounting | `balanceOf` | `public view` (:239) | `unlocked + locked·multiplier/BIPS` — counts the locked balance at the multiplier **regardless of expiry**. |
| Critical accounting | `earned` | `public view` (:288) | Computes rewards from `balanceOf(user)`, so the boosted (and post-expiry-retained) weight flows straight into reward share. |
| Value realization | `getRewards` | `public`, `whenNotPaused` (:191) | Path the user uses to claim the over-accrued rewards (`_getRewards` → `rewardToken.safeTransfer`). |
| De-boost (sole) | `processExpiredLocks` | `onlyOperators` (:397) | The **only** path that moves `locked → unlocked` and removes the boost. No auto de-boost at `unlockTime`; no user-callable equivalent → the boost persists until the operator/keeper acts. |
| Operator distribution | `notifyRewardAmount` | `onlyOperators` (:361) | Distributes reward emissions. **Not attacker-controlled** — the attacker only rides whatever the operator distributes during the gap. |

Key fact: every accounting input (`balanceOf`/`earned`) uses `locked` at the boost multiplier with **no
per-lock expiry check**; the corrective control (`processExpiredLocks`) is operator-gated, which is exactly
why an honest staker cannot self-protect and the expired locker keeps the boost.
