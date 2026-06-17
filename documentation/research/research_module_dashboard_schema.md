# Research-Module Dashboard Schema (REVIEW_ONLY lane)

Research-only, read-only. Defines how research-module REVIEW_ONLY candidates (value-flow now; access-control / signature-
replay later) surface on a dashboard **without** entering production submission. The lane is clearly labelled
"research / review-only — not a verdict". Forbidden states never render (they are not in the schema).

## Lane record
```json
{
  "research_only": true,
  "review_only": true,
  "module": "value_flow_chain | access_control_chain | signature_replay_chain",
  "module_status": "research_only | promotion_review_candidate",
  "subject": "string",
  "candidate_id": "string",
  "target": { "file": "string", "function": "string", "lines": "string" },
  "mechanism_class": "string",
  "output_state": "REVIEW_ONLY_ADVANCE | REVIEW_ONLY_ABSTAIN | REVIEW_ONLY_NEEDS_IMPACT | REVIEW_ONLY_REJECTED | REGRESSION_FAILURE",
  "confidence": "HIGH | MEDIUM | LOW",
  "impact_proof_status": "PROVEN_SOURCE_BACKED | BOUNDED_HYPOTHESIS | NOT_ESTABLISHED",
  "regression_status": "GREEN | REGRESSION_FAILURE",
  "human_decision": "pending | escalated_to_poc | routed_to_human_queue | rejected",
  "evidence_link": "path to the REVIEW_ONLY artifact"
}
```

## Rendering rules
- Banner per lane: "RESEARCH / REVIEW-ONLY — candidate generator, not a verdict. No confirmed bugs, no submissions."
- Only `REVIEW_ONLY_*` and `REGRESSION_FAILURE` states are renderable; `CONFIRMED_BUG`/`READY_TO_SUBMIT`/`AUTO_SUBMIT`
  are not in the enum and cannot appear.
- `REGRESSION_FAILURE` rows pin the lane to a red state and suppress the ADVANCE list until cleared.
- `human_decision` is the only mutable field, set by a human; the dashboard never auto-advances a candidate.
- Read-only with respect to production: no write-back into `submit.jsonl`, `merged_findings.json`, or any submission gate.

## Separation from production
This lane is parallel to — and never feeds — the production submission pipeline. Promotion of any module from
`research_only` to a production role is a separate, later, human decision (per the platform research-track invariants);
this dashboard only displays, it does not promote.
