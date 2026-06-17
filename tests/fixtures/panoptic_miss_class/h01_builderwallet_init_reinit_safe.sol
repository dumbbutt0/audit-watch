// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract BuilderWalletSafe {
    address public admin;
    bool private _initialized;
    function init(address _admin) external {
        require(!_initialized, "init once");                              // init-once guard
        _initialized = true; admin = _admin;
    }
    function sweep(address to) external { require(msg.sender == admin, "only admin"); /* ... */ }
}
