# P200 — integrity checks

## Production hashes byte-identical START == END (md5 first-8)
| artifact | START | END | ok |
|---|---|---|---|
| `prompts/deep_trace.md` | ef93a6c2 | ef93a6c2 | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | 5d2a97f9 | 5d2a97f9 | ✓ |
| `scripts/eval_locus_resolver.py` | 3b0b2c02 | 3b0b2c02 | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | e23c5bc9 | e23c5bc9 | ✓ |

No production prompt/checker/router/ledger/detector/severity edit. The P199 gate was applied **offline/read-only**
(in `scripts/validate_p200.py`, `EVAL_HARNESS_ONLY=True`, `ROUTES_IN_PRODUCTION=False`) and **not** implemented in
production.

## Double freeze (both before answer-key read)
- FREEZE 1 — blind threat-ceiling raw outputs (concat md5 first-8): **`4aede343`** (stable on re-hash).
- FREEZE 2 — offline severity calibration `OFFLINE_SEVERITY_CALIBRATION.json` (md5 first-8): **`1e158f1e`**
  (deterministic re-run reproduces it).
- Answer key (`predy report.md`) opened in full only at scoring (Step 6), after both freezes.

## Blind firewall
- 16 frozen blind prompts = `deep_trace.md` (ef93a6c2) + verbatim source; pre-run leak-scan **CLEAN** (no
  `[H-/M-/C-/L-0`, no `code-423n4`, no `Risk Findings`/`Severity Criteria`).
- 16 raw outputs preserved verbatim; leak-scan **CLEAN** (no finding-ID/issue-link cited by any agent).
- Blind model: Sonnet (same-vendor caveat recorded). Scorer answer-aware only post-freeze; no backfill.
- `fabrication_rate = 0` — every artifact derives from a frozen output or the opened report; calibration grades
  cite each output's own evidence.

## Seal / corpus / symlink
- `predy-2024-05-holdout/_sealed_answer_key/` opened read-only; files intact (`README.md data report.md`); no
  source/corpus mutation. badger seal touched only for count-only viability (abandoned, not scored).
- `output -> audits/quantamm-2024-12-eval/output` symlink unchanged.
- All P200 JSON valid.

## Deliverables
13 docs (`P200_PLAN`, `INTEGRITY_PRECHECK`, `CONTROLLED_UNSEAL`, `CORPUS_VIABILITY`, `COVERAGE_MANIFEST`,
`BLIND_THREAT_CEILING_RESULTS`, `OFFLINE_SEVERITY_CALIBRATION.json`, `CALIBRATED_SCORECARD`, `ORIGINAL_VS_CALIBRATED`,
`FAILURE_CASES`, `P200_RECOMMENDATION`, `metrics.json`, `integrity_checks.md`) + 16 `blind_prompts/` + 16
`raw_outputs/` + read-only harness `scripts/validate_p200.py`.
