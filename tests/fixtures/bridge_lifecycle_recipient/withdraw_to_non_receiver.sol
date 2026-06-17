// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// VULNERABLE (AK-M2): withdraw delivers the NFT to a recipient decoded from the L2 message via
// safeTransferFrom, with NO check that the recipient can receive ERC721 and NO retry/recovery path.
// If `to` is a contract without onERC721Received, the transfer reverts and the NFT is permanently locked.
import "openzeppelin-contracts/contracts/token/ERC721/IERC721.sol";
contract Bridge {
    function withdraw(address collection, address to, uint256 id) external {
        IERC721(collection).safeTransferFrom(address(this), to, id); // reverts if `to` lacks onERC721Received
    }
}
