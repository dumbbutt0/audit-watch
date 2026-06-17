# P282 — IMPLEMENTATION_NOTES

- `source_span_guard_extractor.py`: `detect()` now also returns `state_write`, `asset_move`,
  `value_anomaly_div_before_mul`, `value_flow_out_of_span`; `value_flow_detected` requires terms AND a concrete write/
  move. D1 closures: `_MSGSENDER_EITHER` (msg.sender on either side of ==/!=) and `_MODIFIER_AUTH` (`only[A-Z]\w*`,
  case-sensitive, matches the signature line in the span) appended to guard markers.
- `completion_evidence_deriver.py`: emits `value_flow_evidence` (summary, attacker_input_to_state_link,
  affected_variables, value_movement_or_accounting_write, expected/broken invariant, confidence, source_basis,
  unresolved_assumptions). Confidence MEDIUM only with a div-before-mul anomaly; else LOW with a core-carrying
  cross-function/data-flow assumption.
- `poc_readiness_evidence_gate.py`: value-class D3 block now requires `value_flow_detected AND
  value_anomaly_div_before_mul` to pass; decision carries `value_flow_subreason`. Precedence unchanged
  (declaration -> inline_guard -> value -> state). The improved guard markers flow through the existing inline_guard
  step automatically (commitCheckpoint/openPosition now caught).
- Deterministic; no answer-key/target constants; source_basis retained; fail-closed; advisory contract preserved.
