// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract VaultSafe {
    function _cleanupLoan(uint256 tokenId, address owner) internal nonReentrant {
        _updateAndCheckCollateral(tokenId, 0);                // effects first
        nft.safeTransferFrom(address(this), owner, tokenId);  // interaction last
    }
}
