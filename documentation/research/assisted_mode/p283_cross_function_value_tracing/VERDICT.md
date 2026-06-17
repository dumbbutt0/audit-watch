# P283 — VERDICT

## Verdict: **B — CROSS_FUNCTION_TRACE_PROMISING_NEEDS_REFINEMENT**

## Core question
Can bounded cross-function tracing lift value-class candidates to READY without reintroducing false READYs — and where it
can't, localize why? **Answer:** it lifts 0 *without* any false READY, and it localizes the remaining blocker precisely:
the violation is semantic (corrected-reference / data-flow), not a lexical anomaly even across function boundaries.

## Why B (not A)
- **Newly lifted: 0.** A requires ≥2 newly lifted OR a clear source-backed supply reason. The supply reason is clear and
  source-backed (semantic violation, no lexical anomaly), and tracing genuinely deepens evidence (35 TRACE_FOUND) and
  sharpens the backlog — but lift is 0, so this is B, not A.

## Why not C
- No unsupported/noisy READYs. The only anomalies found were false; **none produced a READY** (caught by D1 precedence,
  class gating, the readiness dimensions, and the `**` fix). Severe concluded/reportable FP = 0.

## Scorecard vs the A-bar
| criterion | result |
|---|---|
| ≥2 newly lifted OR clear source-backed supply reason | supply reason ✔ (semantic violation); lifts 0 |
| no P281/P282 false-READY regressions | ✔ (status dist. unchanged except a +1 precision gain) |
| L2Governor.execute stays READY / PASS_SUPPORTED | ✔ (PoC re-run 2/2 PASS) |
| audit finds no hallucinated core | ✔ |
| generic transfer/write doesn't create READY | ✔ (test + audit) |
| severe FP = 0 | ✔ |
| tests green | ✔ |

## Net effect of P283
- **Precision integrity improved:** comment-stripping + `**` exponent exclusion removed two classes of false anomaly;
  one candidate (`PanopticPool:_burnOptions`) that had passed the value-flow gate on a false anomaly was correctly
  demoted to NEEDS_VALUE_FLOW_EVIDENCE.
- **Evidence depth improved:** 35 value-class candidates now carry a resolved cross-function trace path instead of an
  opaque "value-flow out of span".
- **Backlog sharpened:** the dominant blocker is now named — `value_flow_present_but_no_anomaly` → corrected-reference /
  data-flow (SSA).

## Production authority
**WITHHELD.** Research-only, advisory, un-wired, default-off, fail-closed throughout.

## Next (per plan)
Implement **corrected-reference / data-flow (SSA) derivation** (the violation is a value-relationship vs a reference,
not a keyword) → re-map → small PoC sweep on the trustworthy READY set → fresh blind target.
