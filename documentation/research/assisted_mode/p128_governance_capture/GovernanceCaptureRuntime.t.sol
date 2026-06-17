// SPDX-License-Identifier: ISC
pragma solidity >=0.8.25;

// P128 downstream harness — forced graduation -> governance capture? (research-only).
// Resolves P127 C2: after attacker-funded premature graduation (stage 0->1), can the attacker use the newly-alive
// agent/governance state for unauthorized control/value movement? Real AIToken + TokenGovernor + Agent; the test
// contract acts as the AgentFactory. Runtime decides. iq-ai src UNMUTATED (test/audit/ only).

import {Test} from "forge-std/src/Test.sol";
import {AIToken} from "../../src/AIToken.sol";
import {TokenGovernor} from "../../src/TokenGovernor.sol";
import {Agent} from "../../src/Agent.sol";
import {IVotes} from "@openzeppelin/contracts/governance/utils/IVotes.sol";
import {IGovernor} from "@openzeppelin/contracts/governance/IGovernor.sol";

contract GovernanceCaptureRuntime is Test {
    AIToken token;
    TokenGovernor gov;
    Agent agent;
    address attacker = makeAddr("attacker");
    address organic = makeAddr("organic");
    address whale = makeAddr("whale");
    uint256 constant SUPPLY = 100_000_000 ether;

    // --- the test contract stands in as the AgentFactory ---
    function defaultProxyImplementation() external view returns (address) { return address(0); }
    function allowedProxyImplementation(address) external pure returns (bool) { return false; }

    function setUp() public {
        vm.warp(1_000_000); // non-zero timestamp clock
        agent = new Agent("Agent", "AGT", "ipfs://x", address(this));     // owner=this(factory), holds NFT 0
        token = new AIToken("AIToken", "AIT", address(agent), address(this)); // mints SUPPLY to this; owner=agent
        agent.initializeToken(token);                                      // onlyOwner=this
        gov = new TokenGovernor("Gov", IVotes(address(token)), agent);
        agent.transferOwnership(address(gov));                            // Agent now governed by the Governor
    }

    function _give(address to, uint256 amt) internal {
        token.transfer(to, amt);
        vm.prank(to);
        token.delegate(to); // self-delegate to activate voting power
    }

    function _graduate() internal { agent.setStage(1); } // onlyFactory = this

    // build a proposal to make the governor (Agent owner) act on the Agent: setTokenURI (onlyOwner onlyWhenAlive)
    function _captureProposal()
        internal view
        returns (address[] memory t, uint256[] memory v, bytes[] memory c, string memory d)
    {
        t = new address[](1); v = new uint256[](1); c = new bytes[](1);
        t[0] = address(agent); v[0] = 0;
        c[0] = abi.encodeWithSelector(Agent.setTokenURI.selector, uint256(0), "CAPTURED");
        d = "capture";
    }

    // ---------- A: pre-graduation — proposalThreshold == max, action path blocked ----------
    function test_A_pre_graduation_blocked() public {
        _give(attacker, 1_000_000 ether); // 1% — still cannot propose while stage 0
        vm.warp(block.timestamp + 1);
        assertEq(agent.stage(), 0, "stage 0");
        assertEq(gov.proposalThreshold(), type(uint256).max, "threshold is max pre-graduation");
        (address[] memory t, uint256[] memory v, bytes[] memory c, string memory d) = _captureProposal();
        vm.prank(attacker);
        vm.expectRevert(); // GovernorInsufficientProposerVotes (votes < uint256.max)
        gov.propose(t, v, c, d);
    }

    // ---------- B/C: graduation governance state (honest small holder vs forced-donation ~0 holder) ----------
    function test_BC_graduation_state_and_voting_power() public {
        _graduate();
        vm.warp(block.timestamp + 1);
        uint256 q = gov.quorum(block.timestamp - 1);
        uint256 thr = gov.proposalThreshold();
        emit log_named_uint("quorum_tokens", q);
        emit log_named_uint("proposal_threshold_tokens", thr);
        // honest: small organic holder; forced: attacker donated currency -> holds 0 AIToken
        _give(organic, 500_000 ether); // 0.5%
        vm.warp(block.timestamp + 1);
        assertEq(token.getVotes(attacker), 0, "forced-donation attacker has 0 voting power");
        assertLt(token.getVotes(organic), q, "a small honest holder is far below quorum");
        assertGt(q, 0, "quorum is a positive fraction of supply");
    }

    // ---------- D1: forced-donation attacker cannot capture (path executed, fails quorum) ----------
    function test_D1_forced_attacker_cannot_capture() public {
        _graduate();
        // give the attacker exactly enough to PROPOSE (so we can execute the governance path) but nowhere near quorum
        vm.warp(block.timestamp + 1);
        uint256 thr = gov.proposalThreshold();
        _give(attacker, thr + 1); // just over the 0.01% propose threshold
        vm.warp(block.timestamp + 2);

        (address[] memory t, uint256[] memory v, bytes[] memory c, string memory d) = _captureProposal();
        vm.prank(attacker);
        uint256 id = gov.propose(t, v, c, d);
        vm.warp(block.timestamp + gov.votingDelay() + 1);
        vm.prank(attacker);
        gov.castVote(id, 1); // For, with ~0.01% power
        vm.warp(block.timestamp + gov.votingPeriod() + 1);

        // quorum not met -> Defeated -> execute reverts; the captured action never happens
        assertEq(uint256(gov.state(id)), uint256(IGovernor.ProposalState.Defeated), "proposal defeated (quorum fail)");
        vm.expectRevert();
        gov.execute(t, v, c, keccak256(bytes(d)));
        assertEq(token.getVotes(attacker), thr + 1, "attacker power unchanged by forced graduation");
    }

    // ---------- D2: positive control — only a >=quorum holder can pass/execute (proves mechanism + the bar) ----------
    function test_D2_quorum_holder_can_capture() public {
        _graduate();
        _give(whale, 30_000_000 ether); // 30% — exceeds quorum regardless of 4% vs 25%
        vm.warp(block.timestamp + 2);

        (address[] memory t, uint256[] memory v, bytes[] memory c, string memory d) = _captureProposal();
        vm.prank(whale);
        uint256 id = gov.propose(t, v, c, d);
        vm.warp(block.timestamp + gov.votingDelay() + 1);
        vm.prank(whale);
        gov.castVote(id, 1);
        vm.warp(block.timestamp + gov.votingPeriod() + 1);
        assertEq(uint256(gov.state(id)), uint256(IGovernor.ProposalState.Succeeded), "30% holder passes quorum");
        gov.execute(t, v, c, keccak256(bytes(d))); // governor (Agent owner) executes setTokenURI
        assertEq(agent.tokenURI(0), "CAPTURED", "governance controlled the agent (needs >=quorum, mode-independent)");
    }

    // ---------- E: agent-alive functions are governance-owned, not attacker-callable ----------
    function test_E_agent_alive_not_attacker_callable() public {
        _graduate();
        vm.startPrank(attacker);
        vm.expectRevert(); // OwnableUnauthorizedAccount: owner is the Governor
        agent.setTokenURI(0, "x");
        vm.expectRevert(); // OwnableUnauthorizedAccount
        agent.setProxyImplementation(address(0xBEEF));
        vm.stopPrank();
    }
}
