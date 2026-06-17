# P245 — Safety Report

Verifies every hard constraint from the build brief.

## Constraint checklist
| Constraint | Status | Evidence |
|---|---|---|
| Default-off | ✅ | `enforce_read_completeness:false`, `enforce_read_completeness_full_audit:false`, `rejection_depth_record_enforced:false` in `config/agent_policy.json`. Arm A (flag off) PASSES; 17 pre-existing coverage tests green. |
| No detector-family additions | ✅ | Only two pure *gate* utils + gate/triage wiring; no taxonomy/classifier/`*_audit.py` detector, no normalization/registry entry. |
| No severity-policy edits | ✅ | No change to severity scale, `decide()`, or any severity mapping. |
| No dashboard behavior edits | ✅ | `dashboard_sync.py` byte-identical; no dashboard file touched. |
| No routing/submission changes | ✅ | No routing tables; #4 only reroutes to the *existing* `human_review_queue.jsonl`; nothing auto-submits. |
| No prompt rewrites | ✅ | `find prompts -mmin` empty; `deep_trace.md` byte-identical. |
| No production source edits beyond the gate | ✅ | Changed files = exactly the 7 intended (5 edited + 2 new); see below. |
| No auto-promotion | ✅ | No `promote_learning`/registry writes. |
| No auto-submit | ✅ | #4 reroutes/preserves; never mints or submits a finding. |
| Forbidden file hashes preserved | ✅ | all 5 match baseline (below). |
| Active audit restored | ✅ | never switched (nextgen not in registry → `switch` refused); validation ran in a tmp workspace; `output` → `size-credit-2024-06-blind`. |
| Research/process-gate only until validated | ✅ | gate is default-off; this phase only validated it. |
| No broad schema migration | ✅ | `read_state` is an additive optional disposition field; no manifest/triage schema change; 6-state machine untouched. |

## Forbidden file hashes (baseline == post-build)
```
c1af70e1…  scripts/dashboard_sync.py
c095c426…  prompts/deep_trace.md
2a15169a…  scripts/min_confirm_gate.py
afc481c9…  scripts/confirm_gate.py
ae55eb80…  scripts/validate_p208_l3_readiness.py
```

## Files changed (exactly the intended set)
New: `scripts/read_completeness_utils.py`, `scripts/reasoning_depth_utils.py`.
Edited: `scripts/coverage_completeness_gate.py`, `scripts/init_coverage_dispositions.py`,
`scripts/update_coverage_disposition.py`, `scripts/triage_write.py`, `config/agent_policy.json`.
Tests/docs: `tests/coverage/test_read_completeness_gate.py`,
`tests/reasoning_depth/test_rejection_depth_record.py`,
`tests/research/test_p245_coverage_reasoning_gate_build.py`, this report dir.
Not edited: `run_pipeline.sh`, anything under `schemas/` or `prompts/`, the API `triage_findings.py` path.

## Stop-condition review (none triggered)
- broad schema migration needed → **no** (additive optional field only).
- gate over-blocks normal workflow → **no** (default-off; getters excluded; non-critical only warns).
- sensitive-area detection noisy → **no** (fires only on incomplete sensitive-area rejections; complete &
  non-sensitive pass through — validated).
- depth records busywork with no recall protection → **no** (`coverage_enforced_recall_gain` shows the
  blocked/rerouted work lands on real P241 misses, incl. the H-01 anchor).
- forbidden files changed → **no**.

→ Safe to leave merged in the **default-off** state. Turning either flag on for live hunting is a separate,
deliberate operator decision (the `enforce_read_completeness` / `rejection_depth_record_enforced` keys, or
the `--enforce-read-completeness` flag).

## Second validation (DittoETH diamond/facet) — safety re-confirmation
`VALIDATION_DITTOETH.md` was produced by a **validation-only** run (verdict A — GENERALIZES_TO_DIAMOND_FACETS).
No gate code was changed for it. Re-verified after that run:
- Forbidden file hashes unchanged (all 5 match the baseline above).
- No edits to `scripts/`, `config/`, `schemas/`, `prompts/`, `run_pipeline.sh` during the dittoeth run
  (validation executed in a tmp workspace via `get_audit_root` redirect — zero audit writes).
- Active audit still `size-credit-2024-06-blind` (never switched; dittoeth read in-place / tmp only).
- No stop-condition triggered (predicate generalized to facets with 0 false blocks on diamond infra; no
  schema/routing/dashboard change needed). Added deliverables only: `VALIDATION_DITTOETH.md` +
  `_validation_dittoeth_data.json` + `_triage_dittoeth_data.json`.
