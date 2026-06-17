// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;
// H-07: compact() iterates with an ABSOLUTE index compared against the pending count -> skips entries.
contract H07 {
    struct Releases { uint256 startIdx; uint256[] amounts; }
    mapping(address => Releases) internal rel;
    function addNewRelease(address v, uint256 amt) internal { rel[v].amounts.push(amt); }          // queue append
    function compact(address v) internal returns (uint256 paid) {                                  // VULN: index vs pending count
        Releases storage r = rel[v];
        for (uint256 i = 0; i < r.amounts.length; ) { paid += r.amounts[i]; unchecked { ++i; } }   // absolute i vs startIdx mismatch
        r.startIdx = r.amounts.length;
    }
}
