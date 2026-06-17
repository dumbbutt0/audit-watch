# P285 — ROLLBACK_PLAN

P285 edits two research modules; nothing in production imports them. Options, smallest first:

## 1. Disable (no removal)
The refined D1 runs only inside the research deriver/gate. Not running them = no effect. Never wired into production.

## 2. Revert D1 to token-presence (keep the taxonomy)
In `source_span_guard_extractor.detect()`, set `inline_guard_detected = bool(guard_tokens or gerrs or msgsender_either
or modifier_auth)` (the pre-P285 behavior) while still emitting `guard_contexts` as advisory diagnostics. Re-run the
corpus; claim_many returns to INLINE_GUARD_REFUTED.

## 3. Revert the gate-only piece
In `poc_readiness_evidence_gate.py`, remove the `NEEDS_GUARD_CONTEXT` elif + `P285_STATUSES` and the
`inline_guard_ambiguous`/`guard_contexts` summary fields. Behavior reverts to consuming `inline_guard_detected` only.

## 4. Full removal
Revert `source_span_guard_extractor.py` to its P284 state (remove `_match_close`/`_gate_spans`/`_read_context`/
`classify_guard_contexts` and restore the token-presence `detect()`), revert the gate edits, delete
`tests/research/test_p285_inline_guard_granularity.py` + this docs dir. FROZEN P260–P273, P283 tracer, P284 deriver, the
reused detector platform, and the forbidden 5 are untouched by P285, so removal restores the P284 state exactly.

## Verification after any rollback
`pytest tests/research/test_p284_invariant_delta_deriver.py` green · FROZEN + reused + forbidden 5 sha256 unchanged ·
`output` symlink → `audits/size-credit-2024-06-blind/output`.
