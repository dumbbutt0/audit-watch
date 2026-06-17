# P173 — Promotion review (guarded-downstream rule · F1 · F2)

Read-only promotion review. **No production wiring this phase** — actual promotion touches `scripts/*_audit.py`
+ the coverage-sweep/clear policy and is a separate, explicitly-approved implementation phase. This document
produces the verdict that decision needs and does NOT rubber-stamp P172's developer recommendation.

A standing fact that shapes every verdict: **F1/F2 are re-surface selectors** — they route a function to
deep-trace; they never confirm, route, or set severity. So their only cost is **deep-trace load**, and they
carry **no reportable-false-positive risk** (the campaign's `fabrication_rate=0` and reject-first precision are
untouched regardless of these verdicts).

## Measured criteria (reproduced from `recall_selectors.validate` + off-family probe)
| Metric | F1 (dynamic-weight lifecycle) | F2 (estimator-math) |
|---|---|---|
| answer-key recovery (quantamm) | **6/6** targets | 5/6 (≈6 effective; L-09 `rules/*` unmappable) |
| re-surface precision (rec / rec+FP) | **6/9 = 0.67** | 5/12 = 0.42 raw |
| re-surface rate (of 122 protocol_src fns) | 8/122 = 6.6% | 10/122 = 8.2% |
| expected deep-trace load — on-family (quantamm) | 8 fns | 10 fns (17 combined, deduped) |
| expected deep-trace load — **off-family** (basin/renzo/wildcat) | **0 / 0 / 0** | **0 / 0 / 0** |
| false-positive cost | 3 re-surface FPs (deep-trace work, not false reportables) | 7 raw (several are estimator surfaces labeled generically → effective lower) |
| coverage improvement (Track A only) | — | 8/44 → **19/44 touched** (F1+F2 combined, +11) |

**Key empirical result:** both selectors fire **0 hits off-family** (basin/renzo/wildcat) — their function-name
patterns (`setWeights`/`onSwap`/`computeBalance`; `*MathGuard*`/`*covariance*`/`pack*`) self-scope to the
Balancer-V3 dynamic-weight pool family. Promotion therefore imposes **bounded cost on-family and zero cost
off-family**.

## Promotion bar (scored)
| Criterion | Guarded-downstream | F1 | F2 |
|---|---|---|---|
| answer-key recovery | re-surfaces the biggest miss class (H-09/H-10/L-06) | 6/6 | 5–6/6 |
| re-surface precision | n/a (policy) | 0.67 ✅ | 0.42 ❌ |
| deep-trace cost | bounded (only converts in-scope-unproven-guard clears) ✅ | low (17 on-family, 0 off) ✅ | moderate (10 on-family) ⚠ |
| cross-corpus safety | corpus-agnostic ✅ | 0 off-family ✅ | 0 off-family ✅ |
| generalization evidence | structural (not pattern-fitted) ✅ | **in-sample only** ⚠ | in-sample ⚠ |
| precision-discipline risk | none (re-surface) ✅ | none (re-surface) ✅ | none (re-surface) ✅ |

## Verdicts

### Guarded-downstream rule → **PROMOTE**
Strictly conservative and corpus-agnostic: it only converts "guarded-downstream" strong-clears (where the guard
is itself in scope and unproven) into deep-passes. It can **never reduce recall or create a false confirm**;
its only effect is to route more in-scope-unproven-guard cases to deep-trace — exactly the fix for the largest
quantamm miss class. Highest-confidence promote. **Wiring target:** the strong-clear rationale check in the
coverage-sweep / `dependency_clear_utils.py` clear path — reject the clear and emit `needs_deep_pass` when the
named guard is in-scope and unproven.

### F1 dynamic-weight lifecycle selector → **PROMOTE (scoped + monitored)**
Clears the bar on every axis except generalization, which is **in-sample** (the patterns are Balancer-V3
dynamic-weight function names derived from quantamm's own answer key). This is acceptable to promote because:
(1) it is **re-surface-only** → no precision/confirmation risk; (2) it is **empirically self-scoping** (0
off-family hits) → promoting it cannot add noise to non-dynamic-weight audits; (3) deep-trace load is **low and
bounded** (≤8 on-family, 0 off). The worst case of a non-generalizing re-surface selector is "fewer future
recoveries," not production harm. **Conditions:** scope it to the dynamic-weight / Balancer-V3-pool family
(its names already enforce this); **monitor out-of-sample recall** on the next dynamic-weight corpus and review
the deep-trace load there. **Wiring target:** a new production lens `scripts/dynamic_weight_lifecycle_audit.py`
(family-gated), routing flagged update/pool-accounting fns to `needs_deep_pass`.
- *Cautious alternative (recorded, not chosen):* KEEP_EXPERIMENTAL until one out-of-sample dynamic-weight corpus
  confirms recall. Chosen PROMOTE because the promotion cost is provably low/zero and re-surface carries no
  precision risk; the cautious path delays a safe, high-value recall gain for evidence the re-surface design
  doesn't strictly require.

### F2 estimator-math selector → **KEEP_EXPERIMENTAL (refine only)**
Recall value is real (5–6/6), but **raw re-surface precision 0.42** and a broad estimator-family FP set make it
not production-ready. Not REJECT — refine, then re-review:
1. **Add a corrected-reference / edge gate:** require a concrete incorrect-result comparand (e.g. a
   division-before-multiplication that demonstrably changes the result, or a missing-clamp on a path that feeds
   a value), not merely an arithmetic-edge keyword match.
2. **Fix the generic-`affected` mapping** so true estimator surfaces (covariance/variance/pack) the answer key
   labels generically (`rules/*`) are credited as recovered, not miscounted as FPs — this alone raises measured
   precision.
3. **Narrow the edge set** (drop the broad `fixed_point_scaling` keyword; keep div-before-mul + signed-edge +
   normalization-without-reclamp).
Target: re-surface precision ≥ ~0.6 with recovery held at ≥5/6, then re-review for promotion.

## Recommended next action
A separate, explicitly-approved **production-wiring phase** for the two PROMOTE items (new family-gated
`*_audit.py` lens for F1 + the coverage-sweep clear-policy edit for the guarded-downstream rule), plus a
research-track **F2 refinement** phase. P173 itself wires nothing.

## Honesty notes
- "Recovery" = re-surface for deep-trace, not confirmation. Coverage is Track A (quantamm) only — never combined
  with the campaign refutation-correctness track.
- F1's 6/6 and F2's recovery are **in-sample** (validated on the corpus the patterns were derived from);
  out-of-sample recall is unmeasured and is the explicit monitoring condition on the F1 promotion.
- All cost/precision claims are re-surface metrics; exploit-grade precision is out of scope for re-surface
  selectors and is unaffected.
