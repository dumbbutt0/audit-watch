# M-1 (Medium) — Inverted ratio guard blocks legitimate de-risking of an unhealthy account (liveness/DoS)

- **Target:** TipRun, perp profile. Commit `d5d4d2a…`.
- **Contract:** `src/core/risk/Risk.sol` → `checkValidTransition` (line ~133 ratio guard).
- **Severity:** Medium (liveness / DoS; shares the root cause with F-1).
- **PoC:** `poc/PoC_DeriskDoS.t.sol` (passing) · log `poc_output.log`.

## Root cause
In the unhealthy branch, guard (C) reverts when
`initTotalValue * updatedTotalRisk < updatedTotalValue * initTotalRisk`, i.e. when the value/risk ratio **increases**
(the account gets healthier). The project's own `test_RiskRatioComparisonLogic` computes `ratioImproved =
initRisk·updatedValue > updatedRisk·initValue`, which is algebraically identical to this revert condition — so the
contract reverts exactly when the ratio improves. An account that is below maintenance margin and tries to **reduce**
its position (the legitimate way to recover) passes `checkSmallerInSyntheticHoldings` (positions shrank) and then
reverts at (C) — unless it can close enough in a single step to become fully healthy.

## Impact
With partial orderbook fills (the norm), an underwater account cannot recover incrementally: any partial de-risk that
improves health but stays under margin reverts `PM: val/risk dec`. Combined with F-1 (which lets accounts reach the
unhealthy state), positions can be stranded. The same gate sits on the trade and deleverage paths via
`FundingApplyLib.applyAndUpdate → PositionManager.updatePosition`.

## PoC (passing)
`forge test --match-contract PoC_DeriskDoS -vv` (from `../../harness/`):
- reach an under-margin account (collateral 2 000 / long 5 000 ⇒ value 7 000·FXP, risk 10 000·FXP²) via F-1.
- a fair **partial** de-risk — sell 500 synthetic for 500 collateral (value-neutral, risk ↓ to 9 000·FXP², strictly
  healthier but still under margin) — **reverts** `PM: val/risk dec`; the position is left untouched.
- only a de-risk large enough to reach *full* health in one step (sell 4 000) is allowed.

## Suggested fix
Invert the comparison so it reverts when the updated value/risk ratio *decreases* (account gets less healthy), with
explicit handling of negative `totalValue`; and apply the health-non-worsening guard unconditionally. One fix to
`checkValidTransition` resolves both M-1 and F-1.
