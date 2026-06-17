# P272 — REVEAL_AND_SCORE (Phase 9, POST-FREEZE) — BLIND

## Freeze integrity (recorded BEFORE the answer key)
SELECTOR_OUTPUTS `ba300d6fb82c8dcb` · IMPACT_FIRST_TRIAGE `90e985e9b0ec187c` · RANKING_AND_COMPLETION
`2c5ac56b6605ca6e` · POC_INTENT `e9cbb1a2a4ac8b18` · selector_decisions `ce28237c9d676986` · triage_decisions
`fdc66756bc51107f` · PoC `6b4f5189e43d03bd`.
Reveal source: `code-423n4/2024-01-init-capital-invitational-findings/report.md` (PUBLIC). Awarded: **3 High + 4
Medium** — ALL in **MarginTradingHook order management**.

## Awarded findings vs my candidates
| awarded | subsystem / class | my path |
|---|---|---|
| H-01 `MarginTradingHook.updateOrder` lacks access control | order mgmt / **access-control** | NOT selected (recall surfaced adjacent MarginTradingHook fns, not updateOrder) |
| H-02 updateOrder lets creator set arbitrary `tokenOut` | order mgmt / **input validation** | NOT selected |
| H-03 `fillOrder` front-run via `limitPrice_e36` | order mgmt / **front-running** | adjacent (`_calculateFillOrderInfo` was in advisory #None) but NOT selected |
| M-01..M-03 MarginTradingHook DOS / cancel / balance | order mgmt / DoS | NOT selected |
| M-04 LP unwrap/MasterChef reward DoS blocks decollateralize/liquidation | rewards/LP DoS | adjacent (harvest surfaced) but DEFERRED (unsupported-drama control) |

**The awards are entirely access-control / order-validation / front-running / DoS in the MarginTradingHook ORDER
layer — NOT the bad-debt / liquidation / collateral-credit ACCOUNTING class** the P271 lending checklist + impact-
first triage prioritized.

## My candidate scoring
| id | mechanism | PoC | awarded? | classification |
|---|---|---|---|---|
| **C-incentive** | LiqIncentiveCalculator min-floor-after-max-cap | **PASS (real code, exact)** | **NO** | **NON-AWARDED TRUE POSITIVE** (real ordering quirk; config-reachable `min>max`; not awarded — likely QA/out-of-scope) |
| C-health-zero | liquidate health==0 bad-debt | not run | NO | not awarded |
| C-coll-credit | collateral-credit miscalc | not run | NO | not awarded |

## Mechanism-recovery scoring
- **EXACT_AWARDED_MECHANISM: 0** · STRONG: 0 · FAMILY: 0.
- **NON-AWARDED TRUE POSITIVE (exact, real-code, pre-reveal): 1** (C-incentive cap ordering).
- **SUBSYSTEM_ONLY_RECALL of the awarded subsystem: partial** — MarginTradingHook was surfaced (repayDebt/
  addCollateral/removeCollateral/coreCallback/_calculateFillOrderInfo) but the **awarded order-mgmt loci (updateOrder/
  fillOrder) and the access-control award CLASS were not selected** (impact-first triage steered to lending-accounting
  impact classes).
- **FALSE_POSITIVE (severe concluded/reportable): 0** — nothing concluded/reportable; C-incentive flagged with its
  config precondition.

## Headline (honest)
**The family→exact bridge GENERALIZED BLIND** — C-incentive was recovered as an *exact, real-code, runtime-proven*
mechanism pre-reveal (the P271 capability is not Wise-specific). **But 0 awarded recovery**, because (1) the exact
mechanism is **non-awarded**, and (2) init-capital's awards are an **access-control / order-management class** that the
impact-first triage + lending-accounting checklist de-prioritized. This is the **objective mismatch (D)**: *real bug
discovery ≠ contest-awarded bug matching* — the awards were a different class than what the lending-accounting
targeting pursued (compounded by the invitational target's small, peripheral award set).
