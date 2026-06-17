# P272 — TARGET_SCREEN (content-safe; existence not content; BLIND)

Fresh external scored **lending** contest, so the P271 LENDING_COMPLETION_CHECKLIST applies. Findings-repo
availability via `git ls-remote` (refs only, control = benddao-findings). No finding titles/bodies/report tables/
severity/awards opened.

## Decision: **SELECT `code-423n4/2024-01-init-capital-invitational`**
| criterion | status |
|---|---|
| EVM / Solidity | yes (solc 0.8.19; foundry/ape; OZ v4.9.3) |
| lending protocol (checklist fit) | **yes, ideal** — money market/leverage: `InitCore` (borrow/collateralize/decollateralize/liquidate), `PosManager` (positions), `Config` (modes), `LiqIncentiveCalculator`, `LendingPool` (mint/burn/borrow/accrueInterest), `RiskManager`, `DoubleSlopeIRM`, `MoneyMarketHook`/`MarginTradingHook` |
| answer key retrievable | **PUBLIC** (`...-invitational-findings`; control benddao confirms probe) |
| in this repo? | **NO** — cloned fresh, source-only, to `/tmp/p272_fresh/init` |
| used in P260–P271 scoring? | **NO** |
| prior exposure | **NONE real** — only named as a rejected alternative in the P270 TARGET_SCREEN (benign name-mention; no candidate-gen / no answer-key) |
| PoC feasibility | moderate — ~20 in-scope contracts (InitCore 610L, PosManager 360L, LendingPool 266L); the P271 inherit-and-expose / faithful-reproduction patterns apply |

## Confounds / caveats (disclosed)
- **Training-confound:** 2024-01, pre-cutoff, public ⇒ awards may be in training. Accepted as in P263/P266/P268/P270;
  candidates/selector/triage dimensions/completion are all done BLIND, pre-reveal.
- **Invitational contest:** fewer wardens → possibly **sparser awarded findings** than an open contest (recorded;
  may limit the scoring denominator).

## Rejected alternatives
gondi (NFT-collateral lending — weaker share/bad-debt/position-vs-global fit) · krystal-defi (less core-lending).
Fall back to gondi only if init fails the screen / lacks a usable lending award surface.

## Pre-reveal forbidden (held)
No finding titles / bodies / report tables / severity / award summaries / award-bearing searches before Phase 9.
Leak ⇒ mark contaminated, exclude, fall back.
