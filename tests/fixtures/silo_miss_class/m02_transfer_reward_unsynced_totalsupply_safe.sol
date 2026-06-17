// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Safe equivalent: pending fee shares are realized into totalSupply BEFORE the reward index is updated, and
// the per-account reward debt is snapshotted against the pre-transfer balance.
contract VaultRewardSynced {
    uint256 public totalSupply;
    uint256 public pendingFeeShares;
    uint256 public rewardIndex;
    mapping(address => uint256) public balanceOf;
    mapping(address => uint256) public rewardDebt;

    function _syncFeeShares() internal {
        if (pendingFeeShares > 0) {
            totalSupply += pendingFeeShares;   // realize before any reward math
            pendingFeeShares = 0;
        }
    }

    function _accrueFor(address account) internal {
        rewardDebt[account] = balanceOf[account] * rewardIndex; // snapshot on pre-transfer balance
    }

    function _update(address from, address to, uint256 amount) internal {
        _syncFeeShares();
        uint256 newRewards = block.number;
        if (totalSupply > 0) {
            rewardIndex += newRewards / totalSupply;   // synced supply
        }
        _accrueFor(from);
        _accrueFor(to);
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        _update(msg.sender, to, amount);
        return true;
    }
}
