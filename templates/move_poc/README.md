# Move (Sui) PoC template — Level-3 standard

Copy to `pocs/<audit-id>/<finding-id>/` and fill in. Run with the Sui CLI: `sui move test` (the harness expects
`sui` on PATH — a prebuilt binary from the MystenLabs releases works, e.g. `sui-mainnet-vX-ubuntu-x86_64.tgz`).

## The three layers (all must pass, or be honestly `#[expected_failure]` / ignored with a written reason)
- **L1 — Entry** (`l1_entry_unprivileged`): the attacker invokes the in-scope `public`/`entry` function from a
  **fresh address** via `sui::test_scenario`, with no admin/privileged setup. Proves reachability.
- **L2 — State flip** (`l2_state_flip`): name the exact object field / `balance::value` / reserves / position
  liquidity and assert its value **before vs after** — the concrete invariant break (e.g. liquidity minted ≫ what
  the deposited amount should buy).
- **L3 — Outcome** (`l3_outcome`): prove the economic/security consequence — attacker `Coin` balance increased, or
  the pool can no longer cover LP obligations — asserted in test output, not inferred.

## Rules
1. **Exercise the REAL audited code unmodified.** Add the in-scope package as a `local` dependency in `Move.toml`;
   never copy/patch the target source into the PoC. If a needed entry isn't `public`, add a `#[test_only]`
   accessor in the PoC that calls the real entry — do not weaken the target's visibility/asserts.
2. **No cheating the setup.** Don't forge capabilities, mint `Coin` from nothing, or fabricate admin/shared state.
   Build only legitimate state (create pool, deposit real liquidity, share objects), then attack from an
   unprivileged address. Sui-specific: model shared vs owned objects correctly (`test_scenario::take_shared` /
   `take_from_sender`).
3. **Move specifics:** native `u64/u128` arithmetic aborts on overflow (so an overflow PoC must exercise a custom
   wide-math/`checked_*` helper, not plain `+`); EVM-style reentrancy is generally impossible — model callbacks
   via the actual hot-potato/flash receipt if relevant.
4. An honest partial PoC (L1+L2 pass, L3 `#[expected_failure]` with a reason) beats a fabricated passing test.
   **This program does not accept AI-generated reports without a runnable PoC.**
