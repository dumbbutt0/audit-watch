# P82 — PoC Handoff Report: Vultisig 2024-06 H-01 (ILOPool.claim fee siphon)

## Status: **REPRODUCED**

An executable Foundry test fails on the vulnerable source for the exact source-derived reason (a later claimant's
`claim()` reverts / loses their entire vested position because an earlier claim swept the shared position's fees to
`feeTaker`), and passes under a minimal patch. Built from source behavior; the answer key was used only as a
post-freeze scoring reference (P81e), never as the source of truth.

## Subject / environment (reproducible)
- Repo `github.com/code-423n4/2024-06-vultisig` @ `befb1b11702a26ad0018308ef6e82b73683fe1d6`.
- Submodules: forge-std `52715a2`, openzeppelin-contracts `04695ae`, v3-core `d8b1c63` (`git submodule update --init`).
- Foundry `forge 1.5.1`, solc `0.7.6`.
- The harness `test/IntegrationTestBase.sol` forks mainnet; its hardcoded `rpc.ankr.com/eth` now requires a key, so the
  fork URL was switched to the keyless public node `https://ethereum-rpc.publicnode.com` and the pinned historical block
  was dropped (fork at **latest** — the only mainnet deps are the stable Uniswap V3 factory / WETH9 / USDC addresses).
  This is a **test-fixture** change, not a change to any in-scope contract.
- PoC file: `test/H01ClaimFeeSiphon.t.sol` (copied to `poc_test/` here). Reuses the repo's own `IntegrationTestBase`
  helpers + a 30-line `PoolSwapper` to accrue real Uniswap fees.

## Exact command
```
forge test --match-test testH01_ClaimProceedsAreOrderIndependent -vv
```

## Exact failing assertion / trace (vulnerable source)
```
[FAIL: H-01: INVESTOR_2 claim REVERTS after INVESTOR claimed first (fees already swept to feeTaker)]
  INVESTOR_2 USDC, claiming FIRST  (fair)  : 15151790833520151101763
  INVESTOR_2 claim succeeded when SECOND? (1=yes,0=revert): 0
  INVESTOR_2 USDC, claiming SECOND (bugged) : 0
  USDC lost by INVESTOR_2 due to earlier claim: 15151790833520151101763
```
The test encodes the **invariant that holds on correct code**: a position's claim proceeds are independent of whether
another LP claimed first. On the vulnerable source INVESTOR_2 receives 15,151 USDC when claiming first but **reverts and
receives 0** when claiming after INVESTOR → `assertTrue(okB)` fails.

## Validation gates (all met)
- **Fails on vulnerable source for the expected reason:** ✅ (above — later claimant locked out once fees > the 0.1%
  platform-fee buffer; with small fees the loss is silently masked, also documented).
- **Passes under a minimal patch:** ✅ — changing `pool.collect(..., type(uint128).max, type(uint128).max)` (L246-247)
  to `pool.collect(..., uint128(amount0), uint128(amount1))` (collect only what this claim distributes, leaving other
  LPs' fees in the pool) makes the test PASS (INVESTOR_2 gets 15,151 USDC in either order, no revert). Patch applied to a
  copy then reverted; this is an *illustrative* discriminator, not the production fix.
- **No unrelated tests broken:** ✅ — full suite: 29/29 existing tests pass; only this PoC fails (the intended proof).
- **Source citations captured:** ✅ (`bug_chain.md`).
- **No unsupported claims:** ✅ — every step is source-line-anchored and executable.

## Impact statement
LPs other than the first claimant lose their share of accrued Uniswap fees (diverted to `feeTaker`); once accrued fees
exceed the platform-fee buffer, later claimants **cannot withdraw their vested liquidity at all** — `claim()` reverts and
the position's funds are locked. High severity (matches awarded H-01).

## Remaining uncertainty
- The **loss is magnitude-dependent**: below ~0.1% accrued fees relative to a position's principal, the double-counted
  fee is absorbed by the platform-fee buffer and the claim still succeeds (silent under-payment rather than revert). The
  revert manifests once fees exceed that buffer (demonstrated with realistic swap volume). A submission draft should
  present both regimes (silent fee loss → hard lock).
- The minimal patch here is a discriminator, not a vetted production fix (the real fix must also preserve correct
  platform/performance-fee routing).
- Fork is at `latest` rather than the contest's pinned block; the in-scope contracts are deployed locally in the test,
  so this does not affect the result, but a submission can pin a specific archive block via a keyed RPC for determinism.

## Ready for human submission drafting?
**Yes.** REPRODUCED with an executable failing test, a source-anchored bug chain, a discriminating minimal patch, and a
clear impact statement. Recommended next step (human): write the C4-style submission from `bug_chain.md` +
`H01ClaimFeeSiphon.t.sol`, presenting the silent-fee-loss and hard-lock regimes.

## Integrity
PoC built in an external clone; **no change to any Audit-Watch detector/lens/deep_pass/hygiene/severity machinery**, and
**no change to any in-scope Vultisig contract** (the only edits were the test-harness fork URL and a temporary,
reverted illustrative patch). P81e artifacts untouched and frozen. Research/eval only; promotes nothing.
