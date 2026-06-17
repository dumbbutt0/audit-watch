# P120 — Mechanical novel candidate selection

**Research-only / un-wired.** Selection orders the already-enumerated public/external surface; it does not promote,
score severity, or route anything. Ranking ≠ finding.

## Rule
P119-corrected (permissionless-first) ranking over the P105 corpus via
`terminal_distribution.select_next_n` → `rank_candidates_prototype.rank_surface(REC_FEATS)`, then exclude:
1. **Confirmed positive controls** — `iq-ai LiquidityManager.moveLiquidity`, `secondswap SecondSwap_Marketplace.spotPurchase`.
2. **Everything run P113–P118** — `ramses swap` (P113); `wildcat closeMarket`, `wildcat repayAndProcessUnpaidWithdrawalBatches`,
   `phi claimFromFactory` (P114); `munchables burnRemainingPurchasedNFTs`, `phi distribute`, `munchables burnNFTs`
   (P116); `phi distribute` harnessed (P117); `secondswap unlistVesting` harnessed (P118).
3. **Full awarded set** (for novelty).

Highest remaining permissionless = the next harness candidate. Deterministic tie-break (score, subject, name).

## Top-12 novel permissionless ranking
| # | candidate | score |
|---|---|---|
| 1 | **ramses-2024-10 :: FeeCollector.collectProtocolFees** | **2.9853** ← CHOSEN |
| 2 | traitforge-2024-07 :: NukeFund.nuke | 2.9833 |
| 3 | phi-2024-08 :: PhiFactory.claim | 2.9831 |
| 4 | iq-ai-2025-01 :: AgentRouter.buy | 2.9608 |
| 5 | iq-ai-2025-01 :: AgentRouter.sell | 2.9608 |
| 6 | secondswap-2024-12 :: SecondSwap_StepVesting.claim | 2.9412 |
| 7 | phi-2024-08 :: Claimable.signatureClaim | 2.9322 |
| 8 | phi-2024-08 :: Claimable.merkleClaim | 2.8983 |
| 9 | traitforge-2024-07 :: Airdrop.claim | 2.8889 |
| 10 | wildcat-2024-08 :: WildcatMarket.collectFees | 2.8863 |
| 11 | wildcat-2024-08 :: WildcatSanctionsEscrow.releaseEscrow | 2.8863 |
| 12 | ramses-2024-10 :: GaugeV3.cachePeriodEarned | 2.8824 |

## Novelty check
Ramses awarded set = `RamsesV3Pool.flash` (RAM-M-02) + `GaugeV3.getPeriodReward` (RAM-M-01).
`FeeCollector.collectProtocolFees` is **not** awarded → genuinely novel.

## Chosen
`ramses-2024-10 :: FeeCollector.collectProtocolFees` (score 2.9853, permissionless). Runner-ups recorded for the
next phase: `NukeFund.nuke`, `PhiFactory.claim`, `AgentRouter.buy/sell`.
