# P180 integrity checks (production change #4)

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| **routing logic** `scripts/dependency_clear_utils.py` | NOT edited in P180 (`f15886103…`) — routing semantics unchanged |
| zaros `coverage_dispositions.json` | unchanged (`5f76e9fc…`) — validation read-only |
| P179 `metrics.json` (pre-patch record) | unchanged (`6757fe87…`) — not overwritten |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Guardrail grep (expected zero) — PASS
No `"severity"` / `routing_allowed` / `submission_ready` / `"status":"finding"` / `SWP-` writes in
`dependency_metadata.py`. The patch only adds suppression (stoplist + boilerplate/survey skip) → the extractor
is strictly MORE advisory. `coverage_sweep_write.py` / `deep_pass_write.py` wiring untouched; routing
(`classify_clear` / `dependency_route_decision`) untouched.

## Validation result
zaros structured blocks 83 → 0; `loadLive` concentration gone; `_guardQuantAMMWeights`/`ensureNoNavOps` still
resolve; explicit `clear_depends_on` honored; generic prose advisory. `validate_p180.py` sole write =
`before_after.json` in this dir.

## Tests
`tests/coverage/test_dependency_metadata.py` 18 (+6 P180); dependency suite 46 pass; full `tests/coverage`
**177 passed, 0 failed**. `fabrication_rate=0`.
