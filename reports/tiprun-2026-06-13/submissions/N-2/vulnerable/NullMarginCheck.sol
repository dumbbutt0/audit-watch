// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./IMarginCheck.sol";
import "../position/IPositionManager.sol";

/// @notice No-op margin check. Spot deployments rely on this — there is no
/// maintenance margin in spot, so every transition is "valid" by definition.
contract NullMarginCheck is IMarginCheck {
    function getAccountPositionStatus(AccountPosition memory) external view returns (int256, int256) {
        return (0, 0);
    }

    function checkValidTransition(AccountPosition memory, AccountPosition memory, uint64, uint64) external view {}
}
