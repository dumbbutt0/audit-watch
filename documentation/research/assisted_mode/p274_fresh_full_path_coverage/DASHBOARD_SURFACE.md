# P274 — DASHBOARD_SURFACE (Phase 2)

Standalone advisory surface only. **No** `dashboard.py` / `dashboard_sync.py` / canonical-dashboard touch
(forbidden `dashboard_sync.py` `c1af70e1` byte-identical, verified Phase 0). The feed + page are built from the frozen
Phase-1 advisory candidates and carry the advisory contract end-to-end.

## Artifacts
| artifact | hash | note |
|---|---|---|
| `outputs/advisory_recall_feed.json` | `e91eff88ae752fce` | 15 advisory candidates, all `emits_findings:false` |
| `outputs/p274_advisory.html` | `28a581cc8515933d` | static page; banner = ADVISORY ONLY |

## Advisory contract (page + feed)
- `is_gate:false · research_only:true · routes_in_production:false · emits_findings:false`.
- Banner: `ADVISORY ONLY · NOT CONFIRMED · NOT REPORTABLE · NOT SUBMISSION-READY · severity: HUMAN_PENDING`.
- `controls_present`: only `select_for_p274_poc_queue (advisory)`.
- `controls_absent`: `promote_to_finding · confirm · set_severity · mark_reportable · mark_submission_ready · submit`
  — none are wired; there is no path from this surface to a production finding.

## What it shows (Phase-1 candidates, multi-class)
15 advisory loci, `promotion_label = NEEDS_RANKING` (downstream selector/coverage/triage decide). Spread across
order/offer, accounting, DoS/liveness, and auction/state — the diversity P274 is testing. No severity, no award
labels, no answer-key content.

Next: Phase 3 — frozen P267 selector over B/C pairs (BLIND dimensions).
