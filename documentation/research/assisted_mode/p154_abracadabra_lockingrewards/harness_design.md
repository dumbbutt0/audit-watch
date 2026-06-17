# P154 — Stage 4 Harness Design

Location: `audits/abracadabra-2024-03-holdout/pocs/p154/`
File: `test/LockingRewardsBoostAfterExpiry.t.sol` · `foundry.toml` (solc 0.8.23, evm shanghai)

## Contract under test
The **real production** `LockingMultiRewards` (imported via remapping `src/=../../contracts/src/`,
**unmodified**, md5 unchanged). Inherited deps are the real upstream libraries cloned into `lib/`
(forge-std, solmate, solady, OpenZeppelin v4.9.6) and the audit's own `mixins/OperatableV2.sol` +
`libraries/MathLib.sol`. `lib/` is removed after the run (re-clonable via the documented URLs).

## Non-production code (dependencies only)
- `MockERC20` (solmate ERC20 with a `mint`) — the staking + reward token dependencies.
- The test contract is owner+operator of the staking contract (constructor `_owner=address(this)`, then
  `setOperator(this,true)`), used **only** to perform the legitimate operator actions (`addReward`,
  `notifyRewardAmount`, and — in the corrected case — `processExpiredLocks`). The attacker actions
  (`stake`) are performed by ordinary EOAs `A`/`B` via `vm.prank`.

## Corrected reference = real code (no subclass)
There is **no** subclass override of the contract. The "corrected" behavior is the SAME real contract with
the expired lock processed **promptly** at `unlockTime` via the real `processExpiredLocks`. This isolates
the single variable — *processing timing* — and shows that prompt processing drives the over-accrual to
zero. This is a stronger, more faithful reference than a hand-written fix because it uses only production
logic.

## Parameters
boost `MULT=30000` (3×), `REWARDS_DURATION=7d`, `LOCK_DURATION=91d` (= 13 epochs), stake `X=1000e18`,
reward `R=700e18`/epoch. `T0 = 1000 * 7d` (epoch boundary) so reward periods align to full epochs.

## Scenario
1. `A` `stake(X, true)` (locked); `B` `stake(X, false)` (unlocked) → `balanceOf(A)=3X`, `balanceOf(B)=X`,
   `totalSupply=4X`.
2. **Window 1** (lock active): distribute `R` over one epoch, warp to period end.
3. Warp to `unlockTime = nextEpoch(T0)+LOCK_DURATION = T0+98d`. Lock is now expired.
4. **Window 2** in two variants: (a) **unprocessed** — distribute `R` again, no processing; (b)
   **processed** — call `processExpiredLocks([A],[0])` at `unlockTime`, then distribute `R`.

## Tests (4)
- `test_control_boost_legitimate_during_active_lock` — Window 1: assert `A ≈ 3·B` (intended boost). **Matched control / no-bug.**
- `test_mechanism_boost_persists_after_expiry_unprocessed` — Window 2(a): assert `balanceOf(A)` still `3X`
  after expiry and `A ≈ 3·B` for window-2 accrual. **The mechanism.**
- `test_corrected_prompt_processing_removes_overaccrual` — Window 2(b): after prompt processing,
  `balanceOf(A)=X` and `A ≈ B`. **Corrected reference (real code).**
- `test_quantify_overaccrual_window2` — runs both variants from the same `T0`; asserts A's over-accrual
  `> 0` and exactly equals B's loss (zero-sum).

## State/value deltas recorded
Reward `earned()` per user per window (see runtime_result.md). All assertions are exact/`assertApproxEqRel`
at 1e-6 tolerance (only rounding dust differs).
