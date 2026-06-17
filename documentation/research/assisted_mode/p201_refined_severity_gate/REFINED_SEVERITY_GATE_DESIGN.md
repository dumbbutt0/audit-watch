# P201 — refined severity-gate design (offline, mechanism-level)

**Status: design + offline-validation only.** Not built into production, not wired, not auto-applied. Additive to
the `deep_trace.md` threat-ceiling verdict (the verdict stays a ceiling; this maps `(mechanism, evidence)` → a
*calibrated* severity). Reject-first: absence of proof of a High dimension → demote, never promote.

## Two structural changes vs the P199/P200 gate
1. **Mechanism-level, not surface-level.** Every carried mechanism (`selected_mechanisms[*]`, plus
   `unresolved_mechanisms` with `NEEDS_HARNESS`) gets its **own** calibrated label. A surface may emit several
   labels; a Medium primary must **never** suppress a High secondary. (Fixes P200 predy-06/H-02 folding.)
2. **Class-specific, evidence-conditional rules** (below), replacing P199's blanket oracle→High / precision rules.

## Per-mechanism classifier → one of 6 classes
Classify each mechanism by its impact, then apply the class rule. (Class assignment is by the mechanism's proven
impact path, not keyword surface.) Labels: `HIGH_CONFIRMED · MEDIUM_OR_LOWER_CALIBRATED · NEEDS_HARNESS_FOR_SEVERITY
· SOURCE_REFUTED · INSUFFICIENT_EVIDENCE`.

### A — Direct theft / insolvency / permanent loss
- **HIGH** only if: permissionless **and** executable from shown source **and** material magnitude **and** NOT
  dependent on unseen code / narrow config.
- Else: dependent-on-unseen / unproven-magnitude → **NEEDS_HARNESS**; trusted-prereq → **Medium**; refuted → SOURCE_REFUTED.

### B — Oracle / price-feed  *(design-only; UNVALIDATED_OUT_OF_SAMPLE — zetachain has no oracle findings)*
- **HIGH** only if evidence proves a **permissionless** path to **material** insolvency / wrongful-liquidation /
  bad-debt / extractable value.
- **Medium** if stale/manipulable-price risk is real but magnitude, exploitability, market conditions, or the
  liquidation path are **unproven**.
- **NEEDS_HARNESS** if the path depends on runtime liquidity, oracle configuration, or external market setup.
- *(Directly targets P200 predy-09/M-04: "no staleness guard" alone → Medium/Harness, not High.)*

### C — Precision / rounding / tick math
- **HIGH** only if the error can **compound or be amplified** into material loss (e.g. repeatable drain, share-price
  inflation, accumulation across positions).
- **Medium** if bounded per trade / dust-scale / requires narrow conditions.
- **NEEDS_HARNESS** if magnitude is unknown.
- *(Targets P200 predy-10/M-03: bounded negative-tick rounding → Medium, not High.)*

### D — DoS / griefing / liquidation-blocking
- **Medium** by default.
- **HIGH** only if it causes **permanent fund lock**, **protocol-wide insolvency**, or **unavoidable material bad
  debt**. *(This rule already generalized in P200 — keep.)*

### E — Auth / privileged transition
- **HIGH** only if an **unauthorized** actor can execute a **privileged state transition** with **material loss**
  or **permanent control** impact.
- **Medium** or **NEEDS_HARNESS** if impact is limited, reversible, or magnitude unproven.

### F — Secondary-mechanism preservation (cross-cutting)
- Each selected mechanism is graded independently; the JSON stores a list of `(mechanism, class, label, rationale)`.
- A surface-level summary label MAY be emitted (= max of its mechanism labels) but **scoring uses per-mechanism
  labels**, so a High secondary is never lost behind a Medium primary.

## Reject-first invariants (unchanged)
- HIGH requires *proof* of its dimensions from the shown source; asserted-but-unproven reachability/magnitude →
  NEEDS_HARNESS (not High). Source-refuted → SOURCE_REFUTED. No promotion of a Medium ceiling.

## Application method (honesty)
Applied by the orchestrator as a **rubric** over each frozen blind output's own evidence, **answer-key-blind**, and
frozen as constants in `scripts/validate_p201.py` before the seal opens (P200 showed a keyword regex is too noisy —
kept only as supplementary signal). Deterministic in the sense of "fixed rubric applied once and frozen."

## Non-goals
Not a `deep_trace.md`/checker/router/detector change. Not a recall change (cannot fix recall FPs). Not auto-applied.
Oracle class B is design-only and **not** validated by P201.
