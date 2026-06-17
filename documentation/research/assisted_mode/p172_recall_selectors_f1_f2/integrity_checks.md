# P172 integrity checks (research-only; production untouched)

| Artifact | Baseline | Post-P172 | Result |
|---|---|---|---|
| campaign ledger (`head -20`) | `e23c5bc9…` | `e23c5bc9…` | **byte-identical** (no ledger write) |
| runtime sidecar | `491da8c1…` | `491da8c1…` | **byte-identical** |
| frozen corpus | `60089ff5…` | `60089ff5…` | **byte-identical** |
| quantamm `match_matrix.json` + answer keys | (P171) | unchanged | **read-only** |
| production detectors `scripts/*_audit.py` | — | unchanged | **none touched** |
| coverage-sweep / clear policy `scripts/coverage_sweep*`, `dependency_clear_utils.py` | — | unchanged | **none touched** |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- New files only: `scripts/research/recall_selectors.py`, `tests/research/test_recall_selectors.py`, this P172
  doc dir. All selector outputs carry `research_only:true / routes_in_production:false / is_gate:false`.
- Un-wired: `grep recall_selectors run_pipeline.sh config/agent_policy.json` → empty (asserted in test).
- `sandbox_check.py` CLEAN before reading quantamm source. 3 firewall seals intact (not opened).
- No routing / severity / submission / detector / coverage-sweep / prompt / corpus / sidecar / answer-key change.
- Promotion of F1/F2 into production lenses = separate human decision (not performed).
