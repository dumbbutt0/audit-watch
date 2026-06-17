# P113 — Candidate selection (mechanical)

**Rule:** recommended-feature score across all subjects; exclude confirmed controls / missing-source; highest remaining; deterministic tie-break (score, subject, name)

**Selected:** `ramses-2024-10 :: RamsesV3Pool.swap` (recommended score 4.0, permissionless=True).
Total functions ranked: 954.

## Skipped before selection (excluded by rule)
- none (the selected candidate is the global #1; no excluded candidate ranked above it)

## Considered ranking (top 12, for audit)

| # | score | subject | contract.function | excluded? |
|---|---|---|---|---|
| 1 | 4.0 | ramses-2024-10 | RamsesV3Pool.swap |  |
| 2 | 3.9953 | wildcat-2024-08 | WildcatMarket.closeMarket |  |
| 3 | 3.9384 | wildcat-2024-08 | WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches |  |
| 4 | 3.8644 | phi-2024-08 | PhiNFT1155.claimFromFactory |  |
| 5 | 3.0 | munchables-2024-07 | MigrationManager.burnRemainingPurchasedNFTs |  |
| 6 | 3.0 | phi-2024-08 | CuratorRewardsDistributor.distribute |  |
| 7 | 2.9912 | munchables-2024-07 | MigrationManager.burnNFTs |  |
| 8 | 2.9882 | secondswap-2024-12 | SecondSwap_Marketplace.unlistVesting |  |
| 9 | 2.9853 | ramses-2024-10 | FeeCollector.collectProtocolFees |  |
| 10 | 2.9833 | traitforge-2024-07 | NukeFund.nuke |  |
| 11 | 2.9831 | phi-2024-08 | PhiFactory.claim |  |
| 12 | 2.9608 | iq-ai-2025-01 | AgentRouter.buy |  |

_No manual cherry-picking: the candidate is the deterministic global maximum of the recommended ranking after excluding confirmed controls. Ranking only chooses investigation order._

