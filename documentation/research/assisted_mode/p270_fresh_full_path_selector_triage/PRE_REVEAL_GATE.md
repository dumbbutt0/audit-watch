# P270 — PRE_REVEAL_GATE (Phase 8, frozen BEFORE reveal)

Strict gate. Marks PRE_REVEAL_STRONG_CANDIDATE / PRE_REVEAL_PARTIAL_CANDIDATE / REFUTED / NEEDS_MORE_RUNTIME only.
Never severity/reportable/submission-ready/confirmed.

| candidate | selector | triage | completion | PoC | gate result |
|---|---|---|---|---|---|
| C-pp Pendle-share | KEEP_BOTH | SELECT_FOR_PARTIAL_RUNTIME | PARTIAL→guarded | **PASS (refutes inflation)** | **REFUTED** (guarded; true negative) |
| C-liq liquidation | KEEP_BOTH | SELECT_FOR_PARTIAL_RUNTIME | PARTIAL | not run (heavy) | **NEEDS_MORE_RUNTIME** |
| C-bd bad-debt | KEEP_BOTH | SELECT_FOR_PARTIAL_RUNTIME | PARTIAL | not run (heavy) | **NEEDS_MORE_RUNTIME** |

## Outcome
- **No PRE_REVEAL_STRONG_CANDIDATE and no PRE_REVEAL_PARTIAL_CANDIDATE** this round: the one runnable PoC (C-pp)
  *refuted* its mechanism (guarded), and the two high-award-class mechanisms (C-liq, C-bd) are NEEDS_MORE_RUNTIME
  (full-stack harness not built in scope).
- The gate requires PoC/runtime support for a strong/partial candidate; C-liq/C-bd lack it (not yet run) → they
  cannot be marked strong/partial. Honest: the path *routed* them correctly; completion/PoC is the open step.
- **0 severe concluded/reportable FP.** Nothing marked severity/reportable/submission/confirmed. C-pp is a true
  negative, not a false positive.

Full pre-reveal set frozen; hashes echoed in REVEAL_AND_SCORE. No answer key consulted.
