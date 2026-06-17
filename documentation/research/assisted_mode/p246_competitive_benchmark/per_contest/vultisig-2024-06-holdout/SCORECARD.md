# vultisig-2024-06-holdout — SCORECARD

Freeze hash: 632f76c5da1e7f1a1d651b0c3860cfa0dcb0674ee0153deb871dde619dbb01ae (before reveal).
Sealed-key hash: 9f6adb9a8ff29753. Awarded: 3 High + 3 Medium = 6.

## Awarded-finding scoring
| Awarded | Sev | My candidate | Class | Credit |
|---|---|---|---|---|
| H-01 most users can't claim their Uniswap fee share (fee accounting) | High | V-H1 (uninitialized feeGrowthInside baseline → claim over-collection) | DIRECT_HIT | 1.0 |
| H-02 whitelisting can be bypassed by anyone | High | V-L1 (whitelist checks `recipient`, not buyer) | SAME_ROOT_CAUSE | 0.5 |
| H-03 adversary blocks launch via single-sided liquidity (price) | High | V-M2 (launch requires slot0==initialPrice; swap → DoS) | DIRECT_HIT | 1.0 |
| M-01 Vultisig token should be burnable | Medium | — (VultisigToken not in ILO manifest read set) | MISSED | 0 |
| M-02 claim lacks slippage controls on pool.burn amounts | Medium | — | MISSED | 0 |
| M-03 NFT transfer bypasses maxCapPerUser | Medium | (examined buy/maxCapPerUser; missed transfer bypass) | SAME_AREA_WRONG_MECHANISM | 0.25 |

## System-finding scoring (precision)
V-H1→AWARDED_EQUIVALENT(H-01); V-M2→AWARDED_EQUIVALENT(H-03); V-L1→AWARDED_EQUIVALENT(H-02 root);
V-H2 (refund `_refundTriggered` blocks launch)→PLAUSIBLE (real launch-griefing vector, not separately awarded
as H/M; akin to launch-DoS family); V-M1 (unprotected ILOManager.initialize)→PLAUSIBLE; V-M3 (0.7.6
underflow)→PLAUSIBLE/BENIGN; V-L2 (gas)→BENIGN. False positives: 0.

## Metrics
- High recall: strict (DIRECT) 2/3 = 67%; credited 2.5/3 = 83%.
- Medium recall: strict 0/3 = 0%; credited 0.25/3 = 8%.
- Weighted recall (H=3,M=1; denom 12): numerator 7.75 → **64.6%**.
- Precision: 0 FP; 3 AWARDED_EQUIVALENT + 3 PLAUSIBLE + 1 BENIGN.
- Coverage: 100% of in-scope ILO manifest read (47/47 critical). Gate PASS. (M-01's VultisigToken not in the
  ILO manifest's in-scope set → see attribution.)
- Advisory lens contribution: 0. Proof: BLOCKED_BY_BUILD.

## Miss attribution
- M-01 → **Coverage** (VultisigToken contract not in the ILO in-scope manifest that was read)
- M-02 → **Reasoning depth** (missing slippage on claim burn — economic/depth)
- M-03 → **Reasoning depth** (NFT-transfer invariant bypass of maxCapPerUser)

## Note
Training-data confound applies (public C4 findings); recorded for aggregate honesty.
