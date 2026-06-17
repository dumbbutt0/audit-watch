# P282 — ROLLBACK_PLAN

1. Revert the P282 additions in `source_span_guard_extractor.py` (D3 detectors + D1-gap regexes), `completion_evidence_
   deriver.py` (value_flow_evidence block), and `poc_readiness_evidence_gate.py` (anomaly-required D3 lift +
   value_flow_subreason) to their P281 state.
2. Delete `tests/research/test_p282_value_flow_derivation.py` and
   `documentation/research/assisted_mode/p282_value_flow_evidence_derivation/`.
3. Verify P260–P278 modules + router code 6debb753/config 91f9deac + P271 + forbidden 5 byte-identical (P282 never
   touched them) and the `output` symlink → audits/size-credit-2024-06-blind/output.
No production routing/gate/severity path touched; no production authority granted; eval/contest sources read-only.
