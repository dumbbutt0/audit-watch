# P166 integrity checks

| Artifact | Baseline | Post-P166 | Result |
|---|---|---|---|
| campaign ledger — existing 5 rows (`head -5`) | `c74ce773…` | `c74ce773…` | **byte-identical** (H10 appended as row 6; no rewrite/backfill) |
| campaign ledger row count | 5 | 6 | append-only +1 (H10) |
| prediction_log.jsonl | (absent) | 1 line | new append-only (H10 prediction) |
| runtime sidecar | `491da8c1…` | `491da8c1…` | **byte-identical** (H10 not_run → no sidecar row) |
| frozen corpus | `60089ff5…` | `60089ff5…` | **byte-identical** |
| readiness file | `ff8243c4…` | `ff8243c4…` | **byte-identical** |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- Part A (tooling) + Part B (protocol doc) are independent of the Part C (H10) run; H10 was recorded
  `SOURCE_REFUTED_NO_HARNESS` (no forced harness — per the independence guardrail).
- `sandbox_check.py` CLEAN before reading candidate source. No harness built → no PoC dir / Foundry lib.
- Campaign tool stays **un-wired**: `grep option_a_campaign|p166 run_pipeline.sh config/agent_policy.json` → empty.
- Production calibration/learning pipeline (`compute_metrics.py` / `derive_learning.py` / ground_truth)
  **untouched** — P166 lives entirely in the research-only Option-A track + read-only dashboard.
- No detector/taxonomy/routing/severity/submission-policy/prompt/corpus/sidecar-schema/production change.
  `submission_ready`/`routing_allowed` never set true; `fabrication_rate = 0/6`.
- Tests: see the suite run (`test_option_a_campaign` + `test_unified_candidate_detail` + `test_submission_readiness`).
