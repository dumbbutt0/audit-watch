# Empirical test — does filling coverage gaps increase recall?

Eval-only. Recall measured against each program's answer key (scored sheet). `recall_ceiling` = fraction of awarded findings whose locus file was examined (the most recall any reasoning could achieve at that coverage); `coverage_gap_misses` = awarded findings in UNREAD files (guaranteed misses, independent of reasoning).

## (A) Coverage decomposition

| program | awarded | recall | ceiling@coverage | recalled | reasoning-gap miss | COVERAGE-GAP miss | %awarded lost to coverage |
|---|---|---|---|---|---|---|---|
| cap-2025-07-eval | 10 | **0.4** | 1.0 | 4 | 6 | **0** | 0% |
| numa-2024-12-eval | 16 | **0.0** | 0.25 | 0 | 4 | **12** | 75% |

## (B) Coverage ablation — recall vs # catch-bearing files covered (forward = filling gaps)

- **cap-2025-07-eval** (catches in 4 files): recall as those files are covered: 0f:0.0 → 1f:0.1 → 2f:0.2 → 3f:0.3 → 4f:0.4. I.e. ALL of its 0.4 recall came from covering those files; not covering them → recall 0.0.
- **numa-2024-12-eval**: 0 catches → ablation flat at recall 0.0 (its recall was capped at the ceiling 0.25 by coverage: 12/16 findings were in unread files).

## Conclusion

- **Coverage strangles recall.** numa-2024-12-eval: 75% of awarded findings sat in UNREAD files → recall ceiling forced to 0.25 and actual recall 0.0, regardless of reasoning quality. Those misses are recoverable ONLY by filling coverage.
- **Filling coverage to the loci removes the coverage-gap miss category.** cap-2025-07-eval: coverage reached every awarded locus (0 coverage-gap misses), lifting the ceiling to 1.0; the remaining misses are now purely reasoning (addressable by prompt sections, not coverage).
- **Ablation proves causality:** removing the catch-bearing files drops recall monotonically to 0.0; equivalently, covering them is what produced the recall. Coverage is necessary for recall.
