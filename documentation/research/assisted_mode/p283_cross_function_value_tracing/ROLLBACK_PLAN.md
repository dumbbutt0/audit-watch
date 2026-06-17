# P283 — ROLLBACK_PLAN

P283 is additive and un-wired; nothing in the production pipeline imports it. Rollback options, smallest first:

## 1. Disable (no removal)
The tracer is only invoked by `completion_evidence_deriver.py` (research module) when a real callee body and no in-span
anomaly are present. Not running the deriver/gate = P283 has no effect. No flag flip needed in production (it was never
wired).

## 2. Revert the cross-function lift, keep the correctness fixes
In `poc_readiness_evidence_gate.py`, drop the P283 `OR trace_evidence … TRACE_FOUND` clause from the value-class D3
condition. Result: behavior reverts to P282's span-local lift rule while **keeping** comment-stripping and the `**`
exclusion (pure precision improvements). Re-run the corpus; expect identical READY set.

## 3. Revert the correctness fixes (NOT recommended)
Undo `strip_comments()` in `detect()` and restore `_DIV_BEFORE_MUL = /[^;\n]*\*`. This re-introduces false anomalies
(comment text + `**` exponent) and is strictly worse. Only do this if a regression is traced to comment-stripping
itself (none observed).

## 4. Full removal
Delete `scripts/research/cross_function_value_tracer.py`, `config/research_cross_function_value_tracer.json`,
`tests/research/test_p283_cross_function_value_tracer.py`, and this docs dir; remove the `_cfvt` import + trace
attachment in the deriver and the trace clause in the gate; revert `source_span_guard_extractor.py` comment-strip/`**`
edits. FROZEN modules and the forbidden 5 are untouched by P283, so removal restores the P282 state exactly.

## Verification after any rollback
`pytest tests/research/test_p282_value_flow_derivation.py` green · FROZEN + forbidden 5 sha256 unchanged · `output`
symlink → `audits/size-credit-2024-06-blind/output`.
