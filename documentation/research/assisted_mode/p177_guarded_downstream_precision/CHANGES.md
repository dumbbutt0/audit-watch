# P177 — Tighten guarded-downstream routing precision (production change #2)

## Problem (from P176)
On metadata-poor clears, `dcu.is_dependency_based_clear` fires on incidental clear *prose* ("invariant"/
"guard"/"oracle"/…); the clears lack structured dependency fields, so `classify_clear` returns
`missing_dependency_metadata`, which was **hard-blocking**. Result: 237/471 zaros clears (56.5% deep-pass load)
and all 30 revert-lend clears re-routed at 96%/87% off-target — a blunt flood, not precise recovery.

## Fix
Hard-route a dependency-based clear ONLY when **complete structured metadata resolves a genuine in-scope,
unproven downstream guard**. Prose-only / incomplete / unresolvable detections become **advisory** (recorded,
not routed). Reversible via `coverage_policy.guarded_downstream_require_structured` (default `true`).

| `classify_clear` status | P177 routing |
|---|---|
| `unreviewed_dependency`, `dependency_evidence_missing` (complete structured, in-scope, unproven) | **block** → needs_deep_pass |
| `guard_not_path_dominant` (locality, when locality flag on) | **block** |
| `missing_dependency_metadata` (prose-only OR structured-but-incomplete) | **advisory** |
| `unknown_dependency` (names don't resolve to an in-scope item) | **advisory** |
| `not_dependency_based` / `dependency_valid` / `finding_linked_dependency` / `out_of_scope_dependency` | **allow** |

Two new clear-time shortcuts in `classify_clear` (additive; absent fields → prior behavior): an auditor-declared
`dependency_scope="out_of_scope"` → `out_of_scope_dependency` (allow); a `proof_status` ∈ {valid, proven,
math_proof_valid, lifecycle_proof_valid} → `dependency_valid` (allow).

## Code changed
- `scripts/dependency_clear_utils.py`: new `STRUCTURED_BLOCKING`, `ADVISORY_CLASSIFICATIONS`,
  `ALLOW_CLASSIFICATIONS`, `PROOF_OK`, `DEP_SCOPE_OOS`; new `dependency_signal_source()` and the centralized
  `dependency_route_decision(cls, disp, locality_on, require_structured)`; `classify_clear` honors
  `dependency_scope`/`proof_status`. Legacy `BLOCKING_CLASSIFICATIONS` kept for the flag-off path.
- `scripts/coverage_sweep_write.py` + `scripts/deep_pass_write.py`: replace the ad-hoc blocking computation with
  `dcu.dependency_route_decision(...)`; prose-only/incomplete → advisory annotation (no route); add the 4
  capture fields to the `synth` dict. Routing action is unchanged (`apply_update("assigned", deep, …)` —
  re-surface only).
- `scripts/validate_dependency_clears.py`: `blocking` rows computed via the same flag.
- `scripts/update_coverage_disposition.py`: `apply_update` gains optional `dependency_name`,
  `dependency_scope`, `dependency_status`, `proof_status` (clear-time evidence capture; stored when provided).
- `config/agent_policy.json`: `coverage_policy.guarded_downstream_require_structured: true`.

## Validation (replay, read-only — `validate_p177.py`, before=legacy / after=P177)
| corpus | deep-pass load before → after | precise recovered (math/F1) | guarded (prose/incomplete) recovered |
|---|---|--:|--:|
| zaros | 266 (56.5%) → **49 (10.4%)** | 5 → **5** | 4 → **0** |
| revert-lend | 30 (29.4%) → **0 (0.0%)** | 0 → 0 | 4 → **0** |

All P177 invariants asserted by the script hold: load drops, precise recoveries unchanged, prose/incomplete
guarded recovery → 0, and no recovered finding routes via a prose guarded-downstream match.

**Why zaros lands at 49, not the plan's ~29 estimate:** first-match reattribution. 20 clears that the legacy
rule attributed to guarded-downstream are *also* math-estimator-sensitive; once guarded-downstream goes advisory
they fall through and route via the (precise, pre-existing) math-estimator lens (28 → 48), + 1 F1 = 49. This is
intended precise routing of estimator-shaped clears, not the blunt flood that was removed (217 previously-routed
items now correctly stay cleared+advisory). Net: an 82% deep-pass-load reduction on zaros, 100% on revert-lend.

## Boundaries
Re-surface-only preserved (routing still only assigns deep-pass; never mints findings / sets severity / touches
submission — guardrail grep = zero such writes). No mutation of old dispositions (the change affects future
sweeps; the replay is read-only). No answer-key / corpus / dashboard / severity / submission change. No new
accounting/liquidation selector. `fabrication_rate=0` + reject-first untouched.
