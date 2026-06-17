# P284 — INVARIANT_DELTA_REPAIR_BACKLOG

## HEADLINE next repair — refine D1 inline-guard granularity (unblocks the one HIGH deviation)
**Why:** the only source-backed deviation in the corpus (`claim_many`, SIBLING_REFERENCE_FOUND, HIGH, missing
`getOriginalOwner` = Blackhole M-04) is blocked by the P281 D1 inline-guard precedence because its body contains
`ownerOf(`. D1 treats `ownerOf`/`balanceOf`-style ownership READS as access GUARDS, but here `ownerOf` is the *buggy*
value on the path, not a guard. **Repair:** D1 should require the guard token to actually gate a `revert`/`return`
(predicate position), not merely appear in the body — distinguishing an ownership READ from an access GUARD. **FP risk:**
LOW-MED (must not re-open genuinely guarded functions). **Priority: 1.** This is a P281-module repair (separate approval;
it changes P281–P283 outputs, so it cannot land inside P284's byte-identical constraint).

## Per still-blocked bucket
| bucket (count) | failed derivation type | missing reference basis | next repair | FP risk | prio |
|---|---|---|---|---|---|
| claim_many M-04 (1) | D4.3 succeeded; gate D1 over-blocks | — | D1 read-vs-guard granularity | LOW-MED | 1 |
| NO_REFERENCE value-class (81) | no sibling/registry/rounding/oracle deviation in source | the "correct" value is not a source-local reference | share-math helper (D4.1 with a per-class corrected formula) + sibling pairing across modules (cross_contract_sibling_parity) | MED-HIGH | 2 |
| ORACLE (only 1 candidate surfaced) | D4.6 needs the oracle read + value use IN the same span | normalization often in a helper | extend D4.6 across the P283 trace path | MED | 3 |
| accounting/share | conservation equation present but no deviation | needs the *intended* formula (corrected-reference) | per-class corrected-reference templates (mulDivUp vs Down by protocol-favoring side) — source-anchored only | HIGH | 4 |
| recall | many value bugs never surface as candidates | upstream selection | recall sweep (separate track) | — | 5 |

## Notable: cross-contract siblings (D4.3 extension)
The intra-contract `classify_pair` found 1 deviation. `cross_contract_sibling_parity_taxonomy.classify_cross_pair`
(Size M-06 anchor) pairs siblings ACROSS per-action-library contracts — a natural D4.3 extension that may surface more
deviations on multi-contract modules. Read-only reuse, same precision discipline. **Priority 2 (with the share-math
helper).**

## Not next (deliberately)
- Inventing corrected expressions to force lifts (would break FP=0; the audit shows fail-closed is what keeps it clean).
- Widening discovery / budgets / routing.
