# P178 integrity checks (production change #3)

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| zaros / revert-lend `coverage_dispositions.json` | unchanged (`5f76e9fc…` / `8a6bbefe…`) — measurement read-only |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Guardrail grep (expected zero) — PASS
No `"severity"` / `routing_allowed` / `submission_ready` / `"status":"finding"` / `SWP-` writes in
`dependency_metadata.py` or `validate_dependency_metadata.py`. **`dependency_clear_utils.py` (the
`classify_clear` / `dependency_route_decision` routing logic) was NOT edited in P178** — routing semantics
unchanged; P178 only feeds resolved facts upstream. `measure_capture.py` sole write = `capture_coverage.json`.

## Tests
- `tests/coverage/test_dependency_metadata.py` (new, 12) + `test_dependency_clear_validation.py` +
  `test_dependency_locality.py`: 40 pass.
- Full `tests/coverage tests/research`: **284 passed, 0 failed.** (The 2 pre-existing frozen-snapshot drifts
  from P177 live in `tests/deep_solidity` — dated 2026-06-01, produced by lenses importing no P178/P177 code —
  out of scope here.)

## Honesty notes
- Auto-extraction runs on COPIES of dispositions in the measurement (`dict(d)`); the corpora are never written.
- The >80% / structured>prose success bar is for prompt-driven future clears; legacy-corpus coverage (35%/0%)
  is reported as the deterministic floor, not asserted as success. (Accepted limitation.)
- `fabrication_rate=0`: `dependency_evidence` is a real manifest source span; routing only re-surfaces for
  review (never mints a finding / sets severity).
