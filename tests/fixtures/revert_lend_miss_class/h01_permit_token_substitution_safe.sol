// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract VaultSafe {
    address public asset;
    function deposit(uint256 assets, bytes calldata permitData) external {
        (Permit memory p, bytes memory sig) = abi.decode(permitData, (Permit, bytes));
        require(p.permitted.token == asset, "wrong token");   // received == paid token enforced
        permit2.permitTransferFrom(p, Details(address(this), assets), msg.sender, sig);
        _mint(msg.sender, assets);
    }
}
