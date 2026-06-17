# P288 — EVIDENCE_AND_READY_GATE (blind, ECG)

Ran deriver (P279/P282/P283/P284) + gate (P281/P285). severe FP=0, guard PASS.
status_tally: **NEEDS_VALUE_FLOW_EVIDENCE 6 · INLINE_GUARD_REFUTED 1 · NEEDS_STATE_MACHINE_EVIDENCE 1 · READY 0.**

## Per-candidate
| candidate | status | basis |
|---|---|---|
| SurplusGuildMinter.stake | NEEDS_VALUE_FLOW_EVIDENCE | value_flow present, TRACE_FOUND, **no anomaly**; invariant_delta NO_REFERENCE |
| ERC20RebaseDistributor._burn | NEEDS_VALUE_FLOW_EVIDENCE | value_flow present, TRACE_FOUND, no anomaly; NO_REFERENCE |
| ERC20RebaseDistributor.distribute | NEEDS_VALUE_FLOW_EVIDENCE | rewards value-flow, TRACE_FOUND, no anomaly; NO_REFERENCE |
| LendingTerm.onBid | INLINE_GUARD_REFUTED | execution-gate present (P285 D1) |
| ProfitManager.claimRewards | NEEDS_VALUE_FLOW_EVIDENCE | rewards value-flow, TRACE_FOUND, no anomaly; NO_REFERENCE |
| LendingTerm.borrow | NEEDS_VALUE_FLOW_EVIDENCE | accounting value-flow, TRACE_FOUND, no anomaly; NO_REFERENCE |
| LendingTerm._borrow | NEEDS_VALUE_FLOW_EVIDENCE | accounting, TRACE_TOO_DYNAMIC; NO_REFERENCE |
| SimplePSM.redeem | NEEDS_STATE_MACHINE_EVIDENCE | state class, no or-state gate / state-machine delta |

## Localization — why 0 READY
**Every value candidate is `value_flow_present_but_no_anomaly` with invariant_delta = NO_REFERENCE.** The value math is
reached (cross-function tracing even resolves callees, TRACE_FOUND) but **no deviation the current lenses model** is
present: no div-before-mul anomaly, no sibling missing-component, no registry desync, no rounding-direction evidence, and
crucially **no D4.6 oracle-normalization hit** (ECG is not oracle-centric — unlike kelp). So the binding constraint is
EVIDENCE_DERIVATION_GAP: the credit-guild accounting/share/rewards bugs (if present in these loci) are relationship/
accounting mechanisms the deriver does not yet derive. The READY gate is behaving correctly (fail-closed), not over-
strict on a derivable deviation — it simply found none.

## Precision note
0 false READY; the 1 INLINE_GUARD_REFUTED is a real execution gate; severe FP=0. The stack stayed precise on a fresh
target; the failure is recall-of-evidence, not precision.
