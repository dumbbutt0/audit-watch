// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Safe equivalent: deposit/redeem bound the user-received amount (minShares / minAssetsOut) and enforce a
// deadline, so the caller cannot be sandwiched into an unbounded-loss exchange.
interface IMarket {
    function exchangeRate() external view returns (uint256);
    function supply(uint256 assets) external returns (uint256 shares);
}

contract VaultWithSlippage {
    IMarket public market;
    mapping(address => uint256) public shares;

    error TooLittleOut();
    error Expired();

    function deposit(uint256 assets, address receiver, uint256 minShares, uint256 deadline)
        external
        returns (uint256 mintedShares)
    {
        if (block.timestamp > deadline) revert Expired();
        mintedShares = market.supply(assets);
        if (mintedShares < minShares) revert TooLittleOut();
        shares[receiver] += mintedShares;
    }

    function redeem(uint256 sharesIn, address receiver, uint256 minAssetsOut, uint256 deadline)
        external
        returns (uint256 assetsOut)
    {
        if (block.timestamp > deadline) revert Expired();
        shares[msg.sender] -= sharesIn;
        assetsOut = sharesIn * market.exchangeRate() / 1e18;
        if (assetsOut < minAssetsOut) revert TooLittleOut();
        receiver;
    }
}
