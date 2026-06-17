## 2 step withdrawal leads to gas inefficiency
## Summary
The function in `repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol` uses a 2 step withdrawal to an address which wastes gas when you can do it in one.

Instead of transferring WETH9 to the ZetaConnectorZEVM and then sending it to FUNGIBLE_MODULE_ADDRESS, you can just transfer to FUNGIBLE_MODULE_ADDRESS


```diff
    function send(ZetaInterfaces.SendInput calldata input) external {
        // Transfer wzeta to "fungible" module, which will be burnt by the protocol post processing via hooks.
--        if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();
++        if (!WZETA(wzeta).transferFrom(msg.sender, WZETA(wzeta), input.zetaValueAndGas)) revert WZETATransferFailed();
        // @audit-issue Waste of gas, should just implement function to send funds to FUNGIBLE_MODULE_INSTEAD. What a waste of the 2 steps.
--        WZETA(wzeta).withdraw(input.zetaValueAndGas);
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