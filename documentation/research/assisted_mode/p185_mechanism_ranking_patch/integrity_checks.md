# P185 integrity checks (production change #6 — prompt + advisory checker)

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| routing `scripts/dependency_clear_utils.py` | byte-identical `f15886103…` (untouched) |
| quantamm `normalized_answer_key.json` | unchanged (`2e9dee7f…`) |
| P184 deliverable `mechanism_selection_trace.json` | unchanged (`068a72a8…`) — not overwritten |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Guardrail grep (expected zero) — PASS
No `"severity"` / `routing_allowed` / `submission_ready` / `"status":"finding"` / `SWP-` writes in
`scripts/validate_deep_pass_mechanisms.py`. The checker stays ADVISORY (returns 0; writes only an advisory
report). The `prompts/deep_trace.md` change is additive + recall-safe (it only PRESERVES more mechanisms — it
cannot demote/drop). No selector/taxonomy/routing/severity/submission/answer-key/corpus/dashboard change.

## Tests
- `tests/deep_solidity/test_deep_pass_mechanism_checker.py`: 8/8 (existing + P185 list/prose-accept,
  demoted-unresolved-flag, clean-rejection-not-flagged).
- `tests/deep_solidity`: **117 passed, 2 failed.** The 2 failures are the PRE-EXISTING frozen-snapshot drifts
  (`test_panoptic_miss_class_replay` / `test_recall_miss_class_replay`; drifted files
  `cross_artifact_lifecycle_audit.*` / `recipient_custody_audit.*` dated 2026-06-01, produced by lenses that
  import no deep_trace/checker code). Unrelated to P185 (same as P177/P178/P183).

## Validation
`validate_p185.py` runs read-only (asserts pass): P184 checker-replay 5/5 complete + 2/5 demoted detected;
P185 re-run 2/2 complete, 0 demoted, avg_selected 2.5 (stable). Both p185 JSON deliverables validate.
`fabrication_rate=0`; raw blind outputs preserved verbatim; recall recovery NOT claimed (blind n=2).
