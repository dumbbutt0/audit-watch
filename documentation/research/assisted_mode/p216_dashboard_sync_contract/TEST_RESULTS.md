# P216 — TEST RESULTS

## New suite: `tests/research/test_dashboard_sync.py` — 16/16 PASS
Covers every acceptance dimension:
- schema validation (every mirror record `validate_synced == []`)
- adapter: missing fields → `unknown`/`MISSING_EVIDENCE`; no inferred severity (recorded only); safety flags constant
- mirror: no duplicate `record_id`; all safety flags false; adapter deterministic (idempotent)
- visibility: 12 P215 records in `funnel.load_records()`, `findings_overview.load_overview()`, and the
  `api_funnel`/`api_findings`/`api_candidates` handlers — **no active-audit switch**
- detail card: 15/15 H5 verifier sections for all 12; `submission_ready/routing_allowed:false`; `read_only_synced:true`
- severity is never a conversion/lifecycle token (browser computes no severity)
- finished Abracadabra H5 runtime card still renders (regression guard)
- no `<form>`/POST/"submit now"/"promote to platform" in the three pages' HTML

## Regression check: existing funnel/findings/detail suites
First full run flagged **4 failures** in `tests/funnel/test_funnel.py` (seed/metric counts) because the initial reader
merge used `path == DEFAULT_RECORDS_PATH`, which also fired for tests that pin `SEED` (== the default path), inflating
seed counts (blind 7 → 19).

**Fix:** gate the merge to the **implicit default call only** (`path is None`) — the live dashboard read path. A caller
that pins an explicit path (tests/tools), even when equal to the default, gets exactly that file. Verified:
`load_records()` → 20 (8 curated + 12 mirror); `load_records(DEFAULT_RECORDS_PATH)` → 8.

After the fix: the 4 tests **pass**; full suite re-run = `tests/funnel/` + `test_findings_overview.py` +
`test_unified_candidate_detail.py` + `test_dashboard_sync.py` → 0 failures (see run log). No existing test was modified.

## Final full re-run (after the merge-gating fix)
`tests/funnel/ + test_findings_overview.py + test_unified_candidate_detail.py + test_dashboard_sync.py` →
**105 passed, 0 failed** (395.93s). 0 regressions. (The first run's "4 failed / 134 passed" deselected a wider set;
the targeted final run executes the four relevant suites in full.)
