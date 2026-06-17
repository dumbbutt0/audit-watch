**contracts/zevm/ZRC20.sol**
- L161/163/183/185/203/205 - The currentAllowance - amount operation is performed, but the subtraction is previously validated, therefore it could become unchecked.

**contracts/zevm/WZETA.sol**
- L26/27/50/51 - The balanceOf[msg.sender] -= wad operation is performed, but the subtraction is previously validated, therefore it could become unchecked.

**contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol**
- L15 - The error ErrorSendingETH() is created but it is never used, therefore the correct thing to do would be to eliminate it so as not to take up storage space.
