# Report


## Gas Optimizations


|                 | Issue                                  | Instances |
| --------------- | :------------------------------------- | :-------: |
| [GAS-1](#GAS-1) | Use assembly to check for `address(0)` |     67    |

### <a name="GAS-1"></a>[GAS-1] Use assembly to check for `address(0)`

*Saves 6 gas per instance*

*Instances (67)*:

```solidity
File: repos/protocol-contracts/contracts/zevm/ZRC20.sol

179:            if (sender == address(0)) revert ZeroAddress();

180:            if (recipient == address(0)) revert ZeroAddress();

192:            if (account == address(0)) revert ZeroAddress();

200:            if (account == address(0)) revert ZeroAddress();

212:            if (owner == address(0)) revert ZeroAddress();

213:            if (owner == address(0)) revert ZeroAddress();

238:            if (gasZRC20 == address(0)) {

```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol)

```solidity
File: repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

80:             zetaToken_ == address(0) ||

81:             pancakeV3Router_ == address(0) ||

82:             uniswapV3Factory_ == address(0) ||

83:             WETH9Address_ == address(0)

107:            if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        
132:            if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        
156:            if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        
190:            if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        
212:            if (poolAddress == address(0)) {
        
```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol)

```solidity
File: repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.solrepos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

47:             zetaToken_ == address(0) ||

48:             uniswapV3Router_ == address(0) ||

49:             WETH9Address_ == address(0) ||

50:             poolFactory_ == address(0)

78:            if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
               
105:           if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        
141:           if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
        
172:           if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        
```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol)

```solidity
File: repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

51:            zetaToken_ == address(0) ||

52:            uniswapV3Router_ == address(0) ||

53:            uniswapV3Factory_ == address(0) ||

54:            WETH9Address_ == address(0)

78:            if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
       
104:           if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

129:           if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

164:           if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
         
187:           if (poolAddress == address(0)) {

```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol)

```solidity
File: repos/protocol-contracts/contracts/evm/ERC20Custody.sol

81:             if (TSSAddress_ == address(0)) {

108:            if (TSSAddress == address(0)) {

122:            if (TSSAddress == address(0)) {

177:            if (zetaFee != 0 && address(zeta) != address(0)) {

```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol)

```solidity
File: repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

27:             if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

38:             if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

64:             if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

100:            if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

130:            if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol)

```solidity
File: repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

76:             zetaToken_ == address(0) ||

77:             tssAddress_ == address(0) ||

78:             tssAddressUpdater_ == address(0) ||

79:             pauserAddress_ == address(0)

118:            if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

130:            if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

141:            if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol)

```solidity
File: repos/protocol-contracts/contracts/zevm/SystemContract.sol

90:             if (token0 == address(0)) revert CantBeZeroAddress();

158:            if (addr == address(0)) revert ZeroAddress();

169:            if (addr == address(0)) revert ZeroAddress();

```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol)

```solidity
File: repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol

34:            if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();

42:            if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();

56:            if (tssAddress == address(0)) revert InvalidAddress();

```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol)

```solidity
File: repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

38:            if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

```

[Link to code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol)
