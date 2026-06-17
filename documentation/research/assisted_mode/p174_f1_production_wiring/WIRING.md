# P174 — Production-wire the F1 dynamic-weight-lifecycle selector (re-surface only)

Scope (approved): **confirm existing guarded-downstream + math-estimator; add ONLY F1.** First production change
of the campaign. F1 is re-surface-only — it can ONLY route a clear to `needs_deep_pass`
(`dynamic_weight_lifecycle_review`); it never mints a finding, sets severity, routes, or marks submission-ready.

## Confirmed already in production (NOT re-implemented)
- **Guarded-downstream clear-policy rule** — `scripts/dependency_clear_utils.py` + the `coverage_sweep_write.py`
  enforcement already route a dependency-based clear that leans on an in-scope/unproven downstream guard to
  `needs_deep_pass`. Enforced on full audits (`dependency_clear_strict_full_audit: true`). Same quantamm
  motivation. Left untouched.
- **Math-estimator enforcement** (a superset of the F2 research idea, which the task correctly excluded) —
  `math_estimator_taxonomy.py` + `validate_math_estimator_clears.py` + `config/math_estimator_patterns.json`,
  `require_math_estimator_proof: true`. On quantamm it already flags the estimator family
  (`_normalizeWeightUpdates`=H-10, `_clampWeights`=L-06, `_calculateQuantAMMCovariance`=H-11,
  `_calculateQuantAMMVariance`=L-09). Left untouched. **The research F2 selector
  (`scripts/research/recall_selectors.py`) stays experimental and un-promoted (byte-identical).**

## Implemented (F1, mirrors the math_estimator lens exactly)
- `config/dynamic_weight_lifecycle_patterns.json` — two-signal taxonomy (DOMAIN term + STRUCTURAL signal, or an
  unambiguous lifecycle token). FP controls: pure getters excluded on the ambiguous path (but unambiguous
  entrypoints `onSwap`/`computeBalance` survive — they are `view` in Balancer-V3 yet are the M-08/M-12 surfaces);
  admin-only-gated non-entrypoint setters excluded.
- `scripts/dynamic_weight_lifecycle_taxonomy.py` — `classify` / `classify_manifest_item` (shared by lens +
  validator + writer).
- `scripts/validate_dynamic_weight_lifecycle_clears.py` — `validate_proof` (requires a lifecycle-completeness
  proof: sum/bounds/epsilon/interval/staleness with concrete anchors; boilerplate → `confirmatory_lifecycle_proof`).
- `scripts/dynamic_weight_lifecycle_audit.py` — the standalone re-surface lens (`is_gate:false`,
  `routes_in_production:false`, `re_surface_only:true`) → `output/dynamic_weight_lifecycle_audit.{json,md}`.
- `scripts/coverage_sweep_write.py` — one additive enforcement block after the math-estimator block (same
  fail-open + flag-gated style); a lifecycle-sensitive clear without a valid proof under strict →
  `apply_update("assigned", assigned_pass="deep", assigned_agent="dynamic_weight_lifecycle_review")`. Also adds
  `lc_sensitive` to `already_specialized` so a valid lifecycle proof substitutes for the special-focus checklist
  (mirrors the math_estimator `me_sensitive` exemption).
- `scripts/update_coverage_disposition.py` — added the optional `dynamic_weight_lifecycle_proof` param (mirrors
  `math_estimator_proof`; stored when provided; backward-compatible).
- `config/agent_policy.json` — `require_dynamic_weight_lifecycle_proof: true`,
  `dynamic_weight_lifecycle_strict: false`, `dynamic_weight_lifecycle_strict_full_audit: true`,
  `lifecycle_adversarial_proof: true` (matches the math_estimator convention: blocks only on full audits).

## Validation (quantamm)
- F1 re-surfaces the full lifecycle family: `setWeights` (M-04/M-09/M-14), `onSwap` (M-08), `computeBalance`
  (M-12), `performUpdate` (H-04) — all flagged.
- Combined with the pre-existing math-estimator (estimator family H-09/H-10/H-11/L-06/L-09), the **+11 touched
  recovery (8/44 → 19/44)** is reproduced. Residual: M-07 (`quantAMMPack32Array` precision) is not covered by
  either lens — a known small gap.
- **No production false confirmations:** guardrail grep of all P174 code → zero writes to severity /
  routing_allowed / submission_ready / finding-status / SWP-mint / sidecar. F1 only `apply_update("assigned",
  deep, dynamic_weight_lifecycle_review)`.
- **Deep-trace load bounded:** manifest-faithful **32 of 205 in-scope quantamm items (16%)** via
  `classify_manifest_item` (source-span snippets). Off-family corpora by the same path: basin 0, renzo 0,
  centrifuge 0; a small residual fires on **ve-voting "weight" surfaces** (blackhole `setVoteWeights`/`vote`)
  and withdrawal-batch surfaces (wildcat) because `weights` is a shared domain term. Precision caveat, not a
  correctness one: F1 is **re-surface-only and fail-open**, so an off-family hit costs at most one bounded
  deep-trace and can never produce a false confirmation, severity, or submission.
- **F2 stays experimental** (research-only `recall_selectors.f2_estimator_math`, un-promoted, byte-identical;
  the production math-estimator is the pre-existing sibling, not F2).

## Boundaries
`fabrication_rate=0` + reject-first untouched. No change to routing/severity/submission/dashboard, the
guarded-downstream rule, math-estimator, F2, F3, corpus, runtime sidecar, campaign ledger, answer keys, or the
active symlink. Research/campaign artifacts byte-identical.
