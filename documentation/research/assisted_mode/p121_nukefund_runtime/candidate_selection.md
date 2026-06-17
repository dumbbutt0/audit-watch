# P121 — Mechanical novel candidate selection

**Research-only / un-wired.** Ranking ≠ finding; no promotion, no severity, no routing.

## Rule
P119-corrected (permissionless-first) ranking over the P105 corpus via
`terminal_distribution.select_next_n` → `rank_candidates_prototype.rank_surface(REC_FEATS)`, excluding confirmed
controls (`moveLiquidity`, `spotPurchase`) + everything run **P113–P120** (P113 `swap`; P114 `closeMarket`,
`repayAndProcessUnpaidWithdrawalBatches`, `claimFromFactory`; P116 `burnRemainingPurchasedNFTs`, `distribute`,
`burnNFTs`; P117 `distribute`; P118 `unlistVesting`; **P120 `FeeCollector.collectProtocolFees`**) + the full
awarded set (novelty). Highest remaining permissionless = next harness candidate.

## Result — top-5 novel permissionless
| # | candidate | score |
|---|---|---|
| 1 | **traitforge-2024-07 :: NukeFund.nuke** | **2.9833** ← CHOSEN |
| 2 | phi-2024-08 :: PhiFactory.claim | 2.9831 |
| 3 | iq-ai-2025-01 :: AgentRouter.buy | 2.9608 |
| 4 | iq-ai-2025-01 :: AgentRouter.sell | 2.9608 |
| 5 | secondswap-2024-12 :: SecondSwap_StepVesting.claim | 2.9412 |

`NukeFund.nuke` was P120's #2 runner-up; with `FeeCollector.collectProtocolFees` now in the run set it is the #1
remaining novel permissionless candidate — selected per the user's instruction ("harness NukeFund.nuke").

## Novelty check
traitforge awarded set = `TraitForgeNft.mintWithBudget` (TRF-H-01) + `EntityForging.forgeWithListed` (TRF-M-18).
`NukeFund.nuke` is **not** awarded → genuinely novel.
