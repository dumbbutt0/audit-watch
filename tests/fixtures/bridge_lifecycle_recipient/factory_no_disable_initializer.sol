// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// VULNERABLE: factory deploys a proxy + calls initialize but never _disableInitializers on the implementation.
import "openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol";
contract VaultFactory {
    function createVault(address asset) external returns (address) {
        address impl = address(new Vault());
        return address(new ERC1967Proxy(impl, abi.encodeWithSelector(Vault.initialize.selector, asset)));
    }
}
