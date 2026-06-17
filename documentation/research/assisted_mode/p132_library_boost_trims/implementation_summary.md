# P132 — Implementation Summary

Two general noise trims added to the P130 library/helper surface boost — **boost-local only**, no change to the
boost's core gate (risk tag + helper shape + in_scope + cap) and no change to the single off-switch
(`library_internal_surface_boost`).

## Files changed (2)
1. **`scripts/build_coverage_manifest.py`**
   - `_is_mock_item(item)` — structural mock/test detection (file basename / contract name contains `mock`,
     or a test/mock/fixture path segment). Catches `Mock*.sol` **and** `*Mock*.sol` (`ConnectorMock2.sol`) **and**
     `contract ConnectorMock2` even when the file isn't Mock-prefixed. Never inspects comments/strings.
   - `_is_trivial_body(body_src)` — True iff the body is empty or a single `return <trivial-expr>;` with
     trivial-expr ∈ {`new T[](0)`, `address(0)`, `0`, `1`, `true`, `false`, `""`, `''`, ALL-CAPS constant};
     comments stripped first. Anything with a call / arithmetic / indexing / loop / conditional / assignment /
     multiple statements / value logic is non-trivial → kept. Conservative (when unsure → keep).
   - During function enumeration: `it["trivial_body"] = _is_trivial_body(<function source>)` (additive field).
   - `_apply_library_surface_boost.eligible()` gains: `and not _is_mock_item(it) and not it.get("trivial_body", False)`.
2. **`tests/coverage/test_library_internal_surface.py`** — +14 P132 tests (all 10 required behaviors).

## What stayed unchanged
- The boost gate (risk tag + helper shape + in_scope + per-contract cap) and `library_internal_surface_boost`
  as the single off switch. No config-flag change. No `contract_type` change.
- No detector / severity / submission / specialist-prompt change. Existing `Mock*.sol` exclude-glob behavior
  (global scope) untouched — the mock trim is boost-local.

## Result (noya, real scope)
boosts 67→60 distinct (−7 = 3 mock + 4 trivial); **all 8 awarded value_exit/oracle functions preserved**;
awarded-function deep-pass coverage **74% → 74%**; deep-pass volume 228→221. decent control unchanged
(awarded 33%→33%, volume 52→52). Full suite 1586 passed / 2 pre-existing snapshot fails / 4 skipped.
