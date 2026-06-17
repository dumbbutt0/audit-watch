// SPDX-License-Identifier: ISC
pragma solidity >=0.8.25;

// P126 lifecycle-transition harness — BootstrapPool.kill() -> LiquidityManager.moveLiquidity() (research-only).
// Question: can attacker-influenced BootstrapPool end-state (reserves/fees/donations/residual) at kill() materially
// alter the moveLiquidity() outcome? Exercises the clean createPair migration branch (NOT the awarded pair-adoption
// M-01). Real LiquidityManager + BootstrapPool; mock AgentFactory + a faithful constant-product Fraxswap pair
// (etched at the hardcoded factory address). Runtime decides. iq-ai src UNMUTATED (test/audit/ only).

import {Test} from "forge-std/src/Test.sol";
import {LiquidityManager} from "../../src/LiquidityManager.sol";
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

// faithful constant-product pair (UniV2, 0.3% fee) — destination of the migration; supports mint/swap/arb
contract MockFraxswapPair {
    address public token0;
    address public token1;
    uint112 private r0;
    uint112 private r1;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf; // LP
    mapping(address => mapping(address => uint256)) public allowance;
    constructor(address t0, address t1) { token0 = t0; token1 = t1; }
    function getReserves() external view returns (uint112, uint112, uint32) { return (r0, r1, 0); }
    function _bal(address t) internal view returns (uint256) { return MockERC20(t).balanceOf(address(this)); }
    function _sqrt(uint256 y) internal pure returns (uint256 z) { if (y>3){z=y;uint256 x=y/2+1;while(x<z){z=x;x=(y/x+x)/2;}}else if(y!=0){z=1;} }
    function _min(uint256 a, uint256 b) internal pure returns (uint256) { return a < b ? a : b; }
    function mint(address to) external returns (uint256 liq) {
        uint256 b0 = _bal(token0); uint256 b1 = _bal(token1);
        uint256 a0 = b0 - r0; uint256 a1 = b1 - r1;
        if (totalSupply == 0) liq = _sqrt(a0 * a1);
        else liq = _min(a0 * totalSupply / r0, a1 * totalSupply / r1);
        require(liq > 0, "ILM");
        totalSupply += liq; balanceOf[to] += liq;
        r0 = uint112(b0); r1 = uint112(b1);
    }
    function getAmountOut(uint256 amountIn, address tokenIn) public view returns (uint256) {
        (uint256 rin, uint256 rout) = tokenIn == token0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));
        uint256 aInFee = amountIn * 997;
        return aInFee * rout / (rin * 1000 + aInFee);
    }
    function swap(uint256 a0Out, uint256 a1Out, address to, bytes calldata) external {
        require(a0Out > 0 || a1Out > 0, "IOA");
        if (a0Out > 0) MockERC20(token0).transfer(to, a0Out);
        if (a1Out > 0) MockERC20(token1).transfer(to, a1Out);
        uint256 b0 = _bal(token0); uint256 b1 = _bal(token1);
        uint256 in0 = b0 > r0 - a0Out ? b0 - (r0 - a0Out) : 0;
        uint256 in1 = b1 > r1 - a1Out ? b1 - (r1 - a1Out) : 0;
        require(in0 > 0 || in1 > 0, "IIA");
        uint256 b0adj = b0 * 1000 - in0 * 3;
        uint256 b1adj = b1 * 1000 - in1 * 3;
        require(b0adj * b1adj >= uint256(r0) * uint256(r1) * 1_000_000, "K");
        r0 = uint112(b0); r1 = uint112(b1);
    }
    function transfer(address to, uint256 a) external returns (bool) { balanceOf[msg.sender]-=a; balanceOf[to]+=a; return true; }
    function approve(address s, uint256 a) external returns (bool) { allowance[msg.sender][s]=a; return true; }
}

contract MockFraxswapFactory {
    mapping(bytes32 => address) public pairs;
    address public nextPair;
    function setNextPair(address p) external { nextPair = p; }
    function getPair(address a, address b) external view returns (address) { return pairs[_k(a, b)]; }
    function createPair(address a, address b, uint256) external returns (address) { pairs[_k(a, b)] = nextPair; return nextPair; }
    function _k(address a, address b) internal pure returns (bytes32) { return a < b ? keccak256(abi.encode(a,b)) : keccak256(abi.encode(b,a)); }
}

contract MockAgentFactory {
    uint256 public targetCCYLiquidity;
    uint256 public shareToBamm; // 0 -> skip BAMM
    mapping(address => uint256) public stage;
    constructor(uint256 t) { targetCCYLiquidity = t; shareToBamm = 0; }
    function setAgentStage(address a, uint256 s) external { stage[a] = s; }
}

contract LifecycleTransitionRuntime is Test {
    address constant FRAX = 0xE30521fe7f3bEB6Ad556887b50739d6C7CA667E6;
    MockERC20 currency;
    MockERC20 agent;
    MockAgentFactory factory; // = owner of LM, also feeTo for swept fees
    LiquidityManager lm;
    BootstrapPool pool;
    MockFraxswapPair pair;
    address agentAddr = makeAddr("agentContract");
    address user = makeAddr("user");
    address attacker = makeAddr("attacker");

    uint256 constant PRICE = 1e18;
    uint256 constant INIT_LIQ = 1_000_000 ether; // agent bootstrap liquidity
    uint256 constant TARGET = 10_000 ether;       // gate threshold
    uint256 constant FEE_BPS = 100;               // 1%

    function setUp() public {
        currency = new MockERC20();
        agent = new MockERC20();
        factory = new MockAgentFactory(TARGET);
        lm = new LiquidityManager(IERC20(address(currency)), IERC20(address(agent)), address(factory), agentAddr,
                                  PRICE, TARGET, INIT_LIQ, FEE_BPS);
        agent.mint(address(lm), INIT_LIQ);
        lm.initializeBootstrapPool();
        pool = lm.bootstrapPool();
        // etch a faithful Fraxswap factory at the hardcoded constant + pre-deploy the destination pair
        MockFraxswapFactory facImpl = new MockFraxswapFactory();
        vm.etch(FRAX, address(facImpl).code);
        pair = new MockFraxswapPair(address(currency), address(agent));
        MockFraxswapFactory(FRAX).setNextPair(address(pair));
    }

    function _buy(address who, uint256 amountIn) internal returns (uint256 out) {
        currency.mint(who, amountIn);
        vm.startPrank(who);
        currency.approve(address(pool), amountIn);
        out = pool.buy(amountIn, who);
        vm.stopPrank();
    }

    function _realCurrencyReserve() internal view returns (uint256) {
        (uint256 rc,) = pool.getReserves();
        return rc - pool.phantomAmount();
    }

    // ---------- A: clean pool — baseline + value conservation (I1/I2/I4) ----------
    function test_A_clean_migration_conserves_value() public {
        _buy(user, 20_000 ether);
        uint256 Cb = currency.balanceOf(address(pool));
        uint256 Ab = agent.balanceOf(address(pool));
        uint256 cf = pool.currencyTokenFeeEarned();
        uint256 af = pool.agentTokenFeeEarned();

        vm.prank(attacker); // permissionless caller
        lm.moveLiquidity();

        // I2: fees swept to the factory (feeTo), excluded from migration
        assertEq(currency.balanceOf(address(factory)), cf, "currency fee swept to factory");
        assertEq(agent.balanceOf(address(factory)), af, "agent fee swept to factory");
        // I1: value conservation (currency)
        assertEq(currency.balanceOf(address(pair)), Cb - cf, "pair currency == real pool currency");
        assertEq(currency.balanceOf(address(factory)) + currency.balanceOf(address(pair))
                 + currency.balanceOf(agentAddr), Cb, "currency conserved");
        // I1: value conservation (agent) = pair + agentLeftover + fee
        assertEq(agent.balanceOf(address(pair)) + agent.balanceOf(agentAddr) + agent.balanceOf(address(factory)), Ab,
                 "agent conserved");
        // nothing stuck in the LM
        assertEq(currency.balanceOf(address(lm)), 0, "LM no currency residual");
        assertEq(agent.balanceOf(address(lm)), 0, "LM no agent residual");
        // I4: pair seeded at the pool spot price; LP routed to the agent (shareToBamm=0)
        assertGt(pair.balanceOf(agentAddr), 0, "LP routed to agent");
        assertEq(factory.stage(agentAddr), 1, "agent stage advanced");
    }

    // ---------- B: fee-heavy pool — fees swept, not migrated (I2) ----------
    function test_B_fee_heavy_fees_excluded() public {
        _buy(user, 20_000 ether);
        // round-trips to accrue both fee accumulators
        uint256 g = agent.balanceOf(user);
        vm.startPrank(user);
        agent.approve(address(pool), g);
        pool.sell(g / 2, user);
        vm.stopPrank();
        _buy(user, 5_000 ether);

        uint256 cf = pool.currencyTokenFeeEarned();
        uint256 af = pool.agentTokenFeeEarned();
        assertGt(cf, 0, "currency fees accrued"); assertGt(af, 0, "agent fees accrued");
        uint256 Cb = currency.balanceOf(address(pool));
        uint256 Ab = agent.balanceOf(address(pool));

        vm.prank(attacker); lm.moveLiquidity();

        assertEq(currency.balanceOf(address(factory)), cf, "currency fee swept");
        assertEq(agent.balanceOf(address(factory)), af, "agent fee swept");
        assertEq(currency.balanceOf(address(pair)), Cb - cf, "only fee-excluded currency migrated");
        // conservation still holds with both fee legs
        assertEq(agent.balanceOf(address(pair)) + agent.balanceOf(agentAddr) + af, Ab, "agent conserved (with agent fee)");
    }

    // ---------- C: donation-inflated currency — donor gets nothing (I3) ----------
    function test_C_currency_donation_not_recouped() public {
        _buy(user, 20_000 ether);
        // attacker donates currency directly to the pool
        uint256 D = 5_000 ether;
        currency.mint(attacker, D);
        vm.prank(attacker); currency.transfer(address(pool), D);

        uint256 atkBefore = currency.balanceOf(attacker) + agent.balanceOf(attacker); // 0
        vm.prank(attacker); lm.moveLiquidity();
        uint256 atkAfter = currency.balanceOf(attacker) + agent.balanceOf(attacker)
                           + pair.balanceOf(attacker); // attacker holds no LP either
        assertEq(atkBefore, 0, "attacker started flat");
        assertEq(atkAfter, 0, "attacker recouped nothing from the donation (I3)");
        // the donated currency ended up in the pair (migrated liquidity owned by the agent), not returned
        assertGt(currency.balanceOf(address(pair)), 20_000 ether, "donation flowed into migrated liquidity");
    }

    // ---------- D: agent-donation — donor gets nothing + availability (no DoS) (I3/I6a) ----------
    function test_D_agent_donation_no_recoup_no_dos() public {
        _buy(user, 20_000 ether);
        uint256 D = 50_000 ether;
        agent.mint(attacker, D);
        vm.prank(attacker); agent.transfer(address(pool), D); // donate agent -> lowers price, raises liquidityAmount

        vm.prank(attacker);
        lm.moveLiquidity(); // I6a: must NOT revert (availability under attacker-prepared reserve state)

        assertEq(currency.balanceOf(attacker) + agent.balanceOf(attacker) + pair.balanceOf(attacker), 0,
                 "attacker recouped nothing from the agent donation (I3)");
        assertEq(factory.stage(agentAddr), 1, "migration completed despite donation (I6a)");
    }

    // ---------- E: attacker-prepared edge + arb the new pair — net P&L (I5) ----------
    function test_E_price_manipulation_arb_pnl() public {
        _buy(user, 20_000 ether); // organic bootstrap
        // attacker manipulates the bootstrap spot price up with a large buy, capturing agent
        uint256 spend = 50_000 ether;
        uint256 gotAgent = _buy(attacker, spend);
        // permissionless migration seeds the Fraxswap pair at the (manipulated) spot price
        vm.prank(attacker); lm.moveLiquidity();
        // attacker arbs: sell the captured agent into the freshly-seeded pair
        vm.startPrank(attacker);
        uint256 sellOut;
        if (gotAgent > 0 && pair.totalSupply() > 0) {
            uint256 q = pair.getAmountOut(gotAgent, address(agent)); // agent -> currency
            if (q > 0 && q < currency.balanceOf(address(pair))) {
                agent.transfer(address(pair), gotAgent);
                pair.swap(q, 0, attacker, ""); // token0 == currency
                sellOut = q;
            }
        }
        vm.stopPrank();
        uint256 atkCurrencyFinal = currency.balanceOf(attacker);
        // attacker spent `spend` currency and recovered `atkCurrencyFinal`; record net P&L
        emit log_named_uint("attacker_spend", spend);
        emit log_named_uint("attacker_recovered", atkCurrencyFinal);
        emit log_named_uint("arb_sellOut", sellOut);
        // I5: the manipulate->migrate->arb sequence must not net the attacker a profit
        assertLe(atkCurrencyFinal, spend, "no attacker profit from boundary price manipulation (I5)");
    }

    // ---------- F: forced-early migration via donation crossing the gate (I6b control) ----------
    function test_F_forced_early_migration_control() public {
        // pool is BELOW the gate (no organic bootstrap)
        assertLt(_realCurrencyReserve(), TARGET, "pool below gate initially");
        // an unforced migration must revert (gate not reached)
        vm.prank(attacker);
        vm.expectRevert(bytes("Bootstrap end-criterion not reached"));
        lm.moveLiquidity();

        // attacker donates just enough currency to cross the gate, then immediately forces migration
        uint256 D = TARGET; // exactly the threshold
        currency.mint(attacker, D);
        vm.prank(attacker); currency.transfer(address(pool), D);
        assertGe(_realCurrencyReserve(), TARGET, "donation crossed the gate");

        vm.prank(attacker); lm.moveLiquidity(); // forced-early migration fires

        // CONTROL fact: migration was forced early; protocol state advanced; attacker paid D and recouped nothing
        assertEq(factory.stage(agentAddr), 1, "migration forced (stage advanced) when it otherwise could not fire");
        assertEq(currency.balanceOf(attacker) + agent.balanceOf(attacker) + pair.balanceOf(attacker), 0,
                 "attacker recouped nothing (forced-early is a cost, not a profit)");
        emit log_named_uint("forced_migration_cost", D);
    }
}
