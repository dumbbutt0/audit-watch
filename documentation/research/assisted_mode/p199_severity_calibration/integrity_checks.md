# P199 integrity checks (read-only severity-calibration study)

md5sum first-8, START == END (byte-identical):
| artifact | hash |
|---|---|
| prompts/deep_trace.md | ef93a6c2 |
| scripts/validate_deep_pass_mechanisms.py | 5d2a97f9 |
| scripts/eval_locus_resolver.py | 3b0b2c02 |
| output_research/option_a_campaign/ledger.jsonl | e23c5bc9 |
| active output symlink | audits/quantamm-2024-12-eval/output (unchanged) |

- Read-only: no production prompt/checker/router/detector/severity edits; no severity labels changed in canonical
  artifacts; no promote/demote/route/submit; deep_trace.md NOT patched. The severity gate is a DESIGN NOTE ONLY.
- Dataset built from existing P186/P189/P198 artifacts + answer-key-id severity prefixes; no model runs.
- Every dataset row + over-HIGH classification cites its artifact (raw_output verdict, scoring table, id prefix).
  Unknowns kept UNKNOWN. Over-HIGH measured before any fix proposed. fabrication_rate=0. All P199 JSON valid.
- Sealed answer keys untouched; P186-P198 deliverables unchanged.

Deliverables: P199_PLAN.md, INTEGRITY_PRECHECK.md, CALIBRATION_DATASET.json, CALIBRATION_SCORECARD.md,
OVER_HIGH_CASES.md, FAILURE_TAXONOMY.md, HIGH_VS_MEDIUM_DISCRIMINATORS.md, SEVERITY_GATE_PROPOSAL.md,
P199_RECOMMENDATION.md, metrics.json, integrity_checks.md + scripts/validate_p199.py.
