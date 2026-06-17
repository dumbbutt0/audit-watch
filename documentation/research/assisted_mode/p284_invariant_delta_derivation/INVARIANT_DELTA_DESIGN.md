# P284 — INVARIANT_DELTA_DESIGN

## 1. P283 diagnosis — why lexical matching is exhausted
P281 (modifier→body guards), P282 (span-local value-flow), P283 (cross-function value-flow) progressively answered "is
there an anomalous TOKEN on a value path?" The corpus answer is no: 32 value-class candidates sit at
NEEDS_VALUE_FLOW_EVIDENCE, dominated by `value_flow_present_but_no_anomaly` (the value math is reached, runs, has no
div-before-mul). The violation is a RELATIONSHIP: wrong numerator/denominator, wrong rounding direction, wrong order of
update, wrong ledger adjusted, missing symmetric update, global-vs-position mismatch, oracle value used without required
normalization, computed value not applied, applied value computed from stale state. None of these is a lexeme; each is
"observed value ≠ the value implied by a source-backed reference."

## 2. The reference models (where the "correct" value comes from — never invented)
A relationship error is only detectable against a reference. P284 derives the reference from SOURCE only:
- **a sibling function** doing the same family op (claim/claimMany, deposit/mint, withdraw/redeem, add/remove, partial/
  full) that carries a component the candidate omits;
- **a registry/lifecycle sibling** performing a symmetric position↔global update the candidate omits;
- **a conservation rule** the function's own writes should satisfy (before+received==after, totalΔ==minted);
- **a before/after delta equation** extractable from the candidate's own state writes + balance reads;
- **a normalization rule** (feed decimals / staleness) the oracle read should apply;
- **a forbidden state** the value mutation should be gated against.
If no source-backed reference exists → NO_REFERENCE / AMBIGUOUS_REFERENCE / INSUFFICIENT_SOURCE → never lift.

## 3. Derivation types D4.1–D4.7 and their precision spine
| type | what it derives | reference / spine |
|---|---|---|
| D4.1 Conservation invariant | function writes should conserve (assets↔shares, collateral↔debt, before+received==after) | local bounded-SSA equation |
| D4.2 Symmetric ledger update | paired position↔global / principal↔interest writes that must move together | `registry_position_lifecycle_taxonomy.classify_contract` |
| D4.3 Sibling-function reference | weak sibling omits a component the strong sibling has | `sibling_function_parity_taxonomy.classify_pair` (high/medium tier) |
| D4.4 Corrected-reference expr | computed value not applied; rounding direction; updated-vs-stale var | `omitted_term_dataflow_gate._term_flow` + `bound_semantics_gate._rounding_evidence` |
| D4.5 Before/after delta equation | runtime assertion from state writes + balance reads | local bounded-SSA equation |
| D4.6 Oracle normalization | price read lacks decimals scaling / staleness check before valuation | local pattern over value_flow markers |
| D4.7 State-machine value invariant | value mutation reachable in a forbidden state | P281 state-machine evidence + or-state gate |

## 4. Bounded SSA scope (internal method ONLY)
Allowed: assign temp names to expressions; track simple variable substitutions across ONE function or ONE resolved
trace path; record def-use for params + state writes; structurally compare two expressions. Forbidden: compiler-grade
SSA, interprocedural alias analysis, unbounded symbolic execution, SMT, path explosion.

## 5. Fail-closed rules
- Sibling must be a genuine kin pair on a shared mutating path with a NAMED missing component (the 0-FP high/medium
  tier); naming-only similarity → LOW → never lifts.
- Ambiguous sibling (multiple weak candidates, conflicting) → AMBIGUOUS_REFERENCE.
- A corrected expression is emitted only when BOTH the observed and the expected expression are present in source; an
  expected expression that would have to be invented → INSUFFICIENT_SOURCE.
- D1 inline-guard precedence is preserved upstream (guarded candidate stays INLINE_GUARD_REFUTED).
- Declaration-only / missing source span → INSUFFICIENT_SOURCE.

## 6. Confidence & lift
HIGH: source-backed reference + specific observed/expected + named vars + implementable assertion + source-backed
attacker influence + no guard refute + no unresolved core. MEDIUM: one link bounded/implicit. LOW: naming-only / generic
/ partial / guarded-without-bypass. **Lift** (value/state class NEEDS_VALUE_FLOW → READY) only if status ∈ {DELTA_FOUND,
REFERENCE_FOUND, SIBLING_REFERENCE_FOUND, CONSERVATION_FOUND, STATE_MACHINE_DELTA_FOUND} AND confidence HIGH|MEDIUM AND
the core readiness dims (attacker/impact/victim) are raised to HIGH|MEDIUM by the same source-backed reference AND a
specific poc_assertion exists AND D1 doesn't refute.

## 7. Valid vs invalid reference examples
- VALID (D4.3): `claim` resolves `getOriginalOwner` inside an AVM guard; `claimMany` omits it on a shared `transfer`
  path → SIBLING_REFERENCE_FOUND, missing_component=getOriginalOwner, recipient_parity, HIGH. (Blackhole M-04 shape.)
- VALID (D4.2): a connector mutates a position via a lifecycle verb its registry-updating siblings also mutate but omits
  `registry.updateHoldingPosition` → CONSERVATION_FOUND. (NOYA H-23 shape.)
- INVALID: `deposit` and `withdraw` differ (they SHOULD) with no named missing component on a shared mutating path →
  NO_REFERENCE; never lifts.
- INVALID: "totalAssets should equal sum of balances" with no in-source equation to compare → generic conservation
  language → INSUFFICIENT_SOURCE.
- INVALID: inventing `mulDivUp` because a function "looks like it rounds wrong" with no rounding evidence → fail-closed.

## 8. FP risks
The dominant risk is treating a legitimate sibling difference as a violation. Mitigations: require the 0-FP detectors'
high/medium tier (named missing component on a shared mutating path), not raw difference; cap siblings examined; require
the candidate to be the WEAK side; never invent expected expressions; keep D1 precedence; lift only when the reference
also raises the core readiness dims. Severe concluded/reportable FP target = 0.
