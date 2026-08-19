# IPOR — Immunefi bug bounty — audit conclusion

**Target:** IPOR (Immunefi $20k, interest-rate-derivatives AMM, KYC+PoC, deployed Ethereum). Live Apr-2023, scope updated Mar-30-2026.
**Scope:** ~13 deployed contracts = the AMM (IporProtocolRouter + per-asset AmmTreasury/AmmStorage + ipTokens for USDC/USDT/ETH/weETH). Source: github.com/IPOR-Labs/ipor-protocol (22k LOC, HEAD 434327d). Repo audit baseline thin/old (Zokyo 2022.08, Aacke 2022.11/2023.01).
**In-scope impacts:** Critical = direct theft / permanent freezing · High = freezing of unclaimed yield · Medium = contract unable to operate (lack of funds) for 24h.
**Method:** mapped 22k LOC; deep-read the core value surface (swap lifecycle + payoff/SOAP + treasury custody + core LP) and the spread-pricing + IPOR Index oracle (the inputs that price every swap).

## Verdict: honest negative (core); one non-submittable Medium

### Core swap engine — well-built (0 findings)
Two structural invariants close every economic vector:
1. **PnL hard-capped to ±collateral** — `SwapLogicBaseV1.normalizePnlValue` caps every swap's PnL (incl. the unwind component), applied twice. A winning swapper can't claim more than the pool owes; a loser can't lose more than collateral.
2. **LP-solvency guard** — `AmmStorage._updateBalancesWhenCloseSwap` requires `liquidityPool >= absPnlValue` before crediting the payout, and the ipToken exchange rate is gated by `require(LP − SOAP ≥ 0)`.
Plus: floating leg priced off the oracle-accrued IBT price (not spot); fixed rate bounded by ECDSA-signed risk indicators + `acceptableFixedInterestRate` slippage; demand spread rises monotonically with the trader's own notional (self-penalizing) + time-decays + is fee-laden (round-trips strictly fee-negative); SOAP symmetric on open/close; treasury fund-movers `onlyRouter`/`onlyOwner` with CEI + `nonReentrant`; exchange rate floored at 1e18 (no inflation attack), redeem fee applied before down-conversion (dust only). No over-claim, no insolvency-induction, no payout-redirection.

### Spread + IPOR Index — not manipulable for profit (0 Critical/High)
Demand spread is monotonic-against-trader + signed-cap-bounded + decaying (no in-block wash-manipulation profit); spread inputs are trusted off-chain-signed risk params; TWN/spread storage is router-gated + collision-free (per asset×tenor); index update is `onlyUpdater` + monotonic + non-backdatable.

### SP-001 (Medium) — NOT submittable
No on-chain staleness/heartbeat check on the IPOR Index at swap open (`IporOracle.getAccruedIndex` returns the value verbatim; `AmmOpenSwapService._beforeOpenSwap` consumes it with no freshness check). A stale index (trusted updater offline during a rate move) lets a trader open the favored leg off-market → LP value leak (bounded by `fixedRateCapPerLeg` + collateral caps). **Not submittable:** (a) doesn't match IPOR's only in-scope Medium impact ("contract unable to operate due to lack of funds for 24h"); (b) contingent on the **trusted, protocol-owned** updater being stale (operational/centralization); (c) oracle-data issues on a protocol-owned oracle are a standard OOS/trust assumption. Also non-nonce'd signed risk-indicator window = accepted off-chain-risk-oracle design (can't defeat the PnL cap or LP-solvency guard).

## Extensions pass (DONE) — base-architecture yield-bearing pools (stETH/wstETH/weETH/USDM)
Deep-read the newer `contracts/base/` V1/V2 architecture (AmmPoolsServiceBaseV1/WstEth/WeEth, AmmPoolsServiceUsdm, AmmTreasuryBaseV1/V2, AmmStorageBaseV1, SwapLogicBaseV1, base open/close swap services, DemandSpreadStEthLibsBaseV1).
- **Swap engine: clean.** PnL-cap (`SwapLogicBaseV1.normalizePnlValue`) + LP-solvency invariants hold identically in the base V1/V2 architecture; floating leg priced off the IPOR rate index (not asset market price), so stETH/wstETH/weETH rebase or wrap-rate changes between open/close are NOT exploitable; wstETH→stETH conversion happens once at open. No asset-specific payoff/conversion bug.

### LP-001 (High in code, but **latent** — not currently submittable) — donation/inflation regression in yield-bearing LP pools
The base yield-bearing pools compute the ipToken exchange rate from **raw `asset.balanceOf(treasury)`** (`AmmTreasuryBaseV1/V2.getLiquidityPoolBalance`) and `AmmLib.getExchangeRate` has **no virtual-offset / dead-shares guard** (1e18 floor only when `totalSupply==0`). This is a **regression vs the classic USDC/USDT AMM**, which tracks `liquidityPool` as a donation-**immune internal field** (`AmmStorage.add/subtractLiquidityInternal`). Dropping it → the rate is donation-inflatable → classic ERC-4626 first-depositor inflation theft.
- **Why not currently payable:** the only in-scope yield-bearing pool, **ipweETH, is well-seeded** (live mainnet read: `ipweETH.totalSupply()=59.05e18`, treasury weETH `59.68e18`). Inflation needs an empty pool; on a seeded pool a donation accrues pro-rata to all LPs (attacker net-loses). `provideLiquidity` mints round-half-up (threshold <0.5 shares — doesn't prevent, but moot while seeded).
- **Disposition:** real architectural regression, **latent High** — exploitable only on a freshly-deployed/unseeded (or fully-drained) yield-bearing pool. Strong **defensive-disclosure** to IPOR (add a virtual-offset / mandatory genesis seed, or restore internal LP accounting for the base pools). Borderline-submittable only if a new in-scope yield-bearing pool is deployed unseeded (or under Primacy of Impact for a future-pool risk). Mirrors the Cronos pattern: real bug-in-code, killed by live recon (seeded pool).

## Submission
**Nothing submitted.** Core swap engine structurally sound (PnL cap + LP-solvency); SP-001 oracle-staleness OOS/non-matching-tier; **LP-001 is a real donation/inflation regression in the yield-bearing base pools but latent** (in-scope ipweETH is seeded → not live-exploitable). Worth a defensive disclosure to IPOR; not a clean payable bounty finding. Honest negative for submission; LP-001 banked as latent/disclosure.
