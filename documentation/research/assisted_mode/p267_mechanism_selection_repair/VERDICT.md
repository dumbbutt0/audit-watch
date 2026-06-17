# P267 — VERDICT

## Verdict: A — SELECTOR_READY_FOR_FRESH_PRODUCTION_PATH_TEST

### Why
P267 built a narrow, default-off, advisory **pairwise mechanism selector** that repairs the exact P266 failure
(`awarded mechanism in B/C top-2 → dropped for an easier, lower-impact rival`). All A-criteria are met:

- **P266 H-03 awarded top-2 miss is preserved:** backtest case A → **KEEP_BOTH** with `anti_easy_poc_flag=true`. The
  awarded curator-enumeration gas-DoS (terminal_impact 10) is no longer dropped for the easier royalty skim
  (terminal_impact 0); both are carried into completion/PoC.
- **≥1 prior runner-up awarded case improves:** three do — P256 Plaza P-L2 (insolvency) and P-L1 (≤1.2 convexity)
  → KEEP_BOTH; P257 Notional N-L2 (messy fee-dodge) → SELECT_AWARDED outright.
- **Negative controls not degraded:** NC1 (dramatic but refuted) → REFUTE_FIRST (did NOT pick the drama); NC2 (two
  weak, no dominance) → KEEP_BOTH (no fabricated winner; feasibility did not decide). The selector is **not** a
  "pick the messier mechanism" heuristic.
- **Advisory guard: 0 violations** across all decisions; malformed/missing input fails closed (exit 2, no output).
- **No production-authority leakage; infrastructure unchanged:** P260/P262/P264 modules + 5 forbidden files
  byte-identical (verified pre/post); active audit `size-credit-2024-06-blind` unchanged; no contest/production
  source touched; selector needs no answer key.
- **Tests green.**

### Honest bounds (no over-claim)
- The A/B/C wins are **KEEP_BOTH**, i.e. "stop dropping the awarded mechanism," not "perfectly select it." That is
  the intended, conservative fix — exact recovery is then the job of completion/PoC on a **fresh full-path run**.
  P267 is READY for that test; it does not by itself prove exact recovery improved.
- **BakerFi L5 is INCONCLUSIVE** by construction: the awarded mechanism was never enumerated, and a pairwise
  selector cannot recover an un-enumerated mechanism. P267 fixes ranking/selection, not discovery.
- Dimension signals are operator-assigned; the backtest is necessary-not-sufficient (hand-encoded from frozen scored
  artifacts). The decisive proof is a fresh run where dimensions are assigned blind, pre-reveal.

### Not B / C / D
- Not **B** (PROMISING_NEEDS_REFINEMENT): the core requirement — preserve the P266 H-03 top-2 miss and improve ≥1
  prior runner-up case without degrading negative controls — is fully met, with a clean guard.
- Not **C** (NOT_USEFUL): it demonstrably converts the P266 drop into KEEP_BOTH and improves 3 prior cases.
- Not **D** (ABORTED): no constraint violated — research-only, advisory, un-wired, 0 production edits, forbidden +
  frozen files byte-identical, active audit unchanged.

### Required next step — fresh full-path run (P268)
Re-run the P266 production path on a fresh public-findings contest **with the selector wired into
`B/C top-2 → selector → completion/PoC queue`** (per INTEGRATION_PROPOSAL), assigning dimensions blind before reveal,
and score **exact mechanism recovery**. Production authority remains **withheld** until exact recovery is shown
repeatedly.
