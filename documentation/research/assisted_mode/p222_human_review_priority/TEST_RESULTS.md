# P222 — Test results

## New: `tests/research/test_p222_human_review_priority.py` (20 tests)
Pure classifier: ZETA-04 → HIGH but not submission-ready (and the helper carries no submission/severity keys) ·
ZETA-10 not HIGH after L3 refutation · ZETA-11 MEDIUM (wrong-mechanism partial) · static-only trusted-system not
HIGH · source-refuted cannot be HIGH (incl. "refuted" note) · mock-created vuln not HIGH · H5-style unprivileged
stays out of the lane · priority value is never a (meaningful) attacker_model value.
Severity invariance: `decide()` = medium/invalid/medium, all `high_promotion_allowed` false (unchanged).
Sync mirror: every record carries valid priority fields; ZETA-04 backfill + safety flags preserved;
ZETA-10/11/07 backfill. Detail card top-line banner exact. Funnel/overview carry the fields; HIGH boosts to
`_effective_rank=1.5` and ranks above ordinary noise. Completion guard: valid HIGH passes; HIGH+submission_ready
fails; HIGH+routing_allowed fails; absent priority fails; `NONE` accepted as valid.

## Edited: `tests/research/test_hunt_sync_completion.py`
`_rec()` fixture now seeds `human_review_priority="NONE"` (what `CARD_INJECT` supplies on every real synced
record). Two P218 guard tests (`test_happy_path_passes`, `test_missing_package_link_warns_and_strict_fails_hook_level`)
predated the new mandatory-field check; the seed restores them. 13/13 pass.

## Runs
- `test_p222_human_review_priority.py`: **20 passed**.
- `test_hunt_sync_completion.py` after the fixture fix: **13 passed**.
- **Full research regression (`tests/research/`): 259 passed / 0 failed** (P221 was 239; +20 P222 tests).
  (The first full run surfaced exactly the two stale P218 guard fixtures above; both fixed, re-run clean.)

## Pipeline
`run_hunt_sync_hook.py`: exit 0, completion guard PASS (failures/warnings/reader/card empty; 12 records;
all_safety_ok True; completeness 90%; completion_ok True).
