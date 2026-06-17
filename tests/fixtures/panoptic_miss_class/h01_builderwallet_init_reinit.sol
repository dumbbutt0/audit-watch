// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
// H-01 shape: init() has no init-once guard and no auth → anyone can re-init and overwrite admin, then drain.
contract BuilderWallet {
    address public admin;
    function init(address _admin) external { admin = _admin; }            // re-callable by anyone
    function sweep(address token, address to) external {
        require(msg.sender == admin, "only admin");
        IERC20(token).transfer(to, IERC20(token).balanceOf(address(this)));
    }
}
interface IERC20 { function transfer(address,uint256) external returns (bool); function balanceOf(address) external view returns (uint256); }
