# Phase 81f — Two generic repairs surfaced by P81d (recall + severity calibration)

**Result: PASS (repair/regression phase).** Both P81d-surfaced defects are fixed generically, with the protective
behaviour preserved and full regression green. Eval/repair only; no production wiring; promotes nothing.

| repair | before (P81d) | after (P81f) |
|---|---|---|
| **Fix 1 — missing-auth-setter recall** | Decent audited **8/9 DIRECT** (H-01 `setRouter` missed — `admin_config_setter` *required* an auth modifier, blind to unguarded setters) | Decent audited **9/9 DIRECT** (`setRouter` captured, `signals.auth_gated=False`); NOYA surface-relevant **8/8 preserved** |
| **Fix 2 — severity-gate calibration** | gate false-demoted true Mediums **M-04, M-01** to NEEDS_CONTEXT on conservative "revert/estimation" language (conversion hits 3) | M-04, M-01 **kept** (source-backed material consequence); D2 dust **still demoted** (conversion hits 5, **0 severity FP**) |

## Fix 1 — unguarded config setters are now captured (config-only)
`config/surface_recall_lens.json` `admin_config_setter`: **dropped `requires_auth_modifier`** and **added
`exclude_view_pure`**. An *unguarded* state-changing config setter (the missing-access-control bug class, e.g. H-01
unguarded `setRouter`) is exactly the interesting case and is now a lead; the existing `signals.auth_gated` flag
distinguishes guarded vs unguarded so the downstream deep-pass can still reject a guarded one. The lens **code is
byte-identical** (`surface_recall_lens.py` `29a7b915`) — `classify_surface` already supported a missing
`requires_auth_modifier` and `exclude_view_pure` (added in P81c), so this is a pure config repair. No subject names
added (no-subject-names test still passes). Verified: Decent audited 8/9→**9/9**; NOYA surface-relevant **8/8**
preserved (`setRouter` → `[admin_config_setter]`, `auth_gated=False`).

## Fix 2 — severity gate no longer false-demotes true Mediums
`config/severity_impact_gate.json` + `severity_impact_gate.py`: added `material_consequence_tags`
(`user_loss`/`protocol_loss`/`fund_loss`/`stuck_funds`/`frozen_funds`/`misrouted_funds`/`unauthorized_execution`/
`failed_settlement`/`denial_of_asset_movement`/`loss_of_capital`) and the rule **`lift_low_to_material_if_consequence`**.
A `low`-labelled candidate is **kept** when the impact_assessment asserts a **source-backed** material consequence
(`source_true` gates it); conservative wording (revert/estimation/routing/bridge/execution failure) alone no longer
demotes a true Medium. **Preserved:** dust/transient magnitude (and the dust *class*) with no material consequence
still demotes — the P81a D2 fix is intact. The material-consequence tags are read from the **key-blind** investigation/
review, never from an answer key.

**P81d re-score under the calibrated gate** (using the key-blind adversarial reviewer's own source-only language):
| lead | awarded | impact | before | after |
|---|---|---|---|---|
| `UniSwapper.swapNoPath` (D2 control) | — | dust | NEEDS_CONTEXT | **NEEDS_CONTEXT** (preserved) |
| `UTB.receiveFromBridge` | M-03 | high (unauthorized_execution) | POC_REQUIRED | POC_REQUIRED |
| `DecentBridgeExecutor.execute` | H-03 | medium (misrouted_funds) | POC_REQUIRED | POC_REQUIRED |
| `DecentEthRouter.bridge` | H-04 | medium (denial_of_asset_movement) | POC_REQUIRED | POC_REQUIRED |
| `StargateBridgeAdapter.bridge` | M-04 | low + denial_of_asset_movement/failed_settlement | NEEDS_CONTEXT | **POC_REQUIRED** ✓ |
| `UniSwapper.swap` | M-01 | low + stuck_funds/failed_settlement | NEEDS_CONTEXT | **POC_REQUIRED** ✓ |

Conversion hits 3 → **5**; severity FP still **0** (D2 demoted). The recall cost flagged in P81d is closed without
re-introducing the D2 over-promotion.

## Regression tests added (the user's a–d)
- (a) `test_4_unguarded_config_setter_is_captured` — unguarded setter advances (`auth_gated=False`); view `set`-named getter excluded.
- (b) `test_4_…` (guarded leg) + `test_4b_guarded_setter_rejected_downstream` — guarded setter is a surface but `auth_gated=True`, and the unchanged deep_pass REJECTs it via a blocking defense.
- (c) `test_9_p81f_dust_revert_control_still_demotes` — the D2 dust/revert-only control still demotes.
- (d) `test_10_p81f_true_medium_material_not_auto_demoted` — low + source-backed material consequence (failed-settlement/stuck/loss/unauthorized) is NOT auto-demoted; non-source-true material tag still demotes; dust class still demotes.
Plus 4 new cases in the module `--self-test`. **150 tests pass** (investigation 55 + signature_replay 22 + access_control 51 + candidates 22).

## Integrity
Touched (new hashes): `config/surface_recall_lens.json` `49b5c8a3`, `config/severity_impact_gate.json` `e420b01d`,
`scripts/investigation/severity_impact_gate.py` `0b7c54e4`. **Unchanged / byte-identical:** `surface_recall_lens.py`
`29a7b915` (config-only Fix 1), `deep_pass.py` `57c29fff`, `hygiene_validate.py` `b9e18f29`, `transitions.py`
`2c00069c`, `lead_schema.py` `3c57f04e`, `abc_eval.py` `5e0d855d`, `surface_recall_score.py` `fd3c7543`; parked
detectors (`f9ec0bff`/`e72b9994`) + value_flow (`aca9125a`). Artifacts: `_p81f/{recall_before_after,
severity_recalibration}.json` + `_p81f/_freeze/phase81f_freeze.json`. P81b/c/d reports carry the audited-source
correction. No-wiring CLEAN. Promotes nothing.

## Next — P81e (now unblocked)
Fresh **sealed-key blind** conversion test: a new contest subject, key sealed until all bundles frozen, run
lens (with both P81f repairs) → deep_pass → isolated key-blind adversarial → severity gate → keyed scoring. This is the
genuinely key-blind proof Decent could not provide. Order: leads ✅ → investigate-safe ✅ → severity gate ✅ →
conversion shown (key-known) ✅ → **repairs ✅ (this phase)** → P81e blind → PoC handoff.
