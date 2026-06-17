### Missing sanity check for zetaFee < zetaMaxFee_
###### Description:
If a user deploys the contract with **`zetaFee`** greater than **`zetaMaxFee_`**, it may result in unintended consequences and could compromise the integrity of the contract.

###### **Links to affected code**:
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74

###### Recommended Mitigation Steps
```solidity
constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
 +  require(zetaFee_ <= zetaMaxFee_, "Invalid zetaFee value");
	.....  
}
```

### Uninitialized connectorAddress in constructor
###### Description:
The **`updateTssAndConnectorAddresses`** function in the smart contract allows for updating both **`tssAddress`** and **`connectorAddress`** at a time. 
```solidity
function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {
			............ 
       if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();
      .........
    }
```
However, a potential issue has been identified in the constructor of the smart contract, where the **`connectorAddress`** is not defined and set. It is recommended to define and set the **`connectorAddress`** in the constructor to ensure proper initialization.

###### **Links to affected code**:
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L38

###### Recommended Mitigation Steps:
```solidity
constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {
  
	- if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();
  + if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();
        tssAddress = tssAddress_;
        tssAddressUpdater = tssAddressUpdater_;
	+     connectorAddress = connectorAddress_;
    }
```

### Open TODO in code
###### Description:
The hasZetaLiquidity method in ZetaTokenConsumerTrident.strategy.sol has an open TODO, consider fixing or deleting it. 

###### **Links to affected code**:
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L205


### Conside override allowance() in ZetaEth.sol
###### Description:
ZetaEth.sol inherited whole ERC20.sol, so conside override approve() to custom error for preventing to this may cause edge case like approve/transferFrom . 

### Remove unused import
###### Description:
Remove unused import from the contracts. 

###### **Links to affected code**:
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L6

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L10

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L6-L10

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L8

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L10

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L4

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L6

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L4

### Variables could be declared immutable
###### **Links to affected code**:
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L36-L39

###### Instance:
```solidity
// Existing variable declarations
uint256 private immutable _totalSupply;
string private immutable _name;
string private immutable _symbol;
uint8 private immutable _decimals;
```

### ZetaInteractor.sol fail on hard fork
###### Description
ZetaInteractor.sol uses block.chainid, which may be break on hard fork of this contract. 
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L39