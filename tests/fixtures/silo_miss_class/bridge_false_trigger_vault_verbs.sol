// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Bridge-lens FP control: a plain vault with deposit/withdraw/mint and a `recipient` parameter must NOT trip
// the bridge thread-escalation gate (round 2 demotes generic vault verbs). There is no cross-chain
// coordination here at all — no message/endpoint/relayer/domain/L1/L2/escrow.
contract PlainVaultNoBridge {
    mapping(address => uint256) public balanceOf;

    function deposit(uint256 amount, address recipient) external {
        balanceOf[recipient] += amount;
    }

    function withdraw(uint256 amount, address recipient) external {
        balanceOf[msg.sender] -= amount;
        balanceOf[recipient] += amount; // local accounting only
    }

    function mint(uint256 amount, address recipient) external {
        balanceOf[recipient] += amount;
    }
}
