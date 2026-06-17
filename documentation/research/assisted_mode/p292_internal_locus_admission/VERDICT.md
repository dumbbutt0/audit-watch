# P292 — VERDICT

## Verdict: **B — INTERNAL_LOCUS_ADMISSION_PROMISING_NEEDS_REFINEMENT**

## Core question
Can the coverage/queue layer admit distinct internal reward/accounting/share/index loci even when a same-class candidate
exists, without monoculture or false READYs? **Yes — admission is repaired.** The P291-blocked awarded locus
`StakingRewards._increaseUserShare` is now ADMITTED and REACHES Lens 3, bounded, with 0 false READY and stable diversity.
But Lens 3 cannot LIFT it (reward-index logic not span-local) → per the agreed ladder, "reaches Lens 3 but Lens 3 still
cannot lift" = **B**.

## Scorecard
| criterion | result |
|---|---|
| `_increaseUserShare`-style internal locus ADMITTED to the queue | ✔ (3 admitted incl. the awarded locus; reaches Lens 3) |
| no generic EXTERNAL_INTEGRATION READY regression | ✔ (Pools.deposit still NEEDS_INTEGRATION_DEVIATION_EVIDENCE) |
| no false READY introduced | ✔ (admitted loci → precise NEEDS_VALUE_FLOW; 0 READY added) |
| internal expansion bounded | ✔ (≤1/audit; caps 2/class,5/contest) |
| class diversity acceptable | ✔ (max class fraction ≤0.27; monoculture OK on all 8) |
| severe concluded/reportable FP = 0 | ✔ |
| regressions kelp H-01 / blackhole claim_many / L2Governor / ECG H-04 preserved | ✔ (all READY) |
| tests green | ✔ (363 P260–P291 + P292) |

## Why B not A
The A-bar (admission) is met, but the END goal — Lens 3 actually firing on the reward-index bug — is not: all 3 admitted
internal loci get NEEDS_VALUE_FLOW (NO_REFERENCE) because Lens 3's reward-index detection is span-local and the index
logic lives in a callee / uses non-standard naming. Per the user's explicit framing ("B because the locus reaches Lens 3
but Lens 3 still cannot lift, fix the lens/gate next") this is B.

## Net effect
The P291→P292 admission chain is now closed end-to-end up to the lens: surfaced (P291) → admitted past duplicate-class
dedup → reaches Lens 3 (P292). The binding residual moved one stage deeper: Lens 3's reward-index matching. Default dedup
preserved; router byte-identical; 0 false READY; regressions stable.

## Production authority
**WITHHELD.** Research/advisory only.

## Next
Fix the lens/gate (P293): Lens 3 over the P283 trace path OR broaden reward-index/user-share terms (with refutation to
keep FP=0) so the admitted `_increaseUserShare` lifts or precise-blocks on a real reward-index signal. Then re-blind.
NOT scaleout.
