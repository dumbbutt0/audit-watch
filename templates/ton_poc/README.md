# TON (FunC) PoC template — Level-3 standard, `@ton/sandbox`

Local, in-process TVM. **No network, no testnet broadcast, no keys** — `@ton/sandbox` runs the REAL compiled
FunC contracts in memory, so it satisfies the program's "no mainnet / no live testing" rule with zero deployment.

## Two ways to run (pick A for STON.fi-style targets)

**A — Inside the target's own Blueprint repo (recommended).** `ston-fi/dex-core-v2` already ships
`wrappers/` (Router.ts, Pool.ts, LPAccount.ts, LPWallet.ts, Vault.ts) + `*.compile.ts` and a working
`@ton/sandbox` + `jest` setup. Copy `tests/poc.spec.ts` from this template into the target repo's `tests/`,
`npm install` once, and run `npx blueprint test poc` (or `npx jest tests/poc.spec.ts`). You reuse the audited
compile + typed wrappers — no re-scaffolding.

**B — Standalone.** Use this folder's `package.json` / `jest.config.js` / `tsconfig.json`, add the in-scope
`.fc` as a Blueprint compile target (a `*.compile.ts` pointing at the audited source — never copy/patch it),
and run `npx jest`.

## The three layers (all must pass, or be honestly skipped with a written reason)

- **L1 — Entry** (`l1_entry_unprivileged`): the attacker sends the in-scope message from a **fresh sandbox
  wallet** (`blockchain.treasury('attacker')`) with no admin/privileged setup. Proves reachability from an EOA.
- **L2 — State flip** (`l2_state_flip`): name the exact storage field / balance and assert **before vs after**
  via `blockchain.getContract(addr).account` (raw balance / state) or a get-method on the typed wrapper
  (`pool.getReserves()`, `lpAccount.getData()`). The concrete invariant break.
- **L3 — Outcome** (`l3_outcome`): prove the economic/security consequence — attacker jetton balance up, or a
  victim's funds stranded — asserted in test output, **not inferred**. On success the test MUST
  `console.log('BUG CONFIRMED')` (the harness `determine_status` keys "proved" off that string).

## Rules

1. **Exercise the REAL audited FunC unmodified.** Compile the in-scope source via Blueprint; never copy/patch
   the target into the PoC. Build legitimate setup state (deploy router/pool, provide real liquidity, mint real
   jettons to the victim) using the contracts' OWN flows, then attack from an unprivileged wallet.
2. **No cheating the setup.** Don't hand-write storage to fabricate balances/reserves; reach the pre-exploit
   state through real messages. Model TON faithfully: messages are async — use `blockchain.sendMessage` /
   wrapper sends and inspect the resulting transaction tree (`expect(result.transactions).toHaveTransaction(...)`).
3. **TON specifics:**
   - There is **no synchronous reentrancy** — model an attack as a sequence/interleaving of messages, or a
     crafted cell body, not a nested call.
   - To prove a **bounce** bug, force the downstream message to throw and assert via
     `toHaveTransaction({ inMessageBounced: true })` that the bounce returns, then assert the sender's state
     was NOT restored (funds stranded).
   - To prove **sender-spoofing**, send the privileged message (e.g. a forged `transfer_notification`) from an
     attacker treasury that is NOT the contract's real jetton wallet, and assert it was accepted.
   - Assert exit codes with `toHaveTransaction({ exitCode: ... })`; read raw TON balance from
     `(await blockchain.getContract(addr)).balance`.
4. An honest partial PoC (L1+L2 pass, L3 documented as not-yet-reproduced) beats a fabricated passing test.
   **This program does not accept reports without a runnable PoC.**
