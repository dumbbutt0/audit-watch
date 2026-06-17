# P277 — IMPLEMENTATION_NOTES

## Router (`award_class_coverage_router.py`)
- `_candidate_text` split into `_locus_text(c)` (names/signals/templates — unchanged tier) and `_body_text(c, cfg)`
  (allow-listed body fields, top-level + nested `mechanisms[]`/`generated_mechanisms[]`, denylist enforced, missing
  fields → "").
- `_classify(c, cfg)` rewritten: locus-primary; body reinforces same-class strength; body assigns class ONLY when
  locus is blank; per-class body hits capped (`body_signal_cap_per_class`, default 3). Returns
  `(class, signal_strength, detail)`.
- `route()` consumes the 3-tuple; decisions now also carry `class_signal_sources`, `body_signal_hits`,
  `body_signal_classes`, `final_class_score`, `body_changed_decision`.
- `_plausible`, round-robin + monoculture guard, `_enforce_guards`, fail-closed, caps validation — **unchanged**.

## Config additions
`body_signal_weight` (1), `body_signal_cap_per_class` (default 3 in code), `body_signal_fields` (allowlist),
`body_field_denylist` (award-text guard); extended `class_signals` keyword lists for ORACLE/EXTERNAL/FRONT/ORDER/DOS/
ACCESS/SHARE per the R1 spec. Caps unchanged (poc_budget stays 5 — see REPAIR_METRICS for the budget ablation).

## Backtest driver
`p277_corpus_replay.py` (NEW) = `p276_corpus_replay.py` with the coverage candidate carrying `mechanisms` (allow-listed
body fields from the harness) and `signals` = locus name tokens only (clean tier separation). `p276_corpus_replay.py`
is untouched (the before-baseline).

## Back-compat
With no body fields present the router is byte-equivalent in behavior to pre-P277 (locus-only). Verified: P273's own
behavior tests pass unchanged; P274/P275/P276 read stored artifacts + bumped hash pins.
