// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;
// H-05: leave() pays a genesisBalance (a SUPPLY amount) out of collateralSource (wrong asset source).
contract H05 {
    AssetSource internal collateralSource; AssetSource internal supplySource;
    mapping(address => uint256) internal genesisBalance;
    function leave() external {
        uint256 amount = genesisBalance[msg.sender];                                             // amount_origin = supply/genesis
        genesisBalance[msg.sender] = 0;
        collateralSource.transferFunds(msg.sender, amount);                                       // VULN: transfer from collateral
    }
}
contract H05Safe {
    AssetSource internal collateralSource; AssetSource internal supplySource;
    mapping(address => uint256) internal genesisBalance;
    function leave() external {
        uint256 amount = genesisBalance[msg.sender]; genesisBalance[msg.sender] = 0;
        supplySource.transferFunds(msg.sender, amount);                                           // SAFE: supply amount from supply source
    }
}
interface AssetSource { function transferFunds(address to, uint256 amount) external; }
