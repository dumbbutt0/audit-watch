# P137 — Blind Source Packet (H-03 target)

Answer-key-free, function-scoped bundle given to the blind subagent. No bug description, severity, issue id, or
prior-phase hints. Candidate: `NoyaValueOracle._getValue(asset, baseToken, amount, sources)`.

```solidity
// NoyaValueOracle.sol  (helpers/valueOracle/NoyaValueOracle.sol)  — pragma 0.8.20
contract NoyaValueOracle is INoyaValueOracle {
    mapping(address => INoyaValueOracle) public defaultPriceSource;
    mapping(address => mapping(address => address[])) public priceRoutes;          // asset => base => [hop tokens]
    mapping(address => mapping(address => INoyaValueOracle)) public priceSource;   // quoting => base => oracle

    // public entry
    function getValue(address asset, address baseToken, uint256 amount) public view returns (uint256) {
        if (asset == baseToken || amount == 0) {
            return amount;
        }
        address[] memory sources = priceRoutes[asset][baseToken];
        return _getValue(asset, baseToken, amount, sources);
    }

    // CANDIDATE: multi-hop value computation along `sources`
    function _getValue(address asset, address baseToken, uint256 amount, address[] memory sources)
        internal view returns (uint256 value)
    {
        uint256 initialValue = amount;
        address quotingToken = asset;
        for (uint256 i = 0; i < sources.length; i++) {
            initialValue = _getValue(asset, sources[i], initialValue);
            quotingToken = sources[i];
        }
        return _getValue(quotingToken, baseToken, initialValue);
    }

    // callee: single-hop oracle lookup + conversion
    function _getValue(address quotingToken, address baseToken, uint256 amount) internal view returns (uint256) {
        INoyaValueOracle oracle = priceSource[quotingToken][baseToken];
        if (address(oracle) == address(0)) oracle = priceSource[baseToken][quotingToken];
        if (address(oracle) == address(0)) oracle = defaultPriceSource[baseToken];
        if (address(oracle) == address(0)) oracle = defaultPriceSource[quotingToken];
        if (address(oracle) == address(0)) revert NoyaOracle_PriceOracleUnavailable(quotingToken, baseToken);
        return oracle.getValue(quotingToken, baseToken, amount);
    }
}

// interface
interface INoyaValueOracle {
    function getValue(address asset, address baseCurrency, uint256 amount) external view returns (uint256);
}
```

Intended semantics (neutral): `getValue(asset, base, amount)` converts `amount` of `asset` into `base`, routed
through the ordered intermediate tokens in `priceRoutes[asset][base]` (e.g. `[s0, s1]` means
asset → s0 → s1 → base). Each `priceSource[X][Y]` is a per-pair oracle.
