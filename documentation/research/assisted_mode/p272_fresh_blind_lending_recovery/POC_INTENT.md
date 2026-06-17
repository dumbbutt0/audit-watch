# P272 — POC_INTENT (Phase 6, frozen BEFORE PoC code)

Mechanism claims frozen pre-code (committed in RANKING_AND_COMPLETION.md + the selector/triage inputs before any PoC
code). No answer key. BLIND.

## C-incentive (LiqIncentiveCalculator) — FULL PoC, Tier B
- Target: `getLiqIncentiveMultiplier_e18`. Root cause: min-floor `Math.max(.., minLiqIncentiveMultiplier_e18[mode])`
  applied AFTER max-cap `Math.min(.., maxLiqIncentiveMultiplier_e18)`; independent setters, no `min<=max` invariant.
- Attacker/condition: a `min[mode] > max` config (governor setters, no cross-check). Liquidator of an unhealthy
  position then receives a multiplier above the protocol-wide max → over-incentive / over-seizure.
- Setup: clone+init LiqIncentiveCalculator (MockACM); set mode/token mults; set min[mode] > max.
- Assertion: `getLiqIncentiveMultiplier_e18(mode, health<1e18, ...) > maxLiqIncentiveMultiplier_e18`. Control:
  min<=max → cap holds. Refutation: a `min<=max` invariant enforced elsewhere.

## C-health-zero (InitCore.liquidate health==0) — PARTIAL, heavy
- Hypothesis: health==0 → incentive multiplier 0 → 0 collateral seized + post-liq health check bypassed → underwater
  positions unliquidatable / bad debt unrecoverable. Refutation: separate bad-debt socialization path.
- Status: NEEDS_MORE_RUNTIME (full deposit→borrow→underwater→liquidate stack).

## C-coll-credit (getCollateralCreditCurrent_e36) — PARTIAL, heavy
- Hypothesis: collateral-credit/health miscalc → over-borrow/under-liquidation. Status: NEEDS_MORE_RUNTIME.
