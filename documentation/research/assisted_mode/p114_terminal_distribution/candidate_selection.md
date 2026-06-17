# P114 — Candidate selection (mechanical, next 3)

**Rule:** recommended-feature score across all subjects; exclude confirmed controls + already-run + missing-source; next N highest; deterministic tie-break (score, subject, name)

Total functions ranked: 954.

## Selected (next 3 highest remaining)
1. `wildcat-2024-08 :: WildcatMarket.closeMarket` (score 3.9953)
2. `wildcat-2024-08 :: WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches` (score 3.9384)
3. `phi-2024-08 :: PhiNFT1155.claimFromFactory` (score 3.8644)

## Skipped (excluded by rule)
- `ramses-2024-10::RamsesV3Pool.swap` (score 4.0) — excluded: already-run in a prior phase

## Considered ranking (top 15, audit)

| # | score | subject | contract.function |
|---|---|---|---|
| 1 | 4.0 | ramses-2024-10 | RamsesV3Pool.swap |
| 2 | 3.9953 | wildcat-2024-08 | WildcatMarket.closeMarket |
| 3 | 3.9384 | wildcat-2024-08 | WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches |
| 4 | 3.8644 | phi-2024-08 | PhiNFT1155.claimFromFactory |
| 5 | 3.0 | munchables-2024-07 | MigrationManager.burnRemainingPurchasedNFTs |
| 6 | 3.0 | phi-2024-08 | CuratorRewardsDistributor.distribute |
| 7 | 2.9912 | munchables-2024-07 | MigrationManager.burnNFTs |
| 8 | 2.9882 | secondswap-2024-12 | SecondSwap_Marketplace.unlistVesting |
| 9 | 2.9853 | ramses-2024-10 | FeeCollector.collectProtocolFees |
| 10 | 2.9833 | traitforge-2024-07 | NukeFund.nuke |
| 11 | 2.9831 | phi-2024-08 | PhiFactory.claim |
| 12 | 2.9608 | iq-ai-2025-01 | AgentRouter.buy |
| 13 | 2.9608 | iq-ai-2025-01 | AgentRouter.sell |
| 14 | 2.9608 | iq-ai-2025-01 | LiquidityManager.moveLiquidity |
| 15 | 2.9412 | secondswap-2024-12 | SecondSwap_StepVesting.claim |

_No manual cherry-picking; selection is the deterministic next-3 of the recommended ranking._

