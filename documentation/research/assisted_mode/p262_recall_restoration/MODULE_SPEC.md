# P262 — MODULE_SPEC (recall_first_shape_sweep.py)
CLI: --manifest --accounting --state-transition [--base-candidates] [--prioritizer <p260.json>] --out [--md] [--quiet]
## Recall-first inclusion (over ALL in-scope fn items; NO P260 low-signal pre-filter = the fix)
1) top-10 by P260 score · 2) all T7/T8 in top-15 · 3) checkpoint-hit funcs in top-20 with recall name-keywords ·
4) any checkpoint-hit locus with evidence markers {shares/assets/debt/collateral/rewards/index/fees/epoch/queue/
pendingClaims/escrow/solvency/liquidation/redemption/migration/external_call/callback} · 5) **T9 math-name loci**
(checkpoint-hit OR strong-math name {decode/calc/calcreserve/lptoken/sqrt/muldiv/scale/convert}), bounded to ≤8.
## Templates: reuse T1–T8 (P260) + optional T9 (math/units/convergence), T9 ranked LAST (never dominates subtle path).
## Bounded output: ≤25 swept loci, ≤2 mech/template/locus, ≤5 mech/locus, ≤30 mech total; records truncated + counts.
## Zero-conclusion-FP guard: advisory only; status_label RECALL_CANDIDATE_ONLY; needs[NEEDS_RANKING/COMPLETION/
REFUTATION]; runtime-assert no severity/concluded/vulnerability/reportable/submission_ready. Promotion-gated (FP_GUARD.md).
