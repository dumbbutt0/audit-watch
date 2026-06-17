// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./TransactionProcessor.sol";
import "./core/config/GeneralConfig.sol";

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

import "./core/position/IPositionManager.sol";

contract MultiTransactionProcessor is Initializable, OwnableUpgradeable {
    TransactionProcessor transactionProcessor;
    GeneralConfig generalConfig;
    address txBatcher;

    event MultiTransactionsProcessed(int64 processedIndex, int64 total);
    event AccountPositionUpdated(uint64 indexed account, AccountPosition position);
    event OrderFulfillmentUpdated(bytes32 orderId, int256 newValue);
    event CollateralPositionIndexSet(uint64 indexed accountId, uint64 indexed assetId, uint64 collateralPositionIndex);
    event CollateralTransferred(uint64 indexed accountId, uint64 fromIndex, uint64 toIndex, int256 amount);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    modifier onlyTxBatcher() {
        require(msg.sender == txBatcher, "MultiTransactionProcessor: caller is not txBatcher");
        _;
    }

    function initialize(address owner) public initializer {
        if (owner == address(0)) {
            owner = msg.sender;
        }
        __Ownable_init(owner);
    }

    function setGeneralConfig(address _generalConfig) public onlyOwner {
        generalConfig = GeneralConfig(_generalConfig);
    }

    function setTransactionProcessor(address _transactionProcessor) public onlyOwner {
        transactionProcessor = TransactionProcessor(_transactionProcessor);
    }

    function setTxBatcher(address _txBatcher) public onlyOwner {
        txBatcher = _txBatcher;
    }

    function getTransactionProcessor() public view returns (address) {
        return address(transactionProcessor);
    }

    function processMultiTransactions(bytes[] memory txs, uint64 configVersion) public onlyTxBatcher {
        require(txs.length > 0, "MultiTransactionProcessor: no transactions");
        uint64 currentVersion = generalConfig.configVersion();
        if (configVersion < currentVersion) {
            revert("MultiTransactionProcessor: config version mismatch");
        }
        uint256 len = txs.length;
        for (uint256 i = 0; i < len;) {
            _processTransaction(txs[i]);
            unchecked {
                ++i;
            }
        }

        require(len <= uint256(int256(type(int64).max)), "MultiTransactionProcessor: batch too large");
        int64 processedIndex = len == 0 ? int64(-1) : int64(int256(len) - 1);
        emit MultiTransactionsProcessed(processedIndex, int64(int256(len)));
    }

    function _processTransaction(bytes memory txData) internal {
        (uint8 txType, bytes memory payload) = _decodeEnvelope(txData);
        transactionProcessor.processTransaction(txType, payload);
    }

    function _decodeEnvelope(bytes memory txData) private pure returns (uint8 txType, bytes memory payload) {
        bytes1 bytesTxType;
        (bytesTxType, payload) = abi.decode(txData, (bytes1, bytes));
        require(payload.length > 0, "MultiTransactionProcessor: empty payload");
        txType = uint8(bytesTxType);
    }
}
