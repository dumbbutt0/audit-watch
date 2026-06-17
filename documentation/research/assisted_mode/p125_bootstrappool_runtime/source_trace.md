# P125 — Source trace: BootstrapPool (iq-ai-2025-01)

Subject: `src/BootstrapPool.sol` (solc 0.8.25, `ReentrancyGuard`). Read-only; framing only — runtime decides.
A balance-based constant-product AMM with a VIRTUAL currency reserve (the "phantom").

## Reserves (the phantom model)
`phantomAmount = initialPrice * bootstrapAmount / 1e18` (set once in the constructor; never backed by real tokens).
`getReserves()`:
- `reserveCurrencyToken = phantomAmount + currencyToken.balanceOf(this) - currencyTokenFeeEarned`
- `reserveAgentToken   = agentToken.balanceOf(this) - agentTokenFeeEarned`
Live `balanceOf` (balance-based, not stored reserves); accrued fees are carved out of the trading reserve.

## Pricing
`fee = 10_000 - _feeBps` (the keep-rate in bps). `getAmountOut`:
`out = (amountIn*fee*reserveOut) / (reserveIn*10_000 + amountIn*fee)` — the UniV2 formula. `getAmountIn` is its
inverse; `maxSwapAmount(agent)` = the agent input that drains exactly the real currency (`getAmountIn(realCurrency -
fee, currency)`).

## Trades (both permissionless, `nonReentrant notKilled`)
- `buy(amountIn, recipient)`: `amountOut = getAmountOut(amountIn, currency)`; `currencyTokenFeeEarned +=
  amountIn*_feeBps/10_000`; pull `amountIn` currency; send `amountOut` agent. (Fee charged on the CURRENCY input.)
- `sell(amountIn, recipient)`: `amountOut = getAmountOut(amountIn, agent)`; `agentTokenFeeEarned +=
  amountIn*_feeBps/10_000`; pull `amountIn` agent; send `amountOut` currency; then
  `require(currencyToken.balanceOf(this) >= currencyTokenFeeEarned, "INSUFFICIENT_LIQUIDITY")` (fees protected after
  the payout). (Fee charged on the AGENT input.)

## Fee / admin surface
- `sweepFees()` — **permissionless** — transfers `currencyTokenFeeEarned`/`agentTokenFeeEarned` to
  `LiquidityManager(owner).owner()` and zeroes them. (Because fees are carved out of `getReserves`, sweeping is
  reserve-neutral.)
- `kill()` — `onlyOwner` (the LiquidityManager) — sweeps fees then transfers the entire balance to the owner; sets
  `killed`. This is the migration hand-off to `moveLiquidity` (the awarded IQ-M-01 area).

## Invariants to probe (runtime)
1. round-trip is strictly lossy (fees ⇒ no free extraction for a lone trader).
2. constant-product `k = reserveCurrency*reserveAgent` is non-decreasing across each trade.
3. solvency — the pool never pays out currency it does not hold (sells beyond real currency revert; the phantom only
   inflates the *quote*, not the *payout*).
4. `sweepFees` is reserve-neutral and routes exactly the accrued fees.
5. donation-safety — a direct token transfer cannot make the donor net-profit (CPMM donor self-loss).

## Out-of-scope (NEEDS_CONTEXT)
Reserve carryover at `kill()` → `moveLiquidity` migration (mis-pricing the Fraxswap pair) = the awarded IQ-M-01 flow;
not the per-trade pool invariants tested here.
