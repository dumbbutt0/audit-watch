[Gas-1] Optimizing findCreate2Address with Assembly for Efficient Contract Address Computation
The following is the optimized findCreate2Address function with all enhancements:
```solidity
File: repos/protocol-contracts/evm/tools/ImmutableCreate2Factory.sol
function findCreate2Address(
        bytes32 salt,
        bytes calldata initCode
    ) external view returns (address deploymentAddress) {
        deploymentAddress = computeAddress(salt, keccak256(abi.encodePacked(initCode)), address(this));
        // return null address to signify failure if contract has been deployed.
        if (_deployed[deploymentAddress]) {
            return address(0);
        }
    }
 function computeAddress(bytes32 salt, bytes32 bytecodeHash, address deployer) private pure returns (address addr) {
        assembly {
            let ptr := mload(0x40) // Get free memory pointer
            mstore(add(ptr, 0x40), bytecodeHash)
            mstore(add(ptr, 0x20), salt)
            mstore(ptr, deployer) // Right-aligned with 12 preceding garbage bytes
            let start := add(ptr, 0x0b) // The hashed data starts at the final garbage byte which we will set to 0xff
            mstore8(start, 0xff)
            addr := keccak256(start, 85)
        }
    }

```

[Gas-2] Merge findCreate2Address and findCreate2AddressViaHash logic
Using findCreate2Address call findCreate2AddressViaHash like this:
```

    function findCreate2Address(
        bytes32 salt,
        bytes calldata initCode
    ) external view returns (address deploymentAddress) {
     return findCreate2AddressViaHash(salt,keccak256(abi.encodePacked(initCode)));
}
```