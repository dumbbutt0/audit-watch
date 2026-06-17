# P284 — LIMITATIONS

1. **0 newly-lifted READY.** Invariant-delta derivation works (it recovered the Blackhole M-04 sibling-recipient
   deviation from source, 0 FP) but lifts 0 because (a) the one HIGH deviation is blocked upstream by D1 inline-guard
   over-match, and (b) the other 81 value-class candidates have no source-local deviation reference (their "correct"
   value is not a sibling/registry/rounding/oracle fact in scope).
2. **Source-local references only.** The deviation detectors need the reference to be present in source: a sibling in the
   same contract, a registry-updating sibling, rounding evidence, or an oracle read + value use in the same span. When
   the corrected value is an *intended formula* with no in-source comparand, P284 fail-closes (NO_REFERENCE) — by design.
3. **The before/after / conservation equation is a scaffold, not a violation.** D4.1/D4.5 extract an assertion template
   (balanceAfter-balanceBefore==expected, totalΔ==minted) but never lift on their own; a deviation detector must
   corroborate. This is what keeps FP=0.
4. **D4.4 corrected-reference is conservative.** Rounding-direction uses `bound_semantics_gate._rounding_evidence`
   (needs explicit `Rounding.Floor/Ceil`/mulDiv evidence); it never invents `mulDivUp` from "looks wrong".
5. **Intra-contract siblings only (this phase).** Cross-contract sibling pairing
   (`cross_contract_sibling_parity_taxonomy`) is available but not yet wired into the deriver (backlog priority 2).
6. **Reused detectors are imported read-only.** P284 consumes their pure classifications; it never edits, routes, or
   sets `routes_in_production`/`routed_manifest_ids` for them. Their sha256 are pinned.
7. **Supervised eval, not blind, not production.** 12 eval audits; award titles/bodies never read by code. No production
   authority; advisory/eval-only; default-off; un-wired. No PoCs beyond the L2Governor regression.
