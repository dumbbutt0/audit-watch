# P258 — VERDICT

## Bottleneck: DISCOVERY_GAP_DOMINATES
## Verdict: NEEDS_MORE_HELDOUT

### What happened
P258 gave **discovery a fair shot**: 7-family widened enumeration **before** the A/B/C ranking ablation, blind,
on two clean subtle contests (astaria, ethos; existence-precheck held, no content leaked). Result: the awarded
mechanisms were **NOT_ENUMERATED** at essentially all 6 loci — **Profile A/B/C each selected 0 awarded
mechanisms**, 0 completed, 0 severe FP. The A/B/C separation was visible in the ablation (A tidy; B/C messy; B≠C
at astaria A-L2 and ethos E-L3) but **moot for scoring** because discovery didn't surface the awarded mechanisms.

### Why this bottleneck
Widening hand-enumeration to 7 families **broadened candidate breadth but did not reach the specific awarded
mechanisms**: astaria's awards were mechanical/access-control/token-compat/casting (e.g. transferWithdrawReserve
access-control, #54 zero-transfer DoS, #375 uint88 cast, refinance-low-ask); ethos's clearest (#693) is an
**external-AAVE-liquidity availability DoS** on `_rebalance` I missed. So **discovery is the binding constraint**
(it co-dominated in P257 and dominates here) — ranking (B/C), already shown to work *when* the mechanism is
enumerated (P257 #886), had nothing correct to act on.

### Why NEEDS_MORE_HELDOUT (not BUILD_DISCOVERY_HARNESS yet)
The discovery-gap signal is real and now the clear priority, but **three confounds** make committing to a build
premature on this round:
1. **Target-fit (astaria):** its awarded set is the **mechanical/token-compat class P258 explicitly excluded** —
   so astaria's NOT_ENUMERATED partly reflects award-class mismatch, not discovery skill. The existence precheck
   verified *retrievability* but **not award-class fit** (new lesson).
2. **Reveal visibility:** search-level, not full per-issue — some NOT_ENUMERATED could be ENUMERATED_OUTSIDE_TOP5.
3. **n=2**, and only ethos #693 is an unambiguous genuine subtle discovery miss.
Per the standing no-softening rule, I also will not over-claim a ranking result (B/C selected 0 awarded here).

### Required next step (P259)
One more round with **two precheck/target upgrades**, then commit:
1. **Award-class target-fit screen** (content-safe): prefer protocols whose award *history* is subtle-accounting
   (use category-level priors, not the specific contest's findings) — avoid contests whose awards are
   mechanical/token-compat/access-control.
2. **Full per-issue reveal scoring** (not search-level) to place every awarded mechanism in the 6 classes exactly.
Then: if awards remain NOT_ENUMERATED on **award-class-fit** subtle targets → **BUILD_DISCOVERY_HARNESS** (the
manual 7-family checklist is insufficient; discovery needs tooling — e.g. mechanism-shape generators for external-
dependency DoS, decimal-conversion, state-machine reInsert, that hand-enumeration keeps missing). If widened
discovery + B/C then selects ≥2 awarded across ≥2 contests → revisit the ranking-harness verdicts (B vs C).

### Honest synthesis (P256→P258 arc)
- When the awarded mechanism **is enumerated**, ranking is the gap and B/C reweighting fixes it (P256 plaza mis-rank;
  P257 notional #886 corrected).
- But the awarded mechanism **often isn't enumerated**, and **widening the manual family checklist did not fix
  that** (P258). ⇒ **Discovery is the leading bottleneck; it likely needs tooling, not a bigger checklist.**
- Build order implied: **discovery harness first**, then the (already-validated-in-principle) ranking harness on
  top — i.e. trending toward the user's "top-2 discovery + ranking" combined harness, but discovery must be proven
  first on award-class-fit targets.

### Caveats
n=2; search-level reveal; astaria target-fit; training-confound (famous 2023 contests); no PoCs; B/C separation
observed but unscored (0 awarded enumerated). No softening — A/B/C 0-selected reported plainly.

### Arc
P255(B bug-class-confined) → P256(B top-2 2/3, ranks tidy #1) → P257(B B/C fix mis-ranking on the 1 enumerated
locus; discovery co-dominates) → **P258(DISCOVERY_GAP_DOMINATES; widened 7-family hand-enumeration still
NOT_ENUMERATED, A/B/C 0-selected; NEEDS_MORE_HELDOUT on award-class-fit targets + full reveal, then build the
discovery harness — likely tooling, not a bigger checklist).**
