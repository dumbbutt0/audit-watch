# P210 — backtest results (through the wired path)

The P208 dry-run policy and the P210 wired `l3_evaluate()` use the SAME imported `decide()` → identical verdicts.

- `python scripts/validate_p208_l3_readiness.py backtest` → 10 candidates, 10 expected matches, 0 false-allows,
  0 false-blocks, schema 10/10. (`validate_p208_l3_readiness.py` hash `7e148e18` unchanged.)
- Parity test (`test_parity_with_p208_fixtures`): `srr.l3_evaluate(rec,"High")["high_promotion_allowed"]` ==
  each fixture's `expected.high_promotion_allowed` for all 10 → PASS.
- Allowed L3 Highs = 2 (decent H-01, vultisig H-01); blocked = 8 (M-03 x2 + 6 regressions).
- 0 dashboard mismatches (panel uses the same helper); 0 submission/routing side effects (no-submit guard test green).
