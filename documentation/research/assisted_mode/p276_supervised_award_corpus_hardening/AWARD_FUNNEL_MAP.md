# P276 — AWARD_FUNNEL_MAP (Pass B, key-guided)

Every awarded H/M finding in the **7 locus-mapped** contests assigned a furthest funnel stage + `first_failed_stage`.
Mapper: `scripts/research/p276_award_funnel_map.py` (award-key adapter handles all corpus schemas). Maps under
`outputs/<audit>/award_funnel_map.json`.

## Per-contest (locus-mapped: 144 awarded H/M)
| contest | awarded H/M | stage tally |
|---|---|---|
| zaros | 51 | MECHANISM_GENERATED 23 · ADVISORY_SURFACED 18 · MISSED 10 |
| revert-lend | 31 | MECHANISM_GENERATED 19 · ADVISORY_SURFACED 4 · MISSED 8 |
| panoptic | 22 | MECHANISM_GENERATED 7 · ADVISORY_SURFACED 3 · MISSED 12 |
| recall | 13 | ADVISORY_SURFACED 8 · MISSED 3 · MECHANISM_GENERATED 2 |
| ark | 11 | MISSED 9 · ADVISORY_SURFACED 2 |
| hybra | 10 | ADVISORY_SURFACED 5 · MISSED 4 · MECHANISM_GENERATED 1 |
| silo | 6 | MECHANISM_GENERATED 5 · ADVISORY_SURFACED 1 |

## Corpus funnel (144 awarded H/M)
- **advisory_surfaced: 68.1%** · class_routed: 39.6% · locus_triaged: 39.6% · mechanism_generated: 39.6% ·
  **missed: 31.9%**.
- chain_completed / poc_supported / exact: **NOT_SAMPLED corpus-wide** (completion/PoC is the expensive tail; the
  sampled datapoints are P274 gondi = 2 EXACT awarded recoveries with runtime PoCs, and P275 ronin = partial — those
  blind runs are the completion/PoC sample for the mechanism→exact bridge).

## first_failed_stage (the repair signal)
`COMPLETION_GAP 57` (reached MECHANISM_GENERATED, completion/PoC not sampled — expected tail) ·
`COVERAGE_CLASS_GAP 41` (surfaced but class not routed) · `RECALL_GAP 30` (in manifest, not surfaced) ·
`MANIFEST_GAP 15` · `TARGET_SCOPE_GAP 1`.

Reading: above the completion tail, the binding upstream gaps are **coverage-class routing (41)** then **recall depth
(30)** then **manifest enumeration (15)** — exactly the "deeply routes only a small subset" symptom. These drive the
repair backlog.

## Count-only contests (no locus info)
swan (65) + quantamm (40) = 105 awarded H/M recorded `DUPLICATE_OR_REPORT_ONLY_AMBIGUITY` (title-only award keys);
counted, not funnel-mapped. Backlog R6 = enrich these keys.
