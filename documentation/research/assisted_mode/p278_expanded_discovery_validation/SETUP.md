# P278 — SETUP (SUPERVISED_EVAL / SHADOW_RESEARCH)

Wider discovery/validation breadth + strict evidence -> PoC-readiness gate. **More candidates may enter validation;
none becomes PoC-ready without complete evidence.** Maps+improves; no production authority; severe FP must stay 0.

## Allowed edits (this phase)
- `config/research_award_class_coverage_router.json` caps only: poc_budget 5->10, max_classes 5->8 (router CODE
  unchanged, hash `6debb753b45f1833`; config hash now `91f9deac7867af62`).
- NEW `scripts/research/expanded_validation_queue.py`, `scripts/research/poc_readiness_evidence_gate.py`,
  `config/research_expanded_validation_queue.json`, `tests/research/test_p278_expanded_discovery_validation.py`, this dir.
- Config-hash-pin bump in test_p274/p275/p276/p277.
- Reuse (no edit): p277_corpus_replay.py, p276_award_funnel_map.py, p276_metrics.py.

## Byte-identical (verified): P260 d6b494bc · P262 a48336275f · P264 harness 85f9cbe6 · P267 b0623b8c · P269 63c88d02 ·
**router CODE 6debb753** + P267/P269 configs + P271 checklist 2929a2154a88; forbidden 5; p276/p277 glue. Active audit
symlink -> audits/size-credit-2024-06-blind/output.
