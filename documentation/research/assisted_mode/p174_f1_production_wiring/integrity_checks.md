# P174 integrity checks (first production change — F1 only)

| Artifact | Result |
|---|---|
| research campaign ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` (un-promoted) |
| guarded-downstream `dependency_clear_utils.py` | unchanged (confirmed already enforced) |
| math-estimator lens/validator/config | unchanged (confirmed already enforced) |
| 3 firewall seals | intact |
| active `output` symlink | unchanged |

## Production changes (intended, F1 only)
- New: `config/dynamic_weight_lifecycle_patterns.json`, `scripts/dynamic_weight_lifecycle_taxonomy.py`,
  `scripts/validate_dynamic_weight_lifecycle_clears.py`, `scripts/dynamic_weight_lifecycle_audit.py`,
  `tests/coverage/test_dynamic_weight_lifecycle.py`.
- Edit: `scripts/coverage_sweep_write.py` (additive F1 block + `lc_sensitive` in `already_specialized` +
  imports/policy reads), `scripts/update_coverage_disposition.py` (+`dynamic_weight_lifecycle_proof` param),
  `config/agent_policy.json` (4 flags).

## Guardrail (post-implementation grep) — expected ZERO, actual ZERO
No write to `severity` / `routing_allowed` / `submission_ready` / `"status":"finding"` / `SWP-` /
`findings_coverage` / `runtime_status.jsonl` (sidecar) in any new F1 module or the F1 sweep block. F1 only emits
`apply_update("assigned", assigned_pass="deep", assigned_agent="dynamic_weight_lifecycle_review")`.

## Tests
F1 suite 12/12; full coverage + research suites green (see run). `fabrication_rate=0` and reject-first invariants
untouched. F1 self-scopes (0 off-family).
