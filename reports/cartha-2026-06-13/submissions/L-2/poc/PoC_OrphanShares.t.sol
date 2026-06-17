// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {CarthaVaultPoolTest} from "./vault/CarthaVaultPool.t.sol";
import {CarthaVault} from "../src/CarthaVault.sol";

/// @title PoC (L-2): child shares are transferable post-lock but only redeemable via a Position
/// @notice CarthaVault has no position-independent redeem; redemption (release/forceExit/processQueuedWithdrawals) is
/// Position-bound. But shares are ERC20-transferable once the lock expires (_update only blocks while locked). Shares
/// moved to an address without a Position are ORPHANED: non-redeemable, yet still counted in totalSupply.
contract PoC_OrphanShares is CarthaVaultPoolTest {
    function test_PoC_transferredSharesAreOrphaned() public {
        CarthaVault cv = CarthaVault(address(vault));
        uint64 lockDays = 30;

        // user1 deposits + locks -> gets shares + a Position
        _depositAndLock(user1, MIN_LOCK, lockDays);
        uint256 shares = cv.balanceOf(user1);
        assertGt(shares, 0, "user1 has shares");
        uint256 supplyBefore = cv.totalSupply();

        // lock expires -> shares become transferable
        _expireLock(lockDays);

        // user1 transfers half its shares to user3 (who has NO position in this pool)
        uint256 moved = shares / 2;
        vm.prank(user1);
        cv.transfer(user3, moved);
        assertEq(cv.balanceOf(user3), moved, "user3 received shares");
        assertEq(cv.totalSupply(), supplyBefore, "supply unchanged by transfer (orphan shares still counted)");

        // user3 holds shares but has NO redemption path: release() reverts (no Position), and there is no
        // redeem(shares) entrypoint. The shares are stuck.
        vm.prank(user3);
        vm.expectRevert(); // PositionNotFound — user3 has no position for this pool
        vault.release(poolId, 1);

        vm.prank(user3);
        vm.expectRevert(); // requestRelease also requires a Position
        vault.requestRelease(poolId);

        // The orphaned shares remain in supply, diluting _convertToAssets for everyone else.
        assertEq(cv.balanceOf(user3), moved, "user3 still holds non-redeemable shares");
        emit log_named_uint("orphaned (non-redeemable) shares held by user3", moved);
    }
}
