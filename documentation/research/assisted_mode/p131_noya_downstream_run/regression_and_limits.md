# P131 — Regression & Limits

## Regression checks
- **Precision loop unchanged:** `compute_metrics` FP 0.143 / over-severity 0.267 invariant (reads ground
  truth, not the manifest).
- **Deterministic A/B:** OFF and ON manifests differ only on the 70 boosted functions; ON reproducible (P130
  already verified identical scores on re-run).
- **No production code changed in P131:** `build_coverage_manifest.py` / tests untouched since P130;
  `config/agent_policy.json` was toggled OFF→ON and **restored** to its committed value (`library_internal_
  surface_boost: true`, cap 3).
- **Integrity:** `rank_signal_probe --self-test` OK; full `pytest -q` = **1572 passed / 2 pre-existing
  snapshot fails / 4 skipped** (unchanged). Active audit restored to `quantamm-2024-12-eval`.

## Volume / cost
- noya deep-pass volume +44% (158→228 fns). ~79% productive (recall + on-class value logic), ~21% trimmable
  noise. Tool runtime unchanged; the cost is reviewer/specialist time on the larger deep-pass set.

## Limits (what this phase does and does not establish)
1. **Not a full pipeline run.** slither/static degraded (no build env); no 13-specialist sweep over 377 fns;
   no human-graded outcomes. Established by design — see `run_setup.md`.
2. **Recall = deep-pass visibility + source-grounded discoverability**, not confirmed automated findings. The
   +8 awarded functions are made reviewable and are substantively reviewable; conversion to confirmed findings
   needs a human-graded specialist run.
3. **FP = estimate.** Non-awarded confirmed-looking leads are routed to needs_human_review, never auto-labeled.
   The "no speculative-FP inflation" conclusion is mechanism-based (boost re-ranks read logic; adds no new
   state-mutating paths) + sample-grounded, not a measured FP rate.
4. **Residual uncovered awarded functions** (`SNXConnector._getPositionTVL` absent; `updateTVL` untagged) are
   outside the ranking lever — enumeration/scope/reachability work for a later phase.
