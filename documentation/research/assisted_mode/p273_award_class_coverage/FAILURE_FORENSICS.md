# P273 — FAILURE_FORENSICS

The P272 objective mismatch, from the frozen P272 reveal (no new answer keys).

## Init awarded class distribution (post-reveal)
All 7 awards (3H+4M) in **MarginTradingHook order layer**:
- H-01 `updateOrder` lacks access control → **ACCESS_CONTROL_AUTHORIZATION**.
- H-02 `updateOrder` arbitrary `tokenOut` → **ORDER_VALIDATION**.
- H-03 `fillOrder` front-run via `limitPrice_e36` → **FRONT_RUNNING_MEV**.
- M-01..M-03 MarginTradingHook DOS/cancel/balance → **DOS_LIVENESS** / ORDER_VALIDATION.
- M-04 LP-unwrap/MasterChef-reward DoS blocks decollateralize/liquidation → **DOS_LIVENESS**.
→ class distribution = {ACCESS_CONTROL, ORDER_VALIDATION, FRONT_RUNNING_MEV, DOS_LIVENESS}. **Zero** in
ACCOUNTING_LIQUIDATION_BAD_DEBT.

## What the current policy routed
P269 impact-first triage selected `liq_incentive_cap_order`, `health_zero_unliquidatable`, `coll_credit_miscalc` —
ALL **ACCOUNTING_LIQUIDATION_BAD_DEBT** (impact_class = liq_redemption_blockage / bad_debt / insolvency). The
lending-accounting class **monopolized** all 3 PoC slots. The awarded order/access/front-run/DoS classes got 0 slots.

## Why the order-layer awards were under-routed
P269 ranks by **value-accounting impact** (bad-debt/liquidation/insolvency weight 5–6; griefing_minor weight 2).
Access-control / order-validation / front-running candidates score LOW on that axis (they're not "value-at-risk
accounting" by impact_class), so impact-first triage structurally de-prioritizes them — even when they are the
awarded class. No layer enforced cross-class representation.

## Were the signals present pre-reveal?
**Yes, partially.** The advisory candidate set included MarginTradingHook functions: `repayDebt`, `addCollateral`,
`removeCollateral`, `coreCallback`, `_calculateFillOrderInfo` (T9). `_calculateFillOrderInfo`/`coreCallback` carry
ORDER_VALIDATION / FRONT_RUNNING_MEV signals (fill, order, callback). So a coverage layer keying on those signals
would have surfaced the order class as distinct from the accounting class and routed ≥1 representative — even though
the EXACT awarded loci (updateOrder/fillOrder) were not all in the top-20 (a recall-depth limit, separate from
coverage).

## The coverage rule that would have helped
"Before filling PoC slots, route ≥1 representative from each DISTINCT plausible high-signal class." Init's pool had
both ACCOUNTING (liquidation/collateral) AND ORDER_VALIDATION/FRONT_RUNNING (MarginTradingHook fill/callback) signals
→ the router would route ≥1 order-class rep instead of 3 accounting reps.

## How to avoid over-routing every access-control-looking function (anti-drama)
Many functions have `onlyOwner`/admin signals but are correctly gated (benign). The router must require, per the
anti-drama rule, a **source-backed signal + a falsifiable mechanism** (e.g. a missing/inconsistent check, an
arbitrary recipient, a mutable-order-before-fill race), not the mere presence of an access-control keyword. A properly
gated admin function = low signal → COVERAGE_CONTROL/DEFER, not a routed representative.
