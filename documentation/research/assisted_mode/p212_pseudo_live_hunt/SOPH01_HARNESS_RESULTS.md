# SOPH-01 harness results — REFUTED (conservation holds)

`pocs/p212/test/SOPH01_withdraw_boost.t.sol` — `forge test --match-contract SOPH01 -vv` (PASS).

Scenario: A deposits 100 with boost 40 (boosterMultiplier 2x), B deposits 100 plain; roll; A withdraws full deposit slice.
| state | value |
|---|---|
| A.amount preW / postW | 140e18 → **80e18** |
| A.boostAmount preW / postW | 80e18 → **80e18** (unchanged) |
| A.depositAmount postW | 0 |
| conservation `amount==boostAmount` (deposit=0) | **YES** |
| A LP returned | 60e18 (deposit slice); 40e18 boost went to heldProceeds (paid) |
| A pending @110 / @130 (deposit=0) | 1.458e18 → 3.68e18 |

**Verdict:** the "conservation break" hypothesis is **REFUTED** — `withdraw` reduces `amount` by the deposit slice,
leaving `amount == boostAmount`; accounting is consistent. The residual is the **paid boost weight** (A spent 40 LP to
heldProceeds for permanent purchased weight), which persists by design. Observation: a booster keeps earning points
after withdrawing their deposit (economic quirk, at most Low/Medium, plausibly intended). **L3: FAIL (no material
High; hypothesis invalid).**
