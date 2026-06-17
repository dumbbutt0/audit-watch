# P203 — integrity checks

## Production hashes byte-identical START == END (md5 first-8)
| artifact | START | END | ok |
|---|---|---|---|
| `prompts/deep_trace.md` | ef93a6c2 | ef93a6c2 | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | 5d2a97f9 | 5d2a97f9 | ✓ |
| `scripts/eval_locus_resolver.py` | 3b0b2c02 | 3b0b2c02 | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | e23c5bc9 | e23c5bc9 | ✓ |

No production prompt/checker/router/ledger/detector/severity edit; no `deep_trace.md` patch; gate not wired; no
submit/route/promote/demote. Offline calibration experiment only.

## Frozen P202 artifacts reused unchanged (no rerun)
- P202 raw blind outputs FREEZE 1: `54abf9ca` (unchanged) — no blind agents rerun.
- P202 v1 calibration FREEZE 2: `90cf2a4f` (unchanged).
- decent in-scope source tree: `623aedd6` (unchanged).

## P203 freeze
- v2 regrade `V2_MECHANISM_REGRADING.json`: `e2100588`, `regraded_by: fresh_keyblind_firewall_subagent`.

## Backfit firewall (executed)
- v2 rule (`REFINED_GATE_V2_RULE.md`) written **before** application, general (no answer-key references).
- v2 regrade authored by a **fresh cold-start key-blind subagent** given only: the v2 rule (inline), the frozen
  raw outputs, the frozen v1 calibration (for keys), and decent source. Forbidden: `_sealed_answer_key/`, any
  `report.md`, P202 scoring docs, the P203 `V1_FAILURE_EXTRACTION.md` (orchestrator prediction frame),
  `positive_control_screening/`, memory, and the spec's expected-case outcomes. → regrade is key-blind; the
  orchestrator did only the post-regrade answer-aware scoring. Not INVALID_RUN.
- `V2_MECHANISM_REGRADING.json` leak-scan: no answer-key tokens.

## Symlink
`output -> audits/quantamm-2024-12-eval/output` — intact. All P203 JSON valid. `fabrication_rate=0`.

## Decision
`V2_GATE_FAILED_FALSE_HIGH` — H-01 retained High (0 false demotions), but M-03 (receiveFromBridge) still
HIGH_CONFIRMED and false-Highs unchanged. Root cause: the static source-substantiation precondition is gameable by
arbitrary-execution capability; the gap is worst-case-capability vs realized-impact → needs a PoC/harness magnitude
standard, not a static rule.

## Deliverables
`P203_PLAN.md` · `INTEGRITY_PRECHECK.md` · `REFINED_GATE_V2_RULE.md` · `V1_FAILURE_EXTRACTION.md` ·
`V2_MECHANISM_REGRADING.json` · `V1_VS_V2_SCORECARD.md` · `HIGH_PRECONDITION_AUDIT.md` · `FAILURE_CASES.md` ·
`P203_RECOMMENDATION.md` · `metrics.json` · `integrity_checks.md` + read-only `scripts/validate_p203.py`.
