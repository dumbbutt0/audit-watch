# P210 — test results

| suite | command | result |
|---|---|---|
| Flag-OFF regression (existing) | `pytest tests/research/test_submission_readiness.py` (flag unset) | **14 passed** (unchanged from baseline) |
| New L3 readiness tests | `pytest tests/research/test_l3_readiness.py` | **20 passed** |
| P208 backtest (dry-run policy) | `python scripts/validate_p208_l3_readiness.py backtest` | **10/10**, 0 false-allow/0 false-block |

## New-test coverage (20)
- flag-off: `evaluate()` has no L3 blocker; `detail_overlay()` has no `l3` key.
- flag-on: High+no-record → blocked; High+PASS (decent & vultisig H-01) → clears; High+FAIL (decent & vultisig M-03)
  → blocked; Medium → unaffected; malformed/None/garbage High → fail-closed (4 cases); static-High-no-PoC → blocked.
- Critical: `l3_evaluate` applies + fails-closed (pure level; note q6 vocab independently excludes Critical).
- human override: with-reason → allowed; without-reason → blocked.
- parity: `l3_evaluate` over all 10 P208 fixtures == P208 expected `high_promotion_allowed`.
- no-submit guard: L3 outputs `research_only:true`/`routing_allowed:false`, no `submission_ready`; L3 source region
  contains none of `submission_ready = True`/`routing_allowed = True`/`final_submission_pack`/`route(`/`submit(`;
  overlay still carries the "never set true" invariant.
