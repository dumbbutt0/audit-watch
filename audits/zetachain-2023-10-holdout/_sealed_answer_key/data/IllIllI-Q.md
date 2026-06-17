## Summary

### Low Risk Issues

| |Issue|Instances|
|-|:-|:-:|
| [[L&#x2011;01](#l01-receivepayable-fallback-function-does-not-authorize-requests)] | `receive()`/`payable fallback()` function does not authorize requests | 3 | 
| [[L&#x2011;02](#l02-events-may-be-emitted-out-of-order-due-to-reentrancy)] | Events may be emitted out of order due to reentrancy | 78 | 

Total: 81 instances over 2 issues

### Non-critical Issues

| |Issue|Instances|
|-|:-|:-:|
| [[N&#x2011;01](#n01-2n---1-should-be-re-written-as-typeuintnmaxnn)] | `2**<n> - 1` should be re-written as `type(uint<n>).max` | 1 | 
| [[N&#x2011;02](#n02-constants-should-be-defined-rather-than-using-magic-numbers)] | `constant`s should be defined rather than using magic numbers | 3 | 
| [[N&#x2011;03](#n03-public-functions-not-called-by-the-contract-should-be-declared-external-instead)] | `public` functions not called by the contract should be declared `external` instead | 9 | 
| [[N&#x2011;04](#n04-array-indices-should-be-referenced-via-enums-rather-than-via-numeric-literals)] | Array indices should be referenced via `enum`s rather than via numeric literals | 26 | 
| [[N&#x2011;05](#n05-avoid-the-use-of-sensitive-terms)] | Avoid the use of sensitive terms | 22 | 
| [[N&#x2011;06](#n06-cast-to-bytes-or-bytes32-for-clearer-semantic-meaning)] | Cast to `bytes` or `bytes32` for clearer semantic meaning | 1 | 
| [[N&#x2011;07](#n07-consider-defining-system-wide-constants-in-a-single-file)] | Consider defining system-wide constants in a single file | 7 | 
| [[N&#x2011;08](#n08-consider-emitting-an-event-at-the-end-of-the-constructor)] | Consider emitting an event at the end of the constructor | 13 | 
| [[N&#x2011;09](#n09-consider-using-delete-rather-than-assigning-zerofalse-to-clear-values)] | Consider using `delete` rather than assigning zero/false to clear values | 5 | 
| [[N&#x2011;10](#n10-consider-using-a-struct-rather-than-having-many-function-input-parameters)] | Consider using a `struct` rather than having many function input parameters | 8 | 
| [[N&#x2011;11](#n11-consider-using-descriptive-constants-when-passing-zero-as-a-function-argument)] | Consider using descriptive `constant`s when passing zero as a function argument | 14 | 
| [[N&#x2011;12](#n12-consider-using-named-mappings)] | Consider using named mappings | 8 | 
| [[N&#x2011;13](#n13-consider-using-named-returns)] | Consider using named returns | 80 | 
| [[N&#x2011;14](#n14-constants-in-comparisons-should-appear-on-the-left-side)] | Constants in comparisons should appear on the left side | 26 | 
| [[N&#x2011;15](#n15-contract-should-expose-an-interface)] | Contract should expose an `interface` | 12 | 
| [[N&#x2011;16](#n16-contracts-should-have-full-test-coverage)] | Contracts should have full test coverage | 1 | 
| [[N&#x2011;17](#n17-contractslibrariesinterfaces-should-each-be-defined-in-separate-files)] | Contracts/libraries/interfaces should each be defined in separate files | 27 | 
| [[N&#x2011;18](#n18-custom-error-has-no-parameters-showing-error-details)] | Custom error has no parameters showing error details | 42 | 
| [[N&#x2011;19](#n19-duplicated-requirerevert-checks-should-be-refactored-to-a-modifier-or-function)] | Duplicated `require()`/`revert()` checks should be refactored to a modifier or function | 14 | 
| [[N&#x2011;20](#n20-event-is-not-properly-indexed)] | Event is not properly `indexed` | 23 | 
| [[N&#x2011;21](#n21-events-should-use-parameters-to-convey-information)] | Events should use parameters to convey information | 1 | 
| [[N&#x2011;22](#n22-expressions-for-constant-values-should-use-immutable-rather-than-constant)] | Expressions for constant values should use `immutable` rather than `constant` | 2 | 
| [[N&#x2011;23](#n23-function-state-mutability-can-be-restricted-to-pure)] | Function state mutability can be restricted to `pure` | 1 | 
| [[N&#x2011;24](#n24-import-declarations-should-import-specific-identifiers-rather-than-the-whole-file)] | Import declarations should import specific identifiers, rather than the whole file | 49 | 
| [[N&#x2011;25](#n25-imports-could-be-organized-more-systematically)] | Imports could be organized more systematically | 4 | 
| [[N&#x2011;26](#n26-inconsistent-spacing-in-comments)] | Inconsistent spacing in comments | 1 | 
| [[N&#x2011;27](#n27-interfaces-should-be-defined-in-separate-files-from-their-usage)] | Interfaces should be defined in separate files from their usage | 12 | 
| [[N&#x2011;28](#n28-interfaces-should-be-indicated-with-an-i-prefix-in-the-contract-name)] | Interfaces should be indicated with an `I` prefix in the contract name | 22 | 
| [[N&#x2011;29](#n29-interfaces-should-use-floating-version-pragmas)] | Interfaces should use floating version pragmas | 29 | 
| [[N&#x2011;30](#n30-missing-event-for-critical-parameter-change)] | Missing event for critical parameter change | 1 | 
| [[N&#x2011;31](#n31-mixed-usage-of-intuint-with-int256uint256)] | Mixed usage of `int`/`uint` with `int256`/`uint256` | 100 | 
| [[N&#x2011;32](#n32-named-imports-of-parent-contracts-are-missing)] | Named imports of parent contracts are missing | 28 | 
| [[N&#x2011;33](#n33-names-of-interfaces-should-be-prefixed-with-an-i-or-contain-the-word-interface)] | Names of `interface`s should be prefixed with an `I`, or contain the word `Interface` | 19 | 
| [[N&#x2011;34](#n34-natspec-contract-declarations-should-have-author-tags)] | NatSpec: Contract declarations should have `@author` tags | 45 | 
| [[N&#x2011;35](#n35-natspec-contract-declarations-should-have-dev-tags)] | NatSpec: Contract declarations should have `@dev` tags | 28 | 
| [[N&#x2011;36](#n36-natspec-contract-declarations-should-have-notice-tags)] | NatSpec: Contract declarations should have `@notice` tags | 27 | 
| [[N&#x2011;37](#n37-natspec-contract-declarations-should-have-title-tags)] | NatSpec: Contract declarations should have `@title` tags | 44 | 
| [[N&#x2011;38](#n38-natspec-contract-declarations-should-have-descriptions)] | NatSpec: Contract declarations should have descriptions | 27 | 
| [[N&#x2011;39](#n39-natspec-error-param-tag-is-missing)] | NatSpec: Error `@param` tag is missing | 10 | 
| [[N&#x2011;40](#n40-natspec-error-declarations-should-have-dev-tags)] | NatSpec: Error declarations should have `@dev` tags | 52 | 
| [[N&#x2011;41](#n41-natspec-error-declarations-should-have-notice-tags)] | NatSpec: Error declarations should have `@notice` tags | 51 | 
| [[N&#x2011;42](#n42-natspec-error-declarations-should-have-descriptions)] | NatSpec: Error declarations should have descriptions | 51 | 
| [[N&#x2011;43](#n43-natspec-event-param-tag-is-missing)] | NatSpec: Event `@param` tag is missing | 117 | 
| [[N&#x2011;44](#n44-natspec-event-declarations-should-have-dev-tags)] | NatSpec: Event declarations should have `@dev` tags | 51 | 
| [[N&#x2011;45](#n45-natspec-event-declarations-should-have-notice-tags)] | NatSpec: Event declarations should have `@notice` tags | 50 | 
| [[N&#x2011;46](#n46-natspec-event-declarations-should-have-descriptions)] | NatSpec: Event declarations should have descriptions | 50 | 
| [[N&#x2011;47](#n47-natspec-file-is-missing-natspec)] | NatSpec: File is missing NatSpec | 6 | 
| [[N&#x2011;48](#n48-natspec-function-param-tag-is-missing)] | NatSpec: Function `@param` tag is missing | 381 | 
| [[N&#x2011;49](#n49-natspec-function-return-tag-is-missing)] | NatSpec: Function `@return` tag is missing | 103 | 
| [[N&#x2011;50](#n50-natspec-function-declarations-should-have-dev-tags)] | NatSpec: Function declarations should have `@dev` tags | 127 | 
| [[N&#x2011;51](#n51-natspec-function-declarations-should-have-notice-tags)] | NatSpec: Function declarations should have `@notice` tags | 120 | 
| [[N&#x2011;52](#n52-natspec-function-declarations-should-have-descriptions)] | NatSpec: Function declarations should have descriptions | 120 | 
| [[N&#x2011;53](#n53-natspec-modifier-param-tag-is-missing)] | NatSpec: Modifier `@param` tag is missing | 2 | 
| [[N&#x2011;54](#n54-natspec-modifier-declarations-should-have-dev-tags)] | NatSpec: Modifier declarations should have `@dev` tags | 5 | 
| [[N&#x2011;55](#n55-natspec-modifier-declarations-should-have-notice-tags)] | NatSpec: Modifier declarations should have `@notice` tags | 5 | 
| [[N&#x2011;56](#n56-natspec-modifier-declarations-should-have-descriptions)] | NatSpec: Modifier declarations should have descriptions | 5 | 
| [[N&#x2011;57](#n57-natspec-non-public-state-variable-declarations-should-use-dev-tags)] | NatSpec: Non-public state variable declarations should use `@dev` tags | 18 | 
| [[N&#x2011;58](#n58-natspec-state-variable-declarations-should-have-descriptions)] | NatSpec: State variable declarations should have descriptions | 40 | 
| [[N&#x2011;59](#n59-natspec-use-inheritdoc-to-inherit-the-natspec-of-the-base-function)] | NatSpec: Use `@inheritdoc` to inherit the NatSpec of the base function | 1 | 
| [[N&#x2011;60](#n60-pausable-contract-never-uses-whennotposed-modifier)] | Pausable contract never uses `whenNotPosed` modifier | 1 | 
| [[N&#x2011;61](#n61-style-guide-contract-does-not-follow-the-solidity-style-guides-suggested-layout-ordering)] | Style guide: Contract does not follow the Solidity style guide's suggested layout ordering | 7 | 
| [[N&#x2011;62](#n62-style-guide-contract-names-should-use-camelcase)] | Style guide: Contract names should use CamelCase | 1 | 
| [[N&#x2011;63](#n63-style-guide-control-structures-do-not-follow-the-solidity-style-guide)] | Style guide: Control structures do not follow the Solidity Style Guide | 139 | 
| [[N&#x2011;64](#n64-style-guide-extraneous-whitespace)] | Style guide: Extraneous whitespace | 3 | 
| [[N&#x2011;65](#n65-style-guide-function-ordering-does-not-follow-the-solidity-style-guide)] | Style guide: Function ordering does not follow the Solidity style guide | 9 | 
| [[N&#x2011;66](#n66-style-guide-lines-are-too-long)] | Style guide: Lines are too long | 14 | 
| [[N&#x2011;67](#n67-style-guide-local-and-state-variables-should-be-named-using-lowercamelcase)] | Style guide: Local and state variables should be named using lowerCamelCase | 6 | 
| [[N&#x2011;68](#n68-style-guide-non-externalpublic-function-names-should-begin-with-an-underscore)] | Style guide: Non-`external`/`public` function names should begin with an underscore | 2 | 
| [[N&#x2011;69](#n69-style-guide-non-externalpublic-variable-names-should-begin-with-an-underscore)] | Style guide: Non-`external`/`public` variable names should begin with an underscore | 9 | 
| [[N&#x2011;70](#n70-style-guide-struct-names-should-use-camelcase)] | Style guide: Struct names should use CamelCase | 1 | 
| [[N&#x2011;71](#n71-style-guide-top-level-declarations-should-be-separated-by-at-least-two-lines)] | Style guide: Top-level declarations should be separated by at least two lines | 25 | 
| [[N&#x2011;72](#n72-style-guide-variable-names-for-immutables-should-use-constant_case)] | Style guide: Variable names for `immutable`s should use CONSTANT_CASE | 23 | 
| [[N&#x2011;73](#n73-style-guide-variable-names-that-consist-of-all-capital-letters-should-be-reserved-for-constantimmutable-variables)] | Style guide: Variable names that consist of all capital letters should be reserved for `constant`/`immutable` variables | 3 | 
| [[N&#x2011;74](#n74-unnecessary-cast)] | Unnecessary cast | 1 | 
| [[N&#x2011;75](#n75-unused-error-definition)] | Unused `error` definition | 4 | 
| [[N&#x2011;76](#n76-unused-event-definition)] | Unused `event` definition | 11 | 
| [[N&#x2011;77](#n77-unused-modifers)] | Unused `modifer`s | 2 | 
| [[N&#x2011;78](#n78-unused-struct-definition)] | Unused `struct` definition | 2 | 
| [[N&#x2011;79](#n79-unused-contract-variables)] | Unused contract variables | 2 | 
| [[N&#x2011;80](#n80-unused-file)] | Unused file | 2 | 
| [[N&#x2011;81](#n81-unused-file-import)] | Unused file import | 7 | 
| [[N&#x2011;82](#n82-unused-function-parameter)] | Unused function parameter | 14 | 
| [[N&#x2011;83](#n83-use-the-latest-solidity-prior-to-0820-if-on-l2s-for-deployment)] | Use the latest solidity (prior to 0.8.20 if on L2s) for deployment | 14 | 
| [[N&#x2011;84](#n84-using--without-specifying-an-upper-bound-is-unsafe)] | Using `>`/`>=` without specifying an upper bound is unsafe | 2 | 
| [[N&#x2011;85](#n85-visibility-should-be-set-explicitly-rather-than-defaulting-to-internal)] | Visibility should be set explicitly rather than defaulting to `internal` | 1 | 

Total: 2452 instances over 85 issues





## Low Risk Issues


### [L&#x2011;01] `receive()`/`payable fallback()` function does not authorize requests
Having no access control on the function (e.g. `require(msg.sender == address(weth))`) means that someone may send Ether to the contract, and have no way to get anything back out, which is a loss of funds. If the concern is having to spend a small amount of gas to check the sender against an immutable address, the code should at least have a function to rescue mistakenly-sent Ether.

*There are 3 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

101:      receive() external payable {}

```
*GitHub*: [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

66:       receive() external payable {}

```
*GitHub*: [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

72:       receive() external payable {}

```
*GitHub*: [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72)



### [L&#x2011;02] Events may be emitted out of order due to reentrancy
Ensure that events follow the best practice of check-effects-interaction, and are emitted before external calls

*There are 78 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

/// @audit transferFrom() called prior to this emission in deposit(), via: deposit(), safeTransferFrom()
/// @audit balanceOf() called prior to this emission in deposit(), via: deposit()
184:         emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);

/// @audit transfer() called prior to this emission in withdraw(), via: withdraw(), safeTransfer()
198:         emit Withdrawn(recipient, asset, amount);

```
*GitHub*: [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L184-L184), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L184-L184), [198](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L198-L198)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

/// @audit transferFrom() called prior to this emission in send(), via: send()
35           emit ZetaSent(
36               tx.origin,
37               msg.sender,
38               input.destinationChainId,
39               input.destinationAddress,
40               input.zetaValueAndGas,
41               input.destinationGasLimit,
42               input.message,
43               input.zetaParams
44:          );

/// @audit onZetaMessage() called prior to this emission in onReceive(), via: onReceive()
/// @audit transfer() called prior to this emission in onReceive(), via: onReceive()
69:          emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);

/// @audit onZetaRevert() called prior to this emission in onRevert(), via: onRevert()
/// @audit transfer() called prior to this emission in onRevert(), via: onRevert()
102          emit ZetaReverted(
103              zetaTxSenderAddress,
104              sourceChainId,
105              destinationChainId,
106              destinationAddress,
107              remainingZetaValue,
108              message,
109              internalSendHash
110:         );

```
*GitHub*: [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L35-L44), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L69-L69), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L69-L69), [102](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L102-L110), [102](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L102-L110)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

/// @audit burnFrom() called prior to this emission in send(), via: send()
43           emit ZetaSent(
44               tx.origin,
45               msg.sender,
46               input.destinationChainId,
47               input.destinationAddress,
48               input.zetaValueAndGas,
49               input.destinationGasLimit,
50               input.message,
51               input.zetaParams
52:          );

/// @audit onZetaMessage() called prior to this emission in onReceive(), via: onReceive()
/// @audit mint() called prior to this emission in onReceive(), via: onReceive()
/// @audit totalSupply() called prior to this emission in onReceive(), via: onReceive()
78:          emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);

/// @audit onZetaRevert() called prior to this emission in onRevert(), via: onRevert()
/// @audit mint() called prior to this emission in onRevert(), via: onRevert()
/// @audit totalSupply() called prior to this emission in onRevert(), via: onRevert()
113          emit ZetaReverted(
114              zetaTxSenderAddress,
115              sourceChainId,
116              destinationChainId,
117              destinationAddress,
118              remainingZetaValue,
119              message,
120              internalSendHash
121:         );

```
*GitHub*: [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L43-L52), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L78-L78), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L78-L78), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L78-L78), [113](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L113-L121), [113](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L113-L121), [113](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L113-L121)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

/// @audit exactInputSingle() called prior to this emission in getZetaFromEth(), via: getZetaFromEth()
122:         emit EthExchangedForZeta(msg.value, amountOut);

/// @audit exactInput() called prior to this emission in getZetaFromToken(), via: getZetaFromToken()
/// @audit approve() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeApprove()
/// @audit allowance() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeApprove()
/// @audit transferFrom() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeTransferFrom()
147:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

/// @audit withdraw() called prior to this emission in getEthFromZeta(), via: getEthFromZeta()
/// @audit exactInputSingle() called prior to this emission in getEthFromZeta(), via: getEthFromZeta()
/// @audit approve() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeApprove()
/// @audit allowance() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeApprove()
/// @audit transferFrom() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeTransferFrom()
176:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

/// @audit exactInput() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta()
/// @audit approve() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeApprove()
/// @audit allowance() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeApprove()
/// @audit transferFrom() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeTransferFrom()
205:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);

```
*GitHub*: [122](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L122-L122), [147](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L147-L147), [147](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L147-L147), [147](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L147-L147), [147](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L147-L147), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176-L176), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176-L176), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176-L176), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176-L176), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176-L176), [205](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L205-L205), [205](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L205-L205), [205](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L205-L205), [205](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L205-L205)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit exactInputSingle() called prior to this emission in getZetaFromEth(), via: getZetaFromEth()
/// @audit getPools() called prior to this emission in getZetaFromEth(), via: getZetaFromEth()
95:          emit EthExchangedForZeta(msg.value, amountOut);

/// @audit exactInput() called prior to this emission in getZetaFromToken(), via: getZetaFromToken()
/// @audit getPools() called prior to this emission in getZetaFromToken(), via: getZetaFromToken()
/// @audit approve() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeApprove()
/// @audit allowance() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeApprove()
/// @audit transferFrom() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeTransferFrom()
132:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

/// @audit exactInputSingle() called prior to this emission in getEthFromZeta(), via: getEthFromZeta()
/// @audit getPools() called prior to this emission in getEthFromZeta(), via: getEthFromZeta()
/// @audit approve() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeApprove()
/// @audit allowance() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeApprove()
/// @audit transferFrom() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeTransferFrom()
161:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

/// @audit exactInput() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta()
/// @audit getPools() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta()
/// @audit approve() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeApprove()
/// @audit allowance() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeApprove()
/// @audit transferFrom() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeTransferFrom()
199:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);

```
*GitHub*: [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L95-L95), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L95-L95), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L132-L132), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L132-L132), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L132-L132), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L132-L132), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L132-L132), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L161-L161), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L161-L161), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L161-L161), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L161-L161), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L161-L161), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L199-L199), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L199-L199), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L199-L199), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L199-L199), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L199-L199)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

/// @audit swapExactETHForTokens() called prior to this emission in getZetaFromEth(), via: getZetaFromEth()
54:          emit EthExchangedForZeta(msg.value, amountOut);

/// @audit swapExactTokensForTokens() called prior to this emission in getZetaFromToken(), via: getZetaFromToken()
/// @audit approve() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeApprove()
/// @audit allowance() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeApprove()
/// @audit transferFrom() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeTransferFrom()
91:          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

/// @audit swapExactTokensForETH() called prior to this emission in getEthFromZeta(), via: getEthFromZeta()
/// @audit approve() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeApprove()
/// @audit allowance() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeApprove()
/// @audit transferFrom() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeTransferFrom()
120:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

/// @audit swapExactTokensForTokens() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta()
/// @audit approve() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeApprove()
/// @audit allowance() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeApprove()
/// @audit transferFrom() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeTransferFrom()
158:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);

```
*GitHub*: [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L54-L54), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L91-L91), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L91-L91), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L91-L91), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L91-L91), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L120-L120), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L120-L120), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L120-L120), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L120-L120), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L158-L158), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L158-L158), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L158-L158), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L158-L158)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

/// @audit exactInputSingle() called prior to this emission in getZetaFromEth(), via: getZetaFromEth()
94:          emit EthExchangedForZeta(msg.value, amountOut);

/// @audit exactInput() called prior to this emission in getZetaFromToken(), via: getZetaFromToken()
/// @audit approve() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeApprove()
/// @audit allowance() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeApprove()
/// @audit transferFrom() called prior to this emission in getZetaFromToken(), via: getZetaFromToken(), safeTransferFrom()
120:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

/// @audit withdraw() called prior to this emission in getEthFromZeta(), via: getEthFromZeta()
/// @audit exactInputSingle() called prior to this emission in getEthFromZeta(), via: getEthFromZeta()
/// @audit approve() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeApprove()
/// @audit allowance() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeApprove()
/// @audit transferFrom() called prior to this emission in getEthFromZeta(), via: getEthFromZeta(), safeTransferFrom()
150:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

/// @audit exactInput() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta()
/// @audit approve() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeApprove()
/// @audit allowance() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeApprove()
/// @audit transferFrom() called prior to this emission in getTokenFromZeta(), via: getTokenFromZeta(), safeTransferFrom()
180:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);

```
*GitHub*: [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L94-L94), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L120-L120), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L120-L120), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L120-L120), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L120-L120), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150-L150), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150-L150), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150-L150), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150-L150), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150-L150), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L180-L180), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L180-L180), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L180-L180), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L180-L180)

```solidity
File: contracts/zevm/ZRC20.sol

/// @audit transferFrom() called prior to this emission in withdraw(), via: withdraw()
/// @audit gasPriceByChainId() called prior to this emission in withdraw(), via: withdraw(), withdrawGasFee()
/// @audit gasCoinZRC20ByChainId() called prior to this emission in withdraw(), via: withdraw(), withdrawGasFee()
262:         emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);

```
*GitHub*: [262](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L262-L262), [262](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L262-L262), [262](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L262-L262)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

/// @audit withdraw() called prior to this emission in send(), via: send()
/// @audit transferFrom() called prior to this emission in send(), via: send()
98           emit ZetaSent(
99               tx.origin,
100              msg.sender,
101              input.destinationChainId,
102              input.destinationAddress,
103              input.zetaValueAndGas,
104              input.destinationGasLimit,
105              input.message,
106              input.zetaParams
107:         );

```
*GitHub*: [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L98-L107), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L98-L107)

</details>




## Non-critical Issues


### [N&#x2011;01] `2**<n> - 1` should be re-written as `type(uint<n>).max`
Earlier versions of solidity can use `uint<n>(-1)` instead. Expressions not including the `- 1` can often be re-written to accommodate the change (e.g. by using a `>` rather than a `>=`, which will also save some gas)

*There is one instance of this issue:*

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

16:      uint256 public maxSupply = 2 ** 256 - 1;

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16-L16)



### [N&#x2011;02] `constant`s should be defined rather than using magic numbers
Even [assembly](https://github.com/code-423n4/2022-05-opensea-seaport/blob/9d7ce4d08bf3c3010304a0476a785c70c0e90ae7/contracts/lib/TokenTransferrer.sol#L35-L39) can benefit from using readable constants instead of hex/numeric literals

*There are 3 instances of this issue:*

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

/// @audit 256
16:      uint256 public maxSupply = 2 ** 256 - 1;

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16-L16)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

/// @audit 3
76:              path = new address[](3);

/// @audit 3
142:             path = new address[](3);

```
*GitHub*: [76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L76-L76), [142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L142-L142)



### [N&#x2011;03] `public` functions not called by the contract should be declared `external` instead
Contracts [are allowed](https://docs.soliditylang.org/en/latest/contracts.html#function-overriding) to override their parents' functions and change the visibility from `external` to `public`.

*There are 9 instances of this issue:*

```solidity
File: contracts/evm/Zeta.non-eth.sol

73:       function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {

```
*GitHub*: [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73)

```solidity
File: contracts/zevm/ZRC20.sol

83:       function name() public view virtual override returns (string memory) {

91:       function symbol() public view virtual override returns (string memory) {

107:      function totalSupply() public view virtual override returns (uint256) {

116:      function balanceOf(address account) public view virtual override returns (uint256) {

125:      function transfer(address recipient, uint256 amount) public virtual override returns (bool) {

135:      function allowance(address owner, address spender) public view virtual override returns (uint256) {

145:      function approve(address spender, uint256 amount) public virtual override returns (bool) {

157:      function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {

```
*GitHub*: [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L107), [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L116), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157)



### [N&#x2011;04] Array indices should be referenced via `enum`s rather than via numeric literals


*There are 26 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

88:              pool: pairPools[0],

118:         path[0] = pairPools1[0];

118:         path[0] = pairPools1[0];

119:         path[1] = pairPools2[0];

119:         path[1] = pairPools2[0];

154:             pool: pairPools[0],

185:         path[0] = pairPools1[0];

185:         path[0] = pairPools1[0];

186:         path[1] = pairPools2[0];

186:         path[1] = pairPools2[0];

```
*GitHub*: [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L88-L88), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L118-L118), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L118-L118), [119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L119-L119), [119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L119-L119), [154](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L154-L154), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L185-L185), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L185-L185), [186](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L186-L186), [186](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L186-L186)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

42:          path[0] = wETH;

43:          path[1] = zetaToken;

73:              path[0] = wETH;

74:              path[1] = zetaToken;

77:              path[0] = inputToken;

78:              path[1] = wETH;

79:              path[2] = zetaToken;

107:         path[0] = zetaToken;

108:         path[1] = wETH;

139:             path[0] = zetaToken;

140:             path[1] = wETH;

143:             path[0] = zetaToken;

144:             path[1] = wETH;

145:             path[2] = outputToken;

164:         path[0] = wETH;

165:         path[1] = zetaToken;

```
*GitHub*: [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L43-L43), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L73-L73), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L74-L74), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L77-L77), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L78-L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L79-L79), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L107-L107), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L108-L108), [139](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L139-L139), [140](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L140-L140), [143](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L143-L143), [144](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L144-L144), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L145-L145), [164](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L164-L164), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L165-L165)



### [N&#x2011;05] Avoid the use of sensitive terms
Use [alternative variants](https://www.zdnet.com/article/mysql-drops-master-slave-and-blacklist-whitelist-terminology/), e.g. allowlist/denylist instead of whitelist/blacklist

*There are 22 instances of this issue:*

```solidity
File: contracts/evm/ERC20Custody.sol

36:       mapping(IERC20 => bool) public whitelisted;

14:       error NotWhitelisted();

36:       mapping(IERC20 => bool) public whitelisted;

40:       event Whitelisted(IERC20 indexed asset);

41:       event Unwhitelisted(IERC20 indexed asset);

144:      function whitelist(IERC20 asset) external onlyTSS {

145:          whitelisted[asset] = true;

146:          emit Whitelisted(asset);

153:      function unwhitelist(IERC20 asset) external onlyTSS {

154:          whitelisted[asset] = false;

155:          emit Unwhitelisted(asset);

174:          if (!whitelisted[asset]) {

175:              revert NotWhitelisted();

194:          if (!whitelisted[asset]) {

195:              revert NotWhitelisted();

35:       /// @notice Mapping of whitelisted token => true/false.

36:       mapping(IERC20 => bool) public whitelisted;

141:       * @dev Whitelist asset.

144:      function whitelist(IERC20 asset) external onlyTSS {

150:       * @dev Unwhitelist asset.

153:      function unwhitelist(IERC20 asset) external onlyTSS {

```
*GitHub*: [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41), [144](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L145), [146](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L146), [153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153), [154](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L154), [155](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L155), [174](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L174), [175](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L175), [194](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L194), [195](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L195), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36), [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L141), [144](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L150), [153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

8:        // @dev Thrown when try to send a message or tokens to a non whitelisted chain

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L8)



### [N&#x2011;06] Cast to `bytes` or `bytes32` for clearer semantic meaning
Using a [cast](https://ethereum.stackexchange.com/questions/30912/how-to-compare-strings-in-solidity#answer-82739) on a single argument, rather than `abi.encodePacked()` makes the intended operation more clear, leading to less reviewer confusion.

*There is one instance of this issue:*

```solidity
File: contracts/zevm/ZRC20.sol

228:         emit Deposit(abi.encodePacked(FUNGIBLE_MODULE_ADDRESS), to, amount);

```
*GitHub*: [228](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L228-L228)



### [N&#x2011;07] Consider defining system-wide constants in a single file
`ContA.X = 0`, `ContB.Y = 1`, `ContC.Z = 2` -> `ContConstants.X = 0`, `ContConstants.Y = 1`, `ContConstants.Z = 2`; `ContA.X = X`, `ContB.Y = Y`, `ContC.Z = Z`,

*There are 7 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

58:      uint256 internal constant MAX_DEADLINE = 200;

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58-L58)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

35:      uint256 internal constant MAX_DEADLINE = 200;

```
*GitHub*: [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L35)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

19:      uint256 internal constant MAX_DEADLINE = 200;

```
*GitHub*: [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19-L19)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

29:      uint256 internal constant MAX_DEADLINE = 200;

```
*GitHub*: [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29-L29)

```solidity
File: contracts/zevm/SystemContract.sol

31:      address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;

```
*GitHub*: [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L31-L31)

```solidity
File: contracts/zevm/ZRC20.sol

22:      address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;

```
*GitHub*: [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22-L22)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

63:      address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);

```
*GitHub*: [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63-L63)

</details>





### [N&#x2011;08] Consider emitting an event at the end of the constructor
This will allow users to easily exactly pinpoint when and by whom a contract was constructed

*There are 13 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

68:      constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

```
*GitHub*: [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L68)

```solidity
File: contracts/evm/Zeta.eth.sol

10:      constructor(address creator, uint256 initialSupply) {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L10)

```solidity
File: contracts/evm/Zeta.non-eth.sol

33:      constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

```
*GitHub*: [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L33)

```solidity
File: contracts/evm/ZetaConnector.base.sol

74:      constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {

```
*GitHub*: [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74-L74)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

16       constructor(
17           address zetaToken_,
18           address tssAddress_,
19           address tssAddressUpdater_,
20           address pauserAddress_
21:      ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

20       constructor(
21           address zetaTokenAddress_,
22           address tssAddress_,
23           address tssAddressUpdater_,
24           address pauserAddress_
25:      ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

```
*GitHub*: [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

37:      constructor(address zetaConnectorAddress) {

```
*GitHub*: [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L37-L37)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

71       constructor(
72           address zetaToken_,
73           address pancakeV3Router_,
74           address uniswapV3Factory_,
75           address WETH9Address_,
76           uint24 zetaPoolFee_,
77           uint24 tokenPoolFee_
78:      ) {

```
*GitHub*: [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L78)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

45:      constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

```
*GitHub*: [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L45)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

26:      constructor(address zetaToken_, address uniswapV2Router_) {

```
*GitHub*: [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26-L26)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

42       constructor(
43           address zetaToken_,
44           address uniswapV3Router_,
45           address uniswapV3Factory_,
46           address WETH9Address_,
47           uint24 zetaPoolFee_,
48           uint24 tokenPoolFee_
49:      ) {

```
*GitHub*: [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L49)

```solidity
File: contracts/zevm/ZRC20.sol

60       constructor(
61           string memory name_,
62           string memory symbol_,
63           uint8 decimals_,
64           uint256 chainid_,
65           CoinType coinType_,
66           uint256 gasLimit_,
67           address systemContractAddress_
68:      ) {

```
*GitHub*: [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L68)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

79:      constructor(address wzeta_) {

```
*GitHub*: [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L79)

</details>





### [N&#x2011;09] Consider using `delete` rather than assigning zero/false to clear values
The `delete` keyword more closely matches the semantics of what is being done, and draws more attention to the changing of state, which may lead to a more thorough audit of its associated logic

*There are 5 instances of this issue:*

```solidity
File: contracts/evm/ERC20Custody.sol

136:         paused = false;

154:         whitelisted[asset] = false;

```
*GitHub*: [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L136-L136), [154](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L154-L154)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

98:          _locked = false;

```
*GitHub*: [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L98-L98)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

63:          _locked = false;

```
*GitHub*: [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L63-L63)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

69:          _locked = false;

```
*GitHub*: [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L69-L69)



### [N&#x2011;10] Consider using a `struct` rather than having many function input parameters
Often times, a subset of the parameters would be more clear if they were passed as a struct

*There are 8 instances of this issue:*

```solidity
File: contracts/evm/ZetaConnector.eth.sol

52       function onReceive(
53           bytes calldata zetaTxSenderAddress,
54           uint256 sourceChainId,
55           address destinationAddress,
56           uint256 zetaValue,
57           bytes calldata message,
58           bytes32 internalSendHash
59:      ) external override onlyTssAddress {

77       function onRevert(
78           address zetaTxSenderAddress,
79           uint256 sourceChainId,
80           bytes calldata destinationAddress,
81           uint256 destinationChainId,
82           uint256 remainingZetaValue,
83           bytes calldata message,
84           bytes32 internalSendHash
85:      ) external override whenNotPaused onlyTssAddress {

```
*GitHub*: [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L59), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L85)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

61       function onReceive(
62           bytes calldata zetaTxSenderAddress,
63           uint256 sourceChainId,
64           address destinationAddress,
65           uint256 zetaValue,
66           bytes calldata message,
67           bytes32 internalSendHash
68:      ) external override onlyTssAddress {

87       function onRevert(
88           address zetaTxSenderAddress,
89           uint256 sourceChainId,
90           bytes calldata destinationAddress,
91           uint256 destinationChainId,
92           uint256 remainingZetaValue,
93           bytes calldata message,
94           bytes32 internalSendHash
95:      ) external override whenNotPaused onlyTssAddress {

```
*GitHub*: [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L68), [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L95)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

71       constructor(
72           address zetaToken_,
73           address pancakeV3Router_,
74           address uniswapV3Factory_,
75           address WETH9Address_,
76           uint24 zetaPoolFee_,
77           uint24 tokenPoolFee_
78:      ) {

```
*GitHub*: [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L78)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

42       constructor(
43           address zetaToken_,
44           address uniswapV3Router_,
45           address uniswapV3Factory_,
46           address WETH9Address_,
47           uint24 zetaPoolFee_,
48           uint24 tokenPoolFee_
49:      ) {

```
*GitHub*: [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L49)

```solidity
File: contracts/zevm/SystemContract.sol

67       function depositAndCall(
68           zContext calldata context,
69           address zrc20,
70           uint256 amount,
71           address target,
72           bytes calldata message
73:      ) external {

```
*GitHub*: [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L73)

```solidity
File: contracts/zevm/ZRC20.sol

60       constructor(
61           string memory name_,
62           string memory symbol_,
63           uint8 decimals_,
64           uint256 chainid_,
65           CoinType coinType_,
66           uint256 gasLimit_,
67           address systemContractAddress_
68:      ) {

```
*GitHub*: [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L68)



### [N&#x2011;11] Consider using descriptive `constant`s when passing zero as a function argument
Passing zero as a function argument can sometimes result in a security issue (e.g. passing zero as the slippage parameter). Consider using a `constant` variable with a descriptive name, so it's clear that the argument is intentionally being used, and for the right reasons.

*There are 14 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

10:      bytes32 constant ZERO_BYTES = keccak256(new bytes(0));

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10-L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

117:             sqrtPriceLimitX96: 0

169:             sqrtPriceLimitX96: 0

```
*GitHub*: [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L117-L117), [169](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L169-L169)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

82:          address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);

85:              tokenIn: address(0),

112:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);

115:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);

148:         address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);

179:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);

182:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);

```
*GitHub*: [82](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L82-L82), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L85-L85), [112](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L112-L112), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L115-L115), [148](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L148-L148), [179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L179-L179), [182](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L182-L182)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

89:              sqrtPriceLimitX96: 0

143:             sqrtPriceLimitX96: 0

```
*GitHub*: [89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L89-L89), [143](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L143-L143)

```solidity
File: contracts/zevm/ZRC20.sol

196:         emit Transfer(address(0), account, amount);

208:         emit Transfer(account, address(0), amount);

```
*GitHub*: [196](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L196-L196), [208](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L208-L208)



### [N&#x2011;12] Consider using named mappings
Consider moving to solidity version 0.8.18 or later, and using [named mappings](https://ethereum.stackexchange.com/a/145555) to make it easier to understand the purpose of each mapping

*There are 8 instances of this issue:*

```solidity
File: contracts/evm/ERC20Custody.sol

36:      mapping(IERC20 => bool) public whitelisted;

```
*GitHub*: [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36-L36)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

21:      mapping(uint256 => bytes) public interactorsByChainId;

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L21-L21)

```solidity
File: contracts/zevm/SystemContract.sol

24:      mapping(uint256 => uint256) public gasPriceByChainId;

26:      mapping(uint256 => address) public gasCoinZRC20ByChainId;

28:      mapping(uint256 => address) public gasZetaPoolByChainId;

```
*GitHub*: [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L24-L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L26-L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L28-L28)

```solidity
File: contracts/zevm/ZRC20.sol

34:      mapping(address => uint256) private _balances;

35:      mapping(address => mapping(address => uint256)) private _allowances;

35:      mapping(address => mapping(address => uint256)) private _allowances;

```
*GitHub*: [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L34-L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35-L35), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35-L35)



### [N&#x2011;13] Consider using named returns
Using named returns makes the code more self-documenting, makes it easier to fill out NatSpec, and in some cases can save gas. The cases below are where there currently is at most one return statement, which is ideal for named returns.

*There are 80 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ZetaConnector.eth.sol

23:      function getLockedAmount() external view returns (uint256) {

```
*GitHub*: [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23-L23)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

27:      function getLockedAmount() external view returns (uint256) {

```
*GitHub*: [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27-L27)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

83:      function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89           uint256 inputTokenAmount
90:      ) external returns (uint256);

92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96:      ) external returns (uint256);

98       function getTokenFromZeta(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address outputToken,
102          uint256 zetaTokenAmount
103:     ) external returns (uint256);

105:     function hasZetaLiquidity() external view returns (bool);

```
*GitHub*: [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83-L83), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85-L90), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92-L96), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98-L103), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L105-L105)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

50:      function _isValidChainId(uint256 chainId) internal view returns (bool) {

```
*GitHub*: [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L50-L50)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

103      function getZetaFromEth(
104          address destinationAddress,
105          uint256 minAmountOut
106:     ) external payable override returns (uint256) {

126      function getZetaFromToken(
127          address destinationAddress,
128          uint256 minAmountOut,
129          address inputToken,
130          uint256 inputTokenAmount
131:     ) external override returns (uint256) {

151      function getEthFromZeta(
152          address destinationAddress,
153          uint256 minAmountOut,
154          uint256 zetaTokenAmount
155:     ) external override returns (uint256) {

184      function getTokenFromZeta(
185          address destinationAddress,
186          uint256 minAmountOut,
187          address outputToken,
188          uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {

```
*GitHub*: [103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L106), [126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L131), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L155), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L189)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

99       function getZetaFromToken(
100          address destinationAddress,
101          uint256 minAmountOut,
102          address inputToken,
103          uint256 inputTokenAmount
104:     ) external override returns (uint256) {

136      function getEthFromZeta(
137          address destinationAddress,
138          uint256 minAmountOut,
139          uint256 zetaTokenAmount
140:     ) external override returns (uint256) {

166      function getTokenFromZeta(
167          address destinationAddress,
168          uint256 minAmountOut,
169          address outputToken,
170          uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {

203:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L77), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L104), [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L140), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L171), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L203)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

34       function getZetaFromEth(
35           address destinationAddress,
36           uint256 minAmountOut
37:      ) external payable override returns (uint256) {

58       function getZetaFromToken(
59           address destinationAddress,
60           uint256 minAmountOut,
61           address inputToken,
62           uint256 inputTokenAmount
63:      ) external override returns (uint256) {

95       function getEthFromZeta(
96           address destinationAddress,
97           uint256 minAmountOut,
98           uint256 zetaTokenAmount
99:      ) external override returns (uint256) {

124      function getTokenFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          address outputToken,
128          uint256 zetaTokenAmount
129:     ) external override returns (uint256) {

```
*GitHub*: [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34-L37), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L63), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L99), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L129)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

98       function getZetaFromToken(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address inputToken,
102          uint256 inputTokenAmount
103:     ) external override returns (uint256) {

124      function getEthFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          uint256 zetaTokenAmount
128:     ) external override returns (uint256) {

158      function getTokenFromZeta(
159          address destinationAddress,
160          uint256 minAmountOut,
161          address outputToken,
162          uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {

```
*GitHub*: [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L77), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L103), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L128), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L163)

```solidity
File: contracts/zevm/Interfaces.sol

8:       function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

10:      function wZetaContractAddress() external view returns (address);

12:      function uniswapv2FactoryAddress() external view returns (address);

14:      function gasPriceByChainId(uint256 chainID) external view returns (uint256);

16:      function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

18:      function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

22:      function totalSupply() external view returns (uint256);

24:      function balanceOf(address account) external view returns (uint256);

26:      function transfer(address recipient, uint256 amount) external returns (bool);

28:      function allowance(address owner, address spender) external view returns (uint256);

30:      function approve(address spender, uint256 amount) external returns (bool);

32:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

34:      function deposit(address to, uint256 amount) external returns (bool);

36:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

38:      function withdrawGasFee() external view returns (address, uint256);

50:      function name() external view returns (string memory);

52:      function symbol() external view returns (string memory);

54:      function decimals() external view returns (uint8);

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8-L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18-L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22-L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24-L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26-L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28-L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30-L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32-L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34-L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36-L36), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L38-L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L50-L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L52-L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L54-L54)

```solidity
File: contracts/zevm/ZRC20.sol

41:      function _msgSender() internal view virtual returns (address) {

45:      function _msgData() internal view virtual returns (bytes calldata) {

83:      function name() public view virtual override returns (string memory) {

91:      function symbol() public view virtual override returns (string memory) {

99:      function decimals() public view virtual override returns (uint8) {

107:     function totalSupply() public view virtual override returns (uint256) {

116:     function balanceOf(address account) public view virtual override returns (uint256) {

125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {

135:     function allowance(address owner, address spender) public view virtual override returns (uint256) {

145:     function approve(address spender, uint256 amount) public virtual override returns (bool) {

157:     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {

173:     function burn(uint256 amount) external returns (bool) {

225:     function deposit(address to, uint256 amount) external override returns (bool) {

236:     function withdrawGasFee() public view override returns (address, uint256) {

256:     function withdraw(bytes memory to, uint256 amount) external override returns (bool) {

```
*GitHub*: [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L41-L41), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L45-L45), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83-L83), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91-L91), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99-L99), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L107-L107), [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L116-L116), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125-L125), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135-L135), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145-L145), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157-L157), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173-L173), [225](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225-L225), [236](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236-L236), [256](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256-L256)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

50:      function transferFrom(address src, address dst, uint wad) external returns (bool);

```
*GitHub*: [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50-L50)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

5:       function factory() external pure returns (address);

7:       function WETH() external pure returns (address);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5-L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7-L7)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

10:      function totalSupply() external view returns (uint);

12:      function balanceOf(address owner) external view returns (uint);

14:      function allowance(address owner, address spender) external view returns (uint);

16:      function approve(address spender, uint wad) external returns (bool);

18:      function transfer(address to, uint wad) external returns (bool);

20:      function transferFrom(address from, address to, uint wad) external returns (bool);

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18-L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20-L20)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

5:       function totalSupply() external view returns (uint256);

7:       function balanceOf(address account) external view returns (uint256);

9:       function transfer(address recipient, uint256 amount) external returns (bool);

11:      function allowance(address owner, address spender) external view returns (uint256);

13:      function approve(address spender, uint256 amount) external returns (bool);

15:      function decreaseAllowance(address spender, uint256 amount) external returns (bool);

17:      function increaseAllowance(address spender, uint256 amount) external returns (bool);

19:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

21:      function deposit(address to, uint256 amount) external returns (bool);

23:      function burn(address account, uint256 amount) external returns (bool);

25:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

27:      function withdrawGasFee() external view returns (address, uint256);

29:      function PROTOCOL_FEE() external view returns (uint256);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5-L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7-L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9-L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11-L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17-L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19-L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29-L29)

</details>





### [N&#x2011;14] Constants in comparisons should appear on the left side
Doing so will prevent [typo bugs](https://www.moserware.com/2008/01/constants-on-left-are-better-but-this.html) where the first '!', '>', '<', or '=' at the beginning of the operator is missing.

*There are 26 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

93:          if (zetaFee_ == 0) {

177:         if (zetaFee != 0 && address(zeta) != address(0)) {

```
*GitHub*: [93](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L93-L93), [177](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L177-L177)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

63:          if (message.length > 0) {

89:          if (message.length > 0) {

```
*GitHub*: [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L63-L63), [89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L89-L89)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

72:          if (message.length > 0) {

100:         if (message.length > 0) {

```
*GitHub*: [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L72-L72), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L100-L100)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

108:         if (msg.value == 0) revert InputCantBeZero();

133:         if (inputTokenAmount == 0) revert InputCantBeZero();

157:         if (zetaTokenAmount == 0) revert InputCantBeZero();

191:         if (zetaTokenAmount == 0) revert InputCantBeZero();

218:         return pool.liquidity() > 0;

```
*GitHub*: [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L108-L108), [133](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L133-L133), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L157-L157), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191-L191), [218](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L218-L218)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

79:          if (msg.value == 0) revert InputCantBeZero();

106:         if (inputTokenAmount == 0) revert InputCantBeZero();

142:         if (zetaTokenAmount == 0) revert InputCantBeZero();

173:         if (zetaTokenAmount == 0) revert InputCantBeZero();

```
*GitHub*: [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L79-L79), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L106-L106), [142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L142-L142), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173-L173)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

39:          if (msg.value == 0) revert InputCantBeZero();

65:          if (inputTokenAmount == 0) revert InputCantBeZero();

101:         if (zetaTokenAmount == 0) revert InputCantBeZero();

131:         if (zetaTokenAmount == 0) revert InputCantBeZero();

168:             return amounts[path.length - 1] > 0;

```
*GitHub*: [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L39-L39), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L65-L65), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L101-L101), [131](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131-L131), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L168-L168)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

79:          if (msg.value == 0) revert InputCantBeZero();

105:         if (inputTokenAmount == 0) revert InputCantBeZero();

130:         if (zetaTokenAmount == 0) revert InputCantBeZero();

165:         if (zetaTokenAmount == 0) revert InputCantBeZero();

193:         return pool.liquidity() > 0;

```
*GitHub*: [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79-L79), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105-L105), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130-L130), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165-L165), [193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L193-L193)

```solidity
File: contracts/zevm/ZRC20.sol

242:         if (gasPrice == 0) {

```
*GitHub*: [242](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L242-L242)

</details>





### [N&#x2011;15] Contract should expose an `interface`
The `contract`s should expose an `interface` so that other projects can more easily integrate with it, without having to develop their own non-standard variants.

*There are 12 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

/// @audit  paused(), TSSAddress(), TSSAddressUpdater(), zetaFee(), zetaMaxFee(), zeta(), whitelisted(), updateTSSAddress(), updateZetaFee(), renounceTSSAddressUpdater(), pause(), unpause(), whitelist(), unwhitelist(), deposit(), withdraw()
11:  contract ERC20Custody is ReentrancyGuard {

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11-L11)

```solidity
File: contracts/evm/Zeta.non-eth.sol

/// @audit  connectorAddress(), tssAddress(), tssAddressUpdater(), updateTssAndConnectorAddresses(), renounceTssAddressUpdater()
10:  contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10)

```solidity
File: contracts/evm/ZetaConnector.base.sol

/// @audit  zetaToken(), pauserAddress(), tssAddress(), tssAddressUpdater(), updatePauserAddress(), updateTssAddress(), renounceTssAddressUpdater(), pause(), unpause(), send(), onReceive(), onRevert()
15:  contract ZetaConnectorBase is ConnectorErrors, Pausable {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

/// @audit  getLockedAmount()
15:  contract ZetaConnectorEth is ZetaConnectorBase {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15-L15)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

/// @audit  maxSupply(), getLockedAmount(), setMaxSupply()
15:  contract ZetaConnectorNonEth is ZetaConnectorBase {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15-L15)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

/// @audit  zetaPoolFee(), tokenPoolFee(), WETH9Address(), zetaToken(), pancakeV3Router(), uniswapV3Factory()
56:  contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56-L56)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit  zetaToken(), tridentRouter(), poolFactory()
33:  contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {

```
*GitHub*: [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

/// @audit  zetaToken()
17:  contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

/// @audit  zetaPoolFee(), tokenPoolFee(), WETH9Address(), zetaToken(), uniswapV3Router(), uniswapV3Factory()
27:  contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27-L27)

```solidity
File: contracts/zevm/SystemContract.sol

/// @audit  gasPriceByChainId(), gasCoinZRC20ByChainId(), gasZetaPoolByChainId(), FUNGIBLE_MODULE_ADDRESS(), uniswapv2FactoryAddress(), uniswapv2Router02Address(), wZetaContractAddress(), zetaConnectorZEVMAddress(), depositAndCall(), uniswapv2PairFor(), setGasPrice(), setGasCoinZRC20(), setGasZetaPool(), setWZETAContractAddress(), setConnectorZEVMAddress()
22   contract SystemContract is SystemContractErrors {
23:      /// @notice Map to know the gas price of each chain given a chain id.

```
*GitHub*: [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22-L23)

```solidity
File: contracts/zevm/ZRC20.sol

/// @audit  FUNGIBLE_MODULE_ADDRESS(), CHAIN_ID(), COIN_TYPE(), SYSTEM_CONTRACT_ADDRESS(), GAS_LIMIT(), PROTOCOL_FLAT_FEE(), burn(), updateSystemContractAddress(), updateGasLimit(), updateProtocolFlatFee()
20   contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:      /// @notice Fungible address is always the same, maintained at the protocol level

```
*GitHub*: [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L21)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

/// @audit  FUNGIBLE_MODULE_ADDRESS(), wzeta(), send(), setWzetaAddress()
55   contract ZetaConnectorZEVM is ZetaInterfaces {
56:      /// @notice Contract custom errors.

```
*GitHub*: [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55-L56)

</details>





### [N&#x2011;16] Contracts should have full test coverage
While 100% code coverage does not guarantee that there are no bugs, it often will catch easy-to-find bugs, and will ensure that there are fewer regressions when the code invariably has to be modified. Furthermore, in order to get full coverage, code authors will often have to re-organize their code so that it is more modular, so that each component can be tested separately, which reduces interdependencies between modules and layers, and makes for code that is easier to reason about and audit.

*There is one instance of this issue:*

```solidity
File: Various Files


```
*GitHub*: [various](https://github.com/code-423n4/2023-11-zetachain/tree/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts)



### [N&#x2011;17] Contracts/libraries/interfaces should each be defined in separate files
This helps to make tracking changes across commits easier, among other reasons. They can be combined into a single file later by importing multiple contracts, and using that file as the common import.

*There are 27 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

/// @audit ZetaInterfaces,ZetaConnector,ZetaReceiver,ZetaTokenConsumer,ZetaCommonErrors
4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

/// @audit ZetaInterfaces,ZetaConnector,ZetaReceiver,ZetaTokenConsumer,ZetaCommonErrors
49   interface ZetaConnector {
50       /**
51        * @dev Sending value and data cross-chain is as easy as calling connector.send(SendInput)
52:       */

/// @audit ZetaInterfaces,ZetaConnector,ZetaReceiver,ZetaTokenConsumer,ZetaCommonErrors
56   interface ZetaReceiver {
57       /**
58        * @dev onZetaMessage is called when a cross-chain message reaches a contract
59:       */

/// @audit ZetaInterfaces,ZetaConnector,ZetaReceiver,ZetaTokenConsumer,ZetaCommonErrors
77:  interface ZetaTokenConsumer {

/// @audit ZetaInterfaces,ZetaConnector,ZetaReceiver,ZetaTokenConsumer,ZetaCommonErrors
108: interface ZetaCommonErrors {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49-L52), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L59), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77-L77), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108-L108)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

/// @audit WETH9,ISwapRouterPancake,ZetaTokenConsumerPancakeV3,ZetaTokenConsumerUniV3Errors
12:  interface ZetaTokenConsumerUniV3Errors {

/// @audit WETH9,ISwapRouterPancake,ZetaTokenConsumerPancakeV3,ZetaTokenConsumerUniV3Errors
20:  interface WETH9 {

/// @audit WETH9,ISwapRouterPancake,ZetaTokenConsumerPancakeV3,ZetaTokenConsumerUniV3Errors
24:  interface ISwapRouterPancake is IUniswapV3SwapCallback {

/// @audit WETH9,ISwapRouterPancake,ZetaTokenConsumerPancakeV3,ZetaTokenConsumerUniV3Errors
56:  contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20-L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24-L24), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56-L56)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit ZetaTokenConsumerTridentErrors,WETH9,ZetaTokenConsumerTrident
12:  interface ZetaTokenConsumerTridentErrors {

/// @audit ZetaTokenConsumerTridentErrors,WETH9,ZetaTokenConsumerTrident
20:  interface WETH9 {

/// @audit ZetaTokenConsumerTridentErrors,WETH9,ZetaTokenConsumerTrident
33:  contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20-L20), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

/// @audit ZetaTokenConsumerUniV2,ZetaTokenConsumerUniV2Errors
10:  interface ZetaTokenConsumerUniV2Errors {

/// @audit ZetaTokenConsumerUniV2,ZetaTokenConsumerUniV2Errors
17:  contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

/// @audit WETH9,ZetaTokenConsumerUniV3,ZetaTokenConsumerUniV3Errors
12:  interface ZetaTokenConsumerUniV3Errors {

/// @audit WETH9,ZetaTokenConsumerUniV3,ZetaTokenConsumerUniV3Errors
20:  interface WETH9 {

/// @audit WETH9,ZetaTokenConsumerUniV3,ZetaTokenConsumerUniV3Errors
27:  contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27-L27)

```solidity
File: contracts/zevm/Interfaces.sol

/// @audit ISystem,IZRC20,IZRC20Metadata
7:   interface ISystem {

/// @audit ISystem,IZRC20,IZRC20Metadata
21:  interface IZRC20 {

/// @audit ISystem,IZRC20,IZRC20Metadata
49:  interface IZRC20Metadata is IZRC20 {

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L7-L7), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21-L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49-L49)

```solidity
File: contracts/zevm/SystemContract.sol

/// @audit SystemContractErrors,SystemContract
10:  interface SystemContractErrors {

/// @audit SystemContractErrors,SystemContract
22   contract SystemContract is SystemContractErrors {
23:      /// @notice Map to know the gas price of each chain given a chain id.

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10-L10), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22-L23)

```solidity
File: contracts/zevm/ZRC20.sol

/// @audit ZRC20Errors,ZRC20
8    interface ZRC20Errors {
9:       // @dev: Error thrown when caller is not the fungible module

/// @audit ZRC20Errors,ZRC20
20   contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:      /// @notice Fungible address is always the same, maintained at the protocol level

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8-L9), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L21)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

/// @audit ZetaInterfaces,WZETA,ZetaConnectorZEVM
4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

/// @audit ZetaInterfaces,WZETA,ZetaConnectorZEVM
49:  interface WZETA {

/// @audit ZetaInterfaces,WZETA,ZetaConnectorZEVM
55   contract ZetaConnectorZEVM is ZetaInterfaces {
56:      /// @notice Contract custom errors.

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55-L56)

</details>





### [N&#x2011;18] Custom error has no parameters showing error details
Consider adding parameters to the error to indicate which user or values caused the failure

*There are 42 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

14:      error NotWhitelisted();

15:      error NotPaused();

16:      error InvalidSender();

17:      error InvalidTSSUpdater();

18:      error ZeroAddress();

19:      error IsPaused();

20:      error ZetaMaxFeeExceeded();

21:      error ZeroFee();

```
*GitHub*: [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L15-L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L16-L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L17-L17), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L18-L18), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L19-L19), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L20-L20), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L21-L21)

```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

21:      error ZetaTransferError();

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L21-L21)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

21:      error InvalidAddress();

24:      error ZetaTransferError();

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L24-L24)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

9:       error InvalidDestinationChainId();

15:      error InvalidZetaMessageCall();

18:      error InvalidZetaRevertCall();

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L9-L9), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L18-L18)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

109:     error InvalidAddress();

```
*GitHub*: [109](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L109-L109)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

11:      error InputCantBeZero();

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L11-L11)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L17-L17)

```solidity
File: contracts/zevm/SystemContract.sol

11:      error CallerIsNotFungibleModule();

12:      error InvalidTarget();

13:      error CantBeIdenticalAddresses();

14:      error CantBeZeroAddress();

15:      error ZeroAddress();

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L12-L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L15-L15)

```solidity
File: contracts/zevm/ZRC20.sol

10:      error CallerIsNotFungibleModule();

11:      error InvalidSender();

12:      error GasFeeTransferFailed();

13:      error ZeroGasCoin();

14:      error ZeroGasPrice();

15:      error LowAllowance();

16:      error LowBalance();

17:      error ZeroAddress();

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L10-L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L12-L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L15-L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L16-L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L17-L17)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

57:      error OnlyWZETA();

58:      error WZETATransferFailed();

59:      error OnlyFungibleModule();

60:      error FailedZetaSent();

```
*GitHub*: [57](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L57-L57), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L58-L58), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L59-L59), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L60-L60)

</details>





### [N&#x2011;19] Duplicated `require()`/`revert()` checks should be refactored to a modifier or function
The compiler will inline the function, which will avoid `JUMP` instructions usually associated with functions

*There are 14 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/Zeta.non-eth.sol

77:           if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);

```
*GitHub*: [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L77)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

61:           if (!success) revert ZetaTransferError();

```
*GitHub*: [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L61)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

156:          if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

191:          if (zetaTokenAmount == 0) revert InputCantBeZero();

```
*GitHub*: [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L156), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

141:          if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

173:          if (zetaTokenAmount == 0) revert InputCantBeZero();

```
*GitHub*: [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L141), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

100:          if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

131:          if (zetaTokenAmount == 0) revert InputCantBeZero();

```
*GitHub*: [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L100), [131](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

129:          if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

165:          if (zetaTokenAmount == 0) revert InputCantBeZero();

```
*GitHub*: [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L129), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165)

```solidity
File: contracts/zevm/SystemContract.sol

74:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

169:          if (addr == address(0)) revert ZeroAddress();

```
*GitHub*: [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74), [169](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L169)

```solidity
File: contracts/zevm/ZRC20.sol

69:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

200:          if (account == address(0)) revert ZeroAddress();

```
*GitHub*: [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69), [200](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L200)

</details>





### [N&#x2011;20] Event is not properly `indexed`
Index event fields make the field more quickly accessible [to off-chain tools](https://ethereum.stackexchange.com/questions/40396/can-somebody-please-explain-the-concept-of-event-indexing) that parse events. This is especially useful when it comes to filtering based on an address. However, note that each index field costs extra gas during emission, so it's not necessarily best to index the maximum allowed per event (three fields). Where applicable, each `event` should use three `indexed` fields if there are three or more fields, and gas usage is not particularly of concern for the events in question. If there are fewer than three applicable fields, all of the applicable fields should be indexed.

*There are 23 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

38:       event Paused(address sender);

39:       event Unpaused(address sender);

44:       event RenouncedTSSUpdater(address TSSAddressUpdater_);

45:       event UpdatedTSSAddress(address TSSAddress_);

```
*GitHub*: [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45)

```solidity
File: contracts/evm/Zeta.non-eth.sol

27:       event TSSAddressUpdated(address callerAddress, address newTssAddress);

29:       event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

31:       event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);

```
*GitHub*: [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31)

```solidity
File: contracts/evm/ZetaConnector.base.sol

34        event ZetaSent(
35            address sourceTxOriginAddress,
36            address indexed zetaTxSenderAddress,
37            uint256 indexed destinationChainId,
38            bytes destinationAddress,
39            uint256 zetaValueAndGas,
40            uint256 destinationGasLimit,
41            bytes message,
42            bytes zetaParams
43:       );

54        event ZetaReverted(
55            address zetaTxSenderAddress,
56            uint256 sourceChainId,
57            uint256 indexed destinationChainId,
58            bytes destinationAddress,
59            uint256 remainingZetaValue,
60            bytes message,
61            bytes32 indexed internalSendHash
62:       );

64:       event TSSAddressUpdated(address callerAddress, address newTssAddress);

66:       event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

68:       event PauserAddressUpdated(address callerAddress, address newTssAddress);

```
*GitHub*: [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34-L43), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L62), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

18:       event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);

```
*GitHub*: [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

79:       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

81:       event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);

```
*GitHub*: [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81)

```solidity
File: contracts/zevm/Interfaces.sol

44:       event UpdatedSystemContract(address systemContract);

```
*GitHub*: [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44)

```solidity
File: contracts/zevm/SystemContract.sol

43:       event SetGasCoin(uint256, address);

44:       event SetGasZetaPool(uint256, address);

45:       event SetWZeta(address);

46:       event SetConnectorZEVM(address);

```
*GitHub*: [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

67        event ZetaSent(
68            address sourceTxOriginAddress,
69            address indexed zetaTxSenderAddress,
70            uint256 indexed destinationChainId,
71            bytes destinationAddress,
72            uint256 zetaValueAndGas,
73            uint256 destinationGasLimit,
74            bytes message,
75            bytes zetaParams
76:       );

77:       event SetWZETA(address wzeta_);

```
*GitHub*: [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

35:       event UpdatedSystemContract(address systemContract);

```
*GitHub*: [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35)

</details>





### [N&#x2011;21] Events should use parameters to convey information
For example, rather than using `event Paused()` and `event Unpaused()`, use `event PauseState(address indexed whoChangedIt, bool wasPaused, bool isNowPaused)`

*There is one instance of this issue:*

```solidity
File: contracts/zevm/SystemContract.sol

41:      event SystemContractDeployed();

```
*GitHub*: [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L41-L41)



### [N&#x2011;22] Expressions for constant values should use `immutable` rather than `constant`
While it does not save gas for some simple binary expressions because the compiler knows that developers often make this mistake, it's still best to use the right tool for the task at hand. There is a difference between `constant` variables and `immutable` variables, and they should each be used in their appropriate contexts. `constants` should be used for literal values written into the code, and `immutable` variables should be used for expressions, or values calculated in, or passed into the constructor.

*There are 2 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

10:      bytes32 constant ZERO_BYTES = keccak256(new bytes(0));

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10-L10)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

63:      address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);

```
*GitHub*: [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63-L63)



### [N&#x2011;23] Function state mutability can be restricted to `pure`


*There is one instance of this issue:*

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

203:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L203)



### [N&#x2011;24] Import declarations should import specific identifiers, rather than the whole file
Using import declarations of the form `import {<identifier_name>} from "some/file.sol"` avoids polluting the symbol namespace making flattened files smaller, and speeds up compilation (but does not save any gas)

*There are 49 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

5:    import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

6:    import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

7:    import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L7)

```solidity
File: contracts/evm/Zeta.eth.sol

4:    import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L4)

```solidity
File: contracts/evm/Zeta.non-eth.sol

4:    import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

6:    import "./interfaces/ZetaErrors.sol";

8:    import "./interfaces/ZetaNonEthInterface.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L6), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L8)

```solidity
File: contracts/evm/ZetaConnector.base.sol

4:    import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

5:    import "@openzeppelin/contracts/security/Pausable.sol";

7:    import "./interfaces/ConnectorErrors.sol";

8:    import "./interfaces/ZetaInterfaces.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L8)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

4:    import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

6:    import "./interfaces/ConnectorErrors.sol";

7:    import "./ZetaConnector.base.sol";

8:    import "./interfaces/ZetaInterfaces.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L8)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

4:    import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

6:    import "./ZetaConnector.base.sol";

7:    import "./interfaces/ZetaInterfaces.sol";

8:    import "./interfaces/ZetaNonEthInterface.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L8)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

4:    import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L4)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

4:    import "@openzeppelin/contracts/access/Ownable2Step.sol";

6:    import "../interfaces/ZetaInterfaces.sol";

7:    import "../interfaces/ZetaInteractorErrors.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L7)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

4:    import "@openzeppelin/contracts/interfaces/IERC20.sol";

5:    import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6:    import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

7:    import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";

8:    import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

10:   import "../interfaces/ZetaInterfaces.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

4:    import "@openzeppelin/contracts/interfaces/IERC20.sol";

5:    import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6:    import "@uniswap/v3-periphery/contracts/interfaces/IQuoter.sol";

8:    import "../interfaces/ZetaInterfaces.sol";

9:    import "./interfaces/TridentConcentratedLiquidityPoolFactory.sol";

10:   import "./interfaces/TridentIPoolRouter.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L6), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L8), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L9), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

4:    import "@openzeppelin/contracts/interfaces/IERC20.sol";

5:    import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6:    import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

8:    import "../interfaces/ZetaInterfaces.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L6), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L8)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

4:    import "@openzeppelin/contracts/interfaces/IERC20.sol";

5:    import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6:    import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

7:    import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";

8:    import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

10:   import "../interfaces/ZetaInterfaces.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L10)

```solidity
File: contracts/zevm/SystemContract.sol

4:    import "./interfaces/zContract.sol";

5:    import "./interfaces/IZRC20.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L5)

```solidity
File: contracts/zevm/ZRC20.sol

3:    import "./Interfaces.sol";

```
*GitHub*: [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L3)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

4:    import "./IUniswapV2Router01.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L4)

</details>





### [N&#x2011;25] Imports could be organized more systematically
The contract's interface should be imported first, followed by each of the interfaces it uses, followed by all other files. The examples below do not follow this layout.

*There are 4 instances of this issue:*

```solidity
File: contracts/evm/Zeta.non-eth.sol

8:   import "./interfaces/ZetaNonEthInterface.sol";

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L8-L8)

```solidity
File: contracts/evm/ZetaConnector.base.sol

8:   import "./interfaces/ZetaInterfaces.sol";

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L8-L8)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

8:   import "./interfaces/ZetaNonEthInterface.sol";

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L8-L8)

```solidity
File: contracts/zevm/SystemContract.sol

5:   import "./interfaces/IZRC20.sol";

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L5-L5)



### [N&#x2011;26] Inconsistent spacing in comments
Some lines use `// x` and some use `//x`. The instances below point out the usages that don't follow the majority, within each file

*There is one instance of this issue:*

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

216:          //@dev: if pool does exist, get its liquidity

```
*GitHub*: [216](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L216)



### [N&#x2011;27] Interfaces should be defined in separate files from their usage
The interfaces below should be defined in separate files, so that it's easier for future projects to import them, and to avoid duplication later on if they need to be used elsewhere in the project

*There are 12 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

24:  interface ISwapRouterPancake is IUniswapV3SwapCallback {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20-L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24-L24)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

12:  interface ZetaTokenConsumerTridentErrors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

10:  interface ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20)

```solidity
File: contracts/zevm/Interfaces.sol

21:  interface IZRC20 {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21-L21)

```solidity
File: contracts/zevm/SystemContract.sol

10:  interface SystemContractErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10-L10)

```solidity
File: contracts/zevm/ZRC20.sol

8    interface ZRC20Errors {
9:       // @dev: Error thrown when caller is not the fungible module

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8-L9)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49:  interface WZETA {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49)

</details>





### [N&#x2011;28] Interfaces should be indicated with an `I` prefix in the contract name


*There are 22 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

7:    interface ConnectorErrors {

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

7:    interface ZetaErrors {

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

7:    interface ZetaInteractorErrors {

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

4:    interface ZetaInterfaces {

49:   interface ZetaConnector {

56:   interface ZetaReceiver {

77:   interface ZetaTokenConsumer {

108:  interface ZetaCommonErrors {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

9:    interface ZetaNonEthInterface is IERC20 {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

12:   interface ZetaTokenConsumerUniV3Errors {

20:   interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

12:   interface ZetaTokenConsumerTridentErrors {

20:   interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

10:   interface ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

12:   interface ZetaTokenConsumerUniV3Errors {

20:   interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

16:   interface ConcentratedLiquidityPoolFactory {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16)

```solidity
File: contracts/zevm/SystemContract.sol

10:   interface SystemContractErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10)

```solidity
File: contracts/zevm/ZRC20.sol

8:    interface ZRC20Errors {

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

4:    interface ZetaInterfaces {

49:   interface WZETA {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49)

```solidity
File: contracts/zevm/interfaces/zContract.sol

10:   interface zContract {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10)

</details>





### [N&#x2011;29] Interfaces should use floating version pragmas
If the file contains non-interfaces as well, the interfaces should be moved to a separate file.

*There are 29 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

/// @audit ConnectorErrors
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L2-L2)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

/// @audit ZetaErrors
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L2-L2)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

/// @audit ZetaInteractorErrors
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L2-L2)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

/// @audit ZetaInterfaces
/// @audit ZetaConnector
/// @audit ZetaReceiver
/// @audit ZetaTokenConsumer
/// @audit ZetaCommonErrors
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2-L2)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

/// @audit ZetaNonEthInterface
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2-L2)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

/// @audit ZetaTokenConsumerUniV3Errors
/// @audit WETH9
/// @audit ISwapRouterPancake
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L2-L2)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit ZetaTokenConsumerTridentErrors
/// @audit WETH9
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L2-L2)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

/// @audit ZetaTokenConsumerUniV2Errors
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L2-L2)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

/// @audit ZetaTokenConsumerUniV3Errors
/// @audit WETH9
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L2-L2)

```solidity
File: contracts/zevm/Interfaces.sol

/// @audit ISystem
/// @audit IZRC20
/// @audit IZRC20Metadata
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L2-L2)

```solidity
File: contracts/zevm/SystemContract.sol

/// @audit SystemContractErrors
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L2-L2)

```solidity
File: contracts/zevm/ZRC20.sol

/// @audit ZRC20Errors
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L2-L2)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

/// @audit ZetaInterfaces
/// @audit WZETA
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L2-L2), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L2-L2)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

/// @audit IUniswapV2Router01
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L2-L2)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

/// @audit IUniswapV2Router02
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L2-L2)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

/// @audit IWETH9
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L2-L2)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

/// @audit IZRC20
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L2-L2)

```solidity
File: contracts/zevm/interfaces/zContract.sol

/// @audit zContract
2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L2-L2)

</details>





### [N&#x2011;30] Missing event for critical parameter change
Events help non-contract tools to track changes

*There is one instance of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

/// @audit interactorsByChainId:  setInteractorByChainId()
54:      function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {

```
*GitHub*: [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)



### [N&#x2011;31] Mixed usage of `int`/`uint` with `int256`/`uint256`
`int256`/`uint256` are the preferred type names (they're what are used for function signatures), so they should be used consistently

*There are 100 instances of this issue:*

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

50:      function transferFrom(address src, address dst, uint wad) external returns (bool);

52:      function withdraw(uint wad) external;

```
*GitHub*: [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50-L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52-L52)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

12:          uint amountADesired,

13:          uint amountBDesired,

14:          uint amountAMin,

15:          uint amountBMin,

17:          uint deadline

18:      ) external returns (uint amountA, uint amountB, uint liquidity);

18:      ) external returns (uint amountA, uint amountB, uint liquidity);

18:      ) external returns (uint amountA, uint amountB, uint liquidity);

22:          uint amountTokenDesired,

23:          uint amountTokenMin,

24:          uint amountETHMin,

26:          uint deadline

27:      ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

27:      ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

27:      ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

32:          uint liquidity,

33:          uint amountAMin,

34:          uint amountBMin,

36:          uint deadline

37:      ) external returns (uint amountA, uint amountB);

37:      ) external returns (uint amountA, uint amountB);

41:          uint liquidity,

42:          uint amountTokenMin,

43:          uint amountETHMin,

45:          uint deadline

46:      ) external returns (uint amountToken, uint amountETH);

46:      ) external returns (uint amountToken, uint amountETH);

51:          uint liquidity,

52:          uint amountAMin,

53:          uint amountBMin,

55:          uint deadline,

60:      ) external returns (uint amountA, uint amountB);

60:      ) external returns (uint amountA, uint amountB);

64:          uint liquidity,

65:          uint amountTokenMin,

66:          uint amountETHMin,

68:          uint deadline,

73:      ) external returns (uint amountToken, uint amountETH);

73:      ) external returns (uint amountToken, uint amountETH);

76:          uint amountIn,

77:          uint amountOutMin,

80:          uint deadline

84:          uint amountOut,

85:          uint amountInMax,

88:          uint deadline

92:          uint amountOutMin,

95:          uint deadline

99:          uint amountOut,

100:         uint amountInMax,

103:         uint deadline

107:         uint amountIn,

108:         uint amountOutMin,

111:         uint deadline

115:         uint amountOut,

118:         uint deadline

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L12-L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L17-L17), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L18-L18), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L18-L18), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L18-L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L22-L22), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L23-L23), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L24-L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L26-L26), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L27-L27), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L27-L27), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L27-L27), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L32-L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L33-L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L34-L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L36-L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L37-L37), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L37-L37), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L43-L43), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L46-L46), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L46-L46), [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L51-L51), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L52-L52), [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L53-L53), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L55-L55), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L60-L60), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L60-L60), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L64-L64), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L65-L65), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L66-L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L68-L68), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L73-L73), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L73-L73), [76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L76-L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L77-L77), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L80-L80), [84](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L84-L84), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L85-L85), [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L88-L88), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L92-L92), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L95-L95), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L99-L99), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L100-L100), [103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L103-L103), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L107-L107), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L108-L108), [111](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L111-L111), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L115-L115), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L118-L118), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121-L121), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121-L121), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121-L121), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121-L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123-L123), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123-L123), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123-L123), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123-L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125-L125), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125-L125), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125-L125), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125-L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127-L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129-L129)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

9:           uint liquidity,

10:          uint amountTokenMin,

11:          uint amountETHMin,

13:          uint deadline

14:      ) external returns (uint amountETH);

18:          uint liquidity,

19:          uint amountTokenMin,

20:          uint amountETHMin,

22:          uint deadline,

27:      ) external returns (uint amountETH);

30:          uint amountIn,

31:          uint amountOutMin,

34:          uint deadline

38:          uint amountOutMin,

41:          uint deadline

45:          uint amountIn,

46:          uint amountOutMin,

49:          uint deadline

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L9-L9), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L10-L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L11-L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L14-L14), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L18-L18), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L19-L19), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L20-L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L22-L22), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L27-L27), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L30-L30), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L31-L31), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L34-L34), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L38-L38), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L41-L41), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L46-L46), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L49-L49)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

5:       event Approval(address indexed owner, address indexed spender, uint value);

6:       event Transfer(address indexed from, address indexed to, uint value);

7:       event Deposit(address indexed dst, uint wad);

8:       event Withdrawal(address indexed src, uint wad);

10:      function totalSupply() external view returns (uint);

12:      function balanceOf(address owner) external view returns (uint);

14:      function allowance(address owner, address spender) external view returns (uint);

16:      function approve(address spender, uint wad) external returns (bool);

18:      function transfer(address to, uint wad) external returns (bool);

20:      function transferFrom(address from, address to, uint wad) external returns (bool);

24:      function withdraw(uint wad) external;

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8-L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18-L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20-L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24-L24)



### [N&#x2011;32] Named imports of parent contracts are missing


*There are 28 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

/// @audit ReentrancyGuard
11:  contract ERC20Custody is ReentrancyGuard {

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11-L11)

```solidity
File: contracts/evm/Zeta.eth.sol

/// @audit ERC20
9:   contract ZetaEth is ERC20("Zeta", "ZETA") {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9-L9)

```solidity
File: contracts/evm/Zeta.non-eth.sol

/// @audit ZetaNonEthInterface
/// @audit ERC20Burnable
/// @audit ZetaErrors
10:  contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10)

```solidity
File: contracts/evm/ZetaConnector.base.sol

/// @audit ConnectorErrors
/// @audit Pausable
15:  contract ZetaConnectorBase is ConnectorErrors, Pausable {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

/// @audit ZetaConnectorBase
15:  contract ZetaConnectorEth is ZetaConnectorBase {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15-L15)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

/// @audit ZetaConnectorBase
15:  contract ZetaConnectorNonEth is ZetaConnectorBase {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15-L15)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

/// @audit IERC20
9:   interface ZetaNonEthInterface is IERC20 {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

/// @audit Ownable2Step
/// @audit ZetaInteractorErrors
9:   abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9-L9), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

/// @audit IUniswapV3SwapCallback
24:  interface ISwapRouterPancake is IUniswapV3SwapCallback {

/// @audit ZetaTokenConsumer
/// @audit ZetaTokenConsumerUniV3Errors
56:  contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24-L24), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56-L56), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56-L56)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit ZetaTokenConsumer
/// @audit ZetaTokenConsumerTridentErrors
33:  contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {

```
*GitHub*: [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

/// @audit ZetaTokenConsumer
/// @audit ZetaTokenConsumerUniV2Errors
17:  contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17-L17), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

/// @audit ZetaTokenConsumer
/// @audit ZetaTokenConsumerUniV3Errors
27:  contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27-L27), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27-L27)

```solidity
File: contracts/zevm/Interfaces.sol

/// @audit IZRC20
49:  interface IZRC20Metadata is IZRC20 {

```
*GitHub*: [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49-L49)

```solidity
File: contracts/zevm/SystemContract.sol

/// @audit SystemContractErrors
22:  contract SystemContract is SystemContractErrors {

```
*GitHub*: [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22-L22)

```solidity
File: contracts/zevm/ZRC20.sol

/// @audit IZRC20
/// @audit IZRC20Metadata
/// @audit ZRC20Errors
20:  contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {

```
*GitHub*: [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L20), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L20), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L20)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

/// @audit ZetaInterfaces
55:  contract ZetaConnectorZEVM is ZetaInterfaces {

```
*GitHub*: [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55-L55)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

/// @audit IUniswapV2Router01
6:   interface IUniswapV2Router02 is IUniswapV2Router01 {

```
*GitHub*: [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6-L6)

</details>





### [N&#x2011;33] Names of `interface`s should be prefixed with an `I`, or contain the word `Interface`


*There are 19 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

7    interface ConnectorErrors {
8:       // @dev Thrown when caller is not the address defined as paused address

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7-L8)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

7    interface ZetaErrors {
8:       // @dev Thrown when caller is not the address defined as TSS address

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7-L8)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

7    interface ZetaInteractorErrors {
8:       // @dev Thrown when try to send a message or tokens to a non whitelisted chain

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7-L8)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

49   interface ZetaConnector {
50       /**
51        * @dev Sending value and data cross-chain is as easy as calling connector.send(SendInput)
52:       */

56   interface ZetaReceiver {
57       /**
58        * @dev onZetaMessage is called when a cross-chain message reaches a contract
59:       */

77:  interface ZetaTokenConsumer {

108: interface ZetaCommonErrors {

```
*GitHub*: [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49-L52), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L59), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77-L77), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108-L108)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20-L20)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

12:  interface ZetaTokenConsumerTridentErrors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20-L20)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

10:  interface ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

16:  interface ConcentratedLiquidityPoolFactory {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16-L16)

```solidity
File: contracts/zevm/SystemContract.sol

10:  interface SystemContractErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10-L10)

```solidity
File: contracts/zevm/ZRC20.sol

8    interface ZRC20Errors {
9:       // @dev: Error thrown when caller is not the fungible module

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8-L9)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

49:  interface WZETA {

```
*GitHub*: [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49)

```solidity
File: contracts/zevm/interfaces/zContract.sol

10:  interface zContract {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10-L10)

</details>





### [N&#x2011;34] NatSpec: Contract declarations should have `@author` tags


*There are 45 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

11:  contract ERC20Custody is ReentrancyGuard {

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11-L11)

```solidity
File: contracts/evm/Zeta.eth.sol

9:   contract ZetaEth is ERC20("Zeta", "ZETA") {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9-L9)

```solidity
File: contracts/evm/Zeta.non-eth.sol

10:  contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10)

```solidity
File: contracts/evm/ZetaConnector.base.sol

15:  contract ZetaConnectorBase is ConnectorErrors, Pausable {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

15:  contract ZetaConnectorEth is ZetaConnectorBase {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15-L15)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

15:  contract ZetaConnectorNonEth is ZetaConnectorBase {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15-L15)

```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

7    interface ConnectorErrors {
8:       // @dev Thrown when caller is not the address defined as paused address

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7-L8)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

7    interface ZetaErrors {
8:       // @dev Thrown when caller is not the address defined as TSS address

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7-L8)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

7    interface ZetaInteractorErrors {
8:       // @dev Thrown when try to send a message or tokens to a non whitelisted chain

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7-L8)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49   interface ZetaConnector {
50       /**
51        * @dev Sending value and data cross-chain is as easy as calling connector.send(SendInput)
52:       */

56   interface ZetaReceiver {
57       /**
58        * @dev onZetaMessage is called when a cross-chain message reaches a contract
59:       */

77:  interface ZetaTokenConsumer {

108: interface ZetaCommonErrors {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49-L52), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L59), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77-L77), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108-L108)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

9:   interface ZetaNonEthInterface is IERC20 {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

9:   abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

24:  interface ISwapRouterPancake is IUniswapV3SwapCallback {

56:  contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20-L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24-L24), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56-L56)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

12:  interface ZetaTokenConsumerTridentErrors {

20:  interface WETH9 {

33:  contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20-L20), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

10:  interface ZetaTokenConsumerUniV2Errors {

17:  contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

27:  contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27-L27)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

16:  interface ConcentratedLiquidityPoolFactory {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16-L16)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

16:  interface IPoolRouter {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16-L16)

```solidity
File: contracts/zevm/Interfaces.sol

7:   interface ISystem {

21:  interface IZRC20 {

49:  interface IZRC20Metadata is IZRC20 {

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L7-L7), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21-L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49-L49)

```solidity
File: contracts/zevm/SystemContract.sol

10:  interface SystemContractErrors {

22   contract SystemContract is SystemContractErrors {
23:      /// @notice Map to know the gas price of each chain given a chain id.

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10-L10), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22-L23)

```solidity
File: contracts/zevm/ZRC20.sol

8    interface ZRC20Errors {
9:       // @dev: Error thrown when caller is not the fungible module

20   contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:      /// @notice Fungible address is always the same, maintained at the protocol level

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8-L9), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L21)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49:  interface WZETA {

55   contract ZetaConnectorZEVM is ZetaInterfaces {
56:      /// @notice Contract custom errors.

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55-L56)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

4:   interface IUniswapV2Router01 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

6:   interface IUniswapV2Router02 is IUniswapV2Router01 {

```
*GitHub*: [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6-L6)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

4:   interface IWETH9 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

4:   interface IZRC20 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/zContract.sol

10:  interface zContract {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10-L10)

</details>





### [N&#x2011;35] NatSpec: Contract declarations should have `@dev` tags
`@dev` is used to explain extra details to developers

*There are 28 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

11:  contract ERC20Custody is ReentrancyGuard {

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11-L11)

```solidity
File: contracts/evm/Zeta.non-eth.sol

10:  contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49   interface ZetaConnector {
50       /**
51        * @dev Sending value and data cross-chain is as easy as calling connector.send(SendInput)
52:       */

56   interface ZetaReceiver {
57       /**
58        * @dev onZetaMessage is called when a cross-chain message reaches a contract
59:       */

108: interface ZetaCommonErrors {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49-L52), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L59), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108-L108)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

9:   abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

24:  interface ISwapRouterPancake is IUniswapV3SwapCallback {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20-L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24-L24)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

12:  interface ZetaTokenConsumerTridentErrors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20-L20)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

10:  interface ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

16:  interface ConcentratedLiquidityPoolFactory {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16-L16)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

16:  interface IPoolRouter {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16-L16)

```solidity
File: contracts/zevm/Interfaces.sol

21:  interface IZRC20 {

49:  interface IZRC20Metadata is IZRC20 {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21-L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49-L49)

```solidity
File: contracts/zevm/ZRC20.sol

20   contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:      /// @notice Fungible address is always the same, maintained at the protocol level

```
*GitHub*: [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L21)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49:  interface WZETA {

55   contract ZetaConnectorZEVM is ZetaInterfaces {
56:      /// @notice Contract custom errors.

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55-L56)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

4:   interface IUniswapV2Router01 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

6:   interface IUniswapV2Router02 is IUniswapV2Router01 {

```
*GitHub*: [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6-L6)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

4:   interface IWETH9 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

4:   interface IZRC20 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/zContract.sol

10:  interface zContract {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10-L10)

</details>





### [N&#x2011;36] NatSpec: Contract declarations should have `@notice` tags
`@notice` is used to explain to end users what the contract does, and the compiler interprets `///` or `/**` comments (but not `//` or `/*`) as this tag if one wasn't explicitly provided. Note that the NatSpec comment must be _above_ the contract definition.

*There are 27 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/Zeta.non-eth.sol

10:  contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49   interface ZetaConnector {
50       /**
51        * @dev Sending value and data cross-chain is as easy as calling connector.send(SendInput)
52:       */

56   interface ZetaReceiver {
57       /**
58        * @dev onZetaMessage is called when a cross-chain message reaches a contract
59:       */

108: interface ZetaCommonErrors {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49-L52), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L59), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108-L108)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

9:   abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

24:  interface ISwapRouterPancake is IUniswapV3SwapCallback {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20-L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24-L24)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

12:  interface ZetaTokenConsumerTridentErrors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20-L20)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

10:  interface ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

16:  interface ConcentratedLiquidityPoolFactory {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16-L16)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

16:  interface IPoolRouter {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16-L16)

```solidity
File: contracts/zevm/Interfaces.sol

21:  interface IZRC20 {

49:  interface IZRC20Metadata is IZRC20 {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21-L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49-L49)

```solidity
File: contracts/zevm/ZRC20.sol

20   contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:      /// @notice Fungible address is always the same, maintained at the protocol level

```
*GitHub*: [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L21)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49:  interface WZETA {

55   contract ZetaConnectorZEVM is ZetaInterfaces {
56:      /// @notice Contract custom errors.

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55-L56)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

4:   interface IUniswapV2Router01 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

6:   interface IUniswapV2Router02 is IUniswapV2Router01 {

```
*GitHub*: [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6-L6)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

4:   interface IWETH9 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

4:   interface IZRC20 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/zContract.sol

10:  interface zContract {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10-L10)

</details>





### [N&#x2011;37] NatSpec: Contract declarations should have `@title` tags


*There are 44 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/Zeta.eth.sol

9:   contract ZetaEth is ERC20("Zeta", "ZETA") {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9-L9)

```solidity
File: contracts/evm/Zeta.non-eth.sol

10:  contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10)

```solidity
File: contracts/evm/ZetaConnector.base.sol

15:  contract ZetaConnectorBase is ConnectorErrors, Pausable {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

15:  contract ZetaConnectorEth is ZetaConnectorBase {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15-L15)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

15:  contract ZetaConnectorNonEth is ZetaConnectorBase {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15-L15)

```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

7    interface ConnectorErrors {
8:       // @dev Thrown when caller is not the address defined as paused address

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7-L8)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

7    interface ZetaErrors {
8:       // @dev Thrown when caller is not the address defined as TSS address

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7-L8)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

7    interface ZetaInteractorErrors {
8:       // @dev Thrown when try to send a message or tokens to a non whitelisted chain

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7-L8)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49   interface ZetaConnector {
50       /**
51        * @dev Sending value and data cross-chain is as easy as calling connector.send(SendInput)
52:       */

56   interface ZetaReceiver {
57       /**
58        * @dev onZetaMessage is called when a cross-chain message reaches a contract
59:       */

77:  interface ZetaTokenConsumer {

108: interface ZetaCommonErrors {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49-L52), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L59), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77-L77), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108-L108)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

9:   interface ZetaNonEthInterface is IERC20 {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

9:   abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

24:  interface ISwapRouterPancake is IUniswapV3SwapCallback {

56:  contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20-L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24-L24), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56-L56)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

12:  interface ZetaTokenConsumerTridentErrors {

20:  interface WETH9 {

33:  contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20-L20), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

10:  interface ZetaTokenConsumerUniV2Errors {

17:  contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

27:  contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27-L27)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

16:  interface ConcentratedLiquidityPoolFactory {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16-L16)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

16:  interface IPoolRouter {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16-L16)

```solidity
File: contracts/zevm/Interfaces.sol

7:   interface ISystem {

21:  interface IZRC20 {

49:  interface IZRC20Metadata is IZRC20 {

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L7-L7), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21-L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49-L49)

```solidity
File: contracts/zevm/SystemContract.sol

10:  interface SystemContractErrors {

22   contract SystemContract is SystemContractErrors {
23:      /// @notice Map to know the gas price of each chain given a chain id.

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10-L10), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22-L23)

```solidity
File: contracts/zevm/ZRC20.sol

8    interface ZRC20Errors {
9:       // @dev: Error thrown when caller is not the fungible module

20   contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:      /// @notice Fungible address is always the same, maintained at the protocol level

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8-L9), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L21)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49:  interface WZETA {

55   contract ZetaConnectorZEVM is ZetaInterfaces {
56:      /// @notice Contract custom errors.

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55-L56)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

4:   interface IUniswapV2Router01 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

6:   interface IUniswapV2Router02 is IUniswapV2Router01 {

```
*GitHub*: [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6-L6)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

4:   interface IWETH9 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

4:   interface IZRC20 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/zContract.sol

10:  interface zContract {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10-L10)

</details>





### [N&#x2011;38] NatSpec: Contract declarations should have descriptions
e.g. `@dev` or `@notice`, and it must appear above the contract definition braces in order to be identified by the compiler as NatSpec

*There are 27 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/Zeta.non-eth.sol

10:  contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49   interface ZetaConnector {
50       /**
51        * @dev Sending value and data cross-chain is as easy as calling connector.send(SendInput)
52:       */

56   interface ZetaReceiver {
57       /**
58        * @dev onZetaMessage is called when a cross-chain message reaches a contract
59:       */

108: interface ZetaCommonErrors {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49-L52), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L59), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108-L108)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

9:   abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

24:  interface ISwapRouterPancake is IUniswapV3SwapCallback {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20-L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24-L24)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

12:  interface ZetaTokenConsumerTridentErrors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20-L20)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

10:  interface ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

12:  interface ZetaTokenConsumerUniV3Errors {

20:  interface WETH9 {

```
*GitHub*: [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

16:  interface ConcentratedLiquidityPoolFactory {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16-L16)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

16:  interface IPoolRouter {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16-L16)

```solidity
File: contracts/zevm/Interfaces.sol

21:  interface IZRC20 {

49:  interface IZRC20Metadata is IZRC20 {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21-L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49-L49)

```solidity
File: contracts/zevm/ZRC20.sol

20   contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:      /// @notice Fungible address is always the same, maintained at the protocol level

```
*GitHub*: [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L21)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

4    interface ZetaInterfaces {
5        /**
6         * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
7:        */

49:  interface WZETA {

55   contract ZetaConnectorZEVM is ZetaInterfaces {
56:      /// @notice Contract custom errors.

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L7), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55-L56)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

4:   interface IUniswapV2Router01 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

6:   interface IUniswapV2Router02 is IUniswapV2Router01 {

```
*GitHub*: [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6-L6)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

4:   interface IWETH9 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

4:   interface IZRC20 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4-L4)

```solidity
File: contracts/zevm/interfaces/zContract.sol

10:  interface zContract {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10-L10)

</details>





### [N&#x2011;39] NatSpec: Error `@param` tag is missing


*There are 10 instances of this issue:*

```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

/// @audit Missing '@param caller'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    /**
5     * @dev Interface with connector custom errors
6     */
7    interface ConnectorErrors {
8        // @dev Thrown when caller is not the address defined as paused address
9:       error CallerIsNotPauser(address caller);

/// @audit Missing '@param caller'
2    pragma solidity 0.8.7;
3    
4    /**
5     * @dev Interface with connector custom errors
6     */
7    interface ConnectorErrors {
8        // @dev Thrown when caller is not the address defined as paused address
9        error CallerIsNotPauser(address caller);
10   
11       // @dev Thrown when caller is not the address defined as TSS address
12:      error CallerIsNotTss(address caller);

/// @audit Missing '@param caller'
5     * @dev Interface with connector custom errors
6     */
7    interface ConnectorErrors {
8        // @dev Thrown when caller is not the address defined as paused address
9        error CallerIsNotPauser(address caller);
10   
11       // @dev Thrown when caller is not the address defined as TSS address
12       error CallerIsNotTss(address caller);
13   
14       // @dev Thrown when caller is not the address defined as TSS Updater address
15:      error CallerIsNotTssUpdater(address caller);

/// @audit Missing '@param caller'
8        // @dev Thrown when caller is not the address defined as paused address
9        error CallerIsNotPauser(address caller);
10   
11       // @dev Thrown when caller is not the address defined as TSS address
12       error CallerIsNotTss(address caller);
13   
14       // @dev Thrown when caller is not the address defined as TSS Updater address
15       error CallerIsNotTssUpdater(address caller);
16   
17       // @dev Thrown when caller is not the address defined as TSS or TSS Updater address
18:      error CallerIsNotTssOrUpdater(address caller);

/// @audit Missing '@param maxSupply'
14       // @dev Thrown when caller is not the address defined as TSS Updater address
15       error CallerIsNotTssUpdater(address caller);
16   
17       // @dev Thrown when caller is not the address defined as TSS or TSS Updater address
18       error CallerIsNotTssOrUpdater(address caller);
19   
20       // @dev Thrown when Zeta can't be transferred for some reason
21       error ZetaTransferError();
22   
23       // @dev Thrown when maxSupply will be exceed if minting will proceed
24:      error ExceedsMaxSupply(uint256 maxSupply);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L1-L9), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L2-L12), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L5-L15), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L8-L18), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L14-L24)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

/// @audit Missing '@param caller'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    /**
5     * @dev Common custom errors
6     */
7    interface ZetaErrors {
8        // @dev Thrown when caller is not the address defined as TSS address
9:       error CallerIsNotTss(address caller);

/// @audit Missing '@param caller'
2    pragma solidity 0.8.7;
3    
4    /**
5     * @dev Common custom errors
6     */
7    interface ZetaErrors {
8        // @dev Thrown when caller is not the address defined as TSS address
9        error CallerIsNotTss(address caller);
10   
11       // @dev Thrown when caller is not the address defined as connector address
12:      error CallerIsNotConnector(address caller);

/// @audit Missing '@param caller'
5     * @dev Common custom errors
6     */
7    interface ZetaErrors {
8        // @dev Thrown when caller is not the address defined as TSS address
9        error CallerIsNotTss(address caller);
10   
11       // @dev Thrown when caller is not the address defined as connector address
12       error CallerIsNotConnector(address caller);
13   
14       // @dev Thrown when caller is not the address defined as TSS Updater address
15:      error CallerIsNotTssUpdater(address caller);

/// @audit Missing '@param caller'
8        // @dev Thrown when caller is not the address defined as TSS address
9        error CallerIsNotTss(address caller);
10   
11       // @dev Thrown when caller is not the address defined as connector address
12       error CallerIsNotConnector(address caller);
13   
14       // @dev Thrown when caller is not the address defined as TSS Updater address
15       error CallerIsNotTssUpdater(address caller);
16   
17       // @dev Thrown when caller is not the address defined as TSS or TSS Updater address
18:      error CallerIsNotTssOrUpdater(address caller);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L1-L9), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L2-L12), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L5-L15), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L8-L18)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

/// @audit Missing '@param caller'
2    pragma solidity 0.8.7;
3    
4    /**
5     * @dev Interface with Zeta Interactor errors
6     */
7    interface ZetaInteractorErrors {
8        // @dev Thrown when try to send a message or tokens to a non whitelisted chain
9        error InvalidDestinationChainId();
10   
11       // @dev Thrown when the caller is invalid. e.g.: if onZetaMessage or onZetaRevert are not called by Connector
12:      error InvalidCaller(address caller);

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L2-L12)



### [N&#x2011;40] NatSpec: Error declarations should have `@dev` tags
`@dev` is used to explain extra details to developers

*There are 52 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

14:      error NotWhitelisted();

15:      error NotPaused();

16:      error InvalidSender();

17:      error InvalidTSSUpdater();

18:      error ZeroAddress();

19:      error IsPaused();

20:      error ZetaMaxFeeExceeded();

21:      error ZeroFee();

```
*GitHub*: [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L15-L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L16-L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L17-L17), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L18-L18), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L19-L19), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L20-L20), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L21-L21)

```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

9:       error CallerIsNotPauser(address caller);

12:      error CallerIsNotTss(address caller);

15:      error CallerIsNotTssUpdater(address caller);

18:      error CallerIsNotTssOrUpdater(address caller);

21:      error ZetaTransferError();

24:      error ExceedsMaxSupply(uint256 maxSupply);

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L9-L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L12-L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L18-L18), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L24-L24)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

9:       error CallerIsNotTss(address caller);

12:      error CallerIsNotConnector(address caller);

15:      error CallerIsNotTssUpdater(address caller);

18:      error CallerIsNotTssOrUpdater(address caller);

21:      error InvalidAddress();

24:      error ZetaTransferError();

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L9-L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L12-L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L18-L18), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L24-L24)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

9:       error InvalidDestinationChainId();

12:      error InvalidCaller(address caller);

15:      error InvalidZetaMessageCall();

18:      error InvalidZetaRevertCall();

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L9-L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L12-L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L18-L18)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

109:     error InvalidAddress();

```
*GitHub*: [109](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L109-L109)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

11:      error InputCantBeZero();

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L11-L11)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L17-L17)

```solidity
File: contracts/zevm/SystemContract.sol

11:      error CallerIsNotFungibleModule();

12:      error InvalidTarget();

13:      error CantBeIdenticalAddresses();

14:      error CantBeZeroAddress();

15:      error ZeroAddress();

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L12-L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L15-L15)

```solidity
File: contracts/zevm/ZRC20.sol

10:      error CallerIsNotFungibleModule();

11:      error InvalidSender();

12:      error GasFeeTransferFailed();

13:      error ZeroGasCoin();

14:      error ZeroGasPrice();

15:      error LowAllowance();

16:      error LowBalance();

17:      error ZeroAddress();

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L10-L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L12-L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L15-L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L16-L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L17-L17)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

57:      error OnlyWZETA();

58:      error WZETATransferFailed();

59:      error OnlyFungibleModule();

60:      error FailedZetaSent();

```
*GitHub*: [57](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L57-L57), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L58-L58), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L59-L59), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L60-L60)

</details>





### [N&#x2011;41] NatSpec: Error declarations should have `@notice` tags
`@notice` is used to explain to end users what the error does, and the compiler interprets `///` or `/**` comments (but not `//` or `/*`) as this tag if one wasn't explicitly provided

*There are 51 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

14:      error NotWhitelisted();

15:      error NotPaused();

16:      error InvalidSender();

17:      error InvalidTSSUpdater();

18:      error ZeroAddress();

19:      error IsPaused();

20:      error ZetaMaxFeeExceeded();

21:      error ZeroFee();

```
*GitHub*: [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L15-L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L16-L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L17-L17), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L18-L18), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L19-L19), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L20-L20), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L21-L21)

```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

9:       error CallerIsNotPauser(address caller);

12:      error CallerIsNotTss(address caller);

15:      error CallerIsNotTssUpdater(address caller);

18:      error CallerIsNotTssOrUpdater(address caller);

21:      error ZetaTransferError();

24:      error ExceedsMaxSupply(uint256 maxSupply);

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L9-L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L12-L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L18-L18), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L24-L24)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

9:       error CallerIsNotTss(address caller);

12:      error CallerIsNotConnector(address caller);

15:      error CallerIsNotTssUpdater(address caller);

18:      error CallerIsNotTssOrUpdater(address caller);

21:      error InvalidAddress();

24:      error ZetaTransferError();

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L9-L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L12-L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L18-L18), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L24-L24)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

9:       error InvalidDestinationChainId();

12:      error InvalidCaller(address caller);

15:      error InvalidZetaMessageCall();

18:      error InvalidZetaRevertCall();

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L9-L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L12-L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L18-L18)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

109:     error InvalidAddress();

```
*GitHub*: [109](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L109-L109)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

11:      error InputCantBeZero();

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L11-L11)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L17-L17)

```solidity
File: contracts/zevm/SystemContract.sol

11:      error CallerIsNotFungibleModule();

12:      error InvalidTarget();

13:      error CantBeIdenticalAddresses();

14:      error CantBeZeroAddress();

15:      error ZeroAddress();

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L12-L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L15-L15)

```solidity
File: contracts/zevm/ZRC20.sol

10:      error CallerIsNotFungibleModule();

11:      error InvalidSender();

12:      error GasFeeTransferFailed();

13:      error ZeroGasCoin();

14:      error ZeroGasPrice();

15:      error LowAllowance();

16:      error LowBalance();

17:      error ZeroAddress();

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L10-L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L12-L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L15-L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L16-L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L17-L17)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

58:      error WZETATransferFailed();

59:      error OnlyFungibleModule();

60:      error FailedZetaSent();

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L58-L58), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L59-L59), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L60-L60)

</details>





### [N&#x2011;42] NatSpec: Error declarations should have descriptions


*There are 51 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

14:      error NotWhitelisted();

15:      error NotPaused();

16:      error InvalidSender();

17:      error InvalidTSSUpdater();

18:      error ZeroAddress();

19:      error IsPaused();

20:      error ZetaMaxFeeExceeded();

21:      error ZeroFee();

```
*GitHub*: [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L15-L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L16-L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L17-L17), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L18-L18), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L19-L19), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L20-L20), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L21-L21)

```solidity
File: contracts/evm/interfaces/ConnectorErrors.sol

9:       error CallerIsNotPauser(address caller);

12:      error CallerIsNotTss(address caller);

15:      error CallerIsNotTssUpdater(address caller);

18:      error CallerIsNotTssOrUpdater(address caller);

21:      error ZetaTransferError();

24:      error ExceedsMaxSupply(uint256 maxSupply);

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L9-L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L12-L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L18-L18), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L24-L24)

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

9:       error CallerIsNotTss(address caller);

12:      error CallerIsNotConnector(address caller);

15:      error CallerIsNotTssUpdater(address caller);

18:      error CallerIsNotTssOrUpdater(address caller);

21:      error InvalidAddress();

24:      error ZetaTransferError();

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L9-L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L12-L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L18-L18), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L24-L24)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

9:       error InvalidDestinationChainId();

12:      error InvalidCaller(address caller);

15:      error InvalidZetaMessageCall();

18:      error InvalidZetaRevertCall();

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L9-L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L12-L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L15-L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L18-L18)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

109:     error InvalidAddress();

```
*GitHub*: [109](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L109-L109)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L17-L17)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

11:      error InputCantBeZero();

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L11-L11)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

13:      error InputCantBeZero();

15:      error ErrorSendingETH();

17:      error ReentrancyError();

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L17-L17)

```solidity
File: contracts/zevm/SystemContract.sol

11:      error CallerIsNotFungibleModule();

12:      error InvalidTarget();

13:      error CantBeIdenticalAddresses();

14:      error CantBeZeroAddress();

15:      error ZeroAddress();

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L12-L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L15-L15)

```solidity
File: contracts/zevm/ZRC20.sol

10:      error CallerIsNotFungibleModule();

11:      error InvalidSender();

12:      error GasFeeTransferFailed();

13:      error ZeroGasCoin();

14:      error ZeroGasPrice();

15:      error LowAllowance();

16:      error LowBalance();

17:      error ZeroAddress();

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L10-L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L12-L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L13-L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L14-L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L15-L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L16-L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L17-L17)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

58:      error WZETATransferFailed();

59:      error OnlyFungibleModule();

60:      error FailedZetaSent();

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L58-L58), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L59-L59), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L60-L60)

</details>





### [N&#x2011;43] NatSpec: Event `@param` tag is missing


*There are 117 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

/// @audit Missing '@param sender'
28       address public TSSAddressUpdater;
29       /// @notice Current zeta fee for depositing funds into ZetaChain.
30       uint256 public zetaFee;
31       /// @notice Maximum zeta fee for transaction.
32       uint256 public immutable zetaMaxFee;
33       /// @notice Zeta ERC20 token .
34       IERC20 public immutable zeta;
35       /// @notice Mapping of whitelisted token => true/false.
36       mapping(IERC20 => bool) public whitelisted;
37   
38:      event Paused(address sender);

/// @audit Missing '@param sender'
29       /// @notice Current zeta fee for depositing funds into ZetaChain.
30       uint256 public zetaFee;
31       /// @notice Maximum zeta fee for transaction.
32       uint256 public immutable zetaMaxFee;
33       /// @notice Zeta ERC20 token .
34       IERC20 public immutable zeta;
35       /// @notice Mapping of whitelisted token => true/false.
36       mapping(IERC20 => bool) public whitelisted;
37   
38       event Paused(address sender);
39:      event Unpaused(address sender);

/// @audit Missing '@param asset'
30       uint256 public zetaFee;
31       /// @notice Maximum zeta fee for transaction.
32       uint256 public immutable zetaMaxFee;
33       /// @notice Zeta ERC20 token .
34       IERC20 public immutable zeta;
35       /// @notice Mapping of whitelisted token => true/false.
36       mapping(IERC20 => bool) public whitelisted;
37   
38       event Paused(address sender);
39       event Unpaused(address sender);
40:      event Whitelisted(IERC20 indexed asset);

/// @audit Missing '@param asset'
31       /// @notice Maximum zeta fee for transaction.
32       uint256 public immutable zetaMaxFee;
33       /// @notice Zeta ERC20 token .
34       IERC20 public immutable zeta;
35       /// @notice Mapping of whitelisted token => true/false.
36       mapping(IERC20 => bool) public whitelisted;
37   
38       event Paused(address sender);
39       event Unpaused(address sender);
40       event Whitelisted(IERC20 indexed asset);
41:      event Unwhitelisted(IERC20 indexed asset);

/// @audit Missing '@param recipient'
/// @audit Missing '@param asset'
/// @audit Missing '@param amount'
/// @audit Missing '@param message'
32       uint256 public immutable zetaMaxFee;
33       /// @notice Zeta ERC20 token .
34       IERC20 public immutable zeta;
35       /// @notice Mapping of whitelisted token => true/false.
36       mapping(IERC20 => bool) public whitelisted;
37   
38       event Paused(address sender);
39       event Unpaused(address sender);
40       event Whitelisted(IERC20 indexed asset);
41       event Unwhitelisted(IERC20 indexed asset);
42:      event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);

/// @audit Missing '@param recipient'
/// @audit Missing '@param asset'
/// @audit Missing '@param amount'
33       /// @notice Zeta ERC20 token .
34       IERC20 public immutable zeta;
35       /// @notice Mapping of whitelisted token => true/false.
36       mapping(IERC20 => bool) public whitelisted;
37   
38       event Paused(address sender);
39       event Unpaused(address sender);
40       event Whitelisted(IERC20 indexed asset);
41       event Unwhitelisted(IERC20 indexed asset);
42       event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);
43:      event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);

/// @audit Missing '@param TSSAddressUpdater_'
34       IERC20 public immutable zeta;
35       /// @notice Mapping of whitelisted token => true/false.
36       mapping(IERC20 => bool) public whitelisted;
37   
38       event Paused(address sender);
39       event Unpaused(address sender);
40       event Whitelisted(IERC20 indexed asset);
41       event Unwhitelisted(IERC20 indexed asset);
42       event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);
43       event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);
44:      event RenouncedTSSUpdater(address TSSAddressUpdater_);

/// @audit Missing '@param TSSAddress_'
35       /// @notice Mapping of whitelisted token => true/false.
36       mapping(IERC20 => bool) public whitelisted;
37   
38       event Paused(address sender);
39       event Unpaused(address sender);
40       event Whitelisted(IERC20 indexed asset);
41       event Unwhitelisted(IERC20 indexed asset);
42       event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);
43       event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);
44       event RenouncedTSSUpdater(address TSSAddressUpdater_);
45:      event UpdatedTSSAddress(address TSSAddress_);

/// @audit Missing '@param zetaFee_'
36       mapping(IERC20 => bool) public whitelisted;
37   
38       event Paused(address sender);
39       event Unpaused(address sender);
40       event Whitelisted(IERC20 indexed asset);
41       event Unwhitelisted(IERC20 indexed asset);
42       event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);
43       event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);
44       event RenouncedTSSUpdater(address TSSAddressUpdater_);
45       event UpdatedTSSAddress(address TSSAddress_);
46:      event UpdatedZetaFee(uint256 zetaFee_);

```
*GitHub*: [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L28-L38), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L29-L39), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L30-L40), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L31-L41), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L32-L42), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L32-L42), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L32-L42), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L32-L42), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L33-L43), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L33-L43), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L33-L43), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L34-L44), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L35-L45), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36-L46)

```solidity
File: contracts/evm/Zeta.non-eth.sol

/// @audit Missing '@param mintee'
/// @audit Missing '@param amount'
/// @audit Missing '@param internalSendHash'
13       /**
14        * @dev Collectively held by Zeta blockchain validators
15        */
16       address public tssAddress;
17   
18       /**
19        * @dev Initially a multi-sig, eventually held by Zeta blockchain validators (via renounceTssAddressUpdater)
20        */
21       address public tssAddressUpdater;
22   
23:      event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);

/// @audit Missing '@param burnee'
/// @audit Missing '@param amount'
15        */
16       address public tssAddress;
17   
18       /**
19        * @dev Initially a multi-sig, eventually held by Zeta blockchain validators (via renounceTssAddressUpdater)
20        */
21       address public tssAddressUpdater;
22   
23       event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);
24   
25:      event Burnt(address indexed burnee, uint256 amount);

/// @audit Missing '@param callerAddress'
/// @audit Missing '@param newTssAddress'
17   
18       /**
19        * @dev Initially a multi-sig, eventually held by Zeta blockchain validators (via renounceTssAddressUpdater)
20        */
21       address public tssAddressUpdater;
22   
23       event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);
24   
25       event Burnt(address indexed burnee, uint256 amount);
26   
27:      event TSSAddressUpdated(address callerAddress, address newTssAddress);

/// @audit Missing '@param callerAddress'
/// @audit Missing '@param newTssUpdaterAddress'
19        * @dev Initially a multi-sig, eventually held by Zeta blockchain validators (via renounceTssAddressUpdater)
20        */
21       address public tssAddressUpdater;
22   
23       event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);
24   
25       event Burnt(address indexed burnee, uint256 amount);
26   
27       event TSSAddressUpdated(address callerAddress, address newTssAddress);
28   
29:      event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

/// @audit Missing '@param callerAddress'
/// @audit Missing '@param newConnectorAddress'
21       address public tssAddressUpdater;
22   
23       event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);
24   
25       event Burnt(address indexed burnee, uint256 amount);
26   
27       event TSSAddressUpdated(address callerAddress, address newTssAddress);
28   
29       event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);
30   
31:      event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L13-L23), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L13-L23), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L13-L23), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L15-L25), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L15-L25), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L17-L27), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L17-L27), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L19-L29), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L19-L29), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L21-L31), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L21-L31)

```solidity
File: contracts/evm/ZetaConnector.base.sol

/// @audit Missing '@param sourceTxOriginAddress'
25        * @dev Collectively held by ZetaChain validators.
26        */
27       address public tssAddress;
28   
29       /**
30        * @dev This address will start pointing to a multisig contract, then it will become the TSS address itself.
31        */
32       address public tssAddressUpdater;
33   
34       event ZetaSent(
35:          address sourceTxOriginAddress,

/// @audit Missing '@param zetaTxSenderAddress'
26        */
27       address public tssAddress;
28   
29       /**
30        * @dev This address will start pointing to a multisig contract, then it will become the TSS address itself.
31        */
32       address public tssAddressUpdater;
33   
34       event ZetaSent(
35           address sourceTxOriginAddress,
36:          address indexed zetaTxSenderAddress,

/// @audit Missing '@param destinationChainId'
27       address public tssAddress;
28   
29       /**
30        * @dev This address will start pointing to a multisig contract, then it will become the TSS address itself.
31        */
32       address public tssAddressUpdater;
33   
34       event ZetaSent(
35           address sourceTxOriginAddress,
36           address indexed zetaTxSenderAddress,
37:          uint256 indexed destinationChainId,

/// @audit Missing '@param destinationAddress'
28   
29       /**
30        * @dev This address will start pointing to a multisig contract, then it will become the TSS address itself.
31        */
32       address public tssAddressUpdater;
33   
34       event ZetaSent(
35           address sourceTxOriginAddress,
36           address indexed zetaTxSenderAddress,
37           uint256 indexed destinationChainId,
38:          bytes destinationAddress,

/// @audit Missing '@param zetaValueAndGas'
29       /**
30        * @dev This address will start pointing to a multisig contract, then it will become the TSS address itself.
31        */
32       address public tssAddressUpdater;
33   
34       event ZetaSent(
35           address sourceTxOriginAddress,
36           address indexed zetaTxSenderAddress,
37           uint256 indexed destinationChainId,
38           bytes destinationAddress,
39:          uint256 zetaValueAndGas,

/// @audit Missing '@param destinationGasLimit'
30        * @dev This address will start pointing to a multisig contract, then it will become the TSS address itself.
31        */
32       address public tssAddressUpdater;
33   
34       event ZetaSent(
35           address sourceTxOriginAddress,
36           address indexed zetaTxSenderAddress,
37           uint256 indexed destinationChainId,
38           bytes destinationAddress,
39           uint256 zetaValueAndGas,
40:          uint256 destinationGasLimit,

/// @audit Missing '@param message'
31        */
32       address public tssAddressUpdater;
33   
34       event ZetaSent(
35           address sourceTxOriginAddress,
36           address indexed zetaTxSenderAddress,
37           uint256 indexed destinationChainId,
38           bytes destinationAddress,
39           uint256 zetaValueAndGas,
40           uint256 destinationGasLimit,
41:          bytes message,

/// @audit Missing '@param zetaParams'
32       address public tssAddressUpdater;
33   
34       event ZetaSent(
35           address sourceTxOriginAddress,
36           address indexed zetaTxSenderAddress,
37           uint256 indexed destinationChainId,
38           bytes destinationAddress,
39           uint256 zetaValueAndGas,
40           uint256 destinationGasLimit,
41           bytes message,
42:          bytes zetaParams

/// @audit Missing '@param zetaTxSenderAddress'
36           address indexed zetaTxSenderAddress,
37           uint256 indexed destinationChainId,
38           bytes destinationAddress,
39           uint256 zetaValueAndGas,
40           uint256 destinationGasLimit,
41           bytes message,
42           bytes zetaParams
43       );
44   
45       event ZetaReceived(
46:          bytes zetaTxSenderAddress,

/// @audit Missing '@param sourceChainId'
37           uint256 indexed destinationChainId,
38           bytes destinationAddress,
39           uint256 zetaValueAndGas,
40           uint256 destinationGasLimit,
41           bytes message,
42           bytes zetaParams
43       );
44   
45       event ZetaReceived(
46           bytes zetaTxSenderAddress,
47:          uint256 indexed sourceChainId,

/// @audit Missing '@param destinationAddress'
38           bytes destinationAddress,
39           uint256 zetaValueAndGas,
40           uint256 destinationGasLimit,
41           bytes message,
42           bytes zetaParams
43       );
44   
45       event ZetaReceived(
46           bytes zetaTxSenderAddress,
47           uint256 indexed sourceChainId,
48:          address indexed destinationAddress,

/// @audit Missing '@param zetaValue'
39           uint256 zetaValueAndGas,
40           uint256 destinationGasLimit,
41           bytes message,
42           bytes zetaParams
43       );
44   
45       event ZetaReceived(
46           bytes zetaTxSenderAddress,
47           uint256 indexed sourceChainId,
48           address indexed destinationAddress,
49:          uint256 zetaValue,

/// @audit Missing '@param message'
40           uint256 destinationGasLimit,
41           bytes message,
42           bytes zetaParams
43       );
44   
45       event ZetaReceived(
46           bytes zetaTxSenderAddress,
47           uint256 indexed sourceChainId,
48           address indexed destinationAddress,
49           uint256 zetaValue,
50:          bytes message,

/// @audit Missing '@param internalSendHash'
41           bytes message,
42           bytes zetaParams
43       );
44   
45       event ZetaReceived(
46           bytes zetaTxSenderAddress,
47           uint256 indexed sourceChainId,
48           address indexed destinationAddress,
49           uint256 zetaValue,
50           bytes message,
51:          bytes32 indexed internalSendHash

/// @audit Missing '@param zetaTxSenderAddress'
45       event ZetaReceived(
46           bytes zetaTxSenderAddress,
47           uint256 indexed sourceChainId,
48           address indexed destinationAddress,
49           uint256 zetaValue,
50           bytes message,
51           bytes32 indexed internalSendHash
52       );
53   
54       event ZetaReverted(
55:          address zetaTxSenderAddress,

/// @audit Missing '@param sourceChainId'
46           bytes zetaTxSenderAddress,
47           uint256 indexed sourceChainId,
48           address indexed destinationAddress,
49           uint256 zetaValue,
50           bytes message,
51           bytes32 indexed internalSendHash
52       );
53   
54       event ZetaReverted(
55           address zetaTxSenderAddress,
56:          uint256 sourceChainId,

/// @audit Missing '@param destinationChainId'
47           uint256 indexed sourceChainId,
48           address indexed destinationAddress,
49           uint256 zetaValue,
50           bytes message,
51           bytes32 indexed internalSendHash
52       );
53   
54       event ZetaReverted(
55           address zetaTxSenderAddress,
56           uint256 sourceChainId,
57:          uint256 indexed destinationChainId,

/// @audit Missing '@param destinationAddress'
48           address indexed destinationAddress,
49           uint256 zetaValue,
50           bytes message,
51           bytes32 indexed internalSendHash
52       );
53   
54       event ZetaReverted(
55           address zetaTxSenderAddress,
56           uint256 sourceChainId,
57           uint256 indexed destinationChainId,
58:          bytes destinationAddress,

/// @audit Missing '@param remainingZetaValue'
49           uint256 zetaValue,
50           bytes message,
51           bytes32 indexed internalSendHash
52       );
53   
54       event ZetaReverted(
55           address zetaTxSenderAddress,
56           uint256 sourceChainId,
57           uint256 indexed destinationChainId,
58           bytes destinationAddress,
59:          uint256 remainingZetaValue,

/// @audit Missing '@param message'
50           bytes message,
51           bytes32 indexed internalSendHash
52       );
53   
54       event ZetaReverted(
55           address zetaTxSenderAddress,
56           uint256 sourceChainId,
57           uint256 indexed destinationChainId,
58           bytes destinationAddress,
59           uint256 remainingZetaValue,
60:          bytes message,

/// @audit Missing '@param internalSendHash'
51           bytes32 indexed internalSendHash
52       );
53   
54       event ZetaReverted(
55           address zetaTxSenderAddress,
56           uint256 sourceChainId,
57           uint256 indexed destinationChainId,
58           bytes destinationAddress,
59           uint256 remainingZetaValue,
60           bytes message,
61:          bytes32 indexed internalSendHash

/// @audit Missing '@param callerAddress'
/// @audit Missing '@param newTssAddress'
54       event ZetaReverted(
55           address zetaTxSenderAddress,
56           uint256 sourceChainId,
57           uint256 indexed destinationChainId,
58           bytes destinationAddress,
59           uint256 remainingZetaValue,
60           bytes message,
61           bytes32 indexed internalSendHash
62       );
63   
64:      event TSSAddressUpdated(address callerAddress, address newTssAddress);

/// @audit Missing '@param callerAddress'
/// @audit Missing '@param newTssUpdaterAddress'
56           uint256 sourceChainId,
57           uint256 indexed destinationChainId,
58           bytes destinationAddress,
59           uint256 remainingZetaValue,
60           bytes message,
61           bytes32 indexed internalSendHash
62       );
63   
64       event TSSAddressUpdated(address callerAddress, address newTssAddress);
65   
66:      event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

/// @audit Missing '@param callerAddress'
/// @audit Missing '@param newTssAddress'
58           bytes destinationAddress,
59           uint256 remainingZetaValue,
60           bytes message,
61           bytes32 indexed internalSendHash
62       );
63   
64       event TSSAddressUpdated(address callerAddress, address newTssAddress);
65   
66       event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);
67   
68:      event PauserAddressUpdated(address callerAddress, address newTssAddress);

```
*GitHub*: [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L25-L35), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L26-L36), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L27-L37), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L28-L38), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L29-L39), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L30-L40), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L31-L41), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L32-L42), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L36-L46), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L37-L47), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L38-L48), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L39-L49), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L40-L50), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L41-L51), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L45-L55), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L46-L56), [47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L47-L57), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L48-L58), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L49-L59), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L50-L60), [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L51-L61), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L64), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L64), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L56-L66), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L56-L66), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L58-L68), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L58-L68)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

/// @audit Missing '@param callerAddress'
/// @audit Missing '@param newMaxSupply'
8    import "./interfaces/ZetaNonEthInterface.sol";
9    
10   /**
11    * @dev Non ETH implementation of ZetaConnector.
12    * This contract manages interactions between TSS and different chains.
13    * This version is for every chain but Etherum network because in the other chains we mint and burn and in Etherum we lock and unlock
14    */
15   contract ZetaConnectorNonEth is ZetaConnectorBase {
16       uint256 public maxSupply = 2 ** 256 - 1;
17   
18:      event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L8-L18), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L8-L18)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

/// @audit Missing '@param amountIn'
/// @audit Missing '@param amountOut'
68   
69   /**
70    * @dev ZetaTokenConsumer makes it easier to handle the following situations:
71    *   - Getting Zeta using native coin (to pay for destination gas while using `connector.send`)
72    *   - Getting Zeta using a token (to pay for destination gas while using `connector.send`)
73    *   - Getting native coin using Zeta (to return unused destination gas when `onZetaRevert` is executed)
74    *   - Getting a token using Zeta (to return unused destination gas when `onZetaRevert` is executed)
75    * @dev The interface can be implemented using different strategies, like UniswapV2, UniswapV3, etc
76    */
77   interface ZetaTokenConsumer {
78:      event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);

/// @audit Missing '@param token'
/// @audit Missing '@param amountIn'
/// @audit Missing '@param amountOut'
69   /**
70    * @dev ZetaTokenConsumer makes it easier to handle the following situations:
71    *   - Getting Zeta using native coin (to pay for destination gas while using `connector.send`)
72    *   - Getting Zeta using a token (to pay for destination gas while using `connector.send`)
73    *   - Getting native coin using Zeta (to return unused destination gas when `onZetaRevert` is executed)
74    *   - Getting a token using Zeta (to return unused destination gas when `onZetaRevert` is executed)
75    * @dev The interface can be implemented using different strategies, like UniswapV2, UniswapV3, etc
76    */
77   interface ZetaTokenConsumer {
78       event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
79:      event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

/// @audit Missing '@param amountIn'
/// @audit Missing '@param amountOut'
70    * @dev ZetaTokenConsumer makes it easier to handle the following situations:
71    *   - Getting Zeta using native coin (to pay for destination gas while using `connector.send`)
72    *   - Getting Zeta using a token (to pay for destination gas while using `connector.send`)
73    *   - Getting native coin using Zeta (to return unused destination gas when `onZetaRevert` is executed)
74    *   - Getting a token using Zeta (to return unused destination gas when `onZetaRevert` is executed)
75    * @dev The interface can be implemented using different strategies, like UniswapV2, UniswapV3, etc
76    */
77   interface ZetaTokenConsumer {
78       event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
79       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
80:      event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);

/// @audit Missing '@param token'
/// @audit Missing '@param amountIn'
/// @audit Missing '@param amountOut'
71    *   - Getting Zeta using native coin (to pay for destination gas while using `connector.send`)
72    *   - Getting Zeta using a token (to pay for destination gas while using `connector.send`)
73    *   - Getting native coin using Zeta (to return unused destination gas when `onZetaRevert` is executed)
74    *   - Getting a token using Zeta (to return unused destination gas when `onZetaRevert` is executed)
75    * @dev The interface can be implemented using different strategies, like UniswapV2, UniswapV3, etc
76    */
77   interface ZetaTokenConsumer {
78       event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
79       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
80       event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
81:      event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);

```
*GitHub*: [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L68-L78), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L68-L78), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L69-L79), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L69-L79), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L69-L79), [70](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L70-L80), [70](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L70-L80), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L71-L81), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L71-L81), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L71-L81)

```solidity
File: contracts/zevm/Interfaces.sol

/// @audit Missing '@param from'
/// @audit Missing '@param to'
/// @audit Missing '@param value'
30       function approve(address spender, uint256 amount) external returns (bool);
31   
32       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
33   
34       function deposit(address to, uint256 amount) external returns (bool);
35   
36       function withdraw(bytes memory to, uint256 amount) external returns (bool);
37   
38       function withdrawGasFee() external view returns (address, uint256);
39   
40:      event Transfer(address indexed from, address indexed to, uint256 value);

/// @audit Missing '@param owner'
/// @audit Missing '@param spender'
/// @audit Missing '@param value'
31   
32       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
33   
34       function deposit(address to, uint256 amount) external returns (bool);
35   
36       function withdraw(bytes memory to, uint256 amount) external returns (bool);
37   
38       function withdrawGasFee() external view returns (address, uint256);
39   
40       event Transfer(address indexed from, address indexed to, uint256 value);
41:      event Approval(address indexed owner, address indexed spender, uint256 value);

/// @audit Missing '@param from'
/// @audit Missing '@param to'
/// @audit Missing '@param value'
32       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
33   
34       function deposit(address to, uint256 amount) external returns (bool);
35   
36       function withdraw(bytes memory to, uint256 amount) external returns (bool);
37   
38       function withdrawGasFee() external view returns (address, uint256);
39   
40       event Transfer(address indexed from, address indexed to, uint256 value);
41       event Approval(address indexed owner, address indexed spender, uint256 value);
42:      event Deposit(bytes from, address indexed to, uint256 value);

/// @audit Missing '@param from'
/// @audit Missing '@param to'
/// @audit Missing '@param value'
/// @audit Missing '@param gasfee'
/// @audit Missing '@param protocolFlatFee'
33   
34       function deposit(address to, uint256 amount) external returns (bool);
35   
36       function withdraw(bytes memory to, uint256 amount) external returns (bool);
37   
38       function withdrawGasFee() external view returns (address, uint256);
39   
40       event Transfer(address indexed from, address indexed to, uint256 value);
41       event Approval(address indexed owner, address indexed spender, uint256 value);
42       event Deposit(bytes from, address indexed to, uint256 value);
43:      event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);

/// @audit Missing '@param systemContract'
34       function deposit(address to, uint256 amount) external returns (bool);
35   
36       function withdraw(bytes memory to, uint256 amount) external returns (bool);
37   
38       function withdrawGasFee() external view returns (address, uint256);
39   
40       event Transfer(address indexed from, address indexed to, uint256 value);
41       event Approval(address indexed owner, address indexed spender, uint256 value);
42       event Deposit(bytes from, address indexed to, uint256 value);
43       event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);
44:      event UpdatedSystemContract(address systemContract);

/// @audit Missing '@param gasLimit'
35   
36       function withdraw(bytes memory to, uint256 amount) external returns (bool);
37   
38       function withdrawGasFee() external view returns (address, uint256);
39   
40       event Transfer(address indexed from, address indexed to, uint256 value);
41       event Approval(address indexed owner, address indexed spender, uint256 value);
42       event Deposit(bytes from, address indexed to, uint256 value);
43       event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);
44       event UpdatedSystemContract(address systemContract);
45:      event UpdatedGasLimit(uint256 gasLimit);

/// @audit Missing '@param protocolFlatFee'
36       function withdraw(bytes memory to, uint256 amount) external returns (bool);
37   
38       function withdrawGasFee() external view returns (address, uint256);
39   
40       event Transfer(address indexed from, address indexed to, uint256 value);
41       event Approval(address indexed owner, address indexed spender, uint256 value);
42       event Deposit(bytes from, address indexed to, uint256 value);
43       event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);
44       event UpdatedSystemContract(address systemContract);
45       event UpdatedGasLimit(uint256 gasLimit);
46:      event UpdatedProtocolFlatFee(uint256 protocolFlatFee);

```
*GitHub*: [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30-L40), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30-L40), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30-L40), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L31-L41), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L31-L41), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L31-L41), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32-L42), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32-L42), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32-L42), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L33-L43), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L33-L43), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L33-L43), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L33-L43), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L33-L43), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34-L44), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L35-L45), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36-L46)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

/// @audit Missing '@param sourceTxOriginAddress'
58       error WZETATransferFailed();
59       error OnlyFungibleModule();
60       error FailedZetaSent();
61   
62       /// @notice Fungible module address.
63       address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
64       /// @notice WZETA token address.
65       address public wzeta;
66   
67       event ZetaSent(
68:          address sourceTxOriginAddress,

/// @audit Missing '@param zetaTxSenderAddress'
59       error OnlyFungibleModule();
60       error FailedZetaSent();
61   
62       /// @notice Fungible module address.
63       address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
64       /// @notice WZETA token address.
65       address public wzeta;
66   
67       event ZetaSent(
68           address sourceTxOriginAddress,
69:          address indexed zetaTxSenderAddress,

/// @audit Missing '@param destinationChainId'
60       error FailedZetaSent();
61   
62       /// @notice Fungible module address.
63       address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
64       /// @notice WZETA token address.
65       address public wzeta;
66   
67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70:          uint256 indexed destinationChainId,

/// @audit Missing '@param destinationAddress'
61   
62       /// @notice Fungible module address.
63       address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
64       /// @notice WZETA token address.
65       address public wzeta;
66   
67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71:          bytes destinationAddress,

/// @audit Missing '@param zetaValueAndGas'
62       /// @notice Fungible module address.
63       address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
64       /// @notice WZETA token address.
65       address public wzeta;
66   
67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71           bytes destinationAddress,
72:          uint256 zetaValueAndGas,

/// @audit Missing '@param destinationGasLimit'
63       address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
64       /// @notice WZETA token address.
65       address public wzeta;
66   
67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71           bytes destinationAddress,
72           uint256 zetaValueAndGas,
73:          uint256 destinationGasLimit,

/// @audit Missing '@param message'
64       /// @notice WZETA token address.
65       address public wzeta;
66   
67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71           bytes destinationAddress,
72           uint256 zetaValueAndGas,
73           uint256 destinationGasLimit,
74:          bytes message,

/// @audit Missing '@param zetaParams'
65       address public wzeta;
66   
67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71           bytes destinationAddress,
72           uint256 zetaValueAndGas,
73           uint256 destinationGasLimit,
74           bytes message,
75:          bytes zetaParams

/// @audit Missing '@param wzeta_'
67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71           bytes destinationAddress,
72           uint256 zetaValueAndGas,
73           uint256 destinationGasLimit,
74           bytes message,
75           bytes zetaParams
76       );
77:      event SetWZETA(address wzeta_);

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L58-L68), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L59-L69), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L60-L70), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L61-L71), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L62-L72), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63-L73), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L64-L74), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L65-L75), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L77)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

/// @audit Missing '@param owner'
/// @audit Missing '@param spender'
/// @audit Missing '@param value'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IWETH9 {
5:       event Approval(address indexed owner, address indexed spender, uint value);

/// @audit Missing '@param from'
/// @audit Missing '@param to'
/// @audit Missing '@param value'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IWETH9 {
5        event Approval(address indexed owner, address indexed spender, uint value);
6:       event Transfer(address indexed from, address indexed to, uint value);

/// @audit Missing '@param dst'
/// @audit Missing '@param wad'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IWETH9 {
5        event Approval(address indexed owner, address indexed spender, uint value);
6        event Transfer(address indexed from, address indexed to, uint value);
7:       event Deposit(address indexed dst, uint wad);

/// @audit Missing '@param src'
/// @audit Missing '@param wad'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IWETH9 {
5        event Approval(address indexed owner, address indexed spender, uint value);
6        event Transfer(address indexed from, address indexed to, uint value);
7        event Deposit(address indexed dst, uint wad);
8:       event Withdrawal(address indexed src, uint wad);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L5), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L5), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L5), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L6), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L6), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L6), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L7), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L7), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L8), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L8)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

/// @audit Missing '@param from'
/// @audit Missing '@param to'
/// @audit Missing '@param value'
21       function deposit(address to, uint256 amount) external returns (bool);
22   
23       function burn(address account, uint256 amount) external returns (bool);
24   
25       function withdraw(bytes memory to, uint256 amount) external returns (bool);
26   
27       function withdrawGasFee() external view returns (address, uint256);
28   
29       function PROTOCOL_FEE() external view returns (uint256);
30   
31:      event Transfer(address indexed from, address indexed to, uint256 value);

/// @audit Missing '@param owner'
/// @audit Missing '@param spender'
/// @audit Missing '@param value'
22   
23       function burn(address account, uint256 amount) external returns (bool);
24   
25       function withdraw(bytes memory to, uint256 amount) external returns (bool);
26   
27       function withdrawGasFee() external view returns (address, uint256);
28   
29       function PROTOCOL_FEE() external view returns (uint256);
30   
31       event Transfer(address indexed from, address indexed to, uint256 value);
32:      event Approval(address indexed owner, address indexed spender, uint256 value);

/// @audit Missing '@param from'
/// @audit Missing '@param to'
/// @audit Missing '@param value'
23       function burn(address account, uint256 amount) external returns (bool);
24   
25       function withdraw(bytes memory to, uint256 amount) external returns (bool);
26   
27       function withdrawGasFee() external view returns (address, uint256);
28   
29       function PROTOCOL_FEE() external view returns (uint256);
30   
31       event Transfer(address indexed from, address indexed to, uint256 value);
32       event Approval(address indexed owner, address indexed spender, uint256 value);
33:      event Deposit(bytes from, address indexed to, uint256 value);

/// @audit Missing '@param from'
/// @audit Missing '@param to'
/// @audit Missing '@param value'
/// @audit Missing '@param gasFee'
/// @audit Missing '@param protocolFlatFee'
24   
25       function withdraw(bytes memory to, uint256 amount) external returns (bool);
26   
27       function withdrawGasFee() external view returns (address, uint256);
28   
29       function PROTOCOL_FEE() external view returns (uint256);
30   
31       event Transfer(address indexed from, address indexed to, uint256 value);
32       event Approval(address indexed owner, address indexed spender, uint256 value);
33       event Deposit(bytes from, address indexed to, uint256 value);
34:      event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

/// @audit Missing '@param systemContract'
25       function withdraw(bytes memory to, uint256 amount) external returns (bool);
26   
27       function withdrawGasFee() external view returns (address, uint256);
28   
29       function PROTOCOL_FEE() external view returns (uint256);
30   
31       event Transfer(address indexed from, address indexed to, uint256 value);
32       event Approval(address indexed owner, address indexed spender, uint256 value);
33       event Deposit(bytes from, address indexed to, uint256 value);
34       event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);
35:      event UpdatedSystemContract(address systemContract);

/// @audit Missing '@param gasLimit'
26   
27       function withdrawGasFee() external view returns (address, uint256);
28   
29       function PROTOCOL_FEE() external view returns (uint256);
30   
31       event Transfer(address indexed from, address indexed to, uint256 value);
32       event Approval(address indexed owner, address indexed spender, uint256 value);
33       event Deposit(bytes from, address indexed to, uint256 value);
34       event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);
35       event UpdatedSystemContract(address systemContract);
36:      event UpdatedGasLimit(uint256 gasLimit);

/// @audit Missing '@param protocolFlatFee'
27       function withdrawGasFee() external view returns (address, uint256);
28   
29       function PROTOCOL_FEE() external view returns (uint256);
30   
31       event Transfer(address indexed from, address indexed to, uint256 value);
32       event Approval(address indexed owner, address indexed spender, uint256 value);
33       event Deposit(bytes from, address indexed to, uint256 value);
34       event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);
35       event UpdatedSystemContract(address systemContract);
36       event UpdatedGasLimit(uint256 gasLimit);
37:      event UpdatedProtocolFlatFee(uint256 protocolFlatFee);

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21-L31), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21-L31), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21-L31), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L22-L32), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L22-L32), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L22-L32), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23-L33), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23-L33), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23-L33), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L24-L34), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L24-L34), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L24-L34), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L24-L34), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L24-L34), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25-L35), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L26-L36), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27-L37)

</details>





### [N&#x2011;44] NatSpec: Event declarations should have `@dev` tags
`@dev` is used to explain extra details to developers

*There are 51 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

38:      event Paused(address sender);

39:      event Unpaused(address sender);

40:      event Whitelisted(IERC20 indexed asset);

41:      event Unwhitelisted(IERC20 indexed asset);

42:      event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);

43:      event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);

44:      event RenouncedTSSUpdater(address TSSAddressUpdater_);

45:      event UpdatedTSSAddress(address TSSAddress_);

46:      event UpdatedZetaFee(uint256 zetaFee_);

```
*GitHub*: [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38-L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39-L39), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46-L46)

```solidity
File: contracts/evm/Zeta.non-eth.sol

23:      event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);

25:      event Burnt(address indexed burnee, uint256 amount);

27:      event TSSAddressUpdated(address callerAddress, address newTssAddress);

29:      event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

31:      event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);

```
*GitHub*: [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29-L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31-L31)

```solidity
File: contracts/evm/ZetaConnector.base.sol

34       event ZetaSent(
35           address sourceTxOriginAddress,
36           address indexed zetaTxSenderAddress,
37           uint256 indexed destinationChainId,
38           bytes destinationAddress,
39           uint256 zetaValueAndGas,
40           uint256 destinationGasLimit,
41           bytes message,
42           bytes zetaParams
43:      );

45       event ZetaReceived(
46           bytes zetaTxSenderAddress,
47           uint256 indexed sourceChainId,
48           address indexed destinationAddress,
49           uint256 zetaValue,
50           bytes message,
51           bytes32 indexed internalSendHash
52:      );

54       event ZetaReverted(
55           address zetaTxSenderAddress,
56           uint256 sourceChainId,
57           uint256 indexed destinationChainId,
58           bytes destinationAddress,
59           uint256 remainingZetaValue,
60           bytes message,
61           bytes32 indexed internalSendHash
62:      );

64:      event TSSAddressUpdated(address callerAddress, address newTssAddress);

66:      event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

68:      event PauserAddressUpdated(address callerAddress, address newTssAddress);

```
*GitHub*: [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34-L43), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L45-L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L62), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64-L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66-L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68-L68)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

18:      event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);

```
*GitHub*: [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18-L18)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

78:      event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);

79:      event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

80:      event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);

81:      event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);

```
*GitHub*: [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78-L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79-L79), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L80-L80), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81-L81)

```solidity
File: contracts/zevm/Interfaces.sol

40:      event Transfer(address indexed from, address indexed to, uint256 value);

41:      event Approval(address indexed owner, address indexed spender, uint256 value);

42:      event Deposit(bytes from, address indexed to, uint256 value);

43:      event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);

44:      event UpdatedSystemContract(address systemContract);

45:      event UpdatedGasLimit(uint256 gasLimit);

46:      event UpdatedProtocolFlatFee(uint256 protocolFlatFee);

```
*GitHub*: [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L46-L46)

```solidity
File: contracts/zevm/SystemContract.sol

41:      event SystemContractDeployed();

42:      event SetGasPrice(uint256, uint256);

43:      event SetGasCoin(uint256, address);

44:      event SetGasZetaPool(uint256, address);

45:      event SetWZeta(address);

46:      event SetConnectorZEVM(address);

```
*GitHub*: [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46-L46)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71           bytes destinationAddress,
72           uint256 zetaValueAndGas,
73           uint256 destinationGasLimit,
74           bytes message,
75           bytes zetaParams
76:      );

77:      event SetWZETA(address wzeta_);

```
*GitHub*: [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77-L77)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

5:       event Approval(address indexed owner, address indexed spender, uint value);

6:       event Transfer(address indexed from, address indexed to, uint value);

7:       event Deposit(address indexed dst, uint wad);

8:       event Withdrawal(address indexed src, uint wad);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8-L8)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

31:      event Transfer(address indexed from, address indexed to, uint256 value);

32:      event Approval(address indexed owner, address indexed spender, uint256 value);

33:      event Deposit(bytes from, address indexed to, uint256 value);

34:      event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

35:      event UpdatedSystemContract(address systemContract);

36:      event UpdatedGasLimit(uint256 gasLimit);

37:      event UpdatedProtocolFlatFee(uint256 protocolFlatFee);

```
*GitHub*: [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31-L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32-L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33-L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34-L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35-L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36-L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37-L37)

</details>





### [N&#x2011;45] NatSpec: Event declarations should have `@notice` tags
`@notice` is used to explain to end users what the event does, and the compiler interprets `///` or `/**` comments (but not `//` or `/*`) as this tag if one wasn't explicitly provided

*There are 50 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

38:      event Paused(address sender);

39:      event Unpaused(address sender);

40:      event Whitelisted(IERC20 indexed asset);

41:      event Unwhitelisted(IERC20 indexed asset);

42:      event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);

43:      event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);

44:      event RenouncedTSSUpdater(address TSSAddressUpdater_);

45:      event UpdatedTSSAddress(address TSSAddress_);

46:      event UpdatedZetaFee(uint256 zetaFee_);

```
*GitHub*: [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38-L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39-L39), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46-L46)

```solidity
File: contracts/evm/Zeta.non-eth.sol

23:      event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);

25:      event Burnt(address indexed burnee, uint256 amount);

27:      event TSSAddressUpdated(address callerAddress, address newTssAddress);

29:      event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

31:      event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);

```
*GitHub*: [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29-L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31-L31)

```solidity
File: contracts/evm/ZetaConnector.base.sol

34       event ZetaSent(
35           address sourceTxOriginAddress,
36           address indexed zetaTxSenderAddress,
37           uint256 indexed destinationChainId,
38           bytes destinationAddress,
39           uint256 zetaValueAndGas,
40           uint256 destinationGasLimit,
41           bytes message,
42           bytes zetaParams
43:      );

45       event ZetaReceived(
46           bytes zetaTxSenderAddress,
47           uint256 indexed sourceChainId,
48           address indexed destinationAddress,
49           uint256 zetaValue,
50           bytes message,
51           bytes32 indexed internalSendHash
52:      );

54       event ZetaReverted(
55           address zetaTxSenderAddress,
56           uint256 sourceChainId,
57           uint256 indexed destinationChainId,
58           bytes destinationAddress,
59           uint256 remainingZetaValue,
60           bytes message,
61           bytes32 indexed internalSendHash
62:      );

64:      event TSSAddressUpdated(address callerAddress, address newTssAddress);

66:      event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

68:      event PauserAddressUpdated(address callerAddress, address newTssAddress);

```
*GitHub*: [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34-L43), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L45-L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L62), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64-L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66-L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68-L68)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

18:      event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);

```
*GitHub*: [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18-L18)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

78:      event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);

79:      event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

80:      event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);

81:      event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);

```
*GitHub*: [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78-L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79-L79), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L80-L80), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81-L81)

```solidity
File: contracts/zevm/Interfaces.sol

40:      event Transfer(address indexed from, address indexed to, uint256 value);

41:      event Approval(address indexed owner, address indexed spender, uint256 value);

42:      event Deposit(bytes from, address indexed to, uint256 value);

43:      event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);

44:      event UpdatedSystemContract(address systemContract);

45:      event UpdatedGasLimit(uint256 gasLimit);

46:      event UpdatedProtocolFlatFee(uint256 protocolFlatFee);

```
*GitHub*: [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L46-L46)

```solidity
File: contracts/zevm/SystemContract.sol

42:      event SetGasPrice(uint256, uint256);

43:      event SetGasCoin(uint256, address);

44:      event SetGasZetaPool(uint256, address);

45:      event SetWZeta(address);

46:      event SetConnectorZEVM(address);

```
*GitHub*: [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46-L46)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71           bytes destinationAddress,
72           uint256 zetaValueAndGas,
73           uint256 destinationGasLimit,
74           bytes message,
75           bytes zetaParams
76:      );

77:      event SetWZETA(address wzeta_);

```
*GitHub*: [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77-L77)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

5:       event Approval(address indexed owner, address indexed spender, uint value);

6:       event Transfer(address indexed from, address indexed to, uint value);

7:       event Deposit(address indexed dst, uint wad);

8:       event Withdrawal(address indexed src, uint wad);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8-L8)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

31:      event Transfer(address indexed from, address indexed to, uint256 value);

32:      event Approval(address indexed owner, address indexed spender, uint256 value);

33:      event Deposit(bytes from, address indexed to, uint256 value);

34:      event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

35:      event UpdatedSystemContract(address systemContract);

36:      event UpdatedGasLimit(uint256 gasLimit);

37:      event UpdatedProtocolFlatFee(uint256 protocolFlatFee);

```
*GitHub*: [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31-L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32-L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33-L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34-L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35-L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36-L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37-L37)

</details>





### [N&#x2011;46] NatSpec: Event declarations should have descriptions


*There are 50 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

38:      event Paused(address sender);

39:      event Unpaused(address sender);

40:      event Whitelisted(IERC20 indexed asset);

41:      event Unwhitelisted(IERC20 indexed asset);

42:      event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);

43:      event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);

44:      event RenouncedTSSUpdater(address TSSAddressUpdater_);

45:      event UpdatedTSSAddress(address TSSAddress_);

46:      event UpdatedZetaFee(uint256 zetaFee_);

```
*GitHub*: [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38-L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39-L39), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46-L46)

```solidity
File: contracts/evm/Zeta.non-eth.sol

23:      event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);

25:      event Burnt(address indexed burnee, uint256 amount);

27:      event TSSAddressUpdated(address callerAddress, address newTssAddress);

29:      event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

31:      event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);

```
*GitHub*: [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29-L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31-L31)

```solidity
File: contracts/evm/ZetaConnector.base.sol

34       event ZetaSent(
35           address sourceTxOriginAddress,
36           address indexed zetaTxSenderAddress,
37           uint256 indexed destinationChainId,
38           bytes destinationAddress,
39           uint256 zetaValueAndGas,
40           uint256 destinationGasLimit,
41           bytes message,
42           bytes zetaParams
43:      );

45       event ZetaReceived(
46           bytes zetaTxSenderAddress,
47           uint256 indexed sourceChainId,
48           address indexed destinationAddress,
49           uint256 zetaValue,
50           bytes message,
51           bytes32 indexed internalSendHash
52:      );

54       event ZetaReverted(
55           address zetaTxSenderAddress,
56           uint256 sourceChainId,
57           uint256 indexed destinationChainId,
58           bytes destinationAddress,
59           uint256 remainingZetaValue,
60           bytes message,
61           bytes32 indexed internalSendHash
62:      );

64:      event TSSAddressUpdated(address callerAddress, address newTssAddress);

66:      event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

68:      event PauserAddressUpdated(address callerAddress, address newTssAddress);

```
*GitHub*: [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34-L43), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L45-L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L62), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64-L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66-L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68-L68)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

18:      event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);

```
*GitHub*: [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18-L18)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

78:      event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);

79:      event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

80:      event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);

81:      event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);

```
*GitHub*: [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78-L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79-L79), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L80-L80), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81-L81)

```solidity
File: contracts/zevm/Interfaces.sol

40:      event Transfer(address indexed from, address indexed to, uint256 value);

41:      event Approval(address indexed owner, address indexed spender, uint256 value);

42:      event Deposit(bytes from, address indexed to, uint256 value);

43:      event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);

44:      event UpdatedSystemContract(address systemContract);

45:      event UpdatedGasLimit(uint256 gasLimit);

46:      event UpdatedProtocolFlatFee(uint256 protocolFlatFee);

```
*GitHub*: [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L46-L46)

```solidity
File: contracts/zevm/SystemContract.sol

42:      event SetGasPrice(uint256, uint256);

43:      event SetGasCoin(uint256, address);

44:      event SetGasZetaPool(uint256, address);

45:      event SetWZeta(address);

46:      event SetConnectorZEVM(address);

```
*GitHub*: [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46-L46)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

67       event ZetaSent(
68           address sourceTxOriginAddress,
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71           bytes destinationAddress,
72           uint256 zetaValueAndGas,
73           uint256 destinationGasLimit,
74           bytes message,
75           bytes zetaParams
76:      );

77:      event SetWZETA(address wzeta_);

```
*GitHub*: [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77-L77)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

5:       event Approval(address indexed owner, address indexed spender, uint value);

6:       event Transfer(address indexed from, address indexed to, uint value);

7:       event Deposit(address indexed dst, uint wad);

8:       event Withdrawal(address indexed src, uint wad);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8-L8)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

31:      event Transfer(address indexed from, address indexed to, uint256 value);

32:      event Approval(address indexed owner, address indexed spender, uint256 value);

33:      event Deposit(bytes from, address indexed to, uint256 value);

34:      event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

35:      event UpdatedSystemContract(address systemContract);

36:      event UpdatedGasLimit(uint256 gasLimit);

37:      event UpdatedProtocolFlatFee(uint256 protocolFlatFee);

```
*GitHub*: [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31-L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32-L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33-L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34-L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35-L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36-L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37-L37)

</details>





### [N&#x2011;47] NatSpec: File is missing NatSpec


*There are 6 instances of this issue:*

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol


```
*GitHub*: [various](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol


```
*GitHub*: [various](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol


```
*GitHub*: [various](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol


```
*GitHub*: [various](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol


```
*GitHub*: [various](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol)

```solidity
File: contracts/zevm/interfaces/zContract.sol


```
*GitHub*: [various](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol)



### [N&#x2011;48] NatSpec: Function `@param` tag is missing


*There are 381 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

/// @audit Missing '@param TSSAddress_'
/// @audit Missing '@param TSSAddressUpdater_'
/// @audit Missing '@param zetaFee_'
/// @audit Missing '@param zetaMaxFee_'
/// @audit Missing '@param zeta_'
58       /**
59        * @dev Only TSS address updater allowed modifier.
60        */
61       modifier onlyTSSUpdater() {
62           if (msg.sender != TSSAddressUpdater) {
63               revert InvalidTSSUpdater();
64           }
65           _;
66       }
67   
68:      constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L58-L68), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L58-L68), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L58-L68), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L58-L68), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L58-L68)

```solidity
File: contracts/evm/Zeta.eth.sol

/// @audit Missing '@param creator'
/// @audit Missing '@param initialSupply'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
5    
6    /**
7     * @dev ZetaEth is an implementation of OpenZeppelin's ERC20
8     */
9    contract ZetaEth is ERC20("Zeta", "ZETA") {
10:      constructor(address creator, uint256 initialSupply) {

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L1-L10), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L1-L10)

```solidity
File: contracts/evm/Zeta.non-eth.sol

/// @audit Missing '@param tssAddress_'
/// @audit Missing '@param tssAddressUpdater_'
23       event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);
24   
25       event Burnt(address indexed burnee, uint256 amount);
26   
27       event TSSAddressUpdated(address callerAddress, address newTssAddress);
28   
29       event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);
30   
31       event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);
32   
33:      constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

/// @audit Missing '@param tssAddress_'
/// @audit Missing '@param connectorAddress_'
30   
31       event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);
32   
33       constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {
34           if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();
35   
36           tssAddress = tssAddress_;
37           tssAddressUpdater = tssAddressUpdater_;
38       }
39   
40:      function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

/// @audit Missing '@param mintee'
/// @audit Missing '@param value'
/// @audit Missing '@param internalSendHash'
52        * @dev Sets tssAddressUpdater to be tssAddress
53        */
54       function renounceTssAddressUpdater() external {
55           if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);
56           if (tssAddress == address(0)) revert InvalidAddress();
57   
58           tssAddressUpdater = tssAddress;
59           emit TSSAddressUpdaterUpdated(msg.sender, tssAddress);
60       }
61   
62:      function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

/// @audit Missing '@param account'
/// @audit Missing '@param amount'
63           /**
64            * @dev Only Connector can mint. Minting requires burning the equivalent amount on another chain
65            */
66           if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
67   
68           _mint(mintee, value);
69   
70           emit Minted(mintee, value, internalSendHash);
71       }
72   
73:      function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {

```
*GitHub*: [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23-L33), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23-L33), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L30-L40), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L30-L40), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L52-L62), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L52-L62), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L52-L62), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L63-L73), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L63-L73)

```solidity
File: contracts/evm/ZetaConnector.base.sol

/// @audit Missing '@param zetaToken_'
/// @audit Missing '@param tssAddress_'
/// @audit Missing '@param tssAddressUpdater_'
/// @audit Missing '@param pauserAddress_'
64       event TSSAddressUpdated(address callerAddress, address newTssAddress);
65   
66       event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);
67   
68       event PauserAddressUpdated(address callerAddress, address newTssAddress);
69   
70       /**
71        * @dev Constructor requires initial addresses.
72        * zetaToken address is the only immutable one, while others can be updated.
73        */
74:      constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {

/// @audit Missing '@param pauserAddress_'
107       * @dev Modifier to restrict actions to TSS updater address.
108       */
109      modifier onlyTssUpdater() {
110          if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);
111          _;
112      }
113  
114      /**
115       * @dev Update the pauser address. The only address allowed to do that is the current pauser.
116       */
117:     function updatePauserAddress(address pauserAddress_) external onlyPauser {

/// @audit Missing '@param tssAddress_'
118          if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
119  
120          pauserAddress = pauserAddress_;
121  
122          emit PauserAddressUpdated(msg.sender, pauserAddress_);
123      }
124  
125      /**
126       * @dev Update the TSS address. The address can be updated by the TSS updater or the TSS address itself.
127       */
128:     function updateTssAddress(address tssAddress_) external {

/// @audit Missing '@param input'
156       * @dev Unpause the contract to allow transactions again.
157       */
158  
159      function unpause() external onlyPauser {
160          _unpause();
161      }
162  
163      /**
164       * @dev Entrypoint to send data and value through ZetaChain.
165       */
166:     function send(ZetaInterfaces.SendInput calldata input) external virtual {}

/// @audit Missing '@param zetaTxSenderAddress'
163      /**
164       * @dev Entrypoint to send data and value through ZetaChain.
165       */
166      function send(ZetaInterfaces.SendInput calldata input) external virtual {}
167  
168      /**
169       * @dev Handler to receive data from other chain.
170       * This method can be called only by TSS. Access validation is in implementation.
171       */
172      function onReceive(
173:         bytes calldata zetaTxSenderAddress,

/// @audit Missing '@param sourceChainId'
164       * @dev Entrypoint to send data and value through ZetaChain.
165       */
166      function send(ZetaInterfaces.SendInput calldata input) external virtual {}
167  
168      /**
169       * @dev Handler to receive data from other chain.
170       * This method can be called only by TSS. Access validation is in implementation.
171       */
172      function onReceive(
173          bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,

/// @audit Missing '@param destinationAddress'
165       */
166      function send(ZetaInterfaces.SendInput calldata input) external virtual {}
167  
168      /**
169       * @dev Handler to receive data from other chain.
170       * This method can be called only by TSS. Access validation is in implementation.
171       */
172      function onReceive(
173          bytes calldata zetaTxSenderAddress,
174          uint256 sourceChainId,
175:         address destinationAddress,

/// @audit Missing '@param zetaValue'
166      function send(ZetaInterfaces.SendInput calldata input) external virtual {}
167  
168      /**
169       * @dev Handler to receive data from other chain.
170       * This method can be called only by TSS. Access validation is in implementation.
171       */
172      function onReceive(
173          bytes calldata zetaTxSenderAddress,
174          uint256 sourceChainId,
175          address destinationAddress,
176:         uint256 zetaValue,

/// @audit Missing '@param message'
167  
168      /**
169       * @dev Handler to receive data from other chain.
170       * This method can be called only by TSS. Access validation is in implementation.
171       */
172      function onReceive(
173          bytes calldata zetaTxSenderAddress,
174          uint256 sourceChainId,
175          address destinationAddress,
176          uint256 zetaValue,
177:         bytes calldata message,

/// @audit Missing '@param internalSendHash'
168      /**
169       * @dev Handler to receive data from other chain.
170       * This method can be called only by TSS. Access validation is in implementation.
171       */
172      function onReceive(
173          bytes calldata zetaTxSenderAddress,
174          uint256 sourceChainId,
175          address destinationAddress,
176          uint256 zetaValue,
177          bytes calldata message,
178:         bytes32 internalSendHash

/// @audit Missing '@param zetaTxSenderAddress'
176          uint256 zetaValue,
177          bytes calldata message,
178          bytes32 internalSendHash
179      ) external virtual {}
180  
181      /**
182       * @dev Handler to receive errors from other chain.
183       * This method can be called only by TSS. Access validation is in implementation.
184       */
185      function onRevert(
186:         address zetaTxSenderAddress,

/// @audit Missing '@param sourceChainId'
177          bytes calldata message,
178          bytes32 internalSendHash
179      ) external virtual {}
180  
181      /**
182       * @dev Handler to receive errors from other chain.
183       * This method can be called only by TSS. Access validation is in implementation.
184       */
185      function onRevert(
186          address zetaTxSenderAddress,
187:         uint256 sourceChainId,

/// @audit Missing '@param destinationAddress'
178          bytes32 internalSendHash
179      ) external virtual {}
180  
181      /**
182       * @dev Handler to receive errors from other chain.
183       * This method can be called only by TSS. Access validation is in implementation.
184       */
185      function onRevert(
186          address zetaTxSenderAddress,
187          uint256 sourceChainId,
188:         bytes calldata destinationAddress,

/// @audit Missing '@param destinationChainId'
179      ) external virtual {}
180  
181      /**
182       * @dev Handler to receive errors from other chain.
183       * This method can be called only by TSS. Access validation is in implementation.
184       */
185      function onRevert(
186          address zetaTxSenderAddress,
187          uint256 sourceChainId,
188          bytes calldata destinationAddress,
189:         uint256 destinationChainId,

/// @audit Missing '@param remainingZetaValue'
180  
181      /**
182       * @dev Handler to receive errors from other chain.
183       * This method can be called only by TSS. Access validation is in implementation.
184       */
185      function onRevert(
186          address zetaTxSenderAddress,
187          uint256 sourceChainId,
188          bytes calldata destinationAddress,
189          uint256 destinationChainId,
190:         uint256 remainingZetaValue,

/// @audit Missing '@param message'
181      /**
182       * @dev Handler to receive errors from other chain.
183       * This method can be called only by TSS. Access validation is in implementation.
184       */
185      function onRevert(
186          address zetaTxSenderAddress,
187          uint256 sourceChainId,
188          bytes calldata destinationAddress,
189          uint256 destinationChainId,
190          uint256 remainingZetaValue,
191:         bytes calldata message,

/// @audit Missing '@param internalSendHash'
182       * @dev Handler to receive errors from other chain.
183       * This method can be called only by TSS. Access validation is in implementation.
184       */
185      function onRevert(
186          address zetaTxSenderAddress,
187          uint256 sourceChainId,
188          bytes calldata destinationAddress,
189          uint256 destinationChainId,
190          uint256 remainingZetaValue,
191          bytes calldata message,
192:         bytes32 internalSendHash

```
*GitHub*: [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64-L74), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64-L74), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64-L74), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64-L74), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L107-L117), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L118-L128), [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L156-L166), [163](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L163-L173), [164](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L164-L174), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L165-L175), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166-L176), [167](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L167-L177), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L168-L178), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L176-L186), [177](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L177-L187), [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L178-L188), [179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L179-L189), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L180-L190), [181](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L181-L191), [182](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L182-L192)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

/// @audit Missing '@param zetaToken_'
7    import "./ZetaConnector.base.sol";
8    import "./interfaces/ZetaInterfaces.sol";
9    
10   /**
11    * @dev ETH implementation of ZetaConnector.
12    * This contract manages interactions between TSS and different chains.
13    * This version is only for Ethereum network because in the other chains we mint and burn and in this one we lock and unlock.
14    */
15   contract ZetaConnectorEth is ZetaConnectorBase {
16       constructor(
17:          address zetaToken_,

/// @audit Missing '@param tssAddress_'
8    import "./interfaces/ZetaInterfaces.sol";
9    
10   /**
11    * @dev ETH implementation of ZetaConnector.
12    * This contract manages interactions between TSS and different chains.
13    * This version is only for Ethereum network because in the other chains we mint and burn and in this one we lock and unlock.
14    */
15   contract ZetaConnectorEth is ZetaConnectorBase {
16       constructor(
17           address zetaToken_,
18:          address tssAddress_,

/// @audit Missing '@param tssAddressUpdater_'
9    
10   /**
11    * @dev ETH implementation of ZetaConnector.
12    * This contract manages interactions between TSS and different chains.
13    * This version is only for Ethereum network because in the other chains we mint and burn and in this one we lock and unlock.
14    */
15   contract ZetaConnectorEth is ZetaConnectorBase {
16       constructor(
17           address zetaToken_,
18           address tssAddress_,
19:          address tssAddressUpdater_,

/// @audit Missing '@param pauserAddress_'
10   /**
11    * @dev ETH implementation of ZetaConnector.
12    * This contract manages interactions between TSS and different chains.
13    * This version is only for Ethereum network because in the other chains we mint and burn and in this one we lock and unlock.
14    */
15   contract ZetaConnectorEth is ZetaConnectorBase {
16       constructor(
17           address zetaToken_,
18           address tssAddress_,
19           address tssAddressUpdater_,
20:          address pauserAddress_

/// @audit Missing '@param input'
21       ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
22   
23       function getLockedAmount() external view returns (uint256) {
24           return IERC20(zetaToken).balanceOf(address(this));
25       }
26   
27       /**
28        * @dev Entrypoint to send data through ZetaChain
29        * This call locks the token on the contract and emits an event with all the data needed by the protocol.
30        */
31:      function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

/// @audit Missing '@param zetaTxSenderAddress'
43               input.zetaParams
44           );
45       }
46   
47       /**
48        * @dev Handler to receive data from other chain.
49        * This method can be called only by TSS.
50        * Transfers the Zeta tokens to destination and calls onZetaMessage if it's needed.
51        */
52       function onReceive(
53:          bytes calldata zetaTxSenderAddress,

/// @audit Missing '@param sourceChainId'
44           );
45       }
46   
47       /**
48        * @dev Handler to receive data from other chain.
49        * This method can be called only by TSS.
50        * Transfers the Zeta tokens to destination and calls onZetaMessage if it's needed.
51        */
52       function onReceive(
53           bytes calldata zetaTxSenderAddress,
54:          uint256 sourceChainId,

/// @audit Missing '@param destinationAddress'
45       }
46   
47       /**
48        * @dev Handler to receive data from other chain.
49        * This method can be called only by TSS.
50        * Transfers the Zeta tokens to destination and calls onZetaMessage if it's needed.
51        */
52       function onReceive(
53           bytes calldata zetaTxSenderAddress,
54           uint256 sourceChainId,
55:          address destinationAddress,

/// @audit Missing '@param zetaValue'
46   
47       /**
48        * @dev Handler to receive data from other chain.
49        * This method can be called only by TSS.
50        * Transfers the Zeta tokens to destination and calls onZetaMessage if it's needed.
51        */
52       function onReceive(
53           bytes calldata zetaTxSenderAddress,
54           uint256 sourceChainId,
55           address destinationAddress,
56:          uint256 zetaValue,

/// @audit Missing '@param message'
47       /**
48        * @dev Handler to receive data from other chain.
49        * This method can be called only by TSS.
50        * Transfers the Zeta tokens to destination and calls onZetaMessage if it's needed.
51        */
52       function onReceive(
53           bytes calldata zetaTxSenderAddress,
54           uint256 sourceChainId,
55           address destinationAddress,
56           uint256 zetaValue,
57:          bytes calldata message,

/// @audit Missing '@param internalSendHash'
48        * @dev Handler to receive data from other chain.
49        * This method can be called only by TSS.
50        * Transfers the Zeta tokens to destination and calls onZetaMessage if it's needed.
51        */
52       function onReceive(
53           bytes calldata zetaTxSenderAddress,
54           uint256 sourceChainId,
55           address destinationAddress,
56           uint256 zetaValue,
57           bytes calldata message,
58:          bytes32 internalSendHash

/// @audit Missing '@param zetaTxSenderAddress'
68   
69           emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70       }
71   
72       /**
73        * @dev Handler to receive errors from other chain.
74        * This method can be called only by TSS.
75        * Transfers the Zeta tokens to destination and calls onZetaRevert if it's needed.
76        */
77       function onRevert(
78:          address zetaTxSenderAddress,

/// @audit Missing '@param sourceChainId'
69           emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70       }
71   
72       /**
73        * @dev Handler to receive errors from other chain.
74        * This method can be called only by TSS.
75        * Transfers the Zeta tokens to destination and calls onZetaRevert if it's needed.
76        */
77       function onRevert(
78           address zetaTxSenderAddress,
79:          uint256 sourceChainId,

/// @audit Missing '@param destinationAddress'
70       }
71   
72       /**
73        * @dev Handler to receive errors from other chain.
74        * This method can be called only by TSS.
75        * Transfers the Zeta tokens to destination and calls onZetaRevert if it's needed.
76        */
77       function onRevert(
78           address zetaTxSenderAddress,
79           uint256 sourceChainId,
80:          bytes calldata destinationAddress,

/// @audit Missing '@param destinationChainId'
71   
72       /**
73        * @dev Handler to receive errors from other chain.
74        * This method can be called only by TSS.
75        * Transfers the Zeta tokens to destination and calls onZetaRevert if it's needed.
76        */
77       function onRevert(
78           address zetaTxSenderAddress,
79           uint256 sourceChainId,
80           bytes calldata destinationAddress,
81:          uint256 destinationChainId,

/// @audit Missing '@param remainingZetaValue'
72       /**
73        * @dev Handler to receive errors from other chain.
74        * This method can be called only by TSS.
75        * Transfers the Zeta tokens to destination and calls onZetaRevert if it's needed.
76        */
77       function onRevert(
78           address zetaTxSenderAddress,
79           uint256 sourceChainId,
80           bytes calldata destinationAddress,
81           uint256 destinationChainId,
82:          uint256 remainingZetaValue,

/// @audit Missing '@param message'
73        * @dev Handler to receive errors from other chain.
74        * This method can be called only by TSS.
75        * Transfers the Zeta tokens to destination and calls onZetaRevert if it's needed.
76        */
77       function onRevert(
78           address zetaTxSenderAddress,
79           uint256 sourceChainId,
80           bytes calldata destinationAddress,
81           uint256 destinationChainId,
82           uint256 remainingZetaValue,
83:          bytes calldata message,

/// @audit Missing '@param internalSendHash'
74        * This method can be called only by TSS.
75        * Transfers the Zeta tokens to destination and calls onZetaRevert if it's needed.
76        */
77       function onRevert(
78           address zetaTxSenderAddress,
79           uint256 sourceChainId,
80           bytes calldata destinationAddress,
81           uint256 destinationChainId,
82           uint256 remainingZetaValue,
83           bytes calldata message,
84:          bytes32 internalSendHash

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L7-L17), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L8-L18), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L9-L19), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L10-L20), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L21-L31), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L43-L53), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L44-L54), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L45-L55), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L46-L56), [47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L47-L57), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L48-L58), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L68-L78), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L69-L79), [70](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L70-L80), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L71-L81), [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L72-L82), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L73-L83), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L74-L84)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

/// @audit Missing '@param zetaTokenAddress_'
11    * @dev Non ETH implementation of ZetaConnector.
12    * This contract manages interactions between TSS and different chains.
13    * This version is for every chain but Etherum network because in the other chains we mint and burn and in Etherum we lock and unlock
14    */
15   contract ZetaConnectorNonEth is ZetaConnectorBase {
16       uint256 public maxSupply = 2 ** 256 - 1;
17   
18       event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
19   
20       constructor(
21:          address zetaTokenAddress_,

/// @audit Missing '@param tssAddress_'
12    * This contract manages interactions between TSS and different chains.
13    * This version is for every chain but Etherum network because in the other chains we mint and burn and in Etherum we lock and unlock
14    */
15   contract ZetaConnectorNonEth is ZetaConnectorBase {
16       uint256 public maxSupply = 2 ** 256 - 1;
17   
18       event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
19   
20       constructor(
21           address zetaTokenAddress_,
22:          address tssAddress_,

/// @audit Missing '@param tssAddressUpdater_'
13    * This version is for every chain but Etherum network because in the other chains we mint and burn and in Etherum we lock and unlock
14    */
15   contract ZetaConnectorNonEth is ZetaConnectorBase {
16       uint256 public maxSupply = 2 ** 256 - 1;
17   
18       event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
19   
20       constructor(
21           address zetaTokenAddress_,
22           address tssAddress_,
23:          address tssAddressUpdater_,

/// @audit Missing '@param pauserAddress_'
14    */
15   contract ZetaConnectorNonEth is ZetaConnectorBase {
16       uint256 public maxSupply = 2 ** 256 - 1;
17   
18       event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
19   
20       constructor(
21           address zetaTokenAddress_,
22           address tssAddress_,
23           address tssAddressUpdater_,
24:          address pauserAddress_

/// @audit Missing '@param maxSupply_'
21           address zetaTokenAddress_,
22           address tssAddress_,
23           address tssAddressUpdater_,
24           address pauserAddress_
25       ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
26   
27       function getLockedAmount() external view returns (uint256) {
28           return ZetaNonEthInterface(zetaToken).balanceOf(address(this));
29       }
30   
31:      function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {

/// @audit Missing '@param input'
30   
31       function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
32           maxSupply = maxSupply_;
33           emit MaxSupplyUpdated(msg.sender, maxSupply_);
34       }
35   
36       /**
37        * @dev Entry point to send data to protocol
38        * This call burn the token and emit an event with all the data needed by the protocol
39        */
40:      function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

/// @audit Missing '@param zetaTxSenderAddress'
52           );
53       }
54   
55       /**
56        * @dev Handler to receive data from other chain.
57        * This method can be called only by TSS.
58        * Transfer the Zeta tokens to destination and calls onZetaMessage if it's needed.
59        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
60        */
61       function onReceive(
62:          bytes calldata zetaTxSenderAddress,

/// @audit Missing '@param sourceChainId'
53       }
54   
55       /**
56        * @dev Handler to receive data from other chain.
57        * This method can be called only by TSS.
58        * Transfer the Zeta tokens to destination and calls onZetaMessage if it's needed.
59        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
60        */
61       function onReceive(
62           bytes calldata zetaTxSenderAddress,
63:          uint256 sourceChainId,

/// @audit Missing '@param destinationAddress'
54   
55       /**
56        * @dev Handler to receive data from other chain.
57        * This method can be called only by TSS.
58        * Transfer the Zeta tokens to destination and calls onZetaMessage if it's needed.
59        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
60        */
61       function onReceive(
62           bytes calldata zetaTxSenderAddress,
63           uint256 sourceChainId,
64:          address destinationAddress,

/// @audit Missing '@param zetaValue'
55       /**
56        * @dev Handler to receive data from other chain.
57        * This method can be called only by TSS.
58        * Transfer the Zeta tokens to destination and calls onZetaMessage if it's needed.
59        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
60        */
61       function onReceive(
62           bytes calldata zetaTxSenderAddress,
63           uint256 sourceChainId,
64           address destinationAddress,
65:          uint256 zetaValue,

/// @audit Missing '@param message'
56        * @dev Handler to receive data from other chain.
57        * This method can be called only by TSS.
58        * Transfer the Zeta tokens to destination and calls onZetaMessage if it's needed.
59        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
60        */
61       function onReceive(
62           bytes calldata zetaTxSenderAddress,
63           uint256 sourceChainId,
64           address destinationAddress,
65           uint256 zetaValue,
66:          bytes calldata message,

/// @audit Missing '@param internalSendHash'
57        * This method can be called only by TSS.
58        * Transfer the Zeta tokens to destination and calls onZetaMessage if it's needed.
59        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
60        */
61       function onReceive(
62           bytes calldata zetaTxSenderAddress,
63           uint256 sourceChainId,
64           address destinationAddress,
65           uint256 zetaValue,
66           bytes calldata message,
67:          bytes32 internalSendHash

/// @audit Missing '@param zetaTxSenderAddress'
78           emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79       }
80   
81       /**
82        * @dev Handler to receive errors from other chain.
83        * This method can be called only by TSS.
84        * Transfer the Zeta tokens to destination and calls onZetaRevert if it's needed.
85        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
86        */
87       function onRevert(
88:          address zetaTxSenderAddress,

/// @audit Missing '@param sourceChainId'
79       }
80   
81       /**
82        * @dev Handler to receive errors from other chain.
83        * This method can be called only by TSS.
84        * Transfer the Zeta tokens to destination and calls onZetaRevert if it's needed.
85        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
86        */
87       function onRevert(
88           address zetaTxSenderAddress,
89:          uint256 sourceChainId,

/// @audit Missing '@param destinationAddress'
80   
81       /**
82        * @dev Handler to receive errors from other chain.
83        * This method can be called only by TSS.
84        * Transfer the Zeta tokens to destination and calls onZetaRevert if it's needed.
85        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
86        */
87       function onRevert(
88           address zetaTxSenderAddress,
89           uint256 sourceChainId,
90:          bytes calldata destinationAddress,

/// @audit Missing '@param destinationChainId'
81       /**
82        * @dev Handler to receive errors from other chain.
83        * This method can be called only by TSS.
84        * Transfer the Zeta tokens to destination and calls onZetaRevert if it's needed.
85        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
86        */
87       function onRevert(
88           address zetaTxSenderAddress,
89           uint256 sourceChainId,
90           bytes calldata destinationAddress,
91:          uint256 destinationChainId,

/// @audit Missing '@param remainingZetaValue'
82        * @dev Handler to receive errors from other chain.
83        * This method can be called only by TSS.
84        * Transfer the Zeta tokens to destination and calls onZetaRevert if it's needed.
85        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
86        */
87       function onRevert(
88           address zetaTxSenderAddress,
89           uint256 sourceChainId,
90           bytes calldata destinationAddress,
91           uint256 destinationChainId,
92:          uint256 remainingZetaValue,

/// @audit Missing '@param message'
83        * This method can be called only by TSS.
84        * Transfer the Zeta tokens to destination and calls onZetaRevert if it's needed.
85        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
86        */
87       function onRevert(
88           address zetaTxSenderAddress,
89           uint256 sourceChainId,
90           bytes calldata destinationAddress,
91           uint256 destinationChainId,
92           uint256 remainingZetaValue,
93:          bytes calldata message,

/// @audit Missing '@param internalSendHash'
84        * Transfer the Zeta tokens to destination and calls onZetaRevert if it's needed.
85        * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
86        */
87       function onRevert(
88           address zetaTxSenderAddress,
89           uint256 sourceChainId,
90           bytes calldata destinationAddress,
91           uint256 destinationChainId,
92           uint256 remainingZetaValue,
93           bytes calldata message,
94:          bytes32 internalSendHash

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L11-L21), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L12-L22), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L13-L23), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L14-L24), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L21-L31), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L30-L40), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L52-L62), [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L53-L63), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L54-L64), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L55-L65), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L56-L66), [57](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L57-L67), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L78-L88), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L79-L89), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L80-L90), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L81-L91), [82](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L82-L92), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L83-L93), [84](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L84-L94)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

/// @audit Missing '@param input'
43           /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
44           uint256 remainingZetaValue;
45           bytes message;
46       }
47   }
48   
49   interface ZetaConnector {
50       /**
51        * @dev Sending value and data cross-chain is as easy as calling connector.send(SendInput)
52        */
53:      function send(ZetaInterfaces.SendInput calldata input) external;

/// @audit Missing '@param zetaMessage'
50       /**
51        * @dev Sending value and data cross-chain is as easy as calling connector.send(SendInput)
52        */
53       function send(ZetaInterfaces.SendInput calldata input) external;
54   }
55   
56   interface ZetaReceiver {
57       /**
58        * @dev onZetaMessage is called when a cross-chain message reaches a contract
59        */
60:      function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external;

/// @audit Missing '@param zetaRevert'
56   interface ZetaReceiver {
57       /**
58        * @dev onZetaMessage is called when a cross-chain message reaches a contract
59        */
60       function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external;
61   
62       /**
63        * @dev onZetaRevert is called when a cross-chain message reverts.
64        * It's useful to rollback to the original state
65        */
66:      function onZetaRevert(ZetaInterfaces.ZetaRevert calldata zetaRevert) external;

/// @audit Missing '@param destinationAddress'
/// @audit Missing '@param minAmountOut'
73    *   - Getting native coin using Zeta (to return unused destination gas when `onZetaRevert` is executed)
74    *   - Getting a token using Zeta (to return unused destination gas when `onZetaRevert` is executed)
75    * @dev The interface can be implemented using different strategies, like UniswapV2, UniswapV3, etc
76    */
77   interface ZetaTokenConsumer {
78       event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
79       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
80       event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
81       event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
82   
83:      function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

/// @audit Missing '@param destinationAddress'
76    */
77   interface ZetaTokenConsumer {
78       event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
79       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
80       event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
81       event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
82   
83       function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);
84   
85       function getZetaFromToken(
86:          address destinationAddress,

/// @audit Missing '@param minAmountOut'
77   interface ZetaTokenConsumer {
78       event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
79       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
80       event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
81       event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
82   
83       function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);
84   
85       function getZetaFromToken(
86           address destinationAddress,
87:          uint256 minAmountOut,

/// @audit Missing '@param inputToken'
78       event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
79       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
80       event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
81       event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
82   
83       function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);
84   
85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88:          address inputToken,

/// @audit Missing '@param inputTokenAmount'
79       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
80       event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
81       event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
82   
83       function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);
84   
85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89:          uint256 inputTokenAmount

/// @audit Missing '@param destinationAddress'
83       function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);
84   
85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89           uint256 inputTokenAmount
90       ) external returns (uint256);
91   
92       function getEthFromZeta(
93:          address destinationAddress,

/// @audit Missing '@param minAmountOut'
84   
85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89           uint256 inputTokenAmount
90       ) external returns (uint256);
91   
92       function getEthFromZeta(
93           address destinationAddress,
94:          uint256 minAmountOut,

/// @audit Missing '@param zetaTokenAmount'
85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89           uint256 inputTokenAmount
90       ) external returns (uint256);
91   
92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95:          uint256 zetaTokenAmount

/// @audit Missing '@param destinationAddress'
89           uint256 inputTokenAmount
90       ) external returns (uint256);
91   
92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96       ) external returns (uint256);
97   
98       function getTokenFromZeta(
99:          address destinationAddress,

/// @audit Missing '@param minAmountOut'
90       ) external returns (uint256);
91   
92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96       ) external returns (uint256);
97   
98       function getTokenFromZeta(
99           address destinationAddress,
100:         uint256 minAmountOut,

/// @audit Missing '@param outputToken'
91   
92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96       ) external returns (uint256);
97   
98       function getTokenFromZeta(
99           address destinationAddress,
100          uint256 minAmountOut,
101:         address outputToken,

/// @audit Missing '@param zetaTokenAmount'
92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96       ) external returns (uint256);
97   
98       function getTokenFromZeta(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address outputToken,
102:         uint256 zetaTokenAmount

```
*GitHub*: [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L43-L53), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L50-L60), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L66), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L73-L83), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L73-L83), [76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L76-L86), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77-L87), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78-L88), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79-L89), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83-L93), [84](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L84-L94), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85-L95), [89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L89-L99), [90](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L90-L100), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L91-L101), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92-L102)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

/// @audit Missing '@param account'
/// @audit Missing '@param amount'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
5    
6    /**
7     * @dev ZetaNonEthInterface is a mintable / burnable version of IERC20
8     */
9    interface ZetaNonEthInterface is IERC20 {
10:      function burnFrom(address account, uint256 amount) external;

/// @audit Missing '@param mintee'
/// @audit Missing '@param value'
/// @audit Missing '@param internalSendHash'
2    pragma solidity 0.8.7;
3    
4    import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
5    
6    /**
7     * @dev ZetaNonEthInterface is a mintable / burnable version of IERC20
8     */
9    interface ZetaNonEthInterface is IERC20 {
10       function burnFrom(address account, uint256 amount) external;
11   
12:      function mint(address mintee, uint256 value, bytes32 internalSendHash) external;

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L1-L10), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L1-L10), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2-L12), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2-L12), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2-L12)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

/// @audit Missing '@param zetaConnectorAddress'
27           _;
28       }
29   
30       modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
31           _isValidCaller();
32           if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
33           if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();
34           _;
35       }
36   
37:      constructor(address zetaConnectorAddress) {

/// @audit Missing '@param chainId'
40           connector = ZetaConnector(zetaConnectorAddress);
41       }
42   
43       function _isValidCaller() private view {
44           if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
45       }
46   
47       /**
48        * @dev Useful for contracts that inherit from this one
49        */
50:      function _isValidChainId(uint256 chainId) internal view returns (bool) {

/// @audit Missing '@param destinationChainId'
/// @audit Missing '@param contractAddress'
44           if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
45       }
46   
47       /**
48        * @dev Useful for contracts that inherit from this one
49        */
50       function _isValidChainId(uint256 chainId) internal view returns (bool) {
51           return (keccak256(interactorsByChainId[chainId]) != ZERO_BYTES);
52       }
53   
54:      function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {

```
*GitHub*: [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L27-L37), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L40-L50), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L44-L54), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L44-L54)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

/// @audit Missing '@param wad'
11   
12   interface ZetaTokenConsumerUniV3Errors {
13       error InputCantBeZero();
14   
15       error ErrorSendingETH();
16   
17       error ReentrancyError();
18   }
19   
20   interface WETH9 {
21:      function withdraw(uint256 wad) external;

/// @audit Missing '@param zetaToken_'
62   
63       address public immutable WETH9Address;
64       address public immutable zetaToken;
65   
66       ISwapRouterPancake public immutable pancakeV3Router;
67       IUniswapV3Factory public immutable uniswapV3Factory;
68   
69       bool internal _locked;
70   
71       constructor(
72:          address zetaToken_,

/// @audit Missing '@param pancakeV3Router_'
63       address public immutable WETH9Address;
64       address public immutable zetaToken;
65   
66       ISwapRouterPancake public immutable pancakeV3Router;
67       IUniswapV3Factory public immutable uniswapV3Factory;
68   
69       bool internal _locked;
70   
71       constructor(
72           address zetaToken_,
73:          address pancakeV3Router_,

/// @audit Missing '@param uniswapV3Factory_'
64       address public immutable zetaToken;
65   
66       ISwapRouterPancake public immutable pancakeV3Router;
67       IUniswapV3Factory public immutable uniswapV3Factory;
68   
69       bool internal _locked;
70   
71       constructor(
72           address zetaToken_,
73           address pancakeV3Router_,
74:          address uniswapV3Factory_,

/// @audit Missing '@param WETH9Address_'
65   
66       ISwapRouterPancake public immutable pancakeV3Router;
67       IUniswapV3Factory public immutable uniswapV3Factory;
68   
69       bool internal _locked;
70   
71       constructor(
72           address zetaToken_,
73           address pancakeV3Router_,
74           address uniswapV3Factory_,
75:          address WETH9Address_,

/// @audit Missing '@param zetaPoolFee_'
66       ISwapRouterPancake public immutable pancakeV3Router;
67       IUniswapV3Factory public immutable uniswapV3Factory;
68   
69       bool internal _locked;
70   
71       constructor(
72           address zetaToken_,
73           address pancakeV3Router_,
74           address uniswapV3Factory_,
75           address WETH9Address_,
76:          uint24 zetaPoolFee_,

/// @audit Missing '@param tokenPoolFee_'
67       IUniswapV3Factory public immutable uniswapV3Factory;
68   
69       bool internal _locked;
70   
71       constructor(
72           address zetaToken_,
73           address pancakeV3Router_,
74           address uniswapV3Factory_,
75           address WETH9Address_,
76           uint24 zetaPoolFee_,
77:          uint24 tokenPoolFee_

/// @audit Missing '@param destinationAddress'
94       modifier nonReentrant() {
95           if (_locked) revert ReentrancyError();
96           _locked = true;
97           _;
98           _locked = false;
99       }
100  
101      receive() external payable {}
102  
103      function getZetaFromEth(
104:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
95           if (_locked) revert ReentrancyError();
96           _locked = true;
97           _;
98           _locked = false;
99       }
100  
101      receive() external payable {}
102  
103      function getZetaFromEth(
104          address destinationAddress,
105:         uint256 minAmountOut

/// @audit Missing '@param destinationAddress'
117              sqrtPriceLimitX96: 0
118          });
119  
120          uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);
121  
122          emit EthExchangedForZeta(msg.value, amountOut);
123          return amountOut;
124      }
125  
126      function getZetaFromToken(
127:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
118          });
119  
120          uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);
121  
122          emit EthExchangedForZeta(msg.value, amountOut);
123          return amountOut;
124      }
125  
126      function getZetaFromToken(
127          address destinationAddress,
128:         uint256 minAmountOut,

/// @audit Missing '@param inputToken'
119  
120          uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);
121  
122          emit EthExchangedForZeta(msg.value, amountOut);
123          return amountOut;
124      }
125  
126      function getZetaFromToken(
127          address destinationAddress,
128          uint256 minAmountOut,
129:         address inputToken,

/// @audit Missing '@param inputTokenAmount'
120          uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);
121  
122          emit EthExchangedForZeta(msg.value, amountOut);
123          return amountOut;
124      }
125  
126      function getZetaFromToken(
127          address destinationAddress,
128          uint256 minAmountOut,
129          address inputToken,
130:         uint256 inputTokenAmount

/// @audit Missing '@param destinationAddress'
142              amountOutMinimum: minAmountOut
143          });
144  
145          uint256 amountOut = pancakeV3Router.exactInput(params);
146  
147          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148          return amountOut;
149      }
150  
151      function getEthFromZeta(
152:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
143          });
144  
145          uint256 amountOut = pancakeV3Router.exactInput(params);
146  
147          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148          return amountOut;
149      }
150  
151      function getEthFromZeta(
152          address destinationAddress,
153:         uint256 minAmountOut,

/// @audit Missing '@param zetaTokenAmount'
144  
145          uint256 amountOut = pancakeV3Router.exactInput(params);
146  
147          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148          return amountOut;
149      }
150  
151      function getEthFromZeta(
152          address destinationAddress,
153          uint256 minAmountOut,
154:         uint256 zetaTokenAmount

/// @audit Missing '@param destinationAddress'
175  
176          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
177  
178          (bool sent, ) = destinationAddress.call{value: amountOut}("");
179          if (!sent) revert ErrorSendingETH();
180  
181          return amountOut;
182      }
183  
184      function getTokenFromZeta(
185:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
176          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
177  
178          (bool sent, ) = destinationAddress.call{value: amountOut}("");
179          if (!sent) revert ErrorSendingETH();
180  
181          return amountOut;
182      }
183  
184      function getTokenFromZeta(
185          address destinationAddress,
186:         uint256 minAmountOut,

/// @audit Missing '@param outputToken'
177  
178          (bool sent, ) = destinationAddress.call{value: amountOut}("");
179          if (!sent) revert ErrorSendingETH();
180  
181          return amountOut;
182      }
183  
184      function getTokenFromZeta(
185          address destinationAddress,
186          uint256 minAmountOut,
187:         address outputToken,

/// @audit Missing '@param zetaTokenAmount'
178          (bool sent, ) = destinationAddress.call{value: amountOut}("");
179          if (!sent) revert ErrorSendingETH();
180  
181          return amountOut;
182      }
183  
184      function getTokenFromZeta(
185          address destinationAddress,
186          uint256 minAmountOut,
187          address outputToken,
188:         uint256 zetaTokenAmount

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L11-L21), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L62-L72), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L63-L73), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L64-L74), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L65-L75), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L66-L76), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L67-L77), [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94-L104), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L95-L105), [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L117-L127), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L118-L128), [119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L119-L129), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L120-L130), [142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L142-L152), [143](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L143-L153), [144](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L144-L154), [175](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L175-L185), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176-L186), [177](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L177-L187), [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178-L188)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit Missing '@param wad'
13       error InputCantBeZero();
14   
15       error ErrorSendingETH();
16   
17       error ReentrancyError();
18   }
19   
20   interface WETH9 {
21       function deposit() external payable;
22   
23:      function withdraw(uint256 wad) external;

/// @audit Missing '@param to'
15       error ErrorSendingETH();
16   
17       error ReentrancyError();
18   }
19   
20   interface WETH9 {
21       function deposit() external payable;
22   
23       function withdraw(uint256 wad) external;
24   
25:      function depositTo(address to) external payable;

/// @audit Missing '@param to'
/// @audit Missing '@param value'
17       error ReentrancyError();
18   }
19   
20   interface WETH9 {
21       function deposit() external payable;
22   
23       function withdraw(uint256 wad) external;
24   
25       function depositTo(address to) external payable;
26   
27:      function withdrawTo(address payable to, uint256 value) external;

/// @audit Missing '@param zetaToken_'
/// @audit Missing '@param uniswapV3Router_'
/// @audit Missing '@param WETH9Address_'
/// @audit Missing '@param poolFactory_'
35       uint256 internal constant MAX_DEADLINE = 200;
36   
37       address internal immutable WETH9Address;
38       address public immutable zetaToken;
39   
40       IPoolRouter public immutable tridentRouter;
41       ConcentratedLiquidityPoolFactory public immutable poolFactory;
42   
43       bool internal _locked;
44   
45:      constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

/// @audit Missing '@param token0'
/// @audit Missing '@param token1'
58   
59       modifier nonReentrant() {
60           if (_locked) revert ReentrancyError();
61           _locked = true;
62           _;
63           _locked = false;
64       }
65   
66       receive() external payable {}
67   
68:      function getPair(address token0, address token1) internal pure returns (address, address) {

/// @audit Missing '@param destinationAddress'
65   
66       receive() external payable {}
67   
68       function getPair(address token0, address token1) internal pure returns (address, address) {
69           if (token0 < token1) return (token0, token1);
70   
71           return (token1, token0);
72       }
73   
74       function getZetaFromEth(
75:          address destinationAddress,

/// @audit Missing '@param minAmountOut'
66       receive() external payable {}
67   
68       function getPair(address token0, address token1) internal pure returns (address, address) {
69           if (token0 < token1) return (token0, token1);
70   
71           return (token1, token0);
72       }
73   
74       function getZetaFromEth(
75           address destinationAddress,
76:          uint256 minAmountOut

/// @audit Missing '@param destinationAddress'
90               unwrap: false
91           });
92   
93           uint256 amountOut = tridentRouter.exactInputSingle{value: msg.value}(params);
94   
95           emit EthExchangedForZeta(msg.value, amountOut);
96           return amountOut;
97       }
98   
99       function getZetaFromToken(
100:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
91           });
92   
93           uint256 amountOut = tridentRouter.exactInputSingle{value: msg.value}(params);
94   
95           emit EthExchangedForZeta(msg.value, amountOut);
96           return amountOut;
97       }
98   
99       function getZetaFromToken(
100          address destinationAddress,
101:         uint256 minAmountOut,

/// @audit Missing '@param inputToken'
92   
93           uint256 amountOut = tridentRouter.exactInputSingle{value: msg.value}(params);
94   
95           emit EthExchangedForZeta(msg.value, amountOut);
96           return amountOut;
97       }
98   
99       function getZetaFromToken(
100          address destinationAddress,
101          uint256 minAmountOut,
102:         address inputToken,

/// @audit Missing '@param inputTokenAmount'
93           uint256 amountOut = tridentRouter.exactInputSingle{value: msg.value}(params);
94   
95           emit EthExchangedForZeta(msg.value, amountOut);
96           return amountOut;
97       }
98   
99       function getZetaFromToken(
100          address destinationAddress,
101          uint256 minAmountOut,
102          address inputToken,
103:         uint256 inputTokenAmount

/// @audit Missing '@param destinationAddress'
127              unwrap: false
128          });
129  
130          uint256 amountOut = tridentRouter.exactInput(params);
131  
132          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133          return amountOut;
134      }
135  
136      function getEthFromZeta(
137:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
128          });
129  
130          uint256 amountOut = tridentRouter.exactInput(params);
131  
132          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133          return amountOut;
134      }
135  
136      function getEthFromZeta(
137          address destinationAddress,
138:         uint256 minAmountOut,

/// @audit Missing '@param zetaTokenAmount'
129  
130          uint256 amountOut = tridentRouter.exactInput(params);
131  
132          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133          return amountOut;
134      }
135  
136      function getEthFromZeta(
137          address destinationAddress,
138          uint256 minAmountOut,
139:         uint256 zetaTokenAmount

/// @audit Missing '@param destinationAddress'
157          });
158  
159          uint256 amountOut = tridentRouter.exactInputSingle(params);
160  
161          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162  
163          return amountOut;
164      }
165  
166      function getTokenFromZeta(
167:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
158  
159          uint256 amountOut = tridentRouter.exactInputSingle(params);
160  
161          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162  
163          return amountOut;
164      }
165  
166      function getTokenFromZeta(
167          address destinationAddress,
168:         uint256 minAmountOut,

/// @audit Missing '@param outputToken'
159          uint256 amountOut = tridentRouter.exactInputSingle(params);
160  
161          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162  
163          return amountOut;
164      }
165  
166      function getTokenFromZeta(
167          address destinationAddress,
168          uint256 minAmountOut,
169:         address outputToken,

/// @audit Missing '@param zetaTokenAmount'
160  
161          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162  
163          return amountOut;
164      }
165  
166      function getTokenFromZeta(
167          address destinationAddress,
168          uint256 minAmountOut,
169          address outputToken,
170:         uint256 zetaTokenAmount

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L13-L23), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L15-L25), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L17-L27), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L17-L27), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L45), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L45), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L45), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L45), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L58-L68), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L58-L68), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L65-L75), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66-L76), [90](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L90-L100), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L91-L101), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L92-L102), [93](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L93-L103), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L127-L137), [128](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L128-L138), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L129-L139), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L157-L167), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L158-L168), [159](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L159-L169), [160](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L160-L170)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

/// @audit Missing '@param zetaToken_'
/// @audit Missing '@param uniswapV2Router_'
16    */
17   contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
18       using SafeERC20 for IERC20;
19       uint256 internal constant MAX_DEADLINE = 200;
20   
21       address internal immutable wETH;
22       address public immutable zetaToken;
23   
24       IUniswapV2Router02 internal immutable uniswapV2Router;
25   
26:      constructor(address zetaToken_, address uniswapV2Router_) {

/// @audit Missing '@param destinationAddress'
25   
26       constructor(address zetaToken_, address uniswapV2Router_) {
27           if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
28   
29           zetaToken = zetaToken_;
30           uniswapV2Router = IUniswapV2Router02(uniswapV2Router_);
31           wETH = IUniswapV2Router02(uniswapV2Router_).WETH();
32       }
33   
34       function getZetaFromEth(
35:          address destinationAddress,

/// @audit Missing '@param minAmountOut'
26       constructor(address zetaToken_, address uniswapV2Router_) {
27           if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
28   
29           zetaToken = zetaToken_;
30           uniswapV2Router = IUniswapV2Router02(uniswapV2Router_);
31           wETH = IUniswapV2Router02(uniswapV2Router_).WETH();
32       }
33   
34       function getZetaFromEth(
35           address destinationAddress,
36:          uint256 minAmountOut

/// @audit Missing '@param destinationAddress'
49               block.timestamp + MAX_DEADLINE
50           );
51   
52           uint256 amountOut = amounts[path.length - 1];
53   
54           emit EthExchangedForZeta(msg.value, amountOut);
55           return amountOut;
56       }
57   
58       function getZetaFromToken(
59:          address destinationAddress,

/// @audit Missing '@param minAmountOut'
50           );
51   
52           uint256 amountOut = amounts[path.length - 1];
53   
54           emit EthExchangedForZeta(msg.value, amountOut);
55           return amountOut;
56       }
57   
58       function getZetaFromToken(
59           address destinationAddress,
60:          uint256 minAmountOut,

/// @audit Missing '@param inputToken'
51   
52           uint256 amountOut = amounts[path.length - 1];
53   
54           emit EthExchangedForZeta(msg.value, amountOut);
55           return amountOut;
56       }
57   
58       function getZetaFromToken(
59           address destinationAddress,
60           uint256 minAmountOut,
61:          address inputToken,

/// @audit Missing '@param inputTokenAmount'
52           uint256 amountOut = amounts[path.length - 1];
53   
54           emit EthExchangedForZeta(msg.value, amountOut);
55           return amountOut;
56       }
57   
58       function getZetaFromToken(
59           address destinationAddress,
60           uint256 minAmountOut,
61           address inputToken,
62:          uint256 inputTokenAmount

/// @audit Missing '@param destinationAddress'
86               destinationAddress,
87               block.timestamp + MAX_DEADLINE
88           );
89           uint256 amountOut = amounts[path.length - 1];
90   
91           emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92           return amountOut;
93       }
94   
95       function getEthFromZeta(
96:          address destinationAddress,

/// @audit Missing '@param minAmountOut'
87               block.timestamp + MAX_DEADLINE
88           );
89           uint256 amountOut = amounts[path.length - 1];
90   
91           emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92           return amountOut;
93       }
94   
95       function getEthFromZeta(
96           address destinationAddress,
97:          uint256 minAmountOut,

/// @audit Missing '@param zetaTokenAmount'
88           );
89           uint256 amountOut = amounts[path.length - 1];
90   
91           emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92           return amountOut;
93       }
94   
95       function getEthFromZeta(
96           address destinationAddress,
97           uint256 minAmountOut,
98:          uint256 zetaTokenAmount

/// @audit Missing '@param destinationAddress'
115              block.timestamp + MAX_DEADLINE
116          );
117  
118          uint256 amountOut = amounts[path.length - 1];
119  
120          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121          return amountOut;
122      }
123  
124      function getTokenFromZeta(
125:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
116          );
117  
118          uint256 amountOut = amounts[path.length - 1];
119  
120          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121          return amountOut;
122      }
123  
124      function getTokenFromZeta(
125          address destinationAddress,
126:         uint256 minAmountOut,

/// @audit Missing '@param outputToken'
117  
118          uint256 amountOut = amounts[path.length - 1];
119  
120          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121          return amountOut;
122      }
123  
124      function getTokenFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127:         address outputToken,

/// @audit Missing '@param zetaTokenAmount'
118          uint256 amountOut = amounts[path.length - 1];
119  
120          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121          return amountOut;
122      }
123  
124      function getTokenFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          address outputToken,
128:         uint256 zetaTokenAmount

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L16-L26), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L16-L26), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L25-L35), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26-L36), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L49-L59), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L50-L60), [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L51-L61), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L52-L62), [86](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L86-L96), [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L87-L97), [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L88-L98), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L115-L125), [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L116-L126), [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L117-L127), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L118-L128)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

/// @audit Missing '@param wad'
11   
12   interface ZetaTokenConsumerUniV3Errors {
13       error InputCantBeZero();
14   
15       error ErrorSendingETH();
16   
17       error ReentrancyError();
18   }
19   
20   interface WETH9 {
21:      function withdraw(uint256 wad) external;

/// @audit Missing '@param zetaToken_'
33   
34       address public immutable WETH9Address;
35       address public immutable zetaToken;
36   
37       ISwapRouter public immutable uniswapV3Router;
38       IUniswapV3Factory public immutable uniswapV3Factory;
39   
40       bool internal _locked;
41   
42       constructor(
43:          address zetaToken_,

/// @audit Missing '@param uniswapV3Router_'
34       address public immutable WETH9Address;
35       address public immutable zetaToken;
36   
37       ISwapRouter public immutable uniswapV3Router;
38       IUniswapV3Factory public immutable uniswapV3Factory;
39   
40       bool internal _locked;
41   
42       constructor(
43           address zetaToken_,
44:          address uniswapV3Router_,

/// @audit Missing '@param uniswapV3Factory_'
35       address public immutable zetaToken;
36   
37       ISwapRouter public immutable uniswapV3Router;
38       IUniswapV3Factory public immutable uniswapV3Factory;
39   
40       bool internal _locked;
41   
42       constructor(
43           address zetaToken_,
44           address uniswapV3Router_,
45:          address uniswapV3Factory_,

/// @audit Missing '@param WETH9Address_'
36   
37       ISwapRouter public immutable uniswapV3Router;
38       IUniswapV3Factory public immutable uniswapV3Factory;
39   
40       bool internal _locked;
41   
42       constructor(
43           address zetaToken_,
44           address uniswapV3Router_,
45           address uniswapV3Factory_,
46:          address WETH9Address_,

/// @audit Missing '@param zetaPoolFee_'
37       ISwapRouter public immutable uniswapV3Router;
38       IUniswapV3Factory public immutable uniswapV3Factory;
39   
40       bool internal _locked;
41   
42       constructor(
43           address zetaToken_,
44           address uniswapV3Router_,
45           address uniswapV3Factory_,
46           address WETH9Address_,
47:          uint24 zetaPoolFee_,

/// @audit Missing '@param tokenPoolFee_'
38       IUniswapV3Factory public immutable uniswapV3Factory;
39   
40       bool internal _locked;
41   
42       constructor(
43           address zetaToken_,
44           address uniswapV3Router_,
45           address uniswapV3Factory_,
46           address WETH9Address_,
47           uint24 zetaPoolFee_,
48:          uint24 tokenPoolFee_

/// @audit Missing '@param destinationAddress'
65       modifier nonReentrant() {
66           if (_locked) revert ReentrancyError();
67           _locked = true;
68           _;
69           _locked = false;
70       }
71   
72       receive() external payable {}
73   
74       function getZetaFromEth(
75:          address destinationAddress,

/// @audit Missing '@param minAmountOut'
66           if (_locked) revert ReentrancyError();
67           _locked = true;
68           _;
69           _locked = false;
70       }
71   
72       receive() external payable {}
73   
74       function getZetaFromEth(
75           address destinationAddress,
76:          uint256 minAmountOut

/// @audit Missing '@param destinationAddress'
89               sqrtPriceLimitX96: 0
90           });
91   
92           uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);
93   
94           emit EthExchangedForZeta(msg.value, amountOut);
95           return amountOut;
96       }
97   
98       function getZetaFromToken(
99:          address destinationAddress,

/// @audit Missing '@param minAmountOut'
90           });
91   
92           uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);
93   
94           emit EthExchangedForZeta(msg.value, amountOut);
95           return amountOut;
96       }
97   
98       function getZetaFromToken(
99           address destinationAddress,
100:         uint256 minAmountOut,

/// @audit Missing '@param inputToken'
91   
92           uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);
93   
94           emit EthExchangedForZeta(msg.value, amountOut);
95           return amountOut;
96       }
97   
98       function getZetaFromToken(
99           address destinationAddress,
100          uint256 minAmountOut,
101:         address inputToken,

/// @audit Missing '@param inputTokenAmount'
92           uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);
93   
94           emit EthExchangedForZeta(msg.value, amountOut);
95           return amountOut;
96       }
97   
98       function getZetaFromToken(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address inputToken,
102:         uint256 inputTokenAmount

/// @audit Missing '@param destinationAddress'
115              amountOutMinimum: minAmountOut
116          });
117  
118          uint256 amountOut = uniswapV3Router.exactInput(params);
119  
120          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121          return amountOut;
122      }
123  
124      function getEthFromZeta(
125:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
116          });
117  
118          uint256 amountOut = uniswapV3Router.exactInput(params);
119  
120          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121          return amountOut;
122      }
123  
124      function getEthFromZeta(
125          address destinationAddress,
126:         uint256 minAmountOut,

/// @audit Missing '@param zetaTokenAmount'
117  
118          uint256 amountOut = uniswapV3Router.exactInput(params);
119  
120          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121          return amountOut;
122      }
123  
124      function getEthFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127:         uint256 zetaTokenAmount

/// @audit Missing '@param destinationAddress'
149  
150          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151  
152          (bool sent, ) = destinationAddress.call{value: amountOut}("");
153          if (!sent) revert ErrorSendingETH();
154  
155          return amountOut;
156      }
157  
158      function getTokenFromZeta(
159:         address destinationAddress,

/// @audit Missing '@param minAmountOut'
150          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151  
152          (bool sent, ) = destinationAddress.call{value: amountOut}("");
153          if (!sent) revert ErrorSendingETH();
154  
155          return amountOut;
156      }
157  
158      function getTokenFromZeta(
159          address destinationAddress,
160:         uint256 minAmountOut,

/// @audit Missing '@param outputToken'
151  
152          (bool sent, ) = destinationAddress.call{value: amountOut}("");
153          if (!sent) revert ErrorSendingETH();
154  
155          return amountOut;
156      }
157  
158      function getTokenFromZeta(
159          address destinationAddress,
160          uint256 minAmountOut,
161:         address outputToken,

/// @audit Missing '@param zetaTokenAmount'
152          (bool sent, ) = destinationAddress.call{value: amountOut}("");
153          if (!sent) revert ErrorSendingETH();
154  
155          return amountOut;
156      }
157  
158      function getTokenFromZeta(
159          address destinationAddress,
160          uint256 minAmountOut,
161          address outputToken,
162:         uint256 zetaTokenAmount

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L11-L21), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L33-L43), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L34-L44), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L35-L45), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L36-L46), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L37-L47), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L38-L48), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65-L75), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L66-L76), [89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L89-L99), [90](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L90-L100), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L91-L101), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L92-L102), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L115-L125), [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L116-L126), [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L117-L127), [149](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L149-L159), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150-L160), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L151-L161), [152](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152-L162)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

/// @audit Missing '@param token0'
8     * #####  ###### #  # # #  ### #      ######    #####  #####  #    #   #   #    # #      #    # #
9     * #      #    # #   ## #    # #      #    #    #      #   #  #    #   #   #    # #    # #    # #
10    * #      #    # #    #  ####  ###### #    #    #      #    #  ####    #    ####   ####   ####  ######
11    *
12    */
13   
14   pragma solidity >=0.8.0;
15   
16   interface ConcentratedLiquidityPoolFactory {
17       function getPools(
18:          address token0,

/// @audit Missing '@param token1'
9     * #      #    # #   ## #    # #      #    #    #      #   #  #    #   #   #    # #    # #    # #
10    * #      #    # #    #  ####  ###### #    #    #      #    #  ####    #    ####   ####   ####  ######
11    *
12    */
13   
14   pragma solidity >=0.8.0;
15   
16   interface ConcentratedLiquidityPoolFactory {
17       function getPools(
18           address token0,
19:          address token1,

/// @audit Missing '@param startIndex'
10    * #      #    # #    #  ####  ###### #    #    #      #    #  ####    #    ####   ####   ####  ######
11    *
12    */
13   
14   pragma solidity >=0.8.0;
15   
16   interface ConcentratedLiquidityPoolFactory {
17       function getPools(
18           address token0,
19           address token1,
20:          uint256 startIndex,

/// @audit Missing '@param count'
11    *
12    */
13   
14   pragma solidity >=0.8.0;
15   
16   interface ConcentratedLiquidityPoolFactory {
17       function getPools(
18           address token0,
19           address token1,
20           uint256 startIndex,
21:          uint256 count

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L8-L18), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L9-L19), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L10-L20), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L11-L21)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

/// @audit Missing '@param token'
/// @audit Missing '@param amount'
/// @audit Missing '@param recipient'
60   
61       /// @notice Swaps as little as possible of one token for `amountOut` of another token
62       /// @param params The parameters necessary for the swap, encoded as ExactOutputSingleParams in calldata
63       function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn);
64   
65       /// @notice Swaps as little as possible of one token for `amountOut` of another along the specified path (reversed)
66       /// @param params The parameters necessary for the multi-hop swap, encoded as ExactOutputParams in calldata
67       function exactOutput(ExactOutputParams calldata params) external payable returns (uint256 amountIn);
68   
69       /// @notice Recover mistakenly sent tokens
70:      function sweep(address token, uint256 amount, address recipient) external payable;

```
*GitHub*: [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L60-L70), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L60-L70), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L60-L70)

```solidity
File: contracts/zevm/Interfaces.sol

/// @audit Missing '@param chainID'
4    /**
5     * @dev Interfaces of SystemContract and ZRC20 to make easier to import.
6     */
7    interface ISystem {
8        function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
9    
10       function wZetaContractAddress() external view returns (address);
11   
12       function uniswapv2FactoryAddress() external view returns (address);
13   
14:      function gasPriceByChainId(uint256 chainID) external view returns (uint256);

/// @audit Missing '@param chainID'
6     */
7    interface ISystem {
8        function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
9    
10       function wZetaContractAddress() external view returns (address);
11   
12       function uniswapv2FactoryAddress() external view returns (address);
13   
14       function gasPriceByChainId(uint256 chainID) external view returns (uint256);
15   
16:      function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

/// @audit Missing '@param chainID'
8        function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
9    
10       function wZetaContractAddress() external view returns (address);
11   
12       function uniswapv2FactoryAddress() external view returns (address);
13   
14       function gasPriceByChainId(uint256 chainID) external view returns (uint256);
15   
16       function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);
17   
18:      function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

/// @audit Missing '@param account'
14       function gasPriceByChainId(uint256 chainID) external view returns (uint256);
15   
16       function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);
17   
18       function gasZetaPoolByChainId(uint256 chainID) external view returns (address);
19   }
20   
21   interface IZRC20 {
22       function totalSupply() external view returns (uint256);
23   
24:      function balanceOf(address account) external view returns (uint256);

/// @audit Missing '@param recipient'
/// @audit Missing '@param amount'
16       function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);
17   
18       function gasZetaPoolByChainId(uint256 chainID) external view returns (address);
19   }
20   
21   interface IZRC20 {
22       function totalSupply() external view returns (uint256);
23   
24       function balanceOf(address account) external view returns (uint256);
25   
26:      function transfer(address recipient, uint256 amount) external returns (bool);

/// @audit Missing '@param owner'
/// @audit Missing '@param spender'
18       function gasZetaPoolByChainId(uint256 chainID) external view returns (address);
19   }
20   
21   interface IZRC20 {
22       function totalSupply() external view returns (uint256);
23   
24       function balanceOf(address account) external view returns (uint256);
25   
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28:      function allowance(address owner, address spender) external view returns (uint256);

/// @audit Missing '@param spender'
/// @audit Missing '@param amount'
20   
21   interface IZRC20 {
22       function totalSupply() external view returns (uint256);
23   
24       function balanceOf(address account) external view returns (uint256);
25   
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28       function allowance(address owner, address spender) external view returns (uint256);
29   
30:      function approve(address spender, uint256 amount) external returns (bool);

/// @audit Missing '@param sender'
/// @audit Missing '@param recipient'
/// @audit Missing '@param amount'
22       function totalSupply() external view returns (uint256);
23   
24       function balanceOf(address account) external view returns (uint256);
25   
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28       function allowance(address owner, address spender) external view returns (uint256);
29   
30       function approve(address spender, uint256 amount) external returns (bool);
31   
32:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

/// @audit Missing '@param to'
/// @audit Missing '@param amount'
24       function balanceOf(address account) external view returns (uint256);
25   
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28       function allowance(address owner, address spender) external view returns (uint256);
29   
30       function approve(address spender, uint256 amount) external returns (bool);
31   
32       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
33   
34:      function deposit(address to, uint256 amount) external returns (bool);

/// @audit Missing '@param to'
/// @audit Missing '@param amount'
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28       function allowance(address owner, address spender) external view returns (uint256);
29   
30       function approve(address spender, uint256 amount) external returns (bool);
31   
32       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
33   
34       function deposit(address to, uint256 amount) external returns (bool);
35   
36:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L4-L14), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L6-L16), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8-L18), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14-L24), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16-L26), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16-L26), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18-L28), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18-L28), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L20-L30), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L20-L30), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22-L32), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22-L32), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22-L32), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24-L34), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24-L34), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26-L36), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26-L36)

```solidity
File: contracts/zevm/SystemContract.sol

/// @audit Missing '@param wzeta_'
/// @audit Missing '@param uniswapv2Factory_'
/// @audit Missing '@param uniswapv2Router02_'
41       event SystemContractDeployed();
42       event SetGasPrice(uint256, uint256);
43       event SetGasCoin(uint256, address);
44       event SetGasZetaPool(uint256, address);
45       event SetWZeta(address);
46       event SetConnectorZEVM(address);
47   
48       /**
49        * @dev Only fungible module can deploy a system contract.
50        */
51:      constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {

```
*GitHub*: [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L41-L51), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L41-L51), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L41-L51)

```solidity
File: contracts/zevm/ZRC20.sol

/// @audit Missing '@param name_'
51        */
52       modifier onlyFungible() {
53           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
54           _;
55       }
56   
57       /**
58        * @dev The only one allowed to deploy new ZRC20 is fungible address.
59        */
60       constructor(
61:          string memory name_,

/// @audit Missing '@param symbol_'
52       modifier onlyFungible() {
53           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
54           _;
55       }
56   
57       /**
58        * @dev The only one allowed to deploy new ZRC20 is fungible address.
59        */
60       constructor(
61           string memory name_,
62:          string memory symbol_,

/// @audit Missing '@param decimals_'
53           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
54           _;
55       }
56   
57       /**
58        * @dev The only one allowed to deploy new ZRC20 is fungible address.
59        */
60       constructor(
61           string memory name_,
62           string memory symbol_,
63:          uint8 decimals_,

/// @audit Missing '@param chainid_'
54           _;
55       }
56   
57       /**
58        * @dev The only one allowed to deploy new ZRC20 is fungible address.
59        */
60       constructor(
61           string memory name_,
62           string memory symbol_,
63           uint8 decimals_,
64:          uint256 chainid_,

/// @audit Missing '@param coinType_'
55       }
56   
57       /**
58        * @dev The only one allowed to deploy new ZRC20 is fungible address.
59        */
60       constructor(
61           string memory name_,
62           string memory symbol_,
63           uint8 decimals_,
64           uint256 chainid_,
65:          CoinType coinType_,

/// @audit Missing '@param gasLimit_'
56   
57       /**
58        * @dev The only one allowed to deploy new ZRC20 is fungible address.
59        */
60       constructor(
61           string memory name_,
62           string memory symbol_,
63           uint8 decimals_,
64           uint256 chainid_,
65           CoinType coinType_,
66:          uint256 gasLimit_,

/// @audit Missing '@param systemContractAddress_'
57       /**
58        * @dev The only one allowed to deploy new ZRC20 is fungible address.
59        */
60       constructor(
61           string memory name_,
62           string memory symbol_,
63           uint8 decimals_,
64           uint256 chainid_,
65           CoinType coinType_,
66           uint256 gasLimit_,
67:          address systemContractAddress_

/// @audit Missing '@param amount'
115       */
116      function balanceOf(address account) public view virtual override returns (uint256) {
117          return _balances[account];
118      }
119  
120      /**
121       * @dev Returns ZRC20 balance of an account.
122       * @param recipient, recipiuent address to which transfer is done.
123       * @return true/false if transfer succeeded/failed.
124       */
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {

/// @audit Missing '@param spender'
125      function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
126          _transfer(_msgSender(), recipient, amount);
127          return true;
128      }
129  
130      /**
131       * @dev Returns token allowance from owner to spender.
132       * @param owner, owner address.
133       * @return uint256 allowance.
134       */
135:     function allowance(address owner, address spender) public view virtual override returns (uint256) {

/// @audit Missing '@param sender'
/// @audit Missing '@param recipient'
/// @audit Missing '@param amount'
168      /**
169       * @dev Burns an amount of tokens.
170       * @param amount, amount to burn.
171       * @return true/false if succeeded/failed.
172       */
173      function burn(uint256 amount) external returns (bool) {
174          _burn(msg.sender, amount);
175          return true;
176      }
177  
178:     function _transfer(address sender, address recipient, uint256 amount) internal virtual {

/// @audit Missing '@param account'
/// @audit Missing '@param amount'
181  
182          uint256 senderBalance = _balances[sender];
183          if (senderBalance < amount) revert LowBalance();
184  
185          _balances[sender] = senderBalance - amount;
186          _balances[recipient] += amount;
187  
188          emit Transfer(sender, recipient, amount);
189      }
190  
191:     function _mint(address account, uint256 amount) internal virtual {

/// @audit Missing '@param account'
/// @audit Missing '@param amount'
189      }
190  
191      function _mint(address account, uint256 amount) internal virtual {
192          if (account == address(0)) revert ZeroAddress();
193  
194          _totalSupply += amount;
195          _balances[account] += amount;
196          emit Transfer(address(0), account, amount);
197      }
198  
199:     function _burn(address account, uint256 amount) internal virtual {

/// @audit Missing '@param owner'
/// @audit Missing '@param spender'
/// @audit Missing '@param amount'
201  
202          uint256 accountBalance = _balances[account];
203          if (accountBalance < amount) revert LowBalance();
204  
205          _balances[account] = accountBalance - amount;
206          _totalSupply -= amount;
207  
208          emit Transfer(account, address(0), amount);
209      }
210  
211:     function _approve(address owner, address spender, uint256 amount) internal virtual {

```
*GitHub*: [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L51-L61), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L52-L62), [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53-L63), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L54-L64), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L55-L65), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L56-L66), [57](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L57-L67), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L115-L125), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125-L135), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L168-L178), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L168-L178), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L168-L178), [181](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L181-L191), [181](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L181-L191), [189](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L189-L199), [189](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L189-L199), [201](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L201-L211), [201](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L201-L211), [201](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L201-L211)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

/// @audit Missing '@param src'
/// @audit Missing '@param dst'
/// @audit Missing '@param wad'
40           uint256 sourceChainId;
41           bytes destinationAddress;
42           uint256 destinationChainId;
43           /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
44           uint256 remainingZetaValue;
45           bytes message;
46       }
47   }
48   
49   interface WZETA {
50:      function transferFrom(address src, address dst, uint wad) external returns (bool);

/// @audit Missing '@param wad'
42           uint256 destinationChainId;
43           /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
44           uint256 remainingZetaValue;
45           bytes message;
46       }
47   }
48   
49   interface WZETA {
50       function transferFrom(address src, address dst, uint wad) external returns (bool);
51   
52:      function withdraw(uint wad) external;

/// @audit Missing '@param wzeta_'
69           address indexed zetaTxSenderAddress,
70           uint256 indexed destinationChainId,
71           bytes destinationAddress,
72           uint256 zetaValueAndGas,
73           uint256 destinationGasLimit,
74           bytes message,
75           bytes zetaParams
76       );
77       event SetWZETA(address wzeta_);
78   
79:      constructor(address wzeta_) {

```
*GitHub*: [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L40-L50), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L40-L50), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L40-L50), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L42-L52), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L69-L79)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

/// @audit Missing '@param tokenA'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IUniswapV2Router01 {
5        function factory() external pure returns (address);
6    
7        function WETH() external pure returns (address);
8    
9        function addLiquidity(
10:          address tokenA,

/// @audit Missing '@param tokenB'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IUniswapV2Router01 {
5        function factory() external pure returns (address);
6    
7        function WETH() external pure returns (address);
8    
9        function addLiquidity(
10           address tokenA,
11:          address tokenB,

/// @audit Missing '@param amountADesired'
2    pragma solidity 0.8.7;
3    
4    interface IUniswapV2Router01 {
5        function factory() external pure returns (address);
6    
7        function WETH() external pure returns (address);
8    
9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12:          uint amountADesired,

/// @audit Missing '@param amountBDesired'
3    
4    interface IUniswapV2Router01 {
5        function factory() external pure returns (address);
6    
7        function WETH() external pure returns (address);
8    
9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13:          uint amountBDesired,

/// @audit Missing '@param amountAMin'
4    interface IUniswapV2Router01 {
5        function factory() external pure returns (address);
6    
7        function WETH() external pure returns (address);
8    
9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14:          uint amountAMin,

/// @audit Missing '@param amountBMin'
5        function factory() external pure returns (address);
6    
7        function WETH() external pure returns (address);
8    
9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15:          uint amountBMin,

/// @audit Missing '@param to'
6    
7        function WETH() external pure returns (address);
8    
9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16:          address to,

/// @audit Missing '@param deadline'
7        function WETH() external pure returns (address);
8    
9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17:          uint deadline

/// @audit Missing '@param token'
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17           uint deadline
18       ) external returns (uint amountA, uint amountB, uint liquidity);
19   
20       function addLiquidityETH(
21:          address token,

/// @audit Missing '@param amountTokenDesired'
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17           uint deadline
18       ) external returns (uint amountA, uint amountB, uint liquidity);
19   
20       function addLiquidityETH(
21           address token,
22:          uint amountTokenDesired,

/// @audit Missing '@param amountTokenMin'
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17           uint deadline
18       ) external returns (uint amountA, uint amountB, uint liquidity);
19   
20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23:          uint amountTokenMin,

/// @audit Missing '@param amountETHMin'
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17           uint deadline
18       ) external returns (uint amountA, uint amountB, uint liquidity);
19   
20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24:          uint amountETHMin,

/// @audit Missing '@param to'
15           uint amountBMin,
16           address to,
17           uint deadline
18       ) external returns (uint amountA, uint amountB, uint liquidity);
19   
20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25:          address to,

/// @audit Missing '@param deadline'
16           address to,
17           uint deadline
18       ) external returns (uint amountA, uint amountB, uint liquidity);
19   
20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26:          uint deadline

/// @audit Missing '@param tokenA'
20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26           uint deadline
27       ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
28   
29       function removeLiquidity(
30:          address tokenA,

/// @audit Missing '@param tokenB'
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26           uint deadline
27       ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
28   
29       function removeLiquidity(
30           address tokenA,
31:          address tokenB,

/// @audit Missing '@param liquidity'
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26           uint deadline
27       ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
28   
29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32:          uint liquidity,

/// @audit Missing '@param amountAMin'
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26           uint deadline
27       ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
28   
29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33:          uint amountAMin,

/// @audit Missing '@param amountBMin'
24           uint amountETHMin,
25           address to,
26           uint deadline
27       ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
28   
29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34:          uint amountBMin,

/// @audit Missing '@param to'
25           address to,
26           uint deadline
27       ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
28   
29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35:          address to,

/// @audit Missing '@param deadline'
26           uint deadline
27       ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
28   
29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36:          uint deadline

/// @audit Missing '@param token'
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36           uint deadline
37       ) external returns (uint amountA, uint amountB);
38   
39       function removeLiquidityETH(
40:          address token,

/// @audit Missing '@param liquidity'
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36           uint deadline
37       ) external returns (uint amountA, uint amountB);
38   
39       function removeLiquidityETH(
40           address token,
41:          uint liquidity,

/// @audit Missing '@param amountTokenMin'
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36           uint deadline
37       ) external returns (uint amountA, uint amountB);
38   
39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42:          uint amountTokenMin,

/// @audit Missing '@param amountETHMin'
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36           uint deadline
37       ) external returns (uint amountA, uint amountB);
38   
39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43:          uint amountETHMin,

/// @audit Missing '@param to'
34           uint amountBMin,
35           address to,
36           uint deadline
37       ) external returns (uint amountA, uint amountB);
38   
39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44:          address to,

/// @audit Missing '@param deadline'
35           address to,
36           uint deadline
37       ) external returns (uint amountA, uint amountB);
38   
39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45:          uint deadline

/// @audit Missing '@param tokenA'
39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45           uint deadline
46       ) external returns (uint amountToken, uint amountETH);
47   
48       function removeLiquidityWithPermit(
49:          address tokenA,

/// @audit Missing '@param tokenB'
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45           uint deadline
46       ) external returns (uint amountToken, uint amountETH);
47   
48       function removeLiquidityWithPermit(
49           address tokenA,
50:          address tokenB,

/// @audit Missing '@param liquidity'
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45           uint deadline
46       ) external returns (uint amountToken, uint amountETH);
47   
48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51:          uint liquidity,

/// @audit Missing '@param amountAMin'
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45           uint deadline
46       ) external returns (uint amountToken, uint amountETH);
47   
48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52:          uint amountAMin,

/// @audit Missing '@param amountBMin'
43           uint amountETHMin,
44           address to,
45           uint deadline
46       ) external returns (uint amountToken, uint amountETH);
47   
48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53:          uint amountBMin,

/// @audit Missing '@param to'
44           address to,
45           uint deadline
46       ) external returns (uint amountToken, uint amountETH);
47   
48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54:          address to,

/// @audit Missing '@param deadline'
45           uint deadline
46       ) external returns (uint amountToken, uint amountETH);
47   
48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55:          uint deadline,

/// @audit Missing '@param approveMax'
46       ) external returns (uint amountToken, uint amountETH);
47   
48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55           uint deadline,
56:          bool approveMax,

/// @audit Missing '@param v'
47   
48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55           uint deadline,
56           bool approveMax,
57:          uint8 v,

/// @audit Missing '@param r'
48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58:          bytes32 r,

/// @audit Missing '@param s'
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59:          bytes32 s

/// @audit Missing '@param token'
53           uint amountBMin,
54           address to,
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60       ) external returns (uint amountA, uint amountB);
61   
62       function removeLiquidityETHWithPermit(
63:          address token,

/// @audit Missing '@param liquidity'
54           address to,
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60       ) external returns (uint amountA, uint amountB);
61   
62       function removeLiquidityETHWithPermit(
63           address token,
64:          uint liquidity,

/// @audit Missing '@param amountTokenMin'
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60       ) external returns (uint amountA, uint amountB);
61   
62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65:          uint amountTokenMin,

/// @audit Missing '@param amountETHMin'
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60       ) external returns (uint amountA, uint amountB);
61   
62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66:          uint amountETHMin,

/// @audit Missing '@param to'
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60       ) external returns (uint amountA, uint amountB);
61   
62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67:          address to,

/// @audit Missing '@param deadline'
58           bytes32 r,
59           bytes32 s
60       ) external returns (uint amountA, uint amountB);
61   
62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68:          uint deadline,

/// @audit Missing '@param approveMax'
59           bytes32 s
60       ) external returns (uint amountA, uint amountB);
61   
62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68           uint deadline,
69:          bool approveMax,

/// @audit Missing '@param v'
60       ) external returns (uint amountA, uint amountB);
61   
62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68           uint deadline,
69           bool approveMax,
70:          uint8 v,

/// @audit Missing '@param r'
61   
62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71:          bytes32 r,

/// @audit Missing '@param s'
62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72:          bytes32 s

/// @audit Missing '@param amountIn'
66           uint amountETHMin,
67           address to,
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73       ) external returns (uint amountToken, uint amountETH);
74   
75       function swapExactTokensForTokens(
76:          uint amountIn,

/// @audit Missing '@param amountOutMin'
67           address to,
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73       ) external returns (uint amountToken, uint amountETH);
74   
75       function swapExactTokensForTokens(
76           uint amountIn,
77:          uint amountOutMin,

/// @audit Missing '@param path'
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73       ) external returns (uint amountToken, uint amountETH);
74   
75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78:          address[] calldata path,

/// @audit Missing '@param to'
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73       ) external returns (uint amountToken, uint amountETH);
74   
75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79:          address to,

/// @audit Missing '@param deadline'
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73       ) external returns (uint amountToken, uint amountETH);
74   
75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80:          uint deadline

/// @audit Missing '@param amountOut'
74   
75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80           uint deadline
81       ) external returns (uint[] memory amounts);
82   
83       function swapTokensForExactTokens(
84:          uint amountOut,

/// @audit Missing '@param amountInMax'
75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80           uint deadline
81       ) external returns (uint[] memory amounts);
82   
83       function swapTokensForExactTokens(
84           uint amountOut,
85:          uint amountInMax,

/// @audit Missing '@param path'
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80           uint deadline
81       ) external returns (uint[] memory amounts);
82   
83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86:          address[] calldata path,

/// @audit Missing '@param to'
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80           uint deadline
81       ) external returns (uint[] memory amounts);
82   
83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87:          address to,

/// @audit Missing '@param deadline'
78           address[] calldata path,
79           address to,
80           uint deadline
81       ) external returns (uint[] memory amounts);
82   
83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88:          uint deadline

/// @audit Missing '@param amountOutMin'
82   
83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88           uint deadline
89       ) external returns (uint[] memory amounts);
90   
91       function swapExactETHForTokens(
92:          uint amountOutMin,

/// @audit Missing '@param path'
83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88           uint deadline
89       ) external returns (uint[] memory amounts);
90   
91       function swapExactETHForTokens(
92           uint amountOutMin,
93:          address[] calldata path,

/// @audit Missing '@param to'
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88           uint deadline
89       ) external returns (uint[] memory amounts);
90   
91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94:          address to,

/// @audit Missing '@param deadline'
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88           uint deadline
89       ) external returns (uint[] memory amounts);
90   
91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95:          uint deadline

/// @audit Missing '@param amountOut'
89       ) external returns (uint[] memory amounts);
90   
91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95           uint deadline
96       ) external payable returns (uint[] memory amounts);
97   
98       function swapTokensForExactETH(
99:          uint amountOut,

/// @audit Missing '@param amountInMax'
90   
91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95           uint deadline
96       ) external payable returns (uint[] memory amounts);
97   
98       function swapTokensForExactETH(
99           uint amountOut,
100:         uint amountInMax,

/// @audit Missing '@param path'
91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95           uint deadline
96       ) external payable returns (uint[] memory amounts);
97   
98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101:         address[] calldata path,

/// @audit Missing '@param to'
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95           uint deadline
96       ) external payable returns (uint[] memory amounts);
97   
98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102:         address to,

/// @audit Missing '@param deadline'
93           address[] calldata path,
94           address to,
95           uint deadline
96       ) external payable returns (uint[] memory amounts);
97   
98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103:         uint deadline

/// @audit Missing '@param amountIn'
97   
98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103          uint deadline
104      ) external returns (uint[] memory amounts);
105  
106      function swapExactTokensForETH(
107:         uint amountIn,

/// @audit Missing '@param amountOutMin'
98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103          uint deadline
104      ) external returns (uint[] memory amounts);
105  
106      function swapExactTokensForETH(
107          uint amountIn,
108:         uint amountOutMin,

/// @audit Missing '@param path'
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103          uint deadline
104      ) external returns (uint[] memory amounts);
105  
106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109:         address[] calldata path,

/// @audit Missing '@param to'
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103          uint deadline
104      ) external returns (uint[] memory amounts);
105  
106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110:         address to,

/// @audit Missing '@param deadline'
101          address[] calldata path,
102          address to,
103          uint deadline
104      ) external returns (uint[] memory amounts);
105  
106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111:         uint deadline

/// @audit Missing '@param amountOut'
105  
106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111          uint deadline
112      ) external returns (uint[] memory amounts);
113  
114      function swapETHForExactTokens(
115:         uint amountOut,

/// @audit Missing '@param path'
106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111          uint deadline
112      ) external returns (uint[] memory amounts);
113  
114      function swapETHForExactTokens(
115          uint amountOut,
116:         address[] calldata path,

/// @audit Missing '@param to'
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111          uint deadline
112      ) external returns (uint[] memory amounts);
113  
114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117:         address to,

/// @audit Missing '@param deadline'
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111          uint deadline
112      ) external returns (uint[] memory amounts);
113  
114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117          address to,
118:         uint deadline

/// @audit Missing '@param amountA'
/// @audit Missing '@param reserveA'
/// @audit Missing '@param reserveB'
111          uint deadline
112      ) external returns (uint[] memory amounts);
113  
114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119      ) external payable returns (uint[] memory amounts);
120  
121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

/// @audit Missing '@param amountIn'
/// @audit Missing '@param reserveIn'
/// @audit Missing '@param reserveOut'
113  
114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119      ) external payable returns (uint[] memory amounts);
120  
121      function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);
122  
123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

/// @audit Missing '@param amountOut'
/// @audit Missing '@param reserveIn'
/// @audit Missing '@param reserveOut'
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119      ) external payable returns (uint[] memory amounts);
120  
121      function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);
122  
123      function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);
124  
125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

/// @audit Missing '@param amountIn'
/// @audit Missing '@param path'
117          address to,
118          uint deadline
119      ) external payable returns (uint[] memory amounts);
120  
121      function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);
122  
123      function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);
124  
125      function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);
126  
127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

/// @audit Missing '@param amountOut'
/// @audit Missing '@param path'
119      ) external payable returns (uint[] memory amounts);
120  
121      function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);
122  
123      function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);
124  
125      function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);
126  
127      function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
128  
129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L1-L10), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L1-L11), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L2-L12), [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L3-L13), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4-L14), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5-L15), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L6-L16), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7-L17), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L11-L21), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L12-L22), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L13-L23), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L14-L24), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L15-L25), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L16-L26), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L30), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L21-L31), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L22-L32), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L23-L33), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L24-L34), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L25-L35), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L26-L36), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L30-L40), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L31-L41), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L32-L42), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L33-L43), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L34-L44), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L35-L45), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L49), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L40-L50), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L41-L51), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L42-L52), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L43-L53), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L44-L54), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L45-L55), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L46-L56), [47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L47-L57), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L58), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L49-L59), [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L53-L63), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L54-L64), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L55-L65), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L56-L66), [57](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L57-L67), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L58-L68), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L59-L69), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L60-L70), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L61-L71), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L72), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L66-L76), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L67-L77), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L68-L78), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L69-L79), [70](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L70-L80), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L74-L84), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L85), [76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L76-L86), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L77-L87), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L78-L88), [82](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L82-L92), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L93), [84](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L84-L94), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L85-L95), [89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L89-L99), [90](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L90-L100), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91-L101), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L92-L102), [93](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L93-L103), [97](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L97-L107), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L108), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L99-L109), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L100-L110), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L101-L111), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L105-L115), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L116), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L107-L117), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L108-L118), [111](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L111-L121), [111](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L111-L121), [111](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L111-L121), [113](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L113-L123), [113](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L113-L123), [113](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L113-L123), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L115-L125), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L115-L125), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L115-L125), [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L117-L127), [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L117-L127), [119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L119-L129), [119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L119-L129)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

/// @audit Missing '@param token'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    import "./IUniswapV2Router01.sol";
5    
6    interface IUniswapV2Router02 is IUniswapV2Router01 {
7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8:           address token,

/// @audit Missing '@param liquidity'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    import "./IUniswapV2Router01.sol";
5    
6    interface IUniswapV2Router02 is IUniswapV2Router01 {
7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9:           uint liquidity,

/// @audit Missing '@param amountTokenMin'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    import "./IUniswapV2Router01.sol";
5    
6    interface IUniswapV2Router02 is IUniswapV2Router01 {
7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10:          uint amountTokenMin,

/// @audit Missing '@param amountETHMin'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    import "./IUniswapV2Router01.sol";
5    
6    interface IUniswapV2Router02 is IUniswapV2Router01 {
7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11:          uint amountETHMin,

/// @audit Missing '@param to'
2    pragma solidity 0.8.7;
3    
4    import "./IUniswapV2Router01.sol";
5    
6    interface IUniswapV2Router02 is IUniswapV2Router01 {
7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12:          address to,

/// @audit Missing '@param deadline'
3    
4    import "./IUniswapV2Router01.sol";
5    
6    interface IUniswapV2Router02 is IUniswapV2Router01 {
7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13:          uint deadline

/// @audit Missing '@param token'
7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13           uint deadline
14       ) external returns (uint amountETH);
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17:          address token,

/// @audit Missing '@param liquidity'
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13           uint deadline
14       ) external returns (uint amountETH);
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18:          uint liquidity,

/// @audit Missing '@param amountTokenMin'
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13           uint deadline
14       ) external returns (uint amountETH);
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19:          uint amountTokenMin,

/// @audit Missing '@param amountETHMin'
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13           uint deadline
14       ) external returns (uint amountETH);
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20:          uint amountETHMin,

/// @audit Missing '@param to'
11           uint amountETHMin,
12           address to,
13           uint deadline
14       ) external returns (uint amountETH);
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21:          address to,

/// @audit Missing '@param deadline'
12           address to,
13           uint deadline
14       ) external returns (uint amountETH);
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21           address to,
22:          uint deadline,

/// @audit Missing '@param approveMax'
13           uint deadline
14       ) external returns (uint amountETH);
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21           address to,
22           uint deadline,
23:          bool approveMax,

/// @audit Missing '@param v'
14       ) external returns (uint amountETH);
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21           address to,
22           uint deadline,
23           bool approveMax,
24:          uint8 v,

/// @audit Missing '@param r'
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21           address to,
22           uint deadline,
23           bool approveMax,
24           uint8 v,
25:          bytes32 r,

/// @audit Missing '@param s'
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21           address to,
22           uint deadline,
23           bool approveMax,
24           uint8 v,
25           bytes32 r,
26:          bytes32 s

/// @audit Missing '@param amountIn'
20           uint amountETHMin,
21           address to,
22           uint deadline,
23           bool approveMax,
24           uint8 v,
25           bytes32 r,
26           bytes32 s
27       ) external returns (uint amountETH);
28   
29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30:          uint amountIn,

/// @audit Missing '@param amountOutMin'
21           address to,
22           uint deadline,
23           bool approveMax,
24           uint8 v,
25           bytes32 r,
26           bytes32 s
27       ) external returns (uint amountETH);
28   
29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30           uint amountIn,
31:          uint amountOutMin,

/// @audit Missing '@param path'
22           uint deadline,
23           bool approveMax,
24           uint8 v,
25           bytes32 r,
26           bytes32 s
27       ) external returns (uint amountETH);
28   
29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30           uint amountIn,
31           uint amountOutMin,
32:          address[] calldata path,

/// @audit Missing '@param to'
23           bool approveMax,
24           uint8 v,
25           bytes32 r,
26           bytes32 s
27       ) external returns (uint amountETH);
28   
29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30           uint amountIn,
31           uint amountOutMin,
32           address[] calldata path,
33:          address to,

/// @audit Missing '@param deadline'
24           uint8 v,
25           bytes32 r,
26           bytes32 s
27       ) external returns (uint amountETH);
28   
29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30           uint amountIn,
31           uint amountOutMin,
32           address[] calldata path,
33           address to,
34:          uint deadline

/// @audit Missing '@param amountOutMin'
28   
29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30           uint amountIn,
31           uint amountOutMin,
32           address[] calldata path,
33           address to,
34           uint deadline
35       ) external;
36   
37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38:          uint amountOutMin,

/// @audit Missing '@param path'
29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30           uint amountIn,
31           uint amountOutMin,
32           address[] calldata path,
33           address to,
34           uint deadline
35       ) external;
36   
37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38           uint amountOutMin,
39:          address[] calldata path,

/// @audit Missing '@param to'
30           uint amountIn,
31           uint amountOutMin,
32           address[] calldata path,
33           address to,
34           uint deadline
35       ) external;
36   
37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38           uint amountOutMin,
39           address[] calldata path,
40:          address to,

/// @audit Missing '@param deadline'
31           uint amountOutMin,
32           address[] calldata path,
33           address to,
34           uint deadline
35       ) external;
36   
37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38           uint amountOutMin,
39           address[] calldata path,
40           address to,
41:          uint deadline

/// @audit Missing '@param amountIn'
35       ) external;
36   
37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38           uint amountOutMin,
39           address[] calldata path,
40           address to,
41           uint deadline
42       ) external payable;
43   
44       function swapExactTokensForETHSupportingFeeOnTransferTokens(
45:          uint amountIn,

/// @audit Missing '@param amountOutMin'
36   
37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38           uint amountOutMin,
39           address[] calldata path,
40           address to,
41           uint deadline
42       ) external payable;
43   
44       function swapExactTokensForETHSupportingFeeOnTransferTokens(
45           uint amountIn,
46:          uint amountOutMin,

/// @audit Missing '@param path'
37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38           uint amountOutMin,
39           address[] calldata path,
40           address to,
41           uint deadline
42       ) external payable;
43   
44       function swapExactTokensForETHSupportingFeeOnTransferTokens(
45           uint amountIn,
46           uint amountOutMin,
47:          address[] calldata path,

/// @audit Missing '@param to'
38           uint amountOutMin,
39           address[] calldata path,
40           address to,
41           uint deadline
42       ) external payable;
43   
44       function swapExactTokensForETHSupportingFeeOnTransferTokens(
45           uint amountIn,
46           uint amountOutMin,
47           address[] calldata path,
48:          address to,

/// @audit Missing '@param deadline'
39           address[] calldata path,
40           address to,
41           uint deadline
42       ) external payable;
43   
44       function swapExactTokensForETHSupportingFeeOnTransferTokens(
45           uint amountIn,
46           uint amountOutMin,
47           address[] calldata path,
48           address to,
49:          uint deadline

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L1-L8), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L1-L9), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L1-L10), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L1-L11), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L2-L12), [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L3-L13), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7-L17), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L8-L18), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L9-L19), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L10-L20), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L11-L21), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L12-L22), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L13-L23), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L14-L24), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L15-L25), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L26), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L20-L30), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L21-L31), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L22-L32), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L23-L33), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L24-L34), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L28-L38), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29-L39), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L30-L40), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L31-L41), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L35-L45), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L36-L46), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37-L47), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L38-L48), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L39-L49)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

/// @audit Missing '@param owner'
2    pragma solidity 0.8.7;
3    
4    interface IWETH9 {
5        event Approval(address indexed owner, address indexed spender, uint value);
6        event Transfer(address indexed from, address indexed to, uint value);
7        event Deposit(address indexed dst, uint wad);
8        event Withdrawal(address indexed src, uint wad);
9    
10       function totalSupply() external view returns (uint);
11   
12:      function balanceOf(address owner) external view returns (uint);

/// @audit Missing '@param owner'
/// @audit Missing '@param spender'
4    interface IWETH9 {
5        event Approval(address indexed owner, address indexed spender, uint value);
6        event Transfer(address indexed from, address indexed to, uint value);
7        event Deposit(address indexed dst, uint wad);
8        event Withdrawal(address indexed src, uint wad);
9    
10       function totalSupply() external view returns (uint);
11   
12       function balanceOf(address owner) external view returns (uint);
13   
14:      function allowance(address owner, address spender) external view returns (uint);

/// @audit Missing '@param spender'
/// @audit Missing '@param wad'
6        event Transfer(address indexed from, address indexed to, uint value);
7        event Deposit(address indexed dst, uint wad);
8        event Withdrawal(address indexed src, uint wad);
9    
10       function totalSupply() external view returns (uint);
11   
12       function balanceOf(address owner) external view returns (uint);
13   
14       function allowance(address owner, address spender) external view returns (uint);
15   
16:      function approve(address spender, uint wad) external returns (bool);

/// @audit Missing '@param to'
/// @audit Missing '@param wad'
8        event Withdrawal(address indexed src, uint wad);
9    
10       function totalSupply() external view returns (uint);
11   
12       function balanceOf(address owner) external view returns (uint);
13   
14       function allowance(address owner, address spender) external view returns (uint);
15   
16       function approve(address spender, uint wad) external returns (bool);
17   
18:      function transfer(address to, uint wad) external returns (bool);

/// @audit Missing '@param from'
/// @audit Missing '@param to'
/// @audit Missing '@param wad'
10       function totalSupply() external view returns (uint);
11   
12       function balanceOf(address owner) external view returns (uint);
13   
14       function allowance(address owner, address spender) external view returns (uint);
15   
16       function approve(address spender, uint wad) external returns (bool);
17   
18       function transfer(address to, uint wad) external returns (bool);
19   
20:      function transferFrom(address from, address to, uint wad) external returns (bool);

/// @audit Missing '@param wad'
14       function allowance(address owner, address spender) external view returns (uint);
15   
16       function approve(address spender, uint wad) external returns (bool);
17   
18       function transfer(address to, uint wad) external returns (bool);
19   
20       function transferFrom(address from, address to, uint wad) external returns (bool);
21   
22       function deposit() external payable;
23   
24:      function withdraw(uint wad) external;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L2-L12), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4-L14), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4-L14), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L16), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L16), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8-L18), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8-L18), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10-L20), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10-L20), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10-L20), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14-L24)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

/// @audit Missing '@param account'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IZRC20 {
5        function totalSupply() external view returns (uint256);
6    
7:       function balanceOf(address account) external view returns (uint256);

/// @audit Missing '@param recipient'
/// @audit Missing '@param amount'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IZRC20 {
5        function totalSupply() external view returns (uint256);
6    
7        function balanceOf(address account) external view returns (uint256);
8    
9:       function transfer(address recipient, uint256 amount) external returns (bool);

/// @audit Missing '@param owner'
/// @audit Missing '@param spender'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IZRC20 {
5        function totalSupply() external view returns (uint256);
6    
7        function balanceOf(address account) external view returns (uint256);
8    
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11:      function allowance(address owner, address spender) external view returns (uint256);

/// @audit Missing '@param spender'
/// @audit Missing '@param amount'
3    
4    interface IZRC20 {
5        function totalSupply() external view returns (uint256);
6    
7        function balanceOf(address account) external view returns (uint256);
8    
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13:      function approve(address spender, uint256 amount) external returns (bool);

/// @audit Missing '@param spender'
/// @audit Missing '@param amount'
5        function totalSupply() external view returns (uint256);
6    
7        function balanceOf(address account) external view returns (uint256);
8    
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15:      function decreaseAllowance(address spender, uint256 amount) external returns (bool);

/// @audit Missing '@param spender'
/// @audit Missing '@param amount'
7        function balanceOf(address account) external view returns (uint256);
8    
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17:      function increaseAllowance(address spender, uint256 amount) external returns (bool);

/// @audit Missing '@param sender'
/// @audit Missing '@param recipient'
/// @audit Missing '@param amount'
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17       function increaseAllowance(address spender, uint256 amount) external returns (bool);
18   
19:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

/// @audit Missing '@param to'
/// @audit Missing '@param amount'
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17       function increaseAllowance(address spender, uint256 amount) external returns (bool);
18   
19       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
20   
21:      function deposit(address to, uint256 amount) external returns (bool);

/// @audit Missing '@param account'
/// @audit Missing '@param amount'
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17       function increaseAllowance(address spender, uint256 amount) external returns (bool);
18   
19       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
20   
21       function deposit(address to, uint256 amount) external returns (bool);
22   
23:      function burn(address account, uint256 amount) external returns (bool);

/// @audit Missing '@param to'
/// @audit Missing '@param amount'
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17       function increaseAllowance(address spender, uint256 amount) external returns (bool);
18   
19       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
20   
21       function deposit(address to, uint256 amount) external returns (bool);
22   
23       function burn(address account, uint256 amount) external returns (bool);
24   
25:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L1-L7), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L1-L9), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L1-L9), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L1-L11), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L1-L11), [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L3-L13), [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L3-L13), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5-L15), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5-L15), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7-L17), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7-L17), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9-L19), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9-L19), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9-L19), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11-L21), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11-L21), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13-L23), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13-L23), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15-L25), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15-L25)

```solidity
File: contracts/zevm/interfaces/zContract.sol

/// @audit Missing '@param context'
2    pragma solidity 0.8.7;
3    
4    struct zContext {
5        bytes origin;
6        address sender;
7        uint256 chainID;
8    }
9    
10   interface zContract {
11       function onCrossChainCall(
12:          zContext calldata context,

/// @audit Missing '@param zrc20'
3    
4    struct zContext {
5        bytes origin;
6        address sender;
7        uint256 chainID;
8    }
9    
10   interface zContract {
11       function onCrossChainCall(
12           zContext calldata context,
13:          address zrc20,

/// @audit Missing '@param amount'
4    struct zContext {
5        bytes origin;
6        address sender;
7        uint256 chainID;
8    }
9    
10   interface zContract {
11       function onCrossChainCall(
12           zContext calldata context,
13           address zrc20,
14:          uint256 amount,

/// @audit Missing '@param message'
5        bytes origin;
6        address sender;
7        uint256 chainID;
8    }
9    
10   interface zContract {
11       function onCrossChainCall(
12           zContext calldata context,
13           address zrc20,
14           uint256 amount,
15:          bytes calldata message

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L2-L12), [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L3-L13), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L4-L14), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L5-L15)

</details>





### [N&#x2011;49] NatSpec: Function `@return` tag is missing


*There are 103 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ZetaConnector.eth.sol

/// @audit Missing '@return  '
13    * This version is only for Ethereum network because in the other chains we mint and burn and in this one we lock and unlock.
14    */
15   contract ZetaConnectorEth is ZetaConnectorBase {
16       constructor(
17           address zetaToken_,
18           address tssAddress_,
19           address tssAddressUpdater_,
20           address pauserAddress_
21       ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
22   
23:      function getLockedAmount() external view returns (uint256) {

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L13-L23)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

/// @audit Missing '@return  '
17   
18       event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
19   
20       constructor(
21           address zetaTokenAddress_,
22           address tssAddress_,
23           address tssAddressUpdater_,
24           address pauserAddress_
25       ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
26   
27:      function getLockedAmount() external view returns (uint256) {

```
*GitHub*: [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L17-L27)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

/// @audit Missing '@return  '
73    *   - Getting native coin using Zeta (to return unused destination gas when `onZetaRevert` is executed)
74    *   - Getting a token using Zeta (to return unused destination gas when `onZetaRevert` is executed)
75    * @dev The interface can be implemented using different strategies, like UniswapV2, UniswapV3, etc
76    */
77   interface ZetaTokenConsumer {
78       event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
79       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
80       event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
81       event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
82   
83:      function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

/// @audit Missing '@return  '
75    * @dev The interface can be implemented using different strategies, like UniswapV2, UniswapV3, etc
76    */
77   interface ZetaTokenConsumer {
78       event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
79       event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
80       event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
81       event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
82   
83       function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);
84   
85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89           uint256 inputTokenAmount
90:      ) external returns (uint256);

/// @audit Missing '@return  '
82   
83       function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);
84   
85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89           uint256 inputTokenAmount
90       ) external returns (uint256);
91   
92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96:      ) external returns (uint256);

/// @audit Missing '@return  '
88           address inputToken,
89           uint256 inputTokenAmount
90       ) external returns (uint256);
91   
92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96       ) external returns (uint256);
97   
98       function getTokenFromZeta(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address outputToken,
102          uint256 zetaTokenAmount
103:     ) external returns (uint256);

/// @audit Missing '@return  '
95           uint256 zetaTokenAmount
96       ) external returns (uint256);
97   
98       function getTokenFromZeta(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address outputToken,
102          uint256 zetaTokenAmount
103      ) external returns (uint256);
104  
105:     function hasZetaLiquidity() external view returns (bool);

```
*GitHub*: [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L73-L83), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L75-L90), [82](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L82-L96), [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L88-L103), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L95-L105)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

/// @audit Missing '@return  '
40           connector = ZetaConnector(zetaConnectorAddress);
41       }
42   
43       function _isValidCaller() private view {
44           if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
45       }
46   
47       /**
48        * @dev Useful for contracts that inherit from this one
49        */
50:      function _isValidChainId(uint256 chainId) internal view returns (bool) {

```
*GitHub*: [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L40-L50)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

/// @audit Missing '@return  '
93   
94       modifier nonReentrant() {
95           if (_locked) revert ReentrancyError();
96           _locked = true;
97           _;
98           _locked = false;
99       }
100  
101      receive() external payable {}
102  
103      function getZetaFromEth(
104          address destinationAddress,
105          uint256 minAmountOut
106:     ) external payable override returns (uint256) {

/// @audit Missing '@return  '
116              amountOutMinimum: minAmountOut,
117              sqrtPriceLimitX96: 0
118          });
119  
120          uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);
121  
122          emit EthExchangedForZeta(msg.value, amountOut);
123          return amountOut;
124      }
125  
126      function getZetaFromToken(
127          address destinationAddress,
128          uint256 minAmountOut,
129          address inputToken,
130          uint256 inputTokenAmount
131:     ) external override returns (uint256) {

/// @audit Missing '@return  '
141              amountIn: inputTokenAmount,
142              amountOutMinimum: minAmountOut
143          });
144  
145          uint256 amountOut = pancakeV3Router.exactInput(params);
146  
147          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148          return amountOut;
149      }
150  
151      function getEthFromZeta(
152          address destinationAddress,
153          uint256 minAmountOut,
154          uint256 zetaTokenAmount
155:     ) external override returns (uint256) {

/// @audit Missing '@return  '
174          WETH9(WETH9Address).withdraw(amountOut);
175  
176          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
177  
178          (bool sent, ) = destinationAddress.call{value: amountOut}("");
179          if (!sent) revert ErrorSendingETH();
180  
181          return amountOut;
182      }
183  
184      function getTokenFromZeta(
185          address destinationAddress,
186          uint256 minAmountOut,
187          address outputToken,
188          uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {

/// @audit Missing '@return  '
199              amountIn: zetaTokenAmount,
200              amountOutMinimum: minAmountOut
201          });
202  
203          uint256 amountOut = pancakeV3Router.exactInput(params);
204  
205          emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
206          return amountOut;
207      }
208  
209:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [93](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L93-L106), [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L116-L131), [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L141-L155), [174](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L174-L189), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L199-L209)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit Missing '@return  '
58   
59       modifier nonReentrant() {
60           if (_locked) revert ReentrancyError();
61           _locked = true;
62           _;
63           _locked = false;
64       }
65   
66       receive() external payable {}
67   
68:      function getPair(address token0, address token1) internal pure returns (address, address) {

/// @audit Missing '@return  '
64       }
65   
66       receive() external payable {}
67   
68       function getPair(address token0, address token1) internal pure returns (address, address) {
69           if (token0 < token1) return (token0, token1);
70   
71           return (token1, token0);
72       }
73   
74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

/// @audit Missing '@return  '
89               to: destinationAddress,
90               unwrap: false
91           });
92   
93           uint256 amountOut = tridentRouter.exactInputSingle{value: msg.value}(params);
94   
95           emit EthExchangedForZeta(msg.value, amountOut);
96           return amountOut;
97       }
98   
99       function getZetaFromToken(
100          address destinationAddress,
101          uint256 minAmountOut,
102          address inputToken,
103          uint256 inputTokenAmount
104:     ) external override returns (uint256) {

/// @audit Missing '@return  '
126              to: destinationAddress,
127              unwrap: false
128          });
129  
130          uint256 amountOut = tridentRouter.exactInput(params);
131  
132          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133          return amountOut;
134      }
135  
136      function getEthFromZeta(
137          address destinationAddress,
138          uint256 minAmountOut,
139          uint256 zetaTokenAmount
140:     ) external override returns (uint256) {

/// @audit Missing '@return  '
156              unwrap: true
157          });
158  
159          uint256 amountOut = tridentRouter.exactInputSingle(params);
160  
161          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162  
163          return amountOut;
164      }
165  
166      function getTokenFromZeta(
167          address destinationAddress,
168          uint256 minAmountOut,
169          address outputToken,
170          uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {

/// @audit Missing '@return  '
193              to: destinationAddress,
194              unwrap: false
195          });
196  
197          uint256 amountOut = tridentRouter.exactInput(params);
198  
199          emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
200          return amountOut;
201      }
202  
203:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L58-L68), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L64-L77), [89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L89-L104), [126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L126-L140), [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L156-L171), [193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L193-L203)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

/// @audit Missing '@return  '
24       IUniswapV2Router02 internal immutable uniswapV2Router;
25   
26       constructor(address zetaToken_, address uniswapV2Router_) {
27           if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
28   
29           zetaToken = zetaToken_;
30           uniswapV2Router = IUniswapV2Router02(uniswapV2Router_);
31           wETH = IUniswapV2Router02(uniswapV2Router_).WETH();
32       }
33   
34       function getZetaFromEth(
35           address destinationAddress,
36           uint256 minAmountOut
37:      ) external payable override returns (uint256) {

/// @audit Missing '@return  '
48               destinationAddress,
49               block.timestamp + MAX_DEADLINE
50           );
51   
52           uint256 amountOut = amounts[path.length - 1];
53   
54           emit EthExchangedForZeta(msg.value, amountOut);
55           return amountOut;
56       }
57   
58       function getZetaFromToken(
59           address destinationAddress,
60           uint256 minAmountOut,
61           address inputToken,
62           uint256 inputTokenAmount
63:      ) external override returns (uint256) {

/// @audit Missing '@return  '
85               path,
86               destinationAddress,
87               block.timestamp + MAX_DEADLINE
88           );
89           uint256 amountOut = amounts[path.length - 1];
90   
91           emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92           return amountOut;
93       }
94   
95       function getEthFromZeta(
96           address destinationAddress,
97           uint256 minAmountOut,
98           uint256 zetaTokenAmount
99:      ) external override returns (uint256) {

/// @audit Missing '@return  '
114              destinationAddress,
115              block.timestamp + MAX_DEADLINE
116          );
117  
118          uint256 amountOut = amounts[path.length - 1];
119  
120          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121          return amountOut;
122      }
123  
124      function getTokenFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          address outputToken,
128          uint256 zetaTokenAmount
129:     ) external override returns (uint256) {

/// @audit Missing '@return  '
152              destinationAddress,
153              block.timestamp + MAX_DEADLINE
154          );
155  
156          uint256 amountOut = amounts[path.length - 1];
157  
158          emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
159          return amountOut;
160      }
161  
162:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24-L37), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L48-L63), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L85-L99), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L114-L129), [152](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L152-L162)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

/// @audit Missing '@return  '
64   
65       modifier nonReentrant() {
66           if (_locked) revert ReentrancyError();
67           _locked = true;
68           _;
69           _locked = false;
70       }
71   
72       receive() external payable {}
73   
74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

/// @audit Missing '@return  '
88               amountOutMinimum: minAmountOut,
89               sqrtPriceLimitX96: 0
90           });
91   
92           uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);
93   
94           emit EthExchangedForZeta(msg.value, amountOut);
95           return amountOut;
96       }
97   
98       function getZetaFromToken(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address inputToken,
102          uint256 inputTokenAmount
103:     ) external override returns (uint256) {

/// @audit Missing '@return  '
114              amountIn: inputTokenAmount,
115              amountOutMinimum: minAmountOut
116          });
117  
118          uint256 amountOut = uniswapV3Router.exactInput(params);
119  
120          emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121          return amountOut;
122      }
123  
124      function getEthFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          uint256 zetaTokenAmount
128:     ) external override returns (uint256) {

/// @audit Missing '@return  '
148          WETH9(WETH9Address).withdraw(amountOut);
149  
150          emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151  
152          (bool sent, ) = destinationAddress.call{value: amountOut}("");
153          if (!sent) revert ErrorSendingETH();
154  
155          return amountOut;
156      }
157  
158      function getTokenFromZeta(
159          address destinationAddress,
160          uint256 minAmountOut,
161          address outputToken,
162          uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {

/// @audit Missing '@return  '
174              amountIn: zetaTokenAmount,
175              amountOutMinimum: minAmountOut
176          });
177  
178          uint256 amountOut = uniswapV3Router.exactInput(params);
179  
180          emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
181          return amountOut;
182      }
183  
184:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L64-L77), [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L88-L103), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L114-L128), [148](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L148-L163), [174](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L174-L184)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

/// @audit Missing '@return pairPools'
7     * #    # #    # # #  # #      #####  #    #    #    # #    # #    #   #   #    # #      #    # #
8     * #####  ###### #  # # #  ### #      ######    #####  #####  #    #   #   #    # #      #    # #
9     * #      #    # #   ## #    # #      #    #    #      #   #  #    #   #   #    # #    # #    # #
10    * #      #    # #    #  ####  ###### #    #    #      #    #  ####    #    ####   ####   ####  ######
11    *
12    */
13   
14   pragma solidity >=0.8.0;
15   
16   interface ConcentratedLiquidityPoolFactory {
17       function getPools(
18           address token0,
19           address token1,
20           uint256 startIndex,
21           uint256 count
22:      ) external view returns (address[] memory pairPools);

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L7-L22)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

/// @audit Missing '@return amountOut'
45           address tokenIn; /// @dev the token address to swap-in. If tokenIn is address(0), msg.value will be wrapped and used as input token
46           uint256 amountOut; /// @dev The amount of output tokens to receive
47           uint256 amountInMaximum; /// @dev  maximum available amount of input token after swap
48           address[] path; /// @dev An array of pool addresses to pass through
49           address to; /// @dev recipient of the output tokens
50           bool unwrap; /// @dev unwrap if output token is wrapped klay
51       }
52   
53       /// @notice Swap amountIn of one token for as much as possible of another token
54       /// @param params The parameters necessary for the swap, encoded as ExactInputSingleParams in calldata
55:      function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);

/// @audit Missing '@return amountOut'
49           address to; /// @dev recipient of the output tokens
50           bool unwrap; /// @dev unwrap if output token is wrapped klay
51       }
52   
53       /// @notice Swap amountIn of one token for as much as possible of another token
54       /// @param params The parameters necessary for the swap, encoded as ExactInputSingleParams in calldata
55       function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
56   
57       /// @notice Swap amountIn of one token for as much as possible of another along the specified path
58       /// @param params The parameters necessary for the multi-hop swap, encoded as ExactInputParams in calldata
59:      function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);

/// @audit Missing '@return amountIn'
53       /// @notice Swap amountIn of one token for as much as possible of another token
54       /// @param params The parameters necessary for the swap, encoded as ExactInputSingleParams in calldata
55       function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
56   
57       /// @notice Swap amountIn of one token for as much as possible of another along the specified path
58       /// @param params The parameters necessary for the multi-hop swap, encoded as ExactInputParams in calldata
59       function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);
60   
61       /// @notice Swaps as little as possible of one token for `amountOut` of another token
62       /// @param params The parameters necessary for the swap, encoded as ExactOutputSingleParams in calldata
63:      function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn);

/// @audit Missing '@return amountIn'
57       /// @notice Swap amountIn of one token for as much as possible of another along the specified path
58       /// @param params The parameters necessary for the multi-hop swap, encoded as ExactInputParams in calldata
59       function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);
60   
61       /// @notice Swaps as little as possible of one token for `amountOut` of another token
62       /// @param params The parameters necessary for the swap, encoded as ExactOutputSingleParams in calldata
63       function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn);
64   
65       /// @notice Swaps as little as possible of one token for `amountOut` of another along the specified path (reversed)
66       /// @param params The parameters necessary for the multi-hop swap, encoded as ExactOutputParams in calldata
67:      function exactOutput(ExactOutputParams calldata params) external payable returns (uint256 amountIn);

```
*GitHub*: [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L45-L55), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L49-L59), [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L53-L63), [57](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L57-L67)

```solidity
File: contracts/zevm/Interfaces.sol

/// @audit Missing '@return  '
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    /**
5     * @dev Interfaces of SystemContract and ZRC20 to make easier to import.
6     */
7    interface ISystem {
8:       function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

/// @audit Missing '@return  '
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    /**
5     * @dev Interfaces of SystemContract and ZRC20 to make easier to import.
6     */
7    interface ISystem {
8        function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
9    
10:      function wZetaContractAddress() external view returns (address);

/// @audit Missing '@return  '
2    pragma solidity 0.8.7;
3    
4    /**
5     * @dev Interfaces of SystemContract and ZRC20 to make easier to import.
6     */
7    interface ISystem {
8        function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
9    
10       function wZetaContractAddress() external view returns (address);
11   
12:      function uniswapv2FactoryAddress() external view returns (address);

/// @audit Missing '@return  '
4    /**
5     * @dev Interfaces of SystemContract and ZRC20 to make easier to import.
6     */
7    interface ISystem {
8        function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
9    
10       function wZetaContractAddress() external view returns (address);
11   
12       function uniswapv2FactoryAddress() external view returns (address);
13   
14:      function gasPriceByChainId(uint256 chainID) external view returns (uint256);

/// @audit Missing '@return  '
6     */
7    interface ISystem {
8        function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
9    
10       function wZetaContractAddress() external view returns (address);
11   
12       function uniswapv2FactoryAddress() external view returns (address);
13   
14       function gasPriceByChainId(uint256 chainID) external view returns (uint256);
15   
16:      function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

/// @audit Missing '@return  '
8        function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
9    
10       function wZetaContractAddress() external view returns (address);
11   
12       function uniswapv2FactoryAddress() external view returns (address);
13   
14       function gasPriceByChainId(uint256 chainID) external view returns (uint256);
15   
16       function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);
17   
18:      function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

/// @audit Missing '@return  '
12       function uniswapv2FactoryAddress() external view returns (address);
13   
14       function gasPriceByChainId(uint256 chainID) external view returns (uint256);
15   
16       function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);
17   
18       function gasZetaPoolByChainId(uint256 chainID) external view returns (address);
19   }
20   
21   interface IZRC20 {
22:      function totalSupply() external view returns (uint256);

/// @audit Missing '@return  '
14       function gasPriceByChainId(uint256 chainID) external view returns (uint256);
15   
16       function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);
17   
18       function gasZetaPoolByChainId(uint256 chainID) external view returns (address);
19   }
20   
21   interface IZRC20 {
22       function totalSupply() external view returns (uint256);
23   
24:      function balanceOf(address account) external view returns (uint256);

/// @audit Missing '@return  '
16       function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);
17   
18       function gasZetaPoolByChainId(uint256 chainID) external view returns (address);
19   }
20   
21   interface IZRC20 {
22       function totalSupply() external view returns (uint256);
23   
24       function balanceOf(address account) external view returns (uint256);
25   
26:      function transfer(address recipient, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
18       function gasZetaPoolByChainId(uint256 chainID) external view returns (address);
19   }
20   
21   interface IZRC20 {
22       function totalSupply() external view returns (uint256);
23   
24       function balanceOf(address account) external view returns (uint256);
25   
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28:      function allowance(address owner, address spender) external view returns (uint256);

/// @audit Missing '@return  '
20   
21   interface IZRC20 {
22       function totalSupply() external view returns (uint256);
23   
24       function balanceOf(address account) external view returns (uint256);
25   
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28       function allowance(address owner, address spender) external view returns (uint256);
29   
30:      function approve(address spender, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
22       function totalSupply() external view returns (uint256);
23   
24       function balanceOf(address account) external view returns (uint256);
25   
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28       function allowance(address owner, address spender) external view returns (uint256);
29   
30       function approve(address spender, uint256 amount) external returns (bool);
31   
32:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
24       function balanceOf(address account) external view returns (uint256);
25   
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28       function allowance(address owner, address spender) external view returns (uint256);
29   
30       function approve(address spender, uint256 amount) external returns (bool);
31   
32       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
33   
34:      function deposit(address to, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
26       function transfer(address recipient, uint256 amount) external returns (bool);
27   
28       function allowance(address owner, address spender) external view returns (uint256);
29   
30       function approve(address spender, uint256 amount) external returns (bool);
31   
32       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
33   
34       function deposit(address to, uint256 amount) external returns (bool);
35   
36:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
28       function allowance(address owner, address spender) external view returns (uint256);
29   
30       function approve(address spender, uint256 amount) external returns (bool);
31   
32       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
33   
34       function deposit(address to, uint256 amount) external returns (bool);
35   
36       function withdraw(bytes memory to, uint256 amount) external returns (bool);
37   
38:      function withdrawGasFee() external view returns (address, uint256);

/// @audit Missing '@return  '
40       event Transfer(address indexed from, address indexed to, uint256 value);
41       event Approval(address indexed owner, address indexed spender, uint256 value);
42       event Deposit(bytes from, address indexed to, uint256 value);
43       event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);
44       event UpdatedSystemContract(address systemContract);
45       event UpdatedGasLimit(uint256 gasLimit);
46       event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
47   }
48   
49   interface IZRC20Metadata is IZRC20 {
50:      function name() external view returns (string memory);

/// @audit Missing '@return  '
42       event Deposit(bytes from, address indexed to, uint256 value);
43       event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);
44       event UpdatedSystemContract(address systemContract);
45       event UpdatedGasLimit(uint256 gasLimit);
46       event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
47   }
48   
49   interface IZRC20Metadata is IZRC20 {
50       function name() external view returns (string memory);
51   
52:      function symbol() external view returns (string memory);

/// @audit Missing '@return  '
44       event UpdatedSystemContract(address systemContract);
45       event UpdatedGasLimit(uint256 gasLimit);
46       event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
47   }
48   
49   interface IZRC20Metadata is IZRC20 {
50       function name() external view returns (string memory);
51   
52       function symbol() external view returns (string memory);
53   
54:      function decimals() external view returns (uint8);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L1-L8), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L1-L10), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L2-L12), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L4-L14), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L6-L16), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8-L18), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12-L22), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14-L24), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16-L26), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18-L28), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L20-L30), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22-L32), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24-L34), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26-L36), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28-L38), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40-L50), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42-L52), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44-L54)

```solidity
File: contracts/zevm/ZRC20.sol

/// @audit Missing '@return  '
31       /// @notice Protocol flat fee.
32       uint256 public PROTOCOL_FLAT_FEE;
33   
34       mapping(address => uint256) private _balances;
35       mapping(address => mapping(address => uint256)) private _allowances;
36       uint256 private _totalSupply;
37       string private _name;
38       string private _symbol;
39       uint8 private _decimals;
40   
41:      function _msgSender() internal view virtual returns (address) {

/// @audit Missing '@return  '
35       mapping(address => mapping(address => uint256)) private _allowances;
36       uint256 private _totalSupply;
37       string private _name;
38       string private _symbol;
39       uint8 private _decimals;
40   
41       function _msgSender() internal view virtual returns (address) {
42           return msg.sender;
43       }
44   
45:      function _msgData() internal view virtual returns (bytes calldata) {

```
*GitHub*: [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L31-L41), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35-L45)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

/// @audit Missing '@return  '
40           uint256 sourceChainId;
41           bytes destinationAddress;
42           uint256 destinationChainId;
43           /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
44           uint256 remainingZetaValue;
45           bytes message;
46       }
47   }
48   
49   interface WZETA {
50:      function transferFrom(address src, address dst, uint wad) external returns (bool);

```
*GitHub*: [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L40-L50)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

/// @audit Missing '@return  '
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IUniswapV2Router01 {
5:       function factory() external pure returns (address);

/// @audit Missing '@return  '
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IUniswapV2Router01 {
5        function factory() external pure returns (address);
6    
7:       function WETH() external pure returns (address);

/// @audit Missing '@return amountA'
/// @audit Missing '@return amountB'
/// @audit Missing '@return liquidity'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IUniswapV2Router01 {
5        function factory() external pure returns (address);
6    
7        function WETH() external pure returns (address);
8    
9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17           uint deadline
18:      ) external returns (uint amountA, uint amountB, uint liquidity);

/// @audit Missing '@return amountToken'
/// @audit Missing '@return amountETH'
/// @audit Missing '@return liquidity'
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17           uint deadline
18       ) external returns (uint amountA, uint amountB, uint liquidity);
19   
20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26           uint deadline
27:      ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

/// @audit Missing '@return amountB'
/// @audit Missing '@return amountA'
19   
20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26           uint deadline
27       ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
28   
29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36           uint deadline
37:      ) external returns (uint amountA, uint amountB);

/// @audit Missing '@return amountETH'
/// @audit Missing '@return amountToken'
29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36           uint deadline
37       ) external returns (uint amountA, uint amountB);
38   
39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45           uint deadline
46:      ) external returns (uint amountToken, uint amountETH);

/// @audit Missing '@return amountB'
/// @audit Missing '@return amountA'
38   
39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45           uint deadline
46       ) external returns (uint amountToken, uint amountETH);
47   
48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60:      ) external returns (uint amountA, uint amountB);

/// @audit Missing '@return amountToken'
/// @audit Missing '@return amountETH'
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60       ) external returns (uint amountA, uint amountB);
61   
62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73:      ) external returns (uint amountToken, uint amountETH);

/// @audit Missing '@return amounts'
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73       ) external returns (uint amountToken, uint amountETH);
74   
75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80           uint deadline
81:      ) external returns (uint[] memory amounts);

/// @audit Missing '@return amounts'
73       ) external returns (uint amountToken, uint amountETH);
74   
75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80           uint deadline
81       ) external returns (uint[] memory amounts);
82   
83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88           uint deadline
89:      ) external returns (uint[] memory amounts);

/// @audit Missing '@return amounts'
81       ) external returns (uint[] memory amounts);
82   
83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88           uint deadline
89       ) external returns (uint[] memory amounts);
90   
91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95           uint deadline
96:      ) external payable returns (uint[] memory amounts);

/// @audit Missing '@return amounts'
88           uint deadline
89       ) external returns (uint[] memory amounts);
90   
91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95           uint deadline
96       ) external payable returns (uint[] memory amounts);
97   
98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103          uint deadline
104:     ) external returns (uint[] memory amounts);

/// @audit Missing '@return amounts'
96       ) external payable returns (uint[] memory amounts);
97   
98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103          uint deadline
104      ) external returns (uint[] memory amounts);
105  
106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111          uint deadline
112:     ) external returns (uint[] memory amounts);

/// @audit Missing '@return amounts'
104      ) external returns (uint[] memory amounts);
105  
106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111          uint deadline
112      ) external returns (uint[] memory amounts);
113  
114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119:     ) external payable returns (uint[] memory amounts);

/// @audit Missing '@return amountB'
111          uint deadline
112      ) external returns (uint[] memory amounts);
113  
114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119      ) external payable returns (uint[] memory amounts);
120  
121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

/// @audit Missing '@return amountOut'
113  
114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119      ) external payable returns (uint[] memory amounts);
120  
121      function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);
122  
123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

/// @audit Missing '@return amountIn'
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119      ) external payable returns (uint[] memory amounts);
120  
121      function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);
122  
123      function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);
124  
125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

/// @audit Missing '@return amounts'
117          address to,
118          uint deadline
119      ) external payable returns (uint[] memory amounts);
120  
121      function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);
122  
123      function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);
124  
125      function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);
126  
127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

/// @audit Missing '@return amounts'
119      ) external payable returns (uint[] memory amounts);
120  
121      function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);
122  
123      function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);
124  
125      function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);
126  
127      function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
128  
129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L1-L5), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L1-L7), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L1-L18), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L1-L18), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L1-L18), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L10-L27), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L10-L27), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L10-L27), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L19-L37), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L19-L37), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L46), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L46), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L38-L60), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L38-L60), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L52-L73), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L52-L73), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L65-L81), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L73-L89), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L81-L96), [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L88-L104), [96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L96-L112), [104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L104-L119), [111](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L111-L121), [113](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L113-L123), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L115-L125), [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L117-L127), [119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L119-L129)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

/// @audit Missing '@return amountETH'
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    import "./IUniswapV2Router01.sol";
5    
6    interface IUniswapV2Router02 is IUniswapV2Router01 {
7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13           uint deadline
14:      ) external returns (uint amountETH);

/// @audit Missing '@return amountETH'
6    interface IUniswapV2Router02 is IUniswapV2Router01 {
7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13           uint deadline
14       ) external returns (uint amountETH);
15   
16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21           address to,
22           uint deadline,
23           bool approveMax,
24           uint8 v,
25           bytes32 r,
26           bytes32 s
27:      ) external returns (uint amountETH);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L1-L14), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6-L27)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

/// @audit Missing '@return  '
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IWETH9 {
5        event Approval(address indexed owner, address indexed spender, uint value);
6        event Transfer(address indexed from, address indexed to, uint value);
7        event Deposit(address indexed dst, uint wad);
8        event Withdrawal(address indexed src, uint wad);
9    
10:      function totalSupply() external view returns (uint);

/// @audit Missing '@return  '
2    pragma solidity 0.8.7;
3    
4    interface IWETH9 {
5        event Approval(address indexed owner, address indexed spender, uint value);
6        event Transfer(address indexed from, address indexed to, uint value);
7        event Deposit(address indexed dst, uint wad);
8        event Withdrawal(address indexed src, uint wad);
9    
10       function totalSupply() external view returns (uint);
11   
12:      function balanceOf(address owner) external view returns (uint);

/// @audit Missing '@return  '
4    interface IWETH9 {
5        event Approval(address indexed owner, address indexed spender, uint value);
6        event Transfer(address indexed from, address indexed to, uint value);
7        event Deposit(address indexed dst, uint wad);
8        event Withdrawal(address indexed src, uint wad);
9    
10       function totalSupply() external view returns (uint);
11   
12       function balanceOf(address owner) external view returns (uint);
13   
14:      function allowance(address owner, address spender) external view returns (uint);

/// @audit Missing '@return  '
6        event Transfer(address indexed from, address indexed to, uint value);
7        event Deposit(address indexed dst, uint wad);
8        event Withdrawal(address indexed src, uint wad);
9    
10       function totalSupply() external view returns (uint);
11   
12       function balanceOf(address owner) external view returns (uint);
13   
14       function allowance(address owner, address spender) external view returns (uint);
15   
16:      function approve(address spender, uint wad) external returns (bool);

/// @audit Missing '@return  '
8        event Withdrawal(address indexed src, uint wad);
9    
10       function totalSupply() external view returns (uint);
11   
12       function balanceOf(address owner) external view returns (uint);
13   
14       function allowance(address owner, address spender) external view returns (uint);
15   
16       function approve(address spender, uint wad) external returns (bool);
17   
18:      function transfer(address to, uint wad) external returns (bool);

/// @audit Missing '@return  '
10       function totalSupply() external view returns (uint);
11   
12       function balanceOf(address owner) external view returns (uint);
13   
14       function allowance(address owner, address spender) external view returns (uint);
15   
16       function approve(address spender, uint wad) external returns (bool);
17   
18       function transfer(address to, uint wad) external returns (bool);
19   
20:      function transferFrom(address from, address to, uint wad) external returns (bool);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1-L10), [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L2-L12), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4-L14), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L16), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8-L18), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10-L20)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

/// @audit Missing '@return  '
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IZRC20 {
5:       function totalSupply() external view returns (uint256);

/// @audit Missing '@return  '
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IZRC20 {
5        function totalSupply() external view returns (uint256);
6    
7:       function balanceOf(address account) external view returns (uint256);

/// @audit Missing '@return  '
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IZRC20 {
5        function totalSupply() external view returns (uint256);
6    
7        function balanceOf(address account) external view returns (uint256);
8    
9:       function transfer(address recipient, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
1    // SPDX-License-Identifier: MIT
2    pragma solidity 0.8.7;
3    
4    interface IZRC20 {
5        function totalSupply() external view returns (uint256);
6    
7        function balanceOf(address account) external view returns (uint256);
8    
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11:      function allowance(address owner, address spender) external view returns (uint256);

/// @audit Missing '@return  '
3    
4    interface IZRC20 {
5        function totalSupply() external view returns (uint256);
6    
7        function balanceOf(address account) external view returns (uint256);
8    
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13:      function approve(address spender, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
5        function totalSupply() external view returns (uint256);
6    
7        function balanceOf(address account) external view returns (uint256);
8    
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15:      function decreaseAllowance(address spender, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
7        function balanceOf(address account) external view returns (uint256);
8    
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17:      function increaseAllowance(address spender, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
9        function transfer(address recipient, uint256 amount) external returns (bool);
10   
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17       function increaseAllowance(address spender, uint256 amount) external returns (bool);
18   
19:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
11       function allowance(address owner, address spender) external view returns (uint256);
12   
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17       function increaseAllowance(address spender, uint256 amount) external returns (bool);
18   
19       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
20   
21:      function deposit(address to, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
13       function approve(address spender, uint256 amount) external returns (bool);
14   
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17       function increaseAllowance(address spender, uint256 amount) external returns (bool);
18   
19       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
20   
21       function deposit(address to, uint256 amount) external returns (bool);
22   
23:      function burn(address account, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
15       function decreaseAllowance(address spender, uint256 amount) external returns (bool);
16   
17       function increaseAllowance(address spender, uint256 amount) external returns (bool);
18   
19       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
20   
21       function deposit(address to, uint256 amount) external returns (bool);
22   
23       function burn(address account, uint256 amount) external returns (bool);
24   
25:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

/// @audit Missing '@return  '
17       function increaseAllowance(address spender, uint256 amount) external returns (bool);
18   
19       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
20   
21       function deposit(address to, uint256 amount) external returns (bool);
22   
23       function burn(address account, uint256 amount) external returns (bool);
24   
25       function withdraw(bytes memory to, uint256 amount) external returns (bool);
26   
27:      function withdrawGasFee() external view returns (address, uint256);

/// @audit Missing '@return  '
19       function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
20   
21       function deposit(address to, uint256 amount) external returns (bool);
22   
23       function burn(address account, uint256 amount) external returns (bool);
24   
25       function withdraw(bytes memory to, uint256 amount) external returns (bool);
26   
27       function withdrawGasFee() external view returns (address, uint256);
28   
29:      function PROTOCOL_FEE() external view returns (uint256);

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L1-L5), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L1-L7), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L1-L9), [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L1-L11), [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L3-L13), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5-L15), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7-L17), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9-L19), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11-L21), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13-L23), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15-L25), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17-L27), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19-L29)

</details>





### [N&#x2011;50] NatSpec: Function declarations should have `@dev` tags
`@dev` is used to explain to developers what the potential integration issues/foot-guns are

*There are 127 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

68:      constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

```
*GitHub*: [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L68)

```solidity
File: contracts/evm/Zeta.eth.sol

10:      constructor(address creator, uint256 initialSupply) {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L10)

```solidity
File: contracts/evm/Zeta.non-eth.sol

33:      constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

40:      function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

62:      function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

73:      function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {

```
*GitHub*: [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L33), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40-L40), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73-L73)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

16       constructor(
17           address zetaToken_,
18           address tssAddress_,
19           address tssAddressUpdater_,
20           address pauserAddress_
21:      ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

23:      function getLockedAmount() external view returns (uint256) {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23-L23)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

20       constructor(
21           address zetaTokenAddress_,
22           address tssAddress_,
23           address tssAddressUpdater_,
24           address pauserAddress_
25:      ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

27:      function getLockedAmount() external view returns (uint256) {

31:      function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {

```
*GitHub*: [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27-L27), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31-L31)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

83:      function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89           uint256 inputTokenAmount
90:      ) external returns (uint256);

92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96:      ) external returns (uint256);

98       function getTokenFromZeta(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address outputToken,
102          uint256 zetaTokenAmount
103:     ) external returns (uint256);

105:     function hasZetaLiquidity() external view returns (bool);

```
*GitHub*: [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83-L83), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85-L90), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92-L96), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98-L103), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L105-L105)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

10:      function burnFrom(address account, uint256 amount) external;

12:      function mint(address mintee, uint256 value, bytes32 internalSendHash) external;

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12-L12)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

54:      function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {

```
*GitHub*: [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

21:      function withdraw(uint256 wad) external;

38:      function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);

50:      function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);

71       constructor(
72           address zetaToken_,
73           address pancakeV3Router_,
74           address uniswapV3Factory_,
75           address WETH9Address_,
76           uint24 zetaPoolFee_,
77           uint24 tokenPoolFee_
78:      ) {

101:     receive() external payable {}

103      function getZetaFromEth(
104          address destinationAddress,
105          uint256 minAmountOut
106:     ) external payable override returns (uint256) {

126      function getZetaFromToken(
127          address destinationAddress,
128          uint256 minAmountOut,
129          address inputToken,
130          uint256 inputTokenAmount
131:     ) external override returns (uint256) {

151      function getEthFromZeta(
152          address destinationAddress,
153          uint256 minAmountOut,
154          uint256 zetaTokenAmount
155:     ) external override returns (uint256) {

184      function getTokenFromZeta(
185          address destinationAddress,
186          uint256 minAmountOut,
187          address outputToken,
188          uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {

209:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L21-L21), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L38-L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L50-L50), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L78), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101-L101), [103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L106), [126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L131), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L155), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L189), [209](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209-L209)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

21:      function deposit() external payable;

23:      function withdraw(uint256 wad) external;

25:      function depositTo(address to) external payable;

27:      function withdrawTo(address payable to, uint256 value) external;

45:      constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

66:      receive() external payable {}

74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

99       function getZetaFromToken(
100          address destinationAddress,
101          uint256 minAmountOut,
102          address inputToken,
103          uint256 inputTokenAmount
104:     ) external override returns (uint256) {

136      function getEthFromZeta(
137          address destinationAddress,
138          uint256 minAmountOut,
139          uint256 zetaTokenAmount
140:     ) external override returns (uint256) {

166      function getTokenFromZeta(
167          address destinationAddress,
168          uint256 minAmountOut,
169          address outputToken,
170          uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {

203:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L21-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L27-L27), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L45), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66-L66), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L77), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L104), [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L140), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L171), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L203)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

26:      constructor(address zetaToken_, address uniswapV2Router_) {

34       function getZetaFromEth(
35           address destinationAddress,
36           uint256 minAmountOut
37:      ) external payable override returns (uint256) {

58       function getZetaFromToken(
59           address destinationAddress,
60           uint256 minAmountOut,
61           address inputToken,
62           uint256 inputTokenAmount
63:      ) external override returns (uint256) {

95       function getEthFromZeta(
96           address destinationAddress,
97           uint256 minAmountOut,
98           uint256 zetaTokenAmount
99:      ) external override returns (uint256) {

124      function getTokenFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          address outputToken,
128          uint256 zetaTokenAmount
129:     ) external override returns (uint256) {

162:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26-L26), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34-L37), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L63), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L99), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L129), [162](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162-L162)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

21:      function withdraw(uint256 wad) external;

42       constructor(
43           address zetaToken_,
44           address uniswapV3Router_,
45           address uniswapV3Factory_,
46           address WETH9Address_,
47           uint24 zetaPoolFee_,
48           uint24 tokenPoolFee_
49:      ) {

72:      receive() external payable {}

74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

98       function getZetaFromToken(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address inputToken,
102          uint256 inputTokenAmount
103:     ) external override returns (uint256) {

124      function getEthFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          uint256 zetaTokenAmount
128:     ) external override returns (uint256) {

158      function getTokenFromZeta(
159          address destinationAddress,
160          uint256 minAmountOut,
161          address outputToken,
162          uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {

184:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L21-L21), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L49), [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72-L72), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L77), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L103), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L128), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L163), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184-L184)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

17       function getPools(
18           address token0,
19           address token1,
20           uint256 startIndex,
21           uint256 count
22:      ) external view returns (address[] memory pairPools);

```
*GitHub*: [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17-L22)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

55:      function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);

59:      function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);

63:      function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn);

67:      function exactOutput(ExactOutputParams calldata params) external payable returns (uint256 amountIn);

70:      function sweep(address token, uint256 amount, address recipient) external payable;

```
*GitHub*: [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L55-L55), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L59-L59), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L63-L63), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L67-L67), [70](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L70-L70)

```solidity
File: contracts/zevm/Interfaces.sol

8:       function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

10:      function wZetaContractAddress() external view returns (address);

12:      function uniswapv2FactoryAddress() external view returns (address);

14:      function gasPriceByChainId(uint256 chainID) external view returns (uint256);

16:      function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

18:      function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

22:      function totalSupply() external view returns (uint256);

24:      function balanceOf(address account) external view returns (uint256);

26:      function transfer(address recipient, uint256 amount) external returns (bool);

28:      function allowance(address owner, address spender) external view returns (uint256);

30:      function approve(address spender, uint256 amount) external returns (bool);

32:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

34:      function deposit(address to, uint256 amount) external returns (bool);

36:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

38:      function withdrawGasFee() external view returns (address, uint256);

50:      function name() external view returns (string memory);

52:      function symbol() external view returns (string memory);

54:      function decimals() external view returns (uint8);

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8-L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18-L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22-L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24-L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26-L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28-L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30-L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32-L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34-L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36-L36), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L38-L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L50-L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L52-L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L54-L54)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

50:      function transferFrom(address src, address dst, uint wad) external returns (bool);

52:      function withdraw(uint wad) external;

79:      constructor(address wzeta_) {

```
*GitHub*: [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50-L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52-L52), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L79)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

5:       function factory() external pure returns (address);

7:       function WETH() external pure returns (address);

9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17           uint deadline
18:      ) external returns (uint amountA, uint amountB, uint liquidity);

20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26           uint deadline
27:      ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36           uint deadline
37:      ) external returns (uint amountA, uint amountB);

39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45           uint deadline
46:      ) external returns (uint amountToken, uint amountETH);

48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60:      ) external returns (uint amountA, uint amountB);

62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73:      ) external returns (uint amountToken, uint amountETH);

75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80           uint deadline
81:      ) external returns (uint[] memory amounts);

83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88           uint deadline
89:      ) external returns (uint[] memory amounts);

91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95           uint deadline
96:      ) external payable returns (uint[] memory amounts);

98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103          uint deadline
104:     ) external returns (uint[] memory amounts);

106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111          uint deadline
112:     ) external returns (uint[] memory amounts);

114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119:     ) external payable returns (uint[] memory amounts);

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5-L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7-L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L37), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L46), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L81), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L89), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91-L96), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L104), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L112), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114-L119), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121-L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123-L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125-L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127-L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129-L129)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13           uint deadline
14:      ) external returns (uint amountETH);

16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21           address to,
22           uint deadline,
23           bool approveMax,
24           uint8 v,
25           bytes32 r,
26           bytes32 s
27:      ) external returns (uint amountETH);

29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30           uint amountIn,
31           uint amountOutMin,
32           address[] calldata path,
33           address to,
34           uint deadline
35:      ) external;

37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38           uint amountOutMin,
39           address[] calldata path,
40           address to,
41           uint deadline
42:      ) external payable;

44       function swapExactTokensForETHSupportingFeeOnTransferTokens(
45           uint amountIn,
46           uint amountOutMin,
47           address[] calldata path,
48           address to,
49           uint deadline
50:      ) external;

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29-L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37-L42), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44-L50)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

10:      function totalSupply() external view returns (uint);

12:      function balanceOf(address owner) external view returns (uint);

14:      function allowance(address owner, address spender) external view returns (uint);

16:      function approve(address spender, uint wad) external returns (bool);

18:      function transfer(address to, uint wad) external returns (bool);

20:      function transferFrom(address from, address to, uint wad) external returns (bool);

22:      function deposit() external payable;

24:      function withdraw(uint wad) external;

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18-L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20-L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L22-L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24-L24)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

5:       function totalSupply() external view returns (uint256);

7:       function balanceOf(address account) external view returns (uint256);

9:       function transfer(address recipient, uint256 amount) external returns (bool);

11:      function allowance(address owner, address spender) external view returns (uint256);

13:      function approve(address spender, uint256 amount) external returns (bool);

15:      function decreaseAllowance(address spender, uint256 amount) external returns (bool);

17:      function increaseAllowance(address spender, uint256 amount) external returns (bool);

19:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

21:      function deposit(address to, uint256 amount) external returns (bool);

23:      function burn(address account, uint256 amount) external returns (bool);

25:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

27:      function withdrawGasFee() external view returns (address, uint256);

29:      function PROTOCOL_FEE() external view returns (uint256);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5-L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7-L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9-L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11-L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17-L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19-L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29-L29)

```solidity
File: contracts/zevm/interfaces/zContract.sol

11       function onCrossChainCall(
12           zContext calldata context,
13           address zrc20,
14           uint256 amount,
15           bytes calldata message
16:      ) external;

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11-L16)

</details>





### [N&#x2011;51] NatSpec: Function declarations should have `@notice` tags
`@notice` is used to explain to end users what the function does, and the compiler interprets `///` or `/**` comments (but not `//` or `/*`) as this tag if one wasn't explicitly provided

*There are 120 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

68:      constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

```
*GitHub*: [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L68)

```solidity
File: contracts/evm/Zeta.eth.sol

10:      constructor(address creator, uint256 initialSupply) {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L10)

```solidity
File: contracts/evm/Zeta.non-eth.sol

33:      constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

40:      function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

62:      function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

73:      function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {

```
*GitHub*: [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L33), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40-L40), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73-L73)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

16       constructor(
17           address zetaToken_,
18           address tssAddress_,
19           address tssAddressUpdater_,
20           address pauserAddress_
21:      ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

23:      function getLockedAmount() external view returns (uint256) {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23-L23)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

20       constructor(
21           address zetaTokenAddress_,
22           address tssAddress_,
23           address tssAddressUpdater_,
24           address pauserAddress_
25:      ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

27:      function getLockedAmount() external view returns (uint256) {

31:      function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {

```
*GitHub*: [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27-L27), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31-L31)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

83:      function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89           uint256 inputTokenAmount
90:      ) external returns (uint256);

92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96:      ) external returns (uint256);

98       function getTokenFromZeta(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address outputToken,
102          uint256 zetaTokenAmount
103:     ) external returns (uint256);

105:     function hasZetaLiquidity() external view returns (bool);

```
*GitHub*: [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83-L83), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85-L90), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92-L96), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98-L103), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L105-L105)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

10:      function burnFrom(address account, uint256 amount) external;

12:      function mint(address mintee, uint256 value, bytes32 internalSendHash) external;

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12-L12)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

54:      function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {

```
*GitHub*: [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

21:      function withdraw(uint256 wad) external;

71       constructor(
72           address zetaToken_,
73           address pancakeV3Router_,
74           address uniswapV3Factory_,
75           address WETH9Address_,
76           uint24 zetaPoolFee_,
77           uint24 tokenPoolFee_
78:      ) {

101:     receive() external payable {}

103      function getZetaFromEth(
104          address destinationAddress,
105          uint256 minAmountOut
106:     ) external payable override returns (uint256) {

126      function getZetaFromToken(
127          address destinationAddress,
128          uint256 minAmountOut,
129          address inputToken,
130          uint256 inputTokenAmount
131:     ) external override returns (uint256) {

151      function getEthFromZeta(
152          address destinationAddress,
153          uint256 minAmountOut,
154          uint256 zetaTokenAmount
155:     ) external override returns (uint256) {

184      function getTokenFromZeta(
185          address destinationAddress,
186          uint256 minAmountOut,
187          address outputToken,
188          uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {

209:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L21-L21), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L78), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101-L101), [103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L106), [126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L131), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L155), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L189), [209](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209-L209)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

21:      function deposit() external payable;

23:      function withdraw(uint256 wad) external;

25:      function depositTo(address to) external payable;

27:      function withdrawTo(address payable to, uint256 value) external;

45:      constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

66:      receive() external payable {}

74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

99       function getZetaFromToken(
100          address destinationAddress,
101          uint256 minAmountOut,
102          address inputToken,
103          uint256 inputTokenAmount
104:     ) external override returns (uint256) {

136      function getEthFromZeta(
137          address destinationAddress,
138          uint256 minAmountOut,
139          uint256 zetaTokenAmount
140:     ) external override returns (uint256) {

166      function getTokenFromZeta(
167          address destinationAddress,
168          uint256 minAmountOut,
169          address outputToken,
170          uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {

203:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L21-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L27-L27), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L45), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66-L66), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L77), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L104), [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L140), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L171), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L203)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

26:      constructor(address zetaToken_, address uniswapV2Router_) {

34       function getZetaFromEth(
35           address destinationAddress,
36           uint256 minAmountOut
37:      ) external payable override returns (uint256) {

58       function getZetaFromToken(
59           address destinationAddress,
60           uint256 minAmountOut,
61           address inputToken,
62           uint256 inputTokenAmount
63:      ) external override returns (uint256) {

95       function getEthFromZeta(
96           address destinationAddress,
97           uint256 minAmountOut,
98           uint256 zetaTokenAmount
99:      ) external override returns (uint256) {

124      function getTokenFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          address outputToken,
128          uint256 zetaTokenAmount
129:     ) external override returns (uint256) {

162:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26-L26), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34-L37), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L63), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L99), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L129), [162](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162-L162)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

21:      function withdraw(uint256 wad) external;

42       constructor(
43           address zetaToken_,
44           address uniswapV3Router_,
45           address uniswapV3Factory_,
46           address WETH9Address_,
47           uint24 zetaPoolFee_,
48           uint24 tokenPoolFee_
49:      ) {

72:      receive() external payable {}

74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

98       function getZetaFromToken(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address inputToken,
102          uint256 inputTokenAmount
103:     ) external override returns (uint256) {

124      function getEthFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          uint256 zetaTokenAmount
128:     ) external override returns (uint256) {

158      function getTokenFromZeta(
159          address destinationAddress,
160          uint256 minAmountOut,
161          address outputToken,
162          uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {

184:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L21-L21), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L49), [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72-L72), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L77), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L103), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L128), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L163), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184-L184)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

17       function getPools(
18           address token0,
19           address token1,
20           uint256 startIndex,
21           uint256 count
22:      ) external view returns (address[] memory pairPools);

```
*GitHub*: [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17-L22)

```solidity
File: contracts/zevm/Interfaces.sol

8:       function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

10:      function wZetaContractAddress() external view returns (address);

12:      function uniswapv2FactoryAddress() external view returns (address);

14:      function gasPriceByChainId(uint256 chainID) external view returns (uint256);

16:      function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

18:      function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

22:      function totalSupply() external view returns (uint256);

24:      function balanceOf(address account) external view returns (uint256);

26:      function transfer(address recipient, uint256 amount) external returns (bool);

28:      function allowance(address owner, address spender) external view returns (uint256);

30:      function approve(address spender, uint256 amount) external returns (bool);

32:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

34:      function deposit(address to, uint256 amount) external returns (bool);

36:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

38:      function withdrawGasFee() external view returns (address, uint256);

50:      function name() external view returns (string memory);

52:      function symbol() external view returns (string memory);

54:      function decimals() external view returns (uint8);

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8-L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18-L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22-L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24-L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26-L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28-L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30-L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32-L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34-L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36-L36), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L38-L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L50-L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L52-L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L54-L54)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

50:      function transferFrom(address src, address dst, uint wad) external returns (bool);

52:      function withdraw(uint wad) external;

79:      constructor(address wzeta_) {

```
*GitHub*: [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50-L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52-L52), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L79)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

5:       function factory() external pure returns (address);

7:       function WETH() external pure returns (address);

9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17           uint deadline
18:      ) external returns (uint amountA, uint amountB, uint liquidity);

20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26           uint deadline
27:      ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36           uint deadline
37:      ) external returns (uint amountA, uint amountB);

39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45           uint deadline
46:      ) external returns (uint amountToken, uint amountETH);

48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60:      ) external returns (uint amountA, uint amountB);

62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73:      ) external returns (uint amountToken, uint amountETH);

75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80           uint deadline
81:      ) external returns (uint[] memory amounts);

83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88           uint deadline
89:      ) external returns (uint[] memory amounts);

91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95           uint deadline
96:      ) external payable returns (uint[] memory amounts);

98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103          uint deadline
104:     ) external returns (uint[] memory amounts);

106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111          uint deadline
112:     ) external returns (uint[] memory amounts);

114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119:     ) external payable returns (uint[] memory amounts);

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5-L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7-L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L37), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L46), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L81), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L89), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91-L96), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L104), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L112), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114-L119), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121-L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123-L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125-L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127-L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129-L129)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13           uint deadline
14:      ) external returns (uint amountETH);

16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21           address to,
22           uint deadline,
23           bool approveMax,
24           uint8 v,
25           bytes32 r,
26           bytes32 s
27:      ) external returns (uint amountETH);

29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30           uint amountIn,
31           uint amountOutMin,
32           address[] calldata path,
33           address to,
34           uint deadline
35:      ) external;

37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38           uint amountOutMin,
39           address[] calldata path,
40           address to,
41           uint deadline
42:      ) external payable;

44       function swapExactTokensForETHSupportingFeeOnTransferTokens(
45           uint amountIn,
46           uint amountOutMin,
47           address[] calldata path,
48           address to,
49           uint deadline
50:      ) external;

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29-L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37-L42), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44-L50)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

10:      function totalSupply() external view returns (uint);

12:      function balanceOf(address owner) external view returns (uint);

14:      function allowance(address owner, address spender) external view returns (uint);

16:      function approve(address spender, uint wad) external returns (bool);

18:      function transfer(address to, uint wad) external returns (bool);

20:      function transferFrom(address from, address to, uint wad) external returns (bool);

22:      function deposit() external payable;

24:      function withdraw(uint wad) external;

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18-L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20-L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L22-L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24-L24)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

5:       function totalSupply() external view returns (uint256);

7:       function balanceOf(address account) external view returns (uint256);

9:       function transfer(address recipient, uint256 amount) external returns (bool);

11:      function allowance(address owner, address spender) external view returns (uint256);

13:      function approve(address spender, uint256 amount) external returns (bool);

15:      function decreaseAllowance(address spender, uint256 amount) external returns (bool);

17:      function increaseAllowance(address spender, uint256 amount) external returns (bool);

19:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

21:      function deposit(address to, uint256 amount) external returns (bool);

23:      function burn(address account, uint256 amount) external returns (bool);

25:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

27:      function withdrawGasFee() external view returns (address, uint256);

29:      function PROTOCOL_FEE() external view returns (uint256);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5-L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7-L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9-L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11-L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17-L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19-L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29-L29)

```solidity
File: contracts/zevm/interfaces/zContract.sol

11       function onCrossChainCall(
12           zContext calldata context,
13           address zrc20,
14           uint256 amount,
15           bytes calldata message
16:      ) external;

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11-L16)

</details>





### [N&#x2011;52] NatSpec: Function declarations should have descriptions


*There are 120 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

68:      constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

```
*GitHub*: [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L68)

```solidity
File: contracts/evm/Zeta.eth.sol

10:      constructor(address creator, uint256 initialSupply) {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L10)

```solidity
File: contracts/evm/Zeta.non-eth.sol

33:      constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

40:      function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

62:      function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

73:      function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {

```
*GitHub*: [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L33), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40-L40), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73-L73)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

16       constructor(
17           address zetaToken_,
18           address tssAddress_,
19           address tssAddressUpdater_,
20           address pauserAddress_
21:      ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

23:      function getLockedAmount() external view returns (uint256) {

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23-L23)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

20       constructor(
21           address zetaTokenAddress_,
22           address tssAddress_,
23           address tssAddressUpdater_,
24           address pauserAddress_
25:      ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

27:      function getLockedAmount() external view returns (uint256) {

31:      function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {

```
*GitHub*: [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27-L27), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31-L31)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

83:      function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

85       function getZetaFromToken(
86           address destinationAddress,
87           uint256 minAmountOut,
88           address inputToken,
89           uint256 inputTokenAmount
90:      ) external returns (uint256);

92       function getEthFromZeta(
93           address destinationAddress,
94           uint256 minAmountOut,
95           uint256 zetaTokenAmount
96:      ) external returns (uint256);

98       function getTokenFromZeta(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address outputToken,
102          uint256 zetaTokenAmount
103:     ) external returns (uint256);

105:     function hasZetaLiquidity() external view returns (bool);

```
*GitHub*: [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83-L83), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85-L90), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92-L96), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98-L103), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L105-L105)

```solidity
File: contracts/evm/interfaces/ZetaNonEthInterface.sol

10:      function burnFrom(address account, uint256 amount) external;

12:      function mint(address mintee, uint256 value, bytes32 internalSendHash) external;

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12-L12)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

54:      function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {

```
*GitHub*: [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

21:      function withdraw(uint256 wad) external;

71       constructor(
72           address zetaToken_,
73           address pancakeV3Router_,
74           address uniswapV3Factory_,
75           address WETH9Address_,
76           uint24 zetaPoolFee_,
77           uint24 tokenPoolFee_
78:      ) {

101:     receive() external payable {}

103      function getZetaFromEth(
104          address destinationAddress,
105          uint256 minAmountOut
106:     ) external payable override returns (uint256) {

126      function getZetaFromToken(
127          address destinationAddress,
128          uint256 minAmountOut,
129          address inputToken,
130          uint256 inputTokenAmount
131:     ) external override returns (uint256) {

151      function getEthFromZeta(
152          address destinationAddress,
153          uint256 minAmountOut,
154          uint256 zetaTokenAmount
155:     ) external override returns (uint256) {

184      function getTokenFromZeta(
185          address destinationAddress,
186          uint256 minAmountOut,
187          address outputToken,
188          uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {

209:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L21-L21), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L78), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101-L101), [103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L106), [126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L131), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L155), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L189), [209](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209-L209)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

21:      function deposit() external payable;

23:      function withdraw(uint256 wad) external;

25:      function depositTo(address to) external payable;

27:      function withdrawTo(address payable to, uint256 value) external;

45:      constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

66:      receive() external payable {}

74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

99       function getZetaFromToken(
100          address destinationAddress,
101          uint256 minAmountOut,
102          address inputToken,
103          uint256 inputTokenAmount
104:     ) external override returns (uint256) {

136      function getEthFromZeta(
137          address destinationAddress,
138          uint256 minAmountOut,
139          uint256 zetaTokenAmount
140:     ) external override returns (uint256) {

166      function getTokenFromZeta(
167          address destinationAddress,
168          uint256 minAmountOut,
169          address outputToken,
170          uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {

203:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L21-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L27-L27), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L45), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66-L66), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L77), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L104), [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L140), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L171), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L203)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

26:      constructor(address zetaToken_, address uniswapV2Router_) {

34       function getZetaFromEth(
35           address destinationAddress,
36           uint256 minAmountOut
37:      ) external payable override returns (uint256) {

58       function getZetaFromToken(
59           address destinationAddress,
60           uint256 minAmountOut,
61           address inputToken,
62           uint256 inputTokenAmount
63:      ) external override returns (uint256) {

95       function getEthFromZeta(
96           address destinationAddress,
97           uint256 minAmountOut,
98           uint256 zetaTokenAmount
99:      ) external override returns (uint256) {

124      function getTokenFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          address outputToken,
128          uint256 zetaTokenAmount
129:     ) external override returns (uint256) {

162:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26-L26), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34-L37), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L63), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L99), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L129), [162](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162-L162)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

21:      function withdraw(uint256 wad) external;

42       constructor(
43           address zetaToken_,
44           address uniswapV3Router_,
45           address uniswapV3Factory_,
46           address WETH9Address_,
47           uint24 zetaPoolFee_,
48           uint24 tokenPoolFee_
49:      ) {

72:      receive() external payable {}

74       function getZetaFromEth(
75           address destinationAddress,
76           uint256 minAmountOut
77:      ) external payable override returns (uint256) {

98       function getZetaFromToken(
99           address destinationAddress,
100          uint256 minAmountOut,
101          address inputToken,
102          uint256 inputTokenAmount
103:     ) external override returns (uint256) {

124      function getEthFromZeta(
125          address destinationAddress,
126          uint256 minAmountOut,
127          uint256 zetaTokenAmount
128:     ) external override returns (uint256) {

158      function getTokenFromZeta(
159          address destinationAddress,
160          uint256 minAmountOut,
161          address outputToken,
162          uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {

184:     function hasZetaLiquidity() external view override returns (bool) {

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L21-L21), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L49), [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72-L72), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L77), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L103), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L128), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L163), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184-L184)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

17       function getPools(
18           address token0,
19           address token1,
20           uint256 startIndex,
21           uint256 count
22:      ) external view returns (address[] memory pairPools);

```
*GitHub*: [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17-L22)

```solidity
File: contracts/zevm/Interfaces.sol

8:       function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

10:      function wZetaContractAddress() external view returns (address);

12:      function uniswapv2FactoryAddress() external view returns (address);

14:      function gasPriceByChainId(uint256 chainID) external view returns (uint256);

16:      function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

18:      function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

22:      function totalSupply() external view returns (uint256);

24:      function balanceOf(address account) external view returns (uint256);

26:      function transfer(address recipient, uint256 amount) external returns (bool);

28:      function allowance(address owner, address spender) external view returns (uint256);

30:      function approve(address spender, uint256 amount) external returns (bool);

32:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

34:      function deposit(address to, uint256 amount) external returns (bool);

36:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

38:      function withdrawGasFee() external view returns (address, uint256);

50:      function name() external view returns (string memory);

52:      function symbol() external view returns (string memory);

54:      function decimals() external view returns (uint8);

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8-L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18-L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22-L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24-L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26-L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28-L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30-L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32-L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34-L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36-L36), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L38-L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L50-L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L52-L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L54-L54)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

50:      function transferFrom(address src, address dst, uint wad) external returns (bool);

52:      function withdraw(uint wad) external;

79:      constructor(address wzeta_) {

```
*GitHub*: [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50-L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52-L52), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L79)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

5:       function factory() external pure returns (address);

7:       function WETH() external pure returns (address);

9        function addLiquidity(
10           address tokenA,
11           address tokenB,
12           uint amountADesired,
13           uint amountBDesired,
14           uint amountAMin,
15           uint amountBMin,
16           address to,
17           uint deadline
18:      ) external returns (uint amountA, uint amountB, uint liquidity);

20       function addLiquidityETH(
21           address token,
22           uint amountTokenDesired,
23           uint amountTokenMin,
24           uint amountETHMin,
25           address to,
26           uint deadline
27:      ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

29       function removeLiquidity(
30           address tokenA,
31           address tokenB,
32           uint liquidity,
33           uint amountAMin,
34           uint amountBMin,
35           address to,
36           uint deadline
37:      ) external returns (uint amountA, uint amountB);

39       function removeLiquidityETH(
40           address token,
41           uint liquidity,
42           uint amountTokenMin,
43           uint amountETHMin,
44           address to,
45           uint deadline
46:      ) external returns (uint amountToken, uint amountETH);

48       function removeLiquidityWithPermit(
49           address tokenA,
50           address tokenB,
51           uint liquidity,
52           uint amountAMin,
53           uint amountBMin,
54           address to,
55           uint deadline,
56           bool approveMax,
57           uint8 v,
58           bytes32 r,
59           bytes32 s
60:      ) external returns (uint amountA, uint amountB);

62       function removeLiquidityETHWithPermit(
63           address token,
64           uint liquidity,
65           uint amountTokenMin,
66           uint amountETHMin,
67           address to,
68           uint deadline,
69           bool approveMax,
70           uint8 v,
71           bytes32 r,
72           bytes32 s
73:      ) external returns (uint amountToken, uint amountETH);

75       function swapExactTokensForTokens(
76           uint amountIn,
77           uint amountOutMin,
78           address[] calldata path,
79           address to,
80           uint deadline
81:      ) external returns (uint[] memory amounts);

83       function swapTokensForExactTokens(
84           uint amountOut,
85           uint amountInMax,
86           address[] calldata path,
87           address to,
88           uint deadline
89:      ) external returns (uint[] memory amounts);

91       function swapExactETHForTokens(
92           uint amountOutMin,
93           address[] calldata path,
94           address to,
95           uint deadline
96:      ) external payable returns (uint[] memory amounts);

98       function swapTokensForExactETH(
99           uint amountOut,
100          uint amountInMax,
101          address[] calldata path,
102          address to,
103          uint deadline
104:     ) external returns (uint[] memory amounts);

106      function swapExactTokensForETH(
107          uint amountIn,
108          uint amountOutMin,
109          address[] calldata path,
110          address to,
111          uint deadline
112:     ) external returns (uint[] memory amounts);

114      function swapETHForExactTokens(
115          uint amountOut,
116          address[] calldata path,
117          address to,
118          uint deadline
119:     ) external payable returns (uint[] memory amounts);

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5-L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7-L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L37), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L46), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L81), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L89), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91-L96), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L104), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L112), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114-L119), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121-L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123-L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125-L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127-L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129-L129)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

7        function removeLiquidityETHSupportingFeeOnTransferTokens(
8            address token,
9            uint liquidity,
10           uint amountTokenMin,
11           uint amountETHMin,
12           address to,
13           uint deadline
14:      ) external returns (uint amountETH);

16       function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17           address token,
18           uint liquidity,
19           uint amountTokenMin,
20           uint amountETHMin,
21           address to,
22           uint deadline,
23           bool approveMax,
24           uint8 v,
25           bytes32 r,
26           bytes32 s
27:      ) external returns (uint amountETH);

29       function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30           uint amountIn,
31           uint amountOutMin,
32           address[] calldata path,
33           address to,
34           uint deadline
35:      ) external;

37       function swapExactETHForTokensSupportingFeeOnTransferTokens(
38           uint amountOutMin,
39           address[] calldata path,
40           address to,
41           uint deadline
42:      ) external payable;

44       function swapExactTokensForETHSupportingFeeOnTransferTokens(
45           uint amountIn,
46           uint amountOutMin,
47           address[] calldata path,
48           address to,
49           uint deadline
50:      ) external;

```
*GitHub*: [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29-L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37-L42), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44-L50)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

10:      function totalSupply() external view returns (uint);

12:      function balanceOf(address owner) external view returns (uint);

14:      function allowance(address owner, address spender) external view returns (uint);

16:      function approve(address spender, uint wad) external returns (bool);

18:      function transfer(address to, uint wad) external returns (bool);

20:      function transferFrom(address from, address to, uint wad) external returns (bool);

22:      function deposit() external payable;

24:      function withdraw(uint wad) external;

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18-L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20-L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L22-L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24-L24)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

5:       function totalSupply() external view returns (uint256);

7:       function balanceOf(address account) external view returns (uint256);

9:       function transfer(address recipient, uint256 amount) external returns (bool);

11:      function allowance(address owner, address spender) external view returns (uint256);

13:      function approve(address spender, uint256 amount) external returns (bool);

15:      function decreaseAllowance(address spender, uint256 amount) external returns (bool);

17:      function increaseAllowance(address spender, uint256 amount) external returns (bool);

19:      function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

21:      function deposit(address to, uint256 amount) external returns (bool);

23:      function burn(address account, uint256 amount) external returns (bool);

25:      function withdraw(bytes memory to, uint256 amount) external returns (bool);

27:      function withdrawGasFee() external view returns (address, uint256);

29:      function PROTOCOL_FEE() external view returns (uint256);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5-L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7-L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9-L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11-L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17-L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19-L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21-L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23-L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27-L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29-L29)

```solidity
File: contracts/zevm/interfaces/zContract.sol

11       function onCrossChainCall(
12           zContext calldata context,
13           address zrc20,
14           uint256 amount,
15           bytes calldata message
16:      ) external;

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11-L16)

</details>





### [N&#x2011;53] NatSpec: Modifier `@param` tag is missing


*There are 2 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

/// @audit Missing '@param zetaMessage'
13   
14       /**
15        * @dev Maps a chain id to its corresponding address of the MultiChainSwap contract
16        * The address is expressed in bytes to allow non-EVM chains
17        * This mapping is useful, mainly, for two reasons:
18        *  - Given a chain id, the contract is able to route a transaction to its corresponding address
19        *  - To check that the messages (onZetaMessage, onZetaRevert) come from a trusted source
20        */
21       mapping(uint256 => bytes) public interactorsByChainId;
22   
23:      modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {

/// @audit Missing '@param zetaRevert'
20        */
21       mapping(uint256 => bytes) public interactorsByChainId;
22   
23       modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {
24           _isValidCaller();
25           if (keccak256(zetaMessage.zetaTxSenderAddress) != keccak256(interactorsByChainId[zetaMessage.sourceChainId]))
26               revert InvalidZetaMessageCall();
27           _;
28       }
29   
30:      modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L13-L23), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L20-L30)



### [N&#x2011;54] NatSpec: Modifier declarations should have `@dev` tags
`@dev` is used to explain extra details to developers

*There are 5 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

23       modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {
24           _isValidCaller();
25           if (keccak256(zetaMessage.zetaTxSenderAddress) != keccak256(interactorsByChainId[zetaMessage.sourceChainId]))
26               revert InvalidZetaMessageCall();
27           _;
28:      }

30       modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
31           _isValidCaller();
32           if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
33           if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();
34           _;
35:      }

```
*GitHub*: [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23-L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30-L35)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

94       modifier nonReentrant() {
95           if (_locked) revert ReentrancyError();
96           _locked = true;
97           _;
98           _locked = false;
99:      }

```
*GitHub*: [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94-L99)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

59       modifier nonReentrant() {
60           if (_locked) revert ReentrancyError();
61           _locked = true;
62           _;
63           _locked = false;
64:      }

```
*GitHub*: [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59-L64)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

65       modifier nonReentrant() {
66           if (_locked) revert ReentrancyError();
67           _locked = true;
68           _;
69           _locked = false;
70:      }

```
*GitHub*: [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65-L70)



### [N&#x2011;55] NatSpec: Modifier declarations should have `@notice` tags
`@notice` is used to explain to end users what the modifer does, and the compiler interprets `///` or `/**` comments (but not `//` or `/*`) as this tag if one wasn't explicitly provided

*There are 5 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

23       modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {
24           _isValidCaller();
25           if (keccak256(zetaMessage.zetaTxSenderAddress) != keccak256(interactorsByChainId[zetaMessage.sourceChainId]))
26               revert InvalidZetaMessageCall();
27           _;
28:      }

30       modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
31           _isValidCaller();
32           if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
33           if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();
34           _;
35:      }

```
*GitHub*: [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23-L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30-L35)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

94       modifier nonReentrant() {
95           if (_locked) revert ReentrancyError();
96           _locked = true;
97           _;
98           _locked = false;
99:      }

```
*GitHub*: [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94-L99)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

59       modifier nonReentrant() {
60           if (_locked) revert ReentrancyError();
61           _locked = true;
62           _;
63           _locked = false;
64:      }

```
*GitHub*: [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59-L64)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

65       modifier nonReentrant() {
66           if (_locked) revert ReentrancyError();
67           _locked = true;
68           _;
69           _locked = false;
70:      }

```
*GitHub*: [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65-L70)



### [N&#x2011;56] NatSpec: Modifier declarations should have descriptions


*There are 5 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

23       modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {
24           _isValidCaller();
25           if (keccak256(zetaMessage.zetaTxSenderAddress) != keccak256(interactorsByChainId[zetaMessage.sourceChainId]))
26               revert InvalidZetaMessageCall();
27           _;
28:      }

30       modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
31           _isValidCaller();
32           if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
33           if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();
34           _;
35:      }

```
*GitHub*: [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23-L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30-L35)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

94       modifier nonReentrant() {
95           if (_locked) revert ReentrancyError();
96           _locked = true;
97           _;
98           _locked = false;
99:      }

```
*GitHub*: [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94-L99)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

59       modifier nonReentrant() {
60           if (_locked) revert ReentrancyError();
61           _locked = true;
62           _;
63           _locked = false;
64:      }

```
*GitHub*: [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59-L64)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

65       modifier nonReentrant() {
66           if (_locked) revert ReentrancyError();
67           _locked = true;
68           _;
69           _locked = false;
70:      }

```
*GitHub*: [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65-L70)



### [N&#x2011;57] NatSpec: Non-public state variable declarations should use `@dev` tags
i.e. `@dev` [tags](https://docs.soliditylang.org/en/latest/natspec-format.html#tags). Note that since they're non-public, `@notice` is not the right tag to use.

*There are 18 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

10:      bytes32 constant ZERO_BYTES = keccak256(new bytes(0));

11:      uint256 internal immutable currentChainId;

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10-L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11-L11)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

58:      uint256 internal constant MAX_DEADLINE = 200;

69:      bool internal _locked;

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58-L58), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L69-L69)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

35:      uint256 internal constant MAX_DEADLINE = 200;

37:      address internal immutable WETH9Address;

43:      bool internal _locked;

```
*GitHub*: [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37-L37), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L43-L43)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

19:      uint256 internal constant MAX_DEADLINE = 200;

21:      address internal immutable wETH;

24:      IUniswapV2Router02 internal immutable uniswapV2Router;

```
*GitHub*: [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19-L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24-L24)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

29:      uint256 internal constant MAX_DEADLINE = 200;

40:      bool internal _locked;

```
*GitHub*: [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29-L29), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L40-L40)

```solidity
File: contracts/zevm/ZRC20.sol

34:      mapping(address => uint256) private _balances;

35:      mapping(address => mapping(address => uint256)) private _allowances;

36:      uint256 private _totalSupply;

37:      string private _name;

38:      string private _symbol;

39:      uint8 private _decimals;

```
*GitHub*: [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L34-L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35-L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L36-L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L37-L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L38-L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L39-L39)



### [N&#x2011;58] NatSpec: State variable declarations should have descriptions
e.g. `@notice` [tags](https://docs.soliditylang.org/en/latest/natspec-format.html#tags)

*There are 40 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/Zeta.non-eth.sol

11:      address public connectorAddress;

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L11-L11)

```solidity
File: contracts/evm/ZetaConnector.base.sol

16:      address public immutable zetaToken;

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L16-L16)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

16:      uint256 public maxSupply = 2 ** 256 - 1;

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16-L16)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

10:      bytes32 constant ZERO_BYTES = keccak256(new bytes(0));

11:      uint256 internal immutable currentChainId;

12:      ZetaConnector public immutable connector;

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10-L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L12-L12)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

58:      uint256 internal constant MAX_DEADLINE = 200;

60:      uint24 public immutable zetaPoolFee;

61:      uint24 public immutable tokenPoolFee;

63:      address public immutable WETH9Address;

64:      address public immutable zetaToken;

66:      ISwapRouterPancake public immutable pancakeV3Router;

67:      IUniswapV3Factory public immutable uniswapV3Factory;

69:      bool internal _locked;

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58-L58), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L60-L60), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L61-L61), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L63-L63), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L64-L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L66-L66), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L67-L67), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L69-L69)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

35:      uint256 internal constant MAX_DEADLINE = 200;

37:      address internal immutable WETH9Address;

38:      address public immutable zetaToken;

40:      IPoolRouter public immutable tridentRouter;

41:      ConcentratedLiquidityPoolFactory public immutable poolFactory;

43:      bool internal _locked;

```
*GitHub*: [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37-L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L38-L38), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L41-L41), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L43-L43)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

19:      uint256 internal constant MAX_DEADLINE = 200;

21:      address internal immutable wETH;

22:      address public immutable zetaToken;

24:      IUniswapV2Router02 internal immutable uniswapV2Router;

```
*GitHub*: [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19-L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21-L21), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L22-L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24-L24)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

29:      uint256 internal constant MAX_DEADLINE = 200;

31:      uint24 public immutable zetaPoolFee;

32:      uint24 public immutable tokenPoolFee;

34:      address public immutable WETH9Address;

35:      address public immutable zetaToken;

37:      ISwapRouter public immutable uniswapV3Router;

38:      IUniswapV3Factory public immutable uniswapV3Factory;

40:      bool internal _locked;

```
*GitHub*: [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29-L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L31-L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L32-L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L34-L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L35-L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L37-L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L38-L38), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L40-L40)

```solidity
File: contracts/zevm/SystemContract.sol

28:      mapping(uint256 => address) public gasZetaPoolByChainId;

34:      address public immutable uniswapv2Router02Address;

```
*GitHub*: [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L28-L28), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L34-L34)

```solidity
File: contracts/zevm/ZRC20.sol

34:      mapping(address => uint256) private _balances;

35:      mapping(address => mapping(address => uint256)) private _allowances;

36:      uint256 private _totalSupply;

37:      string private _name;

38:      string private _symbol;

39:      uint8 private _decimals;

```
*GitHub*: [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L34-L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35-L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L36-L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L37-L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L38-L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L39-L39)

</details>





### [N&#x2011;59] NatSpec: Use `@inheritdoc` to inherit the NatSpec of the base function


*There is one instance of this issue:*

```solidity
File: contracts/evm/Zeta.non-eth.sol

73:      function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {

```
*GitHub*: [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73-L73)



### [N&#x2011;60] Pausable contract never uses `whenNotPosed` modifier
Consider whether the contract really needs to be `Pausable`

*There is one instance of this issue:*

```solidity
File: contracts/evm/ZetaConnector.base.sol

/// @audit Pausable
15:  contract ZetaConnectorBase is ConnectorErrors, Pausable {

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15)



### [N&#x2011;61] Style guide: Contract does not follow the Solidity style guide's suggested layout ordering
The [style guide](https://docs.soliditylang.org/en/v0.8.16/style-guide.html#order-of-layout) says that, within a contract, the ordering should be 1) Type declarations, 2) State variables, 3) Events, 4) Modifiers, and 5) Functions, but the contract(s) below do not follow this ordering

*There are 7 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ZetaConnector.base.sol

/// @audit function constructor came earlier
93        modifier onlyPauser() {
94            if (msg.sender != pauserAddress) revert CallerIsNotPauser(msg.sender);
95            _;
96:       }

```
*GitHub*: [93](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L93-L96)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

/// @audit function constructor came earlier
94        modifier nonReentrant() {
95            if (_locked) revert ReentrancyError();
96            _locked = true;
97            _;
98            _locked = false;
99:       }

```
*GitHub*: [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94-L99)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit function constructor came earlier
59        modifier nonReentrant() {
60            if (_locked) revert ReentrancyError();
61            _locked = true;
62            _;
63            _locked = false;
64:       }

```
*GitHub*: [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59-L64)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

/// @audit function constructor came earlier
65        modifier nonReentrant() {
66            if (_locked) revert ReentrancyError();
67            _locked = true;
68            _;
69            _locked = false;
70:       }

```
*GitHub*: [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65-L70)

```solidity
File: contracts/zevm/Interfaces.sol

/// @audit function withdrawGasFee came earlier
40:       event Transfer(address indexed from, address indexed to, uint256 value);

```
*GitHub*: [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40)

```solidity
File: contracts/zevm/ZRC20.sol

/// @audit function _msgData came earlier
52        modifier onlyFungible() {
53            if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
54            _;
55:       }

```
*GitHub*: [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L52-L55)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

/// @audit function PROTOCOL_FEE came earlier
31:       event Transfer(address indexed from, address indexed to, uint256 value);

```
*GitHub*: [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31)

</details>





### [N&#x2011;62] Style guide: Contract names should use CamelCase
According to the Solidity [style guide](https://docs.soliditylang.org/en/latest/style-guide.html#contract-and-library-names) contract names should be in CamelCase and should match their file names.

*There is one instance of this issue:*

```solidity
File: contracts/zevm/interfaces/zContract.sol

10:  interface zContract {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10-L10)



### [N&#x2011;63] Style guide: Control structures do not follow the Solidity Style Guide
See the [control structures](https://docs.soliditylang.org/en/latest/style-guide.html#control-structures) section of the Solidity Style Guide

*There are 139 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/Zeta.non-eth.sol

41:           if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);

55:           if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);

66:           if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);

77:           if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);

34:           if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();

41:           if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);

42:           if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();

55:           if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);

56:           if (tssAddress == address(0)) revert InvalidAddress();

66:           if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);

77:           if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);

```
*GitHub*: [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L41), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L55), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L66), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L77), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L34), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L42), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L55), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L56), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L66), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L77)

```solidity
File: contracts/evm/ZetaConnector.base.sol

94:           if (msg.sender != pauserAddress) revert CallerIsNotPauser(msg.sender);

102:          if (msg.sender != tssAddress) revert CallerIsNotTss(msg.sender);

110:          if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);

129:          if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);

94:           if (msg.sender != pauserAddress) revert CallerIsNotPauser(msg.sender);

102:          if (msg.sender != tssAddress) revert CallerIsNotTss(msg.sender);

110:          if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);

118:          if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

129:          if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);

130:          if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

141:          if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

```
*GitHub*: [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L94), [102](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L102), [110](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L110), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L129), [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L94), [102](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L102), [110](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L110), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L118), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L129), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L130), [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L141)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

33:           if (!success) revert ZetaTransferError();

61:           if (!success) revert ZetaTransferError();

87:           if (!success) revert ZetaTransferError();

33:           if (!success) revert ZetaTransferError();

61:           if (!success) revert ZetaTransferError();

87:           if (!success) revert ZetaTransferError();

```
*GitHub*: [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L33), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L61), [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L87), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L33), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L61), [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L87)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

69:           if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);

```
*GitHub*: [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L69)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

33:           if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();

32:           if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();

33:           if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();

38:           if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

44:           if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);

```
*GitHub*: [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L33), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L33), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L38), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L44)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

95:           if (_locked) revert ReentrancyError();

108:          if (msg.value == 0) revert InputCantBeZero();

133:          if (inputTokenAmount == 0) revert InputCantBeZero();

157:          if (zetaTokenAmount == 0) revert InputCantBeZero();

179:          if (!sent) revert ErrorSendingETH();

191:          if (zetaTokenAmount == 0) revert InputCantBeZero();

95:           if (_locked) revert ReentrancyError();

107:          if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

108:          if (msg.value == 0) revert InputCantBeZero();

132:          if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

133:          if (inputTokenAmount == 0) revert InputCantBeZero();

156:          if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

157:          if (zetaTokenAmount == 0) revert InputCantBeZero();

179:          if (!sent) revert ErrorSendingETH();

190:          if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

191:          if (zetaTokenAmount == 0) revert InputCantBeZero();

```
*GitHub*: [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L95), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L108), [133](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L133), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L157), [179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L179), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L95), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L107), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L108), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L132), [133](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L133), [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L156), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L157), [179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L179), [190](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L190), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

60:           if (_locked) revert ReentrancyError();

79:           if (msg.value == 0) revert InputCantBeZero();

106:          if (inputTokenAmount == 0) revert InputCantBeZero();

142:          if (zetaTokenAmount == 0) revert InputCantBeZero();

173:          if (zetaTokenAmount == 0) revert InputCantBeZero();

60:           if (_locked) revert ReentrancyError();

69:           if (token0 < token1) return (token0, token1);

78:           if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

79:           if (msg.value == 0) revert InputCantBeZero();

105:          if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

106:          if (inputTokenAmount == 0) revert InputCantBeZero();

141:          if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

142:          if (zetaTokenAmount == 0) revert InputCantBeZero();

172:          if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

173:          if (zetaTokenAmount == 0) revert InputCantBeZero();

```
*GitHub*: [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L60), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L79), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L106), [142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L142), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L60), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L69), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L79), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L105), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L106), [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L141), [142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L142), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L172), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

39:           if (msg.value == 0) revert InputCantBeZero();

65:           if (inputTokenAmount == 0) revert InputCantBeZero();

101:          if (zetaTokenAmount == 0) revert InputCantBeZero();

131:          if (zetaTokenAmount == 0) revert InputCantBeZero();

27:           if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

38:           if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

39:           if (msg.value == 0) revert InputCantBeZero();

64:           if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

65:           if (inputTokenAmount == 0) revert InputCantBeZero();

100:          if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

101:          if (zetaTokenAmount == 0) revert InputCantBeZero();

130:          if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

131:          if (zetaTokenAmount == 0) revert InputCantBeZero();

```
*GitHub*: [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L39), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L65), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L101), [131](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L39), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L64), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L65), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L100), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L101), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L130), [131](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

66:           if (_locked) revert ReentrancyError();

79:           if (msg.value == 0) revert InputCantBeZero();

105:          if (inputTokenAmount == 0) revert InputCantBeZero();

130:          if (zetaTokenAmount == 0) revert InputCantBeZero();

153:          if (!sent) revert ErrorSendingETH();

165:          if (zetaTokenAmount == 0) revert InputCantBeZero();

66:           if (_locked) revert ReentrancyError();

78:           if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

79:           if (msg.value == 0) revert InputCantBeZero();

104:          if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

105:          if (inputTokenAmount == 0) revert InputCantBeZero();

129:          if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

130:          if (zetaTokenAmount == 0) revert InputCantBeZero();

153:          if (!sent) revert ErrorSendingETH();

164:          if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

165:          if (zetaTokenAmount == 0) revert InputCantBeZero();

```
*GitHub*: [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L66), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130), [153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L153), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L66), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79), [104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L129), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130), [153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L153), [164](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165)

```solidity
File: contracts/zevm/SystemContract.sol

52:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

74:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

88:           if (tokenA == tokenB) revert CantBeIdenticalAddresses();

124:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

135:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

146:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

157:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

168:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

52:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

74:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

75:           if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();

88:           if (tokenA == tokenB) revert CantBeIdenticalAddresses();

90:           if (token0 == address(0)) revert CantBeZeroAddress();

124:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

135:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

146:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

157:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

158:          if (addr == address(0)) revert ZeroAddress();

168:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

169:          if (addr == address(0)) revert ZeroAddress();

```
*GitHub*: [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74), [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L88), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135), [146](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L75), [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L88), [90](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L90), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135), [146](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L158), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168), [169](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L169)

```solidity
File: contracts/zevm/ZRC20.sol

53:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

69:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

161:          if (currentAllowance < amount) revert LowAllowance();

183:          if (senderBalance < amount) revert LowBalance();

203:          if (accountBalance < amount) revert LowBalance();

226:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();

53:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

69:           if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

161:          if (currentAllowance < amount) revert LowAllowance();

179:          if (sender == address(0)) revert ZeroAddress();

180:          if (recipient == address(0)) revert ZeroAddress();

183:          if (senderBalance < amount) revert LowBalance();

192:          if (account == address(0)) revert ZeroAddress();

200:          if (account == address(0)) revert ZeroAddress();

203:          if (accountBalance < amount) revert LowBalance();

212:          if (owner == address(0)) revert ZeroAddress();

213:          if (spender == address(0)) revert ZeroAddress();

226:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();

```
*GitHub*: [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L161), [183](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L183), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L203), [226](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226), [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L161), [179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L179), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L180), [183](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L183), [192](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L192), [200](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L200), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L203), [212](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L212), [213](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L213), [226](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

85:           if (msg.sender != wzeta) revert OnlyWZETA();

97:           if (!sent) revert FailedZetaSent();

115:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();

85:           if (msg.sender != wzeta) revert OnlyWZETA();

94:           if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();

97:           if (!sent) revert FailedZetaSent();

115:          if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();

```
*GitHub*: [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L85), [97](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L97), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L85), [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L94), [97](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L97), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115)

</details>





### [N&#x2011;64] Style guide: Extraneous whitespace
See the [whitespace](https://docs.soliditylang.org/en/v0.8.16/style-guide.html#whitespace-in-expressions) section of the Solidity Style Guide

*There are 3 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

178:          (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
*GitHub*: [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

152:          (bool sent, ) = destinationAddress.call{value: amountOut}("");

```
*GitHub*: [152](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

96:           (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");

```
*GitHub*: [96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96)



### [N&#x2011;65] Style guide: Function ordering does not follow the Solidity style guide
According to the [Solidity style guide](https://docs.soliditylang.org/en/v0.8.17/style-guide.html#order-of-functions), functions should be laid out in the following order :`constructor()`, `receive()`, `fallback()`, `external`, `public`, `internal`, `private`, but the cases below do not follow this pattern

*There are 9 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

/// @audit _isValidCaller() came earlier
50:       function _isValidChainId(uint256 chainId) internal view returns (bool) {

/// @audit _isValidChainId() came earlier
54:       function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {

```
*GitHub*: [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L50), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

/// @audit getPair() came earlier
74        function getZetaFromEth(
75            address destinationAddress,
76            uint256 minAmountOut
77:       ) external payable override returns (uint256) {

```
*GitHub*: [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L77)

```solidity
File: contracts/zevm/SystemContract.sol

/// @audit sortTokens() came earlier
100:      function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {

/// @audit uniswapv2PairFor() came earlier
123:      function setGasPrice(uint256 chainID, uint256 price) external {

```
*GitHub*: [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L100), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123)

```solidity
File: contracts/zevm/ZRC20.sol

/// @audit _msgData() came earlier
60        constructor(
61            string memory name_,
62            string memory symbol_,
63            uint8 decimals_,
64            uint256 chainid_,
65            CoinType coinType_,
66            uint256 gasLimit_,
67:           address systemContractAddress_

/// @audit transferFrom() came earlier
173:      function burn(uint256 amount) external returns (bool) {

/// @audit _approve() came earlier
225:      function deposit(address to, uint256 amount) external override returns (bool) {

/// @audit withdrawGasFee() came earlier
256:      function withdraw(bytes memory to, uint256 amount) external override returns (bool) {

```
*GitHub*: [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L67), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173), [225](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225), [256](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256)



### [N&#x2011;66] Style guide: Lines are too long
Usually lines in source code are limited to [80](https://softwareengineering.stackexchange.com/questions/148677/why-is-80-characters-the-standard-limit-for-code-width) characters. Today's screens are much larger so it's reasonable to stretch this in some cases. The solidity style guide recommends a maximumum line length of [120 characters](https://docs.soliditylang.org/en/v0.8.17/style-guide.html#maximum-line-length), so the lines below should be split when they reach that length.

*There are 14 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

183:          // and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount.

```
*GitHub*: [183](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L183)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

13:    * This version is only for Ethereum network because in the other chains we mint and burn and in this one we lock and unlock.

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L13)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

13:    * This version is for every chain but Etherum network because in the other chains we mint and burn and in Etherum we lock and unlock

```
*GitHub*: [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L13)

```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

9:            /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id

43:           /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L9), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L43)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

18:           address tokenIn; /// @dev the input token address. If tokenIn is address(0), msg.value will be wrapped and used as input token

27:           address tokenIn; /// @dev the token address to swap-in. If tokenIn is address(0), msg.value will be wrapped and used as input token

36:           address tokenIn; /// @dev the input token address. If tokenIn is address(0), msg.value will be wrapped and used as input token

45:           address tokenIn; /// @dev the token address to swap-in. If tokenIn is address(0), msg.value will be wrapped and used as input token

```
*GitHub*: [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L18), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L27), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L36), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L45)

```solidity
File: contracts/zevm/SystemContract.sol

27:       // @dev: Map to know uniswap V2 pool of ZETA/ZRC20 given a chain id. This refer to the build in uniswap deployed at genesis.

```
*GitHub*: [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L27)

```solidity
File: contracts/zevm/ZRC20.sol

234:       * @return returns the ZRC20 address for gas on the same chain of this ZRC20, and calculates the gas fee for withdraw()

250:       * @dev Withraws ZRC20 tokens to external chains, this function causes cctx module to send out outbound tx to the outbound chain

```
*GitHub*: [234](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L234), [250](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L250)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

9:            /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id

43:           /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L9), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L43)

</details>





### [N&#x2011;67] Style guide: Local and state variables should be named using lowerCamelCase
The Solidity style guide [says](https://docs.soliditylang.org/en/latest/style-guide.html#function-argument-names) to use mixedCase for function argument names

*There are 6 instances of this issue:*

```solidity
File: contracts/evm/ERC20Custody.sol

68:      constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

68:      constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

80:      function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {

```
*GitHub*: [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L68), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L68), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80-L80)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

75:          address WETH9Address_,

```
*GitHub*: [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L75-L75)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

45:      constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

```
*GitHub*: [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L45)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

46:          address WETH9Address_,

```
*GitHub*: [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L46-L46)



### [N&#x2011;68] Style guide: Non-`external`/`public` function names should begin with an underscore
According to the Solidity Style Guide, non-`external`/`public` function names should begin with an [underscore](https://docs.soliditylang.org/en/latest/style-guide.html#underscore-prefix-for-non-external-functions-and-variables)

*There are 2 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

68:      function getPair(address token0, address token1) internal pure returns (address, address) {

```
*GitHub*: [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L68)

```solidity
File: contracts/zevm/SystemContract.sol

87:      function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {

```
*GitHub*: [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87-L87)



### [N&#x2011;69] Style guide: Non-`external`/`public` variable names should begin with an underscore
According to the Solidity Style Guide, non-`external`/`public` variable names should begin with an [underscore](https://docs.soliditylang.org/en/latest/style-guide.html#underscore-prefix-for-non-external-functions-and-variables)

*There are 9 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

10:      bytes32 constant ZERO_BYTES = keccak256(new bytes(0));

11:      uint256 internal immutable currentChainId;

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10-L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11-L11)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

58:      uint256 internal constant MAX_DEADLINE = 200;

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58-L58)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

35:      uint256 internal constant MAX_DEADLINE = 200;

37:      address internal immutable WETH9Address;

```
*GitHub*: [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37-L37)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

19:      uint256 internal constant MAX_DEADLINE = 200;

21:      address internal immutable wETH;

24:      IUniswapV2Router02 internal immutable uniswapV2Router;

```
*GitHub*: [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19-L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24-L24)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

29:      uint256 internal constant MAX_DEADLINE = 200;

```
*GitHub*: [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29-L29)



### [N&#x2011;70] Style guide: Struct names should use CamelCase
According to the Solidity [style guide](https://docs.soliditylang.org/en/latest/style-guide.html#contract-and-library-names) contract names should be in CamelCase and should match their file names.

*There is one instance of this issue:*

```solidity
File: contracts/zevm/interfaces/zContract.sol

4    struct zContext {
5        bytes origin;
6        address sender;
7        uint256 chainID;
8:   }

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L4-L8)



### [N&#x2011;71] Style guide: Top-level declarations should be separated by at least two lines
And functions within contracts should be separate by a [single](https://docs.soliditylang.org/en/latest/style-guide.html#blank-lines) line

*There are 25 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/interfaces/ZetaInterfaces.sol

2     pragma solidity 0.8.7;
3     
4:    interface ZetaInterfaces {

47    }
48    
49:   interface ZetaConnector {

54    }
55    
56:   interface ZetaReceiver {

106   }
107   
108:  interface ZetaCommonErrors {

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2-L4), [47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L47-L49), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L54-L56), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L106-L108)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

10    import "../interfaces/ZetaInterfaces.sol";
11    
12:   interface ZetaTokenConsumerUniV3Errors {

18    }
19    
20:   interface WETH9 {

22    }
23    
24:   interface ISwapRouterPancake is IUniswapV3SwapCallback {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L10-L12), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L18-L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L22-L24)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

10    import "./interfaces/TridentIPoolRouter.sol";
11    
12:   interface ZetaTokenConsumerTridentErrors {

18    }
19    
20:   interface WETH9 {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L10-L12), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L18-L20)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

8     import "../interfaces/ZetaInterfaces.sol";
9     
10:   interface ZetaTokenConsumerUniV2Errors {

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L8-L10)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

10    import "../interfaces/ZetaInterfaces.sol";
11    
12:   interface ZetaTokenConsumerUniV3Errors {

18    }
19    
20:   interface WETH9 {

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L10-L12), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L18-L20)

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

14    pragma solidity >=0.8.0;
15    
16:   interface ConcentratedLiquidityPoolFactory {

```
*GitHub*: [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L14-L16)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

14    pragma solidity >=0.8.0;
15    
16:   interface IPoolRouter {

```
*GitHub*: [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14-L16)

```solidity
File: contracts/zevm/Interfaces.sol

19    }
20    
21:   interface IZRC20 {

47    }
48    
49:   interface IZRC20Metadata is IZRC20 {

```
*GitHub*: [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L19-L21), [47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L47-L49)

```solidity
File: contracts/zevm/ZRC20.sol

18    }
19    
20:   contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {

```
*GitHub*: [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L18-L20)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

2     pragma solidity 0.8.7;
3     
4:    interface ZetaInterfaces {

47    }
48    
49:   interface WZETA {

53    }
54    
55:   contract ZetaConnectorZEVM is ZetaInterfaces {

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L2-L4), [47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L47-L49), [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L53-L55)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router01.sol

2     pragma solidity 0.8.7;
3     
4:    interface IUniswapV2Router01 {

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L2-L4)

```solidity
File: contracts/zevm/interfaces/IUniswapV2Router02.sol

4     import "./IUniswapV2Router01.sol";
5     
6:    interface IUniswapV2Router02 is IUniswapV2Router01 {

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L4-L6)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

2     pragma solidity 0.8.7;
3     
4:    interface IWETH9 {

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L2-L4)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

2     pragma solidity 0.8.7;
3     
4:    interface IZRC20 {

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L2-L4)

```solidity
File: contracts/zevm/interfaces/zContract.sol

8     }
9     
10:   interface zContract {

```
*GitHub*: [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L8-L10)

</details>





### [N&#x2011;72] Style guide: Variable names for `immutable`s should use CONSTANT_CASE
For `immutable` variable names, each word should use all capital letters, with underscores separating each word (CONSTANT_CASE)

*There are 23 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

32:      uint256 public immutable zetaMaxFee;

34:      IERC20 public immutable zeta;

```
*GitHub*: [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L32-L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L34-L34)

```solidity
File: contracts/evm/ZetaConnector.base.sol

16:      address public immutable zetaToken;

```
*GitHub*: [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L16-L16)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

11:      uint256 internal immutable currentChainId;

12:      ZetaConnector public immutable connector;

```
*GitHub*: [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11-L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L12-L12)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

60:      uint24 public immutable zetaPoolFee;

61:      uint24 public immutable tokenPoolFee;

64:      address public immutable zetaToken;

66:      ISwapRouterPancake public immutable pancakeV3Router;

67:      IUniswapV3Factory public immutable uniswapV3Factory;

```
*GitHub*: [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L60-L60), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L61-L61), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L64-L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L66-L66), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L67-L67)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

38:      address public immutable zetaToken;

40:      IPoolRouter public immutable tridentRouter;

41:      ConcentratedLiquidityPoolFactory public immutable poolFactory;

```
*GitHub*: [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L38-L38), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L41-L41)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

21:      address internal immutable wETH;

22:      address public immutable zetaToken;

24:      IUniswapV2Router02 internal immutable uniswapV2Router;

```
*GitHub*: [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21-L21), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L22-L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24-L24)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

31:      uint24 public immutable zetaPoolFee;

32:      uint24 public immutable tokenPoolFee;

35:      address public immutable zetaToken;

37:      ISwapRouter public immutable uniswapV3Router;

38:      IUniswapV3Factory public immutable uniswapV3Factory;

```
*GitHub*: [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L31-L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L32-L32), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L35-L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L37-L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L38-L38)

```solidity
File: contracts/zevm/SystemContract.sol

33:      address public immutable uniswapv2FactoryAddress;

34:      address public immutable uniswapv2Router02Address;

```
*GitHub*: [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L33-L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L34-L34)

</details>





### [N&#x2011;73] Style guide: Variable names that consist of all capital letters should be reserved for `constant`/`immutable` variables
If the variable needs to be different based on which class it comes from, a `view`/`pure` _function_ should be used instead (e.g. like [this](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/76eee35971c2541585e05cbf258510dda7b2fbc6/contracts/token/ERC20/extensions/draft-IERC20Permit.sol#L59)).

*There are 3 instances of this issue:*

```solidity
File: contracts/zevm/ZRC20.sol

28:      address public SYSTEM_CONTRACT_ADDRESS;

30:      uint256 public GAS_LIMIT;

32:      uint256 public PROTOCOL_FLAT_FEE;

```
*GitHub*: [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L28-L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L30-L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L32-L32)



### [N&#x2011;74] Unnecessary cast
The variable is being cast to its own type

*There is one instance of this issue:*

```solidity
File: contracts/evm/ERC20Custody.sol

/// @audit contract IERC20
197:         IERC20(asset).safeTransfer(recipient, amount);

```
*GitHub*: [197](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L197-L197)



### [N&#x2011;75] Unused `error` definition
Note that there may be cases where an error superficially appears to be used, but this is only because there are multiple definitions of the error in different files. In such cases, the error definition should be moved into a separate file. The instances below are the unused definitions.

*There are 4 instances of this issue:*

```solidity
File: contracts/evm/interfaces/ZetaErrors.sol

9:       error CallerIsNotTss(address caller);

24:      error ZetaTransferError();

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L9-L9), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L24-L24)

```solidity
File: contracts/evm/interfaces/ZetaInteractorErrors.sol

9:       error InvalidDestinationChainId();

```
*GitHub*: [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L9-L9)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

15:      error ErrorSendingETH();

```
*GitHub*: [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L15-L15)



### [N&#x2011;76] Unused `event` definition
Note that there may be cases where an event superficially appears to be used, but this is only because there are multiple definitions of the event in different files. In such cases, the event definition should be moved into a separate file. The instances below are the unused definitions.

*There are 11 instances of this issue:*

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

5:       event Approval(address indexed owner, address indexed spender, uint value);

6:       event Transfer(address indexed from, address indexed to, uint value);

7:       event Deposit(address indexed dst, uint wad);

8:       event Withdrawal(address indexed src, uint wad);

```
*GitHub*: [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8-L8)

```solidity
File: contracts/zevm/interfaces/IZRC20.sol

31:      event Transfer(address indexed from, address indexed to, uint256 value);

32:      event Approval(address indexed owner, address indexed spender, uint256 value);

33:      event Deposit(bytes from, address indexed to, uint256 value);

34:      event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

35:      event UpdatedSystemContract(address systemContract);

36:      event UpdatedGasLimit(uint256 gasLimit);

37:      event UpdatedProtocolFlatFee(uint256 protocolFlatFee);

```
*GitHub*: [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31-L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32-L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33-L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34-L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35-L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36-L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37-L37)



### [N&#x2011;77] Unused `modifer`s
Note that there may be cases where a modifier superficially appears to be used, but this is only because there are multiple definitions of the modifier in different files. In such cases, the modifier definition should be moved into a separate file. The instances below are the unused modifiers.

*There are 2 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

23       modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {
24           _isValidCaller();
25           if (keccak256(zetaMessage.zetaTxSenderAddress) != keccak256(interactorsByChainId[zetaMessage.sourceChainId]))
26               revert InvalidZetaMessageCall();
27           _;
28:      }

30       modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
31           _isValidCaller();
32           if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
33           if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();
34           _;
35:      }

```
*GitHub*: [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23-L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30-L35)



### [N&#x2011;78] Unused `struct` definition
Note that there may be cases where a struct superficially appears to be used, but this is only because there are multiple definitions of the struct in different files. In such cases, the struct definition should be moved into a separate file. The instances below are the unused definitions.

*There are 2 instances of this issue:*

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

26       struct ZetaMessage {
27           bytes zetaTxSenderAddress;
28           uint256 sourceChainId;
29           address destinationAddress;
30           /// @dev Remaining ZETA from zetaValueAndGas after subtracting ZetaChain gas fees and destination gas fees
31           uint256 zetaValue;
32           bytes message;
33:      }

38       struct ZetaRevert {
39           address zetaTxSenderAddress;
40           uint256 sourceChainId;
41           bytes destinationAddress;
42           uint256 destinationChainId;
43           /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
44           uint256 remainingZetaValue;
45           bytes message;
46:      }

```
*GitHub*: [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L26-L33), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L38-L46)



### [N&#x2011;79] Unused contract variables
Note that there may be cases where a variable appears to be used, but this is only because there are multiple definitions of the varible in different files. In such cases, the variable definition should be moved into a separate file. The instances below are the unused variables.

*There are 2 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

58:      uint256 internal constant MAX_DEADLINE = 200;

```
*GitHub*: [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58-L58)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

35:      uint256 internal constant MAX_DEADLINE = 200;

```
*GitHub*: [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L35)



### [N&#x2011;80] Unused file
The file is never imported by any other source file. If the file is needed for tests, it should be moved to a test directory

*There are 2 instances of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

1:    // SPDX-License-Identifier: MIT

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L1)

```solidity
File: contracts/zevm/interfaces/IWZETA.sol

1:    // SPDX-License-Identifier: MIT

```
*GitHub*: [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L1)



### [N&#x2011;81] Unused file import
The file is imported, but none of its identifiers are referenced. If identifiers are solely pulled in via child imports, those imports should be done directly instead, and the current one removed.

*There are 7 instances of this issue:*

```solidity
File: contracts/evm/ZetaConnector.base.sol

4:   import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L4-L4)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

4:   import "@openzeppelin/contracts/interfaces/IERC20.sol";

6:   import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L4-L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L6-L6)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

4:   import "@openzeppelin/contracts/interfaces/IERC20.sol";

6:   import "@uniswap/v3-periphery/contracts/interfaces/IQuoter.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L4-L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L6-L6)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

4:   import "@openzeppelin/contracts/interfaces/IERC20.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L4-L4)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

4:   import "@openzeppelin/contracts/interfaces/IERC20.sol";

```
*GitHub*: [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L4-L4)



### [N&#x2011;82] Unused function parameter
Comment out the variable name to suppress compiler warnings

*There are 14 instances of this issue:*

```solidity
File: contracts/evm/ZetaConnector.base.sol

/// @audit input
166:     function send(ZetaInterfaces.SendInput calldata input) external virtual {}

/// @audit zetaTxSenderAddress
/// @audit sourceChainId
/// @audit destinationAddress
/// @audit zetaValue
/// @audit message
/// @audit internalSendHash
172      function onReceive(
173          bytes calldata zetaTxSenderAddress,
174          uint256 sourceChainId,
175          address destinationAddress,
176          uint256 zetaValue,
177          bytes calldata message,
178          bytes32 internalSendHash
179:     ) external virtual {}

/// @audit zetaTxSenderAddress
/// @audit message
/// @audit internalSendHash
/// @audit sourceChainId
/// @audit destinationAddress
/// @audit destinationChainId
/// @audit remainingZetaValue
185      function onRevert(
186          address zetaTxSenderAddress,
187          uint256 sourceChainId,
188          bytes calldata destinationAddress,
189          uint256 destinationChainId,
190          uint256 remainingZetaValue,
191          bytes calldata message,
192          bytes32 internalSendHash
193:     ) external virtual {}

```
*GitHub*: [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166-L166), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)



### [N&#x2011;83] Use the latest solidity (prior to 0.8.20 if on L2s) for deployment
```
When deploying contracts, you should use the latest released version of Solidity. Apart from exceptional cases, only the latest version receives security fixes.
```
https://docs.soliditylang.org/en/v0.8.20/

Since deployed contracts should not use floating pragmas, I've flagged all instances where a version prior to 0.8.19 is allowed by the version pragma

*There are 14 instances of this issue:*

<details>
<summary>see instances</summary>


```solidity
File: contracts/evm/ERC20Custody.sol

3:   pragma solidity 0.8.7;

```
*GitHub*: [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L3-L3)

```solidity
File: contracts/evm/Zeta.eth.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L2-L2)

```solidity
File: contracts/evm/Zeta.non-eth.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L2-L2)

```solidity
File: contracts/evm/ZetaConnector.base.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L2-L2)

```solidity
File: contracts/evm/ZetaConnector.eth.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L2-L2)

```solidity
File: contracts/evm/ZetaConnector.non-eth.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L2-L2)

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L2-L2)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L2-L2)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L2-L2)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L2-L2)

```solidity
File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L2-L2)

```solidity
File: contracts/zevm/SystemContract.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L2-L2)

```solidity
File: contracts/zevm/ZRC20.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L2-L2)

```solidity
File: contracts/zevm/ZetaConnectorZEVM.sol

2:   pragma solidity 0.8.7;

```
*GitHub*: [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L2-L2)

</details>





### [N&#x2011;84] Using `>`/`>=` without specifying an upper bound is unsafe
There _will_ be breaking changes in future versions of solidity, and at that point your code will no longer be compatable. While you may have the specific version to use in a configuration file, others that include your source files may not.

*There are 2 instances of this issue:*

```solidity
File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

14:   pragma solidity >=0.8.0;

```
*GitHub*: [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L14)

```solidity
File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol

14:   pragma solidity >=0.8.0;

```
*GitHub*: [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14)



### [N&#x2011;85] Visibility should be set explicitly rather than defaulting to `internal`


*There is one instance of this issue:*

```solidity
File: contracts/evm/tools/ZetaInteractor.sol

10:       bytes32 constant ZERO_BYTES = keccak256(new bytes(0));

```
*GitHub*: [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10)
