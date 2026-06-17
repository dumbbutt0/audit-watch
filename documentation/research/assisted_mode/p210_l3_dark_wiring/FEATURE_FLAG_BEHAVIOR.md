# P210 — feature flag behavior

Flag: `AUDITWATCH_L3_READINESS` (truthy = `1`/`true`/`True`/`yes`/`on`). Read via `_l3_enabled()` in
`submission_readiness_review.py`; the dashboard reads the same env var directly.

## Flag OFF (default) — output-equivalent to pre-P210
- `evaluate()` adds no L3 blocker (the `if _l3_enabled():` block is skipped).
- `detail_overlay()` returns no `l3` key.
- `dashboard.py` attaches no `l3` field to findings (key absent entirely).
- New set member `blocked_by_missing_l3_poc` exists in `READINESS_STATES` but is never produced.
- Verified: existing `test_submission_readiness.py` → 14/14 pass unchanged.

## Flag ON
- High/Critical target (`severity_recommendation`) + L3 not PASS/HUMAN_OVERRIDE → `evaluate()` appends
  `blocked_by_missing_l3_poc: <reason>` ⇒ not eligible for `ready_for_submission_package`.
- High/Critical + L3 PASS (or HUMAN_OVERRIDE w/ reason) → no L3 blocker; the normal human checklist still applies.
- Medium/Low/QA target → L3 not evaluated (`applies=False`); existing behavior unchanged.
- Missing/malformed L3 record on a High → fails closed (blocked).
- `detail_overlay()` and `dashboard.py` add a read-only `l3` block (advisory; no flags flipped, no controls).
