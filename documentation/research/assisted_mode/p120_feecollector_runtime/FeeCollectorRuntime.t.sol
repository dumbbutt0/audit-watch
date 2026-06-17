// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.26;

// P120 runtime harness — ramses FeeCollector.collectProtocolFees (research-only, un-wired).
// One question: can a permissionless caller redirect/extract protocol fees, given the arbitrary `pool` arg
// and the balanceOf(this) notify amount? Runtime decides. ramses src is UNMUTATED (imported via remapping).

import "forge-std/Test.sol";
import {FeeCollector} from "ramses/CL/gauge/FeeCollector.sol";
import {IRamsesV3Pool} from "ramses/CL/core/interfaces/IRamsesV3Pool.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

// ---- minimal ERC20 (mint/transfer/approve/transferFrom) ----
contract MockERC20 {
    string public name = "Mock";
    string public symbol = "MOCK";
    uint8 public decimals = 18;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    function mint(address to, uint256 amt) external { balanceOf[to] += amt; }
    function transfer(address to, uint256 amt) public returns (bool) {
        require(balanceOf[msg.sender] >= amt, "bal");
        balanceOf[msg.sender] -= amt; balanceOf[to] += amt; return true;
    }
    function approve(address sp, uint256 amt) external returns (bool) { allowance[msg.sender][sp] = amt; return true; }
    function transferFrom(address f, address t, uint256 amt) external returns (bool) {
        require(allowance[f][msg.sender] >= amt, "allow");
        require(balanceOf[f] >= amt, "bal");
        allowance[f][msg.sender] -= amt; balanceOf[f] -= amt; balanceOf[t] += amt; return true;
    }
}

// ---- mock pool: implements only what FeeCollector calls; on collectProtocol sends its token balance to recipient ----
contract MockPool {
    address public token0;
    address public token1;
    address public lastCollectRecipient;
    constructor(address t0, address t1) { token0 = t0; token1 = t1; }
    function collectProtocol(address recipient, uint128, uint128) external returns (uint128 a0, uint128 a1) {
        lastCollectRecipient = recipient;
        a0 = uint128(MockERC20(token0).balanceOf(address(this)));
        a1 = uint128(MockERC20(token1).balanceOf(address(this)));
        if (a0 > 0) MockERC20(token0).transfer(recipient, a0);
        if (a1 > 0) MockERC20(token1).transfer(recipient, a1);
    }
}

// ---- mock voter: configurable gauge/alive/redirect/feeDist ----
contract MockVoter {
    mapping(address => address) public gauge;       // pool => gauge
    mapping(address => bool) public alive;          // gauge => isAlive
    mapping(address => address) public redirect;    // pool => toPool
    mapping(address => address) public feeDist;     // gauge => feeDistributor
    function setGauge(address pool, address g) external { gauge[pool] = g; }
    function setAlive(address g, bool v) external { alive[g] = v; }
    function setRedirect(address pool, address toPool) external { redirect[pool] = toPool; }
    function setFeeDist(address g, address fd) external { feeDist[g] = fd; }
    function gaugeForPool(address pool) external view returns (address) { return gauge[pool]; }
    function isAlive(address g) external view returns (bool) { return alive[g]; }
    function poolRedirect(address pool) external view returns (address) { return redirect[pool]; }
    function feeDistributorForGauge(address g) external view returns (address) { return feeDist[g]; }
}

// ---- mock fee distributor: records notifyRewardAmount and pulls the approved tokens (real ve(3,3) behavior) ----
contract MockFeeDist {
    mapping(address => uint256) public notified;   // token => total notified
    function notifyRewardAmount(address token, uint256 amount) external {
        notified[token] += amount;
        // pull from caller (the FeeCollector) like a real distributor
        MockERC20(token).transferFrom(msg.sender, address(this), amount);
    }
}

contract FeeCollectorRuntime is Test {
    FeeCollector fc;
    MockVoter voter;
    MockFeeDist feeDist;
    MockERC20 t0;
    MockERC20 t1;
    address treasury = makeAddr("treasury");
    address attacker = makeAddr("attacker");
    address gauge = makeAddr("gauge");
    uint256 constant FEE0 = 1_000 ether;
    uint256 constant FEE1 = 500 ether;

    function _deploy(uint256 treasuryFeesBips) internal {
        voter = new MockVoter();
        feeDist = new MockFeeDist();
        t0 = new MockERC20();
        t1 = new MockERC20();
        FeeCollector impl = new FeeCollector();
        bytes memory data = abi.encodeCall(FeeCollector.initialize, (treasury, address(voter)));
        ERC1967Proxy proxy = new ERC1967Proxy(address(impl), data);
        fc = FeeCollector(address(proxy));
        if (treasuryFeesBips > 0) {
            vm.prank(treasury);
            fc.setTreasuryFees(treasuryFeesBips);  // onlyTreasury
        }
        vm.prank(treasury);
        fc.setIsLive(true);  // onlyTreasury — enable fee distribution
    }

    function _newPoolWithFees() internal returns (MockPool p) {
        p = new MockPool(address(t0), address(t1));
        t0.mint(address(p), FEE0);
        t1.mint(address(p), FEE1);
    }

    // CASE A — live gauge, arbitrary EOA caller: fees split treasury + feeDist; attacker gets NOTHING.
    function test_A_liveGauge_attackerCaller_noExtraction() public {
        _deploy(2_000); // 20% treasury fee
        MockPool p = _newPoolWithFees();
        voter.setGauge(address(p), gauge);
        voter.setAlive(gauge, true);
        voter.setFeeDist(gauge, address(feeDist));

        uint256 atk0Before = t0.balanceOf(attacker);
        uint256 atk1Before = t1.balanceOf(attacker);

        vm.prank(attacker);
        fc.collectProtocolFees(IRamsesV3Pool(address(p)));

        // L3 outcome: attacker received nothing
        assertEq(t0.balanceOf(attacker), atk0Before, "attacker t0 unchanged");
        assertEq(t1.balanceOf(attacker), atk1Before, "attacker t1 unchanged");
        assertEq(t0.balanceOf(attacker), 0, "attacker t0 == 0");
        // recipients: 20% treasury, 80% feeDist
        assertEq(t0.balanceOf(treasury), FEE0 * 2_000 / 10_000, "treasury t0 = 20%");
        assertEq(t1.balanceOf(treasury), FEE1 * 2_000 / 10_000, "treasury t1 = 20%");
        assertEq(feeDist.notified(address(t0)), FEE0 * 8_000 / 10_000, "feeDist t0 = 80%");
        assertEq(feeDist.notified(address(t1)), FEE1 * 8_000 / 10_000, "feeDist t1 = 80%");
        // FeeCollector drained to ~0
        assertEq(t0.balanceOf(address(fc)), 0, "fc t0 drained");
        assertEq(t1.balanceOf(address(fc)), 0, "fc t1 drained");
    }

    // CASE B — no gauge: ALL fees to treasury directly; attacker gets nothing.
    function test_B_noGauge_allToTreasury() public {
        _deploy(2_000);
        MockPool p = _newPoolWithFees();
        // no gauge set => gaugeForPool == address(0)
        vm.prank(attacker);
        fc.collectProtocolFees(IRamsesV3Pool(address(p)));
        assertEq(p.lastCollectRecipient(), treasury, "collectProtocol recipient == treasury");
        assertEq(t0.balanceOf(treasury), FEE0, "treasury got all t0");
        assertEq(t1.balanceOf(treasury), FEE1, "treasury got all t1");
        assertEq(t0.balanceOf(attacker), 0, "attacker nothing");
        assertEq(feeDist.notified(address(t0)), 0, "feeDist untouched");
    }

    // CASE C — attacker passes an attacker-deployed fake pool: no gauge => treasury branch; recipient is
    // hardcoded treasury, NOT the attacker. The arbitrary-pool arg cannot steer funds to the caller.
    function test_C_fakePool_cannotRedirectToAttacker() public {
        _deploy(0);
        // attacker-controlled pool holding attacker-funded tokens
        vm.startPrank(attacker);
        MockPool fake = new MockPool(address(t0), address(t1));
        vm.stopPrank();
        t0.mint(address(fake), 777 ether);
        // voter does not recognize the fake pool (gauge 0) -> treasury branch
        vm.prank(attacker);
        fc.collectProtocolFees(IRamsesV3Pool(address(fake)));
        assertEq(fake.lastCollectRecipient(), treasury, "fake pool collectProtocol recipient == treasury, not attacker");
        assertEq(t0.balanceOf(attacker), 0, "attacker did not receive funds");
        assertEq(t0.balanceOf(treasury), 777 ether, "fake pool fees routed to treasury");
    }

    // CASE D — balance quirk probe: pre-seed FeeCollector with a residual t0 balance (a donation), then collect a
    // DIFFERENT pool. notify amount uses balanceOf(this), so the residual is swept into THIS pool's feeDist.
    // This is cross-pool misattribution, but it requires a donation (self-loss) -> not theft. Record the behavior.
    function test_D_balanceOf_sweeps_residual_donation() public {
        _deploy(0); // 0% treasury fee -> entire balance goes to feeDist
        uint256 RESIDUAL = 123 ether;
        t0.mint(address(fc), RESIDUAL); // simulate a prior dust/donation residual
        MockPool p = _newPoolWithFees();
        voter.setGauge(address(p), gauge);
        voter.setAlive(gauge, true);
        voter.setFeeDist(gauge, address(feeDist));

        vm.prank(attacker);
        fc.collectProtocolFees(IRamsesV3Pool(address(p)));

        // feeDist for THIS pool received the pool's fees PLUS the unrelated residual (balanceOf-based amount)
        assertEq(feeDist.notified(address(t0)), FEE0 + RESIDUAL, "residual swept into this pool's feeDist");
        // attacker still gained nothing (donation came from whoever pre-funded, here the test)
        assertEq(t0.balanceOf(attacker), 0, "attacker gained nothing from the quirk");
    }
}
