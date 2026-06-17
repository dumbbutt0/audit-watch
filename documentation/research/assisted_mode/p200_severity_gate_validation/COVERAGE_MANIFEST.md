# P200 — coverage manifest + pre-registered blind sample (predy-2024-05-holdout)

Source-grounded, read-only. predy V6 = perps/gamma derivatives protocol; in-scope core **32 files / 7402 LOC**
(`audits/predy-2024-05-holdout/contracts/src`). Awarded counts (count-only viability unseal): **4 High / 8 Medium**.

## Severity-relevant surface inventory (read-only, from source)
- **Pool entrypoints** (`PredyPool.sol`): `trade`, `reallocate`, `execLiquidationCall`, `supply`, `withdraw`,
  `take` (`onlyByLocker`), `withdrawProtocolRevenue` (`onlyOperator`), `updateRecepient`, `allowTrader`, `createVault`.
- **Liquidation / solvency**: `LiquidationLogic.liquidate`, `LiquidationLogic.checkVaultIsDanger`,
  `PositionCalculator.isLiquidatable / calculateMinMargin / calculateMinValue`.
- **Trade / accounting**: `TradeLogic.trade / callTradeAfterCallback`, `Perp.reallocate / settleUserBalance /
  updatePosition`, `ScaledAsset.updatePosition / addAsset / removeAsset`, `ApplyInterestLib.applyInterestForToken`.
- **Oracle**: `PriceFeed.getSqrtPrice` (Pyth), `UniHelper.getSqrtTWAP / callUniswapObserve` (Uniswap v3 TWAP).
- **Order auth / signatures**: `GammaTradeMarket._executeTrade / _verifyOrder`, `PerpMarketV1.executeOrderV3 /
  _verifyOrderV3`, `ResolvedOrder.validate`, `Permit2Lib.toPermit`.
- **Settlement value flow**: `SettlementCallbackLib.execSettlement / sell / buy`, `UniswapSettlement`.
- **Slippage / MEV**: `SlippageLib.checkPrice`.
- **Dutch-auction pricing**: `DecayLib.decay / decay2`, `GammaTradeMarketLib.calculateSlippageTolerance /
  validateHedgeCondition / validateCloseCondition`.

## Pre-registered blind sample (16 surfaces) — frozen BEFORE any blind run
Chosen for severity spread (genuine-High territory: liquidation, oracle, settlement value-flow, locker auth;
Medium territory: slippage, dutch-auction decay, interest timing, auto-hedge conditions). Each is traced blind by
one Sonnet subagent on production `deep_trace.md` + verbatim source — **no finding details supplied**.

| id | file | function(s) under trace | area |
|---|---|---|---|
| predy-01 | `PredyPool.sol` | `trade` | trade entry / value-flow / reentrancy |
| predy-02 | `PredyPool.sol` | `reallocate` | reallocation accounting |
| predy-03 | `PredyPool.sol` | `execLiquidationCall` | liquidation entry |
| predy-04 | `PredyPool.sol` | `supply` / `withdraw` | supply accounting |
| predy-05 | `PredyPool.sol` | `take` (`onlyByLocker`) | locker auth / value-flow |
| predy-06 | `libraries/logic/LiquidationLogic.sol` | `liquidate` / `checkVaultIsDanger` | liquidation / solvency |
| predy-07 | `libraries/PositionCalculator.sol` | `isLiquidatable` / `calculateMinMargin` | solvency math |
| predy-08 | `libraries/logic/TradeLogic.sol` | `trade` / `callTradeAfterCallback` | settlement callback / reentrancy |
| predy-09 | `PriceFeed.sol` | `getSqrtPrice` | Pyth oracle |
| predy-10 | `libraries/UniHelper.sol` | `getSqrtTWAP` / `callUniswapObserve` | Uniswap TWAP oracle |
| predy-11 | `libraries/SlippageLib.sol` | `checkPrice` | slippage / MEV |
| predy-12 | `base/SettlementCallbackLib.sol` | `execSettlement` / `sell` / `buy` | settlement value flow |
| predy-13 | `markets/gamma/GammaTradeMarket.sol` | `_executeTrade` / `_verifyOrder` | order auth / signature |
| predy-14 | `markets/perp/PerpMarketV1.sol` | `executeOrderV3` / `_verifyOrderV3` | perp order auth |
| predy-15 | `libraries/orders/DecayLib.sol` (+ `GammaTradeMarketLib.calculateSlippageTolerance`) | `decay` / `decay2` | dutch-auction pricing |
| predy-16 | `libraries/Perp.sol` | `reallocate` / `settleUserBalance` | share/interest accounting |

Spread: liquidation/solvency 3 · trade-accounting 4 · oracle 2 · order-auth 2 · settlement 2 · slippage 1 ·
auction 1 · supply 1. Bounded sample → out-of-sample **signal**, not full recall (recorded caveat).
