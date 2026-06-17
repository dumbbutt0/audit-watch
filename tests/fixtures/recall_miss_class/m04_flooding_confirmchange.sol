// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;
// M-04: per-call append to the staking change-log on a checkpoint/confirm surface with no rate limit ->
// a malicious validator floods stake/unstake requests and blocks confirmChange progress.
contract M04 {
    bytes[] internal changeLog;
    function stake(uint256) external { changeLog.push(abi.encode(msg.sender)); }                  // VULN: unbounded append
    function unstake(uint256) external { changeLog.push(abi.encode(msg.sender)); }                // VULN: unbounded append
    function confirmChange(uint64 n) external { for (uint256 i; i < n; ) { unchecked { ++i; } } } // floodable confirm
}
