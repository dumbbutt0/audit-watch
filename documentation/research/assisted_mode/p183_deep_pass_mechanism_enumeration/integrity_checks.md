# P183 integrity checks (production change #5 — prompt + advisory checker)

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| routing `scripts/dependency_clear_utils.py` | byte-identical `f15886103…` (untouched) |
| `scripts/deep_analysis_write.py` / `scripts/deep_pass_write.py` | byte-identical (untouched in P183) |
| quantamm `normalized_answer_key.json` / `coverage_dispositions.json` | unchanged (`2e9dee7f…` / `a17f1ac7…`) |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Guardrail grep (expected zero) — PASS
No `"severity"` / `routing_allowed` / `submission_ready` / `"status":"finding"` / `SWP-` writes in
`scripts/validate_deep_pass_mechanisms.py`. The checker is ADVISORY (returns 0 always; writes only an advisory
report `output/deep_pass_mechanism_validation.{json,md}`). The `prompts/deep_trace.md` change is additive (STEP 0
+ stop-condition + extended schema; existing STEP 1–5 preserved) → recall-safe, no routing/severity/submission
behavior change. The writer was NOT edited (decision per plan: standalone validator suffices; no write-path risk).

## Tests
- `tests/deep_solidity/test_deep_pass_mechanism_checker.py` 5/5 (flags single-mechanism, passes enumerated,
  flags short inventory / missing who-loses-gains, never raises).
- `tests/deep_solidity`: **114 passed, 2 failed.** The 2 failures are PRE-EXISTING frozen-snapshot drift
  (`test_panoptic_miss_class_replay` / `test_recall_miss_class_replay` — drifted files `cross_artifact_lifecycle_audit.*`
  / `recipient_custody_audit.*` dated **2026-06-01**, produced by lenses that import no deep_trace/P183 code).
  Unrelated to P183 (confirmed in P177/P178 likewise).

## Honesty
`fabrication_rate=0`. The offline validation proves enumerability (9/9) + stop-condition coverage (9/9) +
checker correctness — NOT mechanism selection. Recall recovery is explicitly NOT claimed; it is a monitored
in-session follow-up. `validate_p183.py` sole write = `mechanism_trace.json` in this dir.
