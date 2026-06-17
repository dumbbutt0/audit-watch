# Phase 88 — Under-rating / liveness calibration repair

## Why
P87 validated the P86 over-promotion fix (0 severity FP) but exposed the **opposite** direction:
- **H-01 `mintWithBudget`** (a permanent function-brick / liveness) was kept but **under-rated**.
- **M-18 `forgeWithListed`** (an **involuntary** fee-reduction race → stuck funds) was **false-demoted** as
  "self-inflicted."

Both blind runs (P81e H-03, P87 H-01 + M-18) point at the same gap: *under*-rating liveness and
involuntary-loss findings. P88 repairs it **without re-opening the P85/P86 severity-FP hole**. No blind eval.

## The fix — a liveness/involuntary ELEVATION in `severity_impact_gate`
New rule order (config + logic), elevation runs **after** the non-material floors and **before** the bounded
demote:
1. non-promotion passthrough.
2. **non-material impact CLASS floor** → demote (preserves D2 even if a material tag is mis-attached).
3. dust/transient **magnitude** + not concrete → demote (D2).
4. **P88 ELEVATION:** a source-backed **liveness** consequence, OR an **involuntary** harm with a **concrete**
   consequence → **KEEP**; report `high` when `high_liveness_markers` prove a core/all-users/unrecoverable
   brick, else `medium`. → never under-rated below Medium; never demoted by the bounded rule.
5. bounded and not concrete → demote (**P86 strictness preserved**: declared High can't save bounded evidence).
6. low → keep iff concrete, else demote.
7. material class → keep.
8. unproven → fail-closed.

New config tiers: `liveness_consequences` (denial_of_asset_movement, failed_settlement,
permanent_function_brick, blocked_{mint,claim,withdraw,settle,forge,buy_sell}_path, lifecycle_phase_bricked —
all also added to `concrete_material_consequences`), `involuntary_markers` (another_user_tx_ordering,
race_condition, third_party_listing_action, global_state_mutation_by_other, stale_flag_changed_by_other,
unavoidable_protocol_sequencing), `high_liveness_markers`, `self_inflicted_markers`.

**No-free-pass guard:** an involuntary marker **without** a concrete consequence does **not** keep a bounded
issue; `liveness` requires a source-backed liveness tag. So `updateTaxRate` (bounded, only misrouted_funds, no
concrete/liveness/involuntary-concrete) still demotes — even when declared High and even with an involuntary
marker attached.

## Regression anchors (all covered by tests)
| # | Case | Expected | Result |
|---|---|---|---|
| A | P87 H-01 liveness brick (+ high_liveness markers) | keep, report **high**; under-labelled low → keep ≥ medium | ✅ |
| B | P87 M-18 involuntary race + concrete stuck_funds | **keep** (even with a bounded marker attached) | ✅ |
| B′ | voluntary / avoidable, no concrete loss | **demote** | ✅ |
| C | P85 updateTaxRate (bounded, misrouted/stale only, +involuntary marker) | **demote** | ✅ |
| D | P85 H-05 reward-loss | keep | ✅ |
| E | P81e H-03 liveness (denial_of_asset_movement / failed_settlement) | keep | ✅ |
| F | P81a D2 dust (incl. mis-attached liveness tag) | demote | ✅ |
| G | guarded controls (REJECTED, +liveness/involuntary tags) | passthrough, never re-promoted | ✅ |
| — | declared High with ONLY bounded tags | demote | ✅ |

## P84 taxonomy addition — `validation_liveness_counter_scope`
New finding type (config + `templates/proof_requirements/validation_liveness_counter_scope.json`) for the H-01
class: global counter vs per-scope limit, invalid validation domain, permanent function-brick, blocked
mint/claim/withdraw/settle/forge/buy-sell path, lifecycle phase cannot complete. Reuses the generator +
templates unchanged; emits the same reject-first `DO_NOT_SUBMIT` bundle + guarded PoC scaffold (un-promotable).

## Integrity
- Allowed scope only: `severity_impact_gate.py` + config (logic), `config/handoff_finding_types.json` + new
  proof_requirements file (taxonomy), tests, docs.
- **`severity_impact_gate.py` hash changes by design** (`e7d29856` → `193abf9f`, authorized). Byte-identical:
  deep_pass `57c29fff`, hygiene `b9e18f29`, transitions `2c00069c`, lead_schema `3c57f04e`, abc_eval
  `5e0d855d`, surface_recall_lens `29a7b915`, surface_recall_score `fd3c7543`, funnel `720e9092`,
  handoff_generator `9c2c89cb` (new type needed **no** generator code change).
- No frozen artifact mutated. No production wiring (no-wiring grep CLEAN). 187 tests pass.

## Next
**P89 = fourth fresh sealed-key blind run** to verify both severity directions now calibrate — under-rating
fixed AND no severity FP reintroduced — on a fresh subject.
