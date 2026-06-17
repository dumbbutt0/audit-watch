// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// H-04: V3Utils.execute() manipulates a Uniswap V3 position NFT but never checks the caller owns it →
// anyone can operate on a position approved to V3Utils (stolen-position).
contract V3Utils {
    function execute(uint256 tokenId, Instructions calldata ix) external {
        // BUG: no check that msg.sender owns tokenId (or was authorized for it)
        _decreaseLiquidityAndSwap(tokenId, ix);
    }
}
