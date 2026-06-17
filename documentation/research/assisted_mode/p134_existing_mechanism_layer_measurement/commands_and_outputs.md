# P134 — Commands & Outputs

Active audit switched to noya for the runs, restored to `quantamm-2024-12-eval` after. Full console in
`runtime_output.txt`.

```
python scripts/audit_manager.py switch noya-2024-04-eval
python scripts/connector_position_accounting_audit.py   # → output/connector_position_accounting_audit.json
python scripts/units_invariant_audit.py                 # → output/units_invariant_audit.json
python scripts/arithmetic_conservation_audit.py         # → output/arithmetic_conservation_audit.json
python scripts/semantic_tvl_completeness_audit.py       # → output/semantic_tvl_completeness_audit.json
python scripts/registry_position_lifecycle_audit.py     # → output/registry_position_lifecycle_audit.json
python scripts/audit_manager.py switch quantamm-2024-12-eval   # restore
```

| Detector | Exit | Slither/import block? | Source parsing | Candidates (total) | on-target(8) / off-target |
|---|---|---|---|---|---|
| connector_position_accounting | 0 (pass) | none | read-time source | 7 | 3 / 4 |
| arithmetic_conservation | 0 (pass) | none | read-time source | 9 | 4 / 5 |
| units_invariant | 0 (pass) | none | read-time snippets | 45 (10 high-risk) | 6 / 39 |
| semantic_tvl_completeness | 0 (pass) | none | read-time source | 11 | 4 / 7 |
| registry_position_lifecycle | 0 (pass) | none | read-time source | 3 | 0 / 3 (incl. H-18/H-23 bonus) |

**No detector was BLOCKED.** All ran read-time on the committed noya `coverage_manifest.json`; none invoked
Slither or needed noya to compile. Runtime: each completed in seconds (see `runtime_output.txt`). Outputs are
audit-local under `audits/noya-2024-04-eval/output/`.
