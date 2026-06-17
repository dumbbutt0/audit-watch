# P272 — PRE_REVEAL_GATE (Phase 8, frozen BEFORE reveal) — BLIND

| candidate | selector | triage | completion | PoC | gate result |
|---|---|---|---|---|---|
| C-incentive (cap ordering) | KEEP_BOTH | SELECT_FOR_FULL_POC | COMPLETED_CHAIN (exact) | **PASS (real code)** | **PRE_REVEAL_STRONG_CANDIDATE** (conditional on min>max config) |
| C-health-zero (bad debt) | KEEP_BOTH | SELECT_FOR_PARTIAL_RUNTIME | PARTIAL | not run (heavy) | **NEEDS_MORE_RUNTIME** |
| C-coll-credit | KEEP_BOTH | SELECT_FOR_PARTIAL_RUNTIME | PARTIAL | not run (heavy) | **NEEDS_MORE_RUNTIME** |

## Outcome
- **C-incentive = PRE_REVEAL_STRONG_CANDIDATE:** source-backed exact root cause (min-floor after max-cap, no min≤max
  invariant) · value/invariant delta (multiplier > protocol max cap) · victim/gainer (over-seized borrower / liquidator)
  · terminal/amplifiable (every liquidation under the misconfig) · selector+triage survival · COMPLETED_CHAIN ·
  **real-code runtime PoC PASS** · FP refutation (control shows min≤max respects the cap). **Caveat:** requires a
  `min>max` governance config — flagged, not hidden (a precondition that bounds severity).
- C-health-zero / C-coll-credit: NEEDS_MORE_RUNTIME (heavy full-stack not built).
- **0 severe concluded/reportable FP.** Nothing marked severity/reportable/submission/confirmed.

Full pre-reveal set frozen; hashes echoed in REVEAL_AND_SCORE. No answer key consulted.
