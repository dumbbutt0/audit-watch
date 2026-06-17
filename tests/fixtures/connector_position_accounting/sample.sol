// SPDX-License-Identifier: MIT
// Fixture for the connector_position_accounting lens. Distinct contract names per scenario.
pragma solidity ^0.8.0;

// --- Scenario A1: external_reader_aggregate, MEDIUM (NOYA H-11 SNX shape) — aggregate from external reader, no debt
contract SnxLike {
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256 tvl) {
        (uint256 totalDeposited, uint256 totalAssigned,) = proxy.getAccountCollateral(accountId, collateralType);
        tvl = _getValue(collateralType, base, totalDeposited + totalAssigned);
    }
}

// --- Scenario A2: external_reader_aggregate, HIGH (NOYA H-19 Morpho shape) — debt term added as asset
contract MorphoLike {
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256 tvl) {
        Market memory market = morphoBlue.market(id);
        Position memory pos = morphoBlue.position(id, address(this));
        uint256 borrowAmount = uint256(pos.borrowShares).toAssetsUp(market.totalBorrowAssets, market.totalBorrowShares);
        uint256 supplyAmount = uint256(pos.supplyShares).toAssetsUp(market.totalSupplyAssets, market.totalSupplyShares);
        tvl = _getValue(loanToken, base, supplyAmount + borrowAmount + collateral);
    }
}

// --- Scenario B: position_tvl_product_div, MEDIUM (NOYA H-13 Balancer shape) — product/div, no aggregate
contract BalancerLike {
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256) {
        uint256 lpBalance = totalLpBalanceOf(pool);
        uint256 _totalSupply = IERC20(pool.pool).totalSupply();
        uint256 _weight = pool.weights[pool.tokenIndex];
        uint256 token1bal = valueOracle.getValue(pool.tokens[pool.tokenIndex], base, bal);
        return (((1e18 * token1bal * lpBalance) / _weight) / _totalSupply);
    }
}

// --- Scenario C: registry_key_mismatch, MEDIUM (NOYA H-12 shape) — create keyed by msg.sender, remove by calculatorConnector
contract RegistryLike {
    function updateHoldingPosition(uint256 vaultId, bytes32 _positionId, bytes calldata _data, bool removePosition)
        public returns (uint256)
    {
        bytes32 holdingPositionId = keccak256(abi.encode(msg.sender, _positionId, _data));
        uint256 positionIndex = vault.isPositionUsed[holdingPositionId];
        if (removePosition) {
            vault.isPositionUsed[keccak256(abi.encode(
                vault.holdingPositions[positionIndex].calculatorConnector,
                vault.holdingPositions[positionIndex].positionId,
                vault.holdingPositions[positionIndex].data
            ))] = positionIndex;
        }
    }
}

// --- Scenario D: pure getter negative — no arithmetic
contract GetterLike {
    function getValue(address t) external view returns (address) {
        return _v;
    }
}

// --- Scenario E: NON-TVL-named product/division — name gate must exclude it
contract PricingLike {
    function quotePrice(uint a, uint b, uint c) public pure returns (uint) {
        return a * b / c;
    }
}

// --- Scenario F: TVL-named but single term, no aggregate / no product-div — neither shape fires
contract SingleTermTVL {
    function _getPositionTVL(HoldingPI memory p, address base) public view returns (uint256) {
        return _getValue(token, base, IERC20(token).balanceOf(address(this)));
    }
}
