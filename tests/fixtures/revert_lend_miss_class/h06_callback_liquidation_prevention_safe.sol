// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract VaultSafe {
    function liquidate(uint256 tokenId) external {
        _settle(tokenId, msg.sender);
        // pull-payment: owner must claim the remainder; liquidation cannot be blocked by a callback
        pendingReturn[tokenOwner[tokenId]] = tokenId;
    }
}
