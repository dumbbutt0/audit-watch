# Reserve Index DTF / Folio — bug bounty — audit conclusion

**Target:** Reserve Protocol Index DTFs (permissionless on-chain index funds; Folio). Repo github.com/reserve-protocol/reserve-index-dtf, EVM, live+funded (DTFs hold real ERC20 baskets). Core: Folio.sol (1173) + RebalancingLib (479, Dutch-auction rebalancing) + StakingVault (420).
**Method (diff-the-audit + live-state-first):** published audits (Trust Dec-2024, ToB v2.0.0 Apr-2025 + v4.0.0 Jun-2025, Pashov Jun-2025, Cantina Jan-2025) cover up to **v4.0.0**. HEAD = **r5.0.0 + post-r5 (May-Jun 2026)** = the UNAUDITED delta (Folio +465, RebalancingLib +203, StakingVault +148, FolioLib new, the "trusted fill" + the reverted circuit breaker #185 at HEAD). Focused the pass there; deduped the v1-v4 audits.

## Verdict: honest negative — well-built unaudited delta

Headline lead (the freshest/most-suspicious change) was the **circuit-breaker revert (#185, HEAD)**: they added an I-04 "trusted fill circuit breaker" (May 25) that recorded a floor price at open and, at close, disabled the filler if it executed below floor — then **reverted it** (Jun 18). Traced rigorously → **safe redundancy removal:**
- The trusted-fill price floor is set at OPEN: `createTrustedFill` → `_getBid` → `filler.initialize(..., sellAmount, buyAmount)` where buyAmount = sellAmount × current Dutch-auction price.
- The floor is enforced INSIDE the registry-approved filler (CowSwapFiller: `isValidSignature` requires `orderPrice ≥ price` per order; `swapActive()` blocks `closeFiller` until the pro-rata floor `(sellAmount−bal)×price/D27` is met same-block) — including on partial fills.
- `targetFiller` is registry-validated (governance-only `addTrustedFiller`) → no arbitrary-filler drain.
- `closeTrustedFill` (post-revert) just records sold/bought; the reverted breaker only DETECTED a below-floor close the filler already prevents → redundant.

Other unaudited-delta surfaces (all clean / permissionless-safe):
- `openAuctionUnrestricted` (permissionless after the restricted window): the opener gets ZERO price/weight choice (forced to `weights.spot` + `initialPrices` + `limits.spot`); bidding at endPrice is the intended Dutch floor; the manager's price band is the only protection (OOS centralization).
- Conservation: rounding uniformly basket-favorable (sellLimit Ceil, buyLimit Floor, bidAmount Ceil); `rebalance.limits` vs balances is the global stop; auctions can only NARROW limits; `traded` is per-auction.
- StakingVault delta: UUPS-ization (admin/OOS) + `burn()` (self-harm); reward accrual unchanged from audited r4.
- poke/sync: `sync`→`_closeTrustedFill` closes a prior fill before any new op (no mid-swap coexistence); no brick path.

## Submission
**Nothing submitted (honest negative).** The unaudited r5 delta is well-built; the circuit-breaker revert is safe redundancy (the trusted-filler enforces the floor; registry-validated). bid()/createTrustedFill are auction-price-bounded; the permissionless auction-open has no price discretion; conservation rounding favors the basket. (Note: 2 load-bearing facts about the floor enforcement live in the external `@reserve-protocol/trusted-fillers` pinned dep — governance-controlled, not vendored.) diff-the-audit correctly isolated the right unaudited surface; it just holds.
