# Assisted-mode validation — SecondSwap_VestingManager.listVesting

RESEARCH-ONLY · advisory · un-wired. Never sets severity, never auto-submits, never routes.

- **subject:** secondswap-2024-12  ·  **commit:** 6693d9e4f03a37919a52626de64b1cadf632fd29
- **supplied_by:** human  ·  **requested_check:** VALIDATE
- **candidate_invariant:** A vesting/listing holder must not be able to bypass or exceed the intended maxSellPercent restriction through sale/listing/claim state transitions, schedule inheritance, or accounting paths. Any sellability cap should be enforced against the correct holder, schedule, and claim state, and should not be bypassable by ordering or state mutation.
- **suspected_break:** maxSellPercent can be bypassed or misapplied through listing/sale/claim/schedule state transitions

## DECISION: `VALIDATED_FOR_POC_HANDOFF`
PASS_CANDIDATE survived depth trace + adversarial ordering + maximal consequence + severity gate + hygiene — recommend PoC handoff (human-gated)

### localized_depth_trace
```json
{
  "recommended_verdict": "PASS",
  "trace_complete": true,
  "missing_fields": [],
  "reasons": [
    "PASS honored: operation + boundary-case + post-state reach a concrete consequence"
  ]
}
```
### adversarial_ordering_check
```json
{
  "recommended_verdict": "PASS_CANDIDATE",
  "orderings_tested": 7,
  "counterexample": "SELF-PURCHASE bought-inflation: H lists p*A -> H buys its own listing (allowed: no buyer!=seller check at Marketplace.sol:387-404) -> completePurchase credits bought+=p*A (VestingManager.sol:162), which is added at 100% to sellLimit while (currentAlloc+sold-bought) stays = A -> repeating raises sellLimit without bound, letting H eventually sell its entire original allocation to an external buyer for only per-cycle fees. The cap is enforced against an inflatable `bought` counter, not the original schedule.",
  "reasons": [
    "PASS_CANDIDATE: a concrete ordering breaks the relied-upon invariant \u2014 not a REJECT"
  ]
}
```
### maximal_consequence_check
```json
{
  "recommended_impact_class": "medium",
  "escalate": false,
  "attach_high_markers": [],
  "attach_involuntary": false,
  "footgun_flag": false,
  "reason": "no source-backed maximal-consequence escalator -> base impact unchanged (gate decides)"
}
```
### severity_impact_gate
```json
{
  "kept": true,
  "recommended_status": "POC_REQUIRED",
  "reason": "material impact (medium) \u2014 promotion preserved",
  "impact_class": "medium"
}
```
### hygiene_validate
```json
{
  "hygiene_ok": true,
  "violations": [],
  "recommended": "POC_REQUIRED"
}
```

## Next (human)
- Hand to PoC via `scripts/handoff_generator.py` (REPRODUCE). PoC handoff is human-gated; no auto-submission.
