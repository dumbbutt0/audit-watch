// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// SCOPE RULE: this artifact is upgradeable + ownable but NO in-scope contract deploys/owns/upgrades it.
// With no in-scope controller, its lifecycle is genuinely out of scope and must NOT be flagged.
import "openzeppelin-contracts/contracts/proxy/utils/UUPSUpgradeable.sol";
contract StandaloneToken is UUPSUpgradeable {
    function _authorizeUpgrade(address) internal override {}
}
