# P199 — calibration scorecard (read-only, cross-corpus)

Dataset: **30 blind verdict rows** across **6 corpora** (quantamm P186 ×5 functions, zaros/revert-lend/panoptic/ark
P189 ×13, centrifuge P198 ×12). Awarded severity from the answer-key-id prefix (H/M/L). Built from existing
artifacts only.

## Verdict-tier distribution (blind)
| tier | n | % |
|---|---|---|
| CRITICAL_THREAD | 6 | 20.0 |
| HIGH_THREAD | 23 | 76.7 |
| MEDIUM_THREAD | 1 | 3.3 |
| (≥ HIGH) | **29** | **96.7** |

**Only 1 of 30 blind verdicts is below HIGH.** The verdict is, in practice, a near-constant HIGH/CRITICAL ceiling.

## Over-HIGH — the confound-free signal (Medium/Low-awarded surfaces rated ≥ HIGH)
| | n | over-HIGH | rate |
|---|---|---|---|
| Medium/Low-awarded surfaces | 9 | **8** | **88.9%** |
| of which quantamm | 3 | 3 | 100% |
| of which panoptic | 2 | 2 | 100% |
| of which ark | 1 | 1 | 100% |
| of which centrifuge (mapped) | 3 | 2 | 66.7% |

**Controlled corpus (centrifuge, awarded 0 High / 8 Medium): 11/12 surfaces rated ≥ HIGH.** With zero real Highs
in the codebase, a ≥HIGH verdict cannot correspond to a real High — this is the cleanest single-corpus evidence.

## Confound excluded (so the rate is not inflated)
**High-awarded surfaces rated ≥ HIGH: 12/12 (100%).** P189 deliberately sampled High-priority deep-run misses, so
its HIGH/CRITICAL verdicts on those are **correct, not over-rating**. They are excluded from the over-HIGH rate.
There were **zero false-LOW** cases (the stack never under-rated a real High).

## The one correctly-graded Medium
`centrifuge / IM-06 → M-07` (rounding-direction in `_calculateTrancheTokenAmount`) was the **only** MEDIUM_THREAD
verdict in the entire dataset — and it correctly matched the Medium award. Signal: the stack *can* grade Medium
when the mechanism is intrinsically bounded (precision/rounding), but essentially never does otherwise.

## Mechanism volume
Avg selected mechanisms per candidate ≈ 1.9 (+1–3 unresolved each) — aggressive enumeration (good for recall,
contributes to the clean-code over-flagging seen in P198 FM-3).

## Headline
The over-HIGH skew is **systematic across corpora** (88.9% on Medium/Low-awarded; 11/12 on the controlled
all-Medium corpus; 29/30 verdicts ≥HIGH; 1 below-HIGH). **Crucial framing:** the blind `verdict` is a *worst-case
threat ceiling* by `deep_trace.md` design, not a calibrated final severity — there is **no severity-calibration
step** between the threat ceiling and a graded output. The gap is a **missing gate**, not a wrong verdict.
