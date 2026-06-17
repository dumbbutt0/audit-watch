# P290 — DISCOVERY_AND_ROUTING (blind, salty-2024-01-holdout)

Frozen blind chain on the existing coverage_manifest (no answer-key access).

## Results
- Advisory candidates (P264 shadow): **22**.
- Coverage classes routed (P273): ACCESS_CONTROL_AUTHORIZATION · ACCOUNTING_LIQUIDATION_BAD_DEBT · EXTERNAL_INTEGRATION
  · REWARDS_CLAIMS · SHARE_ROUNDING_PRECISION · STATE_MACHINE_LIFECYCLE · UNKNOWN_OTHER (7 classes — broad spread).
- Triage (P269): 8 advanced.
- Validation queue (P278): **10** candidates, 7 classes, max_class_fraction 0.20, anti-monoculture OK.
- Guard: PASS.

## Validation queue (10)
StakingRewards.claimAllRewards (REWARDS) · Pools.withdraw (STATE_MACHINE) · CollateralAndLiquidity.
withdrawCollateralAndClaim (ACCOUNTING) · Upkeep.step2 (UNKNOWN) · Airdrop.allowClaiming (REWARDS) ·
CollateralAndLiquidity.liquidateUser (ACCOUNTING) · Pools.deposit (EXTERNAL_INTEGRATION) · USDS.mintTo (SHARE_ROUNDING) ·
Liquidity.depositLiquidityAndIncreaseShare (SHARE_ROUNDING) · DAOConfig.changePercentPolRewardsBurned (ACCESS).

The surface routed to the salty staking/rewards/pools/liquidation/collateral core — a sensible attack surface and a good
test of the P289 loss/reward lenses. No answer key consulted.
