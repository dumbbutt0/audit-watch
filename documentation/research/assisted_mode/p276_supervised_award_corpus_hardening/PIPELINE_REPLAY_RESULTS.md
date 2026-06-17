# P276 — PIPELINE_REPLAY_RESULTS (Pass A, no key)

12 distinct eval audits replayed through the frozen funnel from their existing `coverage_manifest.json` →
checkpoints → P264 harness (shadow) → P273 coverage → P269 triage. **206 advisory candidates; all guards 0.**
Driver: `scripts/research/p276_corpus_replay.py`; per-contest bundles under `outputs/<audit>/replay_bundle.json`.

| contest | advisory cands | coverage classes | triage selected |
|---|---|---|---|
| ark-project-2024-07-strict-eval | 11 | 3 | 4 |
| beanstalk-2024-05-eval2 | 16 | 5 | 5 |
| blackhole-2025-05-eval | 25 | 5 | 5 |
| hybra-finance-2025-10-strict-eval | 23 | 5 | 5 |
| noya-2024-04-eval | 19 | 5 | 4 |
| panoptic-2025-12-strict-eval | 11 | 3 | 4 |
| quantamm-2024-12-strict-eval | 21 | 3 | 5 |
| recall-2025-02-strict-eval | 18 | 5 | 5 |
| revert-lend-2024-03-strict-eval | 15 | 5 | 4 |
| silo-finance-2025-03-strict-eval | 17 | 5 | 4 |
| swan-dria-2024-10-strict-eval | 13 | 4 | 5 |
| zaros-2025-01-part-2-eval | 17 | 5 | 5 |

Coverage routed 3–5 distinct classes per contest with no monoculture; triage selected 4–5 across classes. The frozen
modules were invoked as black boxes; only their inputs were auto-built from the harness's own advisory candidates
(locus name tokens → class signals). No answer key opened in Pass A.
