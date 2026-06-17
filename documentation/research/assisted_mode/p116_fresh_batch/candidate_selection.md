# P114 — Candidate selection (mechanical, next 3)

**Rule:** recommended-feature score across all subjects; exclude confirmed controls + already-run + missing-source; next N highest; deterministic tie-break (score, subject, name)

Total functions ranked: 954.

## Selected (next 3 highest remaining)
1. `munchables-2024-07 :: MigrationManager.burnRemainingPurchasedNFTs` (score 3.0)
2. `phi-2024-08 :: CuratorRewardsDistributor.distribute` (score 3.0)
3. `munchables-2024-07 :: MigrationManager.burnNFTs` (score 2.9912)

## Skipped (excluded by rule)
- `ramses-2024-10::RamsesV3Pool.swap` (score 4.0) — excluded: already-run in a prior phase
- `wildcat-2024-08::WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches` (score 3.9384) — excluded: already-run in a prior phase

## Considered ranking (top 15, audit)

| # | score | subject | contract.function |
|---|---|---|---|
| 1 | 4.0 | ramses-2024-10 | RamsesV3Pool.swap |
| 2 | 3.9384 | wildcat-2024-08 | WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches |
| 3 | 3.0 | munchables-2024-07 | MigrationManager.burnRemainingPurchasedNFTs |
| 4 | 3.0 | phi-2024-08 | CuratorRewardsDistributor.distribute |
| 5 | 2.9912 | munchables-2024-07 | MigrationManager.burnNFTs |
| 6 | 2.9882 | secondswap-2024-12 | SecondSwap_Marketplace.unlistVesting |
| 7 | 2.9853 | ramses-2024-10 | FeeCollector.collectProtocolFees |
| 8 | 2.9833 | traitforge-2024-07 | NukeFund.nuke |
| 9 | 2.9831 | phi-2024-08 | PhiFactory.claim |
| 10 | 2.9608 | iq-ai-2025-01 | AgentRouter.buy |
| 11 | 2.9608 | iq-ai-2025-01 | AgentRouter.sell |
| 12 | 2.9608 | iq-ai-2025-01 | LiquidityManager.moveLiquidity |
| 13 | 2.9412 | secondswap-2024-12 | SecondSwap_StepVesting.claim |
| 14 | 2.9355 | vultisig-2024-06 | ILOPool.claim |
| 15 | 2.9322 | phi-2024-08 | Claimable.signatureClaim |

_No manual cherry-picking; selection is the deterministic next-3 of the recommended ranking._

