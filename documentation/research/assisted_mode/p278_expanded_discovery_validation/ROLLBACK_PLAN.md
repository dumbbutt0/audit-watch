# P278 — ROLLBACK_PLAN

1. Restore `config/research_award_class_coverage_router.json` caps to poc_budget=5, max_classes=5 (config sha
   `f6d7df670c4df16d`, the P277 state) and restore the config hash pins in test_p274/p275/p276/p277 to that value.
2. Delete `scripts/research/expanded_validation_queue.py`, `scripts/research/poc_readiness_evidence_gate.py`,
   `config/research_expanded_validation_queue.json`, `tests/research/test_p278_expanded_discovery_validation.py`, and
   `documentation/research/assisted_mode/p278_expanded_discovery_validation/`.
3. Router CODE (`6debb753`) and p276/p277 glue were never changed. No production routing/gate/severity path touched; no
   production authority granted; active audit unchanged; eval sources read-only.
