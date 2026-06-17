// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// "Safe" pair for the bridge fixture = the genuinely bridge-relevant version that SHOULD still escalate: the
// same vault verbs, but now paired with cross-chain coordination (a destination-chain message + L2 endpoint).
// This proves the demotion is precise, not a blanket suppression of vault verbs.
contract CrossChainVaultBridge {
    mapping(address => uint256) public balanceOf;

    // deposit + L2 endpoint + cross-chain message => bridge-relevant (must escalate)
    function deposit(uint256 amount, address recipient, uint64 destinationChain, bytes calldata message)
        external
    {
        balanceOf[recipient] += amount;
        _sendMessage(destinationChain, message); // relayer/endpoint coordination
    }

    function _sendMessage(uint64 destinationChain, bytes calldata message) internal {
        // L2 bridge endpoint / relayer dispatch (stand-in)
        destinationChain;
        message;
    }
}
