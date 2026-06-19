# N-1 (High) — Privilege escalation to `ALLOW_ADMIN`: any user self-mints admin and drains any account

- **Target:** TipRun contracts (off-chain-match / on-chain-settlement exchange). Commit `d5d4d2a…`.
- **Contract:** `src/core/signer/transactions/PermissionsTransLib.sol` → `processAdminSetSignerPermissions`
  (the `ADMIN_SET_SIGNER_PERMISSIONS` transaction type), with the drain leg in
  `src/core/balance/transactions/WithdrawalTransLib.sol`.
- **Severity:** High (total loss of the protocol's permission model → drain of any account's collateral).
- **PoC (passing):** `poc/PoC_PermissionEscalation.t.sol` · log `poc_output.log`.
- **Attacker:** an ordinary user who registers their own account — no pre-existing privilege required on-chain.

## Root cause
`processAdminSetSignerPermissions` is intended to be the admin escape hatch: an admin grants/changes a signer's
permission mask on a *target* account. The authorization check is:

```solidity
// PermissionsTransLib.processAdminSetSignerPermissions
require(
    signerManager.checkSignerPermissionsAndNonce(
        txData.adminAccountId, recovered, txData.nonce, SignerPermissions.ALLOW_ADMIN
    ),
    "Permissions: signer lacks Admin permission on admin account"
);
signerManager.setSignerPermissions(txData.targetAccountId, txData.signer, txData.mask);
```

The check confirms that `recovered` (the EIP-712 signer) holds `ALLOW_ADMIN` **on the account named by
`txData.adminAccountId`** — but `adminAccountId` is an *attacker-supplied field*. There is no on-chain check that
`adminAccountId` is a canonical/global admin account (e.g. `adminAccountId == SignerManager.adminAccountId()`); the
function simply trusts whatever account the caller names as the "admin account". So the attacker only needs to hold
`ALLOW_ADMIN` on *some* account they control — and they can mint exactly that for themselves at registration.

The sibling owner-delegated paths (`processSetSignerPermissions`, `processAddSignersWithPermissions`) enforce a
*delegation gate* — `checkSignerPermissionsAndNonce(accountId, signer, nonce, grantedMask)` requires
`(ownerMask & grantedMask) == grantedMask`, i.e. you can only grant bits you already hold. The registration path
that creates an account's initial session keys applies **no such gate to the registration-time mask**, so a brand-new
account can be created already holding `ALLOW_ADMIN`. `processAdminSetSignerPermissions` then never re-validates that
the named admin account is the real admin.

## Exploit path (end-to-end)
1. **`REGISTER_ACCOUNT`** — attacker registers their own account `A` with a session key whose mask includes
   `ALLOW_ADMIN` (no delegation gate strips it at registration).
2. **`ADMIN_SET_SIGNER_PERMISSIONS`** — attacker submits an `AdminSetSignerPermissionsTx` with
   `adminAccountId = A` (their own, on which they legitimately hold `ALLOW_ADMIN`), `targetAccountId = victim`,
   `signer = attackerKey`, `mask = ALLOW_WITHDRAW`. The check passes (they *do* hold `ALLOW_ADMIN` on `A`), and the
   victim now has an attacker-controlled signer with withdraw rights.
3. **`WITHDRAWAL`** — attacker signs a withdrawal for the victim account to an attacker address and drains it.

## Impact
Complete failure of the protocol's permission/authorization model. Any unprivileged user can grant themselves
withdraw/transfer/admin rights on **any** account and drain its collateral. The only thing standing between this and
realized loss is the **trusted txBatcher / backend declining to relay the transactions** — there is no on-chain
guard. On any deployment that relays user-submitted permission and withdrawal transactions, this is a direct,
permissionless-from-the-attacker's-side drain of other users' funds.

## PoC (passing)
From `../../harness/`:

```bash
forge test --match-contract PoC_PermissionEscalation -vv
```

`test_PoC_nonAdminMintsAllowAdminAndDrainsVictim`: an attacker who starts with **zero privileges** registers an
account with an `ALLOW_ADMIN` session key, uses `ADMIN_SET_SIGNER_PERMISSIONS` (naming their own account as the
"admin account") to grant `ALLOW_WITHDRAW` on a victim, and withdraws the victim's full collateral. The test asserts
the attacker began unprivileged and drained the victim's balance (5000). See `poc_output.log`.

## Suggested fix
- In `processAdminSetSignerPermissions`, bind `adminAccountId` to the canonical admin account
  (`require(txData.adminAccountId == signerManager.adminAccountId())` or equivalent) — never trust a caller-named
  admin account.
- Apply the owner-holds-the-bit delegation gate (used by the owner paths) to **registration-time** signer masks, or
  strip `ALLOW_ADMIN` from masks assignable at registration so admin can only ever be conferred by an existing admin.

## Submission caveats (honest — verify before submitting)
- **Deployment reachability:** confirm the `ADMIN_SET_SIGNER_PERMISSIONS` and `REGISTER_ACCOUNT` handlers are wired
  and that the live batcher relays user-supplied permission txs (not filtered off-chain). The on-chain bound is the
  trusted batcher; if the backend rejects self-named admin accounts, on-chain impact is gated by that trust.
- **Novelty:** verify against prior TipRun audits / known issues that the caller-named-`adminAccountId` gap is not a
  previously reported finding.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Access Control — privilege escalation (caller-named admin account trusted without binding to
  the canonical admin) leading to unauthorized fund withdrawal.
- **CWE (informative):** CWE-269 (Improper Privilege Management); CWE-639 (Authorization Bypass Through
  User-Controlled Key).

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Self-mint admin → drain any account | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H` | **8.1** | High |

> The on-chain path is permissionless from the attacker's standpoint (register-then-escalate); the residual gate is
> the trusted off-chain batcher relaying the transactions. Protocol/bounty severity may differ from the CVSS band.

<!-- END classification-cvss -->
