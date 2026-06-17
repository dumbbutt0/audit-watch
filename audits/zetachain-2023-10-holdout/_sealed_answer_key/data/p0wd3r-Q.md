# Repeatedly called code

This line duplicates the call to `RemoveInTxTrackerIfExists` in `defer`.
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L241
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L123-L129

The `chain == nil` decision is duplicated here.
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_gas_price.go#L129-L137

Here, the range of `confirmedBlockNum` is checked twice for duplication.
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/bitcoin_client.go#L332-L335
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/bitcoin_client.go#L210-L218

Here, the same getter is executed three times in succession.
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/bitcoin_client.go#L416-L435

# Prints logs without determining the `to` of the donation transaction

This loop iterates through all the transactions in the block, determining whether they are donations or not is not interpreting whether the `to` address is the project address.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L943-L952
```go
			for _, tx := range block.Transactions() {
				if tx.To() == nil {
					continue
				}
				if bytes.Compare(tx.Data(), []byte(DonationMessage)) == 0 {
					ob.logger.ExternalChainWatcher.Info().Msgf("thank you rich folk for your donation!: %s", tx.Hash().Hex())
					continue
				}

				if *tx.To() == tssAddress {
```

# Events are never triggered

The transferFrom of ZETA, WZETA and ZRC20 will always return true, so the events in the following lines will never be triggered.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L60-L61
```solidity
        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
        if (!success) revert ZetaTransferError();
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L94
```solidity
        if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258-L260
```solidity
        if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
            revert GasFeeTransferFailed();
        }
```

If `TSSAddress == address(0)`, it cannot pass the `onlyTSS` verification, thus `ZeroAddress` will not be triggered.
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L118-L124
```solidity
    function pause() external onlyTSS {
        if (paused) {
            revert IsPaused();
        }
        if (TSSAddress == address(0)) {
            revert ZeroAddress();
        }
```

# The application of `GasPriceIncreaseMax` does not match its description.

Based on the comment below, `GasPriceIncreaseMax` represents the maximum percentage increase allowed.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/crosschain_flags.go#L16-L18
```go
	// Maximum gas price increase in percent of the median gas price
	// 500 means the gas price can be increased by 5 times the median gas price at most
	GasPriceIncreaseMax: 500,
```

However, in actual application, `GasPriceIncreaseMax` is used to compare with the value after the increase, rather than comparing the increased portion.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/abci.go#L85-L102
```go
	gasPriceIncrease := medianGasPrice.MulUint64(uint64(flags.GasPriceIncreasePercent)).QuoUint64(100)

	// compute new gas price
	currentGasPrice, err := cctx.GetCurrentOutTxParam().GetGasPrice()
	if err != nil {
		return math.ZeroUint(), math.ZeroUint(), err
	}
	newGasPrice := math.NewUint(currentGasPrice).Add(gasPriceIncrease)

	// check limit -- use default limit if not set
	gasPriceIncreaseMax := flags.GasPriceIncreaseMax
	if gasPriceIncreaseMax == 0 {
		gasPriceIncreaseMax = observertypes.DefaultGasPriceIncreaseFlags.GasPriceIncreaseMax
	}
	limit := medianGasPrice.MulUint64(uint64(gasPriceIncreaseMax)).QuoUint64(100)
	if newGasPrice.GT(limit) {
		return math.ZeroUint(), math.ZeroUint(), nil
	}
```

# If the extracted `zrc20` and the required `gasZRC20` are the same, directly modify the balance instead of calling `transferFrom`.

If the extracted `zrc20` and the required `gasZRC20` are the same, such as extracting ETH to Ethereum, it's possible to directly modify the balance instead of calling `transferFrom`. This can save users the step of performing an `approve` operation.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256-L260
```solidity
    function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
        (address gasZRC20, uint256 gasFee) = withdrawGasFee();
        if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
            revert GasFeeTransferFailed();
        }
```

# There is a lack of statistics on the total fees acquired by the protocol.

Currently, the collection of `protocolFlatFee` is directly added to `gasFee`, similar to the code below, and there is no record of the total amount of `protocolFlatFee` collected.

```go
	gasZRC20, gasLimit, gasPrice, protocolFlatFee, err := k.ChainGasParams(ctx, chainID)
	if err != nil {
		return cosmoserrors.Wrap(types.ErrCannotFindGasParams, err.Error())
	}
	outTxGasFee := gasLimit.Mul(gasPrice).Add(protocolFlatFee)
```

# In `AppendTss`, there is a lack of nonce update after calling `SetTSS`.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_tss.go#L16-L19
```go
func (k Keeper) AppendTss(ctx sdk.Context, tss types.TSS) {
	k.SetTSS(ctx, tss)
	k.SetTSSHistory(ctx, tss)
}
```

In both `SetTssAndUpdateNonce` and `InitGenesis`, where `SetTSS` is also called, the nonce is updated afterward.

Since currently `AppendTss` is not called by any other function, it is placed under QA for review.

# The implementation of obtaining `startNonce` in `CctxAllPending` does not match the comment.

The comment mentions using 100, but the actual code uses 1000.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx.go#L204-L207
```go
	// now query the previous nonces up to 100 prior to find any pending cctx that we might have missed
	// need this logic because a confirmation of higher nonce will automatically update the p.NonceLow
	// therefore might mask some lower nonce cctx that is still pending.
	startNonce := p.NonceLow - 1000
```