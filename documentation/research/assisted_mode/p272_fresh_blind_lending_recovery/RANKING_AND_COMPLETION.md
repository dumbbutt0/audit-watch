# P272 — RANKING_AND_COMPLETION (Phase 5) — checklist-driven, BLIND

Five-op completion on the triage-selected mechanisms, **explicitly walking the P271 LENDING_COMPLETION_CHECKLIST**
to push family→exact PRE-REVEAL. (Checklist applied as read-only reference; not edited.)

## C-incentive — LiqIncentiveCalculator.getLiqIncentiveMultiplier_e18 (FULL_POC)
- **Checklist items applied:** "guard/cap ordering vs value" + "invariant deltas". The function caps the multiplier:
  `multiplier = Math.min(1e18+incentive, maxLiqIncentiveMultiplier_e18)` THEN `Math.max(multiplier,
  minLiqIncentiveMultiplier_e18[mode])`. The **min-floor is applied AFTER the max-cap.**
- **Exact mechanism:** `setMaxLiqIncentiveMultiplier_e18` and `setMinLiqIncentiveMultiplier_e18` are independent
  governor setters with **no `min ≤ max` invariant**. If `minLiqIncentiveMultiplier_e18[mode] > maxLiqIncentiveMultiplier_e18`,
  the final `Math.max(min(...,max), min[mode])` returns `min[mode]` — **the floor overrides the global max cap**, so a
  liquidator's incentive multiplier can exceed the intended protocol-wide maximum → over-seizure of collateral.
- **STS/IDC:** state {max=M, min[mode]=N>M} → multiplier = N > M (cap violated). **AAS:** liquidator permissionless.
  **TSE:** liquidator seizes `repayAmt × N/1e18` > the `max`-bounded amount. **CCIT:** n/a.
- **Status: COMPLETED_CHAIN (exact, runtime-provable on real code).** Caveat: requires a `min>max` config (no
  on-chain invariant prevents it) — a config-reachable invariant violation.

## C-health-zero — InitCore.liquidate health==0 bad-debt (PARTIAL_RUNTIME)
- **Checklist items applied:** "bad-debt cleanup invariants" + "guard ordering vs value". `liquidate` computes
  `liqIncentive = getLiqIncentiveMultiplier_e18(...)`; for `health_e18 == 0` (underwater) the calculator **returns 0**,
  so `repayAmtWithLiqIncentive = repayAmt × 0 = 0` → **no collateral seized**; and `_ensurePosHealthAfterLiq` is
  **bypassed** when `health==0`.
- **Exact mechanism (hypothesis):** a fully-underwater (health==0) position yields a 0 incentive multiplier → the
  liquidator receives 0 collateral for repaying → **no economic incentive to liquidate → bad debt cannot be cleared**
  (bad-debt-cleanup invariant violated), unless a separate socialization path exists (falsifier).
- **Status: PARTIAL_CHAIN** — exact-ish on paper; full confirmation needs the deposit→borrow→underwater→liquidate
  runtime (heavy). Routed PARTIAL_RUNTIME.

## C-coll-credit — InitCore.getCollateralCreditCurrent_e36 (PARTIAL_RUNTIME)
- **Checklist items applied:** "collateral accounting" + "position-vs-global" + "share/asset conversion". Collateral
  credit feeds the health factor; a miscalc would enable over-borrow / under-liquidation.
- **Status: PARTIAL_CHAIN** — needs the full health-factor runtime (heavy). Routed PARTIAL_RUNTIME.

## Summary
| candidate | checklist items that sharpened it | completion |
|---|---|---|
| C-incentive | cap-ordering, invariant-delta | **COMPLETED_CHAIN (exact, real-code PoC)** |
| C-health-zero | bad-debt-cleanup, guard-ordering | PARTIAL_CHAIN (heavy) |
| C-coll-credit | collateral acct, position-vs-global | PARTIAL_CHAIN (heavy) |
The most PoC-feasible (C-incentive, a near-pure formula) gets a real-code Tier-B PoC; the two heavy ones are
partial-runtime. Frozen before PoC code.
