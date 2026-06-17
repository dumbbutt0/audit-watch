// SPDX-License-Identifier: ISC
pragma solidity >=0.8.25;

// P123 runtime harness — iq-ai AgentRouter.buy (research-only, un-wired).
// One question: is the ROUTER itself safe — does buy() obtain agent tokens only for the full _amountIn paid,
// enforce _minAmountOut, reject non-existent agents, and hold no residual — with pricing delegated to the pool?
// Runtime decides. iq-ai src is UNMUTATED (this is a test-only file under test/audit/).

import {Test} from "forge-std/src/Test.sol";
import {AgentRouter} from "../../src/AgentRouter.sol";
import {AgentFactory} from "../../src/AgentFactory.sol";
import {IERC20} from "@openzeppelin/contracts/interfaces/IERC20.sol";

// ---- minimal ERC20 ----
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

// ---- mock bootstrap pool: pulls currency from the router, sends agent token to recipient ----
contract MockBootstrapPool {
    MockERC20 public currency;
    MockERC20 public agent;
    bool public killed;
    uint256 public quote; // amountOut to return
    address public lastRecipient;
    uint256 public lastAmountIn;
    constructor(MockERC20 c, MockERC20 a, bool k, uint256 q) { currency = c; agent = a; killed = k; quote = q; }
    function getAmountOut(uint256, address) external view returns (uint256) { return quote; }
    function buy(uint256 amountIn, address recipient) external returns (uint256) {
        lastAmountIn = amountIn; lastRecipient = recipient;
        currency.transferFrom(msg.sender, address(this), amountIn); // pull the exact approved amount from the router
        agent.transfer(recipient, quote);                           // deliver agent tokens to the recipient
        return quote;
    }
}

contract MockLiquidityManager {
    address public bootstrapPool;
    constructor(address bp) { bootstrapPool = bp; }
}

contract MockAgentFactory {
    address public currencyToken;
    mapping(address => address) public tokenAgent;
    mapping(address => address) public agentManager;
    constructor(address c) { currencyToken = c; }
    function setAgent(address token, address agent, address lm) external {
        tokenAgent[token] = agent; agentManager[agent] = lm;
    }
}

// ---- Fraxswap mocks (for the killed path; factory etched at the hardcoded constant) ----
contract MockFraxswapPair {
    MockERC20 public agent;
    address public token0;
    uint256 public quote;
    uint256 public received;
    constructor(MockERC20 a, address t0, uint256 q) { agent = a; token0 = t0; quote = q; }
    function sync() external {}
    function getAmountOut(uint256, address) external view returns (uint256) { return quote; }
    function swap(uint256, uint256 amount1Out, address to, bytes calldata) external {
        received = agent.balanceOf(address(this)); // not used; placeholder
        agent.transfer(to, amount1Out == 0 ? quote : amount1Out);
    }
}

contract MockFraxswapFactory {
    mapping(bytes32 => address) public pairs;
    function setPair(address a, address b, address p) external { pairs[_k(a, b)] = p; }
    function getPair(address a, address b) external view returns (address) { return pairs[_k(a, b)]; }
    function _k(address a, address b) internal pure returns (bytes32) {
        return a < b ? keccak256(abi.encode(a, b)) : keccak256(abi.encode(b, a));
    }
}

contract AgentRouterBuyRuntime is Test {
    address constant FRAX_FACTORY = 0xE30521fe7f3bEB6Ad556887b50739d6C7CA667E6;
    MockERC20 currency;
    MockERC20 agentToken;
    MockAgentFactory factory;
    AgentRouter router;
    address buyer = makeAddr("buyer");
    address recipient = makeAddr("recipient");
    address agentId = makeAddr("agentId");

    function setUp() public {
        currency = new MockERC20();
        agentToken = new MockERC20();
        factory = new MockAgentFactory(address(currency));
        router = new AgentRouter(AgentFactory(address(factory)));
    }

    function _wireBootstrap(bool killed, uint256 quote) internal returns (MockBootstrapPool bp) {
        bp = new MockBootstrapPool(currency, agentToken, killed, quote);
        agentToken.mint(address(bp), 1_000_000 ether);
        MockLiquidityManager lm = new MockLiquidityManager(address(bp));
        factory.setAgent(address(agentToken), agentId, address(lm));
    }

    // ---------- CASE A: non-existent agent -> AgentNotFound ----------
    function test_A_agent_not_found() public {
        vm.prank(buyer);
        vm.expectRevert(AgentRouter.AgentNotFound.selector);
        router.buy(address(agentToken), 100 ether, 0, buyer);
    }

    // ---------- CASE B: bootstrap happy path -> exact pull, recipient gets out, router holds 0 ----------
    function test_B_bootstrap_happy_path() public {
        MockBootstrapPool bp = _wireBootstrap(false, 90 ether);
        currency.mint(buyer, 100 ether);
        vm.prank(buyer); currency.approve(address(router), 100 ether);

        vm.prank(buyer);
        uint256 out = router.buy(address(agentToken), 100 ether, 90 ether, recipient);

        assertEq(out, 90 ether, "amountOut");
        assertEq(currency.balanceOf(buyer), 0, "buyer paid exactly amountIn");
        assertEq(bp.lastAmountIn(), 100 ether, "pool received full amountIn");
        assertEq(agentToken.balanceOf(recipient), 90 ether, "recipient got agent tokens");
        // router holds no residual of either token
        assertEq(currency.balanceOf(address(router)), 0, "router holds no currency");
        assertEq(agentToken.balanceOf(address(router)), 0, "router holds no agent token");
    }

    // ---------- CASE C: slippage guard ----------
    function test_C_slippage_revert() public {
        _wireBootstrap(false, 90 ether);
        currency.mint(buyer, 100 ether);
        vm.prank(buyer); currency.approve(address(router), 100 ether);
        vm.prank(buyer);
        vm.expectRevert(AgentRouter.InsufficientAmountOut.selector);
        router.buy(address(agentToken), 100 ether, 91 ether, recipient); // minOut > quote
    }

    // ---------- CASE D: buy for a different recipient ----------
    function test_D_recipient_routing() public {
        _wireBootstrap(false, 90 ether);
        currency.mint(buyer, 100 ether);
        vm.prank(buyer); currency.approve(address(router), 100 ether);
        vm.prank(buyer);
        router.buy(address(agentToken), 100 ether, 0, recipient);
        assertEq(agentToken.balanceOf(recipient), 90 ether, "recipient (not buyer) received tokens");
        assertEq(agentToken.balanceOf(buyer), 0, "buyer received nothing");
        assertEq(currency.balanceOf(buyer), 0, "buyer paid");
    }

    // ---------- CASE E: Fraxswap (killed) path via etched factory ----------
    function test_E_fraxswap_killed_path() public {
        // bootstrap pool reports killed -> router takes the Fraxswap branch
        _wireBootstrap(true, 0);
        // etch a mock factory at the hardcoded constant, then configure the pair
        MockFraxswapFactory facImpl = new MockFraxswapFactory();
        vm.etch(FRAX_FACTORY, address(facImpl).code);
        MockFraxswapPair pair = new MockFraxswapPair(agentToken, address(currency), 80 ether);
        agentToken.mint(address(pair), 1_000_000 ether);
        MockFraxswapFactory(FRAX_FACTORY).setPair(address(currency), address(agentToken), address(pair));

        currency.mint(buyer, 100 ether);
        vm.prank(buyer); currency.approve(address(router), 100 ether);
        vm.prank(buyer);
        uint256 out = router.buy(address(agentToken), 100 ether, 80 ether, recipient);

        assertEq(out, 80 ether, "fraxswap amountOut");
        assertEq(currency.balanceOf(address(pair)), 100 ether, "amountIn routed to the pair");
        assertEq(agentToken.balanceOf(recipient), 80 ether, "recipient got agent tokens from swap");
        assertEq(currency.balanceOf(address(router)), 0, "router holds no currency");
    }
}
