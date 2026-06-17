# Solana PoC template (litesvm, Level 3 standard)

Copy this directory to `pocs/<audit-id>/<finding-id>/` and fill in. It is the Solana counterpart
of the Foundry templates under `pocs/foundry/` — same Level 3 bar (CLAUDE.md → "Level 3 PoC
Standard"), expressed as cargo tests.

## The three layers (all must pass, or be honestly `#[ignore]`d with a reason)
- **L1 — Entry** (`l1_entry_unprivileged`): the attacker tx executes from a fresh keypair with no
  privileged setup/signers — proves permissionlessness.
- **L2 — State Flip** (`l2_state_flip`): name the exact account / token balance / lamports and
  assert before vs after via `svm.get_account()` + `spl_token::state::Account::unpack` — proves the
  storage/balance change, not inferred.
- **L3 — Outcome** (`l3_outcome`): assert the final economic/security consequence (attacker net
  gain == stolen amount; broken conservation invariant) — proves impact.

## Setup
1. `Cargo.toml`: rename the package, and add the in-scope program as a `path` dev-dependency so the
   PoC links the REAL contest code (no re-implementation). Point at `contracts/_sources/...`.
2. If you have the built program `.so`, load it with `svm.add_program_from_file(...)`; otherwise
   build it (`cargo build-sbf`) and point at `target/deploy/*.so`.
3. `setup()`: create only the MINIMUM legitimate state an honest deployer would (vault PDAs, funded
   vault ATA, allowed token/broker). Excess privileged setup undermines the L1 permissionless claim.

## Run
```
cargo test -- --nocapture          # all three layers
cargo test l2_state_flip -- --nocapture
```

## Honesty
An honest partial PoC (one layer proven, others ignored with a written reason) beats a fabricated
passing test. Never assert a balance change you did not observe. For ZK/proof-soundness targets,
do NOT write a soundness PoC here — that is out of scope (`documentation/architecture/zk_boundary.md`).
