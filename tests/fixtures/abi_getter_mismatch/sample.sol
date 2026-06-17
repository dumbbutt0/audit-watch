// SPDX-License-Identifier: MIT
// Fixture for the abi_getter_mismatch lens. Distinct names per scenario avoid cross-pairing.
pragma solidity ^0.8.0;

// --- Scenario A: positive (Hybra M-07 shape) — interface decl vs public-mapping auto-getter, with a call site
interface IVoter {
    function poolVote(uint tokenId) external view returns (address[] memory);
}

contract VoterV3 {
    mapping(uint256 => address[]) public poolVote; // auto-getter: poolVote(uint256,uint256) -> address
}

contract Caller {
    address voter;
    function claimRewards() external view returns (address[] memory) {
        return IVoter(voter).poolVote(123); // cast-and-call through the interface
    }
}

// --- Scenario B: explicit override resolves the mismatch (safe)
interface IReg {
    function items(uint id) external view returns (address[] memory);
}

contract RegImpl {
    mapping(uint256 => address[]) public items;
    function items(uint256 id) external view returns (address[] memory) {
        return items[id];
    }
}

// --- Scenario C: generated getter matches the interface (safe)
interface IMatch {
    function cell(uint a, uint b) external view returns (address);
}

contract MatchImpl {
    mapping(uint256 => address[]) public cell; // auto-getter: cell(uint256,uint256) -> address  (matches IMatch)
}

// --- Scenario D: same name + mismatch but NO plausible binding (no call site, no name pairing) -> low/context
interface IOrphan {
    function orphan(uint id) external view returns (address[] memory);
}

contract LonelyImpl {
    mapping(uint256 => address[]) public orphan; // pairs with neither a call site nor IOrphan's name
}
