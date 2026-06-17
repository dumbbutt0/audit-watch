// SPDX-License-Identifier: MIT
// Fixture for the liquidation_health_accounting PROMOTION wiring tests (high-only routing + helper-volume
// control). `liquidate` is a high external entrypoint that calls the internal helper `_seize` (attached as
// context, not routed); `_redeemOrphan` is a high internal helper with no candidate-entrypoint caller (routes
// standalone). One contract, deterministic confidences.
pragma solidity ^0.8.0;

contract Bank {
    function liquidate(address b) external {
        uint256 debtInColl = state.debt(b);
        uint256 liquidatorProfit = debtInColl + reward;
        uint256 collateralRemainder = assignedCollateral - liquidatorProfit;
        _seize(b, collateralRemainder);
    }
    function _seize(address b, uint256 amt) internal {
        uint256 collateralRemainder = amt - debtRepaid;
        collateralToken.transferFrom(b, msg.sender, collateralRemainder);
    }
    function _redeemOrphan(address b) internal {
        uint256 collDrawn = totalColl.sub(debtToOffset);
        collateralToken.transfer(b, collDrawn);
    }
}
