# P275 — DASHBOARD_SURFACE (Phase 2)

Standalone advisory surface only. **No** `dashboard.py`/`dashboard_sync.py`/canonical touch (forbidden `dashboard_sync`
`c1af70e1` byte-identical). Built from the frozen Phase-1 advisory candidates; carries the advisory contract.

## Artifacts
| artifact | hash | note |
|---|---|---|
| `outputs/advisory_recall_feed.json` | `61080dfc57a33aed` | 6 advisory candidates, all `emits_findings:false` |
| `outputs/p275_advisory.html` | `2444fde665dff5ae` | static page; banner = ADVISORY ONLY |

## Advisory contract
`is_gate:false · research_only:true · routes_in_production:false · emits_findings:false`. Banner:
`ADVISORY ONLY · NOT CONFIRMED · NOT REPORTABLE · NOT SUBMISSION-READY · severity: HUMAN_PENDING`. `controls_present`:
only `select_for_p275_poc_queue (advisory)`. `controls_absent`: promote_to_finding · confirm · set_severity ·
mark_reportable · mark_submission_ready · submit. No path from this surface to a production finding.

## Shows
6 advisory loci (`NEEDS_RANKING`) spanning migration/position/router-callback/AMM-math/upgrade. No severity, no award
labels, no answer-key content. Next: Phase 3 selector.
