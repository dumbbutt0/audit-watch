# Reproduce — X-1 (source-confirmed; no runnable PoC)

Vulnerable source: `vulnerable/MarketUtils.sol` → `getMarketTokenPrice`. Read the return branches:
`if (poolValue == 0) return 0;` and `marketTokenPrice = mulDiv(WEI_PRECISION, poolValue, supply)` where `poolValue`
is a signed `int256` (≤ 0 when capped pending trader PnL ≥ pool token value). A runnable PoC needs a full GMX build to
drive `getPoolValueInfo`. This finding grounds Cartha C-1 — see `../../cartha-2026-06-13/cartha-C1-reachability.md`.
GMX-inherited behavior; no 0xMarkets fix implied.
