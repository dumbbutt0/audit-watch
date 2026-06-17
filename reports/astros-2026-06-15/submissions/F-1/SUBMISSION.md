<!--
PLATFORM-PASTE-READY HackenProof submission for Astros perp_vault F-1.
Paste each "# Field:" section into the matching HackenProof field. Copy from the RAW file, not a rendered
preview. Facts match the PoC (sui move test astros_poc -> 3/3 pass) and on-chain RPC checks. Severity is set
Medium honestly (latent: not exploitable on the current single-vault deployment). NOTHING has been submitted —
the user authors/submits in their own voice.
-->

# Field: Target
https://github.com/naviprotocol/astros-contracts/tree/main/perp_vault

# Field: Category
Business Logic Errors

# Field: Severity
Medium

# Field: Title
Signed withdrawals are not bound to a vault instance — one authorization is replayable across every same-coin ActiveVault, enabling double-withdrawal of user funds

# Field: Vulnerability details

`active_vault::withdraw` authorizes a withdrawal by verifying an off-chain ed25519 signer quorum over a digest
produced by `keccak_message(...)`. That digest binds the network flag, an opaque `msg`, the coin type `T`, the
caller, the recipient, the amount, the `order_id`, and the `order_time` — but it does NOT bind the `ActiveVault`
object the withdrawal targets. The signer set is a single shared global object (`Config`), and the anti-replay
guards are stored per vault (`vault.config.used_hashes`, `vault.config.withdrawal_order_ids`).

As a result, one authorization signed for a vault of coin type `T` is equally valid against EVERY other
`ActiveVault<T>`. Because each vault keeps its own replay tables, the same `(order_id, signatures, message)` is
accepted again on a sibling vault, and the amount is paid out a second time.

Root cause: the authorization scope (the global signer set) is broader than the resource it protects (a specific
vault), and the binding between the two is absent from the signed payload. The per-vault replay guard prevents
reuse on the same vault but does nothing across vaults.

Affected code — `perp_vault/sources/active_vault.move`:

The signed message omits any vault identifier (`keccak_message`, lines 609-628):

```move
public fun keccak_message<T>(
    order_id: u256, order_time: u64, caller: address,
    amount: u64, recipient: address, msg: vector<u8>,
): vector<u8> {
    let mut message = vector::empty<u8>();
    message.append(b"mainnet");
    message.append(msg);
    message.append(into_bytes(into_string(get<T>()))); // coin type only
    message.append(caller.to_bytes());
    message.append(recipient.to_bytes());
    message.append(from_u256((amount as u256)).to_bytes());
    message.append(from_u256(order_id).to_bytes());
    message.append(from_u256((order_time as u256)).to_bytes());
    keccak256(&message)  // <-- vault id never included
}
```

The replay guards in `withdraw` are scoped to the called vault only (lines 243-246), so a sibling vault's tables
are empty for the same `order_id` / hash:

```move
assert!(!vault.config.used_hashes.contains(kmessage), ETRANSACTION_HASH_ALREADY_USED);
vault.config.used_hashes.add(kmessage, true);
assert!(!vault.config.withdrawal_order_ids.contains(order_id), EORDER_ID_ALREADY_USED);
vault.config.withdrawal_order_ids.add(order_id, amount);
```

The signers/threshold live in the one shared `Config` (lines 43-51) referenced by all vaults, so every same-coin
vault validates against the identical signer set.

Not mitigated off-chain: a live withdrawal transaction
(`HfGQxucPu7xpchrWVsNtqKtggv7yNWUD46AacFQqadWq`) passes `msg = "withdraw"` — a constant string with no vault
discriminator — so the signing backend does not encode the vault id in the opaque `msg` field either.

# Field: Impact

When two or more `ActiveVault<T>` of the same coin type exist, a single signed withdrawal authorizes a
withdrawal of the same amount/recipient from each of them. Anyone who obtains one signed authorization — for
example a user with their own legitimate withdrawal — can replay it against each sibling vault and withdraw N×
the authorized amount across N vaults. The vaults that were never meant to pay lose user funds (direct loss of
deposited principal).

Reachability (stated honestly): the architecture is built for multiple vaults — `create_vault<T>` is generic and
unrestricted, `Config.treasuries` is a `vector<address>` accumulating every vault created, and the product is an
"Ultimate Onchain Structured Fund" (multiple products/strategies). At the time of writing mainnet has exactly
one vault (`ActiveVault<USDC>` `0xa33c96502b89cdfd177333c35d70b95451547d223a0d0abc5faeee82793500ab`,
`treasuries` length 1, threshold 2, 2 signers), so the issue is not exploitable at this instant; it becomes a
direct double-withdrawal the moment a second same-coin vault is deployed, which is a normal scaling step the
contract is explicitly designed to support. The fix is one line and prevents the loss before it can occur.

# Field: Proof of Concept

The PoC (`poc/astros_poc.move`, drop into `perp_vault/tests/`) drives the real entrypoints. Two test-only read
helpers were added to `active_vault.move` for assertions (`vault_addr`, `withdrawal_order_id_used`) — no
production logic is changed. Signatures are freshly generated (PyNaCl) over a byte-exact reproduction of
`keccak_message`, so the positive path also proves the 2-of-2 ed25519 gate verifies correctly.

Run:
```
cd perp_vault && sui move test astros_poc
```

Result (`poc/poc_output.log`):
```
[ PASS ] dvault::astros_poc::test_cross_coin_type_not_replayable
[ PASS ] dvault::astros_poc::test_e2e_one_authorization_drains_two_vaults
[ PASS ] dvault::astros_poc::test_same_vault_replay_is_blocked
Test result: OK. Total tests: 3; passed: 3; failed: 0
```

Scenarios:

1. `test_e2e_one_authorization_drains_two_vaults` — two `ActiveVault<USDC>` share one `Config` (2 signers,
   threshold 2). A victim deposits 100 into EACH via the real `user_entry::deposit`. The attacker spends ONE
   2-of-2 authorization (`order_id = 1`, amount 50) through the real `user_entry::withdraw` against vault #1,
   then replays the identical `(order_id, signatures, message)` against vault #2. The attacker ends holding two
   `Coin<USDC>` totalling 100 — extracted from a single 50-authorization; each vault balance drops 100 → 50.

2. `test_same_vault_replay_is_blocked` (control) — replaying on the SAME vault aborts `EORDER_ID_ALREADY_USED`,
   confirming the per-vault guard works and isolating the defect to the missing vault-id binding.

3. `test_cross_coin_type_not_replayable` (control) — the same USDC authorization is rejected on a `SUI_TEST`
   vault (`ETHRESHOLD_TOO_LOW`): the coin-type binding that IS present works, so the signature scheme is sound
   and only the vault-id binding is missing.

# Field: Recommendation

Bind the target vault into the signed message and have the off-chain signer include the same value:

```move
public fun keccak_message<T>(
    vault_id: address,                              // NEW
    order_id: u256, order_time: u64, caller: address,
    amount: u64, recipient: address, msg: vector<u8>,
): vector<u8> {
    let mut message = vector::empty<u8>();
    message.append(b"mainnet");
    message.append(msg);
    message.append(into_bytes(into_string(get<T>())));
    message.append(vault_id.to_bytes());            // NEW — bind the specific vault
    message.append(caller.to_bytes());
    message.append(recipient.to_bytes());
    message.append(from_u256((amount as u256)).to_bytes());
    message.append(from_u256(order_id).to_bytes());
    message.append(from_u256((order_time as u256)).to_bytes());
    keccak256(&message)
}
```

In `withdraw`, pass `vault.id.to_address()` into `keccak_message`, and update the signing backend to add the
vault id to the message it signs. After this, an authorization is valid only for the specific vault it was
signed for, regardless of how many same-coin vaults exist.

# Field: CVSS

CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N — Base 5.9 (Medium). AC:H reflects the precondition that a second
same-coin vault exists; I:H reflects loss/over-withdrawal of vault funds once it does.

# Field: Attachments
- vulnerable_files/active_vault.move   (pristine, from repo HEAD — keccak_message lines 609-628; withdraw lines 214-281; Config lines 43-51)
- vulnerable_files/user_entry.move     (public entrypoints deposit/withdraw)
- poc/astros_poc.move                  (PoC; 3 tests, all pass)
- poc/poc_output.log                   (captured passing run)
