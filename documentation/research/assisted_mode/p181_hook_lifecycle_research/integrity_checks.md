# P181 integrity checks (research-only, un-wired)

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` (untouched; new file added) |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| routing `scripts/dependency_clear_utils.py` | byte-identical `f15886103…` (untouched) |
| quantamm / zaros manifests | unchanged (`81b8d379…` / `ca2e69c6…`) — read-only |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Research-only / un-wired (CLAUDE.md Research Detector Platform)
`scripts/research/hook_lifecycle_selector.py` carries `_FLAGS = {research_only:True, routes_in_production:False,
is_gate:False, re_surface_only:True}`. Grep confirms it is imported by NOTHING in production (only the P181
validation harness references it); no `config/` or `run_pipeline.sh` reference. It never mints findings, sets
severity, routes, or mutates anything. `fabrication_rate=0`.

## Write-scope
`validate_hook_lifecycle.py` writes only `metrics.json` in this dir. No production code/config/routing/severity/
submission/answer-key/corpus/disposition change. No production wiring performed (per the P181 directive).

## Tests
`tests/research/test_hook_lifecycle_selector.py` 9/9 pass (research flags, true-positives on
`onAfterRemoveLiquidity`/`afterUpdate`, avoid-filter skips for view/pure/admin/callback/non-hook/no-state).
