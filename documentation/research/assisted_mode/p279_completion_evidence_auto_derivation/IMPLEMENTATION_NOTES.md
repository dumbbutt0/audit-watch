# P279 — IMPLEMENTATION_NOTES

- `completion_evidence_deriver.py`: joins each P278 package to its manifest item by `contract.function`; derives the 12
  fields via class templates + the anomaly-based confidence rules; writes derived values into the gate-field names
  (attacker_model/state_value_liveness_delta/victim_gainer/tx_sequence/poc_assertion/refutation_result/...) so the gate
  sees them filled, plus a `derived_confidence` map. Emits JSON + guard report; fail-closed; advisory contract stamped.
- `poc_readiness_evidence_gate.py`: added a confidence check — if `derived_confidence` present, the 3 core fields
  (attacker_path/impact_delta/victim_gainer) must be HIGH|MEDIUM for READY; LOW-confidence core ⇒ NEEDS_MORE_EVIDENCE.
  Backward-compatible: hand-authored packages without a confidence map are unaffected (P278 behavior).
- Auth-guard global override added after an evidence audit caught a guarded function (`onlyManager`) reaching READY via
  a substring false-match ('fill' in 'fulfill'); guarded functions now drop to LOW attacker_path.
- Deterministic; no answer-key/target constants; preserves source_basis citing the exact manifest fields.
