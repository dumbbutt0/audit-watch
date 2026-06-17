# P130 — Repair Design

## Chosen repair (one surgical change)
**Risk-tagged computation/helper logic is lifted to the deep-pass cutoff, two-signal-gated and per-contract
capped.** Implemented as a deterministic post-pass over the manifest items, plus a `contract_type` field.

### The two-signal gate (`_apply_library_surface_boost`)
A `function` item is boosted to `score = deep_pass_attack_surface_score_min` (3) iff **BOTH**:
1. **Risk signal** — carries a tag the scorer already rewards: `{accounting, token, oracle, migration, config}`.
2. **Helper-shape signal** — `visibility ∈ {internal, private}` **OR** `mutability ∈ {view, pure}` **OR**
   `contract_type == "library"` **OR** contract name ends with `Facet`.

Only items that are `in_scope` and currently `< cutoff` are eligible. Per contract, at most
`library_internal_surface_boost_cap_per_contract` (=3) are boosted, ranked by signal strength
(strong tags `{oracle,accounting,migration}` first, then tag count, then `external_calls`/`in_tainted_sink`).
Boosted items get `surface_boost: "library_internal_risk"` for provenance.

### Why this design
- **General, not overfit (constraints 3-5):** keys only off generic structure (`contract_type`, visibility,
  mutability, name suffix `Facet`) and the *existing* risk-tag bucket. **No contract names, issue ids, or
  answer-key labels.** It rescues the *class* "risk-bearing helper logic under the cutoff," which is
  architecture-defined.
- **Two-signal = FP-tight:** a view helper with no risk tag is untouched; a risk tag on a non-helper
  state-changing function (already ≥4) is untouched. Mirrors the repo's existing two-signal lens philosophy.
- **Reuses an in-code precedent:** `build_coverage_manifest.py` already force-sets `score=3` for high-risk
  cross-chain constants (lines 322-333). This is the same guarded-boost pattern for a different class.
- **Capped:** the per-contract cap bounds deep-pass inflation on large library files (mirrors the per-file
  diversity cap in the research `value_flow_surface` lane).
- **Reversible/measurable:** the whole behavior is gated by `library_internal_surface_boost` (default on);
  one flag flip restores prior scoring exactly (verified by test).

### Alternatives considered and rejected
- **Widen scope to pull in out-of-scope libraries** — rejected: risks scope-correctness/precision; auto-
  including dependency libraries is unsafe. Left as a flagged follow-on.
- **Tune the risk-tag set to maximize awarded recovery** — rejected as overfitting toward the answer key;
  used the *existing* scorer tag bucket unchanged instead.
- **Full callgraph reachability boost** (propagate external-entrypoint reachability to callees) — more
  general but a much larger change; deferred. The tag+shape proxy captures most of the signal cheaply.
- **Lower the deep-pass cutoff globally** — rejected: blanket inflation, hurts precision everywhere.

### Knobs (config/agent_policy.json → coverage_policy)
- `library_internal_surface_boost` (bool, default true)
- `library_internal_surface_boost_cap_per_contract` (int, default 3)
- reuses `deep_pass_attack_surface_score_min` for the target/cutoff.
