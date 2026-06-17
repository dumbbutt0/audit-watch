// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;
// H-09: external call to the recipient inside a checkpoint/batch loop, with unbounded returndata loaded ->
// one malicious recipient can revert or gas-bomb and block the whole checkpoint submission.
contract H09 {
    function execBottomUpMsgs(Msg[] calldata msgs) external {                                     // checkpoint/batch context + loop
        for (uint256 i; i < msgs.length; ) {
            (bool ok, bytes memory ret) = msgs[i].to.call{value: msgs[i].value}(msgs[i].data);    // VULN: external call + returndata
            require(ok, string(ret));
            unchecked { ++i; }
        }
    }
    struct Msg { address to; uint256 value; bytes data; }
}
contract H09Safe {
    function execBottomUpMsgs(Msg[] calldata msgs) external {
        for (uint256 i; i < msgs.length; ) {
            (bool ok, ) = msgs[i].to.call{value: msgs[i].value, gas: 100000}("");                 // SAFE: no returndata, capped gas, no revert-on-fail
            ok; unchecked { ++i; }
        }
    }
    struct Msg { address to; uint256 value; bytes data; }
}
