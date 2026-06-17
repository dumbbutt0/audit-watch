# P210 — implementation notes

## Files changed (production)
- `scripts/submission_readiness_review.py` `b435a635` → `7c4b563d` — L3 wiring (all flag-guarded).
- `scripts/dashboard.py` `1eb4e278` → `857d593a` — read-only L3 panel (flag-guarded; key absent flag-off).

## Files added
- `tests/research/test_l3_readiness.py` (20 tests).
- `documentation/research/assisted_mode/p210_l3_dark_wiring/fixtures/human_override_{with,without}_reason.json`.
- This deliverable set.

## Design choices
- **Import, not copy:** `l3_evaluate` lazily imports `validate_p208_l3_readiness.decide` → single source of truth;
  a parity test guards against drift. `decide()` is pure and `__main__`-guarded, so import has no side effects.
- **Fail-closed for High, fail-open elsewhere:** missing/malformed L3 record blocks a High target but never affects
  Medium/Low or discovery.
- **Critical:** the L3 policy gates {High, Critical}, but the module's pre-existing q6 severity vocabulary
  (`_SEVERITIES`) does not include "Critical" — so Critical is independently un-submittable today; not changed here.
- **Out of scope (unchanged, hash-verified):** deep_trace, min_confirm_gate, confirm_gate, final_submission_pack,
  routing, candidate selection, canonical severity labels.
