// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract PoolSafe {
    Collateral c; uint256 private _lock;
    modifier nonReentrant() { require(_lock == 0, "reentrant"); _lock = 1; _; _lock = 0; }
    function liquidate(address victim) external payable nonReentrant {
        c.delegate(victim);
        c.settleLiquidation(victim);                                     // settle FIRST (effects)
        (bool ok,) = victim.call{value: msg.value}("");                  // refund last (interaction)
        require(ok);
    }
}
interface Collateral { function delegate(address) external; function settleLiquidation(address) external; }
