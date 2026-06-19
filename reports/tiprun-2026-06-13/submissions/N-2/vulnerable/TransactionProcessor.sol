// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "./core/plugins/ITransactionPlugin.sol";

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract TransactionProcessor is Initializable, OwnableUpgradeable {
    using EnumerableSet for EnumerableSet.AddressSet;

    /// @notice Maps txType => plugin address. Zero address means no plugin registered.
    mapping(uint8 => address) public txTypeToPlugin;

    /// @notice Set of all registered plugin addresses.
    EnumerableSet.AddressSet private _registeredPlugins;

    /// @notice Maps capability id => providing plugin address. Zero address means
    /// no plugin currently provides this capability.
    mapping(bytes32 => address) public capabilityProvider;

    address public multiTransactionProcessor;

    event PluginRegistered(address indexed plugin, uint8[] txTypes);
    event PluginUnregistered(address indexed plugin, uint8[] txTypes);
    event CapabilityRegistered(bytes32 indexed capability, address indexed plugin);
    event CapabilityUnregistered(bytes32 indexed capability, address indexed plugin);
    event TransactionDispatched(uint8 indexed txType, address indexed plugin);

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

    modifier onlyMultiTransactionProcessor() {
        require(
            msg.sender == multiTransactionProcessor, "TransactionProcessor: caller is not the multiTransactionProcessor"
        );
        _;
    }

    function setMultiTransactionProcessor(address _multiTransactionProcessor) public onlyOwner {
        multiTransactionProcessor = _multiTransactionProcessor;
    }

    // ---- Plugin Management ----

    function registerPlugin(address plugin) external onlyOwner {
        require(plugin != address(0), "TransactionProcessor: zero address");
        require(!_registeredPlugins.contains(plugin), "TransactionProcessor: already registered");

        uint8[] memory types = ITransactionPlugin(plugin).supportedTxTypes();
        bytes32[] memory provided = ITransactionPlugin(plugin).providedCapabilities();
        bytes32[] memory required = ITransactionPlugin(plugin).requiredCapabilities();
        require(types.length > 0 || provided.length > 0, "TransactionProcessor: nothing to register");

        // Required capabilities must already be available.
        for (uint256 i = 0; i < required.length;) {
            require(capabilityProvider[required[i]] != address(0), "TransactionProcessor: missing required capability");
            unchecked {
                ++i;
            }
        }

        for (uint256 i = 0; i < types.length;) {
            uint8 txType = types[i];
            require(txTypeToPlugin[txType] == address(0), "TransactionProcessor: txType already registered");
            txTypeToPlugin[txType] = plugin;
            unchecked {
                ++i;
            }
        }

        for (uint256 i = 0; i < provided.length;) {
            bytes32 cap = provided[i];
            require(capabilityProvider[cap] == address(0), "TransactionProcessor: capability already provided");
            capabilityProvider[cap] = plugin;
            emit CapabilityRegistered(cap, plugin);
            unchecked {
                ++i;
            }
        }

        _registeredPlugins.add(plugin);
        emit PluginRegistered(plugin, types);
    }

    function unregisterPlugin(address plugin) external onlyOwner {
        require(_registeredPlugins.contains(plugin), "TransactionProcessor: not registered");

        uint8[] memory types = ITransactionPlugin(plugin).supportedTxTypes();
        for (uint256 i = 0; i < types.length;) {
            delete txTypeToPlugin[types[i]];
            unchecked {
                ++i;
            }
        }

        bytes32[] memory provided = ITransactionPlugin(plugin).providedCapabilities();
        for (uint256 i = 0; i < provided.length;) {
            bytes32 cap = provided[i];
            if (capabilityProvider[cap] == plugin) {
                delete capabilityProvider[cap];
                emit CapabilityUnregistered(cap, plugin);
            }
            unchecked {
                ++i;
            }
        }

        _registeredPlugins.remove(plugin);
        emit PluginUnregistered(plugin, types);
    }

    // ---- Transaction Dispatch ----

    function processTransaction(uint8 txType, bytes calldata payload) external onlyMultiTransactionProcessor {
        address plugin = txTypeToPlugin[txType];
        require(plugin != address(0), "TransactionProcessor: no plugin for txType");

        bool handled = ITransactionPlugin(plugin).processTransaction(txType, payload);
        require(handled, "TransactionProcessor: plugin did not handle txType");

        emit TransactionDispatched(txType, plugin);
    }

    // ---- View Functions ----

    function getPlugin(uint8 txType) external view returns (address) {
        return txTypeToPlugin[txType];
    }

    function getRegisteredPlugins() external view returns (address[] memory) {
        return _registeredPlugins.values();
    }

    function isPluginRegistered(address plugin) external view returns (bool) {
        return _registeredPlugins.contains(plugin);
    }

    function isAuthorizedCaller(address caller) external view returns (bool) {
        return _registeredPlugins.contains(caller);
    }
}
