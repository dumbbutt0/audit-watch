# Move (Sui) language support

Audit-Watch supports **Move on Sui** as a first-class audit language, alongside Solidity and Rust/Solana. It uses
the same cross-language adapter spine as the Rust/Solana extension (see the `language` field in `meta.json` and
`audit_context.audit_language()`), so the Solidity path is byte-behavior-unchanged when `language` is unset.

## How it routes
- **Detection:** `audit_context._KNOWN_LANGUAGES` includes `"move"`; `meta.language="move"` (set by
  `ingest_contest --language move` or the workspace creator) drives all routing. `build_coverage_manifest`
  `_infer_language()` falls back to "move" when the tree has only `.move` files; `profile_target_repo.detect_language`
  returns "move" for a `Move.toml` repo (framework "sui"/"aptos").
- **Coverage manifest:** `_move_files()` enumerates `sources/**/*.move` (skips `tests/`, `build/`, `*_test(s).move`).
  `MOVE_TAG_KEYWORDS` adds Sui-native tags (`capability`/`permissions`, `object_model`, `arithmetic`, `amm_pol`,
  `accounting`, …). The value-at-risk score boosts `arithmetic` + `object_model` so the integer/liquidity math (the
  Cetus-class surface) and capability/object surface rank to the top. Items are tagged `contract_type:"move_module"`.
- **Specialists (`/ite-audit` → move branch):** `agents/move_clmm_math.md` (custom wide-math/`checked_shlw`
  overflow [the Cetus $220M class], liquidity⇄amount + fee-growth rounding direction, i32/i64/i128 signed-int & tick
  math, sqrt-price precision, swap/flash-swap conservation) and `agents/move_object_capability.md` (capability/
  witness/admin gates bound to the specific object, shared-vs-owned object confusion, hot-potato repayment
  enforcement, Coin/Balance conservation, version/upgrade & init guards). The Solidity-syntax and Solana specialists
  are skipped for move. Note Move *aborts on native overflow* and *prevents EVM-style reentrancy* — weight the
  custom-math + object/capability + economic surfaces, not plain arithmetic/reentrancy.
- **Mechanism classes:** seven `move-*` classes in `config/mechanism_classes.json`, all `language:"move"` +
  `status:"seeded"` (NEVER counted toward Solidity/Rust recall; `eval_scoreboard` routes move adjudications to
  `evals/move_scoreboard.md`). They are seeded from the Cetus class + general Sui object/capability review and are
  upgraded to `reincorporated` only when the recall lab earns them on scored Sui/Move contests.

## PoC (required by most Move bounties)
- Template: `templates/move_poc/` (`Move.toml` with a `local` dep on the UNMODIFIED in-scope package +
  `sources/poc_test.move` with the L1-entry / L2-state-flip / L3-outcome skeleton, run via `sui move test`).
- Toolchain: a prebuilt Sui CLI binary works — download the MystenLabs release tarball
  (`sui-mainnet-vX-ubuntu-x86_64.tgz`), extract `sui` to `~/.local/bin`. `sui move test` resolves the Sui framework
  implicitly from the target's `Move.lock`.
- `generate_poc_test.load_repo_profile()` returns `{"language":"move","framework":"sui"}` for a move audit so the
  Sui-Move template is used instead of the Soroban/Foundry defaults.

## Why Move
Many lower-competition bounties (and large CLMM TVL) are on Sui Move. The 2025 **Cetus $220M** hack was a Sui CLMM
overflow-check bug (`checked_shlw` wrong mask) in the liquidity math — so for any Sui CLMM the integer/liquidity
math library is the #1 lead. Validated end-to-end on `turbos-clmm-public` (705 manifest items, 467 `sui move test`
passing; honest negative — the Cetus class is correctly handled there). Drop-in for gated targets like Momentum
`mmt-v3-core` once source access is granted.
