# P272 — DIAGNOSIS (Phase 10)

Fresh BLIND full-path rerun on init-capital (2024-01 invitational; 3H+4M; public findings; training-confound +
invitational-sparsity disclosed) with P267 selector + P269 triage + the P271 LENDING_COMPLETION_CHECKLIST applied
pre-reveal (no tuning).

## Counts
- target awarded: 3 High + 4 Medium (ALL in MarginTradingHook order management).
- advisory candidates: 20 (guard PASS; recall-delta 15/20 = 75%).
- selector: KEEP_BOTH ×3 (high-impact preserved); REFUTE_FIRST ×1 (unsupported drama).
- triage: 3 selected (liq-incentive FULL_POC; bad-debt + collateral-credit PARTIAL_RUNTIME); drama deferred.
- PoCs: 1 attempted, **1 PASS** (C-incentive, real code, exact); 2 NEEDS_MORE_RUNTIME (heavy).
- **exact awarded: 0** · strong: 0 · family: 0 · **non-awarded exact TP: 1** · severe concluded/reportable FP: **0**.

## Did the P271 checklist convert family→exact BLIND? — YES (capability generalized)
C-incentive was sharpened **blind, pre-reveal** from a recall candidate to an **exact, real-code, runtime-proven**
mechanism (min-floor-after-max-cap → multiplier 3.0e18 > 1.5e18 cap), using the checklist's "cap/guard ordering vs
value" item. So the **P271 family→exact bridge is NOT Wise-specific — it works on a fresh target.** This is the
positive, generalizable result.

## Why 0 AWARDED recovery — the objective mismatch (D)
- **Award-class mismatch.** init-capital's awards are **access-control / order-validation / front-running / DoS in the
  MarginTradingHook ORDER layer** (updateOrder access control, arbitrary tokenOut, fillOrder front-run, DoS). The
  impact-first triage (P269) + the P271 LENDING checklist target the **bad-debt / liquidation / collateral-credit
  ACCOUNTING class** — so selection steered to lending-accounting loci, away from the awarded access-control/order
  class. recall partially surfaced MarginTradingHook but the exact awarded loci (updateOrder/fillOrder) + the
  access-control class were not selected.
- **Non-awarded exact TP.** The one exact recovery (C-incentive) is a real ordering quirk requiring a `min>max`
  governance config — not awarded (likely QA/out-of-scope).
- **Target-fit / invitational compounding.** init-capital was picked as a money market expecting lending-accounting
  awards; its actual (sparse, invitational) awards live in a peripheral order-management hook — a target-class
  mismatch the content-safe screen could not detect (it verifies retrievability, not award-class, pre-reveal).

## Per-stage localization
- Recall: ✅ surfaced the lending subsystems + partially MarginTradingHook; ⚠️ did not surface the exact awarded
  order-mgmt loci (updateOrder/fillOrder) in the top-20.
- Selector: ✅ preserved high-impact lending mechanisms.
- Triage: ✅ routed lending-accounting impact classes — but that is exactly why the **access-control award class was
  not pursued** (impact-first prioritizes value-accounting impact, not access-control/validation).
- Completion: ✅ family→exact worked (C-incentive). PoC: ✅ real-code exact for the feasible one.
- Gate: ✅ conservative; 0 severe FP; C-incentive flagged with its config precondition.

## Comparison vs the arc
| phase | result |
|---|---|
| P270 wise | routed onto awarded loci; family-level; PoC harness-blocked |
| P271 wise (calibration) | family→exact + runtime (post-reveal) |
| **P272 init (blind)** | **family→exact GENERALIZED blind (C-incentive), but 0 AWARDED — award-class mismatch (D)** |
The family→exact capability now works blind. The new binding gap is **award-class targeting**: impact-first/lending-
accounting targeting ≠ this contest's access-control/order-management award class (the user's predicted "real bug
discovery ≠ contest-award matching").

## Bottleneck (one): **AWARD_CLASS_TARGET_FIT (objective mismatch)**
Not recall (subsystem partially surfaced), not the family→exact bridge (it worked), not safety (0 FP). The system
proved a real non-awarded mechanism while the awarded access-control/order class was de-prioritized by impact-first
lending-accounting targeting.
