# P137 — Post-hoc Grade vs the known H-03 answer key

(Compared ONLY after the blind grade. Answer key: `documentation/research/_p81b/noya/` + the noya answer_key.md
read in P133/P134.)

**Known H-03 (NoyaValueOracle::_getValue):** "oracle multi-hop — loop reuses static `asset` instead of advancing
`quotingToken` → wrong sequential conversion." Awarded **High**, mechanism_class `value_exit`.

| Dimension | Result |
|---|---|
| **Strict match** | ✅ exact — blind output names the static `asset` vs updated `quotingToken` divergence, the precise H-03 mechanism |
| **Useful match** | ✅ |
| **Mechanism accuracy** | ✅ exact (stale loop-carried variable; correct from-token never used in-loop) |
| **Impact accuracy** | ✅ multi-hop mis-valuation of the asset (feeds the value oracle → mis-priced TVL/accounting = `value_exit`) |
| **Severity support** | Consistent with **High** (oracle mis-valuation drives NAV/accounting), but the prompt is research-only and assigned no severity — High requires human + PoC confirmation |
| **Reviewable candidate without answer-key knowledge?** | ✅ yes — a confident `finding` with evidence + repro hint, produced with zero answer-key access |

**Conclusion:** the blind `deep_pass_value_provenance` pass discovered H-03 from source alone — the residual
detector MISS (P134) is converted to a HIT by the prompt, not by a new detector and not by the answer key.

**Bonus (post-hoc):** T3 independently reproduced the H-19 MorphoBlue sign error (awarded High) — but my control
packet annotated asset/liability roles, so T3 is "aided" and is NOT counted as a clean blind generalization;
T1 is the clean result.
