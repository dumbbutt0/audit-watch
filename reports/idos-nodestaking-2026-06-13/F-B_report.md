# Reward withdrawals can consume staker principal due to missing reward reserve accounting

**Component:** `src/IDOSNodeStaking.sol`
**Target:** idOS Network — HackenProof bug bounty (Smart Contracts) — `IDOSNodeStaking`
**Category:** Business Logic Error — stealing / loss of funds; behavior differs from the documented business
description (rewards should not affect principal).

**Chain / deployment:** Arbitrum One (chainId 42161)
- `IDOSNodeStaking` — `0x6132F2EE66deC6bdf416BDA9588D663EaCeec337`
- `IDOSToken` — `0x68731d6F14B827bBCfFbEBb62b19Daa18de1d79c`

**Source commit:** `idos-network/contracts` @ `ebbae56b3bf3598dc9794032dd3df37c772cfe8d` (master)
**Compiler:** `^0.8.27` (validated with solc 0.8.35)

---

## Severity: High

**CVSS v3.1:** `AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H` — **7.4 (High)**

The affected asset is **user principal**. A permissionless reward withdrawal can reduce the contract's token
balance below the principal it custodies, after which later `withdrawUnstaked()` callers cannot recover their
funds from the contract's balance. This is loss of user funds, not a cosmetic accounting discrepancy, and it
violates the protocol's documented invariant that rewards are claimed without affecting principal.

**The code defect is unconditional; the loss *realization* is conditional on reward underfunding.** It is rated
High (not Critical) because realization depends on the reward-funding posture / rate configuration — but no
on-chain mechanism enforces or restores that posture, and the live deployment carries only a ~2% reward buffer
over the principal it holds.

---

## Summary

`IDOSNodeStaking` custodies staker principal and pays epoch rewards from **one and the same** `idosToken`
balance. Reward accrual is driven by an owner-set per-epoch rate and grows automatically every epoch; it is
**not** bounded by, reconciled against, or backed by any funded reward reserve. Because reward payouts and
principal withdrawals draw on the same pot with no reservation and no solvency check:

> The contract accrues claimable rewards independently of funded reward reserves, but pays those rewards from
> the same balance that backs principal. Therefore, whenever cumulative claimable rewards exceed externally
> supplied reward funding, permissionless reward claims consume principal and create a first-come-first-served
> loss race among unstakers.

The earliest claimers and unstakers are made whole out of other users' principal; the last unstaker(s) cannot
withdraw their principal from the contract's balance — it is unavailable and economically lost unless the
contract is externally recapitalized.

---

## The violated invariant

A principal-custody staking contract should maintain, at all times:

```
idosToken.balanceOf(this) >= (all principal-denominated liabilities)
                          =  active stake
                           + queued (pending) unstakes
                           + any slashed stake that remains withdrawable by the owner/protocol
```

`IDOSNodeStaking` never enforces this. Reward withdrawals transfer tokens out of the same balance with no check
that the inequality still holds afterwards, so a reward claim can push the balance below total principal owed —
and the directly harmed parties are the active/queued stakers (e.g. the last user to `withdrawUnstaked`) whose
own principal becomes unavailable.

This contradicts the protocol's documented model. Nethermind's audit of this contract
(`NM0731-FINAL_IDOS.pdf`, System Overview §4.3 *Unstaking and Withdrawals*) states, verbatim:

> "Claiming Rewards: Distinct from principal withdrawals, accrued yield can be claimed at any time via the
> `withdrawReward()` function **without affecting the principal stake**."

The code does not enforce that property.

---

## Affected code

All reward flows and all principal flows move the **same** `idosToken` at the **same** contract balance, and
there is **no** function to deposit, account for, or reserve reward funding — `setEpochReward` only writes a
*rate* into a checkpoint history, it does not move or earmark any tokens.

```
src/IDOSNodeStaking.sol
  L119  stake()              idosToken.safeTransferFrom(user, address(this), amount);   // principal IN
  L185  withdrawUnstaked()   idosToken.safeTransfer(msg.sender, withdrawableAmount);    // principal OUT
  L264  setEpochReward()     epochRewardHistory.push(currentEpoch(), newReward);        // sets a NUMBER only
  L280  withdrawReward()     idosToken.safeTransfer(msg.sender, withdrawableAmount);    // reward OUT (same balance)
```

`withdrawReward` (L272–283) — no solvency guard before the transfer:

```solidity
function withdrawReward() external nonReentrant whenNotPaused returns (uint256 withdrawableAmount) {
    withdrawableAmount = createEpochCheckpoint(msg.sender);
    require(withdrawableAmount > 0, NoWithdrawableRewards());
    (, uint256 prev) = rewardWithdrawalsByUser.tryGet(msg.sender);
    rewardWithdrawalsByUser.set(msg.sender, prev + withdrawableAmount);
    idosToken.safeTransfer(msg.sender, withdrawableAmount);   // <-- paid from the shared balance, no reserve check
    emit RewardWithdraw(msg.sender, withdrawableAmount);
}
```

Reward accrual (`withdrawableReward`, L230–247) adds `epochReward` for every elapsed epoch regardless of whether
that reward was ever funded:

```solidity
for (uint48 i = checkpoint.epoch; i < currentEpoch(); i++) {
    uint256 epochReward = epochRewardHistory.upperLookup(i);
    ...
    rewardAcc += (userStakeAcc * epochReward) / totalStakeAcc;   // accrues whether or not it is funded
}
```

---

## Root cause

1. **No reward reserve / no funding segregation.** Reward tokens and principal tokens are indistinguishable —
   both are just `idosToken.balanceOf(this)`. There is no reward-reserve accumulator and no deposit/funding
   entry point. Reward funding (if any) is a manual, untracked transfer; reward accrual is automatic and
   unbounded.
2. **No solvency guard on payout.** `withdrawReward` transfers as long as *any* balance remains; it never
   verifies that principal liabilities remain fully backed afterwards.

---

## Preconditions

- Cumulative claimable reward obligations exceed externally supplied reward funding (`balance − principal < 0`
  once rewards are claimed). Because reward funding is manual and untracked while reward accrual is automatic,
  the contract has no on-chain mechanism to detect or prevent underfunding.
- On the live deployment, the buffer absorbing this is small — see the measured posture below (~2% of
  principal).

**Once the contract is underfunded relative to accrued rewards, the loss path is permissionless:** reward
claiming (`withdrawReward`), unstaking (`unstake`), and withdrawal (`withdrawUnstaked`) require no privileged
role. (Setting the reward *rate* is owner-controlled, but that is normal protocol operation and is only used in
the fork PoC as a deterministic accelerator — the local PoC reaches the same loss with no owner action at all.)

---

## Live funding posture (measured on an Arbitrum One fork, epoch 144)

| Quantity | Value (IDOS) |
|---|---|
| `IDOSToken.balanceOf(staking)` | 26,938,533.96 |
| Total active + slashed stake (`Σ getNodeStakes` + `Σ getSlashedNodeStakes`) | 26,411,601.41 |
| **Reward buffer (balance − principal)** | **526,932.54 (≈ 2.0% of principal)** |
| Deficit (principal − balance) | 0 |

At review time the contract is solvent for principal, but the entire safety margin is a ~527K IDOS reward
buffer against ~26.4M IDOS of custodied principal. There is no on-chain guard that maintains or restores this
margin.

---

## Step-by-step (permissionless loss path)

1. Over time, cumulative claimable rewards grow past the funded reward buffer (reward accrual is automatic and
   unbounded; reward funding is a separate, untracked manual process).
2. A staker calls `withdrawReward()` (permissionless) → paid out of the shared balance, which now drops below
   total principal owed. No on-chain check prevents this.
3. Stakers `unstake()` and wait `UNSTAKE_DELAY` (14 days).
4. Earlier callers of `withdrawUnstaked()` are paid in full from the remaining balance.
5. The last caller(s) of `withdrawUnstaked()` revert (token transfer fails on insufficient balance) — their
   principal is **unavailable and economically lost unless the contract is externally recapitalized**. (The
   revert rolls back the deletion of the user's unstake entry, so the claim survives; recovery requires a top-up
   that backfills the shortfall the reward claim created.)

---

## Proof of concept

Two PoCs, both passing.

```
cd contracts
forge test --use ~/.solc-select/artifacts/solc-0.8.35/solc-0.8.35 \
  --match-test test_rewardClaimEatsPrincipal -vv                       # local — isolates the invariant
forge test --use ~/.solc-select/artifacts/solc-0.8.35/solc-0.8.35 \
  --match-contract IDOSNodeStaking_ForkPoC -vv                         # fork — live Arbitrum One bytecode+token
```

### 1) Local PoC — isolates the invariant with **no separate reward funding**

`test/zzz_IDOSNodeStakingPoC.t.sol::test_rewardClaimEatsPrincipal`. Fresh deployment, `epochReward = 50`, and
the contract balance is **only** staker principal (no reward funding at all — this is the cleanest statement of
the bug, with no owner rate change involved):

- alice and bob each stake 100 → balance = 200 (principal only).
- Warp 1 epoch; alice claims her 25 reward → **balance 175** (paid straight out of principal).
- Both unstake 100, warp 14 days; alice `withdrawUnstaked()` → balance 75.
- bob `withdrawUnstaked()` **reverts** — only 75 left against a 100 obligation. **Exact shortfall = 25**, equal
  to the reward alice drained.

```
[PASS] test_rewardClaimEatsPrincipal()
  bob principal stuck: contract balance 75e18 vs 100e18 owed; shortfall: 25000000000000000000
```

### 2) Fork PoC — same failure against the deployed bytecode + real token

`test/zzz_IDOSNodeStaking_ForkPoC.t.sol`, `vm.createSelectFork("https://arb1.arbitrum.io/rpc")`, bound to the
real deployed contracts.

`test_fork_identityAndLivePosture` confirms we are on the real deployment (asserts non-empty code,
`idosToken() == 0x68731d…`, `EPOCH_LENGTH == 1 days`, `UNSTAKE_DELAY == 14 days`) and prints the live posture
shown in the table above.

`test_fork_rewardClaimEatsPrincipal` reproduces the insolvency on live bytecode. To make the loss deterministic
on a fork (independent of the live participant set, timing, and current rate), the test uses two dominant
simulated stakers and compresses many under-funded epochs into one elevated-rate epoch via an owner
`setEpochReward` call. **This is a deterministic accelerator, not the exploit premise** — the underlying defect
(rewards paid from principal with no reserve check) is exactly the local PoC's no-funding scenario, which needs
no owner action; the owner rate change here only accelerates reaching the condition for a single-transaction
demonstration.

```
[PASS] test_fork_rewardClaimEatsPrincipal()
  balance after our stakes:                       226938533955899366758983590
  alice withdrawable reward (1 epoch):             88334696080281979954482072   (~88.33M IDOS)
  balance after alice's reward claim:             138603837875617386804501518
  contract balance now:                            38603837875617386804501518   (after alice's principal withdrawal)
  principal still owed to bob:                    100000000000000000000000000   (100M IDOS)
  bob's principal unavailable; balance short by:   61396162124382613195498482   (~61.4M IDOS)
  after external recapitalization, bob recovers principal: 100000000 IDOS
```

bob's `withdrawUnstaked()` reverts (only ~38.6M IDOS remain against a 100M obligation); `balanceNow < bob's
principal` is asserted — the live contract is insolvent for principal after the reward claim. The test then
confirms the loss is **economic and recapitalization-dependent**: after an external top-up backfills the
shortfall, bob's `withdrawUnstaked()` succeeds and returns his full 100M principal (his unstake entry survived
the earlier revert). Absent such a top-up, his principal stays unavailable.

> Methodology: this is a **read-only fork plus local simulation** — no transaction is broadcast to the live
> network.

---

## Impact

- **Loss of user principal** for the last users to `withdrawUnstaked` once reward payouts have driven the
  balance below outstanding principal obligations. The affected principal is **unavailable and economically lost
  unless the contract is externally recapitalized** (the failed `withdrawUnstaked` reverts and preserves the
  user's unstake claim, but the tokens to satisfy it no longer exist in the contract).
- Breaks the protocol's documented invariant that rewards are "claimed … without affecting the principal stake."
- The failure is silent and accretive: the contract reports healthy balances until the buffer is crossed, after
  which it operates as a first-come-first-served race over a shortfall — exactly the dynamic that disadvantages
  ordinary, less-attentive stakers.

---

## Recommendation

Enforce reward/principal solvency on-chain. Any one of:

1. **Track a dedicated reward reserve.** Add an explicit `fundRewards(uint256)` entry point that credits a
   `rewardReserve` accumulator; pay `withdrawReward` only from `rewardReserve` and decrement it on payout. Cap
   or refuse reward accrual that the reserve cannot cover.
2. **Add a solvency guard to `withdrawReward`.** Require that the post-transfer balance covers all remaining
   principal-denominated liabilities — active stake, pending (queued) unstakes, and withdrawable slashed stake
   — **without double-counting any bucket** (account for each principal token exactly once across the active /
   queued / slashed states).
3. **Separate accounting buckets / escrow.** Hold principal and reward funding in distinct accounting buckets
   so a reward transfer can never reference principal tokens.

Additionally, tie the reward rate to available reward funding (or surface and monitor the buffer) so accrued
obligations cannot silently outgrow the deposited reward budget.

---

## Relationship to the prior Nethermind audit (NM-0731)

This finding is **not** among NM-0731's six findings and directly contradicts its documented System Overview
§4.3, which states accrued yield "can be claimed at any time via the `withdrawReward()` function without
affecting the principal stake":

| Audit finding | Status vs. this finding |
|---|---|
| 6.1 [Critical] stake to non-allowlisted node | Fixed in current code (allowlist check in `stake`). |
| 6.2 [High] `withdrawableReward` wrong epoch reward | Fixed — current code uses `Checkpoints.Trace256.upperLookup`. |
| 6.3 [Low] unbounded loop in `withdrawUnstaked` | Known (separate issue). |
| 6.4 [Low] unbounded loop in `withdrawableReward` (DoS) | Known (separate issue). |
| 6.5 [Low] front-run slash | Known. |
| 6.6 [Low] manipulate reward distribution by staking at epoch end | Known (separate issue). |
| **This finding** — reward withdrawals consume principal (no reward reserve accounting) | **Not in NM-0731; contradicts the documented invariant.** |
