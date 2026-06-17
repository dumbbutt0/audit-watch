// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// M-04: interest only accrues when block.timestamp > lastUpdate → a borrow and repay in the SAME block pay
// zero interest (interest-free flash loan of the lent asset).
contract Vault {
    function _updateGlobalInterest() internal returns (uint256 rate) {
        if (block.timestamp > lastUpdate) { rate = _accrue(); lastUpdate = block.timestamp; }
        else { rate = lastRate; }   // BUG: same-block borrow+repay accrues nothing
    }
}
