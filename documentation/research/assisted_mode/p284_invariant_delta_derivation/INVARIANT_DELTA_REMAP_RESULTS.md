# P284 — INVARIANT_DELTA_REMAP_RESULTS

P283 corpus (84 candidates · 12 eval audits) re-run with invariant-delta derivation enabled. Sources:
`outputs/remap_metrics.json`, `outputs/invariant_delta_evidence.json`.

## Status distribution: P283 → P284
| status | P283 | P284 |
|---|---|---|
| READY_FOR_POC_INTENT | 1 | 1 |
| INLINE_GUARD_REFUTED | 36 | 36 |
| NEEDS_VALUE_FLOW_EVIDENCE | 32 | 32 |
| NEEDS_STATE_MACHINE_EVIDENCE | 8 | 8 |
| NEEDS_SOURCE_SPAN | 1 | 1 |
| NEEDS_MORE_EVIDENCE | 6 | 6 |

**Newly lifted to READY: 0.** Distribution is identical to P283.

## Invariant-delta evidence over the 82 body-resolved candidates
| invariant_delta_status | count |
|---|---|
| NO_REFERENCE | 81 |
| SIBLING_REFERENCE_FOUND | 1 |
| (DELTA / REFERENCE / CONSERVATION / STATE_MACHINE / AMBIGUOUS / INSUFFICIENT) | 0 |

`value_flow_present_but_no_anomaly` is unchanged (P284 adds evidence, it does not relabel the prior buckets).

## The one source-backed deviation found (and why it does not lift)
`blackhole RewardsDistributor.claim_many` → **SIBLING_REFERENCE_FOUND, HIGH**, missing `getOriginalOwner`
(recipient_parity vs sibling `claim`). This is the documented `sibling_function_parity` anchor (Blackhole **M-04**):
`claim` resolves the AVM original owner; `claim_many` omits it on the shared `transfer` path → rewards to the wrong
recipient. The deriver upgraded its core dims (attacker HIGH / impact HIGH / victim MEDIUM) and built a specific PoC
assertion — i.e. the lift mechanism fired end-to-end.

**It does not reach READY because the gate's P281 D1 inline-guard precedence fires first:** the candidate's body
contains `ownerOf(`, which the D1 `recipient_parity`/guard token list matches as an "inline guard", so the gate returns
`INLINE_GUARD_REFUTED` before the value-flow block is reached. Here `ownerOf` is an ownership **read on the buggy value
path** (the M-04 bug is *using* `ownerOf` instead of `getOriginalOwner`), not an access guard — so this is a D1
over-match, documented as the headline backlog item. Fixing D1 is out of P284 scope (it would change P281–P283 outputs).

## Per-class READY: unchanged (REWARDS/ACCOUNTING/SHARE/ORACLE all 0; STATE 1 = L2Governor).
## INLINE_GUARD_REFUTED: 36 (unchanged). Advisory-only survivors: all (nothing routed/reportable).
## Regression & safety
- **L2Governor.execute remains READY_FOR_POC_INTENT** (PoC re-run 2/2 PASS — `outputs/l2governor_regression_log.txt`).
- **severe concluded/reportable FP = 0.** No false READY; the only deviation found is a real awarded-bug shape, and it
  is conservatively held by D1.
