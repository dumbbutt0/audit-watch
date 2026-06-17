# Human Review Report (DRAFT) — Abracadabra LockingMultiRewards: expired locks retain boosted reward weight

> Status: **valid finding, Low baseline (Medium only under sustained keeper failure)** · `submission_ready=false`
> · `routing_allowed=false` · `human_review_required=true`. Platform-neutral draft for a human to decide
> submit-as-Low / hold-as-QA / reject-as-trusted-keeper-scope. Nothing here is submitted.

## Title
Expired locks keep boosted reward weight until `processExpiredLocks` runs, redistributing reward emissions
from honest stakers to the expired locker.

## Summary
`LockingMultiRewards` gives locked stake a reward-weight multiplier. The boost is removed from reward
accounting **only** by the `onlyOperators` `processExpiredLocks`, **not automatically at the lock's
`unlockTime`**. In the ordinary window between a lock's expiry and the next keeper sweep, the expired locker
keeps earning the boosted share, so reward emissions distributed in that window are **misallocated** — honest
stakers receive a smaller share than they should. This is a **user-to-user reward redistribution**, not a
loss of protocol funds.

## Root cause
`balanceOf(user) = unlocked + locked·multiplier/BIPS` and `totalSupply` count `locked` at the boosted weight
regardless of whether each lock's `unlockTime` has passed. `earned()` derives rewards from `balanceOf`. The
only path that moves `locked → unlocked` (removing the boost) is `processExpiredLocks` (`onlyOperators`).
There is **no automatic de-boost at `unlockTime`** and **no user-callable** way to release an expired lock,
so the boost persists through the post-expiry / pre-sweep gap.

## Affected contract / functions
- Contract: `audits/abracadabra-2024-03-holdout/contracts/src/staking/LockingMultiRewards.sol`
- Functions: `stake`, `lock` (public setup), `balanceOf` / `earned` (`public view`, boosted accounting),
  `getRewards` (value realization), `processExpiredLocks` (`onlyOperators`, sole de-boost),
  `notifyRewardAmount` (operator reward distribution — not attacker-controlled).

## Attack scenario (no privileged role; attacker cannot force keeper downtime)
An ordinary user stakes with `lock=true` to obtain the boosted weight, then simply lets time pass until the
lock's `unlockTime`. Because expiry does not auto-de-boost, during the window before the operator/keeper's
next `processExpiredLocks` sweep the now-expired lock still counts at the multiplier, so the user keeps
accruing an outsized share of any reward emissions in that window and can claim them via `getRewards`. Honest
stakers receive correspondingly less. The user never calls any privileged function; the only "wait" is
ordinary elapsed time (the lock must run to expiry — capital is committed for the lock duration, ~13 weeks).

## Impact
- **Who loses:** honest stakers (their reward share is diluted).
- **Who gains:** the expired-but-unprocessed locker (keeps the boosted share).
- **Type:** zero-sum **reward redistribution / misallocation** among stakers — **no protocol funds are lost.**
- **Permanence:** once the over-accrued rewards are claimed/vested, that window's misallocation is permanent;
  later processing fixes only future windows.
- **Magnitude:** small per gap under normal keeper cadence; scales with reward rate × window length ×
  expired-locked size × multiplier, and grows if the keeper/operator is delayed.

## Proof of Concept summary
Real-contract Foundry PoC (P154): real production `LockingMultiRewards`, production source unchanged, isolated
harness; a corrected reference = the **same real contract** with `processExpiredLocks` run promptly (isolates
the single variable: processing timing) + a matched active-lock control. 4/4 tests pass.

## Expected vs actual
- **Active lock (control):** A ≈ 525e18, B ≈ 175e18 → ~3:1 — intended boost while committed.
- **Actual — expired, unprocessed:** A ≈ 525e18, B ≈ 175e18 → ~3:1 — **bug: boost persists after expiry.**
- **Expected — expired, processed (corrected):** A ≈ 350e18, B ≈ 350e18 → ~1:1 — fair.
- **Delta:** A's over-accrual ≈ B's loss (zero-sum).

## Severity rationale
**Low baseline.** The per-gap misallocation is small under the stated keeper cadence
(`processExpiredLocks` "should be called once a `rewardDuration`"), it is zero-sum, and there is no
protocol-fund loss. **Medium only** if sustained keeper failure / delayed operator processing is considered
in scope — that widens the window (unbounded if never processed) but is **environmental and not
attacker-controllable** (the attacker cannot force keeper downtime). **Not High** (no protocol-fund loss; no
attacker-forced amplification). **Not invalid** (mechanism, reachability, and zero-sum loss are runtime-confirmed).

## Scope caveats
This depends on the program's treatment of the `onlyOperators` keeper. Two honest readings (the report does
**not** decide between them — see scope_decision_memo.md): (1) in-scope user-to-user reward misallocation; or
(2) downgrade/out-of-scope if keeper cadence is an accepted trusted-maintenance assumption.

## Novelty / public-known caveats
`public_known_but_not_duplicate`: no exact duplicate among the awarded C4 2024-03 Abracadabra findings;
`LockingMultiRewards` was publicly audited; the lock-boost + lazy-expiry design is public (Convex/Curve
lineage). The full raw issue set was not exhaustively reviewed, so **clean novelty is not claimed.**

## Recommended mitigation
De-boost at expiry rather than relying on operator timing — e.g., compute reward weight from per-lock
`unlockTime > block.timestamp` so expired locks count at 1×, or add a permissionless function letting any
user (or the locker) process their own expired locks so honest stakers are not dependent on keeper liveness.

## Assumptions and limitations
- Keeper (`Gelato`) normally runs ~each epoch (per contest docs); the baseline window is therefore bounded.
- `lockingBoostMultiplerInBips` materially > BIPS (3× in the PoC; configurable higher).
- Impact proven is reward redistribution only — **no end-to-end protocol-fund loss is claimed.**
