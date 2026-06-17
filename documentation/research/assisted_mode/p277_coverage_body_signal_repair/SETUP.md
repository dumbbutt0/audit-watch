# P277 — SETUP (R1 repair; first authorized frozen-module edit)

REPAIR phase (calibration, not blind, not production authority). Implements P276 backlog **R1**: derive coverage-class
signals from generated-mechanism BODY fields, not only locus/name tokens. Maps+improves; the strict late gate is
untouched.

## Allowed edits (everything else byte-identical)
- `scripts/research/award_class_coverage_router.py` — now sha `6debb753b45f1833` (was b87e3d22)
- `config/research_award_class_coverage_router.json` — now sha `f6d7df670c4df16d` (added body-signal config + extended keywords)
- `scripts/research/p277_corpus_replay.py` (NEW; p276 replay + body fields; p276_corpus_replay.py left frozen)
- `tests/research/test_p277_coverage_body_signals.py` (NEW)
- router/config **hash-pin bump** in test_p274/p275/p276 (single constants each)
- this deliverable dir

## Byte-identical (verified): P260 d6b494bc · P262 a48336275f · P264 harness 85f9cbe6 · P267 b0623b8c · P269 63c88d02
+ their configs + P271 checklist 2929a2154a88; forbidden 5 (c1af70e1/c095c426/2a15169a/afc481c9/ae55eb80);
p276_corpus_replay/award_funnel_map/metrics unchanged. Active audit symlink → audits/size-credit-2024-06-blind/output.
No production authority / severity / reportable / submission / confirmed.
