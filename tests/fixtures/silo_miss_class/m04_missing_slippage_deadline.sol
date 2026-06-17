// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Silo M-04 (reconstructed shape): deposit/withdraw/redeem accept no minOut/minShares and no deadline, so a
// user's received shares/assets are whatever the exchange rate is at execution time — exposed to sandwich /
// share-price movement between quote and execution. The slippage_deadline checklist (min_out_protection /
// deadline_bound / user_bounds_received) is what catches this.
interface IMarket {
    function exchangeRate() external view returns (uint256);
    function supply(uint256 assets) external returns (uint256 shares);
}

contract VaultNoSlippage {
    IMarket public market;
    mapping(address => uint256) public shares;

    // BUG: no minShares, no deadline. Received shares depend entirely on the live rate.
    function deposit(uint256 assets, address receiver) external returns (uint256 mintedShares) {
        mintedShares = market.supply(assets);   // arbitrary route output accepted as-is
        shares[receiver] += mintedShares;
    }

    function redeem(uint256 sharesIn, address receiver) external returns (uint256 assetsOut) {
        shares[msg.sender] -= sharesIn;
        assetsOut = sharesIn * market.exchangeRate() / 1e18; // no minAssetsOut, no deadline
        receiver; // assets transferred elsewhere
    }
}
