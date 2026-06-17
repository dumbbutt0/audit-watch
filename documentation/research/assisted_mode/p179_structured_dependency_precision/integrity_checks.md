# P179 integrity checks (read-only measurement)

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| zaros `coverage_dispositions.json` / `coverage_manifest.json` / `eval_match_matrix.json` | unchanged (`5f76e9fc…` / `ca2e69c6…` / `56b0c155…`) |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Write-scope
`precision_harness.py` writes only `precision_by_block.json` + `metrics.json` in the p179 dir. No production
code, routing, selector, prompt, corpus, disposition, or answer-key change. The extractor runs on `dict()`
copies; dispositions are never written. `fabrication_rate=0`.

## Honesty notes
- exact-precision is computed by same-named-function match; it OVER-credits common names (performUpkeep/mint/
  create) → the reported 9.6% is an upper bound; genuine awarded-site precision ≈ 0.
- subsystem precision (~75–84%) is ≈ the base rate (12 subsystems / 29 contracts) → not informative; only the
  exact metric is meaningful.
- answer-key function resolution is partial (27/70 zaros findings resolve to a manifest function) — a known
  measurement limitation, flagged as recommendation (4) in the report.
