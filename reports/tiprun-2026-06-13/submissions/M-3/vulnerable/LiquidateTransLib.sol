// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../../orderbook/LimitOrder.sol";
import "../../orderbook/LimitOrderLib.sol";
import "../../funding/IFunding.sol";
import "../../orderbook/IOrderManager.sol";
import "../../core/signer/ISignerManager.sol";
import "../../core/position/IPositionManager.sol";
import "../../core/account/IAccountManager.sol";
import "../../core/config/GeneralConfig.sol";

struct Liquidate {
    LimitOrder liquidatorOrder;
    uint64 liquidatedUid;
    int256 actualCollateral;
    int256 actualSynthetic;
    uint256 actualLiquidatorFee;
}

/**
 * @title LiquidateTransLib
 * @dev Liquidation transactions
 */
library LiquidateTransLib {
    using LimitOrderLib for LimitOrder;

    function process(
        Liquidate memory liquidate,
        IPositionManager position,
        IFunding funding,
        GeneralConfig generalConfig,
        IOrderManager orderManager,
        ISignerManager signerManager,
        uint64 collateralAssetId,
        uint64 feeAccountId,
        address verifyingContract
    ) public {
        require(liquidate.liquidatedUid != 0, "LiquidateTransLib: liquidatedUid is 0");

        // deltas for the liquidated account/position
        int256 liquidatedCollateralDelta = 0;
        int256 liquidatedSyntheticDelta = 0;
        if (liquidate.liquidatorOrder.isBuyingSynthetic) {
            liquidatedCollateralDelta = liquidate.actualCollateral;
            liquidatedSyntheticDelta = -liquidate.actualSynthetic;
        } else {
            liquidatedCollateralDelta = -liquidate.actualCollateral;
            liquidatedSyntheticDelta = liquidate.actualSynthetic;
        }
        require(
            liquidate.liquidatorOrder.assetIdCollateral == collateralAssetId,
            "LiquidateTransLib: assetIdCollateral is not the same as collateral assetId"
        );
        require(
            generalConfig.isTradable(liquidate.liquidatorOrder.assetIdSynthetic),
            "LiquidateTransLib: assetIdSynthetic is not tradable"
        );

        uint64 syntheticAssetId = liquidate.liquidatorOrder.assetIdSynthetic;
        uint64 liquidatedUid = liquidate.liquidatedUid;

        // Look up the collateral position index for this asset and load the appropriate bucket
        uint64 cpIndex = position.getCollateralPositionIndex(liquidatedUid, syntheticAssetId);
        AccountPosition memory liquidatedPosition = position.getAccountPositionByCollateralIndex(liquidatedUid, cpIndex);

        // Apply funding on the liquidated position before resizing it (no-op when
        // funding is disabled). Core PositionManager stays funding-agnostic.
        if (address(funding) != address(0)) {
            liquidatedPosition = funding.applyFundingForAsset(liquidatedPosition, syntheticAssetId);
        }

        position.updatePosition(
            liquidatedPosition, liquidatedUid, liquidatedCollateralDelta, syntheticAssetId, liquidatedSyntheticDelta
        );
        liquidate.liquidatorOrder
            .execute(
                position,
                funding,
                orderManager,
                signerManager,
                feeAccountId,
                liquidate.actualCollateral,
                liquidate.actualSynthetic,
                liquidate.actualLiquidatorFee,
                true,
                verifyingContract
            );
    }
}
