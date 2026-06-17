# P199 — over-HIGH failure taxonomy

Each over-HIGH case mapped to ≥1 root cause. The **structural** cause applies to all; the **case** causes explain
the specific over-rating.

## Structural root cause (applies to ALL 8 + the whole dataset)
**`verdict-is-threat-ceiling-no-calibration-step`** — `deep_trace.md`'s verdict enum is
`CRITICAL_THREAD/HIGH_THREAD/MEDIUM_THREAD/DEAD_END/NEEDS_MORE_CONTEXT`, a worst-case *threat* grade. There is no
downstream step that demotes the ceiling to a *proven* severity. Result: 29/30 verdicts ≥HIGH; 1 below-HIGH. This
is the dominant cause — without it, the case-specific causes below would be caught.

## Case root causes
| case | surface | root causes |
|---|---|---|
| 1 | quantamm afterUpdate | `griefing/DoS-as-theft`; `temporary-mismatch-as-permanent`; `clean-code over-enumeration` |
| 2 | quantamm UpdateWeightRunner._getData | `griefing/DoS-as-theft` (liveness rated High — the canonical P186/P187 M-06) |
| 3 | quantamm MultiHopOracle._getData | `loss-magnitude-not-proven` (dust precision) |
| 4 | ark withdrawTokens | `griefing/DoS-as-theft`; `temporary-mismatch-as-permanent` (stuck≠stolen) |
| 5 | panoptic _getRequiredCollateral | `local-loss-as-protocol-wide`; `loss-magnitude-not-proven` |
| 6 | panoptic twapEMA | `loss-magnitude-not-proven` (bounded mispricing) |
| 7 | centrifuge IM-04 | `griefing/DoS-as-theft`; `public-entry-reachability-assumed` + `wrapper/callee confusion` (M-04, = P198 FM-2) |
| 8 | centrifuge RM-12 | `local-loss-as-protocol-wide` (compliance ≠ insolvency); `invariant-break-as-insolvency` |

## Root-cause frequency (case-level)
- `griefing/DoS-as-theft` — 4 (cases 1,2,4,7) — **most common case cause**
- `loss-magnitude-not-proven` — 3 (3,5,6)
- `temporary-mismatch-as-permanent` — 2 (1,4)
- `local-loss-as-protocol-wide` — 2 (5,8)
- `clean-code over-enumeration` — 1+ (1; broadly P198 FM-3)
- `public-entry-assumed` + `wrapper/callee confusion` — 1 (7 = FM-2)
- `invariant-break-as-insolvency` — 1 (8)
- `NEEDS_HARNESS-as-severity-substitute` — observed broadly (verdicts stay HIGH while routing disputes to
  NEEDS_HARNESS rather than letting unproven magnitude lower the grade)

## FM-2 verdict (per the spec)
Wrapper/callee confusion appears in **exactly 1** over-HIGH case (centrifuge M-04). It is **not** a recurring
severity cause — included as a calibration **data point**, not promoted to a primary severity finding. (It remains
a real *recall/locus* issue from P198, just not a severity-skew driver.)

## Conclusion
The over-HIGH skew is **one structural gap** (no calibration step) expressed through a small, consistent set of
case patterns dominated by **griefing/DoS-rated-as-theft** and **unproven-loss-magnitude**. This is fixable with a
single additive severity gate (design note: `SEVERITY_GATE_PROPOSAL.md`), not a scatter of detector patches.
