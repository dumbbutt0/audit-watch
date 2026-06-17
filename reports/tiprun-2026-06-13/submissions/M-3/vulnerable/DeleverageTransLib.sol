// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../../core/position/IPositionManager.sol";
import "../../Constants.sol";
import "../../core/config/GeneralConfig.sol";
import "../../core/account/IAccountManager.sol";
import "../../core/signer/ISignerManager.sol";
import "../../funding/IFunding.sol";
import "../../funding/FundingApplyLib.sol";

struct Deleverage {
    address deleveragableAddress;
    uint64 deleveragableAccountId; // Which account is being deleveraged (many-to-many support)
    address deleveragerSigner; // Who signed for deleverager
    uint64 deleveragerAccountId; // Which account deleverager operates on (many-to-many support)
    uint64 syntheticAssetId;
    int256 amountSynthetic;
    int256 amountCollateral;
    int256 deleveragerIsBuyingSynthetic;
}

/**
 * @title DeleverageTransLib
 * @dev Library for handling deleveraging operations
 */
library DeleverageTransLib {
    function process(
        Deleverage memory self,
        IPositionManager position,
        IFunding funding,
        GeneralConfig generalConfig,
        ISignerManager signerManager
    ) public {
        if (self.amountSynthetic <= 0 || self.amountCollateral <= 0) {
            revert("DeleverageTransLib: amountSynthetic or amountCollateral is less than or equal to 0");
        }
        require(generalConfig.isTradable(self.syntheticAssetId), "DeleverageTransLib: syntheticAssetId is not tradable");

        int256 deleveragerSyntheticDelta = 0;
        int256 deleveragerCollateralDelta = 0;
        int256 deleveragableSyntheticDelta = 0;
        int256 deleveragableCollateralDelta = 0;
        if (self.deleveragerIsBuyingSynthetic == 1) {
            deleveragerSyntheticDelta = self.amountSynthetic;
            deleveragerCollateralDelta = -self.amountCollateral;
            deleveragableSyntheticDelta = -self.amountSynthetic;
            deleveragableCollateralDelta = self.amountCollateral;
        } else {
            deleveragerSyntheticDelta = -self.amountSynthetic;
            deleveragerCollateralDelta = self.amountCollateral;
            deleveragableSyntheticDelta = self.amountSynthetic;
            deleveragableCollateralDelta = -self.amountCollateral;
        }

        // Use explicitly specified account IDs (many-to-many support)
        uint64 deleveragable = self.deleveragableAccountId;
        uint64 deleverager = self.deleveragerAccountId;

        require(
            signerManager.checkSigner(deleveragable, self.deleveragableAddress),
            "DeleverageTransLib: deleveragable signer unauthorized"
        );
        require(
            signerManager.checkSigner(deleverager, self.deleveragerSigner),
            "DeleverageTransLib: deleverager signer unauthorized"
        );

        // Ensure positions exist
        position.getOrCreatePosition(deleveragable, self.syntheticAssetId);
        position.getOrCreatePosition(deleverager, self.syntheticAssetId);

        FundingApplyLib.applyAndUpdate(
            position,
            funding,
            deleveragable,
            deleveragableCollateralDelta,
            self.syntheticAssetId,
            deleveragableSyntheticDelta
        );

        FundingApplyLib.applyAndUpdate(
            position, funding, deleverager, deleveragerCollateralDelta, self.syntheticAssetId, deleveragerSyntheticDelta
        );
    }
}
