// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// SAFE (no FP): deployer disables the initializer, transfers ownership to the bridge controller, and the
// controller retains upgrade authority. Full lifecycle handled locally → lifecycle_cleared_with_local_proof.
import "openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol";
contract SafeDeployer {
    function deployManaged(address bridgeOwner) external returns (address) {
        Managed impl = new Managed();
        impl._disableInitializers();
        address proxy = address(new ERC1967Proxy(address(impl), abi.encodeWithSelector(Managed.initialize.selector)));
        Managed(proxy).transferOwnership(bridgeOwner); // ownership handed to the in-scope controller
        Managed(proxy).upgradeToAndCall(address(impl), ""); // controller retains upgrade authority
        return proxy;
    }
}
