# P188 integrity checks (production change — advisory detectors + prompt rules)

Hashes are md5sum first-8 (convention since P176). Two production files **change by design**; everything else is
byte-identical.

## Intended changes
| Artifact | Before | After |
|---|---|---|
| `prompts/deep_trace.md` | `dc7928f2` | `ef93a6c2` (Parts C/D + `claimed_locus`/`status` schema) |
| `scripts/validate_deep_pass_mechanisms.py` | `1cddd73f` | `5d2a97f9` (Parts A/B advisory detectors, additive) |

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| research F2 `scripts/research/recall_selectors.py` | `0c77332e` |
| routing `scripts/dependency_clear_utils.py` | `f1588610` |
| quantamm `normalized_answer_key.json` (eval) | `2e9dee7f` |
| research module `scripts/research/adjudication_rubric.py` (P187) | unchanged — **not imported, not edited** |
| P186 frozen `raw_outputs/*.json` | `3a37b556 / c4e979f7 / 43060330 / 86c8993f / 7015fead` |
| P186 `metrics.json` | `eacfdbde` |
| firewall seals (`_sealed_answer_key/_FIREWALL_SEAL.txt`) | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval`) |

## Advisory / non-blocking discipline
- The checker never writes `severity` / `submission` / `routing_allowed` / `submission_ready` / `"status":"finding"`
  (grep: only descriptive comments mention severity/submission). `main()` returns 0 unconditionally.
- New detectors run only on `rejected_mechanisms`; carried (`selected`/`unresolved`) mechanisms are never flagged;
  **no mechanism is ever upgraded to a finding.**
- The research module stays **un-wired**: `grep "adjudication_rubric" scripts/validate_deep_pass_mechanisms.py`
  finds only a comment noting it is NOT imported.

## Scope honored
No change to coverage sweep, routing, dependency system, F1/F2/F3, severity assignment, submission readiness,
answer keys, corpora, or the frozen P184/P186 traces. `scripts/validate_p188.py` is read-only (in-memory copies).

## Tests
`tests/deep_solidity/test_adjudication_support.py` 10 passed; `test_deep_pass_mechanism_checker.py` 8 passed; full
`tests/deep_solidity` = 127 passed / 2 failed = the **pre-existing** frozen-snapshot drifts
(`cross_artifact_lifecycle*`, `recipient_custody*`) unrelated to P188. `fabrication_rate=0`.
