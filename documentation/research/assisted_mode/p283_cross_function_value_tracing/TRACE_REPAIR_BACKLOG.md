# P283 — TRACE_REPAIR_BACKLOG

Per still-blocked class: the unresolved edge type, the missing source fact, the next repair, FP risk, priority.

## HEADLINE next repair — corrected-reference / data-flow (SSA) derivation
**Why:** after both span-local (P282) and cross-function (P283) tracing, the dominant carrier is
`value_flow_present_but_no_anomaly` (51 across the corpus). The value math is reached and is real, but the VIOLATION is
not lexically present — it is a *value-relationship vs a corrected reference* (wrong epoch index, wrong recipient, stale
vs fresh price, position vs global accumulator, set-vs-increment). No amount of deeper call tracing exposes it because
there is no anomalous token to match. The repair is data-flow/SSA reasoning that compares the computed value against the
reference it *should* equal. **FP risk: HIGH** if it guesses the "correct" reference — must be source-anchored and
conservative (only when both the computed and the reference expression are in scope). **Priority: 1.**

## Per-blocked-bucket backlog
| bucket (count) | unresolved edge / missing fact | next repair | FP risk | prio |
|---|---|---|---|---|
| value_flow_present_but_no_anomaly (51) | no lexical anomaly; needs the *intended* reference value | corrected-reference / data-flow (SSA) | HIGH | 1 |
| TRACE_TOO_DYNAMIC (19) | external/proxy/dynamic dispatch | bounded interface-binding resolver (only when the impl is in-manifest) | MED | 3 |
| no_value_flow_in_span (26 incl. getters) | getter/view; value lives elsewhere | recall — these may be wrong candidates; re-screen at selection | LOW | 4 |
| TRACE_UNRESOLVED (17) | callee body not in manifest / ambiguous | deeper parser + manifest completeness (multi-file libs) | MED | 3 |
| value_flow_out_of_span wrapper (5) | partly handled by P283; some still depth/ambiguity bound | raise depth selectively + arg-link tracking | MED | 2 |
| div-before-mul lexeme unreliability | `(x/U)*U` rounding & `**` scaling are benign even in real code | treat anomaly as a HINT, never a sole lift basis; require data-flow corroboration | (precision) | 2 |

## Not next (deliberately)
- Widening discovery / recall budgets — discovery is not the bottleneck; READY-evidence depth is.
- Loosening the gate to lift more — every loosening here would have produced a false READY on the two benign anomalies.

## After P283
Implement **corrected-reference / data-flow (SSA) derivation** → re-map → a small PoC sweep on the trustworthy READY set
→ then a fresh blind target.
