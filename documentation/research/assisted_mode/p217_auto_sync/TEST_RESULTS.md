# P217 — TEST RESULTS

## New suite: `tests/research/test_sync_hunt_findings.py` — 14/14 PASS
- `--dry-run` writes nothing · `--write` emits 12 (prefixed ids) · idempotent (byte-identical) · no duplicate ids
- every record `validate_synced == []` + `safety_ok` + `submission_ready/routing_allowed:false`
- `--strict` returns 0 on a clean run
- completeness ≥ 85% (and > the 57% P216 baseline)
- unknowns remain explicit (`novelty_duplicate` never invented); no invented severity (recorded-or-HUMAN_PENDING)
- P215 visible in `funnel.load_records()` + `findings_overview.load_overview()`
- detail cards `ZETA-04/07/11` → 15 verifier sections, with populated exploit_steps + mechanism
- no active-audit switch required

(One pre-fix issue: a logging line used `out.relative_to(ROOT)` which raised for tmp `--out` paths outside the repo —
fixed with a safe `_rel()` helper; record content was never affected.)

## Full regression (after the fix)
`tests/research/test_dashboard_sync.py + test_sync_hunt_findings.py + tests/funnel/test_funnel.py +
test_findings_overview.py + test_unified_candidate_detail.py` → **119 passed, 0 failed** (475s). 0 regressions.
The P216 contract tests (16) and the funnel metric tests all stay green (the wrapper writes to a separate mirror and
the reader merge remains gated to the implicit default call).
