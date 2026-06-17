# P288 — NO_READY_DIAGNOSIS (pre-reveal; frozen BEFORE reveal)

0 READY candidates on ECG. First-failed evidence stage per validation candidate (all pre-reveal, findings sealed):

| candidate | class | first-failed stage | why |
|---|---|---|---|
| SurplusGuildMinter.stake | SHARE_ROUNDING | EVIDENCE_DERIVATION (D4.x) | value-flow + TRACE_FOUND, but no anomaly / no source-backed reference (NO_REFERENCE) |
| ERC20RebaseDistributor._burn | SHARE_ROUNDING | EVIDENCE_DERIVATION | rebase share math reached, no detectable deviation |
| ERC20RebaseDistributor.distribute | REWARDS | EVIDENCE_DERIVATION | distribution value-flow, no anomaly/reference |
| ProfitManager.claimRewards | REWARDS | EVIDENCE_DERIVATION | reward accumulator value-flow, no anomaly/reference |
| LendingTerm.borrow | ACCOUNTING | EVIDENCE_DERIVATION | borrow accounting value-flow, no anomaly/reference |
| LendingTerm._borrow | ACCOUNTING | EVIDENCE_DERIVATION + cross-fn dynamic | TRACE_TOO_DYNAMIC (external dispatch) + no reference |
| SimplePSM.redeem | STATE_MACHINE | EVIDENCE_DERIVATION (D2) | no or-state gate / state-machine delta derivable |
| LendingTerm.onBid | UNKNOWN | (refuted) | INLINE_GUARD_REFUTED — real execution gate |

## Root localization
The dominant first-failed stage is **EVIDENCE_DERIVATION_GAP**: 6/8 candidates are
`value_flow_present_but_no_anomaly` + `NO_REFERENCE`. The credit-guild bug classes (lending/borrow accounting, rebase
share math, reward accounting, PSM redemption) are relationship/accounting mechanisms the current evidence lenses
(div-before-mul anomaly · sibling/registry/rounding/oracle-normalization invariant-delta) do not model. No D4.6
oracle-normalization match (ECG is not oracle-centric), which is precisely the lens that carried kelp in P287 — so the
P287 generalization was **lens-specific**, not universal.

## Honest note
The READY gate is fail-closed and correct: it produced 0 READY rather than a false READY (severe FP=0). This is a
recall-of-evidence limitation, localized cleanly, not a precision failure. Reveal (Phase 7) will check whether these
surfaced loci correspond to awarded H/M (and thus whether the gap is on awarded mechanisms).
