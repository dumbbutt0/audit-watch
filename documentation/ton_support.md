# TON (FunC) language support

Audit-Watch supports **TON / FunC** as a first-class audit language, alongside Solidity, Rust/Solana, and
Move/Sui. It uses the same cross-language adapter spine as the Rust and Move extensions (the `language` field in
`meta.json` → `audit_context.audit_language()`), so the Solidity path is byte-behavior-unchanged when `language`
is unset. TON is a fundamentally different VM: an **asynchronous actor model** (contracts talk via messages, not
synchronous calls), so the EVM bug classes that assume atomic composability do **not** transfer.

## How it routes
- **Detection:** `audit_context._KNOWN_LANGUAGES` includes `"ton"`; `meta.language="ton"` (set by
  `ingest_contest --language ton` or the workspace creator) drives all routing. `profile_target_repo.detect_language`
  returns `"ton"` for a repo with `blueprint.config.ts` or any `*.fc`/`*.tolk` (framework `"blueprint"`);
  `build_coverage_manifest._infer_language()` falls back to `"ton"` when the tree has only `.fc`/`.func`/`.tolk`.
- **Static adapter:** `tools/static_analysis.py` dispatches `ton` audits to `tools/static_analysis_ton.py`, which
  emits the SAME `static.json` schema. Best-effort toolchain layer (Misti / `func` if on PATH) + an always-on FunC
  regex census: jetton transfer-notification handling (sender-spoof surface), `equal_slices` sender-auth anchors,
  raw message sends (carry-value egress), `IS_BOUNCED` branches (ignored-bounce stranding), cell/ref parsing
  (`load_ref`/multihop), and coin `muldiv` (TVM 257-bit). TON routing flags: `has_jetton`/`is_dex`/`has_multihop`/
  `bounce_ignored`/`sender_auth_checks`. The EVM conditional-spawn flags (`is_erc4626`/`has_transient_storage`/
  `is_proxy`) are forced **False** so the EVM-only conditional specialists never spawn on a FunC target.
- **Coverage manifest:** `_ton_files()` enumerates `**/*.fc` (+ `.func`/`.tolk`; skips `test/`/`build/`/
  `node_modules/`). FunC has no `function`/`fun`/`fn` keyword, so `FUNC_FN_RE` matches `<return-type> <name>(…)
  <impure|inline|method_id> {` with a negative lookahead that drops `return foo(...)`-style statements;
  `FUNC_CONST_RE`/`FUNC_GLOBAL_RE` capture `const`/`global` declarations. `recv_internal`/`recv_external` and
  `method_id` getters are marked externally-reachable; `impure` = state-changing. `TON_TAG_KEYWORDS` reuses the
  Solidity scoring tags (accounting/token/amm_pol/arithmetic/permissions/config) so DEX message-handlers and
  swap/LP/jetton math rank to the top, plus TON-native lenses (message_handler/bounce/cell/gas). Items are tagged
  `contract_type:"func_contract"`.
- **Specialists (`/ite-audit` → ton branch):** six TON-native agents —
  `agents/ton_sender_auth.md` (jetton transfer-notification SENDER bound to the contract's OWN jetton wallet,
  recipient/to_address derived not caller-supplied, privileged-op `equal_slices` gating, workchain/address-format,
  pool-lock `owner_address` spoof), `agents/ton_message_flow.md` (async non-atomicity, lp_account two-deposit race,
  reserve-vs-swap interleaving, partial-execution, replay/reorder), `agents/ton_bounce_handling.md` (ignored-bounce
  fund-stranding, bounce-no-rollback, non-bounceable sends, double-count, rate-desync), `agents/ton_carry_value.md`
  (gas under-forward stranding, raw_reserve/carry-all drain, storage-fee, value-not-validated, excess misroute),
  `agents/ton_cell_parsing.md` (malformed multihop cell misparse, missing `end_parse`/trailing-data, slice bounds,
  cell-depth DoS, format confusion), and `agents/ton_arithmetic.md` (TVM 257-bit muldiv overflow, rounding
  direction, stableswap convergence, signed-int/sqrt edge, precision scaling) — plus the language-agnostic
  conceptual specialists (logic, economic_attack, dos, access_control, behavioral_state_analysis). The
  Solidity-syntax specialists (reentrancy/storage-collision/erc4626/transient_storage/upgrade_storage) **and** the
  Solana/Move bundles are **skipped** — TON has no synchronous reentrancy, no flash loans, no Chainlink/slot0
  oracle, no ERC-4626/proxy-delegatecall. Each agent has a matching `.claude/skills/ton-*/SKILL.md`. Prefixes:
  `TSA-`/`TMF-`/`TBH-`/`TCV-`/`TCP-`/`TAR-` (registered in `validate_agent_output.AGENT_PREFIX_MAP`).
- **KB reachability:** the Solodit scraper already ingests FunC/Tact reports, so `kb/chroma` holds real TON DEX
  precedent (STON.fi V2/TONCO/Swap Coffee/PixelSwap/FIVA). `scripts/retag_ton_findings.py` (idempotent) re-tags
  those out of `vuln_type="other"` into a TON taxonomy (`jetton-theft`/`sender-spoof`/`bounce-stranding`/
  `message-race`/`cell-parsing`) so the specialist `tools/retriever.py <ton-type>` queries reach them through the
  hard `$eq` filter. The TON specialist skills query these types in their KB-recon phase.
- **Mechanism classes:** 18 `ton-*` classes in `config/mechanism_classes.json`, all `language:"ton"` +
  `status:"seeded"` (NEVER counted toward Solidity/Rust/Move recall; `eval_scoreboard` routes ton adjudications to
  `evals/ton_scoreboard.md`). Seeded from the TON DEX/jetton audit corpus; upgraded to `reincorporated` only when
  the recall lab earns them on scored TON contests. `evals/ton_scoreboard.json` is a seeded placeholder
  (recall **unmeasured** — no TON contest adjudicated yet) listing the available KB answer-key corpus.

## PoC (required by TON bounties)
- Template: `templates/ton_poc/` (`package.json` with the `@ton/blueprint`+`@ton/sandbox`+`@ton/test-utils` stack,
  `tests/poc.spec.ts` with the L1-entry / L2-state-flip / L3-outcome skeleton). PoCs run on **`@ton/sandbox`** — an
  **in-process TVM, no network, no testnet broadcast, no keys** — satisfying the "no live testing" rule with zero
  deployment. L1 = attacker message from a fresh `blockchain.treasury()`; L2 = read storage/balance via
  `blockchain.getContract(addr).account` or a wrapper get-method, assert before/after; L3 = prove the economic
  outcome and `console.log('BUG CONFIRMED')` (the harness `determine_status` keys "proved" off that string).
- For STON.fi-style targets, run PoCs **inside the target's own Blueprint repo** — it already ships typed wrappers
  (`Router.ts`/`Pool.ts`/`LPAccount.ts`/…) + compile, so you reuse the audited compile. Setup:
  `bash scripts/setup_ton_deps.sh <repo>` (= `npm install`). `generate_poc_test.load_repo_profile()` returns
  `{"language":"ton","framework":"blueprint"}` for a ton audit.
- Recon: read-only get-method calls (`get_router_data`/`get_pool_data`/reserves) on the testnet router via the
  public toncenter API confirm live deployed state (LIVE-STATE-FIRST). Read-only, no transactions.

## Why TON
TON DEXes hold large TVL and the FunC async actor model has a **distinct, under-tooled bug surface**: sender-address
spoofing on jetton `transfer_notification` (fake-deposit theft), ignored-bounce fund-stranding, carry-value/gas
drains, and malformed multihop-cell misparses — none of which the EVM specialists model. The public TON audit
corpus (TrailOfBits/Quantstamp reviews of STON.fi, TONCO, Swap Coffee, PixelSwap, FIVA) confirms every one of these
classes as a real awarded High/Medium, and they seed the specialist set. First target: **STON.fi dex-core-v2
v2.2.0** (HackenProof, Critical $100k) — a prior TrailOfBits review (2025-01) maps exactly where this protocol's
bugs cluster (the `lp_account` `to_address`/`route_dex_messages` class), making it a diff-the-audit lead.
