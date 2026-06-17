# P104 — Assisted PoC handoff: IQ-AI migration adopts an attacker-pre-created pool

**Verdict: ✅ CONFIRMED** (reproduced on a Fraxtal fork; source-backed root cause; no covering defense; minimal
mitigation validated). Subject: IQ-AI @ `db0d369b`. Severity: **Medium** (lost fee revenue + attacker-controlled
migration price; no direct theft of user principal). Not submitted — human review next.

## Summary
`LiquidityManager.moveLiquidity` (permissionless) migrates the bootstrap liquidity to Fraxswap via
`addLiquidityToFraxswap`, which does `getPair(currency, agent)` and **adopts any pre-existing pair**, setting the
protocol's intended fee only when it has to create the pair. Because Fraxswap `createPair` is permissionless, an
attacker can pre-create the `(currency, agent)` pair with an attacker-chosen fee and skewed reserves **before**
migration. The protocol then migrates into the attacker's pool — at the attacker's fee — and runs its
unslippage-guarded 3-round "alignment" swaps against attacker-controlled reserves.

## Root cause (source)
- `moveLiquidity()` — external, no access control.
- `addLiquidityToFraxswap()` — the pair-exists branch never verifies the existing pair's fee equals the intended
  `fee`, nor that the pair was protocol-created. The intended fee is applied only in the create branch.
- `createPair` is permissionless on the external Fraxswap factory.
Full trace: `p104/source_trace.md`. Defenses: `p104/defense_map.json` (DOES_NOT_COVER dominates).

## Attack scenario
1. A new agent's bootstrap pool reaches its end-criterion.
2. Attacker (no protocol role) calls `fraxswapFactory.createPair(currency, agent, lowFee)` (and may seed skewed
   reserves).
3. Anyone calls `moveLiquidity()`; the migration adopts the attacker's pair.
4. The live trading pool charges the attacker's fee and started at the attacker's price.

## Impact
The migrated pool charges the attacker's swap fee (**1 bps in the PoC**) instead of the protocol's intended
**100 bps** → ~99% of ongoing swap-fee revenue to the agent/LPs is lost for the life of the pool; the attacker
also controls the adopted pool's initial price/reserves (and can extract value from the unguarded alignment
swaps). Bounded to fee revenue + migration mispricing → **Medium**.

## Proof of Concept (reproduced)
Fraxtal fork @ block 12,918,968 (`rpc.frax.com`), `forge --evm-version cancun`.
- **`test_M01_attacker_precreate_low_fee_is_adopted`** → **PASS**: `migratedPair == attackerPair`;
  `intended feeBps 100`, `attacker-adopted feeBps 1`.
- Files: `p104/M01PreCreatePairPoC.t.sol`; output: `p104/reproduction_output.txt`; plan: `p104/poc_plan.md`.

## Recommended mitigation (validated)
In the pair-exists branch, reject a pre-existing pair whose fee differs from intent:
```solidity
require((10_000 - fraxswapPair.fee()) == fee, "unexpected pre-existing pair fee");
```
(or restrict pair creation / require the pair be protocol-created, and add slippage/min-out guards to the
alignment swaps). **Regression** (`p104/M01PatchRegression.t.sol`): with the guard, the attacker pair makes
`moveLiquidity` revert, while a clean migration still succeeds. The in-scope `LiquidityManager.sol` was restored
to its original hash `9a68efe4b6664f` after the temporary guard test.

## Assumptions / limitations
- PoC uses a Fraxtal fork (the project's own migration test is also fork-based; local mocking is insufficient —
  Fraxswap/BAMM/currency/whale are real Fraxtal state). `shareToBamm=0` (default) so BAMM is not exercised.
- The reproduced loss demonstrated is the fee bypass; the alignment-swap value extraction is plausible from
  source but not separately quantified here.
- Derived and reproduced from source + an executable PoC; **no answer-key wording used**. Scope/duplicate/
  program-severity and final wording remain human decisions; nothing is submitted.
