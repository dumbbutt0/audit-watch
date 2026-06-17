# P176 integrity checks (read-only measurement phase)

| Artifact | Result |
|---|---|
| research campaign ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` (un-promoted) |
| runtime sidecar `…/value_provenance_eval/runtime_status.jsonl` | byte-identical `491da8c1…` |
| frozen corpus `documentation/evals/judge_corpus/frozen_corpus.json` | byte-identical `60089ff5…` |
| P175 `family_scoring.json` (read-only input) | unchanged (`4fa46d37…`) |
| zaros / revert-lend `coverage_dispositions.json` + `coverage_manifest.json` | read-only inputs; unchanged |
| eval match matrices | read-only inputs; unchanged |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Write-scope (expected: only the p176 doc dir)
`routing_recovery.py` has exactly one write: `(HERE / "recovery_by_finding.json").write_text(...)`. It calls
**no** `apply_update`, no `coverage_sweep_write.py`, and writes to **no** disposition/manifest/answer-key/match-
matrix/production file. The production predicates (`dependency_clear_utils`, `math_estimator_taxonomy`,
`validate_math_estimator_clears`, `dynamic_weight_lifecycle_taxonomy`, `validate_dynamic_weight_lifecycle_clears`)
are imported and called read-only. So the corpora are unchanged by construction.

## Reconciliation (self-checked by the harness, asserts pass)
- per corpus: `recovered + recovered_blunt_resurface + discovery_gap + unrecoverable_missing_evidence +
  unmappable == target_findings` (zaros 27, revert-lend 12). The buckets partition the target set.
- population: `routed = guarded(blunt|genuine) + math_estimator + f1_lifecycle + strong_clear_gate` (first-match
  order); recovered items ⊆ routed.

## Honesty notes
- The blunt vs precise split is the central honesty control: a `missing_dependency_metadata` route fired by
  incidental prose is reported as `recovered_blunt_resurface`, never as precise recovery.
- Unmappable findings (titles naming struct/field/spelling-variant, not a resolvable function) are reported as
  `unmappable`, never guessed as recovered/failed. Fuzzy matching deliberately avoided.
- `fabrication_rate=0` preserved; reject-first untouched.
