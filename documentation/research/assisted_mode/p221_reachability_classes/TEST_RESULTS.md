# P221 — Test results

## New: `tests/research/test_p221_reachability_taxonomy.py` (8 tests)
- every synced record carries a valid `reachability_class`;
- class assignment for the harnessed three (TRUSTED_SYSTEM / UNPRIVILEGED / REACHABILITY_UNKNOWN);
- ZETA-04 card: `privilege_required`/`victim_action_required`/`operator_or_keeper_dependency`/`self_remediation`
  all populated (not "unknown");
- **severity invariance**: `decide()` = medium/invalid/medium with high_promotion_allowed false (unchanged);
- `reachability_class` never appears as an `attacker_model` value;
- non-harnessed candidate keeps granular fields explicit (HARD RULE);
- literal "not unprivileged" does not trip the unprivileged heuristic;
- safety flags false; `validate_synced` clean.

## Edited: `tests/research/test_evidence_extraction.py`
`test_reachability_from_confirm` repointed ZETA-04 → ZETA-03 (ZETA-04 now correctly supersedes the confirm-gate
string with its richer L3 trusted-system verdict).

## Runs
- Subset (`test_p221` + `test_p220` + `test_evidence_extraction` + `test_dashboard_sync`): the only failure was the
  now-repointed stale assertion; **49 passed after the fix** (re-covered by the full run below).
- **Full research regression (`tests/research/`): 239 passed in 738s (0 failed)** — up from 231 (P220) by the 8 new
  P221 tests.

## Pipeline
`run_hunt_sync_hook.py`: exit 0, completion guard PASS (failures/warnings/reader/card empty; 12 records;
all_safety_ok true; completeness 90%).
