// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "../../Constants.sol";

struct CollateralAssetInfo {
    uint64 assetId;
    int256 resolution;
}

struct RiskFactorSegment {
    int256 upperBound;
    int256 risk;
}

struct SyntheticAssetInfo {
    int256 resolution;
    RiskFactorSegment[] riskFactorSegments;
    uint64[] oraclePriceSignedAssetIds;
    int256 oraclePriceQuorum;
    address[] oraclePriceSigners;
    int256 maxFundingRate;
}

contract GeneralConfig is Initializable, OwnableUpgradeable {
    CollateralAssetInfo public collateralAssetInfo;
    uint64 public feeAccountId;
    mapping(uint64 => SyntheticAssetInfo) public syntheticAssetsInfo;
    bool public isRiskByBalanceOnly;
    uint64 public configVersion;

    address public batchConfig;
    address public fundingFeeder;
    address public assetAdmin;

    event ConfigVersionChanged(uint64 configVersion);

    modifier canIncrementConfigVersion() {
        require(msg.sender == owner() || msg.sender == batchConfig, "only owner can increment config version");
        _;
    }

    modifier onlyAssetAdmin() {
        require(msg.sender == assetAdmin, "only asset admin can call this function");
        _;
    }

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

    function setBatchConfig(address _batchConfig) public onlyOwner {
        batchConfig = _batchConfig;
    }

    function setFundingFeeder(address _fundingFeeder) public onlyOwner {
        fundingFeeder = _fundingFeeder;
    }

    function setAssetAdmin(address _assetAdmin) public onlyOwner {
        assetAdmin = _assetAdmin;
    }

    function setConfigVersion(uint64 _configVersion) public onlyOwner {
        configVersion = _configVersion;
        emit ConfigVersionChanged(configVersion);
    }

    function incrConfigVersionInternal() internal {
        configVersion++;
        emit ConfigVersionChanged(configVersion);
    }

    function incrConfigVersion() public canIncrementConfigVersion {
        incrConfigVersionInternal();
    }

    function getFeeAccountId() public view returns (uint64) {
        return feeAccountId;
    }

    function getRiskFactor(uint64 assetId, int256 absBalance, int256 priceFxp) public view returns (int256, bool) {
        SyntheticAssetInfo memory assetInfo = syntheticAssetsInfo[assetId];
        RiskFactorSegment[] memory segments = assetInfo.riskFactorSegments;

        uint256 segmentLen = segments.length;
        int256 amount = absBalance;
        if (!isRiskByBalanceOnly) {
            amount = priceFxp * absBalance;
        }

        for (uint256 i = 0; i < segmentLen;) {
            if (amount <= segments[i].upperBound * FXP_32_ONE) {
                return (segments[i].risk, true);
            }
            unchecked {
                ++i;
            }
        }
        return (0, false);
    }

    function setMaxFundingRate(uint64 assetId, int256 _maxFundingRate) external onlyAssetAdmin {
        require(syntheticAssetsInfo[assetId].resolution != 0, "GeneralConfig: synthetic asset not found");
        require(_maxFundingRate > 0, "GeneralConfig: max funding rate must be positive");
        syntheticAssetsInfo[assetId].maxFundingRate = _maxFundingRate;
        incrConfigVersionInternal();
    }

    function getMaxFundingRate(uint64 assetId) external view returns (int256) {
        return syntheticAssetsInfo[assetId].maxFundingRate;
    }

    function resolutionCheck(int256 resolution) internal pure {
        require(
            resolution >= ASSET_RESOLUTION_LOWER_BOUND && resolution < ASSET_RESOLUTION_UPPER_BOUND,
            "resolution out of bounds"
        );
    }

    function setCollateralAssetInfo(CollateralAssetInfo calldata _collateralAssetInfo) external onlyAssetAdmin {
        resolutionCheck(_collateralAssetInfo.resolution);
        require(
            _collateralAssetInfo.assetId != 0 && _collateralAssetInfo.assetId != NO_SYNTHETIC_DELTA_ASSET_ID,
            "GeneralConfig: collateral assetId invalid"
        );
        collateralAssetInfo = _collateralAssetInfo;
        incrConfigVersionInternal();
    }

    function setFeeAccountId(uint64 _feeAccountId) external onlyOwner {
        feeAccountId = _feeAccountId;
        incrConfigVersionInternal();
    }

    function setSyntheticAssetsInfo(uint64[] calldata assetIds, SyntheticAssetInfo[] calldata _syntheticAssetsInfo)
        external
    {
        require(msg.sender == owner() || msg.sender == batchConfig, "GeneralConfig: only owner or batchConfig");
        uint256 len = assetIds.length;
        require(len == _syntheticAssetsInfo.length, "GeneralConfig: synthetic asset length mismatch");
        require(len > 0, "GeneralConfig: no synthetic assets");

        for (uint256 i = 0; i < len;) {
            resolutionCheck(_syntheticAssetsInfo[i].resolution);
            require(
                assetIds[i] != 0 && assetIds[i] != NO_SYNTHETIC_DELTA_ASSET_ID,
                "GeneralConfig: synthetic assetId invalid"
            );
            require(_syntheticAssetsInfo[i].maxFundingRate > 0, "GeneralConfig: max funding rate must be positive");

            uint256 idsLen = _syntheticAssetsInfo[i].oraclePriceSignedAssetIds.length;
            uint256 signersLen = _syntheticAssetsInfo[i].oraclePriceSigners.length;
            require(
                idsLen == signersLen && idsLen > 0,
                "GeneralConfig: oracle price signed assetIds and signers length mismatch"
            );

            syntheticAssetsInfo[assetIds[i]] = _syntheticAssetsInfo[i];

            // Funding is an independent, optional module. It seeds its own index
            // lazily (first funding tick / first apply), so GeneralConfig no longer
            // pre-seeds a funding snapshot here and does not depend on IFunding.
            unchecked {
                ++i;
            }
        }

        // TODO: think about how to do it.
        // Now we dynamically add contract so do not incr config verison.

        // incrConfigVersionInternal();
    }

    function isTradable(uint64 assetId) public view returns (bool) {
        return syntheticAssetsInfo[assetId].resolution != 0;
    }

    function removeSyntheticAssetInfo(uint64 assetId) external onlyOwner {
        require(syntheticAssetsInfo[assetId].resolution != 0, "GeneralConfig: synthetic asset not found");
        delete syntheticAssetsInfo[assetId];
        incrConfigVersionInternal();
    }

    function setIsRiskByBalanceOnly(bool _isRiskByBalanceOnly) external onlyOwner {
        isRiskByBalanceOnly = _isRiskByBalanceOnly;
        incrConfigVersionInternal();
    }

    function getCollateralAssetInfo() public view returns (CollateralAssetInfo memory) {
        return collateralAssetInfo;
    }

    function getSyntheticAssetInfo(uint64 assetId) external view returns (SyntheticAssetInfo memory) {
        require(isTradable(assetId), "GeneralConfig: asset not tradable");
        return syntheticAssetsInfo[assetId];
    }
}
