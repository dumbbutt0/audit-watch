// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;
// H-08: register() on the gateway has NO caller-authenticity check -> any address can register a subnet and
// later drain the gateway. Special-focus (gateway/register/collateral terms): a thin clear must be rejected.
contract H08Gateway {
    mapping(bytes32 => uint256) internal subnetStake;
    function register(uint256 genesisCircSupply, uint256 collateral) external payable {           // VULN: no auth
        bytes32 id = keccak256(abi.encode(msg.sender));
        subnetStake[id] = collateral;
    }
}
contract H08SafeGateway {
    mapping(bytes32 => uint256) internal subnetStake; mapping(address => bool) internal isSubnetActor;
    function register(uint256, uint256 collateral) external payable {
        require(isSubnetActor[msg.sender], "not a registered subnet actor");                      // SAFE: caller-authenticity
        subnetStake[keccak256(abi.encode(msg.sender))] = collateral;
    }
}
