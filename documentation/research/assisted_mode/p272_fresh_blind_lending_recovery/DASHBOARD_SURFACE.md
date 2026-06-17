# P272 — DASHBOARD_SURFACE (Phase 2)

Standalone advisory-only surface (P266 pattern) from the frozen init-capital shadow output. Does NOT touch
dashboard.py / dashboard_sync.py (forbidden, re-verified c1af70e1) / dashboard/*.html / canonical records.

## Artifacts
- outputs/advisory_recall_feed.json (5c3cda01fe1dc10c)
- outputs/p272_advisory.html (14a1a4df5a0f5a58)
From init_shadow/recall_advisory_candidates.json (frozen 000b69658811261b).

## Safety
Banner: ADVISORY ONLY · NOT CONFIRMED · NOT REPORTABLE · NOT SUBMISSION-READY · severity HUMAN_PENDING. Every record
status=ADVISORY_RECALL_CANDIDATE, severity null, all promotion/confirmed/canonical flags false. Controls present:
select_for_p272_poc_queue (advisory). Controls absent: promote/confirm/set_severity/mark_reportable/submit.
20 candidates (5 narrow / 15 recall-delta). Frozen before selector/triage.
