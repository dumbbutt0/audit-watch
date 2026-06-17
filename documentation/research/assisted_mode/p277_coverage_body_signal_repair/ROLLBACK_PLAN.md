# P277 — ROLLBACK_PLAN

To revert the R1 repair:
1. Restore `scripts/research/award_class_coverage_router.py` and `config/research_award_class_coverage_router.json` to
   the pre-P277 versions (router sha `b87e3d22d1fb915b`, config sha `3fbc476e3d8945b6`). Behavior reverts exactly
   (the new code is locus-equivalent when body fields are absent).
2. Restore the `award_class_coverage_router.py` / config hash pins in test_p274/p275/p276 to `b87e3d22…` /
   `3fbc476e…`.
3. Delete `scripts/research/p277_corpus_replay.py`, `tests/research/test_p277_coverage_body_signals.py`, and
   `documentation/research/assisted_mode/p277_coverage_body_signal_repair/`.
4. `p276_corpus_replay.py` / `p276_award_funnel_map.py` / `p276_metrics.py` were never changed.

No production routing/gate/severity path was touched; no production authority granted; active audit unchanged; eval
sources read-only.
