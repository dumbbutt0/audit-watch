# P130 — Implementation Notes

## Files changed (minimal — 3 production files)
1. **`scripts/build_coverage_manifest.py`**
   - Added module-level `_apply_library_surface_boost(items, pol)` (the two-signal, capped boost).
   - In the per-file assembly loop: derive `file_decl_kind` from the already-parsed `TYPE_DECL` results and
     set `it["contract_type"] ∈ {contract, library, interface, abstract_contract}` on every item
     (backward-compatible additive field).
   - Call `n_boosted = _apply_library_surface_boost(items, pol)` after enumeration, before building the
     manifest dict.
   - Added a summary print line: `library/internal risk-logic boosted (P130): N`.
2. **`config/agent_policy.json`** → `coverage_policy`: added `library_internal_surface_boost: true` and
   `library_internal_surface_boost_cap_per_contract: 3` (next to `deep_pass_attack_surface_score_min`).
3. **`tests/coverage/test_library_internal_surface.py`** (new): 10 general-behavior tests.

## Schema impact
- New optional item fields: `contract_type` (always) and `surface_boost` (only on boosted items). Additive;
  existing consumers read manifest items by key and are unaffected. No format/version change required.

## Tests (general behavior, no protocol strings) — all 10 pass
- internal library risk-logic boosted to cutoff; public view + accounting tag boosted; `*Facet` internal
  boosted; **no risk tag → not boosted** (two-signal); external non-helper state-changing → not boosted by
  this rule; already-high left alone; out-of-scope not boosted; **per-contract cap bounds count to 3**;
  **flag off fully reversible** (score + provenance restored); strong tags ranked before weak under cap.

## Determinism & integrity
- Re-running the repaired tool on noya produced an **identical** score vector and the same 70 boosts.
- `rank_signal_probe --self-test`: OK (frozen/research scripts untouched).
- Only the 3 files above changed under `scripts/`/`config/`/`tests/`; **no severity, submission, or detector
  file touched**. Active audit switched to noya/decent/beanstalk for measurement and **restored to
  `quantamm-2024-12-eval`** each time.

## Measurement harness (research-only, under this dir)
- `measure.py` — given a manifest + a `recall_score.json`, reports awarded-contract / awarded-FUNCTION
  deep-pass coverage, internal-fn scoring, and high-surface volume. The awarded list is an **eval yardstick
  only**; it is not read by any production code.
- `awarded_contract_yardstick.json` (Beanstalk), `*_manifest_before.json` / `*_manifest_after.json`
  (noya, decent), `miss_taxonomy.json`.

## Note on Beanstalk
Beanstalk source is no longer on disk (`contracts/_sources` empty), so its manifest cannot be regenerated;
the live before/after is on **noya** (primary, library-heavy) and **decent** (control). Beanstalk remains
the documented diagnostic origin (taxonomy + `coverage_gaps` public-only enumeration).
