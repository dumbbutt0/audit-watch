// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Initializable} from "openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol";
import {UUPSUpgradeable} from "openzeppelin-contracts-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
import {ERC20Upgradeable} from "openzeppelin-contracts-upgradeable/contracts/token/ERC20/ERC20Upgradeable.sol";
import {BeaconProxy} from "openzeppelin-contracts/contracts/proxy/beacon/BeaconProxy.sol";
import {IERC20Metadata} from "openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import {ICarthaVaultFactory} from "./interfaces/ICarthaVaultFactory.sol";
import {CarthaVault} from "./CarthaVault.sol";
import {CarthaParentVault} from "./CarthaParentVault.sol";
import {ICarthaParentVault} from "./interfaces/ICarthaParentVault.sol";
import {ICarthaAccessControl} from "./interfaces/ICarthaAccessControl.sol";
import {ICarthaVault} from "./interfaces/ICarthaVault.sol";
import {Roles} from "./diamond/Roles.sol";

contract CarthaVaultFactory is ICarthaVaultFactory, Initializable, UUPSUpgradeable {
    /// @custom:storage-location erc7201:cartha.storage.CarthaVaultFactory
    struct CarthaVaultFactoryStorage {
        address beacon;
        address accessControl;
        VaultInfo[] vaults;
        mapping(address => bool) isFactoryVault;
        mapping(address => address[]) vaultsByAsset;
        mapping(bytes32 => address) vaultByPoolId;
        // Parent vault storage
        address parentBeacon;
        ParentVaultInfo[] parentVaults;
        mapping(address => bool) isFactoryParent;
        mapping(bytes32 => address) parentByCategory;
        mapping(address => address[]) childrenByParent;
        mapping(address => address) parentByChild;
    }

    // keccak256(abi.encode(uint256(keccak256("cartha.storage.CarthaVaultFactory")) - 1)) & ~bytes32(uint256(0xff))
    bytes32 private constant FACTORY_STORAGE_LOCATION =
        0xdb1962c4a5690592ca7465b77ca9c0256f84cb63342b7979f63bc5799a61d100;

    function _getFactoryStorage() private pure returns (CarthaVaultFactoryStorage storage $) {
        assembly {
            $.slot := FACTORY_STORAGE_LOCATION
        }
    }

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address beacon_, address parentBeacon_, address accessControl_) external initializer {
        if (beacon_ == address(0)) revert InvalidBeacon();
        if (parentBeacon_ == address(0)) revert InvalidBeacon();
        if (accessControl_ == address(0)) revert InvalidAccessControl();

        CarthaVaultFactoryStorage storage $ = _getFactoryStorage();
        $.beacon = beacon_;
        $.parentBeacon = parentBeacon_;
        $.accessControl = accessControl_;
    }

    modifier onlyRole(uint8 role) {
        _checkRole(role);
        _;
    }

    function _checkRole(uint8 role) internal view {
        CarthaVaultFactoryStorage storage $ = _getFactoryStorage();
        if (!ICarthaAccessControl($.accessControl).hasRole(role, msg.sender)) {
            revert Unauthorized();
        }
    }

    function _authorizeUpgrade(address) internal override onlyRole(Roles.ADMIN) {}

    function deployVault(VaultConfig calldata config) external returns (address vault) {
        CarthaVaultFactoryStorage storage $ = _getFactoryStorage();

        if (
            !ICarthaAccessControl($.accessControl).hasRole(Roles.FACTORY, msg.sender)
                && !ICarthaAccessControl($.accessControl).hasRole(Roles.ADMIN, msg.sender)
        ) {
            revert Unauthorized();
        }
        if (config.asset == address(0)) revert InvalidAsset();
        if ($.vaultByPoolId[config.poolId] != address(0)) revert VaultAlreadyExists();

        bytes memory initData = abi.encodeWithSelector(
            CarthaVault.initialize.selector, $.accessControl, config.asset, config.poolId, config.name, config.symbol
        );

        vault = address(new BeaconProxy($.beacon, initData));

        $.vaults
            .push(
                VaultInfo({vaultAddress: vault, asset: config.asset, deployedAt: block.timestamp, deployer: msg.sender})
            );

        $.isFactoryVault[vault] = true;
        $.vaultsByAsset[config.asset].push(vault);
        $.vaultByPoolId[config.poolId] = vault;

        emit VaultDeployed(vault, config.asset, msg.sender, $.vaults.length - 1);
    }

    function deployParentVault(ParentVaultConfig calldata config) external returns (address parentVault) {
        CarthaVaultFactoryStorage storage $ = _getFactoryStorage();

        if (
            !ICarthaAccessControl($.accessControl).hasRole(Roles.FACTORY, msg.sender)
                && !ICarthaAccessControl($.accessControl).hasRole(Roles.ADMIN, msg.sender)
        ) {
            revert Unauthorized();
        }
        if (config.asset == address(0)) revert InvalidAsset();
        if (config.category == bytes32(0)) revert InvalidCategory();
        if ($.parentByCategory[config.category] != address(0)) revert ParentAlreadyExists();

        bytes memory initData = abi.encodeWithSelector(
            CarthaParentVault.initialize.selector,
            config.asset,
            config.category,
            config.name,
            config.symbol,
            $.accessControl
        );

        parentVault = address(new BeaconProxy($.parentBeacon, initData));

        $.parentVaults
            .push(
                ParentVaultInfo({
                    vaultAddress: parentVault,
                    asset: config.asset,
                    category: config.category,
                    deployedAt: block.timestamp,
                    deployer: msg.sender
                })
            );

        $.isFactoryParent[parentVault] = true;
        $.parentByCategory[config.category] = parentVault;

        emit ParentVaultDeployed(parentVault, config.asset, config.category, msg.sender, $.parentVaults.length - 1);
    }

    function addChildToParent(address parent, address child, uint256 weight, uint256 maxAllocation)
        external
        onlyRole(Roles.ADMIN)
    {
        CarthaVaultFactoryStorage storage $ = _getFactoryStorage();

        if (!$.isFactoryParent[parent]) revert InvalidParent();
        if (!$.isFactoryVault[child]) revert InvalidChild();
        if ($.parentByChild[child] != address(0)) revert ChildAlreadyHasParent();
        if (ICarthaParentVault(parent).asset() != ICarthaVault(child).asset()) revert AssetMismatch();

        $.childrenByParent[parent].push(child);
        $.parentByChild[child] = parent;

        ICarthaParentVault(parent).addPool(child, weight, maxAllocation);

        emit ChildAddedToParent(parent, child, weight, maxAllocation);
    }

    function removeChildFromParent(address parent, address child) external onlyRole(Roles.ADMIN) {
        CarthaVaultFactoryStorage storage $ = _getFactoryStorage();

        if (!$.isFactoryParent[parent]) revert InvalidParent();
        if ($.parentByChild[child] != parent) revert ChildNotInParent();

        address[] storage children = $.childrenByParent[parent];
        for (uint256 i = 0; i < children.length; i++) {
            if (children[i] == child) {
                children[i] = children[children.length - 1];
                children.pop();
                break;
            }
        }

        delete $.parentByChild[child];

        ICarthaParentVault(parent).removePool(child, false);

        emit ChildRemovedFromParent(parent, child);
    }

    function beacon() external view returns (address) {
        return _getFactoryStorage().beacon;
    }

    function accessControl() external view returns (address) {
        return _getFactoryStorage().accessControl;
    }

    function getVaultCount() external view returns (uint256) {
        return _getFactoryStorage().vaults.length;
    }

    function getVaultInfo(uint256 vaultId) external view returns (VaultInfo memory) {
        return _getFactoryStorage().vaults[vaultId];
    }

    function getAllVaults() external view returns (address[] memory vaults) {
        CarthaVaultFactoryStorage storage $ = _getFactoryStorage();
        uint256 count = $.vaults.length;
        vaults = new address[](count);
        for (uint256 i = 0; i < count; i++) {
            vaults[i] = $.vaults[i].vaultAddress;
        }
    }

    function getVaultsByAsset(address asset) external view returns (address[] memory) {
        return _getFactoryStorage().vaultsByAsset[asset];
    }

    function isFactoryVault(address vault) external view returns (bool) {
        return _getFactoryStorage().isFactoryVault[vault];
    }

    function getDefaultConfig(address vault) external view returns (VaultConfig memory) {
        ICarthaVault v = ICarthaVault(vault);
        return VaultConfig({
            asset: v.asset(),
            poolId: v.poolId(),
            name: ERC20Upgradeable(vault).name(),
            symbol: ERC20Upgradeable(vault).symbol()
        });
    }

    function parentBeacon() external view returns (address) {
        return _getFactoryStorage().parentBeacon;
    }

    function getParentByCategory(bytes32 category) external view returns (address) {
        return _getFactoryStorage().parentByCategory[category];
    }

    function getChildrenOfParent(address parent) external view returns (address[] memory) {
        return _getFactoryStorage().childrenByParent[parent];
    }

    function getParentOfChild(address child) external view returns (address) {
        return _getFactoryStorage().parentByChild[child];
    }

    function getAllParents() external view returns (address[] memory parents) {
        CarthaVaultFactoryStorage storage $ = _getFactoryStorage();
        uint256 count = $.parentVaults.length;
        parents = new address[](count);
        for (uint256 i = 0; i < count; i++) {
            parents[i] = $.parentVaults[i].vaultAddress;
        }
    }

    function isParentVault(address vault) external view returns (bool) {
        return _getFactoryStorage().isFactoryParent[vault];
    }

    function getParentVaultCount() external view returns (uint256) {
        return _getFactoryStorage().parentVaults.length;
    }

    function getParentVaultInfo(uint256 vaultId) external view returns (ParentVaultInfo memory) {
        return _getFactoryStorage().parentVaults[vaultId];
    }
}
