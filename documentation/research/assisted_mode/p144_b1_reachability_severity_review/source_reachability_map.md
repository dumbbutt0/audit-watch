# P144 — Source Reachability Map

File refs are `audits/noya-2024-04-eval/contracts/2024-04-noya/contracts/...`.

## Entrypoints into the bug
| function | file:line | access | notes |
|---|---|---|---|
| `getValue(asset, baseToken, amount)` | `helpers/valueOracle/NoyaValueOracle.sol:71` | public view | reads `priceRoutes[asset][baseToken]` then calls the vulnerable loop |
| `_getValue(asset, baseToken, amount, sources)` | `:81` | internal view | the multi-hop loop; line 89 uses static `asset`, line 90 advances `quotingToken` |
| `_getValue(quotingToken, baseToken, amount)` | `:95` | internal view | resolves `priceSource`/`defaultPriceSource` → connector `getValue` |

## Route/source configuration (who sets the inputs)
| setter | file:line | access |
|---|---|---|
| `updatePriceRoute(asset, base, s)` | `:61` | `onlyMaintainer` |
| `updateAssetPriceSource(asset[], base[], oracle[])` | `:51` | `onlyMaintainer` |
| `updateDefaultPriceSource(base[], oracle[])` | `:37` | `onlyMaintainer` |
| `onlyMaintainer` | `:24-25` | `registry.hasRole(registry.MAINTAINER_ROLE(), msg.sender)` |

⇒ asset/base/sources arrays are **protocol-controlled (maintainer)**; not user-supplied and not selectable by a
caller (the route is keyed by `(asset, base)` mapping lookup, not a call argument).

## Consumer / call map (who consumes the value, and what it moves)
| consumer | file:line | input asset/base | route source | value consumed by | moves value? |
|---|---|---|---|---|---|
| `BaseConnector._getValue` | `helpers/BaseConnector.sol:260` | token→baseToken | `priceRoutes` | connector TVL | TVL → share price |
| `AccountingManager._getValue` | `accountingManager/AccountingManager.sol:642-646` | token→base | `priceRoutes` | `getPositionTVL` (`:632`) | **yes** |
| `AccountingManager.TVL()` | `:627-628` | — | — | `TVLHelper.getTVL` + base balance | aggregates all positions |
| `AccountingManager.totalAssets()` | `:591-592` | — | — | **ERC4626 share price** ("4626 standard to calculate the shares price") | **yes** |
| `previewDeposit(amount)` | `:239` | — | — | **shares minted on deposit** | **yes** |
| `previewRedeem(shares)` | `:344` | — | — | **assets paid on redeem** | **yes** |
| `depositLimitTotalAmount` check | `:211` | — | — | deposit gating | limits |
| profit/performance-fee calc | `:483-484`, `:577-583` | — | — | fee shares | fees |
| `PendleConnector` TVL | `connectors/PendleConnector.sol:282` | underlying→base | `priceRoutes` | position TVL | TVL → share price |
| `BalancerConnector` TVL | `connectors/BalancerConnector.sol:171` | poolToken→base | `priceRoutes` | position TVL | TVL → share price |
| `Dolomite` TVL | `connectors/Dolomite.sol:114` | token→base | `priceRoutes` | position TVL | TVL → share price |
| `CompoundConnector` TVL | `connectors/CompoundConnector.sol:131` | baseToken→base | `priceRoutes` | position TVL | TVL → share price |
| `AaveConnector` TVL | `connectors/AaveConnector.sol:117` | poolBaseToken→base | `priceRoutes` | position TVL | TVL → share price |
| `UNIv3Connector` TVL | `connectors/UNIv3Connector.sol:148-149` | token0/1→base | `priceRoutes` | position TVL | TVL → share price |
| `GenericSwapAndBridgeHandler` | `helpers/SwapHandler/GenericSwapAndBridgeHandler.sol:110` | inputToken→outputToken | `priceRoutes` | swap **slippage** check | guards a value-moving swap |

## Summary
The vulnerable valuation feeds **TVL → `totalAssets()` → ERC4626 share price → deposit (mint) / redeem (assets
out)** across the whole connector set, plus deposit limits, fees, and swap slippage. The value path to user
balances is **source-supported**. The route inputs are **maintainer-controlled**, not attacker-controlled.
