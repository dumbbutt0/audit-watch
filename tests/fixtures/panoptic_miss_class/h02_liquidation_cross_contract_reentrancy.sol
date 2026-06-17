// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// H-02 shape: the ETH refund is sent BEFORE settlement state is finalized → a malicious liquidatee
// contract reenters during the refund and converts delegated phantom shares into real ones.
contract Pool {
    Collateral c;
    function liquidate(address victim) external payable {
        c.delegate(victim);                                              // phantom shares delegated
        (bool ok,) = victim.call{value: msg.value}("");                  // <-- external call before settle
        require(ok);
        c.settleLiquidation(victim);                                     // settlement happens AFTER refund
    }
}
interface Collateral { function delegate(address) external; function settleLiquidation(address) external; }
