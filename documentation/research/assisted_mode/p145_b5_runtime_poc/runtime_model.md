# P145 — Runtime Model

## Actors / tokens
- `user` = `0xBEEF` — entitled original owner.
- `avmManager` = `0xA814` — `ownerOf()` for AVM-managed NFTs (the wrong recipient).
- reward `token` — MockERC20.
- tokenIds: `idA`,`idB` AVM-managed (claim / claim_many respectively); `idC`,`idD` non-AVM controls.

## Amount mechanics (real `_claim`)
- WEEK = 1800 (`BlackTimeLibrary.WEEK`). Deploy at `T0 = 100*WEEK`.
- Fund distributor with `R = 1000e18`; warp `+WEEK`; `checkpoint_token()` → `tokens_per_week[w0] ≈ R`.
- Mock VE: `balanceOfNFTAt = S = 1e18`, `totalSupplyAtT = SUP = 1000e18`.
- Per-claim payout `PER = R · S / SUP = 1000e18 · 1e18 / 1000e18 = 1e18` (S<SUP keeps each claim a fraction, so
  successive claims in one test don't underflow `token_last_balance`).
- `locked(id) = {end: T0 (< now), isPermanent: false}` → the direct-transfer branch.

## Expected recipients
| call | tokenId | tokenIdToAVMId | ownerOf | recipient | result |
|---|---|---|---|---|---|
| `claim` | idA | nonzero | avmManager | `getOriginalOwner` = **user** | correct |
| `claim_many` | idB | nonzero | avmManager | `ownerOf` = **avmManager** | **wrong (bug)** |
| `claim` | idC | 0 | user | `ownerOf` = user | control (match) |
| `claim_many` | idD | 0 | user | `ownerOf` = user | control (match) |

## Observed (forge logs)
- `claim(idA)` → user, amount `1e18`.
- `claim_many([idB])` → avmManager, misdirected `1e18`.
- non-AVM control: both pay user (`2e18` total), avmManager `0`.
