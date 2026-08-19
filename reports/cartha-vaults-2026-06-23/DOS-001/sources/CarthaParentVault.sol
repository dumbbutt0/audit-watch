// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Initializable} from "openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol";
import {UUPSUpgradeable} from "openzeppelin-contracts-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
import {PausableUpgradeable} from "openzeppelin-contracts-upgradeable/contracts/utils/PausableUpgradeable.sol";
import {EIP712Upgradeable} from "openzeppelin-contracts-upgradeable/contracts/utils/cryptography/EIP712Upgradeable.sol";
import {ERC20Upgradeable} from "openzeppelin-contracts-upgradeable/contracts/token/ERC20/ERC20Upgradeable.sol";
import {IERC20} from "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol";
import {ECDSA} from "openzeppelin-contracts/contracts/utils/cryptography/ECDSA.sol";

import {ICarthaAccessControl} from "./interfaces/ICarthaAccessControl.sol";
import {ICarthaParentVault} from "./interfaces/ICarthaParentVault.sol";
import {ICarthaVault} from "./interfaces/ICarthaVault.sol";
import {Roles} from "./diamond/Roles.sol";

/**
 * @title CarthaParentVault
 * @notice Parent vault that spreads locked deposits across child CarthaVault pools by weight
 */
contract CarthaParentVault is
    Initializable,
    UUPSUpgradeable,
    PausableUpgradeable,
    EIP712Upgradeable,
    ERC20Upgradeable,
    ICarthaParentVault
{
    using SafeERC20 for IERC20;

    /// @custom:storage-location erc7201:cartha.storage.ParentVault
    struct ParentVaultStorage {
        bytes32 category;
        ICarthaAccessControl diamond;
        address[] vaultList;
        mapping(address => PoolConfig) pools;
        mapping(address => uint256) vaultIndex;
        mapping(address => Position) positions; // @dev DEPRECATED
        RebalanceConfig rebalanceConfig;
        uint256 lastRebalanceTime;
        mapping(address => LockPosition) lockPositions;
        mapping(address => uint256) lockNonces;
        mapping(address => bool) parentPendingWithdrawal;
        uint64 maxLockDays;
        uint256 cooldownDuration;
        uint256 minimumLockAmount;
    }

    // keccak256(abi.encode(uint256(keccak256("cartha.storage.ParentVault")) - 1)) & ~bytes32(uint256(0xff))
    bytes32 private constant PARENT_VAULT_STORAGE_LOCATION =
        0x132a1344191806d6acd57512ba0c4193d7f59e510e17f64a6c527c52607be700;

    function _getParentVaultStorage() private pure returns (ParentVaultStorage storage $) {
        assembly {
            $.slot := PARENT_VAULT_STORAGE_LOCATION
        }
    }

    uint256 private constant BASIS_POINTS = 10000;
    uint256 private constant SHARE_DECIMALS = 18;
    uint256 public constant SIGNATURE_VALIDITY_PERIOD = 5 minutes;
    uint256 public constant DEFAULT_MINIMUM_LOCK_AMOUNT = 100_000e6;

    bytes32 public constant PARENT_LOCK_REQUEST_TYPEHASH = keccak256(
        "ParentLockRequest(address owner,bytes32 category,uint256 amount,uint64 lockDays,bytes32 hotkey,uint256 timestamp,uint256 nonce)"
    );

    modifier onlyRole(uint8 role) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        if (!$.diamond.hasRole(role, msg.sender)) {
            revert Unauthorized();
        }
        _;
    }

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address asset_, bytes32 category_, string memory name_, string memory symbol_, address diamond_)
        external
        initializer
    {
        __ERC20_init(name_, symbol_);
        __EIP712_init("CarthaParentVault", "1");
        __Pausable_init();

        // Store asset in ERC4626's storage slot for upgrade compatibility
        bytes32 slot = 0x0773e532dfede91f04b12a73d3d2acd361424f41f76b4fb79f090161e36b4e00;
        assembly { sstore(slot, asset_) }

        ParentVaultStorage storage $ = _getParentVaultStorage();
        $.category = category_;
        $.diamond = ICarthaAccessControl(diamond_);

        $.rebalanceConfig =
            RebalanceConfig({minRebalanceInterval: 1 days, utilizationThreshold: 8000, maxShiftPerRebalance: 2000});

        $.maxLockDays = 365;
        $.cooldownDuration = 7 days;
        $.minimumLockAmount = DEFAULT_MINIMUM_LOCK_AMOUNT;
    }

    /// @notice V2 upgrade — sets up EIP-712 and lock defaults
    function reinitializeV2() external onlyRole(Roles.ADMIN) reinitializer(2) {
        __EIP712_init("CarthaParentVault", "1");

        ParentVaultStorage storage $ = _getParentVaultStorage();
        $.maxLockDays = 365;
        $.cooldownDuration = 7 days;
        $.minimumLockAmount = DEFAULT_MINIMUM_LOCK_AMOUNT;
    }

    /*//////////////////////////////////////////////////////////////
                        SHARE ACCOUNTING
    //////////////////////////////////////////////////////////////*/

    function decimals() public pure override returns (uint8) {
        return 18;
    }

    function asset() public view returns (address a) {
        bytes32 slot = 0x0773e532dfede91f04b12a73d3d2acd361424f41f76b4fb79f090161e36b4e00;
        assembly { a := sload(slot) }
    }

    /// @dev Convert USDC amount to shares. 1e12 offset (18 - 6 decimals) for first deposit.
    function _convertToShares(uint256 amount) internal view returns (uint256) {
        uint256 supply = totalSupply();
        uint256 total = totalAssets();
        if (supply == 0 || total == 0) return amount * 1e12;
        return (amount * supply) / total;
    }

    function _convertToSharesRoundUp(uint256 amount) internal view returns (uint256) {
        uint256 supply = totalSupply();
        uint256 total = totalAssets();
        if (supply == 0 || total == 0) return amount * 1e12;
        return (amount * supply + total - 1) / total;
    }

    /// @notice Legacy LP withdrawal — only for users without a lock position
    function withdraw(uint256 assets, address receiver, address owner) external whenNotPaused returns (uint256 shares) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        if ($.lockPositions[owner].exists) revert ERC4626WithdrawDisabled();

        shares = _convertToSharesRoundUp(assets);
        if (msg.sender != owner) _spendAllowance(owner, msg.sender, shares);

        uint256 idleUsdc = IERC20(asset()).balanceOf(address(this));
        uint256 needed = assets > idleUsdc ? assets - idleUsdc : 0;
        if (needed > 0) {
            if (_availableFromChildren() + 10 < needed) revert InsufficientVaultBalance();
            _withdrawFromChildren(needed);
        }

        uint256 balance = IERC20(asset()).balanceOf(address(this));
        uint256 payout = assets > balance ? balance : assets;
        if (payout == 0 && assets > 0) revert InsufficientVaultBalance();
        _burn(owner, shares);
        SafeERC20.safeTransfer(IERC20(asset()), receiver, payout);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function shiftLiquidity(address fromVault, address toVault, uint256 amount)
        external
        override
        onlyRole(Roles.KEEPER_BOT)
        whenNotPaused
    {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        if (!$.pools[fromVault].isActive || !$.pools[toVault].isActive) {
            revert PoolNotActive();
        }
        if (ICarthaVault(toVault).paused()) revert PoolNotActive();
        if (amount == 0) revert InvalidAmount();

        uint256 withdrawn = ICarthaVault(fromVault).withdrawToParent(amount);

        IERC20(asset()).forceApprove(toVault, withdrawn);
        ICarthaVault(toVault).depositFromParent(withdrawn);
        IERC20(asset()).forceApprove(toVault, 0);

        emit LiquidityShifted(fromVault, toVault, withdrawn);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function addPool(address vault, uint256 weight, uint256 maxAllocation) external override onlyRole(Roles.ADMIN) {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        if (vault == address(0)) revert InvalidVault();
        if ($.pools[vault].vault != address(0)) revert PoolAlreadyExists();
        if (maxAllocation > BASIS_POINTS) revert InvalidAllocation();

        $.vaultList.push(vault);
        $.vaultIndex[vault] = $.vaultList.length - 1;

        $.pools[vault] = PoolConfig({
            vault: vault, weight: weight, targetWeight: weight, maxAllocation: maxAllocation, isActive: true
        });

        emit PoolAdded(vault, weight, maxAllocation);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function removePool(address vault, bool shouldRebalance) external override onlyRole(Roles.ADMIN) {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        if ($.pools[vault].vault == address(0)) revert PoolNotFound();

        uint256 parentShares = IERC20(vault).balanceOf(address(this));
        uint256 totalShares = IERC20(vault).totalSupply();
        uint256 vaultTVL = ICarthaVault(vault).totalValueLocked();

        if (totalShares > 0 && parentShares > 0) {
            uint256 withdrawAmount = (parentShares * vaultTVL) / totalShares;
            if (withdrawAmount > 0) {
                ICarthaVault(vault).withdrawToParent(withdrawAmount);
            }
        }

        uint256 index = $.vaultIndex[vault];
        uint256 lastIndex = $.vaultList.length - 1;

        if (index != lastIndex) {
            address lastVault = $.vaultList[lastIndex];
            $.vaultList[index] = lastVault;
            $.vaultIndex[lastVault] = index;
        }

        $.vaultList.pop();
        delete $.vaultIndex[vault];
        delete $.pools[vault];

        emit PoolRemoved(vault);

        if (shouldRebalance) {
            _rebalanceToWeights();
        }
    }

    /// @notice Rebalance all pools to target weights
    function _rebalanceToWeights() internal returns (uint256 totalShifted) {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        uint256 totalAssets_ = totalAssets();
        if (totalAssets_ == 0) return 0;

        uint256 totalWeight;
        for (uint256 i = 0; i < $.vaultList.length; i++) {
            address vault = $.vaultList[i];
            if ($.pools[vault].isActive && !ICarthaVault(vault).paused()) {
                totalWeight += $.pools[vault].weight;
            }
        }

        if (totalWeight == 0) return 0;

        for (uint256 i = 0; i < $.vaultList.length; i++) {
            address vault = $.vaultList[i];
            if (!$.pools[vault].isActive || ICarthaVault(vault).paused()) continue;

            uint256 targetAllocation = (totalAssets_ * $.pools[vault].weight) / totalWeight;

            uint256 parentShares = IERC20(vault).balanceOf(address(this));
            uint256 childTotalSupply = IERC20(vault).totalSupply();
            uint256 childTVL = ICarthaVault(vault).totalValueLocked();
            uint256 currentAllocation =
                (childTotalSupply > 0 && parentShares > 0) ? (parentShares * childTVL) / childTotalSupply : 0;

            if (targetAllocation > currentAllocation) {
                uint256 depositAmount = targetAllocation - currentAllocation;
                uint256 available = IERC20(asset()).balanceOf(address(this));

                if (depositAmount > available) depositAmount = available;
                if (depositAmount > 0) {
                    IERC20(asset()).forceApprove(vault, depositAmount);
                    ICarthaVault(vault).depositFromParent(depositAmount);
                    IERC20(asset()).forceApprove(vault, 0);
                    totalShifted += depositAmount;
                }
            } else if (targetAllocation < currentAllocation) {
                uint256 withdrawAmount = currentAllocation - targetAllocation;
                if (withdrawAmount > 0) {
                    ICarthaVault(vault).withdrawToParent(withdrawAmount);
                    totalShifted += withdrawAmount;
                }
            }
        }
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function updatePoolWeight(address vault, uint256 newWeight) external override onlyRole(Roles.ADMIN) {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        if ($.pools[vault].vault == address(0)) revert PoolNotFound();

        uint256 oldWeight = $.pools[vault].weight;
        $.pools[vault].weight = newWeight;

        emit PoolWeightUpdated(vault, oldWeight, newWeight);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function setRebalanceConfig(RebalanceConfig calldata config) external override onlyRole(Roles.ADMIN) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        $.rebalanceConfig = config;
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function rebalance() external override onlyRole(Roles.KEEPER_BOT) returns (uint256 totalShifted) {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        if (block.timestamp < $.lastRebalanceTime + $.rebalanceConfig.minRebalanceInterval) {
            revert RebalanceTooSoon();
        }

        totalShifted = _rebalanceToWeights();

        $.lastRebalanceTime = block.timestamp;

        emit Rebalanced(block.timestamp, totalShifted);
    }

    function sharePrice() public view returns (uint256) {
        uint256 totalShares = totalSupply();
        if (totalShares == 0) return 1e6; // 1 USDC

        return (totalAssets() * 1e18) / totalShares;
    }

    /// @notice Sum of parent's share value across all children + idle USDC
    function totalAssets() public view returns (uint256 total) {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        for (uint256 i = 0; i < $.vaultList.length; i++) {
            address vault = $.vaultList[i];
            if ($.pools[vault].isActive) {
                uint256 parentShares = IERC20(vault).balanceOf(address(this));
                uint256 childTotalSupply = IERC20(vault).totalSupply();
                uint256 childTVL = ICarthaVault(vault).totalValueLocked();

                if (childTotalSupply > 0 && parentShares > 0) {
                    total += (parentShares * childTVL) / childTotalSupply;
                }
            }
        }

        total += IERC20(asset()).balanceOf(address(this));
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function getPools() external view override returns (PoolConfig[] memory configs) {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        uint256 poolCount = $.vaultList.length;
        configs = new PoolConfig[](poolCount);

        for (uint256 i = 0; i < poolCount; i++) {
            configs[i] = $.pools[$.vaultList[i]];
        }
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function getPoolUtilization(address vault) public view override returns (uint256 utilization) {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        if ($.pools[vault].vault == address(0)) revert PoolNotFound();

        return ICarthaVault(vault).getUtilization();
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    /**
     * @inheritdoc ICarthaParentVault
     */
    function category() external view override returns (bytes32) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        return $.category;
    }

    /// @notice Split USDC across children by weight
    function _distributeToChildren(uint256 amount) internal {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        uint256 totalWeight;
        for (uint256 i = 0; i < $.vaultList.length; i++) {
            address vault = $.vaultList[i];
            if ($.pools[vault].isActive && !ICarthaVault(vault).paused()) {
                totalWeight += $.pools[vault].weight;
            }
        }

        if (totalWeight == 0) revert NoActivePools();

        for (uint256 i = 0; i < $.vaultList.length; i++) {
            address vault = $.vaultList[i];
            if (!$.pools[vault].isActive || ICarthaVault(vault).paused()) continue;

            uint256 allocation = (amount * $.pools[vault].weight) / totalWeight;
            if (allocation > 0) {
                IERC20(asset()).forceApprove(vault, allocation);
                ICarthaVault(vault).depositFromParent(allocation);
                IERC20(asset()).forceApprove(vault, 0);
            }
        }
    }

    /// @notice Total idle USDC the parent can pull from children right now
    function _availableFromChildren() internal view returns (uint256 available) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        for (uint256 i = 0; i < $.vaultList.length; i++) {
            address vault = $.vaultList[i];
            if (!$.pools[vault].isActive) continue;
            uint256 parentShares = IERC20(vault).balanceOf(address(this));
            if (parentShares == 0) continue;
            uint256 childSupply = IERC20(vault).totalSupply();
            uint256 childIdle = IERC20(asset()).balanceOf(vault);
            available += (parentShares * childIdle) / childSupply;
        }
    }

    /// @dev Tear down a full exit: clear the position + pending flag, burn shares, send payout.
    function _settleFullExit(address owner, uint256 shares, uint256 payout) internal {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        delete $.lockPositions[owner];
        $.parentPendingWithdrawal[owner] = false;
        if (shares > 0) _burn(owner, shares);
        if (payout > 0) SafeERC20.safeTransfer(IERC20(asset()), owner, payout);
    }

    /// @dev Convert shares to USDC at current price, pulling from children if idle is short.
    ///      Returns sufficient=false (and zero payout) when even pulling everything still
    ///      can't cover the share value, so callers can choose between revert and continue.
    function _prepareSharePayout(uint256 shares) internal returns (uint256 payout, bool sufficient) {
        uint256 supply = totalSupply();
        uint256 shareValue = (supply > 0) ? (shares * totalAssets()) / supply : 0;

        uint256 idleUsdc = IERC20(asset()).balanceOf(address(this));
        uint256 needed = shareValue > idleUsdc ? shareValue - idleUsdc : 0;
        if (needed > 0) {
            if (_availableFromChildren() + 10 < needed) return (0, false);
            _withdrawFromChildren(needed);
        }

        uint256 balance = IERC20(asset()).balanceOf(address(this));
        payout = shareValue > balance ? balance : shareValue;
        sufficient = true;
    }

    /// @notice Pull USDC from children proportionally by their idle USDC
    function _withdrawFromChildren(uint256 amount) internal {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        uint256 totalIdle = _availableFromChildren();
        if (totalIdle == 0) return;

        uint256 remaining = amount;

        for (uint256 i = 0; i < $.vaultList.length && remaining > 0; i++) {
            address vault = $.vaultList[i];
            if (!$.pools[vault].isActive) continue;
            uint256 parentShares = IERC20(vault).balanceOf(address(this));
            if (parentShares == 0) continue;

            uint256 childSupply = IERC20(vault).totalSupply();
            uint256 childIdle = IERC20(asset()).balanceOf(vault);
            uint256 parentPortion = (parentShares * childIdle) / childSupply;
            if (parentPortion == 0) continue;

            // Pull proportionally to this child's share of total idle
            uint256 withdrawAmount = (amount * parentPortion) / totalIdle;
            if (withdrawAmount > remaining) withdrawAmount = remaining;
            if (withdrawAmount == 0) continue;

            uint256 withdrawn = ICarthaVault(vault).withdrawToParent(withdrawAmount);
            remaining -= withdrawn;
        }
    }

    /*//////////////////////////////////////////////////////////////
                        LOCK & SPREAD FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaParentVault
     */
    function lockAndSpread(uint256 amount, uint64 lockDays, bytes32 hotkey, uint256 timestamp, bytes calldata signature)
        external
        whenNotPaused
    {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        _validateLockInputs($, amount, lockDays);

        if (block.timestamp > timestamp + SIGNATURE_VALIDITY_PERIOD) {
            revert SignatureExpired();
        }

        _verifyParentLockSignature(
            ParentLockRequest({
                owner: msg.sender,
                category: $.category,
                amount: amount,
                lockDays: lockDays,
                hotkey: hotkey,
                timestamp: timestamp,
                nonce: $.lockNonces[msg.sender]
            }),
            signature
        );

        $.lockNonces[msg.sender]++;

        _executeLockAndSpread(amount, lockDays, hotkey);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function depositAndLockSpread(uint256 amount, uint64 lockDays) external whenNotPaused {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        _validateLockInputs($, amount, lockDays);

        _executeLockAndSpread(amount, lockDays, bytes32(0));
    }

    function _validateLockInputs(ParentVaultStorage storage $, uint256 amount, uint64 lockDays) internal view {
        if (amount == 0 || amount < $.minimumLockAmount) revert InvalidAmount();
        if (lockDays == 0 || lockDays > $.maxLockDays) revert InvalidLockDays();
        if ($.lockPositions[msg.sender].exists) revert LockPositionExists();
        if ($.parentPendingWithdrawal[msg.sender]) revert PendingWithdrawalExists();
    }

    function _pullMintAndDistribute(uint256 amount) internal returns (uint256 shares) {
        shares = _convertToShares(amount);
        SafeERC20.safeTransferFrom(IERC20(asset()), msg.sender, address(this), amount);
        _mint(msg.sender, shares);
        _distributeToChildren(amount);
    }

    function _executeLockAndSpread(uint256 amount, uint64 lockDays, bytes32 hotkey) internal {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        uint256 shares = _pullMintAndDistribute(amount);

        uint64 currentTime = uint64(block.timestamp);
        $.lockPositions[msg.sender] = LockPosition({
            lockedShares: shares,
            lockedAmount: amount,
            lockDays: lockDays,
            start: currentTime,
            cooldownEnds: currentTime + uint64($.cooldownDuration),
            hotkey: hotkey,
            exists: true
        });

        emit ParentLockCreated(msg.sender, $.category, amount, shares, lockDays, hotkey);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function lockTopUp(uint256 amount) external whenNotPaused {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        LockPosition storage lockPos = $.lockPositions[msg.sender];
        if (!lockPos.exists) revert LockPositionNotFound();
        if (amount == 0) revert InvalidAmount();
        if ($.parentPendingWithdrawal[msg.sender]) revert PendingWithdrawalExists();

        uint256 shares = _pullMintAndDistribute(amount);

        lockPos.lockedAmount += amount;
        lockPos.lockedShares += shares;
        lockPos.cooldownEnds = uint64(block.timestamp) + uint64($.cooldownDuration);

        emit ParentLockToppedUp(msg.sender, amount, shares, lockPos.lockedAmount);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function extendLock(uint64 extensionDays) external whenNotPaused {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        LockPosition storage lockPos = $.lockPositions[msg.sender];
        if (!lockPos.exists) revert LockPositionNotFound();
        if ($.parentPendingWithdrawal[msg.sender]) revert PendingWithdrawalExists();

        uint64 newLockDays = lockPos.lockDays + extensionDays;
        if (newLockDays <= lockPos.lockDays) revert InvalidLockDays();
        if (newLockDays > $.maxLockDays) revert InvalidLockDays();

        lockPos.lockDays = newLockDays;

        emit ParentLockExtended(msg.sender, newLockDays);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function releaseFromParent(uint256 amount) external whenNotPaused {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        LockPosition storage lockPos = $.lockPositions[msg.sender];
        if (!lockPos.exists) revert LockPositionNotFound();

        if (block.timestamp < lockPos.start + uint256(lockPos.lockDays) * 1 days) {
            revert PositionLocked();
        }
        if (block.timestamp < lockPos.cooldownEnds) revert CooldownNotExpired();
        if (amount == 0 || amount > lockPos.lockedAmount) revert InvalidAmount();

        bool isFullRelease = (amount == lockPos.lockedAmount);

        uint256 shares;
        if (isFullRelease) {
            shares = lockPos.lockedShares;
        } else {
            shares = (lockPos.lockedShares * amount) / lockPos.lockedAmount;
        }

        (uint256 payout, bool sufficient) = _prepareSharePayout(shares);
        if (!sufficient) revert InsufficientVaultBalance();

        if (isFullRelease) {
            _settleFullExit(msg.sender, shares, payout);
        } else {
            lockPos.lockedShares -= shares;
            lockPos.lockedAmount -= amount;
            _burn(msg.sender, shares);
            SafeERC20.safeTransfer(IERC20(asset()), msg.sender, payout);
        }

        emit ParentLockReleased(msg.sender, shares, payout);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function requestReleaseFromParent() external whenNotPaused {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        LockPosition storage lockPos = $.lockPositions[msg.sender];
        if (!lockPos.exists) revert LockPositionNotFound();

        if (block.timestamp < lockPos.start + uint256(lockPos.lockDays) * 1 days) {
            revert PositionLocked();
        }
        if (block.timestamp < lockPos.cooldownEnds) revert CooldownNotExpired();
        if ($.parentPendingWithdrawal[msg.sender]) revert PendingWithdrawalExists();

        $.parentPendingWithdrawal[msg.sender] = true;

        emit ParentWithdrawalQueued(msg.sender, lockPos.lockedShares);
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function processQueuedParentWithdrawals(address[] calldata owners) external onlyRole(Roles.KEEPER_BOT) {
        ParentVaultStorage storage $ = _getParentVaultStorage();

        for (uint256 i = 0; i < owners.length; i++) {
            address owner = owners[i];
            if (!$.parentPendingWithdrawal[owner]) continue;

            LockPosition storage lockPos = $.lockPositions[owner];
            if (!lockPos.exists) continue;
            if (block.timestamp < lockPos.start + uint256(lockPos.lockDays) * 1 days) continue;
            if (block.timestamp < lockPos.cooldownEnds) continue;

            uint256 shares = lockPos.lockedShares;

            (uint256 payout, bool sufficient) = _prepareSharePayout(shares);
            if (!sufficient || payout == 0) continue;

            _settleFullExit(owner, shares, payout);
            emit ParentWithdrawalProcessed(owner, payout);
        }
    }

    /*//////////////////////////////////////////////////////////////
                        FORCE EXIT (SATELLITE-DRIVEN)
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaParentVault
     */
    function executeForceExit(address owner, uint256 penaltyBps) external onlyRole(Roles.FORCE_EXITER) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        LockPosition storage lockPos = $.lockPositions[owner];
        if (!lockPos.exists) revert LockPositionNotFound();

        uint256 shares = lockPos.lockedShares;
        (uint256 payout, bool sufficient) = _prepareSharePayout(shares);
        if (!sufficient) revert InsufficientVaultBalance();
        if (penaltyBps > 0) payout -= (payout * penaltyBps) / BASIS_POINTS;

        _settleFullExit(owner, shares, payout);
        emit ParentEvicted(owner, $.category, payout);
    }

    /*//////////////////////////////////////////////////////////////
                        TRANSFER RESTRICTION
    //////////////////////////////////////////////////////////////*/

    /// @dev Block transfers into locked shares; mints and burns bypass this
    function _update(address from, address to, uint256 value) internal override {
        if (from != address(0) && to != address(0)) {
            ParentVaultStorage storage $ = _getParentVaultStorage();
            LockPosition storage lockPos = $.lockPositions[from];
            if (lockPos.exists) {
                uint256 unlocked = balanceOf(from) - lockPos.lockedShares;
                if (value > unlocked) revert TransferExceedsUnlocked();
            }
        }
        super._update(from, to, value);
    }

    /*//////////////////////////////////////////////////////////////
                        LOCK CONFIGURATION
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaParentVault
     */
    function setParentMaxLockDays(uint64 newMax) external onlyRole(Roles.ADMIN) {
        if (newMax == 0 || newMax > 1825) revert InvalidLockDays();
        ParentVaultStorage storage $ = _getParentVaultStorage();
        $.maxLockDays = newMax;
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function setParentCooldownDuration(uint256 newDuration) external onlyRole(Roles.ADMIN) {
        if (newDuration > 30 days) revert InvalidCooldown();
        ParentVaultStorage storage $ = _getParentVaultStorage();
        $.cooldownDuration = newDuration;
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function setParentMinimumLockAmount(uint256 newMinimum) external onlyRole(Roles.ADMIN) {
        if (newMinimum == 0) revert InvalidAmount();
        ParentVaultStorage storage $ = _getParentVaultStorage();
        $.minimumLockAmount = newMinimum;
    }

    /*//////////////////////////////////////////////////////////////
                        LOCK VIEW FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @inheritdoc ICarthaParentVault
     */
    function getLockPosition(address user) external view returns (LockPosition memory) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        return $.lockPositions[user];
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function isParentLocked(address user) external view returns (bool) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        LockPosition storage lockPos = $.lockPositions[user];
        if (!lockPos.exists) return false;
        return block.timestamp < lockPos.start + uint256(lockPos.lockDays) * 1 days;
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function canReleaseFromParent(address user) external view returns (bool) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        LockPosition storage lockPos = $.lockPositions[user];
        if (!lockPos.exists) return false;
        return block.timestamp >= lockPos.start + uint256(lockPos.lockDays) * 1 days
            && block.timestamp >= lockPos.cooldownEnds;
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function hasParentPendingWithdrawal(address user) external view returns (bool) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        return $.parentPendingWithdrawal[user];
    }

    /**
     * @inheritdoc ICarthaParentVault
     */
    function lockNonces(address user) external view returns (uint256) {
        ParentVaultStorage storage $ = _getParentVaultStorage();
        return $.lockNonces[user];
    }

    /// @notice EIP-712 domain separator
    function DOMAIN_SEPARATOR() external view returns (bytes32) {
        return _domainSeparatorV4();
    }

    /*//////////////////////////////////////////////////////////////
                        ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function emergencyPause() external onlyRole(Roles.ADMIN) {
        _pause();
    }

    function unpause() external onlyRole(Roles.ADMIN) {
        _unpause();
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyRole(Roles.ADMIN) {}

    /*//////////////////////////////////////////////////////////////
                        INTERNAL: SIGNATURE VERIFICATION
    //////////////////////////////////////////////////////////////*/

    function _verifyParentLockSignature(ParentLockRequest memory request, bytes calldata signature) internal view {
        bytes32 structHash = keccak256(
            abi.encode(
                PARENT_LOCK_REQUEST_TYPEHASH,
                request.owner,
                request.category,
                request.amount,
                request.lockDays,
                request.hotkey,
                request.timestamp,
                request.nonce
            )
        );

        ParentVaultStorage storage $ = _getParentVaultStorage();
        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = ECDSA.recover(digest, signature);

        if (!$.diamond.hasRole(Roles.EJECTOR, signer)) {
            revert Unauthorized();
        }
    }
}
