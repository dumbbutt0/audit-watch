# NAVI Astros `perp_vault` — audit findings (2026-06-15)

**Target:** `github.com/naviprotocol/astros-contracts` → `perp_vault/` (package `dvault`).
**Bounty:** HackenProof NAVI "Astros Smart Contracts" — Critical up to $150k, POC required, 100 rep. In scope: `perp_vault` only.
**Published-at (mainnet):** `0x882cd9388d35a141614a7beb28ec14f7aaf54f8372ccc1dd64046efd82866043`
**Local-only. NOTHING submitted.** PoC: `sui move test astros_poc` → 2/2 pass.

## Verdict: HONEST NEGATIVE on the live deployment (one PoC'd *latent* design issue + minor notes)

This is a small (1231 LOC), **custodial-by-design** "token deposit/withdrawal system" (Movebit's words),
MoveBit-audited (Feb 2025, all 5 issues Fixed/Acknowledged), and correctly configured on mainnet. The
on-chain trust boundary — `active_vault::withdraw`'s 2-of-N ed25519 signer quorum — is **implemented
correctly**. No live-exploitable High/Critical found.

### Architecture
- `user_entry`: `deposit` (permissionless) / `withdraw` (off-chain ed25519 signature-gated).
- `active_vault` (core): `ActiveVault<T>{balance, config}` — **no shares**; deposit = `balance.join`; NAV =
  raw balance. Withdraw verifies a quorum of signatures over `keccak_message(...)`, with per-vault replay
  protection (`used_hashes`, `withdrawal_order_ids`) and an `order_time` deadline.
- `secure_vault`: operator/owner-gated cold custody with per-epoch withdrawal cap.
- `dvault_manage`: cap-gated admin/operator orchestration.
- One **global shared `Config`** holds `signers`/`threshold`/`paused`; **many vaults** can reference it.

### Signature core is correct (the two classic criticals are ABSENT)
`active_vault.move:250-270`: the outer loop iterates the **registered** `config.signers` (not caller-supplied
keys), counts each registered signer **at most once** (inner `break`), and `add_signer` rejects duplicate
pubkeys. So there is **no signer-dedup bypass** (replaying one signature N times can't inflate the count) and
**no key-forgery** (`_signer` is always a registered pubkey). Confirmed end-to-end: PoC generated fresh
SK1/SK2 signatures over a reproduced `keccak_message` and the contract accepted them (2-of-2).

### Live mainnet state (read-only RPC, verified)
- `Config`: `paused=false`, **threshold=2, 2 signers**, `treasuries=[single vault]`. → bootstrap window closed.
- Single `ActiveVault<USDC>` `0xa33c…00ab`, balance **≈26,831 USDC**, `order_id_counter=18473`,
  `max_vault_balance=50,000 USDC`, **0 security periods**. → only one same-coin vault exists.

---

## F-1 (Medium, **latent/conditional** — PoC'd) — Signed withdrawal not bound to the vault object id → cross-vault signature replay
`active_vault::keccak_message` (`active_vault.move:609-628`) binds network flag, `msg`, coin type `T`, caller,
recipient, amount, order_id, order_time — **but not the `ActiveVault` object id**. The signer set lives in the
one global `Config`, and the replay guards (`used_hashes`, `withdrawal_order_ids`) are **per-vault**.
Consequently a single authorization signed for one `ActiveVault<T>` is valid against **every** `ActiveVault<T>`
of the same coin type: the same `(order_id, signatures, message)` clears the quorum on a second vault whose
tables haven't seen that `order_id`.

**PoC** (`poc/astros_poc.move`, `test_poc_one_authorization_drains_two_vaults`, PASS): two `ActiveVault<USDC>`
share one `Config` (2 signers, threshold 2), funded 100 each. One 2-of-2 authorization (`order_id=1`, amount 50)
is spent on vault #1 (50 out) and **replayed on vault #2** (another 50 out) → **100 extracted from a single
50-authorization**. Control `test_poc_same_vault_replay_is_blocked` (PASS) shows same-vault replay aborts
`EORDER_ID_ALREADY_USED`, isolating the root cause to the missing vault-id binding.

**Not mitigated off-chain (verified):** a live withdrawal tx (`HfGQxucPu7xpchrWVsNtqKtggv7yNWUD46AacFQqadWq`)
passes `msg = "withdraw"` — a **constant string with no vault discriminator**. So the signer's authorization is
identical for any same-coin vault; nothing off-chain closes the gap.

**Reachability:** requires ≥2 `ActiveVault` of the same coin type sharing the global `Config`. **Only one vault
exists today**, so this is **not currently exploitable** — but the generic `create_vault<T>` + the
`treasuries: vector<address>` design + the "Ultimate Onchain Structured Fund" multi-product framing make a
second same-coin vault a normal, anticipated scaling step. It would become a direct double-withdraw the moment
that happens. Trivial fix: append `vault.id.to_address()` (or the vault address) into `keccak_message`, and
have the off-chain signer bind it.

## F-2 (Low, defense-in-depth) — `withdraw` does not require signers to be configured
`active_vault::withdraw` never asserts `config.threshold > 0` / `signers` non-empty. From the post-`init`
bootstrap state (`threshold=0`, `signers=[]`), an **empty-signature withdrawal passes** (`0 >= 0`,
empty signer loop). Deposits are permissionless and enabled on `create_vault`, so funds present before signers
are configured are drainable by anyone. **Not reachable on mainnet** (live `threshold=2`); and once configured
the set can't be emptied (`remove_signer`/`reset_signers` enforce `threshold>0`). Add an explicit
`assert!(config.threshold > 0)` guard.

## F-3 (Info) — `dvault_manage::direct_deposit` / `deposit_secure_vault` are permissionless and skip `deposit_enable`
Anyone can push a `Balance<T>` into the active or secure vault even when `deposit_enable=false` / not paused at
the vault level. Harmless donation; no theft. Consider gating or documenting.

## F-4 (Info) — `security_update` divides by `period.duration` with no zero-check
`active_vault.move:540` — a security period created with `duration=0` bricks all withdrawals (div-by-zero).
Admin-only misconfig; **no periods configured live**.

## Note — repo test suite is red (16/79 fail), stale signature vectors
All failures hit `assert!(threshold >= config.threshold)`: the tests' hardcoded ed25519 vectors no longer match
the current `keccak_message` (the message format changed after the vectors were generated). Test-hygiene only —
the deployed off-chain signer matches the contract (live `Withdrawn` events succeed), and fresh sigs verify (F-1 PoC).

---

## Out of scope / acknowledged (do not report)
- **Centralization** (owner `direct_withdraw` from both vaults; off-chain signer dependence; operator-managed
  secure vault) — Movebit AVA-1 **Major / Acknowledged**; "intended for centralized systems."
- Movebit AVA-2/3/4, DMA-1 — Fixed in this code (verified: `reset_signers` replaces the vector; `version_migrate`
  uses `<`; `signatures.length() <= signers.length()` present at `active_vault.move:236`).

## Harness notes
- Two test-only read helpers added to `active_vault.move` (`vault_addr`, `withdrawal_order_id_used`) — no
  production logic changed.
- `sui move test astros_poc` → 2/2 pass. Signatures generated with PyNaCl over a Python reproduction of
  `keccak_message` (verified bit-identical to the contract).
