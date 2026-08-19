// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ICarthaAccessControl} from "../../interfaces/ICarthaAccessControl.sol";
import {LibDiamond} from "../LibDiamond.sol";
import {Roles} from "../Roles.sol";

contract AccessControlFacet is ICarthaAccessControl {
    function grantRole(uint8 role, address account) external override {
        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        if (!ds.roles[Roles.ADMIN][msg.sender]) revert Unauthorized();
        if (account == address(0)) revert InvalidAccount();

        _grantRole(role, account);
    }

    function revokeRole(uint8 role, address account) external override {
        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        if (!ds.roles[Roles.ADMIN][msg.sender]) revert Unauthorized();

        _revokeRole(role, account);
    }

    function renounceRole(uint8 role) external override {
        _revokeRole(role, msg.sender);
    }

    function hasRole(uint8 role, address account) public view override returns (bool) {
        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        return ds.roles[role][account];
    }

    function _grantRole(uint8 role, address account) internal {
        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        if (!ds.roles[role][account]) {
            ds.roles[role][account] = true;
            emit RoleGranted(role, account, msg.sender);
        }
    }

    function _revokeRole(uint8 role, address account) internal {
        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        if (ds.roles[role][account]) {
            ds.roles[role][account] = false;
            emit RoleRevoked(role, account, msg.sender);
        }
    }
}
