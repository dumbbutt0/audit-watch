// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Silo M-02 (reconstructed shape, no answer-key text): a share transfer updates reward accounting using a
// totalSupply that was NOT synced with pending fee shares, so the reward index is computed against a stale
// supply and reward is mis-accrued on transfer/transferFrom. The reward-accounting checklist
// (totalsupply_sync_before_accrual / transfer_side_effects / rewards_on_share_transfer) is what catches this.
contract VaultRewardUnsynced {
    uint256 public totalSupply;          // share supply, EXCLUDING pending fee shares
    uint256 public pendingFeeShares;     // accrued but not-yet-minted fee shares
    uint256 public rewardIndex;
    mapping(address => uint256) public balanceOf;
    mapping(address => uint256) public rewardDebt;

    // BUG: reward index uses `totalSupply` without first minting/accounting pendingFeeShares, and the
    // balance snapshot is taken AFTER the transfer mutates balances.
    function _update(address from, address to, uint256 amount) internal {
        uint256 newRewards = block.number; // stand-in for an external reward stream
        if (totalSupply > 0) {
            rewardIndex += newRewards / totalSupply;   // stale supply: ignores pendingFeeShares
        }
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        // snapshot AFTER mutation → from/to accrue against the wrong balance
        rewardDebt[from] = balanceOf[from] * rewardIndex;
        rewardDebt[to] = balanceOf[to] * rewardIndex;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        _update(msg.sender, to, amount);
        return true;
    }
}
