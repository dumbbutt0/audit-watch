// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Initializable} from "openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol";
import {UUPSUpgradeable} from "openzeppelin-contracts-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
import {EIP712Upgradeable} from "openzeppelin-contracts-upgradeable/contracts/utils/cryptography/EIP712Upgradeable.sol";
import {ERC20Upgradeable} from "openzeppelin-contracts-upgradeable/contracts/token/ERC20/ERC20Upgradeable.sol";
import {ECDSA} from "openzeppelin-contracts/contracts/utils/cryptography/ECDSA.sol";
import {MerkleProof} from "openzeppelin-contracts/contracts/utils/cryptography/MerkleProof.sol";
import {PausableUpgradeable} from "openzeppelin-contracts-upgradeable/contracts/utils/PausableUpgradeable.sol";
import {IERC20} from "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import {IERC20Metadata} from "openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import {SafeERC20} from "openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol";

import {ICarthaVault} from "./interfaces/ICarthaVault.sol";
import {ICarthaVaultEvents} from "./interfaces/ICarthaVaultEvents.sol";
import {ICarthaAccessControl} from "./interfaces/ICarthaAccessControl.sol";
import {Roles} from "./diamond/Roles.sol";
import {PoolDeployLib} from "./libraries/PoolDeployLib.sol";

/**
 * @title CarthaVault
 * @notice Liquidity vault for Cartha subnet (SN35) with time-locked deposits
 * @dev UUPS upgradeable, ERC20 shares with transfer locks, uses external AccessControl diamond
 */
contract CarthaVault is
    ICarthaVault,
    Initializable,
    UUPSUpgradeable,
    EIP712Upgradeable,
    ERC20Upgradeable,
    PausableUpgradeable
{
    using SafeERC20 for IERC20;

    /*//////////////////////////////////////////////////////////////
                            CONSTANTS
    //////////////////////////////////////////////////////////////*/

    bytes32 public constant LOCK_REQUEST_TYPEHASH = keccak256(
        "LockRequest(address owner,bytes32 poolId,uint256 amount,uint64 lockDays,bytes32 hotkey,uint256 timestamp,uint256 nonce)"
    );

    uint256 public constant SIGNATURE_VALIDITY_PERIOD = 5 minutes;
    uint256 public constant EPOCH_DURATION = 7 days;
    uint64 public constant MAX_LOCK_DAYS_LIMIT = 1825;
    uint256 public constant MAX_PENALTY_BPS = 2000;
    uint256 public constant DEFAULT_MINIMUM_LOCK_AMOUNT = 100_000e6; // 100k USDC (6 decimals)
    uint256 public constant MAX_DEPLOY_RATIO_BPS = 10000;

    /*//////////////////////////////////////////////////////////////
                            STORAGE
    //////////////////////////////////////////////////////////////*/

    /// @custom:storage-location erc7201:cartha.storage.CarthaVault
    struct CarthaVaultStorage {
        address accessControl;
        address asset;
        bytes32 poolId;
        mapping(bytes32 => Position) positions;
        mapping(address => uint256) depositNonces;
        uint64 maxLockDays;
        uint256 cooldownDuration;
        uint256 performancePenalty;
        bytes32 underperformerRoot;
        bytes32 activeMinersRoot;
        bytes32 evictionRoot;
        uint256 totalPositions;
        uint256 minimumLockAmount;
        uint256 totalLockedAmount;
        IERC20 poolToken;
        address marketToken;
        address exchangeRouter;
        uint256 deployedGmBalance;
        mapping(bytes32 => bool) pendingWithdrawal;
        address reader;
        address dataStore;
        address oracle;
        mapping(address => bool) autoLockEnabled;
        uint256 maxDeployRatioBps;
        address depositVault;
        address withdrawalVault;
    }

    // keccak256(abi.encode(uint256(keccak256("cartha.storage.CarthaVault")) - 1)) & ~bytes32(uint256(0xff))
    bytes32 private constant CARTHA_VAULT_STORAGE_LOCATION =
        0xe912e8bf36bf83660d227f6af14ede2c91a4dbb2e01a1a24b1d461b36bc30a00;

    function _getCarthaVaultStorage() private pure returns (CarthaVaultStorage storage $) {
        assembly {
            $.slot := CARTHA_VAULT_STORAGE_LOCATION
        }
    }

    /*//////////////////////////////////////////////////////////////
                            CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /*//////////////////////////////////////////////////////////////
                            INITIALIZER
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Initialize the vault
     * @param accessControl_ External access control diamond
     * @param asset_ Asset token address (USDC, etc.)
     * @param poolId_ Pool identifier
     * @param name_ ERC20 token name
     * @param symbol_ ERC20 token symbol
     */
    function initialize(
        address accessControl_,
        address asset_,
        bytes32 poolId_,
        string memory name_,
        string memory symbol_
    ) external initializer {
        if (accessControl_ == address(0)) revert InvalidAccessControl();
        if (asset_ == address(0)) revert InvalidAsset();
        if (poolId_ == bytes32(0)) revert InvalidPoolId();

        __EIP712_init("CarthaVault", "1");
        __ERC20_init(name_, symbol_);
        __Pausable_init();

        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.accessControl = accessControl_;
        $.asset = asset_;
        $.poolId = poolId_;

        $.maxLockDays = 365;
        $.cooldownDuration = 7 days;
        $.performancePenalty = 500;
        $.minimumLockAmount = DEFAULT_MINIMUM_LOCK_AMOUNT;
    }

    /*//////////////////////////////////////////////////////////////
                            MODIFIERS
    //////////////////////////////////////////////////////////////*/

    modifier onlyRole(uint8 role) {
        _checkRole(role);
        _;
    }

    function _checkRole(uint8 role) internal view {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        if (!ICarthaAccessControl($.accessControl).hasRole(role, msg.sender)) {
            revert Unauthorized();
        }
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyRole(Roles.ADMIN) {}

    /*//////////////////////////////////////////////////////////////
                            USER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaVault
     */
    function lock(
        bytes32 poolId_,
        uint256 amount,
        uint64 lockDays,
        bytes32 hotkey,
        uint256 timestamp,
        bytes calldata signature
    ) external whenNotPaused {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        _validateLockInputs($, poolId_, amount, lockDays);

        if (block.timestamp > timestamp + SIGNATURE_VALIDITY_PERIOD) {
            revert SignatureExpired();
        }

        _verifyLockSignature(
            LockRequest({
                owner: msg.sender,
                poolId: poolId_,
                amount: amount,
                lockDays: lockDays,
                hotkey: hotkey,
                timestamp: timestamp,
                nonce: $.depositNonces[msg.sender]
            }),
            signature
        );

        $.depositNonces[msg.sender]++;

        _createPosition($, poolId_, amount, lockDays);
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function depositAndLock(bytes32 poolId_, uint256 amount, uint64 lockDays) external whenNotPaused {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        _validateLockInputs($, poolId_, amount, lockDays);

        _createPosition($, poolId_, amount, lockDays);
    }

    function _validateLockInputs(CarthaVaultStorage storage $, bytes32 poolId_, uint256 amount, uint64 lockDays)
        internal
        view
    {
        if (poolId_ != $.poolId) revert InvalidPoolId();
        if (amount == 0 || amount < $.minimumLockAmount) revert InvalidAmount();
        if (lockDays == 0 || lockDays > $.maxLockDays) revert InvalidLockDays();
        bytes32 lockId = lockIdOf(msg.sender, poolId_);
        if ($.positions[lockId].exists) revert PositionAlreadyExists();
    }

    function _createPosition(CarthaVaultStorage storage $, bytes32 poolId_, uint256 amount, uint64 lockDays) internal {
        uint256 shares = _convertToShares(amount);
        IERC20($.asset).safeTransferFrom(msg.sender, address(this), amount);
        _mint(msg.sender, shares);

        uint64 currentTime = uint64(block.timestamp);
        bytes32 lockId = lockIdOf(msg.sender, poolId_);

        $.positions[lockId] = Position({
            amount: amount,
            shares: shares,
            lockDays: lockDays,
            start: currentTime,
            maxLockDays: lockDays,
            lastEpoch: uint64(block.timestamp / EPOCH_DURATION),
            cooldownEnds: currentTime + uint64($.cooldownDuration),
            exists: true
        });

        $.totalPositions++;
        $.totalLockedAmount += amount;

        emit LockCreated(lockId, msg.sender, poolId_, address(this), amount, currentTime, lockDays);
    }

    /**
     * @inheritdoc ICarthaVault
     * @dev No Merkle proof needed - position.exists ensures valid miner
     *      Underperformers will be force-exited (position deleted) before they can top up
     */
    function lockTopUp(bytes32 poolId_, uint256 amount) external whenNotPaused {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        if (poolId_ != $.poolId) revert InvalidPoolId();
        if (amount == 0) revert InvalidAmount();

        bytes32 lockId = lockIdOf(msg.sender, poolId_);
        Position storage position = $.positions[lockId];
        if (!position.exists) revert PositionNotFound();

        uint256 shares = _convertToShares(amount);

        IERC20($.asset).safeTransferFrom(msg.sender, address(this), amount);
        _mint(msg.sender, shares);

        position.amount += amount;
        position.shares += shares;
        $.totalLockedAmount += amount;
        position.cooldownEnds = uint64(block.timestamp + $.cooldownDuration);

        // forge-lint: disable-next-line(unsafe-typecast)
        emit LockUpdated(lockId, int256(amount), position.lockDays);
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function release(bytes32 poolId_, uint256 amount) external whenNotPaused {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        if (poolId_ != $.poolId) revert InvalidPoolId();

        bytes32 lockId = lockIdOf(msg.sender, poolId_);
        Position storage position = $.positions[lockId];
        if (!position.exists) revert PositionNotFound();

        if (block.timestamp < position.start + uint256(position.lockDays) * 1 days) {
            revert PositionLocked();
        }

        if (block.timestamp < position.cooldownEnds) revert CooldownNotExpired();

        if (amount == 0 || amount > position.amount) revert InvalidAmount();

        bool isFullRelease = (amount == position.amount);

        // Share-based payout using stored shares — reflects pool PnL
        uint256 shares;
        uint256 payout;

        uint256 userBalance = balanceOf(msg.sender);
        if (isFullRelease) {
            shares = position.shares;
        } else {
            shares = (position.shares * amount) / position.amount;
        }
        if (shares > userBalance) shares = userBalance;
        if (shares == userBalance) isFullRelease = true;
        payout = _convertToAssets(shares);

        uint256 vaultBalance = IERC20($.asset).balanceOf(address(this));
        if (payout == 0 || payout > vaultBalance) revert InsufficientVaultBalance();

        uint256 releasedAmount = isFullRelease ? position.amount : amount;

        if (isFullRelease) {
            delete $.positions[lockId];
            $.pendingWithdrawal[lockId] = false;
            $.totalPositions--;
        } else {
            position.shares -= shares;
            position.amount -= amount;
        }

        $.totalLockedAmount -= releasedAmount;
        _burn(msg.sender, shares);
        IERC20($.asset).safeTransfer(msg.sender, payout);

        if (isFullRelease) {
            emit LockReleased(lockId, msg.sender, payout);
        } else {
            // forge-lint: disable-next-line(unsafe-typecast)
            emit LockUpdated(lockId, -int256(amount), position.lockDays);
        }
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function extendLock(bytes32 poolId_, uint64 extensionDays) external whenNotPaused {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        if (poolId_ != $.poolId) revert InvalidPoolId();

        bytes32 lockId = lockIdOf(msg.sender, poolId_);
        Position storage position = $.positions[lockId];
        if (!position.exists) revert PositionNotFound();

        uint64 newLockDays = position.lockDays + extensionDays;

        if (newLockDays <= position.lockDays) revert InvalidLockDays();
        if (newLockDays > $.maxLockDays) revert InvalidLockDays();

        position.lockDays = newLockDays;
        if (newLockDays > position.maxLockDays) {
            position.maxLockDays = newLockDays;
        }

        emit LockUpdated(lockId, 0, newLockDays);
    }

    /*//////////////////////////////////////////////////////////////
                            ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaVault
     */
    function forceExit(address owner, bytes32 poolId_, bytes32[] calldata merkleProof)
        external
        onlyRole(Roles.EJECTOR)
    {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        if (poolId_ != $.poolId) revert InvalidPoolId();

        bytes32 leaf;
        assembly {
            mstore(0x00, owner)
            mstore(0x20, poolId_)
            leaf := keccak256(0x00, 0x40)
        }
        if (!MerkleProof.verify(merkleProof, $.evictionRoot, leaf)) {
            revert InvalidMerkleProof();
        }

        bytes32 lockId = lockIdOf(owner, poolId_);
        Position storage position = $.positions[lockId];
        if (!position.exists) revert PositionNotFound();

        uint256 lockedAmount = position.amount;

        // Use stored shares for payout — reflects pool PnL
        uint256 shares;
        uint256 payout;
        {
            uint256 actualShares = balanceOf(owner);
            shares = position.shares < actualShares ? position.shares : actualShares;
            payout = _convertToAssets(shares);
        }

        // forge-lint: disable-next-line(unsafe-typecast)
        uint64 currentEpoch = uint64(block.timestamp / EPOCH_DURATION);

        delete $.positions[lockId];
        $.pendingWithdrawal[lockId] = false;
        $.totalPositions--;
        $.totalLockedAmount -= lockedAmount;

        if (shares > 0) _burn(owner, shares);
        if (payout > 0) IERC20($.asset).safeTransfer(owner, payout);

        emit Evicted(lockId, owner, poolId_, payout, currentEpoch);
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function forceExitUnderperformer(address owner, bytes32 poolId_, bytes32[] calldata merkleProof)
        external
        onlyRole(Roles.EJECTOR)
    {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        if (poolId_ != $.poolId) revert InvalidPoolId();

        bytes32 leaf;
        assembly {
            mstore(0x00, owner)
            mstore(0x20, poolId_)
            leaf := keccak256(0x00, 0x40)
        }
        if (!MerkleProof.verify(merkleProof, $.underperformerRoot, leaf)) {
            revert InvalidMerkleProof();
        }

        bytes32 lockId = lockIdOf(owner, poolId_);
        Position storage position = $.positions[lockId];
        if (!position.exists) revert PositionNotFound();

        uint256 lockedAmount = position.amount;

        // Use stored shares for payout — reflects pool PnL
        uint256 shares;
        uint256 payout;
        {
            uint256 actualShares = balanceOf(owner);
            shares = position.shares < actualShares ? position.shares : actualShares;
            payout = _convertToAssets(shares);
        }

        // Apply penalty
        payout = payout - (payout * $.performancePenalty) / 10000;

        delete $.positions[lockId];
        $.pendingWithdrawal[lockId] = false;
        $.totalPositions--;
        $.totalLockedAmount -= lockedAmount;

        if (shares > 0) _burn(owner, shares);
        if (payout > 0) IERC20($.asset).safeTransfer(owner, payout);

        // forge-lint: disable-next-line(unsafe-typecast)
        emit Evicted(lockId, owner, poolId_, payout, uint64(block.timestamp / EPOCH_DURATION));
    }

    /*//////////////////////////////////////////////////////////////
                        POOL DEPLOYMENT FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaVault
     */
    function deployToPool(uint256 amount, uint256 minMarketTokens)
        external
        payable
        onlyRole(Roles.KEEPER_BOT)
        whenNotPaused
        returns (bytes32 depositKey)
    {
        if (amount == 0) revert InvalidAmount();

        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        if ($.exchangeRouter == address(0) || $.marketToken == address(0)) revert PoolNotConfigured();

        uint256 vaultBalance = IERC20($.asset).balanceOf(address(this));
        if (amount > vaultBalance) revert InsufficientVaultBalance();

        if ($.maxDeployRatioBps > 0) {
            uint256 totalPoolValue = _totalValueLocked();
            if (totalPoolValue > 0) {
                uint256 currentGmValue = _gmValueInUsdc($);
                uint256 deployedAfter = currentGmValue + amount;
                if ((deployedAfter * MAX_DEPLOY_RATIO_BPS) / totalPoolValue > $.maxDeployRatioBps) {
                    revert ExceedsMaxDeployRatio();
                }
            }
        }

        if ($.depositVault == address(0)) revert PoolNotConfigured();
        depositKey = PoolDeployLib.deploy(
            $.asset, $.exchangeRouter, $.marketToken, $.depositVault, amount, minMarketTokens, msg.value
        );

        emit DeployedToPool(depositKey, amount);
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function recallFromPool(uint256 gmAmount, uint256 minShortTokenAmount)
        external
        payable
        onlyRole(Roles.KEEPER_BOT)
        whenNotPaused
        returns (bytes32 withdrawalKey)
    {
        if (gmAmount == 0) revert InvalidAmount();

        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        if ($.exchangeRouter == address(0) || $.marketToken == address(0)) revert PoolNotConfigured();

        if ($.withdrawalVault == address(0)) revert PoolNotConfigured();
        withdrawalKey = PoolDeployLib.recall(
            $.exchangeRouter, $.marketToken, $.withdrawalVault, gmAmount, minShortTokenAmount, msg.value
        );

        emit RecalledFromPool(withdrawalKey, gmAmount);
    }

    /*//////////////////////////////////////////////////////////////
                        WITHDRAWAL QUEUE FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaVault
     */
    function requestRelease(bytes32 poolId_) external whenNotPaused {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        if (poolId_ != $.poolId) revert InvalidPoolId();

        bytes32 lockId = lockIdOf(msg.sender, poolId_);
        Position storage position = $.positions[lockId];
        if (!position.exists) revert PositionNotFound();

        if (block.timestamp < position.start + uint256(position.lockDays) * 1 days) {
            revert PositionLocked();
        }

        if (block.timestamp < position.cooldownEnds) revert CooldownNotExpired();
        if ($.pendingWithdrawal[lockId]) revert PendingWithdrawalExists();

        $.pendingWithdrawal[lockId] = true;

        uint256 shares = balanceOf(msg.sender);
        emit WithdrawalQueued(lockId, msg.sender, shares);
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function processQueuedWithdrawals(address[] calldata owners) external onlyRole(Roles.KEEPER_BOT) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        for (uint256 i = 0; i < owners.length; i++) {
            bytes32 lockId = lockIdOf(owners[i], $.poolId);
            if (!$.pendingWithdrawal[lockId]) continue;

            Position storage position = $.positions[lockId];
            if (!position.exists) continue;
            if (block.timestamp < position.start + uint256(position.lockDays) * 1 days) continue;
            if (block.timestamp < position.cooldownEnds) continue;

            // Use stored shares for payout — reflects pool PnL
            uint256 shares = position.shares;
            uint256 actualShares = balanceOf(owners[i]);
            if (shares > actualShares) shares = actualShares;

            uint256 payout = _convertToAssets(shares);

            uint256 vaultBalance = IERC20($.asset).balanceOf(address(this));
            if (payout == 0 || payout > vaultBalance) continue;

            uint256 totalAmount = position.amount;
            delete $.positions[lockId];
            $.totalPositions--;
            $.totalLockedAmount -= totalAmount;
            $.pendingWithdrawal[lockId] = false;

            if (shares > 0) _burn(owners[i], shares);
            if (payout > 0) IERC20($.asset).safeTransfer(owners[i], payout);

            emit WithdrawalProcessed(lockId, owners[i], payout);
        }
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function emergencyPause() external onlyRole(Roles.ADMIN) {
        _pause();
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function unpause() external onlyRole(Roles.ADMIN) {
        _unpause();
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function rescueFunds(address token, address recipient, uint256 amount) external onlyRole(Roles.RESCUER) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        if (token == $.asset) revert CannotRescueVaultAsset();
        if (recipient == address(0)) revert InvalidRecipient();
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransfer(recipient, amount);

        emit FundsRescued(token, recipient, amount);
    }

    /*//////////////////////////////////////////////////////////////
                        CONFIGURATION FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaVault
     */
    function setMaxLockDays(uint64 newMax) external onlyRole(Roles.ADMIN) {
        if (newMax == 0 || newMax > MAX_LOCK_DAYS_LIMIT) revert InvalidLockDays();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.maxLockDays = newMax;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function setCooldownDuration(uint256 newDuration) external onlyRole(Roles.ADMIN) {
        if (newDuration > 30 days) revert InvalidCooldown();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.cooldownDuration = newDuration;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function setPerformancePenalty(uint256 newPenalty) external onlyRole(Roles.ADMIN) {
        if (newPenalty > MAX_PENALTY_BPS) revert InvalidPenalty();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.performancePenalty = newPenalty;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function setMinimumLockAmount(uint256 newMinimum) external onlyRole(Roles.ADMIN) {
        if (newMinimum == 0) revert InvalidAmount();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.minimumLockAmount = newMinimum;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function setUnderperformerRoot(bytes32 newRoot) external onlyRole(Roles.ADMIN) {
        if (newRoot == bytes32(0)) revert InvalidRoot();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.underperformerRoot = newRoot;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function setActiveMinersRoot(bytes32 newRoot) external onlyRole(Roles.ADMIN) {
        if (newRoot == bytes32(0)) revert InvalidRoot();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.activeMinersRoot = newRoot;
    }

    /**
     * @notice Set eviction root for force exits
     * @param newRoot New merkle root for eviction list
     */
    function setEvictionRoot(bytes32 newRoot) external onlyRole(Roles.ADMIN) {
        if (newRoot == bytes32(0)) revert InvalidRoot();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.evictionRoot = newRoot;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function migratePositionShares(address[] calldata owners) external onlyRole(Roles.ADMIN) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        for (uint256 i = 0; i < owners.length; i++) {
            bytes32 lockId = lockIdOf(owners[i], $.poolId);
            Position storage position = $.positions[lockId];
            if (!position.exists) continue;
            if (position.shares > 0) continue;
            position.shares = balanceOf(owners[i]);
        }
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function setPoolToken(address newPoolToken) external onlyRole(Roles.ADMIN) {
        if (newPoolToken == address(0)) revert ZeroAddress();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.poolToken = IERC20(newPoolToken);
        emit PoolTokenUpdated(newPoolToken);
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function setMarketToken(address newMarketToken) external onlyRole(Roles.ADMIN) {
        if (newMarketToken == address(0)) revert ZeroAddress();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.marketToken = newMarketToken;
        emit MarketTokenUpdated(newMarketToken);
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function setExchangeRouter(address newExchangeRouter) external onlyRole(Roles.ADMIN) {
        if (newExchangeRouter == address(0)) revert ZeroAddress();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.exchangeRouter = newExchangeRouter;
        emit ExchangeRouterUpdated(newExchangeRouter);
    }

    /**
     * @notice Set 0xM Reader contract address
     */
    function setReader(address newReader) external onlyRole(Roles.ADMIN) {
        if (newReader == address(0)) revert ZeroAddress();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.reader = newReader;
    }

    /**
     * @notice Set 0xM DataStore contract address
     */
    function setDataStore(address newDataStore) external onlyRole(Roles.ADMIN) {
        if (newDataStore == address(0)) revert ZeroAddress();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.dataStore = newDataStore;
    }

    /**
     * @notice Set 0xM Oracle contract address
     */
    function setOracle(address newOracle) external onlyRole(Roles.ADMIN) {
        if (newOracle == address(0)) revert ZeroAddress();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.oracle = newOracle;
    }

    function setDepositVault(address newDepositVault) external onlyRole(Roles.ADMIN) {
        if (newDepositVault == address(0)) revert ZeroAddress();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.depositVault = newDepositVault;
    }

    function setWithdrawalVault(address newWithdrawalVault) external onlyRole(Roles.ADMIN) {
        if (newWithdrawalVault == address(0)) revert ZeroAddress();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.withdrawalVault = newWithdrawalVault;
    }

    /**
     * @param newRatio Max deploy ratio in bps (5000 = 50%, 0 = no cap)
     */
    function setMaxDeployRatio(uint256 newRatio) external onlyRole(Roles.ADMIN) {
        if (newRatio > MAX_DEPLOY_RATIO_BPS) revert InvalidParameter();
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.maxDeployRatioBps = newRatio;
    }

    /**
     * @param enabled Enable/disable auto-lock on expiry
     */
    function setAutoLock(bool enabled) external {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        $.autoLockEnabled[msg.sender] = enabled;
        emit AutoLockToggled(msg.sender, enabled);
    }

    /**
     * @dev Skips users with pendingWithdrawal or still-locked positions
     */
    function processAutoLocks(address[] calldata owners) external onlyRole(Roles.KEEPER_BOT) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        for (uint256 i = 0; i < owners.length; i++) {
            if (!$.autoLockEnabled[owners[i]]) continue;

            bytes32 lockId = lockIdOf(owners[i], $.poolId);
            Position storage position = $.positions[lockId];
            if (!position.exists) continue;
            if ($.pendingWithdrawal[lockId]) continue;

            // Only re-lock if expired
            if (block.timestamp < position.start + uint256(position.lockDays) * 1 days) continue;

            position.start = uint64(block.timestamp);
            position.cooldownEnds = uint64(block.timestamp + $.cooldownDuration);
            // forge-lint: disable-next-line(unsafe-typecast)
            position.lastEpoch = uint64(block.timestamp / EPOCH_DURATION);

            emit AutoLockRenewed(lockId, owners[i], position.lockDays);
        }
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function depositFromParent(uint256 amount)
        external
        onlyRole(Roles.KEEPER_BOT)
        whenNotPaused
        returns (uint256 shares)
    {
        if (amount == 0) revert InvalidAmount();

        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        shares = _convertToShares(amount);

        IERC20($.asset).safeTransferFrom(msg.sender, address(this), amount);
        _mint(msg.sender, shares);

        return shares;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function withdrawToParent(uint256 amount) external onlyRole(Roles.KEEPER_BOT) returns (uint256 assets) {
        if (amount == 0) revert InvalidAmount();

        CarthaVaultStorage storage $ = _getCarthaVaultStorage();

        // Cap at available idle USDC — don't burn shares for GM-deployed funds
        uint256 vaultBalance = IERC20($.asset).balanceOf(address(this));
        assets = amount > vaultBalance ? vaultBalance : amount;
        if (assets == 0) return 0;

        uint256 totalShares = totalSupply();
        uint256 totalAssets_ = _totalValueLocked();

        uint256 shares;
        if (totalAssets_ == 0 || totalShares == 0) {
            shares = assets * 10 ** (decimals() - IERC20Metadata($.asset).decimals());
        } else {
            shares = (assets * totalShares + totalAssets_ - 1) / totalAssets_;
        }

        if (balanceOf(msg.sender) < shares) revert InsufficientShares();

        _burn(msg.sender, shares);
        IERC20($.asset).safeTransfer(msg.sender, assets);

        return assets;
    }

    /*//////////////////////////////////////////////////////////////
                        ERC20 OVERRIDE & HELPERS
    //////////////////////////////////////////////////////////////*/

    /**
     * @dev Override to use 18 decimals for shares regardless of asset decimals
     * @notice This provides better precision and follows ERC4626 best practices
     */
    function decimals() public pure override returns (uint8) {
        return 18;
    }

    /**
     * @notice Override ERC20 transfer to enforce position locks
     */
    function _update(address from, address to, uint256 value) internal override {
        // Allow mints (from == 0) and burns (to == 0) unconditionally
        if (from != address(0) && to != address(0)) {
            CarthaVaultStorage storage $ = _getCarthaVaultStorage();
            bytes32 lockId = lockIdOf(from, $.poolId);
            Position storage position = $.positions[lockId];

            if (position.exists) {
                bool locked = block.timestamp < position.start + uint256(position.lockDays) * 1 days;
                if (locked) {
                    revert PositionLocked();
                }
            }
        }

        super._update(from, to, value);
    }

    /**
     * @notice Convert assets to shares
     * @dev Uses vault TVL and total shares for conversion with decimal offset
     */
    function _convertToShares(uint256 assets) internal view returns (uint256 shares) {
        uint256 totalShares = totalSupply();
        uint256 totalAssets_ = _totalValueLocked();

        if (totalShares == 0 || totalAssets_ == 0) {
            CarthaVaultStorage storage $ = _getCarthaVaultStorage();
            return assets * 10 ** (decimals() - IERC20Metadata($.asset).decimals());
        }

        return (assets * totalShares) / totalAssets_;
    }

    /**
     * @notice Convert shares to assets
     * @dev Uses vault TVL and total shares for conversion
     */
    function _convertToAssets(uint256 shares) internal view returns (uint256 assets) {
        uint256 totalShares = totalSupply();
        if (totalShares == 0) return 0;

        return (shares * _totalValueLocked()) / totalShares;
    }

    /**
     * @dev TVL = USDC balance + GM token value (priced via 0xM Reader)
     */
    function _totalValueLocked() internal view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return IERC20($.asset).balanceOf(address(this)) + _gmValueInUsdc($);
    }

    function _gmValueInUsdc(CarthaVaultStorage storage $) internal view returns (uint256) {
        return PoolDeployLib.gmValueInUsdc(address($.poolToken), $.reader, $.dataStore, $.marketToken, $.oracle);
    }

    /*//////////////////////////////////////////////////////////////
                            VIEW FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaVault
     * @dev One position per wallet per pool. For multiple miners, use different wallets.
     */
    function lockIdOf(address owner, bytes32 poolId_) public pure returns (bytes32) {
        bytes32 lockId;
        assembly {
            mstore(0x00, owner)
            mstore(0x20, poolId_)
            lockId := keccak256(0x00, 0x40)
        }
        return lockId;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function getPosition(address owner, bytes32 poolId_) external view returns (Position memory) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.positions[lockIdOf(owner, poolId_)];
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function isLocked(address owner, bytes32 poolId_) external view returns (bool) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        Position storage position = $.positions[lockIdOf(owner, poolId_)];
        if (!position.exists) return false;
        return block.timestamp < position.start + uint256(position.lockDays) * 1 days;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function getCooldownRemaining(address owner, bytes32 poolId_) external view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        Position storage position = $.positions[lockIdOf(owner, poolId_)];
        if (!position.exists) return 0;
        if (block.timestamp >= position.cooldownEnds) return 0;
        return position.cooldownEnds - block.timestamp;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function canWithdraw(address owner, bytes32 poolId_) external view returns (bool) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        Position storage position = $.positions[lockIdOf(owner, poolId_)];
        if (!position.exists) return false;

        bool lockExpired = block.timestamp >= position.start + uint256(position.lockDays) * 1 days;
        bool cooldownPassed = block.timestamp >= position.cooldownEnds;

        return lockExpired && cooldownPassed;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function asset() external view returns (address) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.asset;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function poolId() external view returns (bytes32) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.poolId;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function maxLockDays() external view returns (uint64) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.maxLockDays;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function cooldownDuration() external view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.cooldownDuration;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function epochDuration() external pure returns (uint256) {
        return EPOCH_DURATION;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function performancePenalty() external view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.performancePenalty;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function minimumLockAmount() external view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.minimumLockAmount;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function underperformerRoot() external view returns (bytes32) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.underperformerRoot;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function activeMinersRoot() external view returns (bytes32) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.activeMinersRoot;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function hasPendingWithdrawal(address owner, bytes32 poolId_) external view returns (bool) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.pendingWithdrawal[lockIdOf(owner, poolId_)];
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function poolToken() external view returns (address) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return address($.poolToken);
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function marketToken() external view returns (address) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.marketToken;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function exchangeRouter() external view returns (address) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.exchangeRouter;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function deployedGmBalance() external view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return _gmValueInUsdc($);
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function totalValueLocked() external view returns (uint256) {
        return _totalValueLocked();
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function totalPositions() external view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.totalPositions;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function depositNonces(address owner) external view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.depositNonces[owner];
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function totalLockedAmount() external view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        return $.totalLockedAmount;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function getUtilization() external view returns (uint256) {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        uint256 tvl = _totalValueLocked();
        if (tvl == 0) return 0;
        return ($.totalLockedAmount * 10000) / tvl;
    }

    /**
     * @inheritdoc ICarthaVault
     */
    function positions(bytes32 lockId)
        external
        view
        returns (
            uint256 amount,
            uint64 lockDays,
            uint64 start,
            uint64 maxLockDays_,
            uint64 lastEpoch,
            uint64 cooldownEnds,
            bool exists
        )
    {
        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        Position storage pos = $.positions[lockId];
        return (pos.amount, pos.lockDays, pos.start, pos.maxLockDays, pos.lastEpoch, pos.cooldownEnds, pos.exists);
    }

    /// @inheritdoc ICarthaVault
    function DOMAIN_SEPARATOR() external view returns (bytes32) {
        return _domainSeparatorV4();
    }

    /// @inheritdoc ICarthaVault
    function paused() public view override(PausableUpgradeable, ICarthaVault) returns (bool) {
        return super.paused();
    }

    /*//////////////////////////////////////////////////////////////
                            INTERNAL FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Verify EIP-712 signature for lock request
     * @param request LockRequest struct
     * @param signature EIP-712 signature from verifier (EJECTOR role)
     */
    function _verifyLockSignature(LockRequest memory request, bytes calldata signature) internal view {
        bytes32 structHash;
        bytes32 typehash = LOCK_REQUEST_TYPEHASH;
        assembly {
            let ptr := mload(0x40)
            mstore(ptr, typehash)
            mstore(add(ptr, 0x20), mload(request)) // owner
            mstore(add(ptr, 0x40), mload(add(request, 0x20))) // poolId
            mstore(add(ptr, 0x60), mload(add(request, 0x40))) // amount
            mstore(add(ptr, 0x80), mload(add(request, 0x60))) // lockDays
            mstore(add(ptr, 0xa0), mload(add(request, 0x80))) // hotkey
            mstore(add(ptr, 0xc0), mload(add(request, 0xa0))) // timestamp
            mstore(add(ptr, 0xe0), mload(add(request, 0xc0))) // nonce
            structHash := keccak256(ptr, 0x100)
        }

        CarthaVaultStorage storage $ = _getCarthaVaultStorage();
        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = ECDSA.recover(digest, signature);

        if (!ICarthaAccessControl($.accessControl).hasRole(Roles.EJECTOR, signer)) {
            revert Unauthorized();
        }
    }
}
