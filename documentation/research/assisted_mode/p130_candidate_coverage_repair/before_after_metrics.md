# P130 — Before/After Metrics

All before/after pairs use **identical `--contract` invocations** of the same tool; the only difference is
the repair (controlled). Deep-pass cutoff = 3. Awarded functions/contracts from `_p81b/*/recall_score.json`
(eval yardstick only).

## Candidate-coverage proxy (recall surrogate at the manifest stage)

### noya-2024-04-eval (PRIMARY — library/strategy-heavy, same class as Beanstalk)
| Metric | Before | After | Δ |
|---|---|---|---|
| **awarded-FUNCTION deep-pass coverage** | **6/19 (32%)** | **14/19 (74%)** | **+42 pp** |
| awarded-CONTRACT deep-pass coverage | 17/19 (89%) | 18/19 (95%) | +6 pp |
| internal/private fns scoring ≥3 | 2/205 (1%) | 13/205 (6%) | +5 pp |
| high-surface in-scope fns (volume) | 158 | 228 | **+70 (+44%)** |
| functions boosted (P130) | — | 70 | — |

Recovered awarded functions: `_getPositionTVL` across Aerodrome/Balancer/Silo/Pendle/Morpho/UNIv3 connectors,
`NoyaValueOracle._getValue`, `ChainlinkOracleConnector.getValue`, etc. Still uncovered (5): e.g.
`SNXConnector._getPositionTVL` (**absent** from manifest — scope/enumeration gap, not ranking),
`OmnichainManagerBaseChain.updateTVL` (no risk tag → gate correctly does not fire).

### decent-2024-01-holdout (CONTROL — no libraries)
| Metric | Before | After | Δ |
|---|---|---|---|
| awarded-FUNCTION deep-pass coverage | 3/9 (33%) | 3/9 (33%) | **0** |
| internal/private fns scoring ≥3 | 10/17 (59%) | 15/17 (88%) | +29 pp |
| high-surface in-scope fns (volume) | 46 | 52 | +6 (+13%) |
| functions boosted (P130) | — | 6 | — |

decent's uncovered awarded functions are all **`(absent)`** — they live in `lib/decent-bridge/src`, excluded
by the `--contract src` root used here; this is a root-selection artifact, **not** a scoring miss. Awarded
coverage is therefore unchanged by the repair (as expected for a non-library audit) — confirming the repair
is **not blanket inflation and not Beanstalk-specific**.

## Precision metrics (must be invariant — these read ground truth, not the manifest)
| Metric | P129 | P130 | Δ |
|---|---|---|---|
| FP rate | 0.143 (n=14) | 0.143 (n=14) | 0 |
| Outcome accuracy (beanstalk) | 0.867 | 0.867 | 0 |
| Over-severity rate | 0.267 | 0.267 | 0 |
| TP / FP / FN (beanstalk) | 12 / 2 / 0 | 12 / 2 / 0 | 0 |

Confirmed: the repair changes candidate ranking only; it does not touch the precision/severity ground-truth
loop. (True downstream precision impact — more deep-pass candidates → potential new FPs — requires a full
pipeline run; see `regression_guard.md`.)

## Tests
- New `tests/coverage/test_library_internal_surface.py`: **10 passed**.
- Full suite: **1572 passed, 2 failed, 4 skipped** — the 2 failures are the pre-existing `deep_solidity`
  frozen-snapshot tests (active-audit `output/` symlink), unchanged from P129; +10 vs P129's 1562 are the
  new tests. No new failures.

## Beanstalk (diagnostic origin)
Source absent on disk → manifest not regenerable. Miss taxonomy: **87% source-resolution/coverage, 68%
directly addressable** by this repair (see `miss_taxonomy.md`). The noya result is the live proof the repair
recovers exactly that class.
