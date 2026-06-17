# P201 — integrity checks

## Production hashes byte-identical START == END (md5 first-8)
| artifact | START | END | ok |
|---|---|---|---|
| `prompts/deep_trace.md` | ef93a6c2 | ef93a6c2 | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | 5d2a97f9 | 5d2a97f9 | ✓ |
| `scripts/eval_locus_resolver.py` | 3b0b2c02 | 3b0b2c02 | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | e23c5bc9 | e23c5bc9 | ✓ |
| `scripts/validate_p200.py` (reused template) | d1c41876 | (read-only) | ✓ |

No production prompt/checker/router/ledger/detector/dashboard edit. The refined gate is applied **offline/read-only**
in `scripts/validate_p201.py` (`EVAL_HARNESS_ONLY=True`, `ROUTES_IN_PRODUCTION=False`) and **not** implemented in
production. No canonical-label change; no submit/route/promote/demote.

## Double freeze (both before answer-key read)
- FREEZE 1 — blind threat-ceiling raw outputs (concat md5 first-8): **`77d57371`** (stable on re-hash).
- FREEZE 2 — refined mechanism-level calibration `OFFLINE_REFINED_CALIBRATION.json`: **`387a95de`** (deterministic
  re-run reproduces it).
- zetachain `report.md` opened in full only at scoring (Step 7), after both freezes. Count-only viability at Step 4.

## Blind firewall
- 18 frozen prompts = `deep_trace.md` (ef93a6c2) + verbatim source; pre-run leak-scan **CLEAN**.
- 18 raw outputs verbatim; leak-scan **CLEAN** (no finding-ID/issue-link cited by any agent).
- Refined calibration (RUBRIC_GRADES) authored from each frozen output's own evidence, **answer-key-blind**
  (orchestrator had only counts 14H/34M, never finding bodies). Scorer answer-aware only post-freeze; no backfill.
- Blind model: Sonnet (same-vendor caveat). `fabrication_rate = 0`.

## Seal / corpus / symlink
- `zetachain-2023-10-holdout/_sealed_answer_key/` opened read-only; files intact (`README.md data report.md`); no
  source/corpus mutation.
- `output -> audits/quantamm-2024-12-eval/output` symlink unchanged.
- All P201 JSON valid.

## Mechanism-level scoring attested
Scoring uses **per-mechanism** labels (46 mechanisms), not only surface labels; secondary-mechanism preservation
machinery exercised on all 18 surfaces. Oracle class B explicitly carried as UNVALIDATED_OUT_OF_SAMPLE.

## Deliverables
14 docs (`P201_PLAN`, `INTEGRITY_PRECHECK`, `P200_FAILURE_EXTRACTION`, `REFINED_SEVERITY_GATE_DESIGN`,
`CONTROLLED_UNSEAL`, `CORPUS_VIABILITY`, `COVERAGE_MANIFEST`, `BLIND_THREAT_CEILING_RESULTS` [in calibration+results],
`OFFLINE_REFINED_CALIBRATION.json`, `ORIGINAL_VS_REFINED_CALIBRATED`, `FAILURE_CASES`, `P201_RECOMMENDATION`,
`metrics.json`, `integrity_checks.md`) + 18 `blind_prompts/` + 18 `raw_outputs/` + read-only harness
`scripts/validate_p201.py`.
