// SPDX-License-Identifier: ISC
pragma solidity >=0.8.25;

// P124 runtime harness — iq-ai AgentRouter.sell (research-only, un-wired). Symmetric mirror of P123 buy.
// One question: is the ROUTER itself safe — does sell() return currency only for the full _amountIn of agent
// tokens surrendered, enforce _minAmountOut, reject non-existent agents, and hold no residual — with pricing
// delegated to the pool? Runtime decides. iq-ai src is UNMUTATED (this is a test-only file under test/audit/).

import {Test} from "forge-std/src/Test.sol";
import {AgentRouter} from "../../src/AgentRouter.sol";
import {AgentFactory} from "../../src/AgentFactory.sol";
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

// mock bootstrap pool: SELL pulls AGENT token from the router, sends CURRENCY to recipient
contract MockBootstrapPool {
    MockERC20 public currency;
    MockERC20 public agent;
    bool public killed;
    uint256 public quote; // currency amountOut to return
    address public lastRecipient;
    uint256 public lastAmountIn;
    constructor(MockERC20 c, MockERC20 a, bool k, uint256 q) { currency = c; agent = a; killed = k; quote = q; }
    function getAmountOut(uint256, address) external view returns (uint256) { return quote; }
    function sell(uint256 amountIn, address recipient) external returns (uint256) {
        lastAmountIn = amountIn; lastRecipient = recipient;
        agent.transferFrom(msg.sender, address(this), amountIn); // pull the exact approved agent tokens from the router
        currency.transfer(recipient, quote);                     // deliver currency to the recipient
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

// Fraxswap mocks (killed path): swap delivers CURRENCY out (agent in)
contract MockFraxswapPair {
    MockERC20 public currency;
    address public token0;
    uint256 public quote;
    constructor(MockERC20 c, address t0, uint256 q) { currency = c; token0 = t0; quote = q; }
    function sync() external {}
    function getAmountOut(uint256, address) external view returns (uint256) { return quote; }
    function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata) external {
        uint256 out = amount0Out == 0 ? amount1Out : amount0Out;
        currency.transfer(to, out == 0 ? quote : out);
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

contract AgentRouterSellRuntime is Test {
    address constant FRAX_FACTORY = 0xE30521fe7f3bEB6Ad556887b50739d6C7CA667E6;
    MockERC20 currency;
    MockERC20 agentToken;
    MockAgentFactory factory;
    AgentRouter router;
    address seller = makeAddr("seller");
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
        currency.mint(address(bp), 1_000_000 ether); // pool pays out currency
        MockLiquidityManager lm = new MockLiquidityManager(address(bp));
        factory.setAgent(address(agentToken), agentId, address(lm));
    }

    // CASE A: non-existent agent -> AgentNotFound
    function test_A_agent_not_found() public {
        vm.prank(seller);
        vm.expectRevert(AgentRouter.AgentNotFound.selector);
        router.sell(address(agentToken), 100 ether, 0, seller);
    }

    // CASE B: bootstrap happy path -> exact agent-token pull, recipient gets currency, router holds 0
    function test_B_bootstrap_happy_path() public {
        MockBootstrapPool bp = _wireBootstrap(false, 90 ether);
        agentToken.mint(seller, 100 ether);
        vm.prank(seller); agentToken.approve(address(router), 100 ether);

        vm.prank(seller);
        uint256 out = router.sell(address(agentToken), 100 ether, 90 ether, recipient);

        assertEq(out, 90 ether, "amountOut");
        assertEq(agentToken.balanceOf(seller), 0, "seller surrendered exactly amountIn");
        assertEq(bp.lastAmountIn(), 100 ether, "pool received full amountIn");
        assertEq(currency.balanceOf(recipient), 90 ether, "recipient got currency");
        assertEq(currency.balanceOf(address(router)), 0, "router holds no currency");
        assertEq(agentToken.balanceOf(address(router)), 0, "router holds no agent token");
    }

    // CASE C: slippage guard
    function test_C_slippage_revert() public {
        _wireBootstrap(false, 90 ether);
        agentToken.mint(seller, 100 ether);
        vm.prank(seller); agentToken.approve(address(router), 100 ether);
        vm.prank(seller);
        vm.expectRevert(AgentRouter.InsufficientAmountOut.selector);
        router.sell(address(agentToken), 100 ether, 91 ether, recipient);
    }

    // CASE D: sell for a different recipient
    function test_D_recipient_routing() public {
        _wireBootstrap(false, 90 ether);
        agentToken.mint(seller, 100 ether);
        vm.prank(seller); agentToken.approve(address(router), 100 ether);
        vm.prank(seller);
        router.sell(address(agentToken), 100 ether, 0, recipient);
        assertEq(currency.balanceOf(recipient), 90 ether, "recipient (not seller) received currency");
        assertEq(currency.balanceOf(seller), 0, "seller received no currency");
        assertEq(agentToken.balanceOf(seller), 0, "seller surrendered agent tokens");
    }

    // CASE E: Fraxswap (killed) path via etched factory
    function test_E_fraxswap_killed_path() public {
        _wireBootstrap(true, 0);
        MockFraxswapFactory facImpl = new MockFraxswapFactory();
        vm.etch(FRAX_FACTORY, address(facImpl).code);
        MockFraxswapPair pair = new MockFraxswapPair(currency, address(currency), 80 ether);
        currency.mint(address(pair), 1_000_000 ether);
        MockFraxswapFactory(FRAX_FACTORY).setPair(address(currency), address(agentToken), address(pair));

        agentToken.mint(seller, 100 ether);
        vm.prank(seller); agentToken.approve(address(router), 100 ether);
        vm.prank(seller);
        uint256 out = router.sell(address(agentToken), 100 ether, 80 ether, recipient);

        assertEq(out, 80 ether, "fraxswap amountOut");
        assertEq(agentToken.balanceOf(address(pair)), 100 ether, "amountIn (agent) routed to the pair");
        assertEq(currency.balanceOf(recipient), 80 ether, "recipient got currency from swap");
        assertEq(agentToken.balanceOf(address(router)), 0, "router holds no agent token");
    }
}
