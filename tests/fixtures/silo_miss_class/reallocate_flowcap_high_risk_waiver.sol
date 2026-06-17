// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Waiver-discipline fixture: reallocation / flow-cap sinks move depositor funds between markets and set the
// per-market supply caps that bound that movement. These are high-risk vault-accounting sinks and may NOT be
// swept under a broad cluster waiver — they require a per-sink waiver (or execution). waiver_utils.risk_class
// must classify reallocateTo / setFlowCaps / market-cap as `vault_accounting`.
contract PublicAllocatorLike {
    struct FlowCap { uint128 maxIn; uint128 maxOut; }
    mapping(address => FlowCap) public flowCaps;

    // moves assets out of one market and into another — depositor funds in flight
    function reallocateTo(address fromMarket, address toMarket, uint256 assets) external {
        fromMarket; toMarket; assets;
    }

    // sets the per-market flow cap that bounds reallocation
    function setFlowCaps(address market, uint128 maxIn, uint128 maxOut) external {
        flowCaps[market] = FlowCap(maxIn, maxOut);
    }
}
