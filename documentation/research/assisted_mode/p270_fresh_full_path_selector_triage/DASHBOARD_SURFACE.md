# P270 — DASHBOARD_SURFACE (Phase 2)

Standalone advisory-only surface (P266 pattern), generated from the frozen wise-lending shadow output. Does NOT touch
`scripts/dashboard.py`, `scripts/dashboard_sync.py` (forbidden, re-verified `c1af70e1`), `dashboard/*.html`, or any
canonical finding record.

## Artifacts
- `outputs/advisory_recall_feed.json` (`83ad66c61f5e7362`)
- `outputs/p270_advisory.html` (`100e83a700b28c00`)
From `wise_shadow/recall_advisory_candidates.json` (frozen `090d10d12e099355`).

## Safety labels (banner + every record)
Banner: **ADVISORY ONLY · NOT CONFIRMED · NOT REPORTABLE · NOT SUBMISSION-READY · severity: HUMAN_PENDING**.
Every record: `status=ADVISORY_RECALL_CANDIDATE`, `severity=null`, all promotion + `confirmed`/`canonical_record`
flags false (re-asserted by the generator).

## Controls
- **Present:** `select_for_p270_poc_queue` (advisory; isolated queue only).
- **Absent by design:** promote_to_finding · confirm · set_severity · mark_reportable · mark_submission_ready · submit.

24 advisory candidates shown (5 narrow / 19 recall-delta). Frozen before selector/triage.
