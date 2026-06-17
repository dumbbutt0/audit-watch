# P258 — Diagnosis (discovery vs ranking separation)

## Scope scored
- Contests scored: **2** (astaria, ethos) — both reveals retrievable (precheck held); **search-level** reveal
  visibility (not full per-issue), a stated limitation.
- Loci scored: 6 (3 per contest).

## Counts (pooled, conservative)
| metric | value |
|---|---|
| awarded mechanisms examined at my loci | astaria: access-control/0-transfer/fee-on-transfer/uint88-cast/refinance-ask/dust-settle; ethos: #693 rebalance-DoS + non-18-decimal theme |
| awarded enumerated (in my widened sets) | ~0 clean (1 ethos decimals theme adjacent) |
| awarded in top-5 | ~0 clean |
| awarded in top-2 | 0 |
| awarded SELECTED by Profile A | 0 |
| awarded SELECTED by Profile B | 0 |
| awarded SELECTED by Profile C | 0 |
| awarded COMPLETED when selected | 0 |
| severe false positives | 0 |
| operator burden | high (7-family enumeration × 6 loci) |

## Did widened discovery reduce NOT_ENUMERATED?
**No — not on these targets.** Even with 7-family enumeration, the awarded mechanisms were **NOT_ENUMERATED**
(astaria) or an external-dependency DoS I missed (ethos #693). Widening **broadened my candidate breadth** (I did
generate C/D/E/F/G candidates) but it did **not** surface the *specific awarded* mechanisms into top-2/top-5 here.

## Did B/C separate from A? From each other?
- A vs B/C **separation was visible in the ablation** (A picked tidy every locus; B/C picked messy; B≠C at
  astaria A-L2 and ethos E-L3) — the ablation mechanism works.
- **But it didn't matter for scoring:** since the awarded mechanisms weren't enumerated, no profile could select
  them (A 0 / B 0 / C 0). Ranking separation is moot when discovery misses.

## Two confounds (honest)
1. **Target-fit:** astaria's awarded set skews **mechanical / token-compat / access-control / casting / auction-
   griefing** — the exact bug-class P258 excluded by design. So astaria's NOT_ENUMERATED partly reflects
   award-class mismatch, not discovery skill. The precheck verified *retrievability* but not *award-class fit*.
2. **Reveal visibility:** search-level (not full per-issue), so some NOT_ENUMERATED could be ENUMERATED_OUTSIDE_TOP5.
3. **Genuine discovery miss:** ethos #693 (external-AAVE-liquidity DoS on `_rebalance`) is a real subtle bug missed
   even with widening — a true discovery failure, not an excuse.

## Awarded-mechanism class legend (full 6-class vocabulary)
The six classes used to grade each awarded mechanism: `NOT_ENUMERATED` (the dominant outcome here) ·
`ENUMERATED_OUTSIDE_TOP5` · `ENUMERATED_TOP5_BUT_NOT_TOP2` · `ENUMERATED_TOP2_BUT_RANKED_TOO_LOW` (the P257 #886
case, not seen here) · `SELECTED_BUT_NOT_COMPLETED` (not seen — nothing awarded was selected) · `COMPLETED_CORRECTLY`
(0 here). On P258's two contests the awarded mechanisms landed at `NOT_ENUMERATED` (astaria 3/3; ethos ~2/3) with
one ethos decimals theme at best `ENUMERATED_OUTSIDE_TOP5`.

## Per-profile label legend (full 4-label vocabulary)
`SELECTED_AWARDED` (0 for A/B/C here) · `TOP2_AWARDED` (0 — nothing awarded reached any profile's top-2) ·
`MISRANKED_AWARDED` (0 — would require an enumerated-but-mis-ranked award, as P257 #886; none here) ·
`MISSED_AWARDED` (all profiles, all loci — awarded mechanisms were NOT_ENUMERATED).

## Bottleneck (one)
**DISCOVERY_GAP_DOMINATES.** Widening enumeration did not get the awarded mechanisms into top-2 on either contest,
so ranking (B/C) had nothing correct to rank — discovery is the binding constraint (it co-dominated in P257, and
here, given a fair shot, it still dominated). Ranking remains a *confirmed-but-downstream* fix (P257 #886).

## Pooled across P256–P258
- Awarded mechanism reaches top-2 → ranking is the gap and B/C fix it (P256 plaza, P257 notional #886).
- Awarded mechanism does NOT reach enumeration → the dominant, recurring failure (P257 2/3, **P258 ~6/6**), and
  **widening hand-enumeration to 7 families did not fix it** — strongly implying discovery needs *tooling*, not
  just a broader manual checklist.
