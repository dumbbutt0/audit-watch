# Aurora Engine (EVM-on-NEAR, Rust) — focused-pass audit notes (2026-06-15)

**Target:** `github.com/aurora-is-near/aurora-engine` (HackenProof, Aurora Labs). Critical up to **$1M**, KYC +
PoC mandatory for ALL severities, private-testnet testing only. In scope: `engine`, `engine-precompiles`,
`engine-sdk`, `engine-transactions`, `engine-types`, `etc/eth-contracts`, `aurora-is-near/sputnikvm` (both
`master` and `develop`). **HEAD `d18047b`** (develop checked out).
**Local read-only. NOTHING submitted, no PoC built.**

## Scope of THIS pass (be precise — NOT a full audit)
This was a **focused deep-trace of the Aurora-unique EVM↔NEAR value/gas boundary** — the part that differs from
generic, heavily-tested EVM. It is **not** a claim that the whole engine (2900-line `engine.rs`, full XCC
subsystem, external connector, `sputnikvm`, eth-contracts) is clean. Surfaces traced this pass are sound.

## Verdict (focused): honest negative on the examined boundary
Aurora is a mature, production EVM-on-NEAR ($1M Critical → heavy prior scrutiny, ~152 competing hackers). Every
highest-EV surface examined is carefully built with the right guards present.

### Traced — sound
- **`engine/src/accounting.rs`** — `Accounting{gained,lost}` saturating supply-delta tracker; `net()` → Gained/
  Lost/Zero. Clean primitive; intentionally subtraction-avoiding.
- **`engine/src/engine.rs::apply` (1975-2068)** — the **insolvency guard**: it sums every balance delta across
  applied accounts and on `Net::Gained` **`panic!("ERR_INVALID_ETH_SUPPLY_INCREASE")`** in production
  (`cfg(all(not(integration-test), feature="contract"))`). So EVM ops can never mint ETH; supply can only be
  increased through the connector deposit path (external contract). Core conservation enforced.
- **`engine-precompiles/src/native.rs` (exit_to_near / exit_to_ethereum, 1316 LOC)** — the bridge out-path.
  Precompiles don't move funds directly: they emit a borsh `PromiseArgs` **log** (engine schedules the NEAR
  `ft_transfer`/`ft_transfer_call`/`withdraw`/`near_withdraw` after EVM exec) + an event. Findings:
  - **No JSON injection:** args built from a validated `AccountId` (no special chars) + decimal `u128` amount;
    the Omni `msg` path uses `serde_json` (escaped). Dedicated `test_ft_transfer_call_args_json_injection`.
  - **ERC-20 exits force `apparent_value == 0`** (else `ERR_ETH_ATTACHED_FOR_ERC20_EXIT`) → no ETH locked.
  - `amount`/`parse_amount` capped at `u128::MAX` (NEP-141 domain). `is_static`/delegate-call rejected.
  - **Atomicity:** the promise rides in EVM logs, so a reverted EVM frame discards both the value movement and
    the promise (no half-exit). Base-ETH sent to the exit precompile address accumulates there (unspendable →
    effectively burned), keeping EVM-spendable supply consistent.
- **`engine.rs::filter_promises_from_logs` (1634-1700)** — converts exit/XCC precompile logs into scheduled
  promises; explicitly "safe because the promise data comes from our own exit precompiles," not user calldata.
- **`engine-transactions/src/eip_7702.rs`** (newest Pectra set-code tx — freshest, highest-bug-odds surface) —
  faithful EIP-7702: per-auth `keccak(MAGIC ‖ rlp([chain_id,address,nonce]))` ecrecover, EIP-2 low-s
  (`SECP256K1N_HALF`), `chain_id ∈ {0, tx.chain_id}`, `parity ≤ 1`, buffers reset per iteration, invalid auths
  kept with `is_valid=false` (correct gas), nonce/delegation application delegated to the EVM. No defect.

- **XCC subsystem — `engine-precompiles/src/xcc.rs` (384) + `engine/src/xcc.rs` (603) +
  `engine/src/contract_methods/xcc.rs` (150)** — EVM contracts calling arbitrary NEAR contracts via per-address
  router sub-accounts. Traced sound:
  - **Router binding:** target = `{sender_hex}.{engine}` derived from `context.caller` → a user can only ever
    drive *their own* router (can't target another's).
  - **User pays for attached NEAR:** the precompile pulls `required_near` wNEAR via
    `wNEAR.transferFrom(sender → engine_implicit)` (sender must have approved the precompile); `required_near =
    attached_near + STORAGE_AMOUNT` (the +storage only when the router isn't deployed yet). The engine then
    unwraps exactly that wNEAR to the router; for new-account creation the engine fronts `STORAGE_AMOUNT` and the
    router `send_refund`s it back → conservation holds.
  - **Engine can't be drained by the precompile:** `handle_precompile_promise` asserts the router promise has
    `attached_balance == ZERO_YOCTO` (`ERR_ATTACHED_XCC_NEAR`) and only ever deploys engine-controlled router
    code / targets the router's `execute`/`schedule`.
  - **Access control on the dangerous methods is present:** `withdraw_wnear_to_router` (unwraps engine wNEAR to a
    router) is **`assert_private_call()`** (engine-self only) + successful-callback-gated — *not* publicly
    drainable; `factory_update` (router code) & `factory_set_wnear_address` are `require_owner_only`;
    `factory_update_address_version` is private; `fund_xcc_sub_account` is public only when the engine derives
    wNEAR itself (owner-only if a wNEAR account is supplied).
  - **Informational (defense-in-depth, not a finding):** the precompile checks the wNEAR `transferFrom`
    `exit_reason` but **ignores the ERC-20 bool return value** (`engine-precompiles/src/xcc.rs:199-216`). Safe
    only because the admin-set wNEAR is the canonical OZ-style token that *reverts* on insufficient
    balance/allowance; a non-reverting wNEAR would let a caller attach NEAR without paying (engine wNEAR drain).
    Recommend checking the return value. Gated on a trusted/standard wNEAR → not exploitable as deployed.

### NOT traced this pass (remaining surface; lower-confidence)
`engine/src/contract_methods/{connector,admin,silo,evm_transactions}.rs`; the rest of `engine.rs` (apply paths,
refunds, submit); the other tx types (`eip_1559/2930/4844/legacy` application side); `engine-sdk`;
`engine-types`; `etc/eth-contracts` (Solidity, incl. the wNEAR ERC-20 itself); **`sputnikvm`** (the entire
underlying EVM — a separate large repo). `master`-vs-`develop` is 500 commits / 453 files (not a usable tight
delta lens).

## EVM core — `aurora-is-near/sputnikvm` (= `aurora-evm` v3.0.0), focused look
Cloned `~/clones/sputnikvm` (HEAD `3af9dd3`). Aurora's maintained fork of rust-ethereum's EVM; **validated by the
Ethereum test suite in CI** (state/consensus + gas correctness). Focused on the freshest delta + the most
value-critical primitives:
- **Recent churn is settled & correct on HEAD.** The two latest commits both touch `executor/stack/memory.rs`
  (the in-execution `MemoryStackState`): `#109` (memory/stack opt) is a behavior-preserving refactor of the
  recursive `known_account`/`deleted`/`is_created`/`is_cold` lookups; `#110` then **fixed a real `is_empty`
  bug** — pre-fix, a substate-cached account with reset balance/nonce but *uncached code* fell through entirely
  to the backend (ignoring the substate's reset balance/nonce), which could mis-drive EIP-161 empty-account
  deletion. **Already merged (it is HEAD)** → not a finding; current `is_empty` correctly uses cached
  balance/nonce and only consults the backend for uncached code (covered by the added tests).
- **Value movement is correct** (`MemoryStackSubstate::{transfer,withdraw,deposit}`): underflow-guarded
  (`balance < value → ExitError::OutOfFund`), saturating credit, and self-transfer nets to zero (same cached
  entry) — no value duplication/underflow.
- **Honest limit:** an EVM core is validated by the execution-spec/Ethereum state tests (run in Aurora CI), and
  a *current* consensus/gas bug here is not realistically findable by manual reading — it needs **differential
  fuzzing** against geth/the execution-spec, which is out of session scope. The examined surface (freshest
  state-caching delta + value primitives) is clean on HEAD.

## Differential fuzz harness (built this session) — `~/clones/aurora-evm-difffuzz/`
To attack the EVM core the only tractable way (differential fuzzing), built a harness comparing
**aurora-evm** (the in-scope sputnikvm fork, path dep — audited repo unmodified) against **revm 41**
(independent reference). Both run the same `TestCase`; `diff()` compares status + return data +
per-account balance/nonce/code/storage (union, empty==absent so EIP-161 deletion is quotiented out);
gas comparison is opt-in (`check_gas`, off while establishing state agreement).
- `proggen.rs` emits structured EVM bytecode biased to high-divergence / new-EIP ops (SSTORE/SLOAD,
  TSTORE/TLOAD, MCOPY, CALL-family, CREATE, LOGn, BLOBHASH/BLOBBASEFEE, SELFDESTRUCT); CALL targets
  are always pool addresses so a precompile is never invoked (keeps the engines comparable).
- Two runners: an in-session stable sweep (`cargo test randomized_differential_sweep`, no nightly) and
  a coverage-guided `cargo-fuzz`/libFuzzer target (`./run.sh`).
- **Results:** 5 hand cases + **50,000** stable-sweep cases + **458,648** coverage-guided executions
  all **agree** on state/status/output at Cancun — **no divergence**. cargo-fuzz surfaced exactly one
  hit which triaged to a **harness false-positive** (caller-nonce: aurora's low-level `transact_call`
  skips tx-validation and bumps the nonce on a tx revm rejects at validation for insufficient funds)
  — fixed by funding the caller fully + `gas_price=0` + keeping the balance check enabled (disabling
  only the fee/base-fee/EIP-3607 checks aurora's entrypoint doesn't perform). `TRIAGE.md` documents the
  workflow.
- **Gas axis (investigated + root-caused).** Enabling gas comparison surfaced ~4% divergence; root-caused
  to a **harness hardfork mismatch** (revm was effectively Prague applying the EIP-7623 calldata floor while
  aurora was Cancun) — fixed by aligning both to **Prague**; plus a validation-asymmetry class (revm rejects
  `gas_limit < intrinsic`; aurora's `transact_call` does no tx-validation) fixed by skipping revm's
  validation rejections. Built a **per-opcode gas tracer** (`src/trace.rs`: aurora `tracing` listeners +
  revm `Inspector`) to pinpoint the residual. Result: calldata/intrinsic gas matches exactly (both correct
  EIP-7623); the residual `-50` is **not a single opcode** — a tiny (~3 gas) execution-phase offset that
  **compounds through the 63/64 CALL-gas-forwarding rule** (STATICCALL +45 / DELEGATECALL +151 / CALL +233)
  and the `GAS` opcode. **State/output are identical at every step → a pure gas-metering micro-difference
  (~0.1%), not security-relevant, not submittable.**
- **Sustained run + geth tie-break (conclusive).** Two coverage-guided **state-axis** workers (Prague + Osaka,
  1 hr each). Prague did **7.88M executions → exactly 1 state divergence**. Investigating it surfaced a real
  harness bug — revm's `c.spec=` does not update the gas schedule (`set_spec_and_mainnet_gas_params` required),
  so revm had been using default gas params regardless of fork; fixing it dropped the gas-divergence rate ~90×
  (81/3000 → 1/3000). The single residual divergence (nested value-bearing CALL to the warm tx-sender: aurora
  transfers, revm OOGs) was tie-broken against **geth 1.17.3 `evm t8n`** (canonical reference): geth gives the
  identical post-state (`pool3` 194306) **and** gas (56718) as **aurora** — revm is the outlier (it under-warms
  the EIP-2929 tx sender). **→ aurora is spec-correct; not an Aurora bug.**
- **Final clean re-run on the fully-fixed harness (gas-params + full block-env aligned).** Both prior known
  divergences now AGREE (aurora==revm==geth). Re-launched both state-axis workers on the corrected binary:
  Prague **7,534,883 execs** and Osaka **3,704,474 execs** (~11.2M total, 1 hr each) → **0 / 0 / 0**
  oom/timeout/crash, **zero divergences** of any kind (consensus, gas, state, hang). This is the trustworthy run.
- **EVM-core verdict: honest negative, validated three ways** — source read → revm differential fuzz → geth
  canonical tie-break. The lone real cross-engine divergence (pre-fix) resolved in aurora's favor; the corrected
  ~11.2M-execution re-run is fully clean.
- **Harness note:** a revm-only differential yields false positives at gas/OOG boundaries; the geth `t8n`
  tie-break (`emit_t8n` test → `/tmp/t8n_*.json`, substitute-sender trick for a signable caller) is the required
  filter before attributing any divergence to aurora. Toolchain notes (cap-lints, revm `optional_*`/gas-params,
  alloy↔primitive-types, `tracing` feature, geth `evm`) are in the repo.

## Honest EV assessment
This is one of the hardest targets in the ecosystem: mature, multi-audited-in-practice, $1M Critical with many
competing researchers, enormous Rust surface, and PoC mandatory on a heavy NEAR sandbox harness. A real shot
needs a multi-week specialist effort (esp. XCC + the underlying `sputnikvm` EVM). The focused boundary pass is a
clean negative — consistent with prior mature-target outcomes. **Nothing submitted.**
