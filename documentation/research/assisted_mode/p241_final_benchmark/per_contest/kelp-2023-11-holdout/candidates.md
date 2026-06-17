# P241 — Kelp DAO (C4 2023-11) blind base candidates (pre-reveal)

Architecture: LRT restaking (LST deposits → mint rsETH; assets delegated to EigenLayer via NodeDelegators). In-scope
9 files / 46 fns; read in full (small target). Answer key NOT opened.

| ID | Title | Contract:fn | Sev | Conf |
|---|---|---|---|---|
| KELP-01 | `ChainlinkPriceOracle.getAssetPrice` uses deprecated `latestAnswer()` with NO staleness/round/heartbeat/negative check → stale or zero price → mis-mint rsETH / wrong rsETH price | ChainlinkPriceOracle:getAssetPrice (37) | **Medium** | High |
| KELP-02 | `depositAsset` has no `minRsETHOut`/slippage protection → depositor takes loss if exchange rate moves / is sandwiched | LRTDepositPool:depositAsset (119) | Medium | Med |
| KELP-03 | rsETH price inflatable via direct asset donation to the deposit pool (`getTotalAssetDeposits` counts `balanceOf`) → new depositors mint fewer rsETH | LRTOracle:getRSETHPrice (52) + LRTDepositPool | Low/Med | Med |
| KELP-05 | cross-asset price/decimals: `getRSETHPrice` sums `assetAmt*assetER` and mint uses `assetPrice/rsETHPrice` assuming uniform 18-dec feeds → non-18-decimal LST or feed mis-scales rsETH | LRTOracle/LRTDepositPool | Low/Med | Med |

Advisory lenses on kelp: Safe 0, hostile 0 (no Safe guard; transfers are deposit `transferFrom` from msg.sender / admin transfer to NDC — out of lens domains). Lens contribution expected 0.
Harness: BLOCKED_BY_BUILD (no foundry deps shipped). Proof attempts 0.
