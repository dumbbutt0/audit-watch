# P276 — METRICS_SUMMARY

Machine-readable: `outputs/corpus_metrics.json`.

## Corpus funnel (144 locus-mapped awarded H/M across 7 contests)
| stage | value | target | status |
|---|---|---|---|
| advisory-surfaced | **68.1%** | ≥70% | ~ (just under) |
| class-routed | **39.6%** | ≥50% | below (R1 target) |
| locus-triaged | 39.6% | — | — |
| mechanism-generated | **39.6%** | ≥30% | **met** |
| chain-completed / PoC-supported / exact | NOT_SAMPLED corpus-wide | 10–20% | sampled via P274 (2 EXACT) / P275 |
| missed | 31.9% | — | — |
| **severe concluded/reportable FP** | **0** | 0 | **met** |

## first_failed_stage
COMPLETION_GAP 57 (expected tail) · COVERAGE_CLASS_GAP 41 · RECALL_GAP 30 · MANIFEST_GAP 15 · TARGET_SCOPE_GAP 1.

## Supplementary
- Count-only corpora (title-only keys): swan 65 + quantamm 40 = 105 awarded H/M (severity counted, locus N/A).
- Pass A: 206 advisory candidates across 12 audits, all guards 0.
- Advisory-only non-awarded survivors: 43 (PoC-queue pressure; 0 severe FP).

## Interpretation
Upstream recall is healthy (surfaced ~68%, mechanism-generated ~40% — note generation tracks routing here because the
harness emits mechanisms for every surfaced candidate). The binding actionable gap is **class routing** (surfaced→routed
drop), then **recall depth** and the **completion/PoC throughput tail**. Exact-recovery % stays low (expensive PoC) —
expected and acceptable per the plan; the blind P274 run is the exact-recovery existence proof.
