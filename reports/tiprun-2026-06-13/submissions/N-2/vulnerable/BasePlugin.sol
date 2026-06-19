// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./ITransactionPlugin.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

abstract contract BasePlugin is ITransactionPlugin, Initializable, OwnableUpgradeable {
    address public transactionProcessor;

    modifier onlyTransactionProcessor() {
        require(msg.sender == transactionProcessor, "BasePlugin: caller is not TransactionProcessor");
        _;
    }

    function setTransactionProcessor(address _transactionProcessor) external onlyOwner {
        require(_transactionProcessor != address(0), "BasePlugin: zero address");
        transactionProcessor = _transactionProcessor;
    }

    /// @inheritdoc ITransactionPlugin
    /// @dev Override in subclass to advertise capabilities.
    function providedCapabilities() external view virtual override returns (bytes32[] memory) {
        return new bytes32[](0);
    }

    /// @inheritdoc ITransactionPlugin
    /// @dev Override in subclass to declare dependencies.
    function requiredCapabilities() external view virtual override returns (bytes32[] memory) {
        return new bytes32[](0);
    }
}
