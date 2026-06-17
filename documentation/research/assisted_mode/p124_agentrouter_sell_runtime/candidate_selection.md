# P124 — Mechanical novel candidate selection

**Research-only / un-wired.** Ranking ≠ finding; no promotion, no severity, no routing.

## Rule
P119-corrected (permissionless-first) ranking via `terminal_distribution.select_next_n` →
`rank_candidates_prototype.rank_surface(REC_FEATS)`, excluding confirmed controls (`moveLiquidity`, `spotPurchase`)
+ everything run **P113–P123** (…; P122 `PhiFactory.claim`; **P123 `AgentRouter.buy`**) + the full awarded set.

## Result — top-5 novel permissionless
| # | candidate | score |
|---|---|---|
| 1 | **iq-ai-2025-01 :: AgentRouter.sell** | **2.9608** ← CHOSEN |
| 2 | secondswap-2024-12 :: SecondSwap_StepVesting.claim | 2.9412 |
| 3 | phi-2024-08 :: Claimable.signatureClaim | 2.9322 |
| 4 | phi-2024-08 :: Claimable.merkleClaim | 2.8983 |
| 5 | traitforge-2024-07 :: Airdrop.claim | 2.8889 |

`AgentRouter.sell` (the sibling of P123's `buy`) is the #1 remaining novel permissionless candidate — selected per
the user's instruction ("harness AgentRouter.sell"). Completes the AgentRouter buy/sell pair at the router level.

## Novelty check
iq-ai awarded set = `LiquidityManager.moveLiquidity` (IQ-M-01) + `AgentFactory` (IQ-H-01).
`AgentRouter.sell` is **not** awarded → genuinely novel.
