# Phase 86 — Cross-eval severity calibration repair

## Why
Two blind evals converged on the **same** weak spot from opposite directions:
- **P81e** *under*-rated a real launch-DoS (H-03) → false-demote.
- **P85** *over*-rated a bounded/lazy-settlement accounting issue (Munchables `updateTaxRate`, tagged
  `misrouted_funds`, labelled Medium) → **severity FP that survived C**, tripping the strict 0-severity-FP bar.

So severity calibration — not surface recall and not adversarial discipline — is the cross-eval bottleneck.
P86 repairs it in both directions. **No blind eval is run in P86.**

## The fix — consequence tiering in `severity_impact_gate`
The gate previously kept any `medium`/`high`/`critical` impact_class and treated `misrouted_funds` as material.
P86 splits consequences into tiers (`config/severity_impact_gate.json`):

- **`concrete_material_consequences`** (the only tags that justify a keep): `user_loss`, `fund_loss`,
  `loss_of_capital`, `stuck_funds`, `frozen_funds`, **`reward_loss_not_recoverable`** (H-05 class),
  `protocol_loss`, `unauthorized_execution`, `denial_of_asset_movement`, `failed_settlement`.
- **`bounded_nonmaterial_consequences`** (do not count on their own): `misrouted_funds`, `accounting_drift`,
  `rate_mismatch`, `stale_parameter`, `delayed_settlement`, `display_mismatch`, `estimation_mismatch`,
  `eventual_correction`.
- **`bounded_lazy_markers`** (the user's "not enough by itself" list): stale configurable parameter, delayed
  settlement w/ eventual correction, admin inconvenience, theoretical accounting drift, bounded rate mismatch,
  temporary display/estimation mismatch, no quantified user loss, no blocked claim/withdraw/settlement path.

`concrete = source_true AND ≥1 tag in concrete_material_consequences`.
`bounded = any bounded_lazy_marker present, OR (consequence tags present but all bounded/non-material with no
concrete)`.

### Gate rule order (load-bearing)
1. non-promotion → passthrough.
2. dust/transient magnitude **and not concrete** → demote (D2 preserved).
3. non-material impact class → demote.
4. **bounded and not concrete → demote** — fires *before* the class-keep, so a declared High/Medium backed
   only by a bounded tag (`misrouted_funds`/`stale_parameter`) **cannot save weak evidence**.
5. `low` → keep iff concrete, else demote.
6. material class (medium/high/critical) → keep (reached only after the bounded check).
7. unproven → fail-closed → demote.

## Regression anchors (all covered by tests, `tests/investigation/test_severity_impact_gate.py`)
| # | Case | Expected | Result |
|---|---|---|---|
| A1 | P85 `updateTaxRate` (medium + `misrouted_funds`, material magnitude) | **demote** | ✅ |
| — | declared **High/critical** with only a bounded tag (`misrouted_funds`/`stale_parameter`) | **demote** | ✅ |
| A2 | H-05 dirty-flag-never-reset (`reward_loss_not_recoverable` / `stuck_funds`) | **keep** | ✅ |
| A3 | P81e H-03 liveness (`denial_of_asset_movement`/`failed_settlement`) | **keep** | ✅ |
| A4 | P81d M-04/M-01 failed-settlement (low/medium + `failed_settlement`) | **keep** | ✅ |
| A5 | P81a D2 dust/transient | **demote** | ✅ |
| A6 | controls (guarded admin) → `REJECTED` passthrough, never re-promoted | **rejected** | ✅ |
| — | bounded + concrete both present → concrete wins | **keep** | ✅ |
| — | `misrouted_funds` alone no longer lifts a `low` | **demote** | ✅ |

## P84 taxonomy addition — `reward_accrual_state_lifecycle`
New finding type (config + `templates/proof_requirements/reward_accrual_state_lifecycle.json`) for the H-05
class: dirty/stale flags, per-user reward checkpoints, reward debt/index lifecycle, reset/update omissions,
permanent reward loss, claim/withdraw misaccounting. Reuses the generator + templates unchanged and emits the
same reject-first bundle + guarded PoC scaffold (`DO_NOT_SUBMIT`, un-promotable). This gives a proper-fit type
for the P85 H-05 candidate (P85 had to use the closest type, `shared_position_fee_routing`).

## Integrity
- Allowed scope only: `severity_impact_gate.py` + its config (logic), `config/handoff_finding_types.json` +
  new proof_requirements file (taxonomy), tests, docs.
- **`severity_impact_gate.py` hash changes by design** (`0b7c54e4` → `e7d29856`, authorized). The other
  machinery is byte-identical: deep_pass `57c29fff`, hygiene `b9e18f29`, transitions `2c00069c`, lead_schema
  `3c57f04e`, abc_eval `5e0d855d`, surface_recall_lens `29a7b915`, surface_recall_score `fd3c7543`, funnel
  `720e9092`, handoff_generator `9c2c89cb` (the new type needed **no** generator code change).
- No frozen artifact mutated (P81e/P82/P83/P84/P85). No-wiring grep CLEAN.
- 174 tests pass across investigation / handoff / funnel / human_validation / candidate_detail / candidates.

## Next
**P87 = third fresh sealed-key blind run** to verify the calibration fix does not regress recall or conversion
(and that the new reward-accrual type is reachable when a relevant finding appears).
