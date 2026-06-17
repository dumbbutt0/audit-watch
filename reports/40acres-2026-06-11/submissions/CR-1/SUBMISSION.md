# [High/Medium] `CommunityRewards.earned()` is public + state-mutating — anyone can permanently brick/zero every depositor's reward claims

> **Status: DRAFT for human review — NOT submitted.** Sherlock bug bounty "40acres Finance" (id 102),
> `40-Acres/loan-contracts` @ `edb53bd`. Human verifies + confirms CommunityRewards is live/in-scope.

## Summary
`CommunityRewards.earned(address _token, address _owner)` is declared **`public`** and **mutates state** —
it writes `tokenClaimedPerEpoch[_owner][_token][ts] += reward` as it walks the epochs. But the actual
**payout** (`safeTransfer`) and the **`lastEarn` cursor** update happen only in `_getReward`. The function
it was adapted from (Velodrome `Reward.earned`) is `view`.

Because `earned()` is callable by anyone and marks a user's epochs as "claimed" **without transferring
anything**, any address can call `earned(token, victim)` to:
- **zero** the victim's reward (when the victim has a single eligible epoch): their later `getReward()`
  computes `reward = share − tokenClaimedPerEpoch = 0`; or
- **permanently brick** the victim's claims (the normal case, ≥2 elapsed epochs): the running-accumulator
  subtraction `reward -= tokenClaimedPerEpoch[ts]` underflows and **reverts**, so `getReward()` can never
  succeed again for that user/token.

This is a **permissionless, zero-cost, repeatable** griefing of *claimable user funds* (accrued reward
tokens), affecting every CommunityRewards depositor. It can also be triggered accidentally by any
frontend/integration that calls `earned()` as if it were a view.

## Severity
- **Impact: High** — permanent freezing / loss of all claimable community rewards for any/all users; the
  reward distribution can be bricked for everyone at no cost and is irrecoverable without an upgrade.
- **Likelihood: High** — single permissionless call, any caller, any victim; ≥2-epoch (brick) state is
  the steady state once the system has run for more than one epoch.
- Net **High** (Sherlock treats permanent freezing of claimable funds as High). A reviewer scoring it as
  a "rewards-only / griefing" issue may place it at **Medium** — flagged for the judge.

## Affected code — `src/CommunityRewards/CommunityRewards.sol`
`earned()` (`:481-529`) — public and mutating:
```solidity
function earned(address _token, address _owner) public returns (uint256) {   // <-- public, NOT view
    ...
    if (numEpochs > 0) {
        for (uint256 i = 0; i < numEpochs; i++) {
            ...
            reward += (cp0._balances * tokenRewardsPerEpoch[_token][_currTs]) / _supply;
            if (tokenClaimedPerEpoch[_owner][_token][_currTs] > 0) {
                reward -= tokenClaimedPerEpoch[_owner][_token][_currTs];     // <-- underflows on re-walk
            }
            tokenClaimedPerEpoch[_owner][_token][_currTs] += reward;         // <-- STATE WRITE, no payout
            _currTs += DURATION;
        }
    }
    return reward;
}
```
The only payout path, `_getReward` (`:611-629`), calls `earned()` (mutating) then transfers and advances
`lastEarn`. A direct `earned()` call performs the "mark claimed" write but neither the transfer nor the
`lastEarn` advance — desynchronizing the accounting against the victim.

## Proof of Concept
Self-contained Foundry test (no fork; `CommunityRewards` behind an ERC1967 proxy, mock voting-escrow +
loan to satisfy `initialize`, a mock reward token funded into the contract). File:
`test/poc/CommunityRewardsEarnedGrief.t.sol` (3/3 pass, run with `--via-ir`):

```
[PASS] test_control_victimGetsReward()        control: victim received 100000000000000000000   (full R)
[PASS] test_grief_singleEpoch_zeroesVictim()  attack(1 epoch): victim received 0
[PASS] test_grief_multiEpoch_bricksVictim()   attack(2 epochs): victim getReward reverted (bricked)
```
- **Control:** victim deposits, reward `R = 100e18` is notified for the epoch, victim `getReward` → `R`.
- **Attack (1 epoch):** attacker (arbitrary EOA) calls `earned(rwd, victim)`; victim `getReward` → **0**.
- **Attack (≥2 epochs):** attacker calls `earned(rwd, victim)`; victim `getReward` → **revert** (underflow),
  permanently bricked.

L1 entry = any EOA. L2 state-flip = `tokenClaimedPerEpoch[victim][token][ts]` set with **no** transfer.
L3 outcome = victim's reward is 0 / their claim reverts forever, vs. `R` in the control.

**Fork confirmation (real wired contracts).** `test/poc/CommunityRewardsEarnedGriefFork.t.sol` reproduces
it on a **Base mainnet fork** against the deployed Loan proxy (`0x87f1…EFD0`, upgraded to in-scope
LoanV2), the real VotingEscrow (`0xeBf4…e6B4`) and real USDC (`0x8335…2913`) — mirroring the repo's own
`testCommunityRewards`. Two equal depositors, 4 USDC notified (2 each); attacker calls
`earned(USDC, victim)`; then:
```
victim USDC received : 0
control USDC received: 2000000   // 2 USDC, full share
```
The victim is zeroed while the control depositor is paid in full — on live code, not mocks. (Run:
`forge test --match-contract CommunityRewardsEarnedGriefFork --via-ir`, with `ETH_RPC_URL` set to a Base
archive RPC, e.g. `https://base-rpc.publicnode.com`.)

## Recommendation
Make `earned()` a true `view` and move the "mark claimed" bookkeeping into `_getReward` **after** the
payout (the Velodrome design): compute the per-epoch amount in a view helper, then in `_getReward` write
`tokenClaimedPerEpoch` and `lastEarn` and transfer atomically. At minimum, `earned()` must not write
state, and the per-epoch subtraction must use the per-epoch claimed amount (not the running accumulator)
to avoid the underflow. Also reconsider `getRewardForUser`/`claimFlightBonus` being callable for arbitrary
`owner` (acceptable once `earned()` is view + payout-coupled, but worth confirming).

## Reviewer caveats
- Confirm CommunityRewards is deployed / in active use (it is wired throughout `LoanV2` via the managedNft
  + `_recordDepositOnManagedNft` → `deposit`, and funded via `notifyRewardAmount`).
- Secondary items examined and NOT escalated: the `_escrow` threshold "double-credit" is a false positive
  (`creditAmount = newBalance` equals total deposited at threshold crossing); the `LoanV2.claim`
  fee/reward distribution is `_entryPoint`(keeper)-gated and bounded by actual balances; the `_increaseNft`
  weight mis-credit is metric-only (`getTotalWeight()` is read only in tests). A Base-fork invariant
  harness for these was specified but not run here (no RPC available); recommend running it pre-submission.
