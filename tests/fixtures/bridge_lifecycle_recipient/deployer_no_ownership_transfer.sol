// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// VULNERABLE (AK-H4): in-scope deployer creates an upgradeable ERC721 proxy but never transfers ownership
// to the bridge nor disables the initializer nor retains upgrade authority. The deployed token's lifecycle
// is then uncontrollable by the bridge — audit-relevant THROUGH this in-scope deployer.
import "openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol";
contract CollectionDeployer {
    function deployCollection(string memory name, string memory symbol) public returns (address) {
        address impl = address(new ERC721Bridgeable());
        bytes memory dataInit = abi.encodeWithSelector(ERC721Bridgeable.initialize.selector, abi.encode(name, symbol));
        return address(new ERC1967Proxy(impl, dataInit)); // no _transferOwnership, no _disableInitializers, no upgrade authority
    }
}
