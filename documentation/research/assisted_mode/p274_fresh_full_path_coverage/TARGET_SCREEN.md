# P274 — TARGET_SCREEN (content-safe; existence not content; BLIND)

Fresh external scored **multi-class** EVM contest (diversity > lending purity). Findings-repo availability via
`git ls-remote` (refs only, control = benddao-findings). No finding titles/bodies/report tables/severity/awards opened.

## Decision: **SELECT `code-423n4/2024-04-gondi`**
| criterion | status |
|---|---|
| EVM / Solidity | yes (solc 0.8.21; foundry; OZ + solmate + forge-std) |
| **class diversity (the point)** | **rich** — P2P NFT lending: **ORDER_VALIDATION** (MultiSourceLoan offers / renegotiation / EIP-712 signatures / `_processOffersFromExecutionData`) · **ACCESS_CONTROL** (onlyOwner setters, repayLoan caller/signature check, AddressManager, TwoStepOwned) · **ACCOUNTING** (Pool, FeeManager, LiquidationDistributor, Interest, WithdrawalQueue) · **DOS_LIVENESS** (AuctionLoanLiquidator, WithdrawalQueue, distribute loop) · **FRONT_RUNNING/EXTERNAL** (offer fill, settleAuction, PurchaseBundler callbacks, Aave/Lido allocators) |
| answer key retrievable | **PUBLIC** (`2024-04-gondi-findings`; control benddao confirms probe) |
| in this repo? | **NO** — cloned fresh, source-only, to `/tmp/p274_fresh/gondi` |
| used in P260–P273 scoring? | **NO** |
| prior exposure | **NONE** (no match in `documentation/research/assisted_mode/`) |
| PoC feasibility | moderate — ~28 in-scope (MultiSourceLoan 1155L, Pool 766L, AuctionLoanLiquidator 336L); P271 inherit-and-expose / faithful-reproduction patterns apply |

## Confounds (disclosed)
Training-confound: 2024-04, pre-cutoff, public ⇒ awards may be in training (accepted as prior phases; all selection/
coverage/triage/completion done BLIND pre-reveal).

## Rejected alternatives
krystal-defi (narrower subsystem spread) · ronin (larger, infra-flavored) — fall back if gondi fails the screen.
superposition (exposed P263/P268; likely Stylus) · olympus/decent/munchables (private or heavily exposed).

## Pre-reveal forbidden (held)
No finding titles / bodies / report tables / severity / award summaries / award-bearing searches before Phase 10.
Leak ⇒ mark contaminated, exclude, fall back.
