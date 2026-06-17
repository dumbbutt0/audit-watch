// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// P121 runtime harness — traitforge NukeFund.nuke (research-only, un-wired).
// One question: can a permissionless caller extract more than the designed cap (<=50%/call), bypass the
// ownership/approval/maturity guards, re-nuke a burned token, or break fund accounting (underflow/insolvency)?
// Runtime decides. traitforge src is UNMUTATED (NukeFund imported via remapping). Cross-contract maturity/entropy
// questions (real TraitForgeNft mint bookkeeping) are out of mock scope -> NEEDS_CONTEXT (see decision.md).

import "forge-std/Test.sol";
import {NukeFund} from "traitforge/NukeFund/NukeFund.sol";
import {ITraitForgeNft} from "traitforge/TraitForgeNft/ITraitForgeNft.sol";

// ---- mock NFT: only the functions NukeFund.nuke()/calculateNukeFactor()/canTokenBeNuked() call ----
contract MockTraitForgeNft {
    mapping(uint256 => address) public _owner;
    mapping(uint256 => address) public approved;     // getApproved
    mapping(address => mapping(address => bool)) public operatorAll; // isApprovedForAll
    mapping(uint256 => uint256) public entropy;
    mapping(uint256 => uint256) public creationTs;
    mapping(uint256 => uint256) public lastXferTs;

    function setToken(uint256 id, address own, uint256 ent, uint256 creation, uint256 lastX) external {
        _owner[id] = own; entropy[id] = ent; creationTs[id] = creation; lastXferTs[id] = lastX;
    }
    function setApproved(uint256 id, address to) external { approved[id] = to; }
    function setApprovalForAll(address own, address op, bool ok) external { operatorAll[own][op] = ok; }

    function ownerOf(uint256 id) external view returns (address) { return _owner[id]; }
    function getApproved(uint256 id) external view returns (address) { return approved[id]; }
    function isApprovedForAll(address own, address op) external view returns (bool) { return operatorAll[own][op]; }
    function isApprovedOrOwner(address spender, uint256 id) external view returns (bool) {
        address o = _owner[id];
        return spender == o || approved[id] == spender || operatorAll[o][spender];
    }
    function getTokenEntropy(uint256 id) external view returns (uint256) { return entropy[id]; }
    function getTokenCreationTimestamp(uint256 id) external view returns (uint256) { return creationTs[id]; }
    function getTokenLastTransferredTimestamp(uint256 id) external view returns (uint256) { return lastXferTs[id]; }
    function burn(uint256 id) external { _owner[id] = address(0); } // burned -> ownerOf == 0
}

// ---- mock airdrop: only what NukeFund.receive() reads when funding the fund ----
contract MockAirdrop {
    function airdropStarted() external pure returns (bool) { return true; }
    function daoFundAllowed() external pure returns (bool) { return true; }
}

contract NukeFundRuntime is Test {
    NukeFund nf;
    MockTraitForgeNft nft;
    MockAirdrop air;
    address dev = makeAddr("dev");
    address dao = makeAddr("dao");
    address attacker = makeAddr("attacker");
    address victim = makeAddr("victim");

    function _deploy() internal {
        nft = new MockTraitForgeNft();
        air = new MockAirdrop();
        nf = new NukeFund(address(nft), address(air), payable(dev), payable(dao));
        // this test contract is the owner (deployer); enable age scaling so high-entropy tokens exceed the cap param
        nf.setAgeMultplier(10000);
    }

    // helper: fund the NukeFund by sending ETH through receive() (90% goes to `fund`, 10% devShare to dao)
    function _fund(uint256 grossWei) internal returns (uint256 fundAdded) {
        vm.deal(address(this), address(this).balance + grossWei);
        (bool ok, ) = address(nf).call{value: grossWei}("");
        require(ok, "fund send failed");
        fundAdded = grossWei - grossWei / nf.taxCut(); // 90%
    }

    // mint a mock token to `own`, mature & approved to NukeFund
    function _mintMature(uint256 id, address own, uint256 ent) internal {
        // created long ago, last transferred long ago (mature), high entropy
        nft.setToken(id, own, ent, 1, 1);
        vm.warp(block.timestamp + 30 days);
        vm.prank(own);
        // owner sets approvalForAll so NukeFund may transfer/burn
        nft.setApprovalForAll(own, address(nf), true);
        nft.setApproved(id, address(nf)); // getApproved(id) == NukeFund (satisfies the 2nd guard)
    }

    // ---------- CASE A: guards ----------
    function test_A_guards_block_unauthorized_and_immature() public {
        _deploy(); _fund(100 ether);
        nft.setToken(1, victim, 500000, 1, 1); // victim's token, mature
        nft.setApproved(1, address(nf));
        // A1: attacker (not owner/approved) cannot nuke victim's token
        vm.prank(attacker);
        vm.expectRevert(bytes("ERC721: caller is not token owner or approved"));
        nf.nuke(1);
        // A2: owner but NukeFund NOT approved to move the NFT -> revert
        nft.setToken(2, attacker, 500000, 1, 1);
        // no approval set for token 2
        vm.prank(attacker);
        vm.expectRevert(bytes("Contract must be approved to transfer the NFT."));
        nf.nuke(2);
        // A3: owner + approved but IMMATURE (last transferred just now) -> revert
        nft.setToken(3, attacker, 500000, block.timestamp, block.timestamp);
        nft.setApproved(3, address(nf));
        vm.prank(attacker);
        vm.expectRevert(bytes("Token is not mature yet"));
        nf.nuke(3);
    }

    // ---------- CASE B: high factor -> claim capped at fund/2 exactly ----------
    function test_B_highFactor_capped_at_half() public {
        _deploy(); uint256 added = _fund(100 ether);
        uint256 fundBefore = nf.getFundBalance();
        assertEq(fundBefore, added, "fund == 90% of gross");
        _mintMature(1, attacker, 999999); // huge entropy -> finalNukeFactor > nukeFactorMaxParam(50000)
        assertGt(nf.calculateNukeFactor(1), nf.nukeFactorMaxParam(), "factor exceeds cap param");

        uint256 expectClaim = fundBefore / nf.maxAllowedClaimDivisor(); // fund/2
        uint256 atkBefore = attacker.balance;
        vm.prank(attacker);
        nf.nuke(1);
        assertEq(attacker.balance - atkBefore, expectClaim, "attacker received exactly fund/2");
        assertEq(nf.getFundBalance(), fundBefore - expectClaim, "fund reduced by exactly claim");
        assertEq(nft.ownerOf(1), address(0), "token burned");
        // never more than the cap
        assertLe(expectClaim, fundBefore / 2);
    }

    // ---------- CASE C: no re-nuke (burned token) ----------
    function test_C_cannot_renuke() public {
        _deploy(); _fund(100 ether);
        _mintMature(1, attacker, 999999);
        vm.prank(attacker); nf.nuke(1);
        // second nuke: token burned -> isApprovedOrOwner false
        vm.prank(attacker);
        vm.expectRevert(bytes("ERC721: caller is not token owner or approved"));
        nf.nuke(1);
    }

    // ---------- CASE D: multi-token drain stays bounded & solvent ----------
    function test_D_multitoken_drain_bounded_and_solvent() public {
        _deploy(); uint256 added = _fund(100 ether);
        _mintMature(1, attacker, 999999);
        _mintMature(2, attacker, 999999);

        uint256 fund0 = nf.getFundBalance();
        vm.prank(attacker); nf.nuke(1);
        uint256 fund1 = nf.getFundBalance();
        assertEq(fund1, fund0 - fund0 / 2, "1st nuke took exactly 50%");
        assertGe(address(nf).balance, fund1, "solvent after 1st (balance >= fund)");

        vm.prank(attacker); nf.nuke(2);
        uint256 fund2 = nf.getFundBalance();
        assertEq(fund2, fund1 - fund1 / 2, "2nd nuke took exactly 50% of remaining");
        assertGe(address(nf).balance, fund2, "solvent after 2nd");
        // total drained ~75%, fund never underflowed (still positive)
        assertGt(fund2, 0, "fund still positive (no underflow)");
        assertEq(fund2, added / 4, "geometric: 25% of original remains");
    }

    // ---------- CASE E: low factor -> proportional claim, <= cap, no underflow ----------
    function test_E_lowFactor_proportional() public {
        _deploy(); _fund(100 ether);
        // small entropy + modest age -> finalNukeFactor <= nukeFactorMaxParam
        nft.setToken(1, attacker, 4000, 1, 1); // entropy/40 = 100 initial; age contributes little
        vm.warp(block.timestamp + 30 days);
        vm.prank(attacker); nft.setApprovalForAll(attacker, address(nf), true);
        nft.setApproved(1, address(nf));
        uint256 factor = nf.calculateNukeFactor(1);
        assertLe(factor, nf.nukeFactorMaxParam(), "low-factor branch");
        uint256 fundBefore = nf.getFundBalance();
        uint256 expect = (fundBefore * factor) / nf.MAX_DENOMINATOR();
        uint256 atkBefore = attacker.balance;
        vm.prank(attacker); nf.nuke(1);
        assertEq(attacker.balance - atkBefore, expect, "proportional claim == fund*factor/DENOM");
        assertLe(expect, fundBefore / 2, "still <= 50% cap");
        assertEq(nf.getFundBalance(), fundBefore - expect, "fund reduced by exactly claim");
    }

    receive() external payable {}
}
