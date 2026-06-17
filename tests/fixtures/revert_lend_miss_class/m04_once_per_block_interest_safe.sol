// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract VaultSafe {
    // charge a minimum origination/commission fee on borrow so same-block round-trips are not free
    function borrow(uint256 tokenId, uint256 assets) external {
        uint256 fee = assets * ORIGINATION_FEE_X32 / Q32;     // makes interest-free round-trip unprofitable
        _mintDebt(tokenId, assets + fee);
    }
}
