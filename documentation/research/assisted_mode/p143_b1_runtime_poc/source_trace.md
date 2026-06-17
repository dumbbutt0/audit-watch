# P143 — Source Trace

File: `audits/noya-2024-04-eval/contracts/2024-04-noya/contracts/helpers/valueOracle/NoyaValueOracle.sol`

## Public entrypoint (line 71)
```solidity
function getValue(address asset, address baseToken, uint256 amount) public view returns (uint256) {
    if (asset == baseToken || amount == 0) { return amount; }
    address[] memory sources = priceRoutes[asset][baseToken];   // the route
    return _getValue(asset, baseToken, amount, sources);
}
```

## Vulnerable multi-hop loop (lines 81–93)
```solidity
function _getValue(address asset, address baseToken, uint256 amount, address[] memory sources)
    internal view returns (uint256 value)
{
    uint256 initialValue = amount;
    address quotingToken = asset;
    for (uint256 i = 0; i < sources.length; i++) {
        initialValue = _getValue(asset, sources[i], initialValue);   // <-- static `asset`, not quotingToken
        quotingToken = sources[i];                                   // advanced but only used after the loop
    }
    return _getValue(quotingToken, baseToken, initialValue);
}
```
The per-hop call (line 89) always uses the **start** `asset` as the from-token. `quotingToken` is advanced
(line 90) but only consumed in the final hop (line 92). Therefore:
- **i = 0** legitimately uses `asset` (the value is still asset-denominated) — correct.
- **i ≥ 1** should price `quotingToken → sources[i]` but instead prices `asset → sources[i]` on an amount already
  denominated in `sources[i-1]` — **wrong from-token** whenever the two oracle paths differ.
⇒ the divergence requires a route with **≥ 2 sources**.

## Inner resolver (lines 95–110)
`_getValue(quotingToken, baseToken, amount)` resolves an oracle from `priceSource[qt][base]` (then reversed, then
defaults) and returns `oracle.getValue(qt, base, amount)`.

## How to reach it in a test
- Deploy `NoyaValueOracle(PositionRegistry registry)`. The valuation read path **never reads `registry`** — only
  the `onlyMaintainer` setters do (`updateAssetPriceSource`, `updatePriceRoute`, `updateDefaultPriceSource`, via
  `registry.hasRole(registry.MAINTAINER_ROLE(), msg.sender)`).
- So a **stub registry** whose `hasRole→true` / `MAINTAINER_ROLE→0x00` lets the **real setters** run; the real
  `getValue` then executes unmodified.
- Oracle connectors implement the tiny real interface `INoyaValueOracle.getValue(asset, base, amount)`.

## Minimum state
Register `priceSource` for each directed pair on the route + a `priceRoute[asset][base] = sources`; provide
per-pair prices via a mock oracle. No other protocol state needed.
