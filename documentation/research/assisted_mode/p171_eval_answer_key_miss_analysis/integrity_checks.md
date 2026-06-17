# P171 integrity checks (read-only analysis)

Analysis + documentation only. No code, detector, routing, severity, submission, corpus, sidecar,
ground_truth, or answer-key mutation. Firewall-sealed holdout keys were NOT opened.

| Artifact | Baseline | Post-P171 | Result |
|---|---|---|---|
| campaign ledger (`head -20`) | `e23c5bc9…` (20 rows) | `e23c5bc9…` (20) | **byte-identical** (no append this phase) |
| runtime sidecar | `491da8c1…` | `491da8c1…` | **byte-identical** |
| frozen corpus | `60089ff5…` | `60089ff5…` | **byte-identical** |
| quantamm `match_matrix.json` | `8bcfda11…` | `8bcfda11…` | **read-only, unchanged** |
| zaros `answer_key.md` | `1637d288…` | `1637d288…` | **read-only, unchanged** |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- Firewall-sealed keys (centrifuge/decent/pooltogether/predy/vultisig `_sealed_answer_key`, `_FIREWALL_SEAL.txt`)
  **not opened** — preserved for blind reuse; their candidates marked `not_analyzed`.
- `data/evaluation/ground_truth.jsonl` absent — nothing read or written there.
- HARD SEPARATION enforced: Track A (quantamm recall, 8/44) and Track B (campaign refutation-correctness, no %)
  are reported in separate tables and never summed.
- New files only, under the P171 doc dir: MISS_ANALYSIS.md, coverage_matrix.json (53 rows, valid JSON),
  taxonomy_gap_recommendations.md, integrity_checks.md.
