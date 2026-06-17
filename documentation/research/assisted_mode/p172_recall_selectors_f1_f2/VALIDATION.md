# P172 — F1/F2 recall selectors + guarded-downstream rule: validation on quantamm

Research-only selectors (`scripts/research/recall_selectors.py`), un-wired, validated **offline** against the
quantamm answer key. No production detector / coverage-sweep / routing change. Promotion into the production
recall pipeline is a separate human decision; this report provides the promote-vs-experimental recommendation.

**These are RE-SURFACE selectors** (Track A recall only): a "recovered" miss means the selector re-surfaced the
answer-key surface for deep-trace — it does **not** auto-confirm the bug. "New false positives" = re-surfaced
functions with no answer-key finding (the deep-trace cost). Track A recall is never combined with Track B.

## Recovered answer-key misses
| Selector | Targets | Recovered | Re-surface precision (rec / rec+FP) |
|---|---|---|---|
| **F1 dynamic-weight lifecycle** | H-04, M-04, M-08, M-09, M-12, M-14 | **6/6** (all) | **6/9 = 0.67** |
| **F2 estimator-math** | H-09, H-10, H-11, L-06, L-09, M-07 | **5/6** (H-09, H-10, H-11, L-06, M-07) | 5/12 = 0.42 (raw) |

- **F1** re-surfaced every lifecycle target — `QuantAMMWeightedPool.setWeights/onSwap/computeBalance` and
  `UpdateWeightRunner` — exactly the functions the coverage sweep over-cleared.
- **F2** re-surfaced 5/6 by exact-affected match. **L-09's `affected` is the generic `rules/*`**, which can't be
  credited by contract-name matching — but the selector **did** hit `QuantammVarianceBasedRule.
  _calculateQuantAMMVariance` (the L-09 single-asset-variance surface), so L-09 is effectively re-surfaced too
  (counted as an FP only because the answer key labels it generically). Effective F2 recovery ≈ 6/6.

## New false positives (deep-trace cost)
- **F1 (3):** `QuantAMMWeightedPool._getNormalisedWeightPair`, `QuantammVarianceBasedRule.
  _calculateQuantAMMVariance`, `UpdateWeightRunner.setWeightsManually` — all weight/estimator-adjacent; modest.
- **F2 (7):** `QuantAMMStorage.quantAMMPackEight32 / quantAMMUnpack32 / quantAMMUnpack32Array`,
  `QuantammCovarianceBasedRule._calculateQuantAMMCovariance / _setIntermediateCovariance`,
  `QuantammGradientBasedRule._calculateQuantAMMGradient`, `QuantammVarianceBasedRule._calculateQuantAMMVariance`.
  **Several of these are the estimator-math family surfaces the answer key references generically** (M-07 pack,
  H-11 covariance, L-09 variance) — so the *effective* F2 FP count is lower than 7; the raw 0.42 is a
  conservative lower bound.

## Should-have-found coverage improvement (Track A only)
- **Before:** 8/44 touched (P171). **After (F1+F2 re-surface):** **19/44 touched** (+11 distinct surfaces:
  H-04, M-04, M-08, M-09, M-12, M-14, H-09, H-10, H-11, L-06, M-07).
- exact-confirm count is unchanged by this phase (re-surface ≠ confirm); the gain is in *what reaches
  deep-trace*, which is precisely where the 36 misses were lost.

## Precision impact
- **Exploit/runtime precision is unaffected** — these selectors do not confirm or route; the campaign's
  `fabrication_rate=0` and reject-first discipline are untouched. They only change which surfaces reach a
  deep-trace.
- **Re-surface precision:** F1 0.67, F2 0.42-raw (higher effective). The F2 FP cost is concentrated in the
  estimator-math family (pack/covariance/variance/gradient) — tightenable with a corrected-reference edge-gate.

## Guarded-downstream rule
`guarded_downstream_flag` returns `do_not_clear=True → needs_deep_pass` when a "guarded downstream" clear rests
on a guard that is itself **in scope and unproven** — exactly the quantamm over-clearance that lost
H-09/H-10/L-06 (the sweep cleared rule-math "because `_guardQuantAMMWeights` clamps downstream", but that guard
was in scope and unproven). The rule re-surfaces those for deep-trace; it does not mutate the production sweep.

## Promote vs keep-experimental
| Item | Recall effect | FP cost | Recommendation |
|---|---|---|---|
| **F1 dynamic-weight lifecycle** | +6 (all targets) | low (3, precision 0.67) | **PROMOTE** (highest leverage, clean) |
| **guarded-downstream rule** | re-surfaces the biggest miss class (H-09/H-10/L-06) | 0 new lens (policy) | **PROMOTE** (process fix) |
| **F2 estimator-math** | +5 (≈6 effective) | higher (raw 0.42; math-family) | **KEEP_EXPERIMENTAL** → promote after adding a corrected-reference / edge-tightening gate to cut estimator-family FPs |

(F3 / dashboard / submission / routing / broad taxonomy: not implemented, per scope.)

## Honesty notes
- Promotion to production (`*_audit.py` lens + sweep-policy edit) is **not** done here — separate human decision.
- "Recovered" = re-surfaced for deep-trace, not confirmed. Coverage is Track A (quantamm) only.
- F2's 0.42 raw precision overstates the FP cost (generic `rules/*`/pack `affected` strings prevent crediting
  several true estimator surfaces); a tighter mapping or edge-gate would raise it.
