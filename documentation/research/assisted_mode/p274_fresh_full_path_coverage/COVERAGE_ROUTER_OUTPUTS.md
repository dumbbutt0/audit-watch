# P274 — COVERAGE_ROUTER_OUTPUTS (Phase 4, frozen P273)

Frozen `award_class_coverage_router.py` (`b87e3d22d1fb915b`) over the 15 frozen Phase-1 recall candidates with BLIND
source-derived class signals (`outputs/coverage_candidates.json`). Output `outputs/coverage_decisions.json` (+ `.md`).
Guard: **0 violations**. This is the only new stage vs P272.

## Class distribution of the 15 candidates (blind)
ORDER_VALIDATION ·  SHARE_ROUNDING_PRECISION (4) ·  DOS_LIVENESS (4) ·  ACCOUNTING_LIQUIDATION_BAD_DEBT ·
STATE_MACHINE_LIFECYCLE (5). Five distinct plausible classes present.

## Routing (handoff to P269)
| rep | award_class | sig | recall-Δ | label |
|---|---|---|---|---|
| `offers` | ORDER_VALIDATION | 4 | – | **COVERAGE_SELECT** |
| `pool_redeem` | SHARE_ROUNDING_PRECISION | 3 | – | **COVERAGE_SELECT** |
| `wq_withdraw` | DOS_LIVENESS | 3 | Y | **COVERAGE_SELECT** |
| `distribute` | ACCOUNTING_LIQUIDATION_BAD_DEBT | 3 | Y | **COVERAGE_SELECT** |
| `burnAndWithdraw` | STATE_MACHINE_LIFECYCLE | 3 | Y | **COVERAGE_SELECT** |

`handoff_queue_to_p269 = [offers, pool_redeem, wq_withdraw, distribute, burnAndWithdraw]` — **5 distinct classes, one
representative each.**

## Deferred (with reason)
`pool_withdraw/pool_mint/wq_mint` → DEFER_DUPLICATE_CLASS (SHARE already represented by `pool_redeem`);
`mergeTranches/queueClaimAll` → DEFER_DUPLICATE_CLASS (DOS already represented); `settleWithBuyout` →
DEFER_DUPLICATE_CLASS (STATE already represented by `burnAndWithdraw`, equal sig, lost the within-class tiebreak on
input order); `_mergeTranches/pool_constructor/deployWithdrawalQueue/pool__withdraw` → DEFER_LOW_SIGNAL
(internal/plumbing, several `impact_supported:false`).

## The headline (the P272 mismatch test)
- **Accounting did NOT monopolize:** only **1 of 5** routed slots is the accounting/liquidation class. The other 4 are
  ORDER, SHARE, DOS, STATE — exactly the cross-class coverage that P272 lacked.
- **≥2 non-accounting classes routed with source-backed signals:** ORDER (offer validation), DOS (queue liveness),
  STATE (vault/auction lifecycle), SHARE (pool rounding). Diversity goal met strongly.
- **Anti-monoculture guard classes** (ACCESS/ORDER/FRONT/DOS): ORDER and DOS both got a representative before any
  class took a 2nd slot. No 2nd reps were issued (budget filled by 5 distinct classes first).

## Honest within-class artifact
`settleWithBuyout` (the richer auction mechanism, blind) lost the STATE slot to `burnAndWithdraw` purely on input-order
tiebreak at equal signal. The router covers *classes*, not the best mechanism within a class — within-class ranking is
P269's job, but P269 only sees the one routed STATE rep. Recorded as a within-class selection limitation; both are
examined in completion.

Next: Phase 5 — frozen P269 impact-first triage inside the covered set.
