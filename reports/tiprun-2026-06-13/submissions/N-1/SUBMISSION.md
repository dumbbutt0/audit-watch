<!--
PLATFORM-PASTE-READY version of the N-1 report. Plain prose + standard code fences only. Paste each labelled
section into the matching platform field. Facts are identical to the PoC (validated, all tests passing). Copy from
the RAW file, not a rendered preview.
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Broken Access Control (BAC) → Privilege Escalation

# Field: Severity
High

# Field: Title
User can self-mint ALLOW_ADMIN during registration, then grant withdraw rights on any account and drain collateral

# Field: Vulnerability details

`PermissionsTransLib.processAdminSetSignerPermissions` authorizes the admin permission-change by checking that the
recovered EIP-712 signer holds `ALLOW_ADMIN` on the account named in `txData.adminAccountId`:

```solidity
require(
    signerManager.checkSignerPermissionsAndNonce(
        txData.adminAccountId, recovered, txData.nonce, SignerPermissions.ALLOW_ADMIN
    ),
    "Permissions: signer lacks Admin permission on admin account"
);
signerManager.setSignerPermissions(txData.targetAccountId, txData.signer, txData.mask);
```

`adminAccountId` is an attacker-supplied field. There is no on-chain check that it equals the canonical/global admin
account, so the function trusts whatever account the caller names as "the admin account." The attacker therefore only
needs `ALLOW_ADMIN` on *some* account they control — which they can mint for themselves at registration, because the
registration path applies no delegation gate to the initial signer mask (unlike the owner-delegated
`processSetSignerPermissions` / `processAddSignersWithPermissions`, which enforce that an owner may only grant bits
it already holds).

## Impact

Complete failure of the permission model. An unprivileged user can grant themselves ALLOW_WITHDRAW / ALLOW_TRANSFER
(or ALLOW_ADMIN) on **any** account and drain its collateral.

The contract entry point is the trusted txBatcher, but the transactions it processes are user-signed typed-data
actions. The PoC submits through that same relay path. No contract-side check rejects the malicious registration,
the admin permission update, or the victim withdrawal once relayed — the backend is an off-chain mitigation, not
part of the on-chain authorization model.

This is proven against a deployment with a **real canonical admin account configured** (the PoC bootstraps the
admin via `setAdminAddress` + admin registration, so `signerManager.adminAccountId()` is a genuine, distinct
account). The attack does not depend on the canonical admin being unset: gap (b) never compares the caller-supplied
`adminAccountId` against `signerManager.adminAccountId()`, so the attacker uses their own account id and still
passes the admin check.

## Exploit path

1. REGISTER_ACCOUNT — attacker registers their own account A with an ALLOW_ADMIN session key.
2. ADMIN_SET_SIGNER_PERMISSIONS — attacker submits adminAccountId = A (their own), targetAccountId = victim,
   signer = attackerKey, mask = ALLOW_WITHDRAW. The check passes because they hold ALLOW_ADMIN on A.
3. WITHDRAWAL — attacker signs a withdrawal for the victim to an attacker address and drains it.

## Root cause

`adminAccountId` is not bound to the canonical admin account, and registration-time signer masks are not delegation-
gated, so admin can be self-conferred and then used to authorize changes to any target account.

## Suggested fix

Bind `adminAccountId` to `signerManager.adminAccountId()` in `processAdminSetSignerPermissions`; apply the
owner-holds-the-bit delegation gate to registration-time masks (or strip ALLOW_ADMIN from registration-assignable
masks).

# Field: Validation steps

The PoC runs against the project's own contracts in a local Foundry harness; all tests pass. From the harness root:

```bash
forge test --match-contract PoC_PermissionEscalation -vv
```

What it proves:

- `test_PoC_nonAdminMintsAllowAdminAndDrainsVictim`: the harness first configures a **real canonical admin account**
  (`setAdminAddress` + admin registration → `adminAccountId() == 1000`). An attacker starting with zero privileges
  then registers their own account (uid 666) with an ALLOW_ADMIN session key, uses ADMIN_SET_SIGNER_PERMISSIONS
  (naming **their own** account 666 as `adminAccountId`, not the canonical admin 1000) to grant ALLOW_WITHDRAW on a
  victim, and withdraws the victim's full collateral (5000). The test asserts the attacker account is not the
  canonical admin and that the canonical admin is unchanged.

Captured output (real run, all passing):

```
Ran 3 tests for test/PoC_PermissionEscalation.t.sol:PoC_PermissionEscalation
[PASS] testResolutionCheck()
[PASS] testSyntheticAssetInfoCRUD()
[PASS] test_PoC_nonAdminMintsAllowAdminAndDrainsVictim()
Logs:
  canonical admin account id: 1000
  attacker started with zero privileges; drained victim collateral: 5000

Suite result: ok. 3 passed; 0 failed; 0 skipped
```

# Field: Attachments
- PoC_PermissionEscalation.t.sol
- poc_output.log   (captured passing run)
