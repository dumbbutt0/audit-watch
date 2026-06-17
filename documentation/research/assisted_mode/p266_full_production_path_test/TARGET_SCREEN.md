# P266 — TARGET_SCREEN (content-safe; existence not content)

**Screen rule:** verify *retrievability/structure* only — no finding titles, issue bodies, report finding sections,
severity tables, or award summaries were opened. Findings-repo availability checked via `git ls-remote` (refs only,
`GIT_TERMINAL_PROMPT=0`, control = known-public benddao-findings). Prior-phase exposure checked by grepping my own
deliverable docs (not the contest answer key).

## Decision summary
| candidate | EVM/Sol | manifest | answer key retrievable | prior exposure | PoC-feasible | decision |
|---|---|---|---|---|---|---|
| **phi-2024-08-fresh** | yes (9 in-scope contracts, 257 fns) | yes | **PUBLIC** (`code-423n4/2024-08-phi-findings`) | **shallow / non-answer-key** | yes (reward/bonding-curve/1155 surface) | **SELECT** |
| secondswap-2024-12-fresh | yes (8 contracts) | yes | **PRIVATE** (`…-secondswap-findings` not retrievable) | deeper (P107 + `spotPurchase` harness_prep scaffold) | yes | **REJECT** |
| traitforge-2024-07-fresh | yes (~19 sol) | yes | PUBLIC | **deeper** (P242 recall-sprint candidate-gen + P107/P119) | yes | REJECT (exposure) |

## Why secondswap (operator's first pick) was rejected
The content-safe screen found `code-423n4/2024-12-secondswap-findings` is **private/unretrievable** (the contest
*source* repo `code-423n4/2024-12-secondswap` is public, but the **findings/answer key is not**). That is the exact
P261/Monetrix failure mode: no retrievable answer key ⇒ a freeze-before-reveal mechanism-recovery test would be
**unscorable**. Secondary: secondswap also had deeper prior exposure (a `SecondSwap_Marketplace_spotPurchase`
harness_prep scaffold + P107 ranking). REJECT on retrievability alone. (Plan pre-authorized the phi/traitforge
fallback if secondswap failed the screen.)

## Why traitforge was rejected
Findings public, but prior exposure is **deeper**: `p242_recall_sprint/outputs/traitforge-2024-07-fresh_ctr.json`
is a candidate-generation artifact (recall sprint), i.e. the target's surface was already worked for candidates.
Plus P107/P119. Cleaner alternatives exist → REJECT.

## Why phi-2024-08-fresh is SELECT
- **EVM/Solidity, PoC-feasible:** 9 in-scope contracts (Cred, PhiFactory, Claimable, CreatorRoyaltiesControl,
  RewardControl, PhiNFT1155, BondingCurve, CuratorRewardsDistributor, PhiRewards), 257 in-scope functions; manifest
  already built. Reward-share / bonding-curve / ERC1155 accounting surface is well-suited to a focused foundry PoC.
- **Answer key retrievable:** `code-423n4/2024-08-phi-findings` is **PUBLIC** (control benddao-findings confirms the
  probe). Findings sealed until Phase 8 (freeze artifacts hashed first).
- **Prior exposure is shallow and NON-answer-key:** phi appears only in `p107/ranking_results.json` (a ranking/
  signal-probe artifact that carries **no** ground_truth/awarded/severity/outcome/label fields — verified) and in
  P115/P119 actor-clarity *prompt-engineering* fixes. No awarded mechanism was recorded in any prior phase, so my
  reasoning is **not** primed on phi's specific bugs. This is lighter than the training-confound already accepted in
  P263.

## Confounds recorded (disclosed, not hidden)
- **Training-confound:** phi is pre-cutoff (2024-08) and public ⇒ its awards may be in training. Accepted exactly as
  in P263; the "beyond P263/P265" comparison is like-for-like (both public-findings + disclosed training-confound).
- **Shallow structural prior-exposure** (P107 ranking listing / P115-P119 prompt fixes) — no answer-key content.

## Pre-reveal forbidden (held)
No finding titles / issue bodies / report finding sections / severity tables / award summaries / award-bearing
searches before Phase 8. If award content leaks before freeze: mark contaminated, exclude from scoring, fall back to
traitforge.
