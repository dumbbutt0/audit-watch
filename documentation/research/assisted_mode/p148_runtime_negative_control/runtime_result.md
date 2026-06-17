# P148 — Runtime Result

| field | value |
|---|---|
| harness_type | **real_contract** (real velodrome `RewardsDistributor`; real `claim`/`claim_many` called) |
| tests | 3 passed / 0 failed / 0 skipped |
| suspected mechanism | B5-style `claim` vs `claim_many` recipient-parity divergence |
| claim(idA) | `deposit_for(idA, 1e18)` |
| claim_many([idB]) | `deposit_for(idB, 1e18)` |
| external recipient (0xBEEF) balance | **0** (no external-recipient transfer in either path) |
| depositForCount | 2 (both siblings routed via `deposit_for`) |
| runtime_status | **runtime_refuted** |
| runtime_confidence | high |
| duplicate_status | duplicate_unknown |

## What this proves
The suspected recipient divergence **cannot occur** in velodrome: `claim` and `claim_many` both route only via
`deposit_for(_tokenId, amount)` to their own tokenId, and neither resolves an external recipient (`ownerOf`/AVM) —
the branch where blackhole's B5 bug lives is **architecturally absent**. The siblings are behaviorally identical.

## Why this is a clean negative-control success
- The candidate was a genuine same-family suspicion (velodrome = blackhole's distributor ancestor), not a strawman.
- The runtime **killed** the suspicion with positive evidence (both `deposit_for`, external recipient untouched),
  not by absence of testing.
- It is classified `runtime_refuted` — the first use of the negative vocabulary — sitting alongside the three
  `runtime_confirmed` rows without contaminating the prompt baseline.

## Honesty / scope
`duplicate_unknown` (no local answer key). The refutation is **specific to the recipient-divergence axis**; it is
not a claim about any other velodrome property. Not submission-ready (it is a refutation, not a finding).
