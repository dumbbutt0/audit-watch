# P218 — TEST RESULTS

## New: `tests/research/test_hunt_sync_completion.py` — 13/13 PASS (0.05s, pure)
Failure modes (each FAILs the guard): missing candidate · unsafe flags · High without L3 PASS · High blocked w/o
blocker · **dry-run-queue entry without synced record** · duplicate record_ids · malformed record · missing package
link (WARN→strict FAIL) · stale extra record · detail card raises · card missing sections. Plus happy-path +
live-real-P215 pass.

## Full regression — 132 passed, 0 failed (474s)
`test_hunt_sync_completion.py + test_sync_hunt_findings.py + test_dashboard_sync.py + tests/funnel/test_funnel.py +
test_findings_overview.py + test_unified_candidate_detail.py`. No dashboard-visibility regression; no route/submit side
effects; P216 (16) + P217 (14) + funnel/overview/detail suites all green.

## Hook end-to-end (REPLAY_MODE)
`run_hunt_sync_hook.py --phase P215 --audit zetachain-2023-10-holdout --workspace …` → exit 0; mirror byte-identical
(idempotent); guard PASS (reader_failures=[], card_failures=[]); sync metrics written.

## Live guard demonstrations
- SUCCESS report on the real mirror → `failures:[]`, exit 0.
- FAILURE report (ZETA-04 removed) → `failures:["ZETA-04: missing from synced mirror","dry-run-queue entry ZETA-04 has
  no synced dashboard record"]`, exit 1.
