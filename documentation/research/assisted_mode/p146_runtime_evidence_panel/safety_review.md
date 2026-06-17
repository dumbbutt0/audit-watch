# P146 — Safety Review

## Requirements 6 & 7 + research invariants — all honored
- **Prompt metrics value-for-value unchanged.** ✓ (`per_arch`/`totals`/`runs` computed solely from the queues;
  panel derives only from corpus + sidecar; integrity test asserts identical with empty vs full sidecar; live
  `totals` reproduce the P142 baseline.)
- **runtime_status / runtime_confidence vocab enforced.** ✓ (allowed sets; out-of-vocab coerced.)
- **Backfill only B1, B5; all others not_run.** ✓ (2 runtime_confirmed / 9 not_run.)
- **routing_allowed false for every row.** ✓ (forced regardless of sidecar; integrity flag True; test feeds
  true→forced false.)
- **submission_ready false for every row.** ✓ (forced.)
- **No production source changed.** ✓ (4 research-only files; nothing under run_pipeline.sh / agent_policy.json /
  production scripts / audit contracts.)
- **Panel supplemental only.** ✓ (additive `runtime_panel` key + standalone file; does not route/submit/confirm
  or set severity.)
- **Harness un-wired.** ✓ (grep-clean of run_pipeline.sh + agent_policy.json.)
- **Four research flags on every output.** ✓ (panel envelope + scorecard carry is_gate:false / research_only:true
  / routes_in_production:false / routed_manifest_ids:[] / routing_allowed:false.)

## Separation of evidence classes
Prompt-derived (per_arch/totals/runs) and runtime-confirmed (runtime_panel) are reported side-by-side but never
merged: a `runtime_confirmed` row contributes nothing to finding/recall/clean-FP counts. B1/B5 remain
`duplicate_known` and `submission_ready=false`; runtime confirmation strengthens advisory evidence only — human
review + scope/duplicate/severity stay separate gates.

## Integrity / state
Full pytest unaffected except the +6 new tests (1657 passed / 2 pre-existing snapshot fails / 4 skipped); active
`output/` symlink unchanged (`quantamm-2024-12-eval`); no audit switched; writes confined to `data/research/` +
`output_research/` + the test file.
