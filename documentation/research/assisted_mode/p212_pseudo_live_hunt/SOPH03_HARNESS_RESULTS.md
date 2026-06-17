# SOPH-03 harness results — CONFIRMED MEDIUM (DoS)

`pocs/p212/test/SOPH03_stEth_wrap.t.sol` — `forge test --match-contract SOPH03 -vv` (2/2 PASS).

| scenario | result |
|---|---|
| control: honest stETH (exact delivery) | `depositStEth(100e18)` succeeds → wstETH-pool user.amount = 100e18 |
| bug: stETH 1-wei share-rounding (delivers amount-1) | `depositStEth(100e18)` **REVERTS** |

Root cause: `depositStEth` pulls `_amount` stETH (contract receives `_amount-1` due to stETH share-rounding), then
`_stEthTOwstEth(_amount)` calls `wstETH.wrap(_amount)` which pulls the **full `_amount`** stETH from the contract → the
contract holds `_amount-1` → revert (or, with prior residual, consumes residual).

**Verdict: CONFIRMED — executable, source-valid (real stETH has 1-2 wei rounding), permissionless. Impact = DoS of
stETH deposits (clean-balance case), not theft → L3: FAIL-for-High → calibrated MEDIUM.** Mitigation: wrap the measured
received balance (before/after delta), not the requested `_amount`. Human-reviewable Medium.
