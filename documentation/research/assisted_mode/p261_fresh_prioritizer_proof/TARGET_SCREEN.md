# P261 — TARGET_SCREEN (content-safe; existence-only; NO award content fetched)
Fresh-target requirement: unseen, EVM/Solidity, award-class-fit (subtle accounting/state), NOT in audits/ corpus,
not used P253–P260, publicly retrievable findings (so a sealed reveal can be scored).

| candidate | architecture | source repo | FINDINGS public? (git ls-remote, refs only) | award-class fit | decision |
|---|---|---|---|---|---|
| **2026-04-monetrix** | C4 HyperEVM USDC-backed synthetic-dollar (MonetrixVault/sUSDM staked-share/Accountant/RedeemEscrow/InsuranceFund/USDM) | PUBLIC (`git ls-remote …/2026-04-monetrix` → refs ok) | **NO** (`…/2026-04-monetrix-findings` → auth-required = private/unpublished; control `2024-07-basin-findings` → public, so this is genuine non-publication) | strong (mint/redeem/share/yield/solvency) | **SELECT (operator-committed) but REVEAL-UNAVAILABLE** |
| 2025-11-merkl / 2025-11-brix-money | reward distribution / staking-yield | public | (public) | fit | NOT USED (operator committed monetrix, no auto-fallback; pre-cutoff → training-confound) |
| 2026-02-jupiter-lend, 2026-01-olas, panoptic-next-core, chainlink-payment, intuition | Solana / wrong-class / contaminated-family | — | — | — | REJECT |

## Phase-0 hard-gate outcome
monetrix is genuinely fresh (2026-04, post-Jan-2026 training cutoff ⇒ unseen by training) and Solidity, but its
**findings are not yet public** (contest still in judging). A freeze-before-reveal PROOF needs a retrievable key to
score; there is none. Per the committed plan (no auto-fallback): proceed with the **operational fresh run + freeze**
(the module IS exercised on fresh data) and return **NEEDS_MORE_FRESH_HELDOUT**, preserving frozen artifacts for a
**deferred reveal** once monetrix findings publish. No award content was fetched; no fabricated reveal.
