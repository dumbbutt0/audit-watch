# P281 — ROLLBACK_PLAN

1. Revert the P281 additions in `completion_evidence_deriver.py` (the `gate_evidence` attachment + extractor import) and
   `poc_readiness_evidence_gate.py` (the D1-D4 precedence block + new statuses) to their P279/P280 state.
2. Delete `scripts/research/source_span_guard_extractor.py`, `config/research_poc_readiness_gate.json`,
   `tests/research/test_p281_ready_gate_repair.py`, `pocs/p281/`, and
   `documentation/research/assisted_mode/p281_ready_gate_repair/`.
3. Verify P260–P278 modules + router code 6debb753/config 91f9deac + P271 + forbidden 5 byte-identical (P281 never
   touched them) and the `output` symlink → audits/size-credit-2024-06-blind/output.
No production routing/gate/severity path touched; no production authority granted; eval/contest sources read-only.
