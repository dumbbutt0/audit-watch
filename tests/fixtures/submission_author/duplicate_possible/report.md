# Reward accounting rounds claimable yield to zero for small stakers

Severity: Medium

## Root Cause
StakingRewards.claim() computes reward as (staked * rate) / PRECISION before
multiplying by elapsed time, so small per-epoch claims truncate to zero.

## Impact
Reward extraction / loss of unclaimed yield for small stakers, quantified below.

## Entry Point
StakingRewards.claim() — callable by any staker from an EOA, with no privileged
setup.

## Preconditions
- Hold a small stake
- Wait at least one epoch before claiming

## Attack Path
- A small staker calls StakingRewards.claim()
- (staked * rate) / PRECISION truncates to 0 before the time multiply
- The claimable yield is silently dropped

## Affected Contracts
- contracts/StakingRewards.sol

## Affected Functions
- StakingRewards.claim()

## Code References
- contracts/StakingRewards.sol:120-135

## State Before
pendingRewards[user] = R (small non-zero amount)

## State After
pendingRewards[user] = 0 while transferred = 0

## Asset Delta
Small stakers lose roughly 100% of per-epoch yield below ~1e6 wei of stake;
modeled at 0.4 token per epoch.

## Worst Case
Every sub-threshold staker loses their entire per-epoch yield.

## Realistic Case
Stakers below ~1e6 wei lose per-epoch yield; bounded by small-staker TVL.

## Program Table Mapping
Immunefi v2.2 — theft/loss of yield (Medium).

## Reproduction
- forge test --match-test test_small_claim_truncates -vvv

## Assumptions
- Realistic small-staker sizes exist on the deployment
