# munchables-2024-05-holdout — SCORECARD

Freeze hash: 545d5dd242f5efc7749657a3687c8d7220324c4043f3e73582547ff0aa682a14 (before reveal).
Sealed-key hash: e1fe145591bd3576. Awarded: 2 High + 4 Medium = 6 — **all in LockManager + MigrationManager
(the two contracts read)**.

## Awarded-finding scoring
| Awarded | Sev | My candidate | Class | Credit |
|---|---|---|---|---|
| H-01 lockOnBehalf repeatedly extends victim unlockTime → withdrawal DoS | High | (read lockOnBehalf/_lock; flagged setLockDuration not the on-behalf griefing) | SAME_AREA_WRONG_MECHANISM | 0.25 |
| H-02 invalid validation allows early unlock | High | MU-H1 (setLockDuration unlockTime=lastLockTime+duration → early unlock) | DIRECT_HIT | 1.0 |
| M-01 approveUSDPrice missing disapproval check (approve+disapprove) | Medium | (read the fn; dismissed) | MISSED | 0 |
| M-02 lockOnBehalf from MigrationManager sets remainder=0 → fewer NFTs | Medium | MU-M2 (remainder reset to 0 in _lock) | SAME_ROOT_CAUSE | 0.5 |
| M-03 players gain extra NFTs from past remainder in subsequent locks | Medium | MU-M2 (same remainder code, opposite exploit) | SAME_AREA_WRONG_MECHANISM | 0.25 |
| M-04 schnibbles not harvested in setLockDuration | Medium | (read setLockDuration; missed missing forceHarvest) | MISSED | 0 |

## System-finding scoring (precision)
MU-H1→AWARDED_EQUIVALENT(H-02); MU-M2→AWARDED_EQUIVALENT(M-02/M-03 area); MU-M1 (mixed-token migration
tokenLocked overwrite)→PLAUSIBLE (not awarded); MU-M3 (uint8 loop overflow)→PLAUSIBLE; MU-L1→PLAUSIBLE
(H-01 family). Hard FP: 0.

## Metrics
- High recall: strict (DIRECT) 1/2 = 50%; credited 1.25/2 = 63%.
- Medium recall: strict 0/4 = 0%; credited 0.75/4 = 19%.
- Weighted recall (H=3,M=1; denom 10): numerator 4.5 → **45.0%**.
- Coverage completeness: ~17% overall (38/224 critical) — **gate would BLOCK** — BUT the awarded findings
  concentrated in the two high-value managers that were read (prioritized reading paid off).
- Advisory lens contribution: 0. Proof: BLOCKED_BY_BUILD.

## Miss attribution
- H-01 → partially credited; residual **Reasoning depth** (lockOnBehalf griefing, read but missed)
- M-01 → **Reasoning depth** (missing disapproval check, read but missed)
- M-04 → **Reasoning depth** (missing forceHarvest, read but missed)

## Note
Key nuance: overall coverage was low, yet recall was 45% because the awarded findings clustered in the
lock/migration managers that were prioritized. Remaining misses are **read-but-missed (reasoning depth)**,
not coverage — even on the right files, depth capped recall. Training-data confound applies.
