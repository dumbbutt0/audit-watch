// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// H-06: liquidate() returns the remaining position to the owner via safeTransferFrom; a malicious owner
// contract REVERTS in onERC721Received, reverting the whole liquidation → underwater loan can't be closed.
contract Vault {
    function liquidate(uint256 tokenId) external {
        _settle(tokenId, msg.sender);
        nft.safeTransferFrom(address(this), tokenOwner[tokenId], tokenId);  // owner can reject → DoS
    }
}
