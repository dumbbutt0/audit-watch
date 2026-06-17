# P285 — D1_GRANULARITY_REMAP_RESULTS

P284 corpus (84 candidates · 12 eval audits) re-run with refined D1. Source: `outputs/remap_metrics.json`,
`outputs/guard_context_evidence.json`.

## Status distribution: P284 → P285
| status | P284 | P285 |
|---|---|---|
| READY_FOR_POC_INTENT | 1 | **2** |
| INLINE_GUARD_REFUTED | 36 | 29 |
| NEEDS_VALUE_FLOW_EVIDENCE | 32 | 37 |
| NEEDS_STATE_MACHINE_EVIDENCE | 8 | 9 |
| NEEDS_SOURCE_SPAN | 1 | 1 |
| NEEDS_MORE_EVIDENCE | 6 | 6 |
| NEEDS_GUARD_CONTEXT | 0 | 0 |

**Newly lifted to READY: 1 — `RewardsDistributor.claim_many`** (Blackhole **M-04**: rewards sent to `ownerOf` instead of
the sibling `claim`'s `getOriginalOwner`). This is the first time the assisted-mode chain carried an awarded
relationship-error bug to READY.

## Guard-context taxonomy (over matched auth tokens)
EXECUTION_GUARD 41 · UNKNOWN_READ 13 · VALUE_READ 4 · RECIPIENT_READ 2. INLINE_GUARD_REFUTED 36→29: **7 candidates**
reclassified out of false D1-refutation; all 7 are held at NEEDS_VALUE_FLOW/NEEDS_STATE_MACHINE except `claim_many`
(correct READY) — i.e. **no false unblock reached READY**.

## The 7 reclassified (P284 INLINE_GUARD_REFUTED → P285)
| candidate | → P285 | token context | verdict |
|---|---|---|---|
| RewardsDistributor.claim_many | READY_FOR_POC_INTENT | ownerOf = RECIPIENT_READ | correct unblock (M-04) |
| CollateralTracker.withdraw / redeem | NEEDS_VALUE_FLOW | `if(msg.sender!=owner){allowance-=}` = UNKNOWN_READ | correct (ERC4626 allowance, no revert) |
| V3Vault._withdraw | NEEDS_STATE_MACHINE | same ERC4626 pattern = UNKNOWN_READ | correct (held) |
| LibConvert._withdrawTokens / FieldFacet._harvest | NEEDS_VALUE_FLOW | `_user()` = VALUE_READ | correct (current-user read) |
| SubnetActorActivityFacet.batchSubnetClaim | NEEDS_VALUE_FLOW | `whenNotPaused` = VALUE_READ | acceptable (liveness, not access) |

## Anchors
claim_many → READY · L2Governor.execute → READY (PoC 2/2 PASS, `outputs/l2governor_regression_log.txt`) ·
V3Vault.transform → INLINE_GUARD_REFUTED (real if-revert) · VotingEscrow.withdraw → INLINE_GUARD_REFUTED (`assert(
_isApprovedOrOwner)`) · IBeanstalk.cancelPodListing → NEEDS_SOURCE_SPAN.

## Safety
**severe concluded/reportable FP = 0.** True guards remain refuted (41 EXECUTION_GUARD). No false READY. No true-guard
regression (the one assert-guard gap was found and fixed during the audit).
