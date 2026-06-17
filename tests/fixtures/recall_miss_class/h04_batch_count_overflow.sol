// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;
// H-04: commitBottomUpMsg appends/increments the batch message count with NO local limit check; the limit
// is enforced only in ensureValid elsewhere -> the writer can drive the count past maxMsgsPerBatch.
contract H04 {
    uint64 public batchMsgCount;
    uint64 public maxMsgsPerBatch;
    function commitBottomUpMsg(bytes calldata) external { batchMsgCount += 1; }                  // VULN: unbounded increment
    function ensureValidCheckpoint(uint64 n) external view { require(n <= maxMsgsPerBatch); }     // limit checked separately
}
contract H04Safe {
    uint64 public batchMsgCount; uint64 public maxMsgsPerBatch;
    function commitBottomUpMsg(bytes calldata) external {
        require(batchMsgCount < maxMsgsPerBatch);                                                 // SAFE: local bound
        batchMsgCount += 1;
    }
}
