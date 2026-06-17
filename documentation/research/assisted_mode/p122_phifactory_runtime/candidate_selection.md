# P122 — Mechanical novel candidate selection

**Research-only / un-wired.** Ranking ≠ finding; no promotion, no severity, no routing.

## Rule
P119-corrected (permissionless-first) ranking over the P105 corpus via
`terminal_distribution.select_next_n` → `rank_candidates_prototype.rank_surface(REC_FEATS)`, excluding confirmed
controls (`moveLiquidity`, `spotPurchase`) + everything run **P113–P121** (P113 `swap`; P114 `closeMarket`,
`repayAndProcessUnpaidWithdrawalBatches`, `claimFromFactory`; P116 `burnRemainingPurchasedNFTs`, `distribute`,
`burnNFTs`; P117 `distribute`; P118 `unlistVesting`; P120 `FeeCollector.collectProtocolFees`; **P121 `NukeFund.nuke`**)
+ the full awarded set (novelty). Highest remaining permissionless = next harness candidate.

## Result — top-5 novel permissionless
| # | candidate | score |
|---|---|---|
| 1 | **phi-2024-08 :: PhiFactory.claim** | **2.9831** ← CHOSEN |
| 2 | iq-ai-2025-01 :: AgentRouter.buy | 2.9608 |
| 3 | iq-ai-2025-01 :: AgentRouter.sell | 2.9608 |
| 4 | secondswap-2024-12 :: SecondSwap_StepVesting.claim | 2.9412 |
| 5 | phi-2024-08 :: Claimable.signatureClaim | 2.9322 |

`PhiFactory.claim` was P121's #2 runner-up; with `NukeFund.nuke` now in the run set it is the #1 remaining novel
permissionless candidate — selected per the user's instruction ("harness PhiFactory.claim").

## Novelty check
phi awarded set in the corpus = `Cred._removeCredIdPerAddress` (PHI-H-05) + `Cred.buyShareCredFor` (PHI-M-07).
`PhiFactory.claim` is **not** awarded → genuinely novel.
