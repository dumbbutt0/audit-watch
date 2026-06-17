# Staking rewards can be under-claimed due to rounding

Severity: High

## Root Cause
StakingRewards.claim() truncates small reward computations to zero before the
time multiply.

## Impact
Reward extraction: small stakers lose their unclaimed yield.

## Entry Point
StakingRewards.claim() is callable by any staker.

## Preconditions
- Hold a small stake

## Affected Contracts
- contracts/StakingRewards.sol

## Affected Functions
- StakingRewards.claim()

## Asset Delta
Estimated up to ~0.4 token per epoch per small staker, from reasoning only — not
yet proven by a runnable test.
