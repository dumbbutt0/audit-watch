## Wrong naming of Interfaces in ZetaNonEthInterface
***It is clear that the ZetaNonEthInterface.sol file in the zeta chain repositories is intended to be an interface. However, it was mistakenly given the name ZetaNonEthInterface instead of IZetaNonEth. By following the convention of naming interfaces with an "I" prefix in Solidity, renaming it to IZetaNonEth would make it easy to identify as an interface and avoid any confusion.***

## Wrong naming of interfaces in CommonErrors contract
***It is essential to have a clear contract naming convention to ensure readability and prevent confusion. The CommonError contract serves as a notification on the blockchain and is utilized by every function. However, the contract's current name does not reflect its nature as an interface, which could make it difficult for users to understand its purpose. Therefore, it is crucial to rename the contract appropriately to improve its clarity and readability.***

##### Recommendation 
>Change CommonError.sol to ICommonError.sol since it is an interface.

## Wrong naming of interfaces in ZetaInteractorErrors
***There are numerous issues with the naming conventions of the Zeta Chain Protocol. However, it's important to note that when using a contract as an interface, it should be clearly specified as such. Unfortunately, the EVM interface in the Zeta Chain contract has naming flaws that can lead to confusion. In order to avoid such confusion, it's essential to follow best practices when naming a contract.***

##### Recommendation
>Change [ZetaInteractorErros.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces) to IZetaInteractorErros.sol

## Avoid the wrong naming of interfaces
***This issue affects multiple contracts in the Zeta EVM chain, such as zContract, ZetaErrors, TridalPoolRouter, ZetaInterfaces, and Interfaces.***

##### Recommendation
>Change all interface contract I mentioned by adding ```I``` as a suffix.

## Unused contract
***It seems that the [contracts/zevm/UniswapPeriphery.sol](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol) and [Uniswap.sol](https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L4), [Zeta.eth.sol](sol) [repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol](https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L4), [contracts/evm/Zeta.eth.sol](https://github.com/search?q=repo%3Acode-423n4%2F2023-11-zetachain%20contracts%2Fevm%2FZeta.eth.sol&type=code),  was not imported into any other contract, indicating that it might be unused. it might be unused.***
#### Recommendation 
>Either it should be used or deleted

## No documentation about the interface functions
***It appears that there is a lack of documentation regarding the usage and origin of the interface contract in the Zeta EVM chain. It would be helpful to have more detailed information about which contracts are using this interface and where it was forked from.***

#### Recommendation
>Giving concise details about the interface will help users understand the protocol better when imported into a contract.

## Avoid using floating pragma
[repos/protocol-contracts/contracts/zevm/WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/WZETA.sol#L5)


##### Recommendation
>Use a fixed pragma

## Avoid using the Old solidity version
***[repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol](https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L4)***

###### Mitigation
> Use a fixed pragma solidity version in every contract that uses a floating pragma.


# [L1]No address zero checks in constructors
***Checking addresses against zero-address during initialization or during setting is a security best practice. However, such checks are missing in address variable initializations/changes in many places.*** 
https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L53C1-L55C55
https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L69C1-L73C34
https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L76C1-L76C58

###### Mitigation
>Add necessary required checks to avoid deploying to zero address.


# [L2] Immutable variable lacks check in the constructor
Constructors should check the address written in an immutable address variable is not the zero address.
https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L34
https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L33C1-L35C1
https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21
https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L22

###### Mitigation
>Add a zero address check for [zeta](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L34), [uniswapv2FactoryAddress](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L33), [uniswapv2Router02Address](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L34C1-L34C55) and spans across other contract


# [L3] Missing Interface Usage in WZETA Contract
***The contract [WZETA](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol) does not utilize or import its associated interface, [IWZETA](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol). This finding could potentially lead to a lack of clarity in the contract's intended structure and interactions. Interfaces serve as a crucial element in ensuring standardized communication between contracts and providing a clear definition of expected functionalities.***

#### Impact
***Lack of interface usage might make it challenging for developers, auditors, and other stakeholders to quickly understand the intended functions and external interactions of the WZETA contract.***
***Interfaces play a key role in standardizing contract interactions. Without importing and implementing the associated interface, there might be a risk of non-standard or unexpected behavior when interacting with other contracts or systems.***

### Recommendation
>It is recommended to import the IWZETA interface in the WZETA contract and ensure that all the required functions are appropriately implemented. This step will enhance the contract's readability and provide a clear definition of its expected behavior.


# [L4] MISSING CAP FOR MAPPED GAS PRICE GOTTEN FROM CHAINID
The msg.sender of the [SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123C1-L127C6) contract, when setting the mapped [gasPriceByChainId[chainID] = price](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L125); protocol parameter within [setGasPrice()](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123)
function, there are no checks regarding the quantity being set.

######
> An important parameter for the protocol is [setGasPrice()](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123), it is strongly recommended to set a cap for it, which plays a vital role.


# [L5] Emit events when all vital processes are completed
***It is important to keep a record of executed vital functions(swapping, creation of a contract with CREATE2, etc) for future reference. However, the Zeta contract has several functions that lack an "emit" function. This means that no information is stored on the blockchain, and there is no emission of events to help keep track of these functions.***
This low issue spans multiple lines:
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L87
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L202
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34C5-L56C6
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58C1-L93C6
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95C5-L122C6
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124C4-L160C6
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74C2-L96C6
###### Recommendation 
>Emit check in all vital functions.

# [L6] MISSING ADDRESS CHECKS IN FUNCTIONS
***This is a low finding moreover it is necessary for address in function to be checked so any transfer of funds will not be sent to an arbitrary address(address(0)). In most of zeta functions the is this lack of address(0) check and it spans across so many contract, I don't think I can identify them all though.***

##### Impact
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270

##### Recommendation
>Implicitly check if an address is not address zero(address(0)).


# [L8] Unsafe downcast

When downsizing a data type to a smaller type, the higher-order bits are truncated, effectively introducing a modulo operation to the original value. It's crucial to note that without proper validation checks, this wrapping behavior may cause unexpected issues and potential bugs in the system. 

Instances (4):

File: evm/tools/ImmutableCreate2Factory.sol

35:             uint160( // downcast to match the address type.

114:             uint160( // downcast to match the address type.

154:             uint160( // downcast to match the address type.

File: zevm/SystemContract.sol

103:             uint160(

# [L9] Solidity version 0.8.20 may not work on other chains due to PUSH0
During the deployment of contracts on alternative chains, compatibility concerns may arise with Solidity version 0.8.20. This issue is primarily due to the introduction of the PUSH0 opcode, a feature inherent to the Shanghai target Ethereum Virtual Machine (EVM) version. Not all Layer-2 solutions universally support this opcode, which can lead to deployment failures on such chains.

The primary project may compile successfully with version 0.8.20. However, difficulties may occur when integrating or extending it with other projects. Such complications can lead to deployment challenges for contracts and libraries in these scenarios.
Impact

The PUSH0 opcode is not implemented on some Layer-2 solutions, including Arbitrum. Therefore, contracts deployed on these chains may become non-functional. The impact is high as contracts would become completely unusable, and funds sent to these addresses by unaware users would become irretrievable.
Proof of Concept

The issue occurs when contracts are compiled using Solidity version 0.8.20 and deployed on chains that do not support the PUSH0 opcode. The contract deploys but is non-functional. An example of this can be seen at: https://arbiscan.io/address/0x504ada2360ac822faf7ac703b350fadc8d931211#code. The contract returns false or nothing at all when reading values, which indicates a failure due to the PUSH0 opcode.
Mitigation Steps

To avoid this potential setback, it is recommended to use an earlier EVM version for contracts that will be deployed to other chains. 

Instances (2):

File: evm/testing/AttackerContract.sol

2: pragma solidity ^0.8.0;

File: zevm/WZETA.sol

1: pragma solidity ^0.4.18;


# [L10] Wrong naming of functions
In in the swaping contract when Zeta was using Uniswap forked functions, there is this function name that wasn't written well. Obviously, Zeta should have used the name in the Uniswap also in their contract but they named it wrongly, this is just a point out nothing much.

###### Recommendation
> Change hasZetaLiquidity] to getZetaLiquidity in all contracts it has been used.

# [L11] TYPOS

# L12] Finish up your docs
***I came across a particular function that is undone or still going to be implemented, let me say this; When you guys are done with your audit make sure you guys finish up with some functions that are no done yet and not used too.***
`E.G`
```
 function hasZetaLiquidity() external view override returns (bool) {
        //@TODO: Implement
        return false;
    }
```
***Here you see is having a TODO inline comment tell us that you marked that out as something that will be done later. What I'm just saying in essence is that you guys should keep to not about this functions in your codebase because this code specially can lead to false return of value when a user wants to check if there is a liquidity in the pool before he/she swaps***


