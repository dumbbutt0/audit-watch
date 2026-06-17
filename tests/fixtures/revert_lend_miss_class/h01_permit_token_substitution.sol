// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// H-01: the permit signature is used to pull `asset`, but the permitted token is never checked to equal
// the vault asset → an attacker can sign a permit for a worthless token and have it accepted as the deposit.
contract Vault {
    address public asset;
    function deposit(uint256 assets, bytes calldata permitData) external {
        (Permit memory p, bytes memory sig) = abi.decode(permitData, (Permit, bytes));
        // BUG: no check that p.token == asset
        permit2.permitTransferFrom(p, Details(address(this), assets), msg.sender, sig);
        _mint(msg.sender, assets);
    }
}
