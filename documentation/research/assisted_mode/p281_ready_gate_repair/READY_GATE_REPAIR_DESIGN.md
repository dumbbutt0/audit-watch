# P281 — READY_GATE_REPAIR_DESIGN

## P280 failure modes (why repair)
3/3 auto-READY ran into PoCs; 0/3 supported. 2 refuted by INLINE guards invisible to the manifest `modifiers` field
(transform inline owner check; cancelPodListing inline ownership require); 1 (L2Governor.execute) ACCESS-mis-framed —
permissionless by design, real anomaly is state-machine (Succeeded||Defeated||Expired). The manifest `modifiers` field
is NOT a sufficient auth signal.

## D4 source-span extractor (the enabling primitive)
`source_span_guard_extractor.py` reads each manifest item's `file` + `source_span` -> function body (tolerant: missing/
unreadable -> body_available=False). Detects, from the BODY only (never award text):
- **D1 inline guards**: require(msg.sender==..) / if(msg.sender!=..)revert / ownerOf/loanOwner/lister/maker / mapping
  ownership (plots[user][index]>0) / isApprovedForAll/getApproved / hasRole / _checkOwner / _isApprovedOrOwner /
  paused / custom errors (Unauthorized/NotOwner/NotApproved/InvalidCaller/...).
- **D2 state-machine**: enum/status/proposal/listing/order/auction/queue gates incl. OR-state gates (`|| status`,
  Succeeded/Defeated/Expired) -> `or_state_gate` = a forbidden-state-accepting anomaly signal.
- **D3 value-flow**: balance/transfer/muldiv/shares/assets/debt/price/rounding/decimals signals.
- **D4 declaration-only**: body ends `;` with no `{` -> interface/abstract decl, no body to establish attacker_path.
**Bypass/satisfaction is NEVER inferred from source keywords** (a body mentioning Reentrancy/create2 is not proof of a
bypass); the gate requires an EXPLICIT package `guard_bypass_evidence` field (auto packages have none -> blocked).

## READY-gate precedence (when body_available, not forced)
1. declaration-only -> NEEDS_SOURCE_SPAN (D4).
2. inline_guard_detected and no source-backed bypass -> INLINE_GUARD_REFUTED (D1).
3. award_class in value classes and not value_flow_detected -> NEEDS_VALUE_FLOW_EVIDENCE (D3).
4. award_class in state-machine classes and not state_machine_detected -> NEEDS_STATE_MACHINE_EVIDENCE (D2).
5. else -> the P279 confidence + required-fields path (now with source spans present).
Advisory-only; never sets severity/reportability; fail-closed on malformed input.
