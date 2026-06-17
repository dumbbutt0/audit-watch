# Security Disclosure — Astros `perp_vault`: signed withdrawals are not bound to a vault instance

**To:** NAVI Protocol security team
**Component:** `naviprotocol/astros-contracts` → `perp_vault` (Move package `dvault`)
**Mainnet package:** `0x882cd9388d35a141614a7beb28ec14f7aaf54f8372ccc1dd64046efd82866043`
**Severity:** Medium — *latent*. Not exploitable on the current single-vault deployment; becomes a direct
double-withdraw the moment a second `ActiveVault` of the same coin type is deployed.
**Status:** Proof-of-concept reproduced (`sui move test astros_poc` → 3/3 pass). Responsible disclosure —
nothing exploited; all testing local.

---

## Summary
`active_vault::withdraw` authorizes a withdrawal by verifying an off-chain ed25519 signer quorum over a message
produced by `keccak_message(...)`. That message binds the network flag, an opaque `msg`, the **coin type `T`**,
caller, recipient, amount, `order_id`, and `order_time` — but it does **not** bind the `ActiveVault` object the
withdrawal targets. The signer set is shared globally (one `Config`), and the replay guards (`used_hashes`,
`withdrawal_order_ids`) are stored **per vault**.

Therefore a single authorization signed for one `ActiveVault<T>` is equally valid against **every** other
`ActiveVault<T>` of the same coin type. An attacker holding one legitimately-signed withdrawal can replay the
same `(order_id, signatures, message)` against each sibling vault and withdraw the amount from each.

## Affected code
`perp_vault/sources/active_vault.move`

- `keccak_message` (lines 609-628) — composes the signed message; no vault identifier is appended:
  ```move
  message.append(b"mainnet");
  message.append(msg);
  message.append(into_bytes(into_string(get<T>()))); // coin type only
  message.append(caller.to_bytes());
  message.append(recipient.to_bytes());
  message.append(from_u256((amount as u256)).to_bytes());
  message.append(from_u256(order_id).to_bytes());
  message.append(from_u256((order_time as u256)).to_bytes());
  // <-- vault id is never included
  ```
- `withdraw` (lines 214-281) — verifies the quorum and enforces replay protection against **this vault's** tables
  (`vault.config.used_hashes`, `vault.config.withdrawal_order_ids`), so a sibling vault's tables are empty for the
  same `order_id`/hash.
- `Config` (lines 43-51) — the `signers`/`threshold` set is a single shared object referenced by all vaults.

## Root cause
Authorization scope (the global signer set) is broader than the resource it protects (a specific vault), and the
binding between the two is missing from the signed payload. The per-vault replay guard prevents reuse on the same
vault but does nothing across vaults.

## Impact
When two or more `ActiveVault<T>` of the same coin type exist (the architecture explicitly supports this — see
below), one signed withdrawal authorizes withdrawals of the same amount/recipient from each of them. A user (or
anyone who obtains one signed authorization, e.g. their own legitimate withdrawal) extracts N× the authorized
amount across N sibling vaults → **direct loss of user funds** from the vaults that were not intended to pay.

## Reachability
- **Today: not exploitable.** Mainnet currently has exactly **one** vault (`ActiveVault<USDC>`
  `0xa33c96502b89cdfd177333c35d70b95451547d223a0d0abc5faeee82793500ab`); `Config.treasuries` has length 1,
  threshold = 2, 2 signers. Verified by RPC.
- **The design anticipates multiple vaults.** `create_vault<T>` is generic and unrestricted for the OwnerCap;
  `Config.treasuries` is a `vector<address>` accumulating every created vault; and the product framing
  ("Ultimate Onchain Structured Fund") implies multiple products/strategies. A second same-coin vault is a
  routine scaling step, after which this becomes immediately exploitable.
- **Not mitigated off-chain.** A live withdrawal transaction
  (`HfGQxucPu7xpchrWVsNtqKtggv7yNWUD46AacFQqadWq`) passes `msg = "withdraw"` — a constant string with no vault
  discriminator — so the off-chain signer service does not encode the vault id in the opaque `msg` field either.

## Proof of concept
File: `poc/astros_poc.move` (drop into `perp_vault/tests/`). Two tiny test-only read helpers were added to
`active_vault.move` (`vault_addr`, `withdrawal_order_id_used`); no production logic changed. Signatures are
freshly generated with PyNaCl over a byte-exact reproduction of `keccak_message`, so the positive path also
demonstrates the 2-of-2 ed25519 gate verifies correctly.

```
cd perp_vault && sui move test astros_poc
```

Output:
```
[ PASS ] dvault::astros_poc::test_cross_coin_type_not_replayable
[ PASS ] dvault::astros_poc::test_e2e_one_authorization_drains_two_vaults
[ PASS ] dvault::astros_poc::test_same_vault_replay_is_blocked
Test result: OK. Total tests: 3; passed: 3; failed: 0
```

- **`test_e2e_one_authorization_drains_two_vaults`** — two `ActiveVault<USDC>` share one `Config` (2 signers,
  threshold 2). A victim deposits 100 into each via the real `user_entry::deposit`. The attacker spends ONE
  2-of-2 authorization (`order_id = 1`, amount 50) through the real `user_entry::withdraw` against vault #1, then
  replays the identical `(order_id, signatures, message)` against vault #2. The attacker ends up holding two
  `Coin<USDC>` totalling **100 from a single 50-authorization**; each vault drops 100 → 50.
- **`test_same_vault_replay_is_blocked`** (control) — replaying on the *same* vault aborts
  `EORDER_ID_ALREADY_USED`, confirming the per-vault guard works and isolating the defect to the missing
  vault-id binding.
- **`test_cross_coin_type_not_replayable`** (control) — the same USDC authorization is rejected on a `SUI_TEST`
  vault (`ETHRESHOLD_TOO_LOW`), confirming the coin-type binding that *is* present works, so the signature scheme
  is sound and only the vault-id binding is missing.

## Recommended fix
Bind the target vault into the signed message, and have the off-chain signer include the same value:

```move
public fun keccak_message<T>(
    vault_id: address, // NEW
    order_id: u256, order_time: u64, caller: address,
    amount: u64, recipient: address, msg: vector<u8>,
): vector<u8> {
    let mut message = vector::empty<u8>();
    message.append(b"mainnet");
    message.append(msg);
    message.append(into_bytes(into_string(get<T>())));
    message.append(vault_id.to_bytes()); // NEW — bind the specific vault
    message.append(caller.to_bytes());
    message.append(recipient.to_bytes());
    message.append(from_u256((amount as u256)).to_bytes());
    message.append(from_u256(order_id).to_bytes());
    message.append(from_u256((order_time as u256)).to_bytes());
    keccak256(&message)
}
```

In `withdraw`, pass `vault.id.to_address()` into `keccak_message`. The signing backend must add the vault id to
the message it signs. (`order_id` reuse across vaults then no longer matters, because the hashes differ per
vault.)

## Disclosure / scope notes
- Reported responsibly; not exploited; the current deployment is unaffected.
- Distinct from MoveBit AVA-1 (centralization, acknowledged) — this is a missing message binding, not a trust
  concern.
- The broader centralization/custodial trust model (OwnerCap direct withdrawals, off-chain signer dependence)
  is acknowledged by NAVI and out of scope of this report.
