# P201 — P200 failure extraction (from P200 artifacts only)

Read from `p200_severity_gate_validation/{metrics.json, CALIBRATED_SCORECARD.md, FAILURE_CASES.md,
OFFLINE_SEVERITY_CALIBRATION.json}`. These are the specific P200 gate failures the refined gate must fix.

## Failure matrix
| case | mechanism | blind verdict | P200 calibrated | awarded sev | why misclassified | what High would have required |
|---|---|---|---|---|---|---|
| predy-09 / **M-04** | Chainlink `latestRoundData` no staleness/round-completeness | HIGH_THREAD | **HIGH_CONFIRMED** | **Medium** | P199 oracle→insolvency=High rule applied blanket; missing-check visible but exploit magnitude/liquidation-path **not proven** | proven permissionless path to *material* insolvency / wrongful-liq / extractable value, not just "no staleness guard" |
| predy-10 / **M-03** | negative-tick rounding (integer truncation) | HIGH_THREAD | **HIGH_CONFIRMED** | **Medium** | surface graded High on the *primary* (TWAP→spot manipulation, unawarded); the awarded mechanism (M-03) is a bounded precision bug | precision error must **compound/amplify to material loss**, not bounded per-call rounding |
| predy-07 / **M-04/M-08** | isLiquidatable oracle usage (overlap) | HIGH_THREAD | **HIGH_CONFIRMED** | **Medium** | same blanket oracle→High; loose-locus oracle overlap rated High | same as M-04: proven material insolvency path |
| predy-06 / **H-02** | liquidator dodges negative-margin compensation → loss to protocol (awarded **High**) | HIGH_THREAD | **MEDIUM** (surface) | **High** | **per-surface** grading: H-02 was selected[1]; surface label driven by primary M-06 (recipient-revert DoS, Medium) → genuine High **folded** | per-**mechanism** grading: grade H-02 on its own (theft/insolvency-to-protocol → High) regardless of the Medium primary |
| predy-08/12/16 | unchecked-hook / settlement-accounting / pool-negative | HIGH_THREAD | **HIGH_CONFIRMED** | — (unawarded) | recall false-positives the severity gate cannot fix; inflate the High bucket | n/a — recall/precision issue, out of severity-gate scope |

## Root causes → refinement targets
1. **Blanket oracle→High** (predy-07/09): replace with **evidence-conditional** oracle class (B): High only on a
   *proven, material* insolvency/wrongful-liq/extractable path; else Medium; Harness if depends on runtime
   liquidity/oracle-config/external market.
2. **Blanket precision treatment** (predy-10): replace with **magnitude-dependent** precision class (C): High only
   if it compounds/amplifies to material; Medium if bounded/dust; Harness if magnitude unknown.
3. **Per-surface folding** (predy-06/H-02): grade **per mechanism**; a Medium primary must never hide a High
   secondary. Scoring preserves per-mechanism labels.
4. **Mechanism substitution inflating High** (predy-10 primary TWAP): grading per-mechanism + requiring the High
   evidence per-mechanism reduces crediting High to an unawarded mechanism on a Medium-awarded surface.
5. Recall FPs (predy-08/12/16) are explicitly **out of scope** for the severity gate (a recall/precision matter).

## Quantified P200 baseline (to beat)
Over-HIGH on matched awarded-Medium: ceiling **4/5 → calibrated 3/5** (only 1 fixed). Genuine-High found by
mechanism: 1 (H-02), graded Medium at surface level (under-graded). The refined gate must (a) cut over-HIGH on the
precision/DoS classes it can, (b) **not** demote a separately-found awarded High, (c) be honest that oracle is
untested here.
