## QA

### L-01 - Unfulfilled TODO comments in the hasZetaLiquidity() in the ZetaTokenConsumerTrident.strategy.sol

hasZetaLiquidity() has an incomplete implementation by the devs. The function does not account for the pool address and there is no means to check for liquidity.

#### Impact
When the hasZetaLiquidity() is called it does not check for the liquidity it is supposed to return in the ZetaTokenConsumerTrident.strategy.sol therefore it will always return false.

#### Proof Of Concept
```solidity
  function hasZetaLiquidity() external view override returns (bool) {
        //@TODO: Implement
        return false;
    }
```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L206

#### Recommended Mitigation Steps
Implement the correct function content in the hasZetaLiquidity().


### L-02 - Lack of address zero checks in the ERC20Custody.sol constructor

The TssAddress, the TssAddressUpdater and the zeta address were not validated in the constructor. The deployer can in error set any of the addresses to address zero which can potentially lead to loss of funds if users begin depositing.

#### Impact
The TssAddress, the TssAddressUpdsater and the zeta address were assigned to the value of the constructor input parameter, but this parameter is not checked before this to know if the parameter passed in is zero.

#### Proof Of Concept
```solidity
   constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
        TSSAddress = TSSAddress_;
        TSSAddressUpdater = TSSAddressUpdater_;
        zetaFee = zetaFee_;
        zeta = zeta_;
        zetaMaxFee = zetaMaxFee_;
    }
```
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74

#### Recommended Mitigation Steps
Make sure you add zero address checks on the input parameter before initializing the variable to ensure that users do not lose funds.


### L-03 - Lack of deadline in the struct called in PancakeV3.

The ISwapRouterPancake.ExactInputSingleParams used in the ZetaTokenConsumerPancakeV3.strategy.sol does not have a deadline currently thereby making all swap transactions calls to PancakeV3 revert.

From the PancakeV3 docs;
https://docs.pancakeswap.finance/developers/smart-contracts/pancakeswap-exchange/v3-contracts
We see that the router has a similar structure to UniswapV3 router and the ISwapRouterPancake.ExactInputSingleParams() struct has a deadline variable. After further research we discovered that the router being used here is the smart router not the PancakeV3 swap router

#### Proof Of Concept
```solidity
  function getZetaFromEth(
        address destinationAddress,
        uint256 minAmountOut
    ) external payable override returns (uint256) {
        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (msg.value == 0) revert InputCantBeZero();


        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
            tokenIn: WETH9Address,
            tokenOut: zetaToken,
            fee: zetaPoolFee,
            recipient: destinationAddress,
            amountIn: msg.value,
            amountOutMinimum: minAmountOut,
            sqrtPriceLimitX96: 0
        });
```

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
```

#### Recommended Mitigation Steps
The getZetaFromEth() and getEthFromZeta() should accept a user input deadline parameter that should be passed along to ISwapRouterPancake.ExactInputSingleParams() to ensure it works.


### L-04 - TssAddressUpdater is not updated if the updater has been renounced.

When the renounceTssAddressUpdater is called, it is meant to renounce the current TssAddressUpdater and it updates the current TssAddress but after updating it if the TssAddress is ever updated at a future time, it only updates the TssAddress instead of both the TssAddress and the TssAddressUpdater since it has been renounced.

#### Impact
The ownership of the TssAddressUpdater is not going to be updated if the updater is renounced when the updateTssAndConnectorAddresses() is called.

#### Proof Of Concept
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40-L49
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L54-L60

```solidity
   function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {
        if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);
        if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();


        tssAddress = tssAddress_;
        connectorAddress = connectorAddress_;


        emit TSSAddressUpdated(msg.sender, tssAddress_);
        emit ConnectorAddressUpdated(msg.sender, connectorAddress_);
    }
```

```solidity
   function renounceTssAddressUpdater() external {
        if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);
        if (tssAddress == address(0)) revert InvalidAddress();


        tssAddressUpdater = tssAddress;
        emit TSSAddressUpdaterUpdated(msg.sender, tssAddress);
    }
```

#### Recommended Mitigation Steps
Update the updateTssAndConnectorAddresses() to atomically update the TssAddressUpdater if it has been originally renounced.


### L-05 - Any user can burn their own tokens in the Zeta.non-eth.sol

Zeta.non-eth.sol inherits from ERC20Burnable which provides a function burnFrom allowing only a connector to burn tokens but as a side effect due to the inheritance from ERC20Burnable anyone can burn their own tokens.

#### Impact
This is a violation of the dev’s assumption as seen in the comment.

#### Proof Of Concept
```solidity
   function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
        /**
         * @dev Only Connector can burn.
         */
        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);


        ERC20Burnable.burnFrom(account, amount);


        emit Burnt(account, amount);
    }
```

#### Recommended Mitigation Steps
Override the public burn function as well to prevent users from burning their own tokens.


### L-06 - Get locked amount will always return zero.

#### Impact
The function getLockedAmount will always return zero because it does not lock tokens, instead it mints and burns tokens on deposit or withdrawals.

#### Proof Of Concept
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27-L29
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40-L53
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122


```solidity
  function getLockedAmount() external view returns (uint256) {
        return ZetaNonEthInterface(zetaToken).balanceOf(address(this));
    }
```

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

#### Recommended Mitigation Steps
Remove the function from the contract as it will never return any value greater than zero.
Alternatively, you can implement an int256 state variable to keep track of the tokens burnt or minted.


### L-07 - Total Supply check in the onRevert can DOS some users.

When cross chain token transfers fail the onRevert method is called to inform users, however the total supply is checked since minting occurs. In cases where fresh new minters have received tokens from other chains which exceeds the total supply users with failed transfers will not be able to get their tokens reverted to them

#### Impact
Although the total supply is malleable, it is controlled by a multi-sig and therefore will require some time to actually increase to a new total supply which will allow the user to get their tokens on revert.

#### Proof Of Concept
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122

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

#### Recommended Mitigation Steps
Only check for max supply when bringing in new tokens for users to that chain, remove the check for the onRevert() to allow users get their tokens even after supply is temporarily full.
