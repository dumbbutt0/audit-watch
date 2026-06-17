# P256 — Selection diagnosis (discovery vs ranking vs completion)

## Scored loci (plaza only; concrete reveal unavailable)
| contest | locus | awarded-mechanism class | in gate top-2? | selected==awarded? |
|---|---|---|---|---|
| plaza | P-L1 collateral-level pricing | ENUMERATED_BUT_RANKED_TOO_LOW (region) | yes (runner-up) | no |
| plaza | P-L2 fee accounting | ENUMERATED_BUT_RANKED_TOO_LOW (clean) | yes (runner-up) | no |
| plaza | P-L3 auction/coupon | NOT_ENUMERATED | no | no |
| concrete | C-L1/2/3 | UNSCORED (reveal unavailable) | — | — |

## Four-class tally (scored loci, n=3, plaza)
| class | count |
|---|---|
| COMPLETED_CORRECTLY | **0** |
| RANKED_HIGH_BUT_NOT_COMPLETED | 0 |
| ENUMERATED_BUT_RANKED_TOO_LOW | **2** (P-L2 clean, P-L1 region) |
| NOT_ENUMERATED | 1 (P-L3; + P-L1's exact exploit, partially) |

## Primary diagnostic — discovery vs ranking vs completion
- **Completion is NOT the bottleneck here:** 0 RANKED_HIGH_BUT_NOT_COMPLETED. When the gate ranked a mechanism #1
  it completed it fine; the problem is upstream of completion.
- **The gap splits between RANKING and DISCOVERY:**
  - **Ranking gap (the encouraging signal):** in **2/3** loci the awarded mechanism was **in the gate's top-2**
    (runner-up) — the gate's enumeration *reached* the awarded mechanism — but it **ranked a wrong mechanism #1**
    both times. This is materially better than P255 blind selection, where the awarded mechanism was not even
    tracked as a runner-up. So the 8-dimension gate **improves enumeration/recall of the awarded mechanism into
    the candidate set**, but its **ranking** picks the wrong #1.
  - **Discovery gap:** P-L3 (auction state-machine: endAuction DoS / premature termination) was NOT_ENUMERATED,
    and P-L1's *exact* exploit (split-deposit convexity) was a refinement the runner-up didn't name. So discovery
    still misses a class of bugs (state-machine / convexity).
- **Net:** the dominant *identifiable* failure when the mechanism WAS reachable is **ranking** (2/2 enumerated
  cases were ranked-too-low); but discovery still fails on ~1.5/3 loci. Evidence is split, n=1 contest scored.

## Did the gate beat P255 blind selection?
Yes, partially: P255 awarded-mechanism-selection was 1/4 (loopfi) and 0/1 (bakerfi subtle), and the awarded
mechanism was not tracked as an explicit runner-up. P256's gate put the awarded mechanism in the **top-2 in 2/3**
plaza loci. But **selected-and-correct is still 0/3** — the gate's *ranking* did not convert top-2 presence into a
#1 pick, and there are **0 COMPLETED_CORRECTLY**.

## What this points to (per the user's decision rule)
- Repeated `ENUMERATED_BUT_RANKED_TOO_LOW` → **mechanism-ranking harness** is the leading candidate.
- But P-L3 `NOT_ENUMERATED` + concrete unscored mean discovery cannot be ruled out, and the sample is n=1 contest.
- → Disambiguate with a confirmation run on ≥1 more **fully-revealed** subtle contest before building. If ranking-
  too-low recurs, build the ranking harness; if not-enumerated recurs, build discovery.
