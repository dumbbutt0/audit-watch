# P129 — Selected Benchmark Audits

7 audits across diverse architectures. Three are **closable locally now** (committed match data);
four contribute **denominators only** (recall pending a pipeline run).

| Audit | Architecture | Ground-truth source | What's measurable now | Why chosen |
|---|---|---|---|---|
| **beanstalk-2024-05** | Stablecoin / economic / L2 migration | `evals/beanstalk_finale/match_matrix.json` (81 public, classified) + `scorecard.json` | **Full**: discovery recall + precision/FP + severity (15 ground-truthed) | Only fully-closed local loop; has both pipeline output and a classified answer key |
| **decent (2024-01)** | Cross-chain bridge / messaging | `_p81b/decent/{awarded_map,recall_score}.json` (9 awarded) | **Lead-recall** (earlier funnel) | Pre-built P81b recall map; bridge architecture |
| **noya** | Vault / strategy aggregator | `_p81b/noya/{awarded_map,recall_score}.json` (19 awarded) | **Lead-recall** (earlier funnel) | Pre-built P81b recall map; oracle/accounting architecture |
| centrifuge-2023-09-holdout | RWA / tranches / liquidity pools | `_sealed_answer_key/report.md` (8 awarded: 8M) | Denominator only | Diverse RWA scope; sealed C4 key |
| pooltogether-2024-03-holdout | Prize vault / ERC4626 yield | `_sealed_answer_key/report.md` (9 awarded: 1H/8M) | Denominator only | ERC4626 yield scope; sealed C4 key |
| predy-2024-05-holdout | Perps / derivatives | `_sealed_answer_key/report.md` (12 awarded: 4H/8M) | Denominator only | Derivatives scope; sealed C4 key |
| zetachain-2023-10-holdout | Cross-chain / omnichain | `_sealed_answer_key/report.md` (48 awarded: 14H/34M) | Denominator only | Large cross-chain scope; sealed C4 key |

## Known-issue totals catalogued
- **Measured-recall audits:** beanstalk 81 (full pipeline) · decent 9 · noya 19 (lead-recall).
- **Denominator-only (recall PENDING_RUN):** centrifuge 8 · pooltogether 9 · predy 12 · zetachain 48 = **77**.
- **Grand total: 186 known awarded issues across 7 audits.**

## What is available vs missing (the structural gap)
- **beanstalk:** ✅ classified match matrix + ✅ `merged_findings.json` ⇒ both directions measurable.
  ⚠️ `data/triage/` was empty (reconstructed faithfully from `merged_findings.json` — see ground_truth_inventory.md).
- **decent / noya:** ✅ awarded map + ✅ P81b *lead*-recall score. ⚠️ This is read-time-lead recall
  (did a lead touch the awarded function), **not** confirmed-finding recall — a weaker, earlier signal.
- **4 holdouts:** ✅ sealed answer key (denominator). ❌ no `merged_findings.json` (only empty/partial
  `data/triage/`) ⇒ recall cannot be computed without running the pipeline on them. Marked `PENDING_RUN`.
- **Why no audit has both:** the holdouts deliberately seal the answer key and were not run end-to-end
  locally; the eval/strict-eval dirs were run but correspond to contests whose reports are not stored
  locally (no `_sealed_answer_key/`). This separation is the single biggest reason ground truth was 0.
