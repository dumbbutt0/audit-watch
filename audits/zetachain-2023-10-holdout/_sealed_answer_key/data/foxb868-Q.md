# [Qa-01] Missing Events in ZetaInteractor Contract.

## Impact

The `setInteractorByChainId` function in the ZetaInteractor contract is missing event emissions. Events allow tracking transactions off-chain which is important for auditability and transparency. Without events, it would be difficult to monitor these interactor updates.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L56
```solidity
    function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
        interactorsByChainId[destinationChainId] = contractAddress;
    }
```

## Recommended Mitigation Steps

Consider emitting events in the `setInteractorByChainId` function to record the `interactor` contract address updated for each `chainID`. Index the event parameters for easier filtering.

# [Qa-02] Missing Events in ZetaConnectorZEVM Contract 

## Impact

The receive function in ZetaConnectorZEVM contract is missing event emissions. Events allow tracking transactions off-chain which is important for auditability and transparency. Without events, it would be difficult to monitor ETH deposits.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L84-L86
```solidity
    receive() external payable {
        if (msg.sender != wzeta) revert OnlyWZETA();
    }
```

## Recommended Mitigation Steps

Consider emitting a Deposit event in the receive function to record ETH deposits from wZETA contract.

# [Qa-03] Missing Events in ImmutableCreate2Factory Contract

## Impact 

The `safeCreate2Internal` function responsible for deploying contracts in the `ImmutableCreate2Factory` contract is missing event emissions. Events allow tracking transactions off-chain which is important for auditability and transparency. Without events, it would be difficult to monitor contract deployments.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L26-L74
```solidity
    function safeCreate2Internal(
        bytes32 salt,
        bytes memory initializationCode
    ) internal returns (address deploymentAddress) {
        // move the initialization code from calldata to memory.
        bytes memory initCode = initializationCode;


        // determine the target address for contract deployment.
        address targetDeploymentAddress = address(
            uint160( // downcast to match the address type.
                uint256( // convert to uint to truncate upper digits.
                    keccak256( // compute the CREATE2 hash using 4 inputs.
                        abi.encodePacked( // pack all inputs to the hash together.
                            hex"ff", // start with 0xff to distinguish from RLP.
                            address(this), // this contract will be the caller.
                            salt, // pass in the supplied salt value.
                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
                        )
                    )
                )
            )
        );


        // ensure that a contract hasn't been previously deployed to target address.
        require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");


        // using inline assembly: load data and length of data, then call CREATE2.
        assembly {
            // solhint-disable-line
            let encoded_data := add(0x20, initCode) // load initialization code.
            let encoded_size := mload(initCode) // load the init code's length.
            deploymentAddress := create2(
                // call CREATE2 with 4 arguments.
                callvalue, // forward any attached value.
                encoded_data, // pass in initialization code.
                encoded_size, // pass in init code's length.
                salt // pass in the salt value.
            )
        }


        // check address against target to ensure that deployment was successful.
        require(
            deploymentAddress == targetDeploymentAddress,
            "Failed to deploy contract using provided salt and initialization code."
        );


        // record the deployment of the contract to prevent redeploys.
        _deployed[deploymentAddress] = true;
    }
```

## Recommended Mitigation Steps

Consider emitting a ContractDeployed event in the safeCreate2Internal function to record details of each deployment through this factory contract.

# [Qa-04] Missing Events in ImmutableCreate2Factory Contract

## Impact

The `safeCreate2` function responsible for deploying contracts in the `ImmutableCreate2Factory` contract is missing event emissions. Events allow tracking transactions off-chain which is important for auditability and transparency. Without events, it would be difficult to monitor contract deployments.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L87-L92
```solidity
    function safeCreate2(
        bytes32 salt,
        bytes memory initializationCode
    ) public payable containsCaller(salt) returns (address deploymentAddress) {
        return safeCreate2Internal(salt, initializationCode);
    }
```

## Recommended Mitigation Steps 

Consider emitting a ContractDeployed event in the `safeCreate2` function to record details of each deployment through this factory contract.

# [Qa-05] Missing Events in ImmutableCreate2Factory Contract  

## Impact

The `safeCreate2AndTransfer` function responsible for deploying & transferring ownership of contracts in the ImmutableCreate2Factory contract is missing event emissions. Events allow tracking transactions off-chain which is important for auditability and transparency. Without events, it would be difficult to monitor contract deployments and ownership transfers.  

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L202-L208
```solidity
    function safeCreate2AndTransfer(
        bytes32 salt,
        bytes calldata initializationCode
    ) external payable containsCaller(salt) returns (address deploymentAddress) {
        deploymentAddress = safeCreate2Internal(salt, initializationCode);
        Ownable(deploymentAddress).transferOwnership(msg.sender);
    }
```

## Recommended Mitigation Steps

Consider emitting events in the `safeCreate2AndTransfer` function - one for contract deployment and one for ownership transfer. Index the deployment address and new owner address.

# [Qa-06] Missing Events in SystemContract

## Impact

The `depositAndCall` function in the SystemContract contract used to deposit tokens and invoke ZEVM contract calls is missing event emissions. Events allow tracking transactions off-chain which is important for auditability and transparency. Without events, it would be difficult to monitor these cross-chain interactions.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L79
```solidity

```

## Recommended Mitigation Steps

Consider emitting a `TokenDepositedAndContractCalled` event in `depositAndCall` function to record token deposit and contract call details for each cross-chain interaction.

# [Qa-07] Missing Events in WZETA Contract  

## Impact

The fallback function in WZETA contract allowing ETH deposits is missing event emissions. Events allow tracking transactions off-chain which is important for auditability and transparency. Without events, it would be difficult to monitor ETH deposits through the fallback function.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L16-L18
```solidity
    function() public payable {
        deposit();
    }
```

## Recommended Mitigation Steps

Consider emitting a Deposit event in the fallback function to record ETH deposits.

# [Qa-08] Missing Events in WZETA Contract

## Impact

The deposit function in WZETA contract used for ETH deposits is missing event parameter indexing. Indexing event parameters allows for easier filtering and parsing of logs.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L20-L23
```solidity
    function deposit() public payable {
        balanceOf[msg.sender] += msg.value;
        Deposit(msg.sender, msg.value);
    }
```

## Recommended Mitigation Steps

Consider indexing the event parameters sender and value in Deposit event emitted from deposit function.

# [Qa-09] Missing Events in WZETA Contract

## Impact 

The withdraw function in WZETA contract used for ETH withdrawals is missing event parameter indexing. Indexing event parameters allows for easier filtering and parsing of logs.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L25-L30
```solidity
    function withdraw(uint wad) public {
        require(balanceOf[msg.sender] >= wad);
        balanceOf[msg.sender] -= wad;
        msg.sender.transfer(wad);
        Withdrawal(msg.sender, wad);
    }
```

## Recommended Mitigation Steps

Consider indexing the event parameters sender and value in Withdrawal event emitted from withdraw function.

# [Qa-10] Missing Events in WZETA Contract  

## Impact

The approve function in WZETA contract used for token allowance management is missing event parameter indexing. Indexing event parameters allows for easier filtering and parsing of logs. 

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36-L40
```solidity
    function approve(address guy, uint wad) public returns (bool) {
        allowance[msg.sender][guy] = wad;
        Approval(msg.sender, guy, wad);
        return true;
    }
```

## Recommended Mitigation Steps 

Consider indexing the event parameters sender, spender and value in Approval event emitted from approve function.

# [Qa-11] Missing Events in WZETA Contract

## Impact

The transfer function in WZETA contract invoking `transferFrom` is missing event emissions. Events allow tracking token transfers off-chain which is important for auditability and transparency.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L42-L44
```solidity
    function transfer(address dst, uint wad) public returns (bool) {
        return transferFrom(msg.sender, dst, wad);
    }
```

## Recommended Mitigation Steps

Consider emitting Transfer event in transfer function or utilize the Transfer event emitted by `transferFrom` function.

# [Qa-12] 

# [Qa-13] Missing Events in ZetaConnectorBase Contract  

## Impact

The pause function in `ZetaConnectorBase` contract used to pause connector operations is missing event emissions. Events allow tracking access control changes off-chain which is important for auditability and transparency. Without events, it would be difficult to monitor pauses in connector operations.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L151-L153
```solidity
    function pause() external onlyPauser {
        _pause();
    }
```

## Recommended Mitigation Steps

Consider emitting a Paused event in the pause function to record connector pauses. Pass relevant details like pauser address.

# [Qa-14] Missing Events in ZEVMSwapApp Contract

## Impact

The `onCrossChainCall` function in `ZEVMSwapApp` contract used for inter-chain token swaps is missing event emissions and parameter indexing. Events allow tracking transactions off-chain which is important for auditability and transparency. Without properly indexed and detailed events, it would be difficult to monitor these swaps.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/node/contrib/localnet/orchestrator/smoketest/contracts/zevmswap/ZEVMSwapApp.sol#L88-L109
```solidity
    function onCrossChainCall(Context calldata, address zrc20, uint256 amount, bytes calldata message) external override {
        if (msg.sender != systemContract) {
            revert InvalidSender();
        }
        address targetZRC20;
        bytes memory recipient;
        (targetZRC20, recipient) = decodeMemo(message);
        address[] memory path;
        path = new address[](2);
        path[0] = zrc20;
        path[1] = targetZRC20;
        // Approve the usage of this token by router02
        IZRC20(zrc20).approve(address(router02), amount);
        // Swap for your target token
        uint256[] memory amounts = IUniswapV2Router02(router02).swapExactTokensForTokens(amount, 0, path, address(this), _DEADLINE);


        // this contract subsides withdraw gas fee
        (address gasZRC20Addr,uint256 gasFee) = IZRC20(targetZRC20).withdrawGasFee();
        IZRC20(gasZRC20Addr).approve(address(targetZRC20), gasFee);
        IZRC20(targetZRC20).approve(address(targetZRC20), amounts[1]); // this does not seem to be necessary
        IZRC20(targetZRC20).withdraw(recipient, amounts[1]-gasFee);
    }
```

## Recommended Mitigation Steps  

Consider emitting a `TokenSwapped` event in `onCrossChainCall` function with indexed parameters for input token, output token, amounts and recipient details.   

# [Qa-15] Missing Events in Vault Contract 

## Impact



## Recommended Mitigation Steps



# [Qa-16] Missing Events in Vault Contract

## Impact 



```solidity

```

## Recommended Mitigation Steps 


# [Qa-17] Incorrect Return Type in ZetaTokenConsumerUniV2 Contract

## Impact

The `hasZetaLiquidity` function specifies the returns keyword but there is no return statement. This forces a default bool value to be returned even if invalid.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162-L172
```solidity
    function hasZetaLiquidity() external view override returns (bool) {
        address[] memory path = new address[](2);
        path[0] = wETH;
        path[1] = zetaToken;


        try uniswapV2Router.getAmountsOut(1, path) returns (uint256[] memory amounts) {
            return amounts[path.length - 1] > 0;
        } catch {
            return false;
        }
    }
```

## Recommended Mitigation Steps  

Remove the returns keyword since a return value is not needed.

# [Qa-18] Event-Based Reentrancy in  ZetaConnectorNonEth Contract

## Impact

The send function performs the external zeta token burn after emitting `ZetaSent` event. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40-L53
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

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission after external call. Additionally use reentrancy guard.

# [Qa-19] Event-Based Reentrancy in ZetaConnectorNonEth Contract  

## Impact  

The `onReceive` function performs the external zeta token mint and contract call after emitting `ZetaReceived` event. This exposes the function to event-based reentrancy vulnerability. 

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79
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

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission after external call. Additionally use reentrancy guard.  

# [Qa-20] Event-Based Reentrancy in ZetaConnectorNonEth Contract

## Impact   

The `onRevert` function performs the external zeta token mint and contract call after emitting ZetaReverted event. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122
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


        emit ZetaReverted(
            zetaTxSenderAddress,
            sourceChainId,
            destinationChainId,
            destinationAddress,
            remainingZetaValue,
            message,
            internalSendHash
        );
    }
```

## Recommended Mitigation Steps  

Apply checks-effects-interactions pattern by moving event emission after external call. Additionally use reentrancy guard.

# [Qa-21] Event-Based Reentrancy in ZetaTokenConsumerPancakeV3 Contract 

## Impact  

The `getZetaFromToken` function performs external calls to Pancake router contract after emitting `TokenExchangedForZeta` event. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149
```solidity
    function getZetaFromToken(
        address destinationAddress,
        uint256 minAmountOut,
        address inputToken,
        uint256 inputTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (inputTokenAmount == 0) revert InputCantBeZero();


        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);


        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
            recipient: destinationAddress,
            amountIn: inputTokenAmount,
            amountOutMinimum: minAmountOut
        });


        uint256 amountOut = pancakeV3Router.exactInput(params);


        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
        return amountOut;
    }
```

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission after external call. Additionally use reentrancy guard.

# [Qa-22] Event-Based Reentrancy in ZetaTokenConsumerPancakeV3 Contract

## Impact   

The `getEthFromZeta` function performs external calls for unwrapping WETH and sending ETH after emitting `ZetaExchangedForEth` event. This exposes the function to event-based reentrancy vulnerability.  

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182
```solidity
    function getEthFromZeta(
        address destinationAddress,
        uint256 minAmountOut,
        uint256 zetaTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (zetaTokenAmount == 0) revert InputCantBeZero();


        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);


        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
            tokenIn: zetaToken,
            tokenOut: WETH9Address,
            fee: zetaPoolFee,
            recipient: address(this),
            amountIn: zetaTokenAmount,
            amountOutMinimum: minAmountOut,
            sqrtPriceLimitX96: 0
        });


        uint256 amountOut = pancakeV3Router.exactInputSingle(params);


        WETH9(WETH9Address).withdraw(amountOut);


        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);


        (bool sent, ) = destinationAddress.call{value: amountOut}("");
        if (!sent) revert ErrorSendingETH();


        return amountOut;
    }
```

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission after external call. Additionally use reentrancy guard.  

# [Qa-23] Event-Based Reentrancy in ZetaConnectorZEVM Contract  

## Impact

The `send` function performs external calls to transfer wZETA and ETH after emitting `ZetaSent` event. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92-L108
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

## Recommended Mitigation Steps 

Apply checks-effects-interactions pattern by moving event emission after external calls. Additionally use reentrancy guard.

# [Qa-24] Event-Based Reentrancy in ZetaTokenConsumerUniV2 Contract 

## Impact  

The `getZetaFromToken` function performs external calls to UniswapV2 router contract after emitting `TokenExchangedForZeta` event. This exposes the function to event-based reentrancy vulnerability.  

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L93
```solidity
    function getZetaFromToken(
        address destinationAddress,
        uint256 minAmountOut,
        address inputToken,
        uint256 inputTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (inputTokenAmount == 0) revert InputCantBeZero();


        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);


        address[] memory path;
        if (inputToken == wETH) {
            path = new address[](2);
            path[0] = wETH;
            path[1] = zetaToken;
        } else {
            path = new address[](3);
            path[0] = inputToken;
            path[1] = wETH;
            path[2] = zetaToken;
        }


        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
            inputTokenAmount,
            minAmountOut,
            path,
            destinationAddress,
            block.timestamp + MAX_DEADLINE
        );
        uint256 amountOut = amounts[path.length - 1];


        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
        return amountOut;
    }
```

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission after external calls. Additionally use reentrancy guard.

# [Qa-25] Event-Based Reentrancy in ZetaTokenConsumerUniV2 Contract

## Impact  

The `getEthFromZeta` function performs external calls for unwrapping WETH and sending ETH after emitting `ZetaExchangedForEth` event. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L122
```solidity
    function getEthFromZeta(
        address destinationAddress,
        uint256 minAmountOut,
        uint256 zetaTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (zetaTokenAmount == 0) revert InputCantBeZero();


        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);


        address[] memory path = new address[](2);
        path[0] = zetaToken;
        path[1] = wETH;


        uint256[] memory amounts = uniswapV2Router.swapExactTokensForETH(
            zetaTokenAmount,
            minAmountOut,
            path,
            destinationAddress,
            block.timestamp + MAX_DEADLINE
        );


        uint256 amountOut = amounts[path.length - 1];


        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
        return amountOut;
    }
```

## Recommended Mitigation Steps   

Apply checks-effects-interactions pattern by moving event emission after external calls. Additionally use reentrancy guard.

# [Qa-26] Event-Based Reentrancy in ZetaTokenConsumerUniV2 Contract  

## Impact

The `getTokenFromZeta` function performs external calls to UniswapV2 router contract after emitting `ZetaExchangedForToken` event. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L160
```solidity
    function getTokenFromZeta(
        address destinationAddress,
        uint256 minAmountOut,
        address outputToken,
        uint256 zetaTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (zetaTokenAmount == 0) revert InputCantBeZero();


        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);


        address[] memory path;
        if (outputToken == wETH) {
            path = new address[](2);
            path[0] = zetaToken;
            path[1] = wETH;
        } else {
            path = new address[](3);
            path[0] = zetaToken;
            path[1] = wETH;
            path[2] = outputToken;
        }


        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
            zetaTokenAmount,
            minAmountOut,
            path,
            destinationAddress,
            block.timestamp + MAX_DEADLINE
        );


        uint256 amountOut = amounts[path.length - 1];


        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
        return amountOut;
    }
```

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission after external calls. Additionally use reentrancy guard.

# [Qa-27] Event-Based Reentrancy in `ZetaTokenConsumerTriden`t Contract   

## Impact  

The `getZetaFromToken` function performs external calls to Trident router contract after emitting `TokenExchangedForZeta` event. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L134
```solidity
    function getZetaFromToken(
        address destinationAddress,
        uint256 minAmountOut,
        address inputToken,
        uint256 inputTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (inputTokenAmount == 0) revert InputCantBeZero();


        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);


        (address token0, address token1) = getPair(inputToken, WETH9Address);
        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);


        (token0, token1) = getPair(WETH9Address, zetaToken);
        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);


        address[] memory path = new address[](2);
        path[0] = pairPools1[0];
        path[1] = pairPools2[0];


        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
            tokenIn: inputToken,
            amountIn: inputTokenAmount,
            amountOutMinimum: minAmountOut,
            path: path,
            to: destinationAddress,
            unwrap: false
        });


        uint256 amountOut = tridentRouter.exactInput(params);


        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
        return amountOut;
    }
```

## Recommended Mitigation Steps  

Apply checks-effects-interactions pattern by moving event emission after external calls. Additionally use reentrancy guard.

# [Qa-28] Event-Based Reentrancy in ZetaTokenConsumerTrident Contract

## Impact  

The `getEthFromZeta` function performs external calls for unwrapping WETH after emitting `ZetaExchangedForEth` event. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L164
```solidity
    function getEthFromZeta(
        address destinationAddress,
        uint256 minAmountOut,
        uint256 zetaTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (zetaTokenAmount == 0) revert InputCantBeZero();


        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);


        (address token0, address token1) = getPair(zetaToken, WETH9Address);
        address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);


        IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
            tokenIn: zetaToken,
            amountIn: zetaTokenAmount,
            amountOutMinimum: minAmountOut,
            pool: pairPools[0],
            to: destinationAddress,
            unwrap: true
        });


        uint256 amountOut = tridentRouter.exactInputSingle(params);


        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);


        return amountOut;
    }
```

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission after external calls. Additionally use reentrancy guard.

# [Qa-29] Event-Based Reentrancy in ZetaConnectorEth Contract   

## Impact

The `send` function emits `ZetaSent` event before transferring tokens. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31-L45
```solidity
    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
        bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas);
        if (!success) revert ZetaTransferError();


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

## Recommended Mitigation Steps  

Apply checks-effects-interactions pattern by moving event emission after token transfer. Additionally use reentrancy guard.

# [Qa-30] Event-Based Reentrancy in ZetaConnectorEth Contract

## Impact  

The `onReceive` function emits `ZetaReceived` event before transferring tokens. This exposes the function to event-based reentrancy vulnerability. 

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70
```solidity
    function onReceive(
        bytes calldata zetaTxSenderAddress,
        uint256 sourceChainId,
        address destinationAddress,
        uint256 zetaValue,
        bytes calldata message,
        bytes32 internalSendHash
    ) external override onlyTssAddress {
        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
        if (!success) revert ZetaTransferError();


        if (message.length > 0) {
            ZetaReceiver(destinationAddress).onZetaMessage(
                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
            );
        }


        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
    }
```

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission after token transfer. Additionally use reentrancy guard.  

# [Qa-31] Event-Based Reentrancy in ZetaConnectorEth Contract  

## Impact

The `onRevert` function emits `ZetaReverted` event before transferring tokens. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111
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
        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
        if (!success) revert ZetaTransferError();


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


        emit ZetaReverted(
            zetaTxSenderAddress,
            sourceChainId,
            destinationChainId,
            destinationAddress,
            remainingZetaValue,
            message,
            internalSendHash
        );
    }
```

## Recommended Mitigation Steps   

Apply checks-effects-interactions pattern by moving event emission after token transfer. Additionally use reentrancy guard.

# [Qa-32] Event-Based Reentrancy in ZRC20 Contract  

## Impact   

The `withdraw` function emits event after transferring gas fee token. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256-L264
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

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission prior to token transfer. Additionally use reentrancy guard.

# [Qa-33] Event-Based Reentrancy in ZetaTokenConsumerUniV3 Contract

## Impact  

The `getZetaFromToken` function performs external calls to UniswapV3 router contract after emitting `TokenExchangedForZeta` event. This exposes the function to event-based reentrancy vulnerability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L122
```solidity
    function getZetaFromToken(
        address destinationAddress,
        uint256 minAmountOut,
        address inputToken,
        uint256 inputTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (inputTokenAmount == 0) revert InputCantBeZero();


        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);


        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
            deadline: block.timestamp + MAX_DEADLINE,
            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
            recipient: destinationAddress,
            amountIn: inputTokenAmount,
            amountOutMinimum: minAmountOut
        });


        uint256 amountOut = uniswapV3Router.exactInput(params);


        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
        return amountOut;
    }
```

## Recommended Mitigation Steps

Apply checks-effects-interactions pattern by moving event emission after external calls. Additionally use reentrancy guard.

# [Qa-34] Event-Based Reentrancy in ZetaTokenConsumerUniV3 Contract  

## Impact

The `getEthFromZeta` function performs external calls for unwrapping WETH and sending ETH after emitting `ZetaExchangedForEth` event. This exposes the function to event-based reentrancy vulnerability.  

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L156
```solidity
    function getZetaFromToken(
        address destinationAddress,
        uint256 minAmountOut,
        address inputToken,
        uint256 inputTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (inputTokenAmount == 0) revert InputCantBeZero();


        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);


        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
            deadline: block.timestamp + MAX_DEADLINE,
            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
            recipient: destinationAddress,
            amountIn: inputTokenAmount,
            amountOutMinimum: minAmountOut
        });


        uint256 amountOut = uniswapV3Router.exactInput(params);


        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
        return amountOut;
    }
```

## Recommended Mitigation Steps  

Apply checks-effects-interactions pattern by moving event emission after external calls. Additionally use reentrancy guard.

# [NC-35] Missing Payable Modifier in ZetaTokenConsumerPancakeV3 Contract  

## Impact  

The `getEthFromZeta` function uses a .call() method to send Ether but is not marked payable. This would fail if contract's balance is empty.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L156
```solidity
    function getEthFromZeta(
        address destinationAddress,
        uint256 minAmountOut,
        uint256 zetaTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (zetaTokenAmount == 0) revert InputCantBeZero();


        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);


        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
            deadline: block.timestamp + MAX_DEADLINE,
            tokenIn: zetaToken,
            tokenOut: WETH9Address,
            fee: zetaPoolFee,
            recipient: address(this),
            amountIn: zetaTokenAmount,
            amountOutMinimum: minAmountOut,
            sqrtPriceLimitX96: 0
        });


        uint256 amountOut = uniswapV3Router.exactInputSingle(params);


        WETH9(WETH9Address).withdraw(amountOut);


        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);


        (bool sent, ) = destinationAddress.call{value: amountOut}("");
        if (!sent) revert ErrorSendingETH();


        return amountOut;
    }
```

## Recommended Mitigation Steps   

Mark the getEthFromZeta function as payable since it sends Ether via .call() method.

# [NC-36] Missing Payable Modifier in ZetaConnectorZEVM Contract

## Impact 

The send function uses a `.call()` method to send Ether but is not marked `payable`. This would fail if contract's balance is empty.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96-L96
```solidity
(bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```

## Recommended Mitigation Steps  

Mark the send function as `payable` since it sends Ether via `.call()` method.

# [NC-37] Missing Payable Modifier in ZetaTokenConsumerUniV3 Contract

## Impact  

The `getEthFromZeta `function uses a .call() method to send Ether but is not marked payable. This would fail if contract's balance is empty.

https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152-L152
```solidity
        (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

## Recommended Mitigation Steps  

Mark the `getEthFromZeta` function as payable since it sends Ether via .call() method.

# [NC-38] CREATE2 Redeploy Attack in ImmutableCreate2Factory

## Impact  

The `CREATE2` opcode usage can enable attackers to deploy malicious code by reusing previously deployed addresses.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L57-L63
```solidity
            deploymentAddress := create2(
                // call CREATE2 with 4 arguments.
                callvalue, // forward any attached value.
                encoded_data, // pass in initialization code.
                encoded_size, // pass in init code's length.
                salt // pass in the salt value.
            )
```

## Recommended Mitigation Steps   

Ensure proper access control validations before `CREATE2` deployment. This usage seems to be an intended feature.

# [NC-39] Missing Interface Inheritance in ZetaConnectorNonEth  

## Impact   

`ZetaConnectorNonEth` implements the ZetaConnector interface but does not explicitly derive from it. This could lead to unintended behavior.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15-L123
```solidity
contract ZetaConnectorNonEth is ZetaConnectorBase {
    uint256 public maxSupply = 2 ** 256 - 1;


    event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);


    constructor(
        address zetaTokenAddress_,
        address tssAddress_,
        address tssAddressUpdater_,
        address pauserAddress_
    ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}


    function getLockedAmount() external view returns (uint256) {
        return ZetaNonEthInterface(zetaToken).balanceOf(address(this));
    }


    function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
        maxSupply = maxSupply_;
        emit MaxSupplyUpdated(msg.sender, maxSupply_);
    }


    /**
     * @dev Entry point to send data to protocol
     * This call burn the token and emit an event with all the data needed by the protocol
     */
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


    /**
     * @dev Handler to receive data from other chain.
     * This method can be called only by TSS.
     * Transfer the Zeta tokens to destination and calls onZetaMessage if it's needed.
     * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
     */
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


    /**
     * @dev Handler to receive errors from other chain.
     * This method can be called only by TSS.
     * Transfer the Zeta tokens to destination and calls onZetaRevert if it's needed.
     * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
     */
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


        emit ZetaReverted(
            zetaTxSenderAddress,
            sourceChainId,
            destinationChainId,
            destinationAddress,
            remainingZetaValue,
            message,
            internalSendHash
        );
    }
}
```

## Recommended Mitigation Steps  

Derive `ZetaConnectorNonEth` contract from ZetaConnector interface.

# [NC-40] Missing Interface Inheritance in ERC20Custody

## Impact  

`ERC20Custody` implements the ERC20Custody interface but does not explicitly derive from it. This could lead to unintended behavior.  

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11-L200
```solidity
contract ERC20Custody is ReentrancyGuard {
    using SafeERC20 for IERC20;


    error NotWhitelisted();
    error NotPaused();
    error InvalidSender();
    error InvalidTSSUpdater();
    error ZeroAddress();
    error IsPaused();
    error ZetaMaxFeeExceeded();
    error ZeroFee();


    /// @notice If custody operations are paused.
    bool public paused;
    /// @notice TSSAddress is the TSS address collectively possessed by Zeta blockchain validators.
    address public TSSAddress;
    /// @notice Threshold Signature Scheme (TSS) [GG20] is a multi-sig ECDSA/EdDSA protocol.
    address public TSSAddressUpdater;
    /// @notice Current zeta fee for depositing funds into ZetaChain.
    uint256 public zetaFee;
    /// @notice Maximum zeta fee for transaction.
    uint256 public immutable zetaMaxFee;
    /// @notice Zeta ERC20 token .
    IERC20 public immutable zeta;
    /// @notice Mapping of whitelisted token => true/false.
    mapping(IERC20 => bool) public whitelisted;


    event Paused(address sender);
    event Unpaused(address sender);
    event Whitelisted(IERC20 indexed asset);
    event Unwhitelisted(IERC20 indexed asset);
    event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);
    event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);
    event RenouncedTSSUpdater(address TSSAddressUpdater_);
    event UpdatedTSSAddress(address TSSAddress_);
    event UpdatedZetaFee(uint256 zetaFee_);


    /**
     * @dev Only TSS address allowed modifier.
     */
    modifier onlyTSS() {
        if (msg.sender != TSSAddress) {
            revert InvalidSender();
        }
        _;
    }


    /**
     * @dev Only TSS address updater allowed modifier.
     */
    modifier onlyTSSUpdater() {
        if (msg.sender != TSSAddressUpdater) {
            revert InvalidTSSUpdater();
        }
        _;
    }


    constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
        TSSAddress = TSSAddress_;
        TSSAddressUpdater = TSSAddressUpdater_;
        zetaFee = zetaFee_;
        zeta = zeta_;
        zetaMaxFee = zetaMaxFee_;
    }


    /**
     * @dev Update the TSSAddress in case of Zeta blockchain validator nodes churn.
     * @param TSSAddress_, new tss address.
     */
    function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {
        if (TSSAddress_ == address(0)) {
            revert ZeroAddress();
        }
        TSSAddress = TSSAddress_;
        emit UpdatedTSSAddress(TSSAddress_);
    }


    /**
     * @dev Update zeta fee
     * @param zetaFee_, new zeta fee
     */
    function updateZetaFee(uint256 zetaFee_) external onlyTSS {
        if (zetaFee_ == 0) {
            revert ZeroFee();
        }
        if (zetaFee_ > zetaMaxFee) {
            revert ZetaMaxFeeExceeded();
        }
        zetaFee = zetaFee_;
        emit UpdatedZetaFee(zetaFee_);
    }


    /**
     * @dev Change the ownership of TSSAddressUpdater to the Zeta blockchain TSS nodes.
     * Effectively, only Zeta blockchain validators collectively can update TSSAddress afterwards.
     */
    function renounceTSSAddressUpdater() external onlyTSSUpdater {
        if (TSSAddress == address(0)) {
            revert ZeroAddress();
        }
        TSSAddressUpdater = TSSAddress;
        emit RenouncedTSSUpdater(msg.sender);
    }


    /**
     * @dev Pause custody operations.
     */
    function pause() external onlyTSS {
        if (paused) {
            revert IsPaused();
        }
        if (TSSAddress == address(0)) {
            revert ZeroAddress();
        }
        paused = true;
        emit Paused(msg.sender);
    }


    /**
     * @dev Unpause custody operations.
     */
    function unpause() external onlyTSS {
        if (!paused) {
            revert NotPaused();
        }
        paused = false;
        emit Unpaused(msg.sender);
    }


    /**
     * @dev Whitelist asset.
     * @param asset, ERC20 asset.
     */
    function whitelist(IERC20 asset) external onlyTSS {
        whitelisted[asset] = true;
        emit Whitelisted(asset);
    }


    /**
     * @dev Unwhitelist asset.
     * @param asset, ERC20 asset.
     */
    function unwhitelist(IERC20 asset) external onlyTSS {
        whitelisted[asset] = false;
        emit Unwhitelisted(asset);
    }


    /**
     * @dev Deposit asset amount to recipient with message that encodes additional zetachain evm call or message.
     * @param recipient, recipient address.
     * @param asset, ERC20 asset.
     * @param amount, asset amount.
     * @param message, bytes message or encoded zetechain call.
     */
    function deposit(
        bytes calldata recipient,
        IERC20 asset,
        uint256 amount,
        bytes calldata message
    ) external nonReentrant {
        if (paused) {
            revert IsPaused();
        }
        if (!whitelisted[asset]) {
            revert NotWhitelisted();
        }
        if (zetaFee != 0 && address(zeta) != address(0)) {
            zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
        }
        uint256 oldBalance = asset.balanceOf(address(this));
        asset.safeTransferFrom(msg.sender, address(this), amount);
        // In case if there is a fee on a token transfer, we might not receive a full exepected amount
        // and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount.
        emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
    }


    /**
     * @dev Withdraw asset amount to recipient by custody TSS owner.
     * @param recipient, recipient address.
     * @param asset, ERC20 asset.
     * @param amount, asset amount.
     */
    function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
        if (!whitelisted[asset]) {
            revert NotWhitelisted();
        }
        IERC20(asset).safeTransfer(recipient, amount);
        emit Withdrawn(recipient, asset, amount);
    }
}
```

## Recommended Mitigation Steps

Derive `ERC20Custody` contract from ERC20Custody interface.

# [NC-41] Missing Interface Inheritance in ZetaConnectorEth  

## Impact  

`ZetaConnectorEth` implements the ZetaConnector interface but does not explicitly derive from it. This could lead to unintended behavior.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15-L112
```solidity
contract ZetaConnectorEth is ZetaConnectorBase {
    constructor(
        address zetaToken_,
        address tssAddress_,
        address tssAddressUpdater_,
        address pauserAddress_
    ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}


    function getLockedAmount() external view returns (uint256) {
        return IERC20(zetaToken).balanceOf(address(this));
    }


    /**
     * @dev Entrypoint to send data through ZetaChain
     * This call locks the token on the contract and emits an event with all the data needed by the protocol.
     */
    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
        bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas);
        if (!success) revert ZetaTransferError();


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


    /**
     * @dev Handler to receive data from other chain.
     * This method can be called only by TSS.
     * Transfers the Zeta tokens to destination and calls onZetaMessage if it's needed.
     */
    function onReceive(
        bytes calldata zetaTxSenderAddress,
        uint256 sourceChainId,
        address destinationAddress,
        uint256 zetaValue,
        bytes calldata message,
        bytes32 internalSendHash
    ) external override onlyTssAddress {
        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
        if (!success) revert ZetaTransferError();


        if (message.length > 0) {
            ZetaReceiver(destinationAddress).onZetaMessage(
                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
            );
        }


        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
    }


    /**
     * @dev Handler to receive errors from other chain.
     * This method can be called only by TSS.
     * Transfers the Zeta tokens to destination and calls onZetaRevert if it's needed.
     */
    function onRevert(
        address zetaTxSenderAddress,
        uint256 sourceChainId,
        bytes calldata destinationAddress,
        uint256 destinationChainId,
        uint256 remainingZetaValue,
        bytes calldata message,
        bytes32 internalSendHash
    ) external override whenNotPaused onlyTssAddress {
        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
        if (!success) revert ZetaTransferError();


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


        emit ZetaReverted(
            zetaTxSenderAddress,
            sourceChainId,
            destinationChainId,
            destinationAddress,
            remainingZetaValue,
            message,
            internalSendHash
        );
    }
}
```

## Recommended Mitigation Steps

Derive `ZetaConnectorEth` contract from ZetaConnector interface.  

# [NC-42] Missing Underscore Convention in ZetaInteractor

## Impact  

The `currentChainId` variable does not follow Solidity naming convention by missing underscore prefix. This reduces readability.  

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11-L11
```solidity
uint256 internal immutable currentChainId;
```

## Recommended Mitigation Steps

Prefix the variable with underscore - `_currentChainId`

# [NC-43] Missing Underscore Convention in ZetaTokenConsumerPancakeV3  

## Impact   

The `MAX_DEADLINE` constant does not follow Solidity naming convention by missing underscore prefix. This reduces readability.

https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58-L58
```solidity
    uint256 internal constant MAX_DEADLINE = 200;
```

## Recommended Mitigation Steps  

Prefix the constant with underscore - `_MAX_DEADLINE`  

# [NC-44] Missing Underscore Convention in ImmutableCreate2Factory  

## Impact

Multiple variables in `safeCreate2Internal` function do not follow Solidity naming


https://github.com//code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L26-L74
```solidity
    function safeCreate2Internal(
        bytes32 salt,
        bytes memory initializationCode
    ) internal returns (address deploymentAddress) {
        // move the initialization code from calldata to memory.
        bytes memory initCode = initializationCode;


        // determine the target address for contract deployment.
        address targetDeploymentAddress = address(
            uint160( // downcast to match the address type.
                uint256( // convert to uint to truncate upper digits.
                    keccak256( // compute the CREATE2 hash using 4 inputs.
                        abi.encodePacked( // pack all inputs to the hash together.
                            hex"ff", // start with 0xff to distinguish from RLP.
                            address(this), // this contract will be the caller.
                            salt, // pass in the supplied salt value.
                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
                        )
                    )
                )
            )
        );


        // ensure that a contract hasn't been previously deployed to target address.
        require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");


        // using inline assembly: load data and length of data, then call CREATE2.
        assembly {
            // solhint-disable-line
            let encoded_data := add(0x20, initCode) // load initialization code.
            let encoded_size := mload(initCode) // load the init code's length.
            deploymentAddress := create2(
                // call CREATE2 with 4 arguments.
                callvalue, // forward any attached value.
                encoded_data, // pass in initialization code.
                encoded_size, // pass in init code's length.
                salt // pass in the salt value.
            )
        }


        // check address against target to ensure that deployment was successful.
        require(
            deploymentAddress == targetDeploymentAddress,
            "Failed to deploy contract using provided salt and initialization code."
        );


        // record the deployment of the contract to prevent redeploys.
        _deployed[deploymentAddress] = true;
    }
```
