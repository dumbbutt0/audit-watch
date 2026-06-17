// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./IRisk.sol";
import "../position/IPositionManager.sol";
import "../position/SyntheticPositionLib.sol";
import "../oracle/IOracle.sol";
import "../config/GeneralConfig.sol";
import "../../Constants.sol";

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract Risk is IRisk, Initializable, OwnableUpgradeable {
    using SyntheticPositionLib for uint256;

    IOracle public oracle;
    GeneralConfig public generalConfig;
    IPositionManager public positionManager;

    event OracleSet(address oracle);
    event GeneralConfigSet(address generalConfig);
    event PositionManagerSet(address positionManager);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address owner) public initializer {
        if (owner == address(0)) {
            owner = msg.sender;
        }
        __Ownable_init(owner);
    }

    // ============ Admin Functions ============

    function setOracle(address _oracle) external onlyOwner {
        oracle = IOracle(_oracle);
        emit OracleSet(_oracle);
    }

    function setGeneralConfig(address _generalConfig) external onlyOwner {
        generalConfig = GeneralConfig(_generalConfig);
        emit GeneralConfigSet(_generalConfig);
    }

    function setPositionManager(address _positionManager) external onlyOwner {
        positionManager = IPositionManager(_positionManager);
        emit PositionManagerSet(_positionManager);
    }

    // ============ Risk Functions ============

    function getAssetValueAndRisk(SyntheticPosition memory asset) public view returns (int256, int256) {
        (int256 oraclePrice, bool priceOk) = oracle.getPrice(asset.packed.getAssetId());
        int256 absAmount = asset.amount < 0 ? -asset.amount : asset.amount;
        (int256 riskFactor, bool riskOk) =
            generalConfig.getRiskFactor(asset.packed.getAssetId(), absAmount, oraclePrice);
        if (!priceOk) {
            require(!riskOk, "Risk: price missing but risk exists");
            return (0, 0);
        }
        require(riskOk, "Risk: no risk");
        int256 valueRep = asset.amount * oraclePrice;
        int256 riskRep = absAmount * oraclePrice * riskFactor;
        return (valueRep, riskRep);
    }

    function getAccountPositionStatus(AccountPosition memory position) public view returns (int256, int256) {
        int256 totalValueRep = position.collateralAmount * FXP_32_ONE;
        int256 totalRiskRep = 0;
        uint256 len = position.assets.length;
        for (uint256 i = 0; i < len;) {
            (int256 valueRep, int256 riskRep) = getAssetValueAndRisk(position.assets[i]);
            totalValueRep += valueRep;
            totalRiskRep += riskRep;
            unchecked {
                ++i;
            }
        }
        return (totalValueRep, totalRiskRep);
    }

    function getAccountPositionStatusWithBoundaryCheck(AccountPosition memory position)
        public
        view
        returns (int256, int256)
    {
        (int256 totalValueRep, int256 totalRiskRep) = getAccountPositionStatus(position);
        if (totalValueRep < TOTAL_VALUE_LOWER_BOUND_FXP || totalValueRep > TOTAL_VALUE_UPPER_BOUND_FXP) {
            revert("PM: val range");
        }
        int256 totalRiskUpperBoundRep = TOTAL_RISK_UPPER_BOUND * FXP_32_ONE * FXP_32_ONE;
        if (totalRiskRep >= totalRiskUpperBoundRep) {
            revert("PM: risk range");
        }
        return (totalValueRep, totalRiskRep);
    }

    /// @inheritdoc IBalanceCheck
    function validateWithdrawal(uint64 accountId, int256 amount) external view {
        require(positionManager.getCollateralBalanceByAccountId(accountId) >= amount, "Risk: insufficient balance");
    }

    function checkValidTransition(
        AccountPosition memory initPosition,
        AccountPosition memory updatedPosition,
        uint64 accountId,
        uint64 collateralPositionIndex
    ) public view {
        // Load full position from storage for complete risk calculation
        AccountPosition memory fullStorage =
            positionManager.getAccountPositionByCollateralIndex(accountId, collateralPositionIndex);

        // Build full positions by merging storage with partial init/updated
        AccountPosition memory fullUpdated = _buildFullPosition(fullStorage, updatedPosition);

        (int256 updatedTotalValue, int256 updatedTotalRisk) = getAccountPositionStatusWithBoundaryCheck(fullUpdated);
        if (updatedTotalRisk <= updatedTotalValue * FXP_32_ONE) {
            return;
        }

        AccountPosition memory fullInit = _buildFullPosition(fullStorage, initPosition);
        (int256 initTotalValue, int256 initTotalRisk) = getAccountPositionStatusWithBoundaryCheck(fullInit);

        checkSmallerInSyntheticHoldings(fullInit, fullUpdated);

        // Compare value/risk ratios: initValue/initRisk >= updatedValue/updatedRisk
        // Rearranged to avoid division: initValue * updatedRisk >= updatedValue * initRisk
        // Safe from overflow because boundary checks above constrain both value and risk
        if (initTotalValue * updatedTotalRisk < updatedTotalValue * initTotalRisk) {
            revert("PM: val/risk dec");
        }
        if (initTotalRisk == 0) {
            if (updatedTotalValue < initTotalValue) {
                revert("PM: val dec");
            }
        }
    }

    /**
     * @dev Build a full position by merging the storage position with a partial position.
     * Partial has 0 assets (deposit/withdraw) or 1 asset (trade).
     * Collateral is always taken from the partial position (which has funding applied).
     */
    function _buildFullPosition(AccountPosition memory fullStorage, AccountPosition memory partialPos)
        internal
        pure
        returns (AccountPosition memory)
    {
        if (partialPos.assets.length == 0) {
            // Deposit/withdraw: use storage assets with partial's collateral
            return AccountPosition(
                fullStorage.accountId,
                fullStorage.collateralPositionIndex,
                partialPos.collateralAmount,
                fullStorage.assets
            );
        }

        // Trade: find and replace the target asset in storage
        uint64 targetAssetId = partialPos.assets[0].packed.getAssetId();
        uint256 storageLen = fullStorage.assets.length;
        bool found = false;

        for (uint256 i = 0; i < storageLen;) {
            if (fullStorage.assets[i].packed.getAssetId() == targetAssetId) {
                found = true;
                break;
            }
            unchecked {
                ++i;
            }
        }

        SyntheticPosition[] memory assets;
        if (found) {
            assets = new SyntheticPosition[](storageLen);
            for (uint256 i = 0; i < storageLen;) {
                if (fullStorage.assets[i].packed.getAssetId() == targetAssetId) {
                    assets[i] = partialPos.assets[0];
                } else {
                    assets[i] = fullStorage.assets[i];
                }
                unchecked {
                    ++i;
                }
            }
        } else {
            // New asset: append to storage assets
            assets = new SyntheticPosition[](storageLen + 1);
            for (uint256 i = 0; i < storageLen;) {
                assets[i] = fullStorage.assets[i];
                unchecked {
                    ++i;
                }
            }
            assets[storageLen] = partialPos.assets[0];
        }

        return AccountPosition(
            fullStorage.accountId, fullStorage.collateralPositionIndex, partialPos.collateralAmount, assets
        );
    }

    function checkSmallerInSyntheticHoldings(
        AccountPosition memory initPosition,
        AccountPosition memory updatedPosition
    ) public pure {
        uint256 updatedLen = updatedPosition.assets.length;
        for (uint256 i = 0; i < updatedLen;) {
            SyntheticPosition memory asset = updatedPosition.assets[i];
            uint64 assetId = asset.packed.getAssetId();
            int256 updatedAmount = asset.amount;
            uint256 findJ = type(uint256).max;
            uint256 initLen = initPosition.assets.length;
            for (uint256 j = 0; j < initLen;) {
                if (initPosition.assets[j].packed.getAssetId() == assetId) {
                    findJ = j;
                    break;
                }
                unchecked {
                    ++j;
                }
            }
            if (findJ == type(uint256).max) {
                revert("PM: risk inc");
            }
            SyntheticPosition memory initAsset = initPosition.assets[findJ];
            int256 initAmount = initAsset.amount;
            if ((initAmount < 0) != (updatedAmount < 0)) {
                revert("PM: sign change");
            }

            int256 absInit = initAmount < 0 ? -initAmount : initAmount;
            int256 absUpdated = updatedAmount < 0 ? -updatedAmount : updatedAmount;
            if (absInit < absUpdated) {
                revert("PM: bal inc");
            }
            unchecked {
                ++i;
            }
        }
    }
}
