// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {MerkleProof} from "openzeppelin-contracts/contracts/utils/cryptography/MerkleProof.sol";

import {ICarthaAccessControl} from "./interfaces/ICarthaAccessControl.sol";
import {ICarthaParentVault} from "./interfaces/ICarthaParentVault.sol";
import {ICarthaErrors} from "./interfaces/ICarthaErrors.sol";
import {Roles} from "./diamond/Roles.sol";

/**
 * @title CarthaForceExit
 * @notice Satellite contract that holds eviction / underperformer merkle roots
 *         and drives forced lock liquidations on a CarthaParentVault.
 * @dev    Extracted from the parent vault to keep the parent under EIP-170. The
 *         parent vault grants this contract Roles.FORCE_EXITER so it can call
 *         CarthaParentVault.executeForceExit. Leaf format mirrors the child
 *         vault: keccak256(abi.encode(owner, category)).
 */
contract CarthaForceExit is ICarthaErrors {
    /// @notice Penalty applied on underperformer force-exits (5%, in basis points).
    uint256 public constant UNDERPERFORMER_PENALTY_BPS = 500;

    /// @notice Parent vault this satellite operates against.
    ICarthaParentVault public immutable parentVault;
    /// @notice Access-control diamond shared with the parent vault.
    ICarthaAccessControl public immutable diamond;
    /// @notice Category bound at construction (read once from the parent).
    bytes32 public immutable category;

    /// @notice Merkle root of deregistered miners (full payout, no penalty).
    bytes32 public evictionRoot;
    /// @notice Merkle root of underperforming miners (penalty applied).
    bytes32 public underperformerRoot;

    event ParentEvictionRootSet(bytes32 newRoot);
    event ParentUnderperformerRootSet(bytes32 newRoot);

    modifier onlyRole(uint8 role) {
        if (!diamond.hasRole(role, msg.sender)) revert Unauthorized();
        _;
    }

    constructor(address parentVault_, address diamond_) {
        if (parentVault_ == address(0) || diamond_ == address(0)) revert ZeroAddress();
        parentVault = ICarthaParentVault(parentVault_);
        diamond = ICarthaAccessControl(diamond_);
        category = ICarthaParentVault(parentVault_).category();
    }

    /**
     * @notice Force exit a deregistered miner (no penalty).
     * @dev Verifies (owner, category) against evictionRoot, then asks the parent
     *      vault to liquidate the position with zero penalty.
     */
    function forceExitParent(address owner, bytes32[] calldata merkleProof) external onlyRole(Roles.EJECTOR) {
        _verifyLeaf(owner, merkleProof, evictionRoot);
        parentVault.executeForceExit(owner, 0);
    }

    /**
     * @notice Force exit an underperforming miner (UNDERPERFORMER_PENALTY_BPS penalty).
     */
    function forceExitUnderperformerParent(address owner, bytes32[] calldata merkleProof)
        external
        onlyRole(Roles.EJECTOR)
    {
        _verifyLeaf(owner, merkleProof, underperformerRoot);
        parentVault.executeForceExit(owner, UNDERPERFORMER_PENALTY_BPS);
    }

    function setParentEvictionRoot(bytes32 newRoot) external onlyRole(Roles.ADMIN) {
        if (newRoot == bytes32(0)) revert InvalidRoot();
        evictionRoot = newRoot;
        emit ParentEvictionRootSet(newRoot);
    }

    function setParentUnderperformerRoot(bytes32 newRoot) external onlyRole(Roles.ADMIN) {
        if (newRoot == bytes32(0)) revert InvalidRoot();
        underperformerRoot = newRoot;
        emit ParentUnderperformerRootSet(newRoot);
    }

    function _verifyLeaf(address owner, bytes32[] calldata merkleProof, bytes32 root) internal view {
        bytes32 cat = category;
        bytes32 leaf;
        assembly {
            mstore(0x00, owner)
            mstore(0x20, cat)
            leaf := keccak256(0x00, 0x40)
        }
        if (!MerkleProof.verify(merkleProof, root, leaf)) revert InvalidMerkleProof();
    }
}
