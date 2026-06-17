// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;
// H-06: leave() is nonReentrant and makes a native transfer; sibling addBootstrap() mutates shared state
// WITHOUT the guard -> cross-function re-entry through the sibling is not prevented.
contract H06 {
    mapping(address => uint256) internal collateral;
    mapping(address => string) internal bootstrapNodes;
    modifier nonReentrant() { _; }
    function leave() external nonReentrant {
        uint256 amount = collateral[msg.sender]; collateral[msg.sender] = 0;
        payable(msg.sender).transfer(amount);                                                    // external/native call
    }
    function addBootstrap(string calldata a) external { bootstrapNodes[msg.sender] = a; }         // VULN: unguarded sibling mutation
}
contract H06Safe {
    mapping(address => uint256) internal collateral;
    mapping(address => string) internal bootstrapNodes;
    modifier nonReentrant() { _; }
    function leave() external nonReentrant {
        uint256 amount = collateral[msg.sender]; collateral[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
    function addBootstrap(string calldata a) external nonReentrant { bootstrapNodes[msg.sender] = a; }  // SAFE: guarded
}
