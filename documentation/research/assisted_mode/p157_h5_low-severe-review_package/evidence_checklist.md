# Evidence Checklist

| Check | Result |
|---|---|
| Uses real production contract | ✓ real `LockingMultiRewards` (inherited unmodified) |
| Production source unchanged | ✓ `LockingMultiRewards.sol` byte-identical (mocks/control in test only) |
| Harness isolated / un-wired | ✓ `audits/abracadabra-2024-03-holdout/pocs/p154/` (deps cloned then removed; not wired to production) |
| Corrected reference present | ✓ same real contract with prompt `processExpiredLocks` (isolates processing-timing variable) |
| Matched control present | ✓ active-lock window (boost intended while committed) |
| Foundry tests | ✓ **4/4 passed** (`forge test -vv`) |
| Actual (expired, unprocessed) | A ≈ 525e18 · B ≈ 175e18 (~3:1) — **boost persists after expiry** |
| Expected (expired, processed/corrected) | A ≈ 350e18 · B ≈ 350e18 (~1:1) — fair |
| Delta | A over-accrual ≈ **B loss** (zero-sum) |
| Loss type | reward **redistribution / misallocation** among stakers — **no protocol-fund loss** |
| Attacker privilege | none (unprivileged EOA); cannot force keeper downtime |

Source of record: P154 runtime PoC + runtime_result.md; reachability/severity in P155/P156. This checklist
**reads** those artifacts; it re-proves nothing and changes nothing.
