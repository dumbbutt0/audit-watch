# P273 — INTEGRATION_PROPOSAL (proposed, NOT wired — no production authority)

Research module. This proposes future use; nothing is wired.

## Proposed pipeline position
`advisory candidates → P267 selector → **P273 award-class coverage router** → P269 impact-first triage (per selected
class) → completion/checklist → PoC intent → runtime proof`. P273 guarantees cross-class representation; P269 still
ranks by impact WITHIN each represented class. P273 does not replace P269.

## Dashboard display (advisory only)
Show, per candidate: award_class · signal_strength · coverage label (COVERAGE_SELECT/SELECT_HEAVY/CONTROL/DEFER_*) ·
the run's selected_classes + class_rationale. No confirmed / reportable / severity state.

## PoC-queue behavior (proposed)
- The `handoff_queue_to_p269` (the SELECT_* ids, spanning multiple classes) is what P269 ranks/routes.
- COVERAGE_SELECT_HEAVY → P269 routes PARTIAL_RUNTIME (per P269's own rule).
- COVERAGE_CONTROL → only if budget remains after class representation.
- COVERAGE_DEFER_* → not handed off (recorded with reason).

## Budget interaction
P273 `poc_budget` (5) bounds the cross-class handoff; P269's own budget (4) then applies within. Tune so cross-class
representation is preserved before same-class depth.

## Rollback
Remove the router stage or run it disabled. Un-wired + advisory → removal returns the pipeline to P269-direct (the
P272 behavior) with zero residue. No production file change to adopt or remove.

## What this does NOT change
No severity/routing/submission/confirmation logic; no P269 internals; no recall/selector/dashboard/PoC infra; no
run_pipeline defaults. Production authority unchanged and withheld.
