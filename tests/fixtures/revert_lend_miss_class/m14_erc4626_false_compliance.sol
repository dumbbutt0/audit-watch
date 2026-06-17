// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// M-14: claims ERC4626 compliance but maxWithdraw ignores open-position lockup and previewWithdraw is not
// consistent with withdraw → a "reviewed → clean" 4626 verdict without the checklist misses this.
contract Vault {
    function maxWithdraw(address) external pure returns (uint256) { return type(uint256).max; }  // wrong
    function previewWithdraw(uint256 a) external view returns (uint256) { return a; }             // ignores rounding
}
