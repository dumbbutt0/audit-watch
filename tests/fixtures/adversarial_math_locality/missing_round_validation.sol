// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// VULNERABLE (Swan/Dria H-02 shape): `purchase` is external and directly callable by the listing buyer,
// but performs NO local round/phase check. The phase guard lives in a DIFFERENT contract (BuyerAgent).
// A dependency clear that leans on BuyerAgent.getRoundPhase to clear Swan.purchase's missing local check
// is not path-dominant: the call graph shows purchase reachable without ever calling the guard.
contract Swan {
    mapping(uint256 => address) public buyerOf;

    // NO round validation here — yet a clear may claim "round validated by BuyerAgent.getRoundPhase".
    function purchase(uint256 assetId) external {
        require(msg.sender == buyerOf[assetId], "only buyer");
        // ... transfers funds + NFT, with no check that listing.round == current round ...
    }
}

contract BuyerAgent {
    // The phase guard the clear leans on — but nothing forces purchase() through it.
    function getRoundPhase() public view returns (uint8 phase) {
        return phase;
    }
}
