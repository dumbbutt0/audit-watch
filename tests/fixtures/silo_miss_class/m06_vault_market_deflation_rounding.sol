// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Silo M-06 (reconstructed shape): the vault's user-share math is OZ-offset-safe, but when the vault SUPPLIES
// to the underlying market the market rounds the strategy-receipt DOWN, and that downstream rounding loss is
// borne by the vault (socialized to depositors). The user-share layer looks fine; the bug lives at the
// vault->market deposit layer. The vault_market_inflation_deflation checklist (vault_market_deposit_traced /
// market_rounding / strategy_receipt_amount / downstream_rounding_loss / loss_attribution) is what catches it.
interface IMarket {
    // market mints shares = assets * totalShares / totalAssets, rounding DOWN
    function supplyShares(uint256 assets) external returns (uint256 marketShares);
}

contract VaultMarketDeflation {
    IMarket public market;
    uint256 public totalAssets;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    // user->vault deposit: OZ-style, fine in isolation
    function deposit(uint256 assets, address receiver) external returns (uint256 userShares) {
        userShares = totalSupply == 0 ? assets : assets * totalSupply / totalAssets;
        balanceOf[receiver] += userShares;
        totalSupply += userShares;

        // BUG: vault->market supply. The market rounds marketShares down; the dust difference between
        // `assets` credited to the user and the value actually received from the market is never reconciled,
        // so a repeated tiny-deposit attacker deflates the vault's backing.
        uint256 marketShares = market.supplyShares(assets);
        totalAssets += marketShares; // credits market shares 1:1 as assets, ignoring the rounding shortfall
    }
}
