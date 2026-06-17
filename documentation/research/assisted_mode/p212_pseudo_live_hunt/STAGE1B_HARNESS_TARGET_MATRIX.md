# P212 Stage 1B — harness target matrix

| id | hypothesis | exploit sequence | affected state | loss model | PASS cond | FAIL cond | mocks | source-validity |
|---|---|---|---|---|---|---|---|---|
| SOPH-01 | withdraw() omits boostAmount decrement → conservation break / phantom rewards | deposit(partial boost) → roll → withdraw full depositAmount → inspect amount/boostAmount + pending | UserInfo.amount/boostAmount/depositAmount, pending points | honest depositors diluted by phantom weight | material phantom rewards / dilution | amount==boostAmount (conservation holds) | MockERC20 generic pool | boost is paid (→heldProceeds); persists by design |
| SOPH-02 | accPointsPerShare 1e18 scaling mismatch → pending over-report | 2 users deposit → roll → compare pendingPoints (view) vs post-updatePool settled | accPointsPerShare, pending points | over/under reward allocation | large view-vs-settled delta | delta≈0 (consistent) | MockERC20 generic pool | view *1e18.../1e36 vs stored /1e18 |
| SOPH-03 | depositStEth wraps full _amount vs stETH received (rounding) → DoS | depositStEth under 1-wei stETH rounding; control = honest stETH | stETH custody, wstETH wrap | DoS of stETH deposits (or residual draw) | revert/stuck under source-valid rounding | succeeds always | MockStETH(rounding), MockWstETH(wrap) | real stETH has 1-2 wei share-rounding |
