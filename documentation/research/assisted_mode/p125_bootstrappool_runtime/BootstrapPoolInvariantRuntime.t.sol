// SPDX-License-Identifier: ISC
pragma solidity >=0.8.25;

// P125 cross-contract harness — iq-ai BootstrapPool invariants (research-only, un-wired).
// Exercises the REAL bonding-curve math (only the ERC20 tokens are standard mocks) to settle the pricing invariants
// the AgentRouter harnesses (P123/P124) deferred as NEEDS_CONTEXT. Runtime decides. iq-ai src UNMUTATED (test/audit/).

import {Test} from "forge-std/src/Test.sol";
import {BootstrapPool} from "../../src/BootstrapPool.sol";
import {IERC20} from "@openzeppelin/contracts/interfaces/IERC20.sol";

contract MockERC20 {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    function mint(address to, uint256 a) external { balanceOf[to] += a; }
    function approve(address s, uint256 a) external returns (bool) { allowance[msg.sender][s] = a; return true; }
    function transfer(address to, uint256 a) public returns (bool) {
        require(balanceOf[msg.sender] >= a, "bal"); balanceOf[msg.sender] -= a; balanceOf[to] += a; return true;
    }
    function transferFrom(address f, address t, uint256 a) external returns (bool) {
        uint256 al = allowance[f][msg.sender];
        require(al >= a, "allow"); require(balanceOf[f] >= a, "bal");
        if (al != type(uint256).max) allowance[f][msg.sender] = al - a;
        balanceOf[f] -= a; balanceOf[t] += a; return true;
    }
}

// Deploys the pool so BootstrapPool.owner == this contract; owner() returns feeTo for the sweepFees fee-routing cast
// (BootstrapPool._sweepFees does LiquidityManager(owner).owner()).
contract MockLiquidityManager {
    address public owner; // = feeTo
    constructor(address feeTo) { owner = feeTo; }
    function deploy(IERC20 c, IERC20 a, uint256 price, uint256 boot, uint256 fee) external returns (BootstrapPool) {
        return new BootstrapPool(c, a, price, boot, fee);
    }
}

contract BootstrapPoolInvariantRuntime is Test {
    MockERC20 currency;
    MockERC20 agent;
    MockLiquidityManager mlm;
    address feeTo = makeAddr("feeTo");
    address trader = makeAddr("trader");
    address attacker = makeAddr("attacker");

    uint256 constant PRICE = 1e18;            // 1:1 initial price
    uint256 constant BOOT = 1_000_000 ether;  // bootstrap agent liquidity
    uint256 constant FEE_BPS = 100;           // 1%

    function setUp() public {
        currency = new MockERC20();
        agent = new MockERC20();
        mlm = new MockLiquidityManager(feeTo);
    }

    // fresh pool seeded with `BOOT` agent bootstrap liquidity; phantom currency reserve set in constructor
    function _freshPool() internal returns (BootstrapPool p) {
        p = mlm.deploy(IERC20(address(currency)), IERC20(address(agent)), PRICE, BOOT, FEE_BPS);
        agent.mint(address(p), BOOT); // bootstrap agent liquidity
    }

    function _k(BootstrapPool p) internal view returns (uint256) {
        (uint256 rc, uint256 ra) = p.getReserves();
        return rc * ra;
    }

    // ---------- A: round-trip is strictly lossy (no free extraction) ----------
    function test_A_roundtrip_no_profit() public {
        BootstrapPool p = _freshPool();
        uint256 C = 1_000 ether;
        currency.mint(trader, C);
        vm.startPrank(trader);
        currency.approve(address(p), C);
        uint256 g = p.buy(C, trader);
        agent.approve(address(p), g);
        uint256 cBack = p.sell(g, trader);
        vm.stopPrank();
        assertGt(g, 0, "bought some agent");
        assertLt(cBack, C, "round-trip returns strictly less currency than spent (fees)");
    }

    // ---------- B: constant-product k is non-decreasing across trades ----------
    function test_B_constant_product_nondecreasing() public {
        BootstrapPool p = _freshPool();
        uint256 k0 = _k(p);
        // buy
        uint256 C = 5_000 ether;
        currency.mint(trader, C);
        vm.startPrank(trader);
        currency.approve(address(p), C);
        uint256 g = p.buy(C, trader);
        uint256 k1 = _k(p);
        assertGe(k1, k0, "k non-decreasing after buy");
        // sell part of it back
        uint256 sellAmt = g / 2;
        agent.approve(address(p), sellAmt);
        p.sell(sellAmt, trader);
        vm.stopPrank();
        uint256 k2 = _k(p);
        assertGe(k2, k1, "k non-decreasing after sell");
    }

    // ---------- C: solvency — pool never pays out currency it does not hold ----------
    function test_C_solvency_large_sell_reverts() public {
        BootstrapPool p = _freshPool();
        // seed real currency via a buy
        uint256 C = 1_000 ether;
        currency.mint(trader, C);
        vm.startPrank(trader);
        currency.approve(address(p), C);
        p.buy(C, trader);
        vm.stopPrank();

        // attacker holds a large agent position
        agent.mint(attacker, 5_000_000 ether);
        vm.startPrank(attacker);
        agent.approve(address(p), type(uint256).max);
        // a small sell is honored (<= real currency available)
        uint256 outSmall = p.sell(100 ether, attacker);
        assertGt(outSmall, 0, "small sell honored");
        // a sell whose quote exceeds the real currency balance must revert (no insolvent payout)
        vm.expectRevert();
        p.sell(5_000_000 ether, attacker);
        vm.stopPrank();
    }

    // ---------- D: permissionless sweepFees is reserve-neutral ----------
    function test_D_sweepfees_reserve_neutral() public {
        BootstrapPool p = _freshPool();
        uint256 C = 2_000 ether;
        currency.mint(trader, C);
        vm.startPrank(trader);
        currency.approve(address(p), C);
        p.buy(C, trader);
        vm.stopPrank();

        uint256 expectFee = C * FEE_BPS / 10_000; // currency fee accrued by the buy
        assertEq(p.currencyTokenFeeEarned(), expectFee, "currency fee accrued");
        (uint256 rcBefore, uint256 raBefore) = p.getReserves();
        uint256 feeToBefore = currency.balanceOf(feeTo);

        // arbitrary permissionless caller sweeps
        vm.prank(attacker);
        p.sweepFees();

        (uint256 rcAfter, uint256 raAfter) = p.getReserves();
        assertEq(rcAfter, rcBefore, "reserveCurrency unchanged by sweep");
        assertEq(raAfter, raBefore, "reserveAgent unchanged by sweep");
        assertEq(p.currencyTokenFeeEarned(), 0, "currency fee zeroed");
        assertEq(p.agentTokenFeeEarned(), 0, "agent fee zeroed");
        assertEq(currency.balanceOf(feeTo) - feeToBefore, expectFee, "feeTo received exactly the accrued fee");
    }

    // ---------- E: donation is not profitable for the donor (donor self-loss) ----------
    function test_E_donation_not_profitable() public {
        uint256 G = 500 ether;      // agent position the attacker will sell
        uint256 SEED = 2_000 ether; // real currency seeded so sells are honored
        uint256 Cd = 1_000 ether;   // donation

        // Scenario 1: no donation
        BootstrapPool p1 = _freshPool();
        _seedCurrency(p1, SEED);
        agent.mint(attacker, G);
        vm.startPrank(attacker);
        agent.approve(address(p1), G);
        uint256 outNo = p1.sell(G, attacker);
        vm.stopPrank();

        // Scenario 2: attacker donates currency to the pool, then sells the SAME G
        BootstrapPool p2 = _freshPool();
        _seedCurrency(p2, SEED);
        agent.mint(attacker, G);
        currency.mint(attacker, Cd);
        vm.startPrank(attacker);
        currency.transfer(address(p2), Cd); // direct donation (inflates reserveCurrency)
        agent.approve(address(p2), G);
        uint256 outYes = p2.sell(G, attacker);
        vm.stopPrank();

        // donating raises the sell quote, but never enough to recoup the donation -> net loss for the donor
        assertLe(outYes, outNo + Cd, "donation is not recouped (no donor profit)");
        assertLt(outYes - 0, outNo + Cd, "strict: donor nets a loss vs not donating");
    }

    // helper: seed real currency into a pool via an honest buy from `trader`
    function _seedCurrency(BootstrapPool p, uint256 amount) internal {
        currency.mint(trader, amount);
        vm.startPrank(trader);
        currency.approve(address(p), amount);
        p.buy(amount, trader);
        vm.stopPrank();
    }
}
