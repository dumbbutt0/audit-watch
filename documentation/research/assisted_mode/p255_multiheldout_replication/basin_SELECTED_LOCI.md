# basin — Phase 2: Selected loci + no-hindsight locks (PRE-REVEAL)

3 loci selected before the key was opened. All `BASE_BORN_INCOMPLETE`. ≥1 accounting (L1) and ≥1 state/upgrade
(L2, L3). Disclosed-exposed Well MEV/donation area not selected.

## L1 ← B1 — `Stable2.decodeWellData` (accounting / units-decimals)
- **Why selected (pre-reveal):** clearest mechanical bug; a copy-paste typo in decimals defaulting can mis-scale all pricing.
- **Signal:** base rank #1 + accounting A1/A5 on calc* (which consume scaled reserves).
- **What base already completed:** identified the typo (`decimal0` re-checked instead of `decimal1`).
- **What remained incomplete:** *when* does it bite (which token-decimals config), who loses, and the oracle/swap impact — not computed.

## L2 ← B2 — `Stable2.calcReserveAtRatioSwap` / `calcLpTokenSupply` silent non-convergence (state / terminal-state)
- **Why selected (pre-reveal):** asymmetry with `calcReserve` (which reverts) suggests an unhandled terminal state that a consumer trusts.
- **Signal:** base rank #3 + accounting A5 on the converging loops.
- **What base already completed:** saw the loops fall through without revert.
- **What remained incomplete:** can crafted reserves force non-convergence, and what does a downstream pump/oracle do with the 0/unconverged return — not traced.

## L3 ← B3 — `WellUpgradeable.init` / upgrade authorization (state-transition / adversarial-actor)
- **Why selected (pre-reveal):** upgradeable + `reinitializer(2)` + minimal-proxy UUPS is a classic init/upgrade hazard surface.
- **Signal:** state-transition checkpoint fired on `init`.
- **What base already completed:** noted `init` lacks explicit access control beyond `reinitializer(2)`; `_authorizeUpgrade` requires delegatecall.
- **What remained incomplete:** whether an attacker can take over the implementation or a freshly-bored well, or brick via the minimal-proxy upgrade path — not resolved.

**FREEZE:** final, recorded before reveal.
