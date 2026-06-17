# P220 — Integrity checks (END)

`api_free=true`. Research-only; 0 route/submit/promote. No audit switch (hook uses `--audit` explicitly).

## Byte-identical START==END (verified)
### Target Zeta sources (copied into realsrc/, never modified)
| md5 | file | START==END |
|-----|------|-----------|
| 735fdaca | evm/ZetaConnector.non-eth.sol | ✓ |
| d288d2f4 | evm/tools/ZetaTokenConsumerTrident.strategy.sol | ✓ |
| 7dd5217e | evm/tools/ZetaTokenConsumerUniV3.strategy.sol | ✓ |
| b1168443 | zevm/ZRC20.sol | ✓ |

`realsrc/` copies confirmed `diff`-identical to the production files above (non-eth, base, Trident, UniV3).

### Pipeline scripts (not edited)
| md5 | file | START==END |
|-----|------|-----------|
| 87764e5e | scripts/sync_hunt_findings.py | ✓ |
| 78c41bf5 | scripts/finding_detail.py | ✓ |
| 26bd7ee0 | scripts/dashboard_sync.py | ✓ |
| 9e38136e | scripts/run_hunt_sync_hook.py | ✓ |
| 00cf5f56 | scripts/validate_hunt_sync_completion.py | ✓ |
| d9f09981 | scripts/funnel.py | ✓ |
| 5c6cccb5 | scripts/findings_overview.py | ✓ |
| 197ac4d5 | scripts/dashboard.py | ✓ |
| fe37e6ad | scripts/validate_p208_l3_readiness.py | ✓ |
| e4960878 | scripts/submission_readiness_review.py | ✓ |
| 04211964 | run_pipeline.sh | ✓ |

### Forbidden files (never touched)
| md5 | file | START==END |
|-----|------|-----------|
| ef93a6c2 | prompts/deep_trace.md | ✓ |
| 41dd3c96 | scripts/min_confirm_gate.py | ✓ |
| 4fadfc5f | scripts/confirm_gate.py | ✓ |
| bea43487 | config/runtime_policy.json | ✓ |

## Intended changes (data + new files)
| file | START → END |
|------|-------------|
| documentation/research/funnel/synced_findings.generated.json | c7166e71 → 33a42431 (only ZETA-04/10/11 records changed) |
| output_research/l3_readiness/ZETA-04.json | a551926d → rewritten (PASS, executed) |
| output_research/l3_readiness/ZETA-10.json | 4384320f → rewritten (FAIL, refuted) |
| output_research/l3_readiness/ZETA-11.json | 029cd55c → rewritten (PASS dos / wrong-mechanism) |
| output_research/funnel/sync_hook_metrics.json | 221c8ad2 → regenerated (completeness 90%, safety_ok, completion_ok) |
| pocs/p220/** | NEW (real source + vendor OZ/Uniswap + mocks + 3 harnesses + logs) |
| documentation/research/assisted_mode/p220_l3_harnesses/** | NEW (14 deliverables) |
| tests/research/test_p220_l3_harness_ingestion.py | NEW |
| tests/research/test_evidence_extraction.py | edited: stale ZETA-04 NEEDS_HARNESS assertion → ZETA-05 |

ZETA-07.json (64c9e4e6) unchanged. No fabricated evidence; every populated L3 field traces to a harness file + run log.
Mirror backups retained next to the mirror (reversible).
