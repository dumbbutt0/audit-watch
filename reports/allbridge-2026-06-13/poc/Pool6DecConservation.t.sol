// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.18;

// Audit harness (NOT part of the protocol): conservation/precision fuzz of Pool.sol with a
// 6-decimal token (real USDC/USDT config), where SYSTEM_PRECISION=3 truncation is coarsest.
// Pure-math mode: feeShareBP=0 and balanceRatioMinBP=0 (balance guard disabled) -> the hardest
// setting for keeping the pool conservative, mirroring the repo's own BasicInvariants choice.

import 'forge-std/console.sol';
import 'forge-std/StdInvariant.sol';
import 'forge-std/Test.sol';

import '@openzeppelin/contracts/token/ERC20/ERC20.sol';
import '../../contracts/Pool.sol';
import '../../contracts/test/TestBridgeForSwap.sol';

contract Token6 is ERC20 {
    constructor(uint256 supply, string memory n, string memory s) ERC20(n, s) {
        _mint(msg.sender, supply);
    }
    function decimals() public pure override returns (uint8) {
        return 6;
    }
}

contract Handler6 is Test {
    Pool public poolA;
    Pool public poolB;
    Token6 public tokA;
    Token6 public tokB;
    TestBridgeForSwap public bridge;
    address public alice;
    uint public initSum;

    constructor(address _alice, Pool _a, Pool _b, TestBridgeForSwap _br, Token6 _ta, Token6 _tb) {
        alice = _alice; poolA = _a; poolB = _b; bridge = _br; tokA = _ta; tokB = _tb;
        initSum = _ta.balanceOf(_alice) + _tb.balanceOf(_alice);
    }

    function _bytes32(address a) internal pure returns (bytes32) { return bytes32(uint(uint160(a))); }

    function depositA(uint amount) public { _deposit(poolA, amount); }
    function depositB(uint amount) public { _deposit(poolB, amount); }
    function _deposit(Pool p, uint amount) internal {
        amount = bound(amount, 1e6, 50_000_000 * 1e6); // $1 .. $50M (6-dec)
        vm.prank(alice); p.deposit(amount);
    }

    function withdrawA(uint lp) public { _withdraw(poolA, lp); }
    function withdrawB(uint lp) public { _withdraw(poolB, lp); }
    function _withdraw(Pool p, uint lp) internal {
        uint cap = Math.min(p.balanceOf(alice), p.reserves()); // LP units (SP, 3-dec)
        if (cap < 1e3) return; // < ~$1
        lp = bound(lp, 1e3, cap);
        vm.prank(alice); p.withdraw(lp);
    }

    function swapAB(uint amount) public { _swap(tokA, tokB, poolB, amount); }
    function swapBA(uint amount) public { _swap(tokB, tokA, poolA, amount); }
    function _swap(Token6 from, Token6 to, Pool destPool, uint amount) internal {
        uint up = destPool.reserves() * 1e3; // SP(3) -> raw(6)
        if (up < 5e6) return; // < $5
        up = Math.min(up, from.balanceOf(alice));
        if (up < 5e6) return;
        amount = bound(amount, 5e6, up);
        vm.prank(alice);
        bridge.swap(amount, _bytes32(address(from)), _bytes32(address(to)), alice, 0);
    }
}

contract Pool6DecConservationTest is StdInvariant, Test {
    Handler6 handler;
    Pool poolA;
    Pool poolB;
    Token6 tokA;
    Token6 tokB;
    TestBridgeForSwap bridge;
    address admin;
    address alice;
    uint constant SP = 3;

    function setUp() public {
        admin = makeAddr('admin');
        alice = makeAddr('alice');

        vm.startPrank(admin);
        tokA = new Token6(type(uint).max, 'USDC', 'USDC');
        tokB = new Token6(type(uint).max, 'USDT', 'USDT');
        bridge = new TestBridgeForSwap();
        // a=20, feeShareBP=0, balanceRatioMinBP=0 (pure math, no guard)
        poolA = new Pool(address(bridge), 20, tokA, 0, 0, 'lpA', 'lpA');
        poolB = new Pool(address(bridge), 20, tokB, 0, 0, 'lpB', 'lpB');
        tokA.approve(address(poolA), type(uint).max);
        tokB.approve(address(poolB), type(uint).max);
        bridge.addPool(poolA, bytes32(uint(uint160(address(tokA)))));
        bridge.addPool(poolB, bytes32(uint(uint160(address(tokB)))));
        // seed liquidity then hand the rest to alice
        poolA.deposit(1_000_000 * 1e6);
        poolB.deposit(1_000_000 * 1e6);
        tokA.transfer(alice, type(uint).max / 1e6);
        tokB.transfer(alice, type(uint).max / 1e6);
        vm.stopPrank();

        vm.startPrank(alice);
        tokA.approve(address(poolA), type(uint).max);
        tokB.approve(address(poolB), type(uint).max);
        tokA.approve(address(bridge), type(uint).max);
        tokB.approve(address(bridge), type(uint).max);
        vm.stopPrank();

        handler = new Handler6(alice, poolA, poolB, bridge, tokA, tokB);
        bytes4[] memory sel = new bytes4[](6);
        sel[0] = Handler6.depositA.selector;
        sel[1] = Handler6.depositB.selector;
        sel[2] = Handler6.withdrawA.selector;
        sel[3] = Handler6.withdrawB.selector;
        sel[4] = Handler6.swapAB.selector;
        sel[5] = Handler6.swapBA.selector;
        targetSelector(FuzzSelector({addr: address(handler), selectors: sel}));
        targetContract(address(handler));
    }

    // Solvency: real tokens held >= reserves (the amount LPs can withdraw), per pool.
    function invariant_realTokensGteReserves() public {
        assertLe(poolA.reserves() * 1e3, tokA.balanceOf(address(poolA)), 'A insolvent');
        assertLe(poolB.reserves() * 1e3, tokB.balanceOf(address(poolB)), 'B insolvent');
    }

    // LP supply never materially exceeds D (the invariant the pool is supposed to maintain).
    function invariant_totalLpLteD() public {
        uint ta = poolA.totalSupply(); uint da = poolA.d();
        uint tb = poolB.totalSupply(); uint db = poolB.d();
        assertLe(ta > da ? ta - da : 0, 2, 'A lp>d');
        assertLe(tb > db ? tb - db : 0, 2, 'B lp>d');
    }

    // No value extraction: a pure swapper/LP cannot end with more raw tokens than they started.
    function invariant_aliceNoProfit() public {
        uint sum = tokA.balanceOf(alice) + tokB.balanceOf(alice);
        assertLe(sum, handler.initSum(), 'alice profited');
    }
}
