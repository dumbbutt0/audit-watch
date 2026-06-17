# P269 — INTEGRATION_PROPOSAL (proposed, NOT wired — no production authority)

A research module. This proposes how a future full-path run would use it. Nothing here is wired; adoption is a
separate human decision.

## Proposed location
`dashboard advisory candidates → P267 pairwise selector → **P269 impact-first PoC triage** → PoC intent →
full / partial runtime harness → pre-reveal gate`. P269 sits between the selector and PoC intent — exactly where
P268 lost the award subsystem.

## Dashboard display (advisory only)
Show each triage decision as an advisory label on the standalone advisory surface: the outcome
(SELECT_FOR_FULL_POC / SELECT_FOR_PARTIAL_RUNTIME / SELECT_FOR_MANUAL_HARNESS_DESIGN / KEEP_AS_CONTROL /
DEFER_LOW_IMPACT / DEFER_INFEASIBLE), the `heavy_poc` flag, and impact_fit. No confirmed / reportable / severity state.

## PoC-queue behavior (proposed)
- `SELECT_FOR_FULL_POC` → normal PoC queue.
- `SELECT_FOR_PARTIAL_RUNTIME` → build a smaller invariant/runtime test (mock the heavy fixtures; assert the
  accounting/state delta directly) — the karak slashing/snapshot route.
- `SELECT_FOR_MANUAL_HARNESS_DESIGN` → operator designs the heavier fixture (beacon/slashing scaffolding).
- `DEFER_INFEASIBLE` → requires an explicit named blocker (source unavailable / unmockable dep / no exploit path /
  no falsifiable assertion).
- `DEFER_LOW_IMPACT` → lower priority.
- `KEEP_AS_CONTROL` → an easy/negative control, only after high-impact subsystems are represented.

## Budget
`poc_budget` (4) caps SELECT_*; every high-impact subsystem gets ≥1 routed representative before a control consumes
budget. A heavy award subsystem is never displaced by an easier low-impact candidate.

## Rollback
Remove the triage stage or run it disabled/no-op. Un-wired and advisory → removal returns the pipeline to the exact
P268 behavior with zero residue. No production file change to adopt or remove.

## What this does NOT change
No severity/routing/submission/confirmation-gate logic; no dashboard confirmed paths; no recall/selector/PoC plumbing;
no run_pipeline defaults. Production authority unchanged and withheld.
