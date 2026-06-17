# P281 — IMPLEMENTATION_NOTES

- NEW `source_span_guard_extractor.py`: `extract(item)` -> {body_available, is_declaration_only, inline_guard_detected,
  guard_markers, state_machine_detected, or_state_gate, value_flow_detected, source_span}. Resolves item `file` from
  repo-root or audit dir; tolerant of missing files. Bypass detection removed from the body scan (keyword presence !=
  proof) — bypass must be an explicit package field.
- `completion_evidence_deriver.py`: imports the extractor; attaches `gate_evidence` to every enriched package (P279
  fields unchanged). When no item/body, gate_evidence.body_available=False.
- `poc_readiness_evidence_gate.py`: added the D1-D4 precedence block (activates only when body_available); new statuses
  INLINE_GUARD_REFUTED / NEEDS_GUARD_BYPASS_EVIDENCE / NEEDS_STATE_MACHINE_EVIDENCE / NEEDS_VALUE_FLOW_EVIDENCE /
  NEEDS_SOURCE_SPAN; decisions now carry `p281_block` + `gate_evidence_summary` (incl source_span). P279 confidence
  check preserved; advisory contract + fail-closed preserved.
- config/research_poc_readiness_gate.json: guard/state/value patterns + value/state class lists.
