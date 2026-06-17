// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Safe equivalent: the vault credits totalAssets by the value ACTUALLY received from the market (reconciling
// the market's down-rounding), so the downstream rounding loss cannot be socialized onto existing depositors.
interface IMarket {
    function supplyShares(uint256 assets) external returns (uint256 marketShares);
    function convertToAssets(uint256 marketShares) external view returns (uint256 assets);
}

contract VaultMarketReconciled {
    IMarket public market;
    uint256 public totalAssets;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    function deposit(uint256 assets, address receiver) external returns (uint256 userShares) {
        uint256 marketShares = market.supplyShares(assets);
        uint256 received = market.convertToAssets(marketShares); // value actually backed by the market
        // mint user shares against the value truly received, not the optimistic `assets`
        userShares = totalSupply == 0 ? received : received * totalSupply / totalAssets;
        balanceOf[receiver] += userShares;
        totalSupply += userShares;
        totalAssets += received;
    }
}
