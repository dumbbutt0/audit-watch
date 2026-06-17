# P285 — D1_GRANULARITY_REPAIR_BACKLOG

## Now-trustworthy READY set
`claim_many` (M-04 recipient) + `L2Governor.execute` (state-machine). **Next: a small PoC sweep** (claim_many L3
recipient-flip Tier-C reproduction; L2Governor already PASS_SUPPORTED) → then a fresh blind target.

## Remaining blocked candidates
| bucket | blocked by | next repair | FP risk | prio |
|---|---|---|---|---|
| ERC4626 withdraw-on-behalf (CollateralTracker/V3Vault) | UNKNOWN_READ allowance pattern → held at NEEDS_VALUE_FLOW | model `_spendAllowance`/allowance as a value-conservation invariant (P284 D4.1) so a real allowance bug could lift | MED | 2 |
| value-class no source-local reference (the P284 81 NO_REFERENCE) | no deviation reference | share-math corrected-reference helper + cross_contract_sibling_parity breadth (P284 backlog) | MED-HIGH | 1 |
| `whenNotPaused` liveness on claim-style fns | treated as non-access read | a distinct DoS/liveness lens (out of D1 scope) if pause-griefing is in scope | LOW | 4 |
| ambiguous auth (NEEDS_GUARD_CONTEXT) | UNKNOWN_READ carries the core claim | operator/source guard-context field or a deeper intra-helper guard resolver | MED | 3 |

## D1 follow-ups (small, optional)
- Resolve a guard that lives in an internal helper called in a gating position (e.g. `_checkOwner()` as a statement) —
  currently a bare helper call is UNKNOWN_READ unless inside require/if-revert. Bounded helper-body peek could promote it.
- Extend recipient-name vocabulary as new corpora arrive (kept conservative to avoid mislabeling VALUE vs RECIPIENT;
  both are non-guard, so it does not affect lift safety).

## Not next (deliberately)
- Weakening D1 globally — the refinement is surgical (token-in-execution-gate); true guards must keep refuting.
