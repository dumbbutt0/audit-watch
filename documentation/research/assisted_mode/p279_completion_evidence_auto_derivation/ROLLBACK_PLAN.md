# P279 — ROLLBACK_PLAN

1. Delete `scripts/research/completion_evidence_deriver.py`, `config/research_completion_evidence_deriver.json`,
   `tests/research/test_p279_completion_evidence_deriver.py`, and
   `documentation/research/assisted_mode/p279_completion_evidence_auto_derivation/`.
2. Revert the P279 additions in `poc_readiness_evidence_gate.py` (the `derived_confidence` check) and any
   `expanded_validation_queue.py` integration — restore to the P278 versions.
3. Verify P260/P262/P264/P267/P273 router code+config/P269 + P271 + forbidden 5 byte-identical (P279 never touched them).
4. Verify `output` symlink → audits/size-credit-2024-06-blind/output. No production routing/gate/severity path touched;
   no production authority granted; eval sources read-only.
