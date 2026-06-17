# Pairwise mechanism selector — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

| case | M1 (impact) | M2 (impact) | gap | anti-easy-PoC | outcome | decisive |
|---|---|---|---|---|---|---|
| pair_0 | KatanaV3Pool.swap skips router-authorization via `if (tx.origin != address(0))` (tx.origin-based access gate) (9) | KatanaV3PoolBeacon.constructor (thin pass-through to OZ UpgradeableBeacon) (1) | 8 | YES | **SELECT_M1** | terminal_impact_dominance; rival weak/refuted; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| pair_1 | KatanaV3Pool.mint/burn concentrated-liquidity amount/fee accounting (9) | V3Migrator.migrate dust/refund handling on V2->V3 migration (2) | 7 | YES | **KEEP_BOTH** | terminal_impact_dominance; both plausible -> protect high-impact before PoC; anti_easy_poc_bias: lower-impact rival is easier to PoC -> do not drop high-impact |
| pair_2 | AggregateRouter/V3SwapRouter swap authorization (governance.isAuthorized) + callback validation (9) | NonfungiblePositionManager.mint AuthorizationLib.checkPair gate (9) | 0 | no | **KEEP_BOTH** | near-equal impact, both plausible -> keep both |
