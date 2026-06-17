# P282 — VALUE_FLOW_EVIDENCE_AUDIT (10 packages)

`outputs/audit.json`. All source-span-backed; no hallucinated core evidence; no over-inference from generic value
movement.

## READY (1) — regression
- **L2Governor.execute** (state-machine): source-backed (or_state_gate `Succeeded||Defeated||Expired`), assertion
  implementable, **PoC PASS_SUPPORTED** (re-run). Correct status. No value-flow over-claim.

## INLINE_GUARD_REFUTED (sampled — all genuine guards, D1-gap closure working)
- UNIv3Connector.openPosition → `onlyManager` (modifier-auth). Correct block.
- VotingEscrow.withdraw → `_isApprovedOrOwner`. Correct block.
- AccountingManager.calculateDepositShares → modifier-auth + whenNotPaused. Correct block.
- V3Vault._withdraw → `if (msg.sender != …)` (either-side fix). Correct block.
- CheckpointingFacet.commitCheckpoint → `… != msg.sender` (either-side fix). Correct block.
No over-flagging found: every marker corresponds to a real inline/modifier guard on a withdrawal/deposit/admin path.

## NEEDS_VALUE_FLOW (sampled by subreason)
- value_flow_present_but_no_anomaly (e.g. Starklane.depositTokens): real state-write + asset-move, but no source-
  detectable violation → correctly blocked (a transfer is not a bug). Needs data-flow/corrected-reference.
- value_flow_out_of_span (e.g. GaugeCL.claimFees → `_claimFees()`): value-flow is in the delegated callee → correctly
  blocked. Needs cross-function tracing.
- no_value_flow_in_span (e.g. SubnetActorGetterFacet.powerScale `return s.powerScale`): getter, no value-flow →
  correctly blocked.

## NEEDS_STATE_MACHINE / NEEDS_SOURCE_SPAN (sampled)
- state class without an in-span state gate → NEEDS_STATE_MACHINE_EVIDENCE (correct).
- interface declaration → NEEDS_SOURCE_SPAN (correct, e.g. IBeanstalk.cancelPodListing).

## Audit result
hallucinated core evidence: **0** · placeholder leaks: **0** · over-inference from generic transfer/write: **0** (the
anomaly-required lift rule prevented it) · mis-classified status: **0**. The deriver establishes value-flow STRUCTURE
correctly and refuses to lift without a concrete anomaly.
