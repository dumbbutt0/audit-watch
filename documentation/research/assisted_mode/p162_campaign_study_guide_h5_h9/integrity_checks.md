# P162 integrity checks (documentation-only)

| Artifact | Baseline | Post-P162 | Result |
|---|---|---|---|
| runtime sidecar `output_research/value_provenance_eval/runtime_status.jsonl` | `491da8c1…` | `491da8c1…` | **byte-identical** (read-only reference) |
| frozen corpus `documentation/evals/judge_corpus/frozen_corpus.json` | `60089ff5…` | `60089ff5…` | **byte-identical** |
| campaign ledger `output_research/option_a_campaign/ledger.jsonl` | `c74ce773…` (5 rows) | `c74ce773…` (5 rows) | **unchanged — no row** (P162 is not a candidate) |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- Documentation-only phase: all edits confined to
  `documentation/research/assisted_mode/p162_campaign_study_guide_h5_h9/` (study_guide.md, metrics.json,
  integrity_checks.md).
- No production source changed; no harness built; no detector / taxonomy / dashboard code / routing / prompt /
  schema change. The §8 prompt patch is **recommended, not applied**.
- Un-wired: `grep p162_campaign run_pipeline.sh config/agent_policy.json` → empty.
- No-regression: `tests/research/test_option_a_campaign.py` green (this phase changes nothing it reads).
