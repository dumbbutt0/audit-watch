# P214 — test results

| suite | result |
|---|---|
| NEW `tests/research/test_l3_dos_carveout.py` | **20 passed** |
| existing `tests/research/test_l3_readiness.py` (flag on/off) | **20 passed** (no regression) |
| existing `tests/research/test_submission_readiness.py` (flag-off) | **14 passed** (no regression) |
| P208 backtest (`validate_p208_l3_readiness.py backtest`) | **10/10** all_match (flag-off unchanged) |
| P213 regression (`validate_p213.py`) | **10/10** all_pass |

## New-test coverage (20)
flag-off: no carve-out keys, no upgrade (output-equivalent). flag-on: full carve-out → high; **each of the 10
criteria missing → blocked** (parametrized ×10); not-candidate → no upgrade; NEEDS_HARNESS → no upgrade; source-refuted
→ invalid; production_source_modified → no upgrade; human_judgment_required w/o notes → blocked; malformed `{}` → fail
closed; non-DoS theft High unaffected; the real SOPH-03 record → high + applied.

## Dashboard (verified via direct `dashboard.api_p212()` call, flag toggled)
flag-off SOPH-03 → medium / carveout_applied=false; flag-on SOPH-03 → high / high_allowed=true / carveout_applied=true;
flag-on SOPH-05 (privileged) → stays medium / carveout_applied=false.
