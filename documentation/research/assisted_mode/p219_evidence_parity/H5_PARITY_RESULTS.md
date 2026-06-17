# P219 — H5 PARITY RESULTS (per-candidate)

Criteria for READY-for-analysis (structural + evidence-source parity, NOT content/severity): function map present or
explicitly unavailable · attacker model present or explicitly blocked · exploit path present or explicitly missing ·
PoC verification present if a PoC exists (else explicit NEEDS_HARNESS) · impact explains who-loses/who-gains or says
unknown · blocker reason present · evidence_backup links present · safety flags correct.

| candidate | classification | note |
|-----------|----------------|------|
| ZETA-07 | **H5_STYLE_READY_FOR_ANALYSIS** | executed PoC; actual/expected/control/value-delta + who_loses + asset all present (8/8 depth) |
| ZETA-04 | **H5_STYLE_READY_FOR_ANALYSIS** | =H-13; mechanism/function_map/attacker+reachability/exploit/defense/asset present; executed-PoC explicit NEEDS_HARNESS |
| ZETA-11 | **H5_STYLE_READY_FOR_ANALYSIS** | ≈H-10; reachability + expected/control + asset present; actual/value-delta NEEDS_HARNESS |
| ZETA-01 | H5_STYLE_READY_FOR_ANALYSIS | 5/8 depth (control + asset + loss_type); NEEDS_HARNESS actual |
| ZETA-03 | H5_STYLE_READY_FOR_ANALYSIS | privileged/centralization; who_loses + value-delta + asset present |
| ZETA-05 | H5_STYLE_READY_FOR_ANALYSIS | privileged; asset + loss_type; NEEDS_HARNESS actual |
| ZETA-06 | H5_STYLE_READY_FOR_ANALYSIS | conditional; asset + loss_type; NEEDS_HARNESS actual |
| ZETA-08 | H5_STYLE_READY_FOR_ANALYSIS | privileged; who_loses + value-delta + asset present |
| ZETA-10 | H5_STYLE_READY_FOR_ANALYSIS | permissionless; control + asset; theft claim source-refuted (note) |
| ZETA-02 | **H5_STYLE_PARTIAL** | no L3 record (2/8 depth): reachability + loss_type only; PoC/impact unknown |
| ZETA-09 | **H5_STYLE_PARTIAL** | rejected/by-design; no L3 record; reachability + loss_type only |
| ZETA-12 | **H5_STYLE_PARTIAL** | no L3 record; reachability + loss_type only |

## Summary
- **9 READY-for-analysis · 3 PARTIAL** (the 3 PARTIAL are the candidates with no L3 record — ZETA-02/09/12 — where
  PoC/impact fields are honestly unknown). None BLOCKED_BY_MISSING_ARTIFACTS (every card has the structural slots +
  evidence_backup); none FAILED_VISIBILITY/SAFETY.
- Phase decision: **H5_STYLE_DASHBOARD_PARITY_READY** — all 12 carry H5-style slots; the focus candidates
  (ZETA-04/07/11) are analyzable; remaining gaps are explicit and artifact-justified (build a harness / no L3 record /
  no novelty artifact), never invented.
