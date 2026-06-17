# P123 — Mechanical novel candidate selection

**Research-only / un-wired.** Ranking ≠ finding; no promotion, no severity, no routing.

## Rule
P119-corrected (permissionless-first) ranking over the P105 corpus via
`terminal_distribution.select_next_n` → `rank_candidates_prototype.rank_surface(REC_FEATS)`, excluding confirmed
controls (`moveLiquidity`, `spotPurchase`) + everything run **P113–P122** (P113 `swap`; P114 `closeMarket`,
`repayAndProcessUnpaidWithdrawalBatches`, `claimFromFactory`; P116 `burnRemainingPurchasedNFTs`, `distribute`,
`burnNFTs`; P117 `distribute`; P118 `unlistVesting`; P120 `FeeCollector.collectProtocolFees`; P121 `NukeFund.nuke`;
**P122 `PhiFactory.claim`**) + the full awarded set (novelty). Highest remaining permissionless = next candidate.

## Result — top-5 novel permissionless
| # | candidate | score |
|---|---|---|
| 1 | **iq-ai-2025-01 :: AgentRouter.buy** | **2.9608** ← CHOSEN |
| 2 | iq-ai-2025-01 :: AgentRouter.sell | 2.9608 |
| 3 | secondswap-2024-12 :: SecondSwap_StepVesting.claim | 2.9412 |
| 4 | phi-2024-08 :: Claimable.signatureClaim | 2.9322 |
| 5 | phi-2024-08 :: Claimable.merkleClaim | 2.8983 |

`AgentRouter.buy` was P122's #2 runner-up; with `PhiFactory.claim` now in the run set it is the #1 remaining novel
permissionless candidate — selected per the user's instruction ("harness AgentRouter.buy"). (`AgentRouter.sell` ties
at 2.9608 and is its sibling; `buy` chosen per the request.)

## Novelty check
iq-ai awarded set = `LiquidityManager.moveLiquidity` (IQ-M-01) + `AgentFactory` (IQ-H-01, constructor-class).
`AgentRouter.buy` is **not** awarded → genuinely novel.
