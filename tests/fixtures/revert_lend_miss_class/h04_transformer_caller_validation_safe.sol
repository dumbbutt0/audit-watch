// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract V3UtilsSafe {
    function execute(uint256 tokenId, Instructions calldata ix) external {
        require(nft.ownerOf(tokenId) == msg.sender, "not owner");
        _decreaseLiquidityAndSwap(tokenId, ix);
    }
}
