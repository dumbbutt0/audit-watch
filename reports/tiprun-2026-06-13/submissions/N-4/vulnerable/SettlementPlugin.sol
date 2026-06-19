// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../../core/plugins/BasePlugin.sol";
import "../transactions/SettlementTransLib.sol";
import "../../core/position/IPositionManager.sol";
import "../../Constants.sol";

contract SettlementPlugin is BasePlugin {
    using SettlementTransLib for Settlement;

    IPositionManager public position;

    event SettlementProcessed(Settlement settlement);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address owner) public initializer {
        if (owner == address(0)) owner = msg.sender;
        __Ownable_init(owner);
    }

    function setPosition(address _p) external onlyOwner {
        position = IPositionManager(_p);
    }

    function supportedTxTypes() external pure override returns (uint8[] memory) {
        uint8[] memory types = new uint8[](1);
        types[0] = TYPE_SETTLEMENT;
        return types;
    }

    function processTransaction(uint8 txType, bytes calldata payload)
        external
        override
        onlyTransactionProcessor
        returns (bool handled)
    {
        if (txType == TYPE_SETTLEMENT) {
            Settlement memory settlement = abi.decode(payload, (Settlement));
            settlement.process(position);
            emit SettlementProcessed(settlement);
            return true;
        }
        return false;
    }
}
