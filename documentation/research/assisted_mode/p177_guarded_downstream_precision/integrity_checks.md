# P177 integrity checks (production change #2)

| Artifact | Result |
|---|---|
| research campaign ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` (un-promoted) |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| zaros / revert-lend `coverage_dispositions.json` | unchanged (`5f76e9fc…` / `8a6bbefe…`) — replay is read-only |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Guardrail grep (expected: zero new severity/routing/submission/finding writes) — PASS
No `"severity"` / `routing_allowed` / `submission_ready` / `"status":"finding"` / `SWP-` writes in
`dependency_clear_utils.py` or `update_coverage_disposition.py`. The sweep/deep_pass routing action is unchanged
(`apply_update("assigned", assigned_pass="deep", …)` — re-surface only); P177 only changed the block/advisory/
allow *decision* + added additive capture fields.

## Production changes (intended)
- Edit: `scripts/dependency_clear_utils.py`, `scripts/coverage_sweep_write.py`, `scripts/deep_pass_write.py`,
  `scripts/validate_dependency_clears.py`, `scripts/update_coverage_disposition.py`, `config/agent_policy.json`.
- Tests: `tests/coverage/test_dependency_clear_validation.py` (updated to the new advisory semantics + new
  block/allow/flag-off/capture-field tests).
- New (read-only docs): `documentation/research/assisted_mode/p177_guarded_downstream_precision/`
  (`CHANGES.md`, `validate_p177.py`, `before_after.json`, `integrity_checks.md`).

## Tests
- `tests/coverage/test_dependency_clear_validation.py` + `test_dependency_locality.py`: 31 → all pass.
- Full `tests/coverage tests/research tests/deep_solidity tests/defi_accounting tests/investigation`:
  **539 passed, 2 failed**. The 2 failures are PRE-EXISTING frozen-snapshot drift
  (`test_panoptic_miss_class_replay::test_frozen_snapshot_unchanged`,
  `test_recall_miss_class_replay::test_frozen_recall_snapshot_unchanged`) — the drifted files
  (`cross_artifact_lifecycle_audit.*`, `recipient_custody_audit.*`) are dated **2026-06-01** (4 days before this
  session) and are produced by lenses that import NO P177-touched code. **Unrelated to P177.**

## Honesty notes
- The replay's `before` uses `require_structured=False` (legacy) and `after` uses the new default, both via the
  production `dcu.dependency_route_decision` — so the before/after delta is the genuine effect of this change.
- Re-surfacing ≠ confirmation: routing only sends a clear to deep-pass; it never confirms a bug.
- `fabrication_rate=0` preserved.
