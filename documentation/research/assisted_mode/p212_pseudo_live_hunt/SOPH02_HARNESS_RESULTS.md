# SOPH-02 harness results — REFUTED (scaling consistent)

`pocs/p212/test/SOPH02_accPointsPerShare.t.sol` — `forge test --match-contract SOPH02 -vv` (PASS).

Scenario: A deposits 100, B deposits 300; roll 50 blocks; compare `pendingPoints` (view, pre-update) vs after `updatePool`.
| user | pending (view) | pending (after updatePool) | delta |
|---|---|---|---|
| A | 3.125e18 | 3.125e18 | **0** |
| B | 9.375e18 | 9.375e18 | **0** |

**Verdict:** the "1e18 scaling mismatch / view over-report" hypothesis is **REFUTED** — the view's `*1e18 … /1e36`
cancels exactly against the stored `/1e18` settlement, and the unsettled increment matches `updatePool`. View ==
settled (delta 0). **L3: FAIL (source-refuted).** (A separate integer-truncation dust exists in `pointReward/lpSupply`
but is bounded and was not the claimed defect.)
