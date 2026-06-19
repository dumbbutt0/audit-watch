// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./IPositionManager.sol";
import "./SyntheticPositionLib.sol";
import "../risk/IMarginCheck.sol";
import "../risk/IMarginCheckProvider.sol";
import "../risk/NullMarginCheck.sol";
import "../config/GeneralConfig.sol";
import "../account/IAccountManager.sol";
import "../plugins/ITransactionPlugin.sol";
import "../../Constants.sol";

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract PositionManager is IPositionManager, Initializable, OwnableUpgradeable {
    using SyntheticPositionLib for SyntheticPosition;
    using SyntheticPositionLib for uint256;

    // Composite key: (accountId, assetId) encoded as uint128
    // [0-63]: accountId (uint64), [64-127]: assetId (uint64)
    mapping(uint128 => SyntheticPosition) public syntheticPositions;
    // Composite key: (accountId, assetId) => collateral position index
    mapping(uint128 => uint64) private _assetCollateralPositionIndex;

    function _toUint64Account(uint64 accountId) internal pure returns (uint64) {
        require(accountId <= type(uint64).max, "PM: accountId overflow");
        return uint64(accountId);
    }

    // Helper function to encode (accountId, assetId) into composite key
    function _encodeKey(uint64 accountId, uint64 assetId) internal pure returns (uint128) {
        require(assetId != 0 && assetId != NO_SYNTHETIC_DELTA_ASSET_ID, "PM: invalid assetId");
        uint64 accountKey = _toUint64Account(accountId);
        uint64 assetKey = assetId;
        return (uint128(accountKey) << 64) | uint128(assetKey);
    }

    function _getCollateralPositionIndex(uint64 accountId, uint64 assetId) internal view returns (uint64) {
        return _assetCollateralPositionIndex[_encodeKey(accountId, assetId)];
    }

    IAccountManager public accountManager;
    GeneralConfig public generalConfig;
    address public transactionProcessor;

    /// @notice No-op IMarginCheck fallback for deployments without a
    /// CAP_MARGIN_CHECK provider (e.g. spot). Deployed once at initialize().
    IMarginCheck public nullMarginCheck;

    event AccountPositionUpdated(uint64 indexed account, AccountPosition position);
    event AccountCollateralUpdated(uint64 indexed account, int256 newCollateral);
    event AccountManagerSet(address accountManager);
    event GeneralConfigSet(address generalConfig);
    event CollateralPositionIndexSet(uint64 indexed accountId, uint64 indexed assetId, uint64 collateralPositionIndex);
    event CollateralTransferred(uint64 indexed accountId, uint64 fromIndex, uint64 toIndex, int256 amount);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address owner) public initializer {
        if (owner == address(0)) {
            owner = msg.sender;
        }
        __Ownable_init(owner);
        nullMarginCheck = new NullMarginCheck();
    }

    /// @notice Discover the IMarginCheck service through the capability registry.
    /// Falls back to NullMarginCheck (no-op) when no CAP_MARGIN_CHECK provider
    /// is registered — spot deployments don't have maintenance margin, so every
    /// transition is "valid" by definition.
    function _marginCheck() internal view returns (IMarginCheck) {
        address provider = ICapabilityRegistry(transactionProcessor).capabilityProvider(CAP_MARGIN_CHECK);
        if (provider == address(0)) return nullMarginCheck;
        return IMarginCheckProvider(provider).marginCheck();
    }

    modifier onlyAuthorizedCaller() {
        require(
            ICallerRegistry(transactionProcessor).isAuthorizedCaller(msg.sender) || msg.sender == owner(),
            "PM: not authorized"
        );
        _;
    }

    // ============ Position Loading ============

    /**
     * @dev Load a single collateral bucket for an account
     */
    function _loadPositionByCollateralIndex(uint64 accountId, uint64 collateralPositionIndex)
        internal
        view
        returns (AccountPosition memory)
    {
        if (accountManager.isAccountIdRegistered(accountId) == false) {
            revert("PM: acct not reg");
        }

        int256 collateralAmount = accountManager.getCollateralPositionBalance(accountId, collateralPositionIndex);
        uint64[] memory assetIds = accountManager.getAssetIdListByCollateralPosition(accountId, collateralPositionIndex);
        SyntheticPosition[] memory assets = new SyntheticPosition[](assetIds.length);
        uint256 len = assetIds.length;
        for (uint256 i = 0; i < len;) {
            assets[i] = syntheticPositions[_encodeKey(accountId, assetIds[i])];
            unchecked {
                ++i;
            }
        }
        return AccountPosition(accountId, collateralPositionIndex, collateralAmount, assets);
    }

    /**
     * @dev Load collateral + a single specific asset (O(1) storage reads)
     */
    function _loadPositionForAsset(uint64 accountId, uint64 collateralPositionIndex, uint64 syntheticAssetId)
        internal
        view
        returns (AccountPosition memory)
    {
        require(accountManager.isAccountIdRegistered(accountId), "PM: acct not reg");
        int256 collateralAmount = accountManager.getCollateralPositionBalance(accountId, collateralPositionIndex);

        SyntheticPosition[] memory assets;
        if (syntheticAssetId != NO_SYNTHETIC_DELTA_ASSET_ID) {
            uint128 key = _encodeKey(accountId, syntheticAssetId);
            SyntheticPosition memory pos = syntheticPositions[key];
            if (pos.packed.getAssetId() != 0) {
                assets = new SyntheticPosition[](1);
                assets[0] = pos;
            } else {
                assets = new SyntheticPosition[](0);
            }
        } else {
            assets = new SyntheticPosition[](0);
        }

        return AccountPosition(accountId, collateralPositionIndex, collateralAmount, assets);
    }

    /**
     * @dev Load full account position across all collateral buckets (read-only view)
     */
    function _loadAccountPosition(uint64 accountId) internal view returns (AccountPosition memory) {
        if (accountManager.isAccountIdRegistered(accountId) == false) {
            revert("PM: acct not reg");
        }

        uint64[] memory indices = accountManager.getCollateralPositionIndices(accountId);
        int256 totalCollateral = 0;
        uint256 totalAssetCount = 0;

        // First pass: count total assets and sum collateral
        for (uint256 i = 0; i < indices.length;) {
            totalCollateral += accountManager.getCollateralPositionBalance(accountId, indices[i]);
            uint64[] memory assetIds = accountManager.getAssetIdListByCollateralPosition(accountId, indices[i]);
            totalAssetCount += assetIds.length;
            unchecked {
                ++i;
            }
        }

        // Second pass: load all assets
        SyntheticPosition[] memory assets = new SyntheticPosition[](totalAssetCount);
        uint256 assetIdx = 0;
        for (uint256 i = 0; i < indices.length;) {
            uint64[] memory assetIds = accountManager.getAssetIdListByCollateralPosition(accountId, indices[i]);
            for (uint256 j = 0; j < assetIds.length;) {
                assets[assetIdx] = syntheticPositions[_encodeKey(accountId, assetIds[j])];
                if (assets[assetIdx].packed.getAssetId() == 0) {
                    revert("PM: asset id 0");
                }
                assetIdx++;
                unchecked {
                    ++j;
                }
            }
            unchecked {
                ++i;
            }
        }

        return AccountPosition(accountId, DEFAULT_COLLATERAL_POSITION_INDEX, totalCollateral, assets);
    }

    // ============ Position Storage ============

    function _storeAccountPosition(AccountPosition memory position) internal {
        accountManager.updateCollateralPositionBalance(
            position.accountId, position.collateralPositionIndex, position.collateralAmount
        );
        uint256 assetsLen = position.assets.length;
        for (uint256 i = 0; i < assetsLen;) {
            SyntheticPosition memory asset = position.assets[i];
            uint256 packed = asset.packed;
            uint64 assetId = packed.getAssetId();
            uint64 cpIndex = packed.getCollateralPositionIndex();

            if (asset.amount == 0) {
                accountManager.removeAsset(position.accountId, assetId, cpIndex);
                delete syntheticPositions[_encodeKey(position.accountId, assetId)];
            } else {
                accountManager.addAsset(position.accountId, assetId, cpIndex);
                syntheticPositions[_encodeKey(position.accountId, assetId)] = asset;
            }
            unchecked {
                ++i;
            }
        }
        emit AccountPositionUpdated(position.accountId, position);
    }

    // ============ Position Updates ============

    function updatePositionInDict(
        uint64 accountId,
        int256 collateralDelta,
        uint64 syntheticAssetId,
        int256 syntheticDelta
    ) external onlyAuthorizedCaller {
        require(accountId != 0, "PM: accountId 0");

        uint64 index = DEFAULT_COLLATERAL_POSITION_INDEX;
        if (syntheticAssetId != NO_SYNTHETIC_DELTA_ASSET_ID) {
            index = _assetCollateralPositionIndex[_encodeKey(accountId, syntheticAssetId)];
        }

        AccountPosition memory acc = _loadPositionForAsset(accountId, index, syntheticAssetId);
        updatePosition(acc, accountId, collateralDelta, syntheticAssetId, syntheticDelta);
    }

    /// @dev `position` is expected to already have funding applied by the caller
    /// (see FundingApplyLib). PositionManager itself is funding-agnostic.
    function updatePosition(
        AccountPosition memory position,
        uint64 accountId,
        int256 collateralDelta,
        uint64 syntheticAssetId,
        int256 syntheticDelta
    ) public onlyAuthorizedCaller {
        if (position.accountId != accountId) {
            revert("PM: bad account");
        }

        AccountPosition memory initialPosition = position;
        AccountPosition memory updatedPosition = AccountPosition(
            initialPosition.accountId,
            initialPosition.collateralPositionIndex,
            initialPosition.collateralAmount,
            new SyntheticPosition[](initialPosition.assets.length)
        );

        // Deep-copy the assets so mutations to updatedPosition below don't alias
        // into initialPosition (which is reused as the margin-check "before" state).
        SyntheticPosition[] memory initialAssets = initialPosition.assets;
        for (uint256 i = 0; i < initialPosition.assets.length;) {
            SyntheticPosition memory asset = initialAssets[i];
            updatedPosition.assets[i] = SyntheticPosition(asset.packed, asset.amount);
            unchecked {
                ++i;
            }
        }

        // Ensure the synthetic asset record exists before routing collateral
        if (syntheticAssetId != NO_SYNTHETIC_DELTA_ASSET_ID) {
            _positionAddSyntheticAsset(updatedPosition, syntheticAssetId, syntheticDelta);
        }
        updatedPosition.collateralAmount += collateralDelta;

        _marginCheck()
            .checkValidTransition(initialPosition, updatedPosition, accountId, position.collateralPositionIndex);
        _storeAccountPosition(updatedPosition);
    }

    function _positionAddSyntheticAsset(AccountPosition memory position, uint64 syntheticAssetId, int256 syntheticDelta)
        internal
    {
        uint256 len = position.assets.length;
        for (uint256 i = 0; i < len;) {
            uint64 assetId = position.assets[i].packed.getAssetId();
            if (assetId == syntheticAssetId) {
                position.assets[i].amount += syntheticDelta;
                return;
            }
            unchecked {
                ++i;
            }
        }

        uint64 cpIndex = _assetCollateralPositionIndex[_encodeKey(position.accountId, syntheticAssetId)];
        uint64 accountKey = _toUint64Account(position.accountId);

        SyntheticPosition memory asset =
            SyntheticPositionLib.create(accountKey, syntheticAssetId, cpIndex, syntheticDelta);
        uint256 newLen = position.assets.length;
        SyntheticPosition[] memory assets = new SyntheticPosition[](newLen + 1);
        for (uint256 i = 0; i < newLen;) {
            assets[i] = position.assets[i];
            unchecked {
                ++i;
            }
        }

        assets[newLen] = asset;
        position.assets = assets;
    }

    // ============ View Functions ============

    function getCollateralBalanceByAccountId(uint64 accountId) external view returns (int256) {
        return accountManager.getCollateralPositionBalance(accountId, DEFAULT_COLLATERAL_POSITION_INDEX);
    }

    function getSyntheticBalance(uint64 accountId, uint64 syntheticAssetId) external view returns (int256) {
        SyntheticPosition storage position = syntheticPositions[_encodeKey(accountId, syntheticAssetId)];
        if (position.packed.getAssetId() == 0) {
            return 0;
        }
        return position.amount;
    }

    function getAccountPositionByUID(uint64 accountId) external view returns (AccountPosition memory) {
        return _loadAccountPosition(accountId);
    }

    function getAccountPositionByCollateralIndex(uint64 accountId, uint64 collateralPositionIndex)
        external
        view
        returns (AccountPosition memory)
    {
        return _loadPositionByCollateralIndex(accountId, collateralPositionIndex);
    }

    function getPositionForAsset(uint64 accountId, uint64 collateralPositionIndex, uint64 syntheticAssetId)
        external
        view
        returns (AccountPosition memory)
    {
        return _loadPositionForAsset(accountId, collateralPositionIndex, syntheticAssetId);
    }

    function incrementCollateralOnlyForFeeAccount(int256 collateralDelta) external onlyAuthorizedCaller {
        uint64 accountId = generalConfig.getFeeAccountId();

        require(accountId != 0, "PM: accountId 0");
        if (collateralDelta == 0) {
            return;
        }
        require(accountManager.isAccountIdRegistered(accountId), "PM: acct not reg");
        int256 current = accountManager.getCollateralPositionBalance(accountId, DEFAULT_COLLATERAL_POSITION_INDEX);
        int256 updated = current + collateralDelta;
        accountManager.updateCollateralPositionBalance(accountId, DEFAULT_COLLATERAL_POSITION_INDEX, updated);

        AccountPosition memory position = AccountPosition({
            accountId: accountId,
            collateralPositionIndex: DEFAULT_COLLATERAL_POSITION_INDEX,
            collateralAmount: updated,
            assets: new SyntheticPosition[](0)
        });
        emit AccountPositionUpdated(position.accountId, position);
    }

    // ============ Collateral Position Management ============

    function setCollateralPositionIndex(uint64 accountId, uint64 assetId, uint64 collateralPositionIndex)
        external
        ownerOrAuthorizedCaller
    {
        require(accountId != 0, "PM: accountId 0");
        require(assetId != 0 && assetId != NO_SYNTHETIC_DELTA_ASSET_ID, "PM: assetId invalid");
        // Disallow changing preference if a position with non-zero amount exists
        require(syntheticPositions[_encodeKey(accountId, assetId)].amount == 0, "PM: pos exists");
        _assetCollateralPositionIndex[_encodeKey(accountId, assetId)] = collateralPositionIndex;
        emit CollateralPositionIndexSet(accountId, assetId, collateralPositionIndex);
    }

    function getCollateralPositionIndex(uint64 accountId, uint64 assetId) external view returns (uint64) {
        require(assetId != 0 && assetId != NO_SYNTHETIC_DELTA_ASSET_ID, "PM: assetId invalid");
        return _assetCollateralPositionIndex[_encodeKey(accountId, assetId)];
    }

    function transferCollateral(uint64 accountId, uint64 fromIndex, uint64 toIndex, int256 amount)
        external
        ownerOrAuthorizedCaller
    {
        require(amount > 0, "PM: amt<=0");
        require(accountId != 0, "PM: accountId 0");
        require(fromIndex != toIndex, "PM: same index");

        // Load source bucket (collateral only), debit collateral
        AccountPosition memory fromPos = _loadPositionForAsset(accountId, fromIndex, NO_SYNTHETIC_DELTA_ASSET_ID);
        updatePosition(fromPos, accountId, -amount, NO_SYNTHETIC_DELTA_ASSET_ID, 0);

        // Load destination bucket (collateral only), credit collateral
        AccountPosition memory toPos = _loadPositionForAsset(accountId, toIndex, NO_SYNTHETIC_DELTA_ASSET_ID);
        updatePosition(toPos, accountId, amount, NO_SYNTHETIC_DELTA_ASSET_ID, 0);

        emit CollateralTransferred(accountId, fromIndex, toIndex, amount);
    }

    function getMaxRemovableCollateral(uint64 accountId, uint64 collateralPositionIndex) public view returns (int256) {
        require(accountId != 0, "PM: accountId 0");

        AccountPosition memory pos = _loadPositionByCollateralIndex(accountId, collateralPositionIndex);
        (int256 totalValueRep, int256 totalRiskRep) = _marginCheck().getAccountPositionStatus(pos);

        if (totalValueRep * FXP_32_ONE <= totalRiskRep) {
            return 0;
        }
        int256 maxRemovable = (totalValueRep * FXP_32_ONE - totalRiskRep) / (FXP_32_ONE * FXP_32_ONE);

        if (maxRemovable < 0) {
            return 0;
        }
        return maxRemovable;
    }

    // ============ Admin Functions ============

    function setAccountManager(address _accountManager) external onlyOwner {
        accountManager = IAccountManager(_accountManager);
        emit AccountManagerSet(_accountManager);
    }

    // setRisk removed: PositionManager discovers IMarginCheck via the capability
    // registry (see _marginCheck()). Risk wiring lives at RiskPlugin; deployer
    // no longer needs to configure it on PositionManager.

    function setGeneralConfig(address _generalConfig) external onlyOwner {
        generalConfig = GeneralConfig(_generalConfig);
        emit GeneralConfigSet(_generalConfig);
    }

    modifier ownerOrAuthorizedCaller() {
        require(
            ICallerRegistry(transactionProcessor).isAuthorizedCaller(msg.sender) || msg.sender == owner(),
            "PM: not authorized"
        );
        _;
    }

    function getOrCreatePosition(uint64 account, uint64 assetId) public ownerOrAuthorizedCaller {
        require(account != 0, "PM: acct 0");
        require(assetId >= 0, "PM: assetId negative");
        if (syntheticPositions[_encodeKey(account, assetId)].packed.getAssetId() == 0) {
            addSyntheticPositionId(account, assetId);
        }
    }

    function addSyntheticPositionId(uint64 account, uint64 assetId) public ownerOrAuthorizedCaller {
        require(account != 0, "PM: accountId 0");
        require(assetId >= 0, "PM: assetId negative");
        uint64 collateralAssetId = generalConfig.getCollateralAssetInfo().assetId;
        if (assetId != collateralAssetId) {
            uint64 cpIndex = _assetCollateralPositionIndex[_encodeKey(account, assetId)];

            uint64 accountKey = _toUint64Account(account);

            SyntheticPosition memory asset = SyntheticPositionLib.create(accountKey, assetId, cpIndex, 0);

            syntheticPositions[_encodeKey(account, assetId)] = asset;
            accountManager.addAsset(account, assetId, cpIndex);
        }
    }

    function setTransactionProcessor(address _transactionProcessor) external onlyOwner {
        transactionProcessor = _transactionProcessor;
    }
}
