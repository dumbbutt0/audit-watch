# P163 integrity checks (documentation-only)

| Artifact | Baseline | Post-P163 | Result |
|---|---|---|---|
| runtime sidecar `output_research/value_provenance_eval/runtime_status.jsonl` | `491da8c1…` | `491da8c1…` | **byte-identical** |
| frozen corpus `documentation/evals/judge_corpus/frozen_corpus.json` | `60089ff5…` | `60089ff5…` | **byte-identical** |
| campaign ledger `output_research/option_a_campaign/ledger.jsonl` | `c74ce773…` (5 rows) | `c74ce773…` (5 rows) | **unchanged — no row** (P163 is not a candidate) |
| active `output` symlink | `audits/quantamm-2024-12-eval/output` | unchanged | **unchanged** |

- Documentation-only: all edits confined to
  `documentation/research/assisted_mode/p163_post_campaign_retrospective/`
  (RETROSPECTIVE.md, metrics.json, integrity_checks.md).
- No code / detector / prompt / dashboard / taxonomy / routing / severity / submission / corpus /
  sidecar-schema change. Every recommendation is marked PROPOSED — NOT IMPLEMENTED.
- Un-wired: `grep p163 run_pipeline.sh config/agent_policy.json` → empty.
- No-regression: `tests/research/test_option_a_campaign.py` green (this phase changes nothing it reads).

**P163.1 amendment (reviewer feedback):** same doc dir, still documentation-only — elevated the validated
source-refutation discipline to a "Headline durable lesson", preserved the conclusion sentence verbatim, and
locked the "Final statuses (P163 review)" table (adds "Named-gate rejection recording → PROMOTE"). No decision
reversed; no code/corpus/sidecar/ledger change. Hashes re-verified unchanged: sidecar `491da8c1…`, corpus
`60089ff5…`, ledger `c74ce773…` (5 rows); symlink `audits/quantamm-2024-12-eval/output`.
