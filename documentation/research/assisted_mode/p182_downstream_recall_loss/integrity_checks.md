# P182 integrity checks (read-only analysis)

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| routing `scripts/dependency_clear_utils.py` | byte-identical `f15886103…` |
| quantamm `coverage_dispositions.json` | unchanged (`a17f1ac7…`) — read-only |
| quantamm `normalized_answer_key.json` | unchanged (`2e9dee7f…`) — read-only |
| quantamm `match_matrix.json` | unchanged (`8bcfda11…`, == P171-recorded hash) |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Write-scope / guardrails
`trace_recall_loss.py` sole write = `loss_trace.json` in this dir. No production code/config/routing/severity/
submission/selector/taxonomy/dashboard/answer-key/corpus/disposition change. JSON validates (44 rows).
`fabrication_rate=0` — every loss-point is anchored to an on-disk artifact; `L-09` reported `unmappable`
(`affected="rules/*"`), never guessed.

## Self-checks (assert in harness, pass)
- 44 rows; recommendation buckets partition the 44 (8 + 12 + 18 + 5 + 1).
- `REPORTABLE_OR_HIT` (8) == match_matrix HIT+PARTIAL+ADJACENT.
- resolution levels reported (function 24 / contract 19 / unresolved 1); contract-level DEEP_RUN attributions
  flagged lower-confidence in LOSS_TRACE.md.

## Honesty notes
- `already_addressed_by_shipped_gates` re-runs the shipped classifiers on the recorded disposition → proves
  re-route-to-deep-pass, not bug confirmation (re-surfacing ≠ confirmation).
- Contract-level resolutions (19/44) are coarse ("covered" = a finding in the same contract, not the exact fn).
