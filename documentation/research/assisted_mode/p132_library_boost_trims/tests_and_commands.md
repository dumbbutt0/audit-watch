# P132 — Tests & Commands

## Tests (`tests/coverage/test_library_internal_surface.py`) — 24 pass (10 P130 + 14 P132)
P132 additions cover the 10 required behaviors:
1. `Mock*.sol` still excluded — `test_mock_glob_file_still_excluded`
2. `*Mock*.sol` / `ConnectorMock2.sol` excluded — `test_starmock_filename_excluded`
3. contract-name mock detection (file not Mock-prefixed) — `test_contract_name_mock_excluded_even_if_file_not_mock_prefixed`
   (+ `test_mock_path_segment_excluded`, `test_legit_contract_not_flagged_as_mock`)
4. `return new address[](0)` not boosted — `test_trivial_empty_array_return` + `test_trivial_helper_not_boosted`
5. `return address(0)` not boosted — `test_trivial_address_zero_return`
6. `return 0/1/true/false/""/CONSTANT` not boosted — `test_trivial_literal_returns` (+ empty body)
7. non-trivial oracle/value helper still boosted — `test_nontrivial_oracle_helper_still_boosted` +
   `test_nontrivial_body_with_call_or_math_kept`
8. `_getPositionTVL`-style helper still boosted — `test_getpositiontvl_style_still_boosted`
9. cap behavior unchanged — `test_per_contract_cap_bounds_inflation` (P130, still passes)
10. `library_internal_surface_boost=false` → no boost — `test_flag_off_is_fully_reversible` (P130, still passes)

## Commands run
```
python -m pytest tests/coverage/test_library_internal_surface.py -q     # 24 passed
python scripts/assisted/rank_signal_probe.py --self-test                 # SELF-TEST: OK
python -m pytest -q                                                      # 1586 passed, 2 failed, 4 skipped
# measurement (active audit switched to noya/decent, then restored to quantamm-2024-12-eval):
python scripts/audit_manager.py switch noya-2024-04-eval
python scripts/build_coverage_manifest.py --contract <noya>/contracts --out p132/noya_ON_trimmed.json
python scripts/audit_manager.py switch decent-2024-01-holdout
python scripts/build_coverage_manifest.py --contract <decent>/src --out p132/decent_ON_trimmed.json
python scripts/audit_manager.py switch quantamm-2024-12-eval            # restored
python3 p130/measure.py <manifest> _p81b/noya/recall_score.json <label>
```

## Results
- Focused: **24 passed**.
- Full suite: **1586 passed, 2 failed, 4 skipped** — the 2 failures are the known pre-existing `deep_solidity`
  frozen-snapshot tests (active-audit `output/` symlink), unchanged from P130/P131; +14 vs P131's 1572 are the
  new P132 tests. No new regressions.
- `rank_signal_probe --self-test`: OK (frozen/research scripts untouched).
- Active audit restored to `quantamm-2024-12-eval`.
