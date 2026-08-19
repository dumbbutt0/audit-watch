// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {LibDiamond} from "./LibDiamond.sol";
import {Roles} from "./Roles.sol";

contract DiamondInit {
    function init(address admin) external {
        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();

        if (admin == address(0)) {
            revert("DiamondInit: admin cannot be zero address");
        }

        ds.roles[Roles.ADMIN][admin] = true;
    }
}
