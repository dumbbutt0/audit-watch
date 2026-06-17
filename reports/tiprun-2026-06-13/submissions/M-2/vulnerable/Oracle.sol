// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./IOracle.sol";
import "../plugins/ITransactionPlugin.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract Oracle is IOracle, Initializable, OwnableUpgradeable {
    address public transactionProcessor;
    mapping(uint64 => OraclePrice) public prices;

    event UpdatePrice(uint64 indexed assetId, OraclePrice newPrice);
    event TransactionProcessorSet(address newTransactionProcessor);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address owner) public initializer {
        if (owner == address(0)) {
            owner = msg.sender;
        }
        __Ownable_init(owner);
    }

    modifier onlyAuthorizedCaller() {
        require(
            ICallerRegistry(transactionProcessor).isAuthorizedCaller(msg.sender) || msg.sender == owner(),
            "Oracle: not authorized"
        );
        _;
    }

    function getPrice(uint64 assetId) external view override returns (int256 price, bool exist) {
        OraclePrice memory priceObj = prices[assetId];
        return (priceObj.price, priceObj.timestamp > 0);
    }

    function getCurrentTimestamp(uint64 assetId) external view override returns (uint256 timestamp) {
        return prices[assetId].timestamp;
    }

    function updatePrice(uint64 assetId, OraclePrice memory newPrice) external override onlyAuthorizedCaller {
        // TODO: check with backend behaviour
        // require(
        //     newPrice.timestamp > prices[assetId].timestamp,
        //     "Oracle: new price timestamp must be greater than current price timestamp"
        // );
        require(newPrice.price > 0, "Oracle: price negative");
        prices[assetId] = newPrice;
        emit UpdatePrice(assetId, newPrice);
    }

    function setTransactionProcessor(address _transactionProcessor) external onlyOwner {
        transactionProcessor = _transactionProcessor;
        emit TransactionProcessorSet(transactionProcessor);
    }
}
