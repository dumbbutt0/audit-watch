# P131 — FP Measurement (estimate)

FP of non-awarded findings cannot be objectively labeled without human verdicts (P129 limit), so this is an
**estimate** from source-grounded review; non-awarded confirmed-looking leads → **needs_human_review**.

## Composition of the +70 boosted candidates (the FP surface the boost adds)
| Class | n | FP verdict |
|---|---|---|
| awarded value_exit/oracle (recall arm) | 10 entries / 8 fns | productive (recall) |
| non-awarded **on-class** value/TVL/price logic | 37 | **not FP** — intended widening; valid-unawarded → human review |
| trivial getters / metadata | 12 | **noise** (fast clear, ~0 speculative-flag risk) |
| other view helpers | 8 | mostly fast clear |
| **mock contract** (`ConnectorMock2`) | 3 | **noise** (should be excluded) |

## Speculative-FP focus (P129 flagged `arithmetic` / `economic_attack`)
- The boost re-ranks **existing read/value-getter logic**; it adds **no new state-mutating call paths**. The
  mechanism that produces speculative arithmetic/economic FPs (complex state transitions, fund movement under
  contrived preconditions) is **not introduced**.
- On-class boosted functions that an arithmetic/economic specialist would examine (e.g.
  `CompoundConnector._getPositionTVL`'s `positiveBalance - negativeBalance`) are **legitimate** leads, not
  speculative noise.
- ⇒ **No evidence the boost inflates speculative `arithmetic`/`economic_attack` FPs.** This is the key
  reassurance P130 lacked.

## Quantified noise (trimmable without losing recall)
- Trivial getters (12) + mock (3) ≈ **15/70 (21%)** of the added volume is low-value noise.
- The remaining ~79% is productive (awarded recall + on-class value logic worth human review).

## Precision metrics (objective, ground-truth loop) — unchanged
`compute_metrics` FP 0.143 / over-severity 0.267 are **invariant** (they read beanstalk ground truth, not the
noya manifest). The boost cannot regress the measured precision loop; the only real precision risk is the
downstream reviewer-time/FP cost of the +44% volume, estimated above as mostly benign with ~21% trimmable noise.

## Recommended FP trims (for a follow-on, not implemented here)
1. **Exclude mock contracts** from boosting/scope: broaden the glob `Mock*.sol` → also catch `*Mock*.sol`
   (`ConnectorMock2.sol`). Removes 3 noise boosts; general fix.
2. **Don't boost trivial bodies:** require the helper to have an external call OR a non-trivial body (e.g.
   exclude single-`return`/empty-array getters). Would remove ~12 noise boosts while keeping all 8 awarded
   (which all have real computation/external calls).
