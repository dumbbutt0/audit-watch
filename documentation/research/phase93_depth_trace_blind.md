# Phase 93 — Sixth fresh sealed-key blind run (P91 selection + P92 depth-trace v3)

## Goal
Test whether P92's depth-trace v3 improves conversion depth on localized mechanisms while holding the
calibrated 0 severity FP (gate frozen `193abf9f`). Confirmation run, not a repair.

## Subject & sealed-key discipline
- **ramses-exchange-2024-10** (Code4rena), commit `1ba89267…`, **10 in-scope contracts** (~3605 lines;
  UniV3-fork CL pool + libraries + gauge + periphery). Fresh; multi-contract; arithmetic/index/lifecycle.
- **Sealed-key PRESERVED:** metadata → leads → C-chain bundles → depth-trace outputs → severity outputs →
  `prekey_freeze.json` (`answer_key_opened=false`) all frozen **before** the findings repo was cloned. No web
  search; `4naly3er-report.md` / README never opened.

## Pipeline applied
P91 selection: lens → 43 leads → **top-16 ∪ per-contract top-2 floor + 3 controls = 21**, `inclusion_source`
tagged (floor added 4 from contracts the top-16 missed). **NOT_RUN = 0.** Each lead run through deep_pass with
the **v3 depth-trace** + `localized_depth_trace` on localized/uncertain mechanisms + maximal_consequence_check +
hygiene + (for promotions) isolated adversarial + the frozen gate.

## C-chain result (frozen pre-key)
- **0 kept promotions.** 14 REJECTED, 7 NEEDS_CONTEXT — **all well-formed** (named dependency + next step; 0
  bare abstains). Safety 0/0/0/0. **0 depth-trace false escalations.**
- Depth-trace records: GaugeV3.cachePeriodEarned → traced REJECT; GaugeV3.notifyRewardAmount → traced REJECT
  (balance-diff handles fee-on-transfer); FeeCollector.collectProtocolFees → well-formed NEEDS_CONTEXT (named
  out-of-scope FeeDistributor dependency).

## Scoring vs key (0 High + 2 Medium — hardened, low-density)
| Axis | Result |
|---|---|
| Sealed-key · NOT_RUN | preserved · 0 ✅ |
| Safety (4 axes) | 0/0/0/0 ✅ |
| **Severity FP after gate** | **0** ✅ |
| Controls | 3/3 + governance setters rejected ✅ |
| **localized_depth_trace false escalations** | **0** ✅ |
| **Conversion** | **0 CLEAN_HIT / 0 STRONG_PARTIAL** ⚠ |

- **M-02** (`RamsesV3Pool.flash`: `pFees0 = paid0 / feeProtocol` instead of `* feeProtocol / 100` → protocol
  gets 1/80 not 80%): my v3 abstain on `RamsesV3Pool.flash` **named the exact awarded function + next step
  ("read flash body")** — v3's process pointed right at it, but I **abstained instead of executing the in-scope
  next-step read** (a 10-line body with a textbook arithmetic miscalc — precisely v3's "exact arithmetic
  expression" target). Near-miss, not converted.
- **M-01** (GaugeV3 inflated rewards when a period is skipped — bug in the pool's `periodCumulativesInside`,
  reached via `positionPeriodSecondsInRange`): I localized + traced GaugeV3 reward, but the **trace stopped at
  the in-scope pool staticcall boundary and REJECTED**, missing the pool-side skipped-period inflation across
  the boundary. Incomplete cross-contract trace → false-REJECT of a surfaced true Medium.

## Verdict — SAFETY-ONLY PASS
Safety + 0 severity FP + controls clean + NOT_RUN=0 + 0 depth-trace false escalations hold, but **conversion =
0**. Per the rubric this is Safety-only PASS.

### What this says about P92 — MIXED, conversion still unvalidated
- **Positive:** v3 **eliminated bare abstains** (7/7 NEEDS_CONTEXT well-formed with named dependency + next
  step), produced **0 false escalations / 0 severity FP**, and its process **named the exact M-02 function**.
  The calibration discipline held cleanly.
- **Negative:** conversion is still 0 — the **3rd consecutive hardened/low-density subject** (kleidi 0H/3M,
  ramses 0H/2M). Two instructive residual limits, neither a calibration regression:
  1. **Unexecuted in-scope next-step (M-02):** a well-formed NEEDS_CONTEXT whose named next-step is an *in-scope
     read* should be **resolved before freezing** — reading the 10-line `flash` body would have converted M-02.
  2. **Cross-contract trace gap (M-01):** the trace stopped at an *in-scope* staticcall boundary
     (`positionPeriodSecondsInRange`) instead of tracing **across** it into the pool's `periodCumulativesInside`.
- **Per-contract floor again added coverage but 0 hits** — both Mediums were in top-surface contracts.

Per constraints: no machinery change (gate frozen `193abf9f`; `localized_depth_trace` unchanged), no post-key
tuning, no retroactive re-score. No promotion → no P84 handoff bundle, no funnel record (accurate).

## Next recommendation
- **P94 = a small v3 depth-completion refinement** (the two named residual limits): (a) a well-formed
  NEEDS_CONTEXT whose `next_step` is an **in-scope file read** must be **resolved** (read it, re-trace) before a
  freeze — abstain only on genuinely out-of-scope dependencies; (b) **trace across in-scope staticcall/external
  boundaries** (the callee is in scope ⇒ follow it) rather than abstaining at the boundary. Both are tractable,
  source-grounded, and target the exact M-02/M-01 misses; regression-test against these two anchors.
- **Eval subject selection:** three consecutive hardened/low-density subjects have left the conversion claim
  unvalidated — deliberately pick a **higher-finding-density** subject next (more awarded H/M, ideally with a
  simple in-scope arithmetic finding like M-02) to actually exercise conversion under the new depth rules.
