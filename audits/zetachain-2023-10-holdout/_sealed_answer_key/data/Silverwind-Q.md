## Front-Running Vulnerability at *safeTransferFrom* and *safeApprove* Functions

The *ZetaTokenConsumerUniV2* contract uses safeTransferFrom and safeApprove from OpenZeppelin's SafeERC20 library to handle ERC20 tokens. While these functions address certain ERC20 token issues, they do not prevent front-running attacks. A malicious actor could observe the approval transaction and if they manage to get their transaction mined before the swap, they could interact with the Uniswap V2 Router using the approved tokens.

[Explanation](https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt) of this possible attack vector.

See also: https://github.com/0xProject/0x-monorepo/issues/850

Instances:
[1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L135-136) [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L159-L160) [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L193-194) [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L108-L109) [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L144-L145) [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L175-L176) [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L67-L68) [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L103-L104) [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L133-L134) [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L107-L108) [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L132-L133) [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L167-L168)

# Unchecked *initializationCode* Parameter
The *safeCreate2Internal* and *safeCreate2AndTransfer* functions accept an *initializationCode* parameter for contract deployment but do not verify whether it is empty. Deploying with empty *initializationCode* results in gas expenditure without deploying any functional bytecode.

Recommendation: Implement a check to ensure *initializationCode* is non-empty to prevent unnecessary gas usage and the creation of non-functional contracts. 

Instances:
https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L31

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L206C11-L206C11


# Incomplete Implementation of *hasZetaLiquidity* Function in *ZetaTokenConsumerTrident* Contract

The *hasZetaLiquidity* function in the *ZetaTokenConsumerTrident* contract is currently unimplemented and returns a hardcoded false. This function is expected to provide information about the availability of Zeta liquidity, which is crucial for users and external contracts to make informed decisions.


https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203

# Inconsistent NatSpec Documentation
The NatSpec comments for six functions within the *ZRC20.sol* contract suggest that these functions return a boolean value (true or false) to indicate success or failure. However, they are implemented to return true unconditionally upon success or to revert the transaction upon failure. There is no code path that allows these functions to return false.


Instances:
[1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125) [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145) [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157) [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173) [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225) [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256)

# Lack of Zero Address Check in Token Transfers
The *WETH9* contract does not prevent the transfer of tokens to the zero address in its *transfer* and *transferFrom* functions. This omission could lead to tokens being permanently lost without a corresponding decrease in the reported *totalSupply*, which is unconventional for ERC-20 tokens and could result in inaccurate supply metrics. To ensure accurate accounting and prevent token loss, it is recommended to add checks to prevent transfers to the zero address or to implement a burn function that adjusts *totalSupply* accordingly.

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L42


# Incorrect NatSpec Documentation for *setWzetaAddress* Function

The NatSpec comment for the *setWzetaAddress* function incorrectly suggests that the function is responsible for sending ZETA and a bytes message cross-chain. However, the actual implementation of the function only updates the contract's *wzeta* address. There is no cross-chain communication or transfer of tokens involved in this function.

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114

# Inaccurate NatSpec Comments for Contract Code Checks

The NatSpec comments for the *findCreate2Address* (line 101) and *findCreate2AddressViaHash* (line 141) functions state that the functions check for existing contract code at the computed address. However, the actual code only checks the *_deployed* mapping to see if the address has been previously deployed by this factory contract, without verifying the presence of contract code.

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L101

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L141

# Missing Zero Address Check in *updateSystemContractAddress* Function

The *updateSystemContractAddress* function allows the contract to update the *SYSTEM_CONTRACT_ADDRESS* without validating that the new address is non-zero. The absence of a check for the zero address (address(0)) could lead to the *SYSTEM_CONTRACT_ADDRESS* being set to an invalid address, which may disrupt critical contract functionality that relies on interactions with the system contract.

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270


# No Event Emission After Ownership Transfer

The *safeCreate2AndTransfer* function transfers ownership of the newly created contract to the caller but does not emit an event to log this action. The absence of such an event makes it difficult for off-chain services to track ownership changes.

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L207C9-L207C9


# Typographical Error in Code Comments

The comment on line 163 contains a typographical error in the spelling of "ZetaChain." It is currently written as "zetachain evm call or message," where it should be "ZetaChain EVM call or message."

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L163


Missing Input Validation at *send* Function

The absence of input validation in the *send* function of the *ZetaConnectorEth* contract poses risks, including the potential for funds to be irretrievably locked within the contract due to incorrect destination addresses, the misrouting of cross-chain transactions from invalid destination chain IDs, inefficient or wasteful gas usage from improperly specified zeta values and gas limits, and a heightened likelihood of user errors leading to transaction failures and loss of funds.

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31

