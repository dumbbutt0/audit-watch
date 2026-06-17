# P241 — DittoETH (C4 2024-03) blind base candidates (pre-reveal)

Architecture: diamond/facet short-long stablecoin DEX (order book, shorts, redemption, liquidation, oracle). **Read
bound:** LibOracle (full); the large order/redemption/liquidation facets (LibOrders 41KB, RedemptionFacet 19KB,
BidOrdersFacet 18KB, PrimaryLiquidationFacet 12KB) NOT read — base recall here is a LOWER BOUND and the awarded
findings are most likely in those unread facets. Answer key NOT opened.

| ID | Title | Contract:fn | Sev | Conf |
|---|---|---|---|---|
| DITTO-01 | `getSavedOrSpotOraclePrice` returns a saved price if <15 min old → liquidation/redemption/matching can execute against a stale oracle price within the 15-min window | LibOracle:getSavedOrSpotOraclePrice (168) | Low/Med | Med |
| DITTO-02 | (unread surface) order-matching / redemption / liquidation accounting in LibOrders/RedemptionFacet/PrimaryLiquidationFacet — not read; likely location of awarded findings | facets/libraries | ? | Speculative |

Note: LibOracle itself is heavily hardened (Chainlink staleness + round + deviation circuit breakers + Uniswap TWAP
fallback with liquidity check) — no clean oracle flagship found in the bounded read. This contest illustrates the
bounded-read recall limit on large diamonds.

Advisory lenses on dittoeth: Safe 0, hostile 0. Lens contribution expected 0. Harness BLOCKED_BY_BUILD.
