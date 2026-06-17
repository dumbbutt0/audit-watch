# P133 — Specialist Findings (source-grounded, in-session)

## Recall arm — confirmed specialist findings (graded HIT/PARTIAL)
The 5 useful detections, as a specialist would write them (the 2 HITs are the most defensible):

- **MorphoBlueConnector._getPositionTVL (HIT, arithmetic/accounting).** `tvl = value(loanToken, supplyAmount +
  borrowAmount + collateral)`. Debt (`borrowAmount`) is **added** to the position value instead of subtracted;
  a borrower's outstanding debt inflates reported TVL. ICE: Impact High (mis-valuation → mint/withdraw mis-price),
  Confidence High (explicit sign error, sibling `SiloConnector` does `deposit − borrow`), Exploitability
  conditional on a Morpho borrow position. → matches awarded H-19.
- **NoyaValueOracle._getValue (HIT, oracle/logic).** Multi-hop loop advances `quotingToken=sources[i]` but feeds
  `_getValue(asset, sources[i], …)` with the static `asset` each iteration, so a 2+ hop conversion path is
  computed wrong (asset→s1 instead of s0→s1). ICE: Impact High (valuation), Confidence High (the in-loop
  `quotingToken` is written but only read after the loop — a clear dead-write). → matches awarded H-03.
- **AerodromeConnector._getPositionTVL (PARTIAL).** Uses only `pool.balanceOf(this)`; if the connector stakes LP
  in an Aerodrome gauge, that balance is omitted → TVL undercount. Requires confirming the deposit path stakes.
- **SiloConnector._getPositionTVL (PARTIAL).** Treats Silo `collateralToken`/`debtToken` `balanceOf` as
  underlying amounts; these are share tokens (need toAssets). Needs Silo share-model confirmation.
- **PendleConnector._getPositionTVL (PARTIAL).** SY+LP+PT+YT→underlying composition; a conservation reviewer
  flags it as a complex ≥4-term aggregate worth verifying; the exact error needs Pendle rate depth.

## Recall arm — visible-but-MISS (the deep-reasoning gap)
- **BalancerConnector._getPositionTVL / totalLpBalanceOf (H-13/H-14, MISS):** weighted-pool single-token
  extrapolation and staked/held composition — formulas look plausible; the specific errors are subtle.
- **ChainlinkOracleConnector.getValue (H-01, MISS):** ETH/USD-route decimals (18 vs 8) across multi-hop — a units
  bug requiring decimal-flow tracing, not surface-visible.

## FP arm — non-awarded boosted (52 distinct)
| Disposition | n | Meaning |
|---|---|---|
| needs_human | 39 | on-class value/TVL/accounting helpers (`_getPositionTVL` on Aave/Camelot/Compound/Curve/Dolomite/Frax/Gearbox/Lido/UNIv3, `LPToUnder`, `getBorrowBalanceInBase`, `neededAssetsForWithdraw`, `_getValue`, …) — same surface as the awarded class; valid-vs-FP needs a human + protocol depth → routed to `human_review_queue.jsonl` |
| clear | 13 | non-on-class helpers (`onERC721Received`, `getData`, `getCurrentLiquidity`, `getTokenDecimals`, `latestRoundData`, `_lzReceive`, `_forward`, …) — low-value, fast clear |
| speculative-reject | 0 | **no boosted function warranted a fabricated/speculative high-severity flag** |

**FP-tendency ≈ 0:** the boost produced **zero speculative FPs**. Its cost is **reviewer load** (39 legitimate
on-class review items, several plausibly valid-unawarded), not false positives — consistent with P131/P132 (the
boost re-ranks read/value logic; it adds no new state-mutating paths that generate speculative flags).
