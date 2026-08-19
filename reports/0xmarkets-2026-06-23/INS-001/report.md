# INS-001 — Drawdown trigger is computed on USD pool value (price-driven), so the insurance fund is drained to subsidize ordinary collateral/index price declines that cause no real LP loss

- **Severity (recommended):** High
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** High
- **ICE:** Impact=High · Confidence=High · Exploitability=Conditional
- **Location(s):** `contracts/insurance/InsuranceFundUtils.sol:58-87,328-349 (consumes MarketUtils.getPoolValueExcludingUnrealizedPnl / getPoolUsdWithoutPnl, MarketUtils.sol:241-302)`
- **Vulnerable files (bundled in `sources/`):** `InsuranceFundUtils.sol`, `MarketUtils.sol`, `DecreasePositionCollateralUtils.sol`

## Description

getDrawdownFraction() (InsuranceFundUtils.sol:58-87) and snapshotEpoch() (InsuranceFundUtils.sol:328-349) both measure pool health as MarketUtils.getPoolValueExcludingUnrealizedPnl(...) which is, per getPoolUsdWithoutPnl (MarketUtils.sol:241-261), poolAmount * tokenPrice + borrowingFees - impactPoolUsd. This is a USD valuation of the pool's long/short token amounts. The 'drawdown' = (epochPoolValueUsd - currentPoolValueUsd) / epochPoolValueUsd therefore moves with the *oracle price of the pool tokens*, not only with realized LP losses (trader PnL paid out, bad debt). The pool tokenAmount is read from DataStore poolAmountKey (donation-resistant, good), but the USD figure still falls whenever the long/short token price falls. Consequence: in any market whose long or short token is a volatile asset (e.g. a WETH-collateral or volatile-index market), a normal downward price move between the epoch snapshot and the live read registers as 'drawdown' even though LPs still hold exactly the same token amounts (no loss in token terms). If that fraction exceeds insuranceFundDrawdownTriggerFactor, the next decrease/liquidation/ADL (which all route through DecreasePositionCollateralUtils.processCollateral -> _maybeInjectInsurancePool -> attemptInjectPool, DecreasePositionCollateralUtils.sol:535-566) injects pnlToken from the InsuranceVault into the pool via applyDeltaToPoolAmount (InsuranceFundUtils.sol:241-255). The injected pnlToken can be a *different* token than the one that depreciated, so the fund is emptied and pool composition is permanently shifted to chase a USD target that price movement, not a real insured event, created. Because the GM/MarketToken share price tracks pool value, the injected reserve accrues pro-rata to whoever holds LP tokens at injection time, i.e. the insurance fund (funded by every trader's liquidation-fee slice) is redistributed to current LPs on every routine price dip past the threshold.

## Impact

The per-market insurance reserve is repeatedly drained into the LP pool on ordinary token-price declines that inflict no token-denominated loss on LPs, leaving the fund empty (InsuranceFundShortfall) precisely when a genuine bad-debt event later occurs. Value funded by all traders' liquidation fees is redistributed to incumbent LPs; in volatile-collateral/index markets this can recur every epoch.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Drain the per-market insurance reserve (collective trader-funded capital) into the LP pool with no corresponding insured loss, leaving the fund unable to cover a real future bad-debt drawdown.
- **Technique:** Onboard / operate a market whose long or short pool token is volatile and set a finite insuranceFundDrawdownTriggerFactor. After a snapshotEpoch baseline, let the token price fall by more than triggerFactor; getDrawdownFraction returns drawdown>trigger purely from price. The next keeper-executed decrease/liquidation/ADL invokes attemptInjectPool, which transfers pnlToken out of the InsuranceVault into the pool (applyDeltaToPoolAmount) up to the reserve balance. No bad debt was realized; the USD gap was caused by oracle price movement.
- **Evasion:** The developer intended drawdown to represent realized pool loss to be 'restored' by the fund, and chose getPoolValueExcludingUnrealizedPnl to exclude unrealized trader PnL. But excluding unrealized PnL does not exclude token-price revaluation of the pool inventory itself; the USD-denominated baseline still floats with price, so a price decline is indistinguishable from a loss. The MAX_EPOCH_AGE stale-check only fails safe (disables) on a missed snapshot; it does not address a fresh snapshot followed by normal price decline.

## Reachability / follow-up

Conditional
