# Evidence bundle — ILOPool.claim shared-position fee accounting

Internal reviewer material backing `submission_draft.md`. Every claim here is anchored to in-scope source or
to an executable result. Nothing here is derived from an answer key.

## Subject / pinned version
- Repo: `github.com/code-423n4/2024-06-vultisig`
- Commit (pinned): `befb1b11702a26ad0018308ef6e82b73683fe1d6`
- Submodules: forge-std `52715a2`, openzeppelin-contracts `04695ae`, v3-core `d8b1c63`
  (`git submodule update --init --recursive`)
- Toolchain: `forge 1.5.1`, solc `0.7.6`

## Exact source references (in-scope)
- `src/ILOPool.sol`
  - `claim()` — ≈ L184–261 (entry point under test)
  - `pool.burn(TICK_LOWER, TICK_UPPER, liquidity2Claim)` — ≈ L205 (credits all fees for the position's full
    liquidity into `tokensOwed`)
  - `pool.collect(address(this), TICK_LOWER, TICK_UPPER, type(uint128).max, type(uint128).max)` — ≈ L242–248
    (pulls the whole owed balance, including other investors' fees)
  - per-NFT amount computation against `_positions[tokenId].feeGrowthInside…Last` — ≈ L214–231
  - payout to claimant — ≈ L252–253
  - residual forwarded to `feeTaker` — ≈ L259–260
  - `launch()` — ≈ L269–335; `addLiquidity(...)` mints the single shared position — ≈ L296–303
  - `buy()` — ≈ L126–176 (per-NFT positions created without fee checkpoints)

These line ranges are the audited-source anchors; a triager should confirm them at the pinned commit (exact
numbers may shift by a line or two with formatting).

## PoC
- PoC file (provenance copy): `documentation/research/_p82_h01_claim_poc/poc_test/H01ClaimFeeSiphon.t.sol`
  - Place into the repo's `test/` directory to run (it `import`s the repo's own `test/IntegrationTestBase.sol`).
- Test-harness note: `test/IntegrationTestBase.sol` forks mainnet; its hard-coded `rpc.ankr.com/eth` now
  requires a key, so the fork URL was switched to the keyless public node `https://ethereum-rpc.publicnode.com`
  and the pinned block dropped (fork at latest). This is a **test-fixture** change only — no in-scope contract
  is modified, and the in-scope contracts are deployed locally in the test. A reviewer with a keyed archive
  RPC can pin a specific block for full determinism.

## Command run
```
forge test --match-test testH01_ClaimProceedsAreOrderIndependent -vv
```

## Vulnerable-source failure output (current source — test FAILS, as intended)
```
[FAIL: H-01: INVESTOR_2 claim REVERTS after INVESTOR claimed first (fees already swept to feeTaker)]
  INVESTOR_2 USDC, claiming FIRST  (fair)  : 15151790833520151101763
  INVESTOR_2 claim succeeded when SECOND? (1=yes,0=revert): 0
  INVESTOR_2 USDC, claiming SECOND (bugged) : 0
  USDC lost by INVESTOR_2 due to earlier claim: 15151790833520151101763
```
Interpretation: investor 2 receives ~15,151 USDC when claiming first, but reverts and receives 0 when claiming
after investor 1 — the shared-position fees were already collected and routed to `feeTaker`.

## Minimal patch validation (discriminator — proves the root cause)
- Patch: change `pool.collect(..., type(uint128).max, type(uint128).max)` (≈ L246–247) to
  `pool.collect(..., uint128(amount0), uint128(amount1))` — collect only what this claim distributes, leaving
  the other investors' fees in the Uniswap position.
- Result after patch: `testH01_ClaimProceedsAreOrderIndependent` **PASSES** — investor 2 receives ~15,151 USDC
  in either order, no revert.
- Source was restored after validation. This patch is an *illustrative discriminator*, not a vetted production
  fix (the production fix must also preserve correct platform/performance-fee routing).

## Unrelated test-suite result (no collateral breakage)
- `forge test` (full suite): **29/29 existing tests pass**; only the PoC test fails on the vulnerable source
  (the intended proof). No unrelated test is broken by the PoC's presence.

## Reproduction provenance (frozen artifacts — read-only, for integrity)
The reproduction was frozen; these references let a reviewer confirm nothing changed under them. SHA-256
prefixes from `documentation/research/_p82_h01_claim_poc/_freeze/phase82_freeze.json`:
- `bug_chain.md` → `458897f7fa3a`
- `handoff_report.md` → `228856db622b`
- `H01ClaimFeeSiphon.t.sol` → `2ceac0146031`
- `run_log.md` → `7ec833a1ef81`

Source-grounded bug chain (full): `documentation/research/_p82_h01_claim_poc/bug_chain.md`.
