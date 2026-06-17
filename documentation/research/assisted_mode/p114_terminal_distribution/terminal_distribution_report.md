# P114 — Fresh-candidate terminal-state distribution

**OVERALL PASS: True**  ·  research-only, un-wired. 3 mechanically-selected fresh candidates run to truthful terminal states.

## Terminal distribution
- {"NEEDS_CONTEXT": 3}

## Per candidate
| Candidate | score | terminal | harness | validation | runtime tried | package allowed |
|---|---|---|---|---|---|---|
| wildcat-2024-08::WildcatMarket.closeMarket | 3.9953 | NEEDS_CONTEXT | HARNESS_MODERATE | NEEDS_MORE_CONTEXT | False | False |
| wildcat-2024-08::WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches | 3.9384 | NEEDS_CONTEXT | HARNESS_MODERATE | NEEDS_MORE_CONTEXT | False | False |
| phi-2024-08::PhiNFT1155.claimFromFactory | 3.8644 | NEEDS_CONTEXT | HARNESS_MODERATE | NEEDS_MORE_CONTEXT | False | False |

## Safety
- all safety assertions pass: True
- all terminals in allowed set: True
- no unsafe package (package only on CONFIRMED_RUNTIME): True

## Honest interpretation
- A distribution dominated by NEEDS_CONTEXT / HARNESS_UNAVAILABLE is NOT failure — it is the pipeline preserving precision and naming the next bottleneck.
- Observed next bottleneck: the recommended ranking's body-only `actor_clarity` signal misses access MODIFIERS declared in the function signature (`onlyBorrower`, `onlyPhiFactory`), so privileged functions can rank as 'permissionless'. Honest validation caught this; a future ranking iteration should read signature modifiers. Ranking chose the order; it did not validate anything.

## Per-candidate rationale
- **wildcat-2024-08__WildcatMarket_closeMarket**: Read WildcatMarket.closeMarket. It is `onlyBorrower nonReentrant sphereXGuardExternal` — a PRIVILEGED borrower-only function, NOT a permissionless attacker path. (Note: the recommended ranking marked it permissionless because the body-only actor_clarity heuristic misses the `onlyBorrower` MODIFIER, which is in the signature, not the body — a ranking-precision gap.) Its closed-market accounting feeds the state that the awarded P95 H-01 exploited, but that bug lives in the sibling permissionless `executeWithdrawal`, not here. I could not form a source-provable exploit on closeMarket (privileged caller) and could not prove it safe (complex closed-market settlement); resolving it needs the cross-function/runtime path. Truthful terminal: NEEDS_CONTEXT.
- **wildcat-2024-08__WildcatMarketWithdrawals_repayAndProcessUnpaidWithdrawalBatches**: Read WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches. It is `public nonReentrant sphereXGuardExternal`; calling it pulls the caller's assets in (safeTransferFrom) to repay debt and then processes unpaid batches with `satSub`-guarded available-liquidity accounting — i.e. calling it DONATES funds, not extracts them. Any real issue would be inside `_processUnpaidWithdrawalBatch`'s pro-rata math (the awarded executeWithdrawal class), which cannot be confirmed or refuted from source alone. No source-provable exploit; not provably safe. Truthful terminal: NEEDS_CONTEXT.
- **phi-2024-08__PhiNFT1155_claimFromFactory**: Read PhiNFT1155.claimFromFactory. It is `external payable whenNotPaused onlyPhiFactory` — gated to the PhiFactory contract, NOT permissionless. (Same ranking gap: the body-only actor_clarity heuristic missed the `onlyPhiFactory` MODIFIER in the signature.) The attacker-facing entrypoint is `PhiFactory.claim`; the reward flow (handleRewardsAndGetValueSent) is cross-contract via PhiRewards. I could not form a source-provable exploit on claimFromFactory in isolation, nor prove it safe. Truthful terminal: NEEDS_CONTEXT.

