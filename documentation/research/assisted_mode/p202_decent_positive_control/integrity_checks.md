# P202 — integrity checks

## Production hashes byte-identical START == END (md5 first-8)
| artifact | START | END | ok |
|---|---|---|---|
| `prompts/deep_trace.md` | ef93a6c2 | ef93a6c2 | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | 5d2a97f9 | 5d2a97f9 | ✓ |
| `scripts/eval_locus_resolver.py` | 3b0b2c02 | 3b0b2c02 | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | e23c5bc9 | e23c5bc9 | ✓ |
| `scripts/validate_decent_pc.py` (new harness, read-only) | b1f62452 (build) | recorded | n/a |

No production prompt/checker/router/ledger/detector/severity edit; no `deep_trace.md` patch; gate **not** wired;
no submit/route/promote/demote. The refined gate was applied **offline** by a fresh firewall subagent.

## Double freeze (both before full answer-key read)
- FREEZE 1 — blind raw outputs (concat md5 first-8): **`54abf9ca`** (stable).
- FREEZE 2 — refined calibration `OFFLINE_REFINED_CALIBRATION.json`: **`90cf2a4f`**, `calibrated_by:
  fresh_firewall_subagent`.
- decent `report.md` opened in full only at scoring (Step 6), after both freezes.

## Contamination mitigation (executed)
- Orchestrator was PCS-contaminated (transient exposure to decent High hints). Mitigation honored: the gate
  calibration was authored by a **fresh cold-start firewall subagent** that received only the frozen raw outputs +
  the generic refined rubric + schema, was forbidden from reading `_sealed_answer_key/`, `positive_control_screening/`,
  any `report.md`, or memory. → result is a **valid out-of-sample validation**, not CONTAMINATED_UPPER_BOUND.
- Orchestrator performed only source-only sampling (broad, 11 categories) and post-freeze scoring (answer-aware by
  definition). Calibration JSON leak-scan: no answer-key tokens.

## Blind firewall
- 14 blind prompts = `deep_trace.md` (ef93a6c2) + verbatim source; prompts + raw outputs leak-scan CLEAN. Sonnet.
  `fabrication_rate=0`. Scorer answer-aware only post-freeze; no backfill.

## Seal / symlink
- `decent-2024-01-holdout/_sealed_answer_key/report.md` opened read-only; intact. Symlink
  `output -> audits/quantamm-2024-12-eval/output` unchanged. All P202 JSON valid.

## Decision
`REFINED_GATE_PARTIAL` — High-confirmation validated (H-01 confirmed; 0 genuine Highs demoted); Medium-demotion
regressed (M-03 receiveFromBridge over-confirmed High ×3 + unawarded false-Highs); root cause = gate inherits blind
layer's magnitude over-claim.

## Deliverables
`P202_DECENT_POSITIVE_CONTROL_PLAN.md` · `INTEGRITY_PRECHECK.md` · `CONTAMINATION_MITIGATION.md` ·
`CORPUS_VIABILITY.md` · `COVERAGE_MANIFEST.md` · `BLIND_THREAT_CEILING_RESULTS.md` ·
`FIREWALL_CALIBRATION_PROTOCOL.md` · `OFFLINE_REFINED_CALIBRATION.json` · `ORIGINAL_VS_REFINED_CALIBRATED.md` ·
`HIGH_PRESERVATION_SCORECARD.md` · `MEDIUM_DEMOTION_SCORECARD.md` · `FAILURE_CASES.md` · `P202_RECOMMENDATION.md` ·
`metrics.json` · `integrity_checks.md` + `blind_prompts/`×14 + `raw_outputs/`×14 + `scripts/validate_decent_pc.py`.
