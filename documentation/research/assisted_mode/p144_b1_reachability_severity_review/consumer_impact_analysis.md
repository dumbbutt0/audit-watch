# P144 — Consumer Impact Analysis

For each consumer of `getValue`/`_getValue`: impact class, how value is used, and who can trigger movement.

| consumer (file:line) | impact class | how value used | over-value benefits attacker? | under-value harms users? | admin-only action? | user can trigger value move? |
|---|---|---|---|---|---|---|
| `AccountingManager.totalAssets`/`TVL` (`:591-592`,`:627`) | **SHARE_PRICE_OR_MINT_BURN** | TVL is the ERC4626 `totalAssets` → share price denominator | yes (skews price) | yes (skews price) | no | **yes** (deposit/redeem) |
| `AccountingManager.previewDeposit` (`:239`) | **SHARE_PRICE_OR_MINT_BURN** | shares minted = f(amount, TVL) | under-valued TVL → too many shares | — | no | **yes** (deposit) |
| `AccountingManager.previewRedeem` (`:344`) | **WITHDRAWAL_OR_REDEMPTION** | assets out = f(shares, TVL) | over-valued TVL → too many assets out | yes | no | **yes** (redeem) |
| `AccountingManager` deposit limit (`:211`) | GOVERNANCE_OR_LIMITS | gate vs `depositLimitTotalAmount` | bypass/early-block | — | no | indirectly |
| `AccountingManager` profit/perf-fee (`:483-484`,`:577-583`) | **FEE_CALCULATION** | profit = TVL-based → fee shares | inflate fees | dilutes users | partly | indirectly |
| connector `getPositionTVL` (Pendle `:282`, Balancer `:171`, Dolomite `:114`, Compound `:131`, Aave `:117`, UNIv3 `:148-149`, BaseConnector `:260`) | **STRATEGY_TVL_ALLOCATION** | per-position TVL summed into vault TVL | yes (any mispriced position skews TVL) | yes | no | **yes** (via deposit/redeem) |
| `GenericSwapAndBridgeHandler` (`:110`) | guards a value-moving swap (slippage) | min-out / slippage check on a swap | a skewed check could pass a bad swap | yes | maintainer-initiated swap | partly |

## Reading
- The dominant, security-relevant path is **TVL → ERC4626 share price → deposit/redeem**: a mis-valued holding
  token (priced via a ≥2-hop route) systematically skews `totalAssets()`, so **any user** can deposit or redeem
  to capture the skew (mint cheap shares / redeem rich), at the expense of the remaining share pool. This is real,
  user-triggerable value movement — **not** view-only and **not** accounting-only.
- Direction: an **over-valued** position inflates TVL → redeem pays out more than fair (drains the pool);
  an **under-valued** position lets deposits mint more shares than fair. Both harm the honest share pool.
- No malicious admin is required for the *mis-valuation*; the *value extraction* is a normal user deposit/redeem.

## Caveat (impact magnitude unproven)
Magnitude depends on (a) whether a material-value holding token is actually priced via a ≥2-hop divergent route in
production, and (b) the size of the per-hop price divergence. Neither is established locally (route_evidence.md).
The P143 PoC proves the **oracle delta** (20e18 vs 6e18), not the **end-to-end deposit/redeem extraction**.
