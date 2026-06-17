# P268 — DASHBOARD_CANDIDATE_SURFACE (Phase 3)

Standalone advisory-only surface, same pattern as P266 (which proved it safe). Generated from the frozen karak shadow
output; does NOT touch `scripts/dashboard.py`, `scripts/dashboard_sync.py` (forbidden, re-verified `c1af70e1`),
`dashboard/*.html`, or any canonical finding record.

## Artifacts
- `outputs/advisory_recall_feed.json` (`0bfb52b70571c7cf`)
- `outputs/p268_advisory.html` (`71103b85abe60820`)
Generated from `karak_shadow/recall_advisory_candidates.json` (frozen `7138129294930f7e`).

## Safety labels (page banner + every JSON record)
Banner: **ADVISORY ONLY · NOT CONFIRMED · NOT REPORTABLE · NOT SUBMISSION-READY · severity: HUMAN_PENDING**.
Every record: `status=ADVISORY_RECALL_CANDIDATE`, `severity=null`, and `reportable=submission_ready=concluded=
emits_finding=production_routing=confirmed=canonical_record=False` (re-asserted by the generator on every row).

## Controls
- **Present:** `select_for_p268_poc_queue` (advisory; writes only the isolated P268 PoC queue).
- **Absent by design:** promote_to_finding · confirm · set_severity · mark_reportable · mark_submission_ready ·
  submit. Structurally impossible for a candidate here to look confirmed/reportable.

## Operator selection
20 advisory candidates shown (5 narrow / 15 recall-delta). The operator picks 2–4 for PoC routing in Phase 4
(TRIAGE_AND_POC_QUEUE writes the isolated queue). No selection mutates a canonical record or sets any authority field.
Frozen before triage.
