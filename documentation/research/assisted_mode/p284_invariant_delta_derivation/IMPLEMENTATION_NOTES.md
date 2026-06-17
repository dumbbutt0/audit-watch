# P284 — IMPLEMENTATION_NOTES

## Files changed (allow-list only)
| File | Change |
|---|---|
| `scripts/research/invariant_delta_deriver.py` | NEW — D4.1–D4.7 deriver; `derive(item, manifest, audit_id, gate_evidence, trace_evidence)`. |
| `config/research_invariant_delta_deriver.json` | NEW — lift statuses, value/state classes, sibling liftable confidence, oracle markers, caps. |
| `scripts/research/completion_evidence_deriver.py` | imports `invariant_delta_deriver`; attaches `invariant_delta_evidence`; on a FOUND deviation at HIGH/MEDIUM for a value/state class, upgrades the 3 core readiness dims + delta/victim/assertion from the source-backed reference. |
| `scripts/research/poc_readiness_evidence_gate.py` | value-class block also passes on `_id_deviation(pkg)`; state-class block also passes on `STATE_MACHINE_DELTA_FOUND`; summary carries `invariant_delta_status/type/confidence`. |

## Reused detector platform (READ-ONLY import; byte-identical)
`invariant_delta_deriver` imports the PURE functions of the validated 0-FP detectors and never edits/routes them:
- `sibling_function_parity_taxonomy.extract_features` / `classify_pair` / `_stem` / `_core` → D4.3.
- `registry_position_lifecycle_taxonomy.extract_registry_features` / `classify_contract` → D4.2.
- `omitted_term_dataflow_gate._term_flow` (available for D4.4 computed-not-applied) and
  `bound_semantics_gate._rounding_evidence` → D4.4 rounding-direction.
- `source_span_guard_extractor` (P281) for bodies + state-machine evidence → D4.7.
Their sha256 are pinned in `test_p284` (`REUSED`). The deriver carries `is_gate:false · research_only:true ·
emits_findings:false · routes_in_production:false · routed_manifest_ids:[]` on every record.

## Lift mechanism (precision spine)
A value/state candidate lifts only when a 0-FP DEVIATION is found (sibling missing-component / registry desync /
rounding-direction / oracle-normalization / forbidden-state). The local before/after equation (D4.1/D4.5) is attached as
the PoC assertion but never lifts on its own (a `NO_REFERENCE` record can still carry an equation scaffold). When a
deviation is found at HIGH/MEDIUM, the deriver upgrades `derived_confidence` for attacker_path/impact_delta/victim_gainer
so the candidate can reach READY through the normal readiness path; otherwise it stays blocked.

## Bounded SSA (internal method only)
`_d15_equation` extracts before/after (≥2 `balanceOf`, or `*Before`/`*After`) and conservation (`total*` writes)
equations from the comment-stripped body — a structural template, not symbolic execution. No alias analysis / SMT /
path exploration. Sibling examination is capped (`max_siblings_examined`, pre-filtered by stem/core kinship).

## Back-compat
The deriver attaches invariant-delta evidence and upgrades core dims ONLY when a real FOUND deviation exists for a
value/state class; synthetic P279–P283 fixtures produce no such deviation, so prior statuses are unchanged (93 P278–P283
tests green). D1 inline-guard precedence and declaration-only blocks are untouched (checked first in the gate).

## No hash-pin cascade
No test pins the deriver/gate/extractor or their configs. FROZEN P260–P273 + the reused detector modules + forbidden 5
are byte-identical (asserted in test_p284 + verification).
