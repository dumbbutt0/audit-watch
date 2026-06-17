# P215 — DASHBOARD REVIEW

Server launch is flaky in this harness (consistent with prior phases), so the read-only routes were verified by
importing `scripts/dashboard.py` and calling the handlers/`_build_state()` directly with `AUDITWATCH_L3_READINESS=1`.
0 stray dashboard processes left running.

## Read-only state (real `_build_state()`)
- `active_audit.audit_id = zetachain-2023-10-holdout` ✅ (reflects the switched workspace).
- `findings = 12`; `triage_funnel = {total_raw 12, submit 2, poc_required 5, downgraded 4, rejected 1}`;
  `severity_distribution = {Critical 1, High 7, Medium 4}` — **matches the on-disk artifacts**.

## Routes audited for safety
POST routes present: `/api/audits/{switch,create}`, `/api/chat`, `/api/run`, `/api/validation/{label,promotion,
chain/section,status}`. **None submit to or route to an external platform.** `/api/validation/promotion` is internal
investigation-workspace promotion (`PROMOTE_TO_CHAIN_ANALYSIS`), not submission. No `submit_now` / `route_to_platform` /
`publish` control exists. The `/p212` API is explicitly `research_only:true`, `routing_allowed:false`,
`active_audit_unchanged:true`, and refuses `_sealed`/`targets` paths (403).

## L3 panel (flag on)
- `submission_readiness_review.l3_evaluate` (the data behind the L3 panel) returns, for High/Critical candidates:
  `applies=True`, `high_promotion_allowed=False`, `l3_blocker_codes=['blocked_by_missing_l3_poc']`,
  `routing_allowed=False` (verified directly earlier).
- `detail_overlay(cid)` shows `not_reviewed` / `routing_allowed=False` until a human review row sets a High severity —
  correct: the L3 panel populates once a reviewer selects a High/Critical target. No `record_review` rows were written,
  so the shared overlay ledger is untouched and every candidate reads `not_reviewed`.

## One mismatch found and resolved (honest)
On first inspection the dashboard funnel read **0** while the triage buckets held 2/5/4/1. Cause: `_build_state()` keys
off `data/findings/<id>.json` (the real-funnel **Step-3 populate**), which had not been run. After running that exact
populate step, the dashboard matched the artifacts. **Net dashboard_mismatches after completing the funnel step: 0.**
(Lesson for the real hunt: the dashboard depends on the Step-3 `populate_finding_metadata` substrate, not just
merged_findings + triage buckets.)

## Verdict
Dashboard is **read-only for findings/state**, exposes **no submit/promote-to-platform control**, surfaces the L3
blockers and (post-populate) the correct funnel counts, and keeps the answer key sealed. Safe.
