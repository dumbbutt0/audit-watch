# P284 — ROLLBACK_PLAN

P284 is additive and un-wired; nothing in the production pipeline imports it. Options, smallest first:

## 1. Disable (no removal)
The invariant-delta deriver runs only inside `completion_evidence_deriver.py` (research module). Not running the
deriver/gate = P284 has no effect. It was never wired into production.

## 2. Revert the lift, keep the evidence
In `poc_readiness_evidence_gate.py`, drop the `or _id_deviation(pkg)` clause from the value-class block and the
`STATE_MACHINE_DELTA_FOUND` clause from the state-class block; in `completion_evidence_deriver.py`, keep attaching
`invariant_delta_evidence` but remove the core-dim upgrade. Behavior reverts to P283 lift rules; the invariant-delta
evidence remains as advisory diagnostics. Re-run the corpus; expect identical READY set (P284 already lifts 0).

## 3. Full removal
Delete `scripts/research/invariant_delta_deriver.py`, `config/research_invariant_delta_deriver.json`,
`tests/research/test_p284_invariant_delta_deriver.py`, and this docs dir; remove the `_idd` import + attach/upgrade block
in the deriver and the two gate clauses + `_id_deviation`/`IDD_LIFT`/summary fields in the gate. FROZEN modules, the
reused detector platform, and the forbidden 5 are untouched by P284, so removal restores the P283 state exactly.

## Note on the reused detectors
P284 only IMPORTS them read-only; rollback never touches `scripts/sibling_function_parity_taxonomy.py`,
`registry_position_lifecycle_taxonomy.py`, `omitted_term_dataflow_gate.py`, `bound_semantics_gate.py` or their configs.

## Verification after any rollback
`pytest tests/research/test_p283_cross_function_value_tracer.py` green · FROZEN + reused + forbidden 5 sha256 unchanged ·
`output` symlink → `audits/size-credit-2024-06-blind/output`.
