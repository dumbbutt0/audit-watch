# P246 — Miss Attribution

Every awarded finding that was **not a DIRECT_HIT** is assigned exactly ONE root cause (the single
improvement most likely to have recovered it). Direct hits (5) are excluded. Partials are listed with their
residual root cause. Buckets: Coverage · Reasoning depth · Oracle freshness · Reward/emission · Economic
invariant · EIP4626 · Permit/signature · Reentrancy · Cross-chain · Governance · Unknown.

## Per-finding (non-direct-hit) attribution
| Contest | Finding | Sev | Result | Root cause |
|---|---|---|---|---|
| decent | H-02 LayerZero min-gas | H | MISSED | Cross-chain |
| decent | H-03 failed-exec funds to random addr | H | PARTIAL | Reasoning depth |
| decent | H-04 lose tx if dst lacks reserves | H | PARTIAL | Cross-chain |
| decent | M-01 stale swap data | M | MISSED | Reasoning depth |
| decent | M-02 fee bypass via bridgeWithPayload | M | PARTIAL | Economic invariant |
| decent | M-04 fixed-fee calc loss | M | MISSED | Economic invariant |
| decent | M-05 refund stuck at adapter | M | MISSED | Cross-chain |
| vultisig | H-02 whitelist bypass | H | PARTIAL | Reasoning depth |
| vultisig | M-01 token should be burnable | M | MISSED | Coverage |
| vultisig | M-02 claim slippage | M | MISSED | Reasoning depth |
| vultisig | M-03 NFT-transfer cap bypass | M | PARTIAL | Reasoning depth |
| kleidi | M-01 proposal gas griefing | M | MISSED | Reasoning depth |
| kleidi | M-02 calldata-index revert | M | PARTIAL | Reasoning depth |
| kleidi | M-03 expiration-update logic | M | MISSED | Reasoning depth |
| centrifuge | M-01 Axelar origin auth | M | MISSED | Coverage |
| centrifuge | M-02 permit front-run | M | MISSED | Permit/signature |
| centrifuge | M-03 wrong DOMAIN_SEPARATOR | M | MISSED | Coverage |
| centrifuge | M-04 dust-deposit DoS | M | PARTIAL | Reasoning depth |
| centrifuge | M-05 shared-escrow claim contention | M | PARTIAL | Reasoning depth |
| centrifuge | M-06 DelayedAdmin/pauser | M | MISSED | Coverage |
| centrifuge | M-07 round-up on withdraw | M | PARTIAL | EIP4626 |
| centrifuge | M-08 ERC1404 restriction bypass | M | MISSED | Coverage |
| munchables | H-01 lockOnBehalf unlock-time griefing | H | PARTIAL | Reasoning depth |
| munchables | M-01 approve+disapprove check | M | MISSED | Reasoning depth |
| munchables | M-03 remainder extra-NFT gain | M | PARTIAL | Reasoning depth |
| munchables | M-04 missing forceHarvest | M | MISSED | Reasoning depth |
| badger | M-01 post-op comparison logic | M | MISSED | Coverage |
| badger | M-02 staking revert bubbling | M | MISSED | Coverage |

## Distribution (29 non-direct-hit awarded findings)
| Root cause | count | share | where |
|---|---|---|---|
| **Reasoning depth** | **13** | **45%** | read-but-missed / shallow (all 6 contests; dominant on fully-read ones) |
| **Coverage** | **7** | **24%** | unread surface (centrifuge gateway/token/admin/restriction, badger core, vultisig token) |
| **Cross-chain** | 3 | 10% | decent LayerZero gas/reserves/refund routing |
| **Economic invariant** | 2 | 7% | decent fee calc / fee bypass |
| **EIP4626** | 1 | 3% | centrifuge withdraw rounding direction |
| **Permit/signature** | 1 | 3% | centrifuge permit front-run (LP read, missed) |
| Oracle freshness / Reward-emission / Reentrancy / Governance / Unknown | 0 | 0% | — (none of the awarded misses; oracle candidate found in badger was not awarded) |
| *(partials count as partially-recovered, listed above with residual cause)* | (12 partials) | | |

## Reading of the distribution
- **Reasoning depth (45%) is the dominant miss cause here** — a shift from P241/P243 where Coverage
  dominated. Cause: on the small/fully-read contests the system read the right code but failed to complete
  the exploit/defense chain (kleidi M-01/M-03, munchables M-01/M-04, vultisig M-02, decent M-01). The P245
  reasoning-depth gate forces a depth record on *rejections* but does not manufacture the missing insight on
  findings the hunter never proposed — so it does not close this bucket.
- **Coverage (24%) concentrates entirely in the coverage-incomplete contests** (centrifuge, badger) + one
  out-of-manifest contract (vultisig token). On those the P245 gate correctly BLOCKS, but blocking ≠
  recovering — the surface still wasn't read.
- **Domain families** (cross-chain, economic, EIP4626, permit) account for ~23% and are diffuse — no single
  detector family would recover more than ~3 findings; oracle-freshness (the P243-recommended future family)
  recovered 0 here (the one oracle candidate found was not awarded).
