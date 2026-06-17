// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract VaultSafe {
    function maxWithdraw(address o) external view returns (uint256) { return _availableFor(o); }
    function previewWithdraw(uint256 a) external view returns (uint256) { return _toShares(a, Rounding.Up); }
}
