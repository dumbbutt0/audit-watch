# P293 — VERDICT

## A — REWARD_INDEX_LENS_READY_FOR_BLIND_RETEST

The cross-function, naming-flexible reward-index lens recovers the awarded salty locus end-to-end and introduces
zero false READYs.

### A-criteria — all met
- **`_increaseUserShare` becomes READY.** It lifts `LENS3_READY / FIRST_DEPOSITOR_ZERO_SUPPLY` →
  `REWARD_INDEX_INIT_FOUND` (MEDIUM) → gate `READY_FOR_POC_INTENT`. Source-backed: global `totalRewards`, per-user
  `virtualRewards`, share `userShare/totalShares`, first-depositor branch `if (existingTotalShares != 0)`, pending
  formula from sibling `userRewardForPool` (P283 downward trace was empty → resolved via the same-contract sibling).
- **No generic staking/share update becomes READY.** The only other firing (`liquidateUser`) is held by the gate's
  D1 (`INLINE_GUARD_REFUTED`). Plain balance updates / checkpoint-then-mutate / atomic-init are silent or refuted.
- **No false READY introduced.** Exactly **1** genuinely-new READY locus across the corpus vs the P292 baseline =
  the awarded `_increaseUserShare` (a true-positive awarded locus).
- **severe concluded/reportable FP = 0.**
- **Pools.deposit stays not-READY** (`NEEDS_INTEGRATION_DEVIATION_EVIDENCE`; P291 precision held).
- **Regressions preserved:** kelp H-01, blackhole claim_many, L2Governor, ECG H-04 all READY.
- **Tests green** (test_p293 + the full research suite; tracer + gate + router + forbidden 5 byte-identical).

### Honest scope
Supervised, not blind — generalization is unproven until a fresh blind retest. One confirmed positive + 0 FP;
patterns A/B/C/E are FP-safe and unit-tested but lack a corpus positive yet (see LIMITATIONS). The arc is now staged
correctly: surfacing (P291) → admission (P292) → lens (P293, recovers the awarded locus).

### Next
Per the ladder: **A → re-blind a 4th fresh target** to test generalization of the reward-index lens. Still NOT
scaleout until a blind retest is clean.
