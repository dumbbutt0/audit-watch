// SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import { Test } from "forge-std/Test.sol";
import { console2 } from "forge-std/console2.sol";
import { CuratorRewardsDistributor } from "phi/reward/CuratorRewardsDistributor.sol";

/// @notice P117 runtime harness — unbounded-loop reward-distribution DoS in CuratorRewardsDistributor.distribute.
/// Real distributor + minimal selector-compatible mocks (distribute() only calls isExist / getCuratorAddresses /
/// getShareNumber on Cred, and depositBatch on PhiRewards). The mock UNDERSTATES real cost (no per-curator storage
/// reads), so measured gas is a CONSERVATIVE LOWER BOUND on the real system. SCAFFOLD/RUNTIME ONLY — no severity,
/// no report, no submission.
contract MockCred {
    uint256 public n;
    function setN(uint256 n_) external { n = n_; }
    function isExist(uint256) external pure returns (bool) { return true; }
    function getShareNumber(uint256, address) external pure returns (uint256) { return 1; }
    function getCuratorAddresses(uint256, uint256, uint256) external view returns (address[] memory a) {
        a = new address[](n);
        for (uint256 i = 0; i < n; i++) { a[i] = address(uint160(i + 1)); }
    }
}
contract MockPhiRewards {
    function depositBatch(address[] calldata, uint256[] calldata, bytes4[] calldata, string calldata) external payable {}
}

contract CuratorDistributeDoS is Test {
    CuratorRewardsDistributor dist;
    MockCred cred;
    MockPhiRewards rewards;
    uint256 constant CRED = 1;
    uint256 constant MAINNET_BLOCK_GAS = 30_000_000;

    receive() external payable {}

    function setUp() public {
        vm.deal(address(this), 1_000_000 ether);
        cred = new MockCred();
        rewards = new MockPhiRewards();
        dist = new CuratorRewardsDistributor(address(rewards), address(cred));
    }

    function _once(uint256 n) internal returns (uint256 used) {
        cred.setN(n);
        if (dist.balanceOf(CRED) == 0) dist.deposit{ value: 1 ether }(CRED, 1 ether);
        uint256 g = gasleft();
        dist.distribute(CRED);
        used = g - gasleft();
    }

    function test_A_smallN_succeeds() public {
        uint256 used = _once(10);
        console2.log("CASE A: N=10 distribute gas:", used);
        assertLt(used, MAINNET_BLOCK_GAS, "small N must fit one block");
    }

    function test_B_gas_grows_and_exceeds_block_gas() public {
        uint256[7] memory ns = [uint256(10), 100, 500, 1000, 2000, 4000, 8000];
        uint256 prev;
        bool exceeded;
        uint256 exceedN;
        for (uint256 i; i < ns.length; i++) {
            uint256 used = _once(ns[i]);
            console2.log("N=", ns[i], " gas=", used);
            assertGt(used, prev, "distribute gas must increase with curator count");
            prev = used;
            if (!exceeded && used > MAINNET_BLOCK_GAS) { exceeded = true; exceedN = ns[i]; }
        }
        console2.log("CASE B: first N with gas > 30M block:", exceedN);
        assertTrue(exceeded, "distribute gas must exceed a 30M block at a reachable curator count");
    }

    function test_B2_distribute_reverts_under_block_gas_cap_at_largeN() public {
        cred.setN(8000);
        if (dist.balanceOf(CRED) == 0) dist.deposit{ value: 1 ether }(CRED, 1 ether);
        (bool ok, ) = address(dist).call{ gas: MAINNET_BLOCK_GAS }(abi.encodeWithSignature("distribute(uint256)", CRED));
        console2.log("CASE B2: distribute under 30M gas cap at N=8000 completed?", ok);
        assertFalse(ok, "distribute must NOT complete within a 30M block at N=8000 (un-includable => DoS)");
    }

    function test_C_control_smallN_still_succeeds() public {
        uint256 used = _once(10);
        console2.log("CASE C control: N=10 distribute gas:", used);
        assertLt(used, MAINNET_BLOCK_GAS, "control: small N still fits one block (no growth => no DoS)");
    }
}
