# P289 — VERDICT

## Verdict: **A — LOSS_REWARD_LENSES_READY_FOR_BLIND_RETEST**

## Core question
Can general loss/slash/reward-index/share-transfer lenses make surfaced ECG-style loci READY with source-backed evidence
without increasing false READYs? **Answer: yes (for the loss-on-stake family).** The exact awarded ECG **H-04**
(`SurplusGuildMinter.stake`) now lifts to READY via a generic, source-faithful Lens 1 match (incomplete same-block-only
loss guard), and the remaining ECG awarded loci stay blocked for precise source-backed non-lens reasons — with **0 false
READY** corpus-wide and all regressions stable.

## Scorecard vs the A-bar
| criterion | result |
|---|---|
| ≥1 ECG exact-locus awarded candidate becomes READY (or all blocked for precise non-lens reasons) | ✔ (H-04 stake READY; H-03/H-02 precisely blocked) |
| no false READY in audit | ✔ (corpus-wide: 2 lens matches, 1 lift = the awarded locus, 1 held) |
| kelp H-01 regression stable | ✔ (getRsETHAmountToMint READY) |
| blackhole claim_many regression stable | ✔ |
| L2Governor regression stable | ✔ |
| severe concluded/reportable FP = 0 | ✔ (ECG + kelp + blackhole + panoptic + silo + revert-lend + hybra) |
| no production-authority leakage | ✔ (advisory; reused platform + frozen-others byte-identical) |
| tests green | ✔ |

## What this buys
P288 showed mechanism derivation was lens-bounded; P289 adds a lens family and **immediately converts a previously
0-READY fresh-blind awarded High to READY**, source-faithfully, with no FP. The loss-on-stake lens is corpus-validated;
the other three are FP-safe but await a positive on a future target.

## Honest limits
Only Lens 1 has a confirmed positive. H-03 (onBid) needs Lens 2 extended over the P283 trace path (bad-debt write in a
callee); H-02 (transfer) needs a rebase-share-accounting sub-lens. These are precise, backlogged next repairs — not FPs.

## Production authority
**WITHHELD.** Research/eval/advisory only; ECG used for evaluation, never hard-coded.

## Next
Per the cycle: **re-blind a third fresh target (P290)** to test whether the new lenses generalize (the P287/P288
protocol), before any recall scaleout. If a target with a confirmed contagion/index-init/transfer-theft award appears,
it also exercises Lenses 2–4 on a positive.
