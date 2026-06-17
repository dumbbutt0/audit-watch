// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;
// H-03: writer stores under toHash(), reader looks up under toTracingId() — store-key vs read-key divergence.
contract H03 {
    mapping(bytes32 => bytes) internal s_postbox;
    function commitMessage(Env memory e) internal { s_postbox[toHash(e)] = e.data; }          // VULN writer
    function consumeMessage(Env memory e) internal view returns (bytes memory) {
        return s_postbox[toTracingId(e)];                                                      // VULN reader (different key)
    }
    function toHash(Env memory e) internal pure returns (bytes32) { return keccak256(abi.encode(e)); }
    function toTracingId(Env memory e) internal pure returns (bytes32) { return keccak256(abi.encode(e.nonce)); }
    struct Env { uint256 nonce; bytes data; }
}
contract H03Safe {                                                                              // SAFE: both sides toHash
    mapping(bytes32 => bytes) internal s_postbox;
    function commitMessage(Env memory e) internal { s_postbox[toHash(e)] = e.data; }
    function consumeMessage(Env memory e) internal view returns (bytes memory) { return s_postbox[toHash(e)]; }
    function toHash(Env memory e) internal pure returns (bytes32) { return keccak256(abi.encode(e)); }
    struct Env { uint256 nonce; bytes data; }
}
