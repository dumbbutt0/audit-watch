// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../ISignerManager.sol";
import "../../account/IAccountManager.sol";
import "../../../utils/SignaturesLib.sol";
import "../../../utils/EIP712DomainLib.sol";
import "../SignerPermissions.sol";

struct SetSignerPermissionsTx {
    uint64 accountId;
    address signer;
    uint256 mask;
    uint256 nonce;
    bytes signature;
}

struct AdminSetSignerPermissionsTx {
    uint64 adminAccountId;
    uint64 targetAccountId;
    address signer;
    uint256 mask;
    uint256 nonce;
    bytes signature;
}

library PermissionsTransLib {
    bytes32 public constant SET_SIGNER_PERMISSIONS_TYPEHASH =
        keccak256("SetSignerPermissions(uint64 accountId,address signer,uint256 mask,uint256 nonce)");

    bytes32 public constant ADD_SIGNERS_WITH_PERMISSIONS_TYPEHASH =
        keccak256("AddSignersWithPermissions(uint64 accountId,address[] signers,uint256[] masks,uint256 nonce)");

    bytes32 public constant ADMIN_SET_SIGNER_PERMISSIONS_TYPEHASH = keccak256(
        "AdminSetSignerPermissions(uint64 adminAccountId,uint64 targetAccountId,address signer,uint256 mask,uint256 nonce)"
    );

    function processSetSignerPermissions(
        SetSignerPermissionsTx memory txData,
        ISignerManager signerManager,
        IAccountManager accountManager,
        address verifyingContract
    ) public {
        require(txData.signer != address(0), "Permissions: signer is zero");
        require(txData.accountId != 0, "Permissions: accountId is zero");

        bytes32 messageHash = getSetSignerPermissionsHash(txData, block.chainid, verifyingContract);
        address signer = SignaturesLib.recoverSigner(messageHash, txData.signature);
        require(
            signer == accountManager.getAddressByAccountId(txData.accountId),
            "Permissions: signer is not the account owner"
        );
        // Delegation rule: the owner may only grant permissions it holds itself.
        // Using the granted mask as the required mask enforces (ownerMask & mask) == mask,
        // and consumes the nonce. An owner who holds ALLOW_ADMIN (e.g., explicitly granted
        // by an admin via setSignerPermissions) may therefore delegate it further.
        require(
            signerManager.checkSignerPermissionsAndNonce(txData.accountId, signer, txData.nonce, txData.mask),
            "Permissions: cannot grant permissions not held, or invalid nonce"
        );
        signerManager.setSignerPermissions(txData.accountId, txData.signer, txData.mask);
    }

    struct AddSignersWithPermissionsTx {
        uint64 accountId;
        address[] signers;
        uint256[] masks;
        uint256 nonce;
        bytes signature;
    }

    function processAddSignersWithPermissions(
        AddSignersWithPermissionsTx memory txData,
        ISignerManager signerManager,
        IAccountManager accountManager,
        address verifyingContract
    ) public {
        require(txData.accountId != 0, "Permissions: accountId is zero");
        address ownerAddr = accountManager.getAddressByAccountId(txData.accountId);
        require(ownerAddr != address(0), "Permissions: owner is zero");
        require(txData.signers.length == txData.masks.length, "Permissions: length mismatch");

        bytes32 messageHash = getAddSignersWithPermissionsHash(txData, block.chainid, verifyingContract);
        address signer = SignaturesLib.recoverSigner(messageHash, txData.signature);
        require(signer == ownerAddr, "Permissions: signer is not the account owner");

        // Delegation rule: the owner may only grant permissions it holds itself.
        // Require the owner to hold the union of every granted mask (and consume the nonce).
        uint256 grantedUnion = 0;
        for (uint256 j = 0; j < txData.masks.length;) {
            grantedUnion |= txData.masks[j];
            unchecked {
                ++j;
            }
        }
        require(
            signerManager.checkSignerPermissionsAndNonce(txData.accountId, signer, txData.nonce, grantedUnion),
            "Permissions: cannot grant permissions not held, or invalid nonce"
        );

        uint256 len = txData.signers.length;
        for (uint256 i = 0; i < len;) {
            address s = txData.signers[i];
            require(s != address(0), "Permissions: signer is zero");
            require(s != ownerAddr, "Permissions: cannot add owner as signer");
            signerManager.addSignerWithPermissions(txData.accountId, s, txData.masks[i]);
            unchecked {
                ++i;
            }
        }
    }

    function getSetSignerPermissionsHash(
        SetSignerPermissionsTx memory txData,
        uint256 chainId,
        address verifyingContract
    ) public pure returns (bytes32) {
        bytes32 structHash = keccak256(
            abi.encode(SET_SIGNER_PERMISSIONS_TYPEHASH, txData.accountId, txData.signer, txData.mask, txData.nonce)
        );
        return EIP712DomainLib.toTypedDataHash(structHash, chainId, verifyingContract);
    }

    function getAddSignersWithPermissionsHash(
        AddSignersWithPermissionsTx memory txData,
        uint256 chainId,
        address verifyingContract
    ) public pure returns (bytes32) {
        // EIP-712 array encoding: hash each element, then hash the concatenation
        uint256 len = txData.signers.length;
        bytes32[] memory addrHashes = new bytes32[](len);
        for (uint256 i = 0; i < len; i++) {
            addrHashes[i] = bytes32(uint256(uint160(txData.signers[i])));
        }
        bytes32 signersHash = keccak256(abi.encodePacked(addrHashes));
        bytes32 masksHash = keccak256(abi.encodePacked(txData.masks));

        bytes32 structHash = keccak256(
            abi.encode(ADD_SIGNERS_WITH_PERMISSIONS_TYPEHASH, txData.accountId, signersHash, masksHash, txData.nonce)
        );
        return EIP712DomainLib.toTypedDataHash(structHash, chainId, verifyingContract);
    }

    function processAdminSetSignerPermissions(
        AdminSetSignerPermissionsTx memory txData,
        ISignerManager signerManager,
        IAccountManager accountManager,
        address verifyingContract
    ) public {
        require(txData.signer != address(0), "Permissions: signer is zero");
        require(txData.adminAccountId != 0, "Permissions: adminAccountId is zero");
        require(txData.targetAccountId != 0, "Permissions: targetAccountId is zero");

        bytes32 messageHash = getAdminSetSignerPermissionsHash(txData, block.chainid, verifyingContract);
        address recovered = SignaturesLib.recoverSigner(messageHash, txData.signature);

        // Verify recovered signer has Admin permission on admin account
        require(
            signerManager.checkSignerPermissionsAndNonce(
                txData.adminAccountId, recovered, txData.nonce, SignerPermissions.ALLOW_ADMIN
            ),
            "Permissions: signer lacks Admin permission on admin account"
        );

        signerManager.setSignerPermissions(txData.targetAccountId, txData.signer, txData.mask);
    }

    function getAdminSetSignerPermissionsHash(
        AdminSetSignerPermissionsTx memory txData,
        uint256 chainId,
        address verifyingContract
    ) public pure returns (bytes32) {
        bytes32 structHash = keccak256(
            abi.encode(
                ADMIN_SET_SIGNER_PERMISSIONS_TYPEHASH,
                txData.adminAccountId,
                txData.targetAccountId,
                txData.signer,
                txData.mask,
                txData.nonce
            )
        );
        return EIP712DomainLib.toTypedDataHash(structHash, chainId, verifyingContract);
    }
}
