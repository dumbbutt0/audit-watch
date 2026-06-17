# P276 — CORPUS_SELECTION (SUPERVISED_EVAL)

13 eval audits under `audits/*-eval` considered. Contamination/prior-exposure is **acceptable here** — this is
supervised eval, not blind. Inclusion driven by award-key machine-readability (locus-level vs title-only vs none).

| contest | award-key schema | awarded H/M | locus info? | tier |
|---|---|---|---|---|
| zaros-2025-01-part-2-eval | `answer_key_raw.json` (list) | 51 | yes | **locus-mapped** |
| revert-lend-2024-03-strict-eval | `answer_key_normalization` | 31 | yes | **locus-mapped** |
| panoptic-2025-12-strict-eval | `answer_key_normalization` | 22 | yes | **locus-mapped** |
| recall-2025-02-strict-eval | `answer_key_normalization` | 13 | yes | **locus-mapped** |
| ark-project-2024-07-strict-eval | `answer_key.json` (families) | 11 | yes | **locus-mapped** |
| hybra-finance-2025-10-strict-eval | `answer_key_normalization` | 10 | yes | **locus-mapped** |
| silo-finance-2025-03-strict-eval | `answer_key_normalization` | 6 | yes | **locus-mapped** |
| swan-dria-2024-10-strict-eval | `raw_answer_key` (captured_rows) | 65 | **no (title only)** | count-only |
| quantamm-2024-12-strict-eval | `raw_answer_key` (captured_rows) | 40 | **no (title only)** | count-only |
| beanstalk-2024-05-eval2 | none in audit (see `evals/beanstalk_finale`) | — | — | excluded (no machine key) |
| blackhole-2025-05-eval | md only | — | — | excluded (md key) |
| noya-2024-04-eval | md only | — | — | excluded (md key) |
| quantamm-2024-12-eval (non-strict dup) | dup of strict | — | — | excluded (duplicate) |

## Decision
- **Locus-mapped funnel = 7 contests / 144 awarded H/M** (the primary repair map; full stage + first_failed_stage).
- **Count-only = 2 contests / 105 awarded H/M** (severity counted; locus funnel N/A → recorded
  `DUPLICATE_OR_REPORT_ONLY_AMBIGUITY`; backlog R6 = enrich keys).
- **Excluded = 4** (md/none/dup award keys — not machine-readable for automated mapping).
- All 12 distinct audits ran **Pass A** cleanly (206 advisory candidates, all guards 0).

Protocol-class spread of the locus-mapped set: AMM/options (panoptic), CDP/lending (revert-lend, silo), perps (zaros),
LST/governance (hybra), bridge (ark), subnet/checkpointing (recall) — genuinely multi-architecture.
