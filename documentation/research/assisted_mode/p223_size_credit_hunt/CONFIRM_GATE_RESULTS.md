# P223 — Confirm-gate results (Step 6)

## min_confirm_gate (ran in review-gate)
PASS — 3 poc_required candidates (SC-01/03/04), 3 confirmed (skeleton fields present), 0 blocking.

## confirm_inventory
12 candidates inventoried → `output/confirm/confirm_inventory.json`. (All 12 flagged "missing confirmation
fields" — expected; the deep_trace candidates carry exploit context but not the full confirm-skeleton, which is
why the High candidate is routed to PoC rather than auto-confirmed.)

## confirm_reachability
→ `output/confirm/reachability_analysis.json`
- by_status: **likely_reachable 5 · uncertain 6 · privileged_only 1**
- by_action: keep 5 · needs_manual_review 5 · downgrade 1 · needs_runtime_poc 1

## confirm_gate
- `--mode eval`: **PASS** (advisory; candidates 12, blocking 0, warnings 7).
- `--mode submission`: **PASS, exit 0** (candidates 12, blocking 0, warnings 7) — no High/Critical candidate is
  non-credible, so the submission gate does not hard-fail. (SC-01 is High but credible; severity promotion is
  deferred to the L3 gate, which is the correct division of labor — confirm_gate checks credibility/reachability,
  L3 decide() owns High promotion.)

Note: `confirm_gate.py`, `min_confirm_gate.py` byte-identical START==END (forbidden files; only read here).
