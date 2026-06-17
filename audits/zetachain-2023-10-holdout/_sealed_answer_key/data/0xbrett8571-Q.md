## [L-1] Missing Events in ZetaConnectorZEVM

## Impact

Lack of events reduces transaction traceability and auditability.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L84-L86

```solidity
    receive() external payable {
        if (msg.sender != wzeta) revert OnlyWZETA();
    }
```
## Recommended Mitigation

Emit events from crucial functions to enable transaction tracking and monitoring. Use indexed parameters for filtering.

## [L-2] Missing Events in SystemContract

## Impact

Missing events for cross-chain deposits makes tracking interactions with omnichain contracts difficult.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L79

```solidity
    function depositAndCall(
        zContext calldata context,
        address zrc20,
        uint256 amount,
        address target,
        bytes calldata message
    ) external {
        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
        if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();


        IZRC20(zrc20).deposit(target, amount);
        zContract(target).onCrossChainCall(context, zrc20, amount, message);
    }
```

## Recommended Mitigation

Emit events from `depositAndCall` with parameters like deposited ZRC20, deposit amount and contract address called.

## [L-3] Event-Based Reentrancy in ZetaConnectorZEVM

## Impact

Emitting events after external calls enables reentrancy attacks to manipulate state before event emission.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92-L108

```solidity
    function send(ZetaInterfaces.SendInput calldata input) external {
        // Transfer wzeta to "fungible" module, which will be burnt by the protocol post processing via hooks.
        if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();
        WZETA(wzeta).withdraw(input.zetaValueAndGas);
        (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
        if (!sent) revert FailedZetaSent();
        emit ZetaSent(
            tx.origin,
            msg.sender,
            input.destinationChainId,
            input.destinationAddress,
            input.zetaValueAndGas,
            input.destinationGasLimit,
            input.message,
            input.zetaParams
        );
    }
```

## Recommended Mitigation

Follow checks-effects-interactions pattern to emit events before external calls. Use reentrancy guards.  

## [L-4] Event-Based Reentrancy in ZRC20

## Impact

Withdrawal event after transfer call allows exploit to manipulate balances through reentrancy.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256-L264

```solidity
    function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
        (address gasZRC20, uint256 gasFee) = withdrawGasFee();
        if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
            revert GasFeeTransferFailed();
        }
        _burn(msg.sender, amount);
        emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);
        return true;
    }
```

## Recommended Mitigation

Emit events before external calls. Use mutexes, reentrancy guards to prevent reentrancy.

## [L-5] Event-Based Reentrancy in ZetaConnector Non-Eth

## Impact

Emitting events after external calls introduces reentrancy vulnerability.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40-L53

```solidity
    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
        ZetaNonEthInterface(zetaToken).burnFrom(msg.sender, input.zetaValueAndGas);


        emit ZetaSent(
            tx.origin,
            msg.sender,
            input.destinationChainId,
            input.destinationAddress,
            input.zetaValueAndGas,
            input.destinationGasLimit,
            input.message,
            input.zetaParams
        );
    }
```

## Recommended Mitigation

Place events before external calls. Follow checks -> effects -> interactions pattern.   

## [L-6] Event-Based Reentrancy in onReceive

## Impact

Reentrancy possible due to event emissions after external call in onReceive.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79

```solidity
    function onReceive(
        bytes calldata zetaTxSenderAddress,
        uint256 sourceChainId,
        address destinationAddress,
        uint256 zetaValue,
        bytes calldata message,
        bytes32 internalSendHash
    ) external override onlyTssAddress {
        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);


        if (message.length > 0) {
            ZetaReceiver(destinationAddress).onZetaMessage(
                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
            );
        }


        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
    }
```

## Recommended Mitigation 

Shift event emissions before external calls.

## [L-7] Event-Based Reentrancy in onRevert
   
## Impact

Event emissions after call enable reentrancy attacks against onRevert.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L112

```solidity
    function onRevert(
        address zetaTxSenderAddress,
        uint256 sourceChainId,
        bytes calldata destinationAddress,
        uint256 destinationChainId,
        uint256 remainingZetaValue,
        bytes calldata message,
        bytes32 internalSendHash
    ) external override whenNotPaused onlyTssAddress {
        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
            revert ExceedsMaxSupply(maxSupply);
        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);


        if (message.length > 0) {
            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
                ZetaInterfaces.ZetaRevert(
                    zetaTxSenderAddress,
                    sourceChainId,
                    destinationAddress,
                    destinationChainId,
                    remainingZetaValue,
                    message
                )
            );
        }
```

## Recommended Mitigation

Check effects interactions pattern should be followed. Emit events before calls.


## [L-8] Missing Payable Flag

## Impact

Transaction may fail if contract balance empty but value passed.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96

```solidity
        (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```

## Recommended Mitigation

Make function payable if value needs to be sent.

## [L-9] Missing Underscores

## Impact 

Reduces readability as internal/private functions lack underscores.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87-L91

```solidity
    function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
        if (tokenA == tokenB) revert CantBeIdenticalAddresses();
        (token0, token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
        if (token0 == address(0)) revert CantBeZeroAddress();
    }
```

## Recommended Mitigation

Prefix underscores before functions and variables based on visibility. 

## [L-10] Hardcoded Gas Limits
   
## Impact

Hardcoded limits hurt future proofing, upgrades require new deployments.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L29-L30

```solidity
    /// @notice Gas limit.
    uint256 public GAS_LIMIT;
```

## Recommended Mitigation

Make gas limits configurable via admin addresses.  

## [L-11] Hardcoded Address 1

## Impact
    
Unknown address detected. Potential loss of funds based on usage.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L62-L63

```solidity
    /// @notice Fungible module address.
    address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
```

## Recommended Mitigation

Add validations for address change.

## [L-12] Hardcoded Address 2

## Impact

Multiple instances of same unknown hardcoded address seen.

```solidity
    /// @notice Fungible address is always the same, maintained at the protocol level
    address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

## Recommended Mitigation 

As above, and add validations.

## [L-13] Hardcoded Address 3

## Impact
    
Repeated instances of 0x735b14BB79463307AAcBED86DAf3322B1e6226aB require investigation.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L30-L31

```solidity
    /// @notice Fungible address is always the same, it's on protocol level.
    address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

## Recommended Mitigation

Check usage and linked contract code thoroughly. Add validations for changes.


## [L-14] Missing Indexed Keywords 1

## Impact

Lack of filtering capabilities for events through indexes. 

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27

```solidity
    event TSSAddressUpdated(address callerAddress, address newTssAddress);
```

## Recommended Mitigation

Add indexed keyword to crucial parameters.

## [L-15] Missing Indexed Keywords 2
   
## Impact

As earlier, missing indexes reduces events filtering utility. 

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29

```solidity
    event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);
```

## Recommended Mitigation

Make highly usable parameters indexed.

## [L-16] Missing Indexed Keywords 3

## Impact

Indexes needed for events to enable selective filtering.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31

```solidity
    event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);
```

## Recommended Mitigation 

Add indexes judiciously balancing costs.  

## [L-17] Missing Indexed Keywords 4

## Impact

Indexes would allow filtering gas related events for analysis.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42

```solidity
    event SetGasPrice(uint256, uint256);
```

## Recommended Mitigation

Add indexes to relevant event topics.  

## [L-18] Missing Indexed Keywords 5

## Impact

Need indexes on SetGasCoin event for filtering functionality.  

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43

```solidity
    event SetGasCoin(uint256, address);
```

## Recommended Mitigation

Add indexes where filtering utility justifies gas cost.

## [L-19] Missing Indexed Keywords 6

## Impact

Indexes required to enable isolating specific SetGasZetaPool event logs.

https://github.com/code-423n4/2023-11-zetachain/blob/44c8dd426e829536850b5d42b3f0ade1ce29a23c/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44

```solidity
    event SetGasZetaPool(uint256, address);
```

## Recommended Mitigation

Index parameters like `chainID`.