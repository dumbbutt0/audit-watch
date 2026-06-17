# P279 — SETUP (R-A completion-stage evidence auto-derivation; REPAIR)

Auto-derive the PoC-readiness evidence fields the harness leaves as 'operator-to-derive', from SOURCE-DERIVED data
only, with per-field confidence. **Auto-derived evidence may prepare PoC intent; it must NOT create confirmed/
reportable/severity findings.** Not blind, not production authority.

## Allowed edits (this phase)
- NEW `scripts/research/completion_evidence_deriver.py` (sha `0af16cd25de481fe`) + `config/research_completion_evidence_deriver.json`.
- `scripts/research/expanded_validation_queue.py` / `poc_readiness_evidence_gate.py` — consume derived evidence +
  add the confidence gate (P278 research glue, not frozen).
- NEW `tests/research/test_p279_completion_evidence_deriver.py`; this doc dir.

## Byte-identical (verified): P260 d6b494bc · P262 a48336275f · P264 harness 85f9cbe6 · P267 b0623b8c · P273 router
CODE 6debb753 + router config 91f9deac · P269 63c88d02 + P267/P269 configs + P271 checklist 2929a2154a88; forbidden 5;
p276/p277 corpus-replay+funnel-map+metrics. Active audit symlink -> audits/size-credit-2024-06-blind/output.

## Input
manifest function metadata (signature/visibility/mutability/modifiers/external_calls/has_loop/tags) joined to each
P278 evidence package by contract.function. Forbidden inputs (award titles/bodies/reveal/issue-IDs/scoring) denylisted
+ tested. No contest-source parsing.
