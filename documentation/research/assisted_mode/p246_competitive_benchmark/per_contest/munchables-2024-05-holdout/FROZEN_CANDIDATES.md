# munchables-2024-05-holdout — FROZEN CANDIDATES (blind, pre-reveal)

Architecture: GameFi on Blast — LockManager (lock tokens→points/NFTs), MigrationManager (old→new NFT
migration), Account/Snuggery/Claim/Rewards/Bonus managers, NFTOverlord, ConfigStorage. Sealed-key hash
e1fe145591bd3576 (not opened). **Coverage note:** 224 critical; I fully read LockManager + MigrationManager
(~38 critical, ~17%); did NOT read AccountManager/SnuggeryManager/ClaimManager/RewardsManager/NFTOverlord/
ConfigStorage/etc → **coverage-INCOMPLETE**; P245 gate would BLOCK. Misses in unread managers are
Coverage-attributed. Advisory lenses: 0.

## Candidates (base hunt, LockManager + MigrationManager)
| id | sev | locus | mechanism |
|---|---|---|---|
| MU-H1 | High | LockManager.setLockDuration | unlockTime recomputed as `lastLockTime + _duration` (not `block.timestamp + _duration`); the guard only checks `block.timestamp + _duration < unlockTime`. A player with an old `lastLockTime` can set a duration that yields an unlockTime at/near the past → unlock earlier than intended / manipulate lock period. |
| MU-M1 | Medium | MigrationManager.loadMigrationSnapshot | `_userLockedAmounts[_user].tokenLocked = data[i].token` is overwritten per snapshot; if a user has snapshots in BOTH USDB and WETH, `totalLockedAmount` sums across tokens but `tokenLocked` keeps only the last → migration locks a single (wrong) token for the combined amount → fund/accounting mismatch. |
| MU-M2 | Medium | LockManager._lock | locking OUTSIDE the lockdrop window sets `lockedToken.remainder = remainder` where `remainder` defaults to 0 → wipes any previously accumulated fractional remainder (lost value); also no NFT reveal outside lockdrop. |
| MU-M3 | Low/Med | MigrationManager._migrateNFTs | loop counter is `uint8 i`; `migratePurchasedNFTs` passes a user-supplied `tokenIds` array — >255 entries overflow/revert → batch DoS (bounded). |
| MU-L1 | Low | MigrationManager.migrateAllNFTs / burnNFTs | permissionless `_user` processing (anyone completes another user's migration once they've chosen an action). |

## Gate / proof status
P245 gate: would **BLOCK** (coverage incomplete: ~38/224 critical read). Proof: BLOCKED_BY_BUILD.
FREEZE: final pre-reveal.
