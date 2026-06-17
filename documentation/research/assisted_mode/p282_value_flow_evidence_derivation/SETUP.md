# P282 — SETUP (D3 value-flow evidence derivation; REPAIR)

Derive source-span-backed value-flow evidence to lift NEEDS_VALUE_FLOW_EVIDENCE candidates WITHOUT reintroducing false
READYs. Principle: don't infer a bug merely because a function moves value — needs a specific source-backed anomaly/
invariant. Research-only; advisory; no production authority; nothing reportable/confirmed.

## Allowed edits (this phase)
- scripts/research/source_span_guard_extractor.py (sha `e8582b9fcbf0f21e`) — added D3 value-flow structure (state-write/asset-move/
  share-math + div-before-mul anomaly + wrapper/delegation detection) AND closed D1 gaps (either-side msg.sender,
  modifier-auth only*).
- completion_evidence_deriver.py (emits value_flow_evidence) + poc_readiness_evidence_gate.py (D3-lift requires a
  concrete anomaly; value-flow subreason in the decision).
- NEW tests/research/test_p282_value_flow_derivation.py; this doc dir.

## Back-compat: D3 activates only when a real body resolves + value-flow evidence is present; synthetic fixtures keep
their statuses. P279/P280/P281 tests green (39/39). No test pins extractor/deriver/gate/configs.
## Byte-identical (verified): P260/P262/P264/P267/P269/P271/P273 router code 6debb753+config 91f9deac/P277/P278 glue +
forbidden 5. Active audit symlink -> audits/size-credit-2024-06-blind/output.
