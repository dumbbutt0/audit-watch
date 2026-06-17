// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// H-02: _cleanupLoan sends the NFT (safeTransferFrom) BEFORE collateral-config state is finalized; the
// receiver's onERC721Received re-enters and manipulates tokenConfigs[].totalDebtShares.
contract Vault {
    function _cleanupLoan(uint256 tokenId, address owner) internal {
        nft.safeTransferFrom(address(this), owner, tokenId);  // <-- callback BEFORE the update below
        _updateAndCheckCollateral(tokenId, 0);                // collateral config mutated after the call
    }
}
