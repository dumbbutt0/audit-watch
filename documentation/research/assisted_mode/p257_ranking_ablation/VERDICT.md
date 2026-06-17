# P257 — VERDICT

## B — RANKING_PROMISING_NEEDS_MORE_HELDOUT

### What happened
Added the three ranking profiles (A = original P256 gate; B = messy-reconciliation weighted; C = runner-up
challenge) ahead of the unchanged five completion ops, blind + freeze-before-reveal, on subtle accounting/state
loci. **reserve was excluded** (the reveal-availability search leaked its awarded Medium titles → blind test
void), so P257 scored **notional only** (Sherlock, clean blind; 3 loci, 1 with the awarded mechanism enumerated).

**The confirmation (the result that matters):** on **N-L2** (fee accrual), the awarded bug #886 "Double Fee
Accrual in Withdrawal Flow" is the **messy** fee-timing mechanism — and **Profile A ranked the tidy
approximation-error mechanism #1 (mis-ranked), while Profiles B and C both elevated the messy mechanism to #1 and
completed it.** That is the first direct confirmation of the P256→P257 hypothesis: re-weighting toward messy
reconciliation (B) or forcing a runner-up challenge (C) **fixes the exact mis-ranking** P256 exposed. Per-profile
awarded-selected: **A 0/3 · B 1/3 · C 1/3**, 0 severe FP.

### Why B (not A/C/D/E/F)
- **Not A (build-ready):** the bar is ≥2 awarded mechanisms selected correctly across fully-scored loci + B/C
  materially beats A. We have **1** (N-L2) on **1** contest (reserve lost to the precheck leak). Genuine but thin.
- **Not C (discovery dominates) outright:** discovery *is* a live gap (2/3 notional awards — #882 redemption
  reentrancy, #883 migration rewards — were NOT_ENUMERATED), but the phase's question was ranking, and where the
  mechanism *was* enumerated the ranking ablation cleanly worked. So discovery co-dominates rather than dominates.
- **Not D (completion gap):** completion succeeded when the right mechanism was ranked #1 (N-L2 B/C → partial chain);
  completion is not the blocker — consistent with P254–P256.
- **Not E/F:** the profiles were useful (B/C beat A on the enumerated locus); the gate isn't useless.

### The honest synthesis (pooled with P256)
When the awarded mechanism is **enumerated**, the failure is **ranking**, and **B/C-style reweighting fixes it**
(P256 plaza showed the mis-ranking; P257 notional now shows B/C *correcting* it). **But** enumeration/discovery
still misses a large share of awards (P256 plaza 1/3, P257 notional 2/3 not enumerated — auction state-machine,
redemption reentrancy, migration). So the system needs **both** a ranking fix **and** broader discovery; the
ranking fix is promising and now has one clean confirmation, not enough to build on alone.

### Required next step
A larger heldout round (the P257 design, with two fixes):
1. **Precheck fix (now standing):** verify reveal *existence* without award-content searches — protect ≥2 scored
   contests (reserve was lost this way).
2. **Widen enumeration beyond accounting-reconciliation** to include the discovery-missed shapes (reentrancy,
   migration, redemption state-machine) so more awarded mechanisms reach the top-2 where the ranking ablation can
   act on them.
Then: if B or C selects ≥2 awarded mechanisms across ≥2 contests (and beats A) → build that harness (B =
messy-reconciliation ranking; C = runner-up-challenge; they tied here, so design the next round to separate them).
If awarded mechanisms keep being NOT_ENUMERATED → prioritize a discovery harness first.

### Honest caveats
n=1 scored contest (reserve excluded by precheck leak); 1 enumerated locus (1 ranking-ablation data point);
N-L2 B/C match is family-level (messy fee double-accrual family, not verbatim mechanism text); no PoCs (root-cause/
impact match to the Sherlock issue). No softening — A 0/3 reported plainly; B/C's single clean win reported as
promising-not-build-ready.

### Arc
P254(B first blind completion 1/4) → P255(B replication bug-class-confined) → P256(B gate lifts awarded mech to
top-2 2/3 but ranks tidy #1) → **P257(B ablation confirms B/C reweighting fixes the mis-ranking on the one
enumerated locus (#886), A 0/3 vs B/C 1/3; but discovery co-dominates (2/3 not enumerated) and reserve lost to a
precheck content-leak → widen enumeration + protect ≥2 scored contests, then separate B vs C).**
