# Value-Flow REVIEW_ONLY Artifact Schema

Research-only (`research_only:true`, `review_only:true`). Every value-flow chain output is one record of this shape. The
record is a **human-review candidate**, never a verdict. Forbidden states (`CONFIRMED_BUG`/`READY_TO_SUBMIT`/`AUTO_SUBMIT`)
are structurally impossible (not in the enum).

```json
{
  "research_only": true,
  "review_only": true,
  "candidate_id": "string",
  "target": { "file": "string", "function": "string", "lines": "string" },
  "mechanism_class": "missing_call | recipient_missing | wrong_basis | missing_bound | missing_scale | omitted_term | computed_unapplied",
  "source_evidence": [ { "snippet": "string", "lines": "string", "why_it_matters": "string" } ],
  "downstream_value_or_authority_effect": "string (transfer/mint/burn/debt/collateral/share/fee/reward/settlement/authority)",
  "gate_decisions": {
    "P34_parity": "PASS | FAIL | N/A",
    "P45_advancement": "ADVANCE | REVIEW_ONLY | ABSTAIN",
    "P47_omitted_term_dataflow": "ADVANCE | ABSTAIN | N/A",
    "P49_bound_semantics": "ADVANCE | ABSTAIN | N/A",
    "P52_native_eth_sink": "ADVANCE | ABSTAIN | N/A"
  },
  "why_advanced_or_abstained": "string",
  "confidence": "HIGH | MEDIUM | LOW",
  "impact_proof_status": "PROVEN_SOURCE_BACKED | BOUNDED_HYPOTHESIS | NOT_ESTABLISHED",
  "required_human_review_steps": [ "string" ],
  "recommended_next_manual_action": "escalate_to_poc | route_to_human_review_queue | gather_impact_evidence | reject",
  "regression_status": "GREEN | REGRESSION_FAILURE | N/A",
  "output_state": "REVIEW_ONLY_ADVANCE | REVIEW_ONLY_ABSTAIN | REVIEW_ONLY_NEEDS_IMPACT | REVIEW_ONLY_REJECTED | REGRESSION_FAILURE"
}
```

## State mapping
- gate stack ADVANCE + impact PROVEN/BOUNDED → `REVIEW_ONLY_ADVANCE`.
- gate stack ADVANCE + impact NOT_ESTABLISHED → `REVIEW_ONLY_NEEDS_IMPACT`.
- gate stack REVIEW_ONLY (corroboration weak) → `REVIEW_ONLY_NEEDS_IMPACT` or `REVIEW_ONLY_ABSTAIN`.
- gate stack ABSTAIN (insufficient evidence) → `REVIEW_ONLY_ABSTAIN`.
- gate stack demote (non-design-absence / refuted premise) → `REVIEW_ONLY_REJECTED`.
- any standing-regression check red → `REGRESSION_FAILURE` (suppress all ADVANCE outputs that run).

## Invariants
- `output_state` enum **excludes** confirmed/submit/auto states by construction.
- `impact_proof_status` defaults to `NOT_ESTABLISHED` (the chain has no impact-path proof layer); only a human or a future
  dedicated layer may set PROVEN.
- The single genuine fresh example (SecondSwap `referralFeeCost`) would render as `REVIEW_ONLY_NEEDS_IMPACT`/`ADVANCE`
  with `confidence: MEDIUM`, `impact_proof_status: BOUNDED_HYPOTHESIS` — a PARTIAL, not a confirmed bug.
