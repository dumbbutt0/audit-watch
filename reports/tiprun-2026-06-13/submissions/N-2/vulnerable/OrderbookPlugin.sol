// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../../core/plugins/BasePlugin.sol";
import "../transactions/TradeTransLib.sol";
import "../../core/position/IPositionManager.sol";
import "../../core/config/GeneralConfig.sol";
import "../IOrderManager.sol";
import "../../core/signer/ISignerManager.sol";
import "../../funding/IFunding.sol";
import "../../Constants.sol";

contract OrderbookPlugin is BasePlugin {
    using TradeTransLib for Trade;

    IPositionManager public position;
    GeneralConfig public generalConfig;
    IOrderManager public order;
    ISignerManager public signer;
    /// @notice Optional funding contract. When unset (address(0)) funding is
    /// disabled and trades perform a plain position update (spot deployments).
    IFunding public funding;

    event TradeProcessed(Trade trade);

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

    function setGeneralConfig(address _g) external onlyOwner {
        generalConfig = GeneralConfig(_g);
    }

    function setOrder(address _o) external onlyOwner {
        order = IOrderManager(_o);
    }

    /// @notice Wire the funding contract to enable funding-aware trades. Leave
    /// unset for spot/funding-disabled deployments.
    function setFunding(address _f) external onlyOwner {
        funding = IFunding(_f);
    }

    function setSigner(address _s) external onlyOwner {
        signer = ISignerManager(_s);
    }

    function supportedTxTypes() external pure override returns (uint8[] memory) {
        uint8[] memory types = new uint8[](1);
        types[0] = TYPE_TRADE;
        return types;
    }

    function processTransaction(uint8 txType, bytes calldata payload)
        external
        override
        onlyTransactionProcessor
        returns (bool handled)
    {
        if (txType == TYPE_TRADE) {
            Trade memory trade = abi.decode(payload, (Trade));
            CollateralAssetInfo memory collateralInfo = generalConfig.getCollateralAssetInfo();
            trade.process(
                position, funding, generalConfig, order, signer, collateralInfo.assetId, generalConfig.getFeeAccountId(), transactionProcessor
            );
            emit TradeProcessed(trade);
            return true;
        }
        return false;
    }
}
