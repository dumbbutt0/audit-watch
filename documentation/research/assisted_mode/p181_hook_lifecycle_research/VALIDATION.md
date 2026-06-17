# P181 — Research F3 hook-lifecycle selector: VALIDATION

**Question:** is the P175 `hook_lifecycle` family worth production promotion? Built + measured **research-only**
(un-wired) on quantamm, with a baseline (unique vs shipped lenses), exact-function specificity, and a
cross-corpus leakage check. Reproduce: `python …/p181_hook_lifecycle_research/validate_hook_lifecycle.py`.

## Verdict: **REJECT for production promotion** (family real but fully subsumed by shipped lenses)

The decisive number is **unique recovery = 0/7**. Every F3 recovery on quantamm is already surfaced by the
shipped F1 (`dynamic_weight_lifecycle`) AND math_estimator lenses. A dedicated F3 selector adds **zero
incremental recall** while adding deep-trace load and false positives.

## Quantamm results
- **Total recovery: 5/7** (H-07, M-03, M-05, M-15, M-18) — via two functions: `onAfterRemoveLiquidity` and
  `afterUpdate`.
- **Unique recovery vs shipped F1/math_estimator: 0/7.** (table below)
- **Missed: M-10** (`LPNFT._update` — thin override, no accounting mutation in body) and **M-11**
  (`onRegister` — "missing initialize" is a missing-function bug, structurally invisible to a classifier of
  existing functions). So F3 does not even close the true gap.
- **Re-surface count: 7 functions. Function precision: 28.6%** (2 of 7 surfaced functions are awarded sites).
  **5 false-positive functions:** `LPNFT.mint`, `LPNFT.burn`, `addLiquidityProportional`,
  `removeLiquidityProportional`, `onAfterSwap`.

### Per-finding unique-recovery baseline (the additions to this phase)
| finding | function | already by F1? | already by math_estimator? | newly by F3? | **unique?** |
|---|---|---|---|---|---|
| H-07 | UpliftOnlyExample.onAfterRemoveLiquidity | yes | yes | yes | **no** |
| M-03 | UpliftOnlyExample.afterUpdate | yes | yes | yes | **no** |
| M-05 | UpliftOnlyExample.onAfterRemoveLiquidity | yes | yes | yes | **no** |
| M-10 | LPNFT._update | no | no | **no (missed)** | no |
| M-11 | UpliftOnlyExample.onRegister | no | no | **no (missed)** | no |
| M-15 | UpliftOnlyExample.onAfterRemoveLiquidity | yes | yes | yes | **no** |
| M-18 | UpliftOnlyExample.afterUpdate | yes | yes | yes | **no** |

All recoveries are exact-function (good specificity), but **all are duplicates** of the shipped lenses.

## Cross-corpus leakage (architecture transfer)
| corpus | in-scope | surfaced | % | note |
|---|--:|--:|--:|---|
| quantamm (Balancer hooks) | 205 | 7 | 3.4% | on-family |
| zaros | 506 | **1** | 0.2% | near-zero leakage |
| revert-lend | 181 | **0** | 0.0% | zero leakage |
F3 is **excellently scoped** — it does NOT explode outside Balancer-hook architectures. This is its one strong
property, but it is not sufficient for promotion given 0 unique recovery.

## Judged by the F1 promotion standard + P181 rubric
| criterion | F1 (promoted) | F3 | |
|---|---|---|---|
| bounded family | yes | yes | ✓ |
| bounded deep-trace load | yes | yes (7) | ✓ |
| clear source signals | yes | yes | ✓ |
| low architecture leakage | yes | yes (0.2% / 0%) | ✓ |
| **most recoveries unique** | yes (recovered net-new) | **0/7 unique** | ✗✗ |
| exact-function recovery | — | 5/7 exact but duplicate | partial |
| function precision | — | 28.6% (5 FP) | ✗ |

- **PROMOTE** requires ≥5/7 *exact* (✓) + bounded load (✓) + minimal leakage (✓) + **most recoveries unique**
  (✗, 0/7). The unique criterion fails outright → not PROMOTE.
- **REJECT** triggers on "mostly duplicate recoveries" — F3 is **100% duplicate** → REJECT.
- (KEEP_EXPERIMENTAL would require it to be "useful"; a 100%-subsumed selector is not.)

## The lesson (consistent with P176 / P179)
The quantamm hook-lifecycle "gap" was **not a discovery gap** — the shipped F1 + math_estimator lenses already
re-surface `onAfterRemoveLiquidity` and `afterUpdate`. The recall was lost downstream (triage/routing), not at
detection. The two findings F3 *doesn't* duplicate (M-10 NFT-transfer-DoS, M-11 missing-initialize) it also
**cannot recover** (thin override / missing function), so a dedicated hook lens closes nothing.

## Recommendation
- **Do NOT promote F3.** Mark the P175 roadmap `hook_lifecycle` row as **"covered by existing F1 + math_estimator
  (re-surface); remaining M-10/M-11 are not pattern-detectable"** rather than "needs new selector".
- The prior (KEEP_EXPERIMENTAL, decided by leakage) is **refuted in the stronger direction**: leakage is fine,
  but the determining factor turned out to be **unique recovery = 0** — REJECT.
- Keep `scripts/research/hook_lifecycle_selector.py` as an un-wired research artifact (documentation of the
  evaluation); it is not a promotion candidate.
