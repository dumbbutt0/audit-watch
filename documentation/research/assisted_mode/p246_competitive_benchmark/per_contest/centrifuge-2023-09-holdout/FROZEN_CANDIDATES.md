# centrifuge-2023-09-holdout — FROZEN CANDIDATES (blind, pre-reveal)

Architecture: cross-chain (Axelar/XCM) RWA liquidity pools — async ERC4626 LiquidityPool + InvestmentManager
(orderbook/epoch) + PoolManager + Gateway/Messages/Routers + Tranche/RestrictionManager. Sealed-key hash
81cb03b04d084cbc (not opened). **Coverage note:** 329 critical in-scope items; I fully read the two core
contracts (InvestmentManager 74, LiquidityPool 68) but NOT the full gateway/message/router/token/restriction
layer → under P245 enforcement this contest is **coverage-INCOMPLETE** (≈45% critical read). Recorded
honestly; misses in unread layers are Coverage-attributed. Advisory lenses: 0 (all 3).

## Candidates (base hunt, core contracts)
| id | sev | locus | mechanism |
|---|---|---|---|
| C-M1 | Medium | InvestmentManager.requestDeposit / requestRedeem | calls `poolManager.isAllowedAsPoolCurrency(...)` but **ignores the return value** (no `require`) → deposit/redeem requests proceed with an unsupported pool currency. |
| C-M2 | Medium | InvestmentManager.convertToShares / convertToAssets | both marked `auth` → the EIP4626 `convertToShares/convertToAssets` views (exposed via LiquidityPool) revert for normal/external callers → EIP4626 compliance break / integrator breakage. |
| C-M3 | Medium | LiquidityPool.withApproval / redeem / withdraw / requestRedeem | `withApproval(owner)` requires `msg.sender == owner`; there is no allowance/operator path → EIP4626 delegated withdraw/redeem impossible; NatSpec ("owner or ward") diverges from code. |
| C-H1 | Medium | InvestmentManager deposit/redeem price (`calculateDepositPrice` avg + `_decreaseDepositLimits` floor-to-0) | per-user average price over accumulated epochs + decrease-limits clamping to 0 introduces rounding drift; repeated partial processing can leave residual maxMint/maxDeposit mispricing → small over-mint / over-withdraw (precision). Lower confidence. |
| C-L1 | Low | LiquidityPool.mint | `require(receiver == msg.sender)` is commented out → anyone can process another user's mint to its receiver. |
| C-L2 | Low | InvestmentManager.handleExecutedCollectInvest | missing `_currency == asset()` check (present in decrease handlers). |

## Gate / proof status
P245 gate: would **BLOCK** (coverage incomplete: ~142/329 critical read). Proof: BLOCKED_BY_BUILD.
FREEZE: final pre-reveal.
