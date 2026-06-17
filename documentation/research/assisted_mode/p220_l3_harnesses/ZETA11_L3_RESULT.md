# ZETA-11 — L3 result: PASS (DoS) / theft is WRONG_MECHANISM

**Harness.** `pocs/p220/test/ZETA11_trident.t.sol` · real unmodified `ZetaTokenConsumerTrident` ·
mocks: `MockTridentFactory` (returns the pool list the test sets) + `MockTridentRouter` (1:1).
**Command.** `forge test --match-contract ZETA11 -vv` → **2/2 PASS** (`pocs/p220/logs/ZETA11_run.log`).

## What was proven
- **PoC (DoS).** With no pool for the pair, `getPools(...)` returns an empty array and `getZetaFromEth` reverts at
  `pairPools[0]` (array out-of-bounds, Panic 0x32) → the core ETH→Zeta swap path is bricked for that pair.
  (`test_emptyPools_bricksGetZetaFromEth`.)
- **Control.** With one pool present, the same call routes through and returns the router output (`1e18`, no revert)
  → the revert is caused specifically by the unvalidated empty `getPools(...)[0]`, not by the call shape.
  (`test_control_withPool_swapSucceeds`.)

## Mechanism distinction (key result)
- The candidate was filed as **theft** (High): an attacker pre-registers a malicious pool that gets routed as
  element `[0]`. That depends entirely on an **external** property — whether the real Trident factory allows
  permissionless pool registration — which is **not present or assertable in the in-scope source**. The harness
  therefore does **not** assert a theft outcome (a `SCOPE NOTE` in the test documents this).
- What the harness *does* reproduce on real source is a **DoS** (empty / unvalidated `getPools()[0]`), a different
  mechanism than the theft claim → **WRONG_MECHANISM_PARTIAL**.

## Classification & calibration
- **l3_status = PASS** (DoS mechanism, executed, with control), `poc_tier = L3_REAL_CONTRACT_POC`,
  `impact_class = dos`, `dependency_mocks = external_only`.
- `decide()` → **calibrated_severity = medium**, `high_promotion_allowed = false`,
  blocker = `attacker_model=unknown (need permissionless/program_accepted)`: the empty-pool DoS is a
  liquidity/deployment state, not an attacker-triggered action, so it is not auto-promoted.
- **Scorecard P220 category: `WRONG_MECHANISM_PARTIAL`** (impact reproduced as DoS; candidate theft mechanism
  not source-confirmable).

## Post-score note (answer key, not used to shape the harness)
Official mapping (~H-10) concerned a different Trident mechanism; P215 already recorded ZETA-11 as a wrong-mechanism
partial. Recorded only in `scoring_note`/`last_reviewer_note`.
