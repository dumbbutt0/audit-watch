# P207 — Vultisig positive-control dependency assembly for L3 validation

## Context
P205 validated the L3 realized-impact HIGH standard's **demotion** side on Vultisig but stayed `PARTIAL`: the
**positive-control High** harness was blocked purely by dependency assembly (solc 0.7.6 + OZ 3.4 + Uniswap V3, no
locally-compatible deps). P206 searched for a lighter positive-control corpus and found none (munchables Highs are
demote-class DoS/griefing; pooltogether's lone High is trusted-prereq) → `FALLBACK_TO_VULTISIG_DEPENDENCY_ASSEMBLY`.
P207 executes that fallback: assemble a minimal isolated 0.7.6 Vultisig harness env and run the missing positive
control (H-01) + the negative control (M-03), to convert P205 `PARTIAL` → `VALIDATED` (or fail/stay-partial honestly).
This reuses P205's already-mapped target classes — **no new blind run**.

## Recon already done (read-only) — assembly is de-risked
- **External deps are bounded; NO v3-periphery needed** — Vultisig vendors its own periphery libs locally
  (`src/base/PeripheryPayments.sol`, `src/libraries/{PoolAddress,LiquidityAmounts,TransferHelper,SqrtPriceMathPartial,
  PositionKey,ChainId}.sol`). External imports are only: **OZ 3.4** (`ERC721`, `Clones`, `EnumerableSet`, `IERC20`,
  `IERC721Enumerable/Metadata`) and **v3-core 0.7.6** (`IUniswapV3Factory/Pool`, `callback/IUniswapV3MintCallback`,
  libs `FullMath`/`TickMath`/`SqrtPriceMath`/`FixedPoint128`/`FixedPoint96`/`UnsafeMath`).
- **Network + forge install confirmed**: `git ls-remote` returns `OpenZeppelin/openzeppelin-contracts@v3.4.0`
  (`7985e4d0`) and `Uniswap/v3-core@v1.0.0` (the 0.7.6 release). Both installable by tag → no vendoring guesswork.
- **H-01 mechanism** (`ILOPool.claim`, lines 184-263): all investors share ONE V3 position; the first claimer's
  `pool.burn(TICK_LOWER,TICK_UPPER,…)` + `pool.collect(…,max,max)` pulls the whole position's accrued fees and ships
  the excess to the feeTaker, so later legitimate claimers' fee math (`feeGrowthInside_now − stored_last`) under-pays
  or **reverts** (`amountCollected − amount` underflow / insufficient balance) = material fee loss to most users.
  Faithful harness needs a real-or-faithful V3 pool with fee-growth accounting.
- **M-03 mechanism** (`ILOPool.buy`): `buy()` never calls the live pool (uses stored `saleInfo` + sqrt consts + pure
  libs + ERC721 + ERC20); transferring the NFT then re-buying mints a fresh tokenId with `raiseAmount=0` → bypasses
  `maxCapPerUser`. No pool needed → easiest harness.

## Strict scope / allowed (from brief)
No production prompt/`deep_trace.md`/checker/router/ledger/detector/dashboard change; no L3 wiring; no
submit/route/promote/demote; **no edit to original Vultisig source**; not a full audit; deps + harnesses isolated under
the P207 dir. Allowed: isolated Foundry project, vendor/install compatible deps, remappings, external-only mocks,
minimal non-source-modifying adapters, byte-identical `realsrc/` copy with hash checks, harnesses + run logs.

## Execution sequence
Work dir: `documentation/research/assisted_mode/p207_vultisig_l3_dependency_assembly/`; Foundry project + harnesses
under `…/pocs/p207/` (keeps `audits/vultisig…/src` untouched).

1. **Integrity precheck** (`INTEGRITY_PRECHECK.md`): START md5-first-8 for `prompts/deep_trace.md` (`ef93a6c2`),
   `scripts/validate_deep_pass_mechanisms.py` (`5d2a97f9`), `scripts/eval_locus_resolver.py` (`3b0b2c02`), hermes
   ledger (`fc446040`), Vultisig src tree (`d9489e47`); confirm Vultisig src untouched; record that the answer key was
   opened read-only in P205 (mapping reused, no new blind run); confirm P205 freeze `fa1afe1b`.
2. **Isolated env** (`pocs/p207/foundry.toml`): solc 0.7.6; remappings `@openzeppelin/=lib/openzeppelin-contracts-3.4/
   contracts/`, `@uniswap/v3-core/=lib/v3-core/`; `vult/=realsrc/src/`; copy Vultisig `src/` byte-identically into
   `realsrc/src/` (hash-verify `d9489e47`). Reuse P205's forge-std-free pattern (inline `Vm` + `HarnessBase`).
3. **Dependency assembly** (`DEPENDENCY_ASSEMBLY.md`, `COMPILE_LOG.md`): `forge install OpenZeppelin/
   openzeppelin-contracts@v3.4.0` + `Uniswap/v3-core@v1.0.0` into `pocs/p207/lib/` (isolated). Record exact tag/commit
   + why 0.7.6-compatible. If install fails, vendor the specific files; if still impossible → `DEPENDENCY_BLOCKED`.
4. **Compile target contracts**: `forge build` on `realsrc/` ILOPool + ILOManager + base + libraries + interfaces.
   Pass = compiles with no edit to copied source. If it fails, classify blocker (missing dep / compiler incompat /
   source mismatch / artifact needed / package too large) and stop `DEPENDENCY_BLOCKED` (no faked harness).
5. **L3 target matrix** (`L3_TARGET_MATRIX.md`): H-01 positive (awarded High; expected `HIGH_CONFIRMED` if material
   fee loss executes) and M-03 negative (awarded Medium; expected `MEDIUM_OR_LOWER` unless material value movement) —
   each with target contracts, attacker/victim setup, tx sequence, measured invariant, pass/fail.
6. **Positive control H-01** (`H01_POSITIVE_CONTROL_POC.md`, `pocs/p207/test/H01_claimFees.t.sol`): real `ILOPool`
   against a V3 pool — **prefer the REAL v3-core `UniswapV3Pool`** (deploy via real factory, real liquidity via
   `launch`, accrue fees via a real swap) for maximal faithfulness; **fallback = a FAITHFUL minimal pool mock**
   implementing canonical V3 `mint`/`burn`/`positions`/`collect`/feeGrowth accounting for one position (fees injected
   via a realistic accrual path, NOT rigged to manufacture the bug — the bug must emerge from ILOPool's cross-user
   accounting). Two position-holders A,B; A claims then B claims; assert B's realized fees ≪ fair share or B's claim
   reverts; before/after balances; control case (single holder claims fairly). Expected `HIGH_CONFIRMED`; if path
   unreachable within budget → `HARNESS_INCONCLUSIVE` (documented).
7. **Negative control M-03** (`M03_NEGATIVE_CONTROL_POC.md`, `pocs/p207/test/M03_capBypass.t.sol`): real `ILOPool`
   initialized with source-valid params (dummy pool addr ok — `buy` never calls it); one buyer fills `maxCapPerUser`,
   transfers the NFT to a fresh address, buys again → assert total allocation by one entity exceeds `maxCapPerUser`
   while they paid full `raiseAmount` each time (no theft) → demote below High. Before/after balances + position state.
8. **Run tests**: `forge build` + `forge test -vvv`; save run logs, traces, pass/fail counts to `pocs/p207/`.
9. **L3 scorecard** (`L3_SCORECARD.md`, `metrics.json`): H-01 result, M-03 result, whether P205 PARTIAL→VALIDATED,
   genuine High preserved, Medium demoted/contradicted, false-Highs/false-demotions (target 0), harness + dependency
   limitations.
10. **Decision + failures + recommendation** (`FAILURE_CASES.md`, `P207_RECOMMENDATION.md`) + integrity re-check +
    memory. Copy this plan to `P207_PLAN.md`.

## Decision space
`L3_STANDARD_VALIDATED_SECOND_CORPUS` (H-01 executes material impact = `HIGH_CONFIRMED` **and** M-03 shows no
High-level material impact = demote, both reproducible, production byte-identical) · `L3_STANDARD_PARTIAL` ·
`L3_STANDARD_FAILED_FALSE_HIGH` · `L3_STANDARD_FAILED_FALSE_DEMOTION` · `DEPENDENCY_BLOCKED` · `HARNESS_INCONCLUSIVE` ·
`INVALID_RUN`. **Expected:** `VALIDATED` (deps confirmed installable; M-03 trivially harnessable; H-01 the only real
effort — faithful V3 pool), with `HARNESS_INCONCLUSIVE` as the honest fallback if the faithful fee-growth path can't be
executed within budget.

## Acceptance criteria
Deps isolated under P207 only; no production source edits; target contracts compile (or blocker honestly classified);
≥1 positive High + ≥1 negative control attempted; L3 impact **measured not inferred**; P205 PARTIAL upgraded / stays
partial for a precise reason / fails honestly; production hashes byte-identical START==END
(`ef93a6c2`/`5d2a97f9`/`3b0b2c02`/ledger `fc446040`, Vultisig src `d9489e47`); JSON valid; `fabrication_rate=0` (every
verdict backed by a run log or a documented source-valid-setup obstacle).

## Deliverables
`P207_PLAN.md` · `INTEGRITY_PRECHECK.md` · `DEPENDENCY_ASSEMBLY.md` · `COMPILE_LOG.md` · `L3_TARGET_MATRIX.md` ·
`H01_POSITIVE_CONTROL_POC.md` · `M03_NEGATIVE_CONTROL_POC.md` · `L3_SCORECARD.md` · `FAILURE_CASES.md` ·
`P207_RECOMMENDATION.md` · `metrics.json` · `integrity_checks.md` · `pocs/p207/` (foundry.toml, lib/ installed deps,
realsrc/ byte-identical copy, test/*.t.sol, run logs). Memory: `project_phase207_*` + one-line MEMORY.md pointer.

## Verification
`forge build` compiles `realsrc/` ILOPool+ILOManager with no source edit; `forge test -vvv` passes the H-01 + M-03
harness assertions (logs saved); `metrics.json` valid JSON; production hashes + Vultisig src tree byte-identical at
END; deps confined to `pocs/p207/lib/`.

## Follow-on (NOT this phase)
If `VALIDATED`: L3 confirmed on a 2nd corpus (positive+negative) → only then consider operationalizing the L3 HIGH bar
(require a passing L1/L2/L3 PoC for HIGH promotion; auto-scaffold vs human + cost) — still pre-wiring. Optional cheap
add-on: munchables executable demotion of a genuine awarded High (P206 secondary). Deep-pass recall + oracle separate.
