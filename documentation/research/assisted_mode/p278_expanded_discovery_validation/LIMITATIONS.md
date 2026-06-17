# P278 — LIMITATIONS

- **Corpus-wide READY ≈ 0 by construction.** Auto-extracted evidence is incomplete because the harness leaves the
  exploitability fields as `operator-to-derive`; READY_FOR_POC_INTENT corpus-wide is 0. The 2 READY are hand-authored
  samples proving reachability, not auto-produced. So "READY count increases" holds only via the hand sample +
  the demonstrated path, not via automation yet (that is repair R-A).
- **Budget saturates at 8.** handoff budget 10 = budget 8 on this corpus (avg handoff 7.0); the +11.8pp is real but
  capped by how many candidates each contest surfaces. `missed` (31.9%) is recall-bound and untouched by any budget.
- **Hand-sample packages are validation hypotheses**, not confirmed findings — source-grounded but unproven at runtime
  (poc_feasibility_tier=partial_runtime; refutation noted-not-run). Labeled SUPERVISED_EVAL.
- **Auto-built upstream inputs are heuristic** (class signals from name+body tokens; triage impact dims from a fixed
  map) — coarser than hand-authored; documented since P276.
- **Supervised, not blind.** All numbers are calibration on the P276 corpus; generalization is measured only by a
  fresh blind target.
- Anti-monoculture 40% fails on the smallest queue (quantamm, 4 candidates) — a small-queue artifact (R-D).
