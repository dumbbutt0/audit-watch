# P220 — Integrity precheck (START)

`api_free=true` (config/runtime_policy.json). No live submit route. Active audit: zetachain-2023-10-holdout (the
sync hook takes `--audit` explicitly; no audit switch performed). Harnesses isolated under `pocs/p220/`.

## START md5 (first 8) — must be byte-identical at END
### Target Zeta sources (never modified; copied into realsrc/)
| md5 | file |
|-----|------|
| 735fdaca | evm/ZetaConnector.non-eth.sol |
| d288d2f4 | evm/tools/ZetaTokenConsumerTrident.strategy.sol |
| 7dd5217e | evm/tools/ZetaTokenConsumerUniV3.strategy.sol |
| b1168443 | zevm/ZRC20.sol |

### Pipeline scripts (not edited this phase)
| md5 | file |
|-----|------|
| 87764e5e | scripts/sync_hunt_findings.py |
| 78c41bf5 | scripts/finding_detail.py |
| 26bd7ee0 | scripts/dashboard_sync.py |
| 9e38136e | scripts/run_hunt_sync_hook.py |
| 00cf5f56 | scripts/validate_hunt_sync_completion.py |
| d9f09981 | scripts/funnel.py |
| 5c6cccb5 | scripts/findings_overview.py |
| 197ac4d5 | scripts/dashboard.py |
| fe37e6ad | scripts/validate_p208_l3_readiness.py |
| e4960878 | scripts/submission_readiness_review.py |
| 04211964 | run_pipeline.sh |

### Forbidden files (never touched)
| md5 | file |
|-----|------|
| ef93a6c2 | prompts/deep_trace.md |
| 41dd3c96 | scripts/min_confirm_gate.py |
| 4fadfc5f | scripts/confirm_gate.py |
| bea43487 | config/runtime_policy.json |

### Data inputs that WILL change (intended)
| START md5 | file |
|-----------|------|
| c7166e71 | documentation/research/funnel/synced_findings.generated.json |
| a551926d | output_research/l3_readiness/ZETA-04.json |
| 4384320f | output_research/l3_readiness/ZETA-10.json |
| 029cd55c | output_research/l3_readiness/ZETA-11.json |
| 221c8ad2 | output_research/funnel/sync_hook_metrics.json |

ZETA-07.json (64c9e4e6) is the executed gold-standard reference and is NOT modified.
END hashes and equality verdict: see `integrity_checks.md`.
