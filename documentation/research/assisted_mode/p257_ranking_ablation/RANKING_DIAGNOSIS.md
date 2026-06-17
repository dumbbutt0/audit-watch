# P257 — Ranking diagnosis (Profile A vs B vs C)

## Scored loci (notional only; reserve excluded — precheck-contaminated)
| locus | awarded mechanism | enumerated? | Profile A | Profile B | Profile C |
|---|---|---|---|---|---|
| N-L1 conversion/escrow | redemption reentrancy / migration rewards (#882/#883) | **no** | MISSED | MISSED | MISSED |
| N-L2 fee accrual | double fee accrual in withdrawal (#886) | **yes** | MISRANKED (tidy M1) | **SELECTED (messy M2)** | **SELECTED (messy M2)** |
| N-L3 escrow/withdraw/transient | redemption reentrancy (#882) | **no** | MISSED | MISSED | MISSED |

## Four-class tally (Profile A, scored loci, n=3)
COMPLETED_CORRECTLY 0 · RANKED_HIGH_BUT_NOT_COMPLETED 0 · ENUMERATED_BUT_RANKED_TOO_LOW 1 (N-L2) · NOT_ENUMERATED 2.

## Per-profile awarded-selected
- **Profile A: 0/3** · **Profile B: 1/3** · **Profile C: 1/3** · severe FP: 0.

## Did Profile B or C materially outperform Profile A?
**Yes, on the one locus where the awarded mechanism was enumerated (N-L2):** Profile A ranked the *tidy*
approximation-error mechanism #1 and **mis-ranked** the awarded *messy* double-fee-accrual mechanism; Profiles B
(messy-reconciliation weighted) and C (runner-up challenge) both **elevated the messy mechanism to #1 and
completed it** (partial chain). This is a direct, first confirmation of the P256→P257 hypothesis: re-weighting
toward messy reconciliation / forcing a runner-up challenge **fixes the specific mis-ranking** P256 exposed.

## But — two limits dominate the read
1. **Discovery co-dominates on notional:** 2/3 awarded mechanisms (#882 redemption reentrancy, #883 migration
   reward loss) were **NOT_ENUMERATED** — my accounting-reconciliation loci/mechanisms didn't generate the
   reentrancy/migration shapes. So a ranking harness alone wouldn't have recovered them.
2. **n=1 scored contest, 1 enumerated locus:** reserve was lost to the precheck content-leak, leaving a single
   ranking-ablation data point. Clean, but far too thin to call the ranking gap "solved."

## Mapping to the build-decision tree
- Profile B and C **both** win the one enumerated locus (and tie each other) → *if* this recurs, the leading
  build is a **messy-reconciliation ranking harness** (B) and/or a **runner-up-challenge harness** (C) — they
  agreed here, so the next round should try to separate B vs C.
- The 2/3 NOT_ENUMERATED → **discovery is also a live gap** (reentrancy/migration/redemption shapes), so the next
  round must (a) widen locus/mechanism enumeration beyond accounting-reconciliation, and (b) score ≥2 contests.

## Pooled with P256 (plaza)
P256 plaza: 2/3 ENUMERATED_BUT_RANKED_TOO_LOW (ranking gap), 1/3 NOT_ENUMERATED.
P257 notional: 1/3 ENUMERATED (and B/C fixed the ranking there), 2/3 NOT_ENUMERATED.
Combined signal: **when the awarded mechanism is enumerated, ranking is the gap and B/C-style reweighting helps
(now shown once on each contest direction); but enumeration/discovery itself still misses a large share** — so
ranking and discovery are *both* live, and the ranking-fix is promising but unconfirmed at scale.
