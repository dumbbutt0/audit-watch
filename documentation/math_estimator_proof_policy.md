# Math / Estimator Proof Policy

## Why NatSpec/code consistency is insufficient

For ordinary access/lifecycle code, confirming the implementation matches its NatSpec is reasonable
evidence. **For mathematical estimators, guards, and formulas it is not.** Code and comments are written
together by the same author; they can agree perfectly while *both* deviate from the intended model —
the whitepaper formula, the invariant, the numerical contract. A "the code does what the comment says"
clear proves internal consistency, not correctness.

A math estimator can therefore be wrong even when NatSpec and code agree. The only adequate evidence is an
**independent re-derivation**: state the intended formula from an external source (whitepaper / protocol
docs / first principles), state what the code actually computes, and compare them — including scaling,
signedness, rounding, bounds, and edge cases.

## The QuantAMM covariance miss (H-11) — the motivating example

In the QuantAMM 2024-12 strict full-audit eval, dependency-aware clear enforcement recovered most of the
rule-math surface (useful detection 7/44 → 24/44, 0 FP). The single highest-value residual MISS was
**H-11: incorrect exponentially-weighted covariance estimation**
(`QuantammCovarianceBasedRule._calculateQuantAMMCovariance`). It was strong-cleared during the deep-pass
campaign with the reason *"estimator math reviewed in deep analysis … formulas match NatSpec"* — the
implementation matched its own documentation, so it was cleared. But the answer key marks the estimator
implementation itself incorrect (the `(1-λ)` placement / outer-product scaling deviates from the intended
estimator). NatSpec agreement hid a model deviation. This policy exists so that clear can no longer happen.

## Required proof fields (`math_estimator_proof`)

Schema: `schemas/math_estimator_proof.schema.json`. A valid strong clear of a math-estimator-sensitive item
must carry a `math_estimator_proof` object with all of these **non-empty**:

- `math_domain` — covariance | variance | gradient | moving_average | normalization | guard_rail |
  interpolation | oracle_math | fee_math | price_math | other
- `intended_formula` — from the whitepaper/model, **not paraphrased from the code's own comments**
- `implemented_formula` — what the code actually computes (operations, order, scaling)
- `formula_source` — array; whitepaper | NatSpec | code | protocol_docs | derived_in_review | unknown.
  **If this is only {NatSpec, code} with no `limitations` justification, the clear is `natspec_only` and invalid.**
- `independent_rederivation` — the reviewer's own step-by-step comparison of intended vs implemented
- `input_domain`, `output_domain`, `scaling_precision`, `rounding_behavior`, `signedness_assumptions`
- `bounds_and_guards` — bounds relied on AND independently confirmed (not merely cited)
- `edge_cases_checked` — concrete edge cases (zero/extreme inputs, n=1, ÷≈0, overflow threshold, odd/even n)
- `invariant_preserved` — e.g. weights sum to 1, variance ≥ 0
- `evidence_span` — file:line span(s) anchoring the implemented formula
- `limitations` — optional; **required** when `formula_source` is NatSpec/code-only

## Adversarial proof requirement (the Swan/Dria getFee miss)

A schema-complete proof is not enough. In the Swan/Dria 2024-10 strict eval, `getFee` was strong-cleared
with a full 14-field proof whose `independent_rederivation` simply **restated the implemented formula**
(`diff = 2 << difficulty`) and declared it intended. The shift is exponential (`2·2^difficulty`); the
intended scaling was linear. The proof confirmed internal consistency and missed the bug — the same
class as QuantAMM H-11. **Internal consistency is not correctness.**

So a valid proof must be **adversarial**, not confirmatory. Five more fields are required, and
`validate_math_estimator_clears.py` raises `confirmatory_proof` (blocking) when the content is merely
self-consistent:

- `formula_diff` — the explicit difference between `intended_formula` and `implemented_formula`
  (operations, order, scaling, constants). *Restating the code is not a diff.*
- `assumptions` — assumptions the re-derivation relies on, each independently justified.
- `monotonicity_and_economic_direction` — which way the output must move with the relevant **economic
  variable** (fee / stake / difficulty / price / reward / weight / time / supply / debt / collateral /
  …) and what the code actually does. **Must name an economic variable.**
- `attacker_favorable_search` — extreme/boundary/attacker-favorable inputs tried (max/min, `2**k`
  boundaries, zero, overflow threshold) and the divergence/overflow/precision-loss/inversion found or
  ruled out. **Required whenever the formula uses shift/scaling** (`<<`, `>>`, `**`, `1e..`).
- `economic_impact_if_wrong` — the concrete protocol/user/attacker consequence if the formula is wrong.

`validate_proof()` returns `confirmatory_proof` (blocking) when, with adversarial checks on:
1. `intended_formula ≈ implemented_formula` (normalized equality or token Jaccard ≥ 0.85) **and** there
   is no external source (`whitepaper`/`protocol_docs`) **and** no genuine economic analysis — re-deriving
   the code from the code proves nothing. (`derived_in_review` alone does **not** count as independent
   support for a matching formula.)
2. the re-derivation/diff uses confirmatory language (“appears intended”, “matches the code”, “internally
   consistent”, …) with no external source;
3. `monotonicity_and_economic_direction` names no economic variable (direction never checked);
4. the implemented formula uses shift/scaling but `attacker_favorable_search` names no extreme/boundary
   value.

**Escape (valid):** when the formulas legitimately match, the clear still stands if the reviewer did the
adversarial work — `monotonicity_and_economic_direction` names an economic variable and both
`attacker_favorable_search` and `economic_impact_if_wrong` are substantive. The reviewer checked and
found no divergence, which is a real proof.

### Mechanical aid — the formula-diff harness

`scripts/math_formula_diff_harness.py --intended "<expr>" --implemented "<expr>" --params name:lo..hi`
evaluates both formulas over a sweep of **boundary + attacker-favorable extremes** with a strict
AST-whitelisted evaluator (no `eval`, no calls except `min/max/abs`) and reports divergence, uint256
overflow/underflow, integer precision loss, and monotonicity inversion. Attach its JSON output as
`attacker_favorable_search` / `formula_diff` evidence. It is a tool the reviewer runs to *produce* the
adversarial evidence — it is **not** wired into the validator hot path.

Config flag: `coverage_policy.math_adversarial_proof` (default `true`) gates the content checks; the
existing `math_estimator_strict[_full_audit]` flags gate whether a non-`math_proof_valid` status routes
to `needs_deep_pass`.

## Invalid clears (rejected for math-estimator-sensitive items)

- "NatSpec matches implementation" · "code follows comments" · "formula appears consistent"
- "guard clamps the output" · "bounded by MathGuard" · "validated by `_guardQuantAMMWeights`"
- "handled by the estimator" · "oracle prevents this" · "lifecycle prevents this"
- "same pattern as sibling rule"

These are consistency assertions or dependency hand-offs, not formula proofs.

## Valid clear

A clear that supplies the `math_estimator_proof` above: the intended formula sourced externally, the
implemented formula read off the code, an explicit independent re-derivation reconciling them, the
scaling/precision/signedness/rounding analysis, the edge cases re-derived, and evidence spans. If an
independent re-derivation was not performed, the item must route to `needs_deep_pass`
(`assigned_agent = math_estimator_review`) — never a clear.

## What is "math-estimator-sensitive"

Classified by `scripts/math_estimator_taxonomy.py` (config `config/math_estimator_patterns.json`) with an
FP-tight two-signal gate:

> `sensitive := unambiguous_token OR (strong_domain_term AND structural_signal) OR
> (weak_domain_term AND strong_structural_signal AND a recognized math domain)`

Strong terms = covariance/variance/gradient/momentum/moving-average/normalize/guard-rail/epsilon/clamp/
interpolation/estimator/invariant. Weak terms = scale/precision/price/fee/oracle/multiplier/pack/lambda/…
(must co-occur with a loop / matrix `[i][j]` / `.pow/.log2/.exp2`). Unambiguous tokens =
`_guardQuantAMMWeights`, `_calculateQuantAMM*`, `_pow`, `calculateBlockNormalisedWeight`. This keeps lone
constants, single +/- arithmetic, plain balance/transfer math, and loop-bearing string getters OUT.

## Advisory vs strict mode

- `scripts/validate_math_estimator_clears.py --mode advisory` (default) — reports every
  math-estimator clear lacking a valid proof; **exit 0** (never blocks). Read-only on dispositions; writes
  `output/math_estimator_clear_validation.{json,md}`.
- `--mode strict` — **exit nonzero** if any math clear is `missing_math_proof`, `incomplete_math_proof`,
  or `natspec_only_proof`.
- `scripts/math_estimator_audit.py` is the 9th recall lens → `output/math_estimator_audit.{json,md}`
  (which math surfaces exist, which are high-risk, which were cleared without a proof — the H-11 surface).
- Run both via `./run_pipeline.sh math-proof-clears [strict]`.

## Writer enforcement (full-audit)

`config/agent_policy.json → coverage_policy`:
`require_math_estimator_proof: true`, `math_estimator_strict: false`, `math_estimator_strict_full_audit: true`.

`coverage_sweep_write.py` and `deep_pass_write.py` store any `math_estimator_proof` on the disposition and,
when math-strict is effective (config `math_estimator_strict` OR `AUDITWATCH_FULL_AUDIT=1` +
`math_estimator_strict_full_audit`), route a proofless math-estimator clear to `needs_deep_pass`
(`assigned_agent = math_estimator_review`). This check runs **after** the dependency-clear check, so
dependency-clear enforcement is never weakened — the two policies are independent and additive. In normal
(non-full-audit) mode the writers only **store** the proof; the standalone validator is the reporting tool.

## Full-audit recommendation

Enable strict enforcement for full audits (it already activates under `AUDITWATCH_FULL_AUDIT=1` via
`math_estimator_strict_full_audit`). Keep `math_estimator_strict=false` for routine/triage runs so the
policy is advisory there. Promoting `math_estimator_strict` to a hard universal gate should wait until the
proof-authoring flow is exercised on another protocol, to confirm the FP rate stays near zero (the
QuantAMM advisory run flagged 18 math clears with no spurious non-math items after the `other`-domain
tightening).

## Relationship to dependency-clear enforcement

Orthogonal. Dependency-clear stops "safe because an *unreviewed downstream component* handles it."
Math-estimator-proof stops "safe because the *code matches its own comments*." A covariance clear can be
caught by either (its prose often names a dependency token); both routes land it in `needs_deep_pass`. The
math policy added zero change to the dependency-clear classifier or its results
(`validate_dependency_clears.py` output is byte-identical before/after this change).
