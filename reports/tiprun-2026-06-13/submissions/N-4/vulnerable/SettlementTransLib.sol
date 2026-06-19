// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../../core/position/IPositionManager.sol";

struct Settlement {
    uint64 accountId;
    uint64 syntheticAssetId;
    int256 settlementPrice; // Fixed-point price to settle at (e.g., 1 for predict YES outcome)
}

/**
 * @title SettlementTransLib
 * @dev Force-settles a user's synthetic position at a given price.
 *      The synthetic is zeroed out and collateral is adjusted accordingly.
 */
library SettlementTransLib {
    function process(Settlement memory self, IPositionManager position) public {
        require(self.accountId != 0, "SettlementTransLib: accountId is 0");
        require(self.settlementPrice >= 0 && self.settlementPrice <= type(int128).max, "SettlementTransLib: invalid settlement price");

        int256 syntheticBalance = position.getSyntheticBalance(self.accountId, self.syntheticAssetId);
        if (syntheticBalance == 0) {
            return;
        }

        // collateralDelta = syntheticBalance * settlementPrice
        // syntheticDelta = -syntheticBalance (zero out the position)
        int256 collateralDelta = syntheticBalance * self.settlementPrice;
        int256 syntheticDelta = -syntheticBalance;

        position.updatePositionInDict(self.accountId, collateralDelta, self.syntheticAssetId, syntheticDelta);
    }
}
