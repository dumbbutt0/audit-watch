# P281 — LIMITATIONS

- **Pattern-based body scan.** D1-D4 use deterministic keyword/structure patterns over the function source span, not a
  full parser. It can miss an obfuscated/inherited guard (→ a residual false READY) or over-flag (→ INLINE_GUARD_REFUTED
  on a guard that is actually bypassable). Mitigation: bypass must be an EXPLICIT package field, and the conservative
  default is to BLOCK — so errors trend toward fewer (not more) READYs.
- **or_state_gate is heuristic.** The state-machine "forbidden-state acceptance" signal is a structural heuristic; the
  one survivor (L2Governor.execute) was PoC-confirmed, but the signal could mis-fire elsewhere (it currently yields a
  single READY corpus-wide, so exposure is small).
- **Recall dropped (intended).** READY 3→1; 40 candidates now blocked with specific reasons. This is precision-up by
  design; value-flow classes stay blocked until the D3 repair.
- **Tier-C reproduction** for the revalidation (not a full governance deploy) — sufficient to support the state-machine
  mechanism CLAIM, not a full end-to-end exploit.
- Supervised/calibration on the P278 corpus; not blind; not production authority; nothing reportable/confirmed.
