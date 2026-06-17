## Summary

### Low Risk Issues
| |Issue|Instances|
|:---|:---|---:|
|[L&#x2011;01](#l01-some-tokens-may-revert-when-large-transfers-are-made)|Some tokens may revert when large transfers are made|1|
|[L&#x2011;02](#l02-some-tokens-may-revert-when-zero-value-transfers-are-made)|Some tokens may revert when zero value transfers are made|2|
|[L&#x2011;03](#l03-critical-functions-should-be-controlled-by-time-locks)|Critical functions should be controlled by time locks|5|
|[L&#x2011;04](#l04-empty-receive-fallback-function)|Empty `receive()`/`fallback()` function|3|
|[L&#x2011;05](#l05-missing-gas-limit-for-external-call)|Missing gas limit for external call|3|
|[L&#x2011;06](#l06-lack-of-contract-existence-checks-before-low-level-calls)|Lack of contract existence checks before low-level calls|3|
|[L&#x2011;07](#l07-unsafe-solidity-low-level-call-can-cause-gas-grief-attack)|Unsafe solidity low-level call can cause gas grief attack|3|
|[L&#x2011;08](#l08-owner-can-renounce-ownership)|Owner can renounce Ownership|1|
|[L&#x2011;09](#l09-using-without-specifying-an-upper-bound-in-version-pragma-is-unsafe)|Using `>`/`>=` without specifying an upper bound in version pragma is unsafe|2|
|[L&#x2011;10](#l10-consider-implementing-two-step-procedure-for-updating-protocol-addresses)|Consider implementing two-step procedure for updating protocol addresses|1|
|[L&#x2011;11](#l11-critical-protocol-parameter-should-have-limits)|Critical protocol parameter should have limits|3|
|[L&#x2011;12](#l12-missing-checks-for-address0-in-the-constructor)|Missing checks for address(0) in the constructor|3|
|[L&#x2011;13](#l13-constructor-function-lacks-parameter-validation)|`constructor` function lacks parameter validation|9|
|[L&#x2011;14](#l14-state-variables-not-capped-at-reasonable-values)|State variables not capped at reasonable values|4|
| | |43|

### Non-critical Issues
| |Issue|Instances|
|:---|:---|---:|
|[N&#x2011;01](#n01-avoid-the-use-of-sensitive-terms)|Avoid the use of sensitive terms|18|
|[N&#x2011;02](#n02-duplicated-if-revert-checks-should-be-refactored)|Duplicated `if`-`revert()` checks should be refactored|16|
|[N&#x2011;03](#n03-multiple-definition-of-the-same-constant-immutable)|Multiple definition of the same `constant`/`immutable`|7|
|[N&#x2011;04](#n04-common-functions-should-be-refactored-to-a-common-base-contract)|Common functions should be refactored to a common base contract|2|
|[N&#x2011;05](#n05-consider-moving-msg-sender-checks-to-modifiers)|Consider moving `msg.sender` checks to modifiers|14|
|[N&#x2011;06](#n06-events-should-use-parameters-to-convey-information)|Events should use parameters to convey information|1|
|[N&#x2011;07](#n07-missing-event-for-critical-changes)|Missing event for critical changes|1|
|[N&#x2011;08](#n08-more-indexed-fields-can-be-added)|More indexed fields can be added|43|
|[N&#x2011;09](#n09-addresses-shouldn-t-be-hard-coded)|Addresses shouldn't be hard-coded|3|
|[N&#x2011;10](#n10-constants-in-comparisons-should-be-on-the-left-side)|Constants in comparisons should be on the left side|18|
|[N&#x2011;11](#n11-prefix-boolean-variables-with-is-or-has)|Prefix boolean variables with `is` or `has`|10|
|[N&#x2011;12](#n12-prefix-interfaces-with-capital-i)|Prefix interfaces with capital I|22|
|[N&#x2011;13](#n13-global-imports-should-be-avoided)|Global imports should be avoided|49|
|[N&#x2011;14](#n14-long-functions-should-be-refactored-into-multiple-functions)|Long functions should be refactored into multiple functions|8|
|[N&#x2011;15](#n15-use-of-floating-pragma)|Use of floating pragma|1|
|[N&#x2011;16](#n16-non-interface-files-should-use-fixed-compiler-versions)|Non-interface files should use fixed compiler versions|1|
|[N&#x2011;17](#n17-use-a-more-recent-version-of-solidity)|Use a more recent version of solidity|29|
|[N&#x2011;18](#n18-redundant-double-casts)|Redundant double casts|1|
|[N&#x2011;19](#n19-style-guide-maximum-suggested-line-length-is-120-characters)|[Style Guide] Maximum suggested line length is 120 characters|14|
|[N&#x2011;20](#n20-style-guide-functions-should-be-grouped-according-to-their-visibility-and-ordered)|[Style Guide] Functions should be grouped according to their visibility and ordered|9|
|[N&#x2011;21](#n21-style-guide-contract-and-library-names-should-match-their-filenames)|[Style Guide] Contract and library names should match their filenames|11|
|[N&#x2011;22](#n22-style-guide-inconsistent-struct-naming)|[Style Guide] Inconsistent struct naming|2|
|[N&#x2011;23](#n23-style-guide-underscore-prefix-for-non-external-functions)|[Style Guide] Underscore Prefix for Non-external Functions|2|
|[N&#x2011;24](#n24-style-guide-underscore-prefix-for-non-external-variables)|[Style Guide] Underscore Prefix for Non-external Variables|4|
|[N&#x2011;25](#n25-style-guide-incorrect-arrangement-of-contract-body-elements)|[Style Guide] Incorrect arrangement of contract body elements|8|
|[N&#x2011;26](#n26-unresolved-todos-in-comments)|Unresolved `TODOs` in comments|1|
|[N&#x2011;27](#n27-consider-using-delete-rather-than-assigning-zero-false-to-clear-values)|Consider using `delete` rather than assigning zero/false to clear values|5|
|[N&#x2011;28](#n28-use-immutable-for-expressions-rather-than-constant)|Use `immutable` for expressions rather than `constant`|1|
|[N&#x2011;29](#n29-use-typex-max-instead-of-constant-formulas-like-2-n)|Use `type(X).max` instead of constant formulas like `2**n`|1|
|[N&#x2011;30](#n30-missing-checks-for-address0-in-the-function)|Missing checks for address(0) in the function|76|
| | |378|

## Low Risk Issues

---

### [L&#x2011;01] Some tokens may revert when large transfers are made
Tokens such as COMP or UNI will revert when an address' balance reaches [`type(uint96).max`](https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/contracts/Governance/Comp.sol#L238).

Ensure that the calls below can be broken up into smaller batches if necessary.

*Total instances: 1*

```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

181:         asset.safeTransferFrom(msg.sender, address(this), amount);
```
*GitHub: [181](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L181-L181)*
### [L&#x2011;02] Some tokens may revert when zero value transfers are made
Despite the fact that EIP-20 states that zero-value transfers must be accepted, some tokens, such as LEND, will revert if this is attempted, which may cause transactions that involve other tokens (such as batch operations) to fully revert.

Consider skipping the transfer if the amount is zero, which will also save gas.

*Total instances: 2*

```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

181:         asset.safeTransferFrom(msg.sender, address(this), amount);
```
*GitHub: [181](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L181-L181)*
```solidity
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

32:         bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas);
```
*GitHub: [32](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L32-L32)*
### [L&#x2011;03] Critical functions should be controlled by time locks
It is a good practice to give time for users to react and adjust to critical changes. A timelock provides more guarantees and reduces the level of trust required, thus decreasing risk for users. It also indicates that the project is legitimate (less risk of a malicious owner making a sandwich attack on a user).

*Total instances: 5*

```solidity
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

117:     function updatePauserAddress(address pauserAddress_) external onlyPauser {

140:     function renounceTssAddressUpdater() external onlyTssUpdater {

151:     function pause() external onlyPauser {

159:     function unpause() external onlyPauser {
```
*GitHub: [117](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117-L117), [140](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L140-L140), [151](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L151-L151), [159](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L159-L159)*
```solidity
// File: contracts/evm/tools/ZetaInteractor.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```
*GitHub: [54](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)*
### [L&#x2011;04] Empty `receive()`/`fallback()` function
If the intention is for Ether sent by a caller to be used for an actual purpose (i.e. the function is not just a WETH `withdraw()` handler), the function should call another function (e.g. call `weth.deposit()` and use the token on the caller's behalf) or at least emit an event to track that funds were sent directly to it.

*Total instances: 3*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

101:     receive() external payable {}
```
*GitHub: [101](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101-L101)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

66:     receive() external payable {}
```
*GitHub: [66](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66-L66)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

72:     receive() external payable {}
```
*GitHub: [72](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72-L72)*
### [L&#x2011;05] Missing gas limit for external call
There is no specified limit on the amount of gas used, allowing the recipient to consume all remaining gas, potentially causing a revert. Hence, when invoking an external contract, it is advisable to provide an explicit gas limit.

*Total instances: 3*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

//@audit: getEthFromZeta
178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```
*GitHub: [178](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178-L178)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

//@audit: getEthFromZeta
152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```
*GitHub: [152](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152-L152)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

//@audit: send
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```
*GitHub: [96](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96-L96)*
### [L&#x2011;06] Lack of contract existence checks before low-level calls
Low-level calls return success even when there is no code located at the specified address. Alongside the zero-address checks, introduce an additional verification step to ensure that `<address>.code.length > 0`.

*Total instances: 3*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

//@audit: destinationAddress
178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```
*GitHub: [178](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178-L178)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

//@audit: destinationAddress
152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```
*GitHub: [152](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152-L152)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

//@audit: input
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```
*GitHub: [96](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96-L96)*
### [L&#x2011;07] Unsafe solidity low-level call can cause gas grief attack
Using the low-level calls of a solidity address can leave the contract open to gas grief attacks. These attacks occur when the called contract returns a large amount of data. So when calling an external contract, it is necessary to check the length of the return data before reading/copying it (using `returndatasize())`.

*Total instances: 3*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```
*GitHub: [178](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178-L178)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```
*GitHub: [152](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152-L152)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```
*GitHub: [96](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96-L96)*
### [L&#x2011;08] Owner can renounce Ownership
Typically, the contract’s owner is the account that deploys the contract. As a result, the owner is able to perform certain privileged activities.

The Openzeppelin’s Ownable used in this project contract implements renounceOwnership. This can represent a certain risk if the ownership is renounced for any other reason than by design. Renouncing ownership will leave the contract without an owner, thereby removing any functionality that is only available to the owner.

*Total instances: 1*

```solidity
// File: contracts/evm/tools/ZetaInteractor.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

9: abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```
*GitHub: [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9-L9)*
### [L&#x2011;09] Using `>`/`>=` without specifying an upper bound in version pragma is unsafe
There will be breaking changes in future versions of solidity, and at that point your code will no longer be compatible. While you may have the specific version to use in a configuration file, others that include your source files may not.

*Total instances: 2*

```solidity
// File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol

14: pragma solidity >=0.8.0;
```
*GitHub: [14](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14-L14)*
```solidity
// File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

14: pragma solidity >=0.8.0;
```
*GitHub: [14](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L14-L14)*
### [L&#x2011;10] Consider implementing two-step procedure for updating protocol addresses
A copy-paste error or a typo may end up bricking protocol functionality, or sending tokens to an address with no known private key. Consider implementing a two-step procedure for updating protocol addresses, where the recipient is set as pending, and must 'accept' the assignment by making an affirmative call. A straight forward way of doing this would be to have the target contracts implement [EIP-165](https://eips.ethereum.org/EIPS/eip-165), and to have the 'set' functions ensure that the recipient is of the right interface type.

*Total instances: 1*

```solidity
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

//@audit: pauserAddress_
117:     function updatePauserAddress(address pauserAddress_) external onlyPauser {
118:         if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
119: 
120:         pauserAddress = pauserAddress_;
121: 
122:         emit PauserAddressUpdated(msg.sender, pauserAddress_);
123:     }
```
*GitHub: [117](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117-L123)*
### [L&#x2011;11] Critical protocol parameter should have limits
Input validation on key function parameters is a best-practice. Not applying sanity/threshold checks will allow incorrect values to be set accidentally/maliciously and may significantly affect the security/functionality of the protocol.

*Total instances: 3*

```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

//@audit: maxSupply_
31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
32:         maxSupply = maxSupply_;
33:         emit MaxSupplyUpdated(msg.sender, maxSupply_);
34:     }
```
*GitHub: [31](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31-L34)*
```solidity
// File: contracts/zevm/interfaces/IUniswapV2Router01.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol

//@audit: amountADesired, amountBDesired, amountAMin, amountBMin
9:     function addLiquidity(
10:         address tokenA,
11:         address tokenB,
12:         uint amountADesired,
13:         uint amountBDesired,
14:         uint amountAMin,
15:         uint amountBMin,
16:         address to,
17:         uint deadline
18:     ) external returns (uint amountA, uint amountB, uint liquidity);

//@audit: amountTokenDesired, amountTokenMin, amountETHMin
20:     function addLiquidityETH(
21:         address token,
22:         uint amountTokenDesired,
23:         uint amountTokenMin,
24:         uint amountETHMin,
25:         address to,
26:         uint deadline
27:     ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
```
*GitHub: [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18), [20](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27)*
### [L&#x2011;12] Missing checks for address(0) in the constructor
Constructors often take address parameters to initialize important components of a contract, such as owner or linked contracts. However, without a checking, there's a risk that an address parameter could be mistakenly set to the zero address (0x0). This could be due to an error or oversight during contract deployment. A zero address in a crucial role can cause serious issues, as it cannot perform actions like a normal address, and any funds sent to it will be irretrievable. It's therefore crucial to include a zero address check in constructors to prevent such potential problems. If a zero address is detected, the constructor should revert the transaction.

*Total instances: 3*

```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

//@audit: systemContractAddress_
60:     constructor(
61:         string memory name_,
62:         string memory symbol_,
63:         uint8 decimals_,
64:         uint256 chainid_,
65:         CoinType coinType_,
66:         uint256 gasLimit_,
67:         address systemContractAddress_
68:     ) {
```
*GitHub: [60](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L68)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

//@audit: wzeta_
79:     constructor(address wzeta_) {
```
*GitHub: [79](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L79)*
```solidity
// File: contracts/evm/Zeta.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol

//@audit: creator
10:     constructor(address creator, uint256 initialSupply) {
```
*GitHub: [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L10)*
### [L&#x2011;13] `constructor` function lacks parameter validation
Constructor play a critical role in contracts by setting important initial states when the contract is first deployed before the system starts. The parameters passed to the constructor functions directly affect the behavior of the contract / protocol. If incorrect parameters are provided, the system may fail to run, behave abnormally, be unstable, or lack security.

Therefore, it's crucial to carefully check each parameter in the constructor. If an exception is found, the transaction should be rolled back. 

*Total instances: 9*

```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

//@audit: not checked: name_, symbol_, decimals_, chainid_, coinType_, gasLimit_, systemContractAddress_
60:     constructor(
61:         string memory name_,
62:         string memory symbol_,
63:         uint8 decimals_,
64:         uint256 chainid_,
65:         CoinType coinType_,
66:         uint256 gasLimit_,
67:         address systemContractAddress_
68:     ) {
```
*GitHub: [60](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L68)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

//@audit: not checked: zetaToken_, zetaPoolFee_, tokenPoolFee_
71:     constructor(
72:         address zetaToken_,
73:         address pancakeV3Router_,
74:         address uniswapV3Factory_,
75:         address WETH9Address_,
76:         uint24 zetaPoolFee_,
77:         uint24 tokenPoolFee_
78:     ) {
```
*GitHub: [71](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L78)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

//@audit: not checked: zetaToken_
45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
```
*GitHub: [45](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L45)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

//@audit: not checked: zetaToken_, zetaPoolFee_, tokenPoolFee_
42:     constructor(
43:         address zetaToken_,
44:         address uniswapV3Router_,
45:         address uniswapV3Factory_,
46:         address WETH9Address_,
47:         uint24 zetaPoolFee_,
48:         uint24 tokenPoolFee_
49:     ) {
```
*GitHub: [42](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L49)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

//@audit: not checked: TSSAddress_, TSSAddressUpdater_, zetaFee_, zetaMaxFee_, zeta_
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
```
*GitHub: [68](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L68)*
```solidity
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

//@audit: not checked: zetaToken_
74:     constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
```
*GitHub: [74](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74-L74)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

//@audit: not checked: wzeta_, uniswapv2Factory_, uniswapv2Router02_
51:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
```
*GitHub: [51](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51-L51)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

//@audit: not checked: wzeta_
79:     constructor(address wzeta_) {
```
*GitHub: [79](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L79)*
```solidity
// File: contracts/evm/Zeta.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol

//@audit: not checked: creator, initialSupply
10:     constructor(address creator, uint256 initialSupply) {
```
*GitHub: [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L10)*
### [L&#x2011;14] State variables not capped at reasonable values
Consider adding minimum/maximum value checks to ensure that the state variables below can never be used to excessively harm users, including via griefing.

*Total instances: 4*

```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

280:         GAS_LIMIT = gasLimit;

289:         PROTOCOL_FLAT_FEE = protocolFlatFee;
```
*GitHub: [280](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L280-L280), [289](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L289-L289)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

99:         zetaFee = zetaFee_;
```
*GitHub: [99](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L99-L99)*
```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

32:         maxSupply = maxSupply_;
```
*GitHub: [32](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L32-L32)*

## Non-critical Issues

---

### [N&#x2011;01] Avoid the use of sensitive terms
Use [alternative variants](https://www.zdnet.com/article/mysql-drops-master-slave-and-blacklist-whitelist-terminology/), e.g. allowlist/denylist instead of whitelist/blacklist.

*Total instances: 18*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

14:     error NotWhitelisted();

35:     /// @notice Mapping of whitelisted token => true/false.

36:     mapping(IERC20 => bool) public whitelisted;

40:     event Whitelisted(IERC20 indexed asset);

41:     event Unwhitelisted(IERC20 indexed asset);

141:      * @dev Whitelist asset.

144:     function whitelist(IERC20 asset) external onlyTSS {

145:         whitelisted[asset] = true;

146:         emit Whitelisted(asset);

150:      * @dev Unwhitelist asset.

153:     function unwhitelist(IERC20 asset) external onlyTSS {

154:         whitelisted[asset] = false;

155:         emit Unwhitelisted(asset);

174:         if (!whitelisted[asset]) {

175:             revert NotWhitelisted();

194:         if (!whitelisted[asset]) {

195:             revert NotWhitelisted();
```
*GitHub: [14](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14-L14), [35](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L35-L35), [36](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36-L36), [40](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41-L41), [141](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L141-L141), [144](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144-L144), [145](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L145-L145), [146](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L146-L146), [150](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L150-L150), [153](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153-L153), [154](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L154-L154), [155](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L155-L155), [174](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L174-L174), [175](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L175-L175), [194](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L194-L194), [195](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L195-L195)*
```solidity
// File: contracts/evm/interfaces/ZetaInteractorErrors.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol

8:     // @dev Thrown when try to send a message or tokens to a non whitelisted chain
```
*GitHub: [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L8-L8)*


</details>


### [N&#x2011;02] Duplicated `if`-`revert()` checks should be refactored
The compiler will inline the function, which will avoid `JUMP` instructions usually associated with functions.

*Total instances: 16*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

69:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

200:         if (account == address(0)) revert ZeroAddress();
```
*GitHub: [69](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69-L69), [200](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L200-L200)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

156:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

191:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```
*GitHub: [156](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L156-L156), [191](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191-L191)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

141:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

173:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```
*GitHub: [141](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L141-L141), [173](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173-L173)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

129:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

165:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```
*GitHub: [129](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L129-L129), [165](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165-L165)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

122:         if (TSSAddress == address(0)) {
123:             revert ZeroAddress();
124:         }

171:         if (paused) {
172:             revert IsPaused();
173:         }

194:         if (!whitelisted[asset]) {
195:             revert NotWhitelisted();
196:         }
```
*GitHub: [122](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L122-L124), [171](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L171-L173), [194](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L194-L196)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

100:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

131:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```
*GitHub: [100](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L100-L100), [131](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131-L131)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

74:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

169:         if (addr == address(0)) revert ZeroAddress();
```
*GitHub: [74](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74-L74), [169](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L169-L169)*
```solidity
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

61:         if (!success) revert ZetaTransferError();
```
*GitHub: [61](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L61-L61)*


</details>


### [N&#x2011;03] Multiple definition of the same `constant`/`immutable`
Consider defining in only one contract so that values cannot become out of sync when only one location is updated.

A cheap way to store constants in a single location is to create an `internal constant` in a `library`.

If the variable is a local cache of another contract's value, consider making the cache variable internal or private, which will require external users to query the contract with the source of truth, so that callers don't get out of sync.

*Total instances: 7*

```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

//@audit: also in contracts/zevm/SystemContract.sol
22:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```
*GitHub: [22](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22-L22)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

//@audit: also in contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol, contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol, contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
58:     uint256 internal constant MAX_DEADLINE = 200;

//@audit: also in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
60:     uint24 public immutable zetaPoolFee;

//@audit: also in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
61:     uint24 public immutable tokenPoolFee;

//@audit: also in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
63:     address public immutable WETH9Address;

//@audit: also in contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol, contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol, contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol, contracts/evm/ZetaConnector.base.sol
64:     address public immutable zetaToken;
//@audit: also in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
67:     IUniswapV3Factory public immutable uniswapV3Factory;
```
*GitHub: [58](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58-L58), [60](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L60-L60), [61](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L61-L61), [63](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L63-L63), [64](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L64-L64), [67](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L67-L67)*
### [N&#x2011;04] Common functions should be refactored to a common base contract
The functions below have the same implementation as is seen in other files. The functions should be refactored into functions of a common base contract.

*Total instances: 2*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

//@audit: also in contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol, contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
94:     modifier nonReentrant() {

//@audit: also in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
209:     function hasZetaLiquidity() external view override returns (bool) {
```
*GitHub: [94](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94-L94), [209](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209-L209)*
### [N&#x2011;05] Consider moving `msg.sender` checks to modifiers
If some functions are only allowed to be called by some specific users, consider using a modifier instead of checking with a require statement, especially if this check is done in multiple functions.

*Total instances: 14*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

69:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();

258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
259:             revert GasFeeTransferFailed();
260:         }
```
*GitHub: [69](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69-L69), [226](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226-L226), [258](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258-L260)*
```solidity
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

129:         if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);
```
*GitHub: [129](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L129-L129)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

52:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

74:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

124:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

135:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

146:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

157:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

168:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```
*GitHub: [52](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52-L52), [74](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74-L74), [124](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124-L124), [135](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135-L135), [146](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146-L146), [157](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157-L157), [168](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168-L168)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

85:         if (msg.sender != wzeta) revert OnlyWZETA();

115:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
```
*GitHub: [85](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L85-L85), [115](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115-L115)*
```solidity
// File: contracts/evm/tools/ZetaInteractor.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

44:         if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
```
*GitHub: [44](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L44-L44)*


</details>


### [N&#x2011;06] Events should use parameters to convey information
For example, rather than using `event Paused()` and `event Unpaused()`, use `event PauseState(address indexed whoChangedIt, bool wasPaused, bool isNowPaused)`

*Total instances: 1*

```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

//@audit: opposite event: Unwhitelisted
40:     event Whitelisted(IERC20 indexed asset);
```
*GitHub: [40](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40-L40)*
### [N&#x2011;07] Missing event for critical changes
Events should be emitted when important changes are made to the contracts.

*Total instances: 1*

```solidity
// File: contracts/evm/tools/ZetaInteractor.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```
*GitHub: [54](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)*
### [N&#x2011;08] More indexed fields can be added
You can add the attribute indexed to up to three parameters which adds them to a special data structure known as ["topics"](https://docs.soliditylang.org/en/latest/abi-spec.html#abi-events) instead of the data part of the log.

Topics allow you to search for events, for example when filtering a sequence of blocks for certain events.

*Total instances: 43*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

38:     event Paused(address sender);

39:     event Unpaused(address sender);

40:     event Whitelisted(IERC20 indexed asset);

41:     event Unwhitelisted(IERC20 indexed asset);

42:     event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);

43:     event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);

44:     event RenouncedTSSUpdater(address TSSAddressUpdater_);

45:     event UpdatedTSSAddress(address TSSAddress_);

46:     event UpdatedZetaFee(uint256 zetaFee_);
```
*GitHub: [38](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38-L38), [39](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39-L39), [40](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46-L46)*
```solidity
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

34:     event ZetaSent(
35:         address sourceTxOriginAddress,
36:         address indexed zetaTxSenderAddress,
37:         uint256 indexed destinationChainId,
38:         bytes destinationAddress,
39:         uint256 zetaValueAndGas,
40:         uint256 destinationGasLimit,
41:         bytes message,
42:         bytes zetaParams
43:     );

54:     event ZetaReverted(
55:         address zetaTxSenderAddress,
56:         uint256 sourceChainId,
57:         uint256 indexed destinationChainId,
58:         bytes destinationAddress,
59:         uint256 remainingZetaValue,
60:         bytes message,
61:         bytes32 indexed internalSendHash
62:     );

64:     event TSSAddressUpdated(address callerAddress, address newTssAddress);

66:     event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

68:     event PauserAddressUpdated(address callerAddress, address newTssAddress);
```
*GitHub: [34](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34-L43), [54](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L62), [64](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64-L64), [66](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66-L66), [68](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68-L68)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

67:     event ZetaSent(
68:         address sourceTxOriginAddress,
69:         address indexed zetaTxSenderAddress,
70:         uint256 indexed destinationChainId,
71:         bytes destinationAddress,
72:         uint256 zetaValueAndGas,
73:         uint256 destinationGasLimit,
74:         bytes message,
75:         bytes zetaParams
76:     );

77:     event SetWZETA(address wzeta_);
```
*GitHub: [67](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L76), [77](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77-L77)*
```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

18:     event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
```
*GitHub: [18](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18-L18)*
```solidity
// File: contracts/zevm/WZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol

8:     event Approval(address indexed src, address indexed guy, uint wad);

9:     event Transfer(address indexed src, address indexed dst, uint wad);

10:     event Deposit(address indexed dst, uint wad);

11:     event Withdrawal(address indexed src, uint wad);
```
*GitHub: [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L8-L8), [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L9-L9), [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L10-L10), [11](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L11-L11)*
```solidity
// File: contracts/evm/interfaces/ZetaInterfaces.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol

78:     event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);

79:     event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

80:     event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);

81:     event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
```
*GitHub: [78](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78-L78), [79](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79-L79), [80](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L80-L80), [81](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81-L81)*
```solidity
// File: contracts/zevm/Interfaces.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol

40:     event Transfer(address indexed from, address indexed to, uint256 value);

41:     event Approval(address indexed owner, address indexed spender, uint256 value);

42:     event Deposit(bytes from, address indexed to, uint256 value);

43:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);

44:     event UpdatedSystemContract(address systemContract);

45:     event UpdatedGasLimit(uint256 gasLimit);

46:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```
*GitHub: [40](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40-L40), [41](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L41-L41), [42](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42-L42), [43](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43-L43), [44](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44-L44), [45](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45-L45), [46](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L46-L46)*
```solidity
// File: contracts/zevm/interfaces/IWZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol

5:     event Approval(address indexed owner, address indexed spender, uint value);

6:     event Transfer(address indexed from, address indexed to, uint value);

7:     event Deposit(address indexed dst, uint wad);

8:     event Withdrawal(address indexed src, uint wad);
```
*GitHub: [5](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8-L8)*
```solidity
// File: contracts/zevm/interfaces/IZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol

31:     event Transfer(address indexed from, address indexed to, uint256 value);

32:     event Approval(address indexed owner, address indexed spender, uint256 value);

33:     event Deposit(bytes from, address indexed to, uint256 value);

34:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

35:     event UpdatedSystemContract(address systemContract);

36:     event UpdatedGasLimit(uint256 gasLimit);

37:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```
*GitHub: [31](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31-L31), [32](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32-L32), [33](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33-L33), [34](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34-L34), [35](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35-L35), [36](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36-L36), [37](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37-L37)*


</details>


### [N&#x2011;09] Addresses shouldn't be hard-coded
It is often better to declare addresses as `constant` or `immutable` which can be assigned in constructor. This allows the code to remain the same across deployments on different networks, and avoids recompilation when addresses need to change.

*Total instances: 3*

```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

22:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```
*GitHub: [22](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22-L22)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

31:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```
*GitHub: [31](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L31-L31)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

63:     address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
```
*GitHub: [63](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63-L63)*
### [N&#x2011;10] Constants in comparisons should be on the left side
This is useful to avoid doing some [typo bugs](https://www.moserware.com/2008/01/constants-on-left-are-better-but-this.html).

*Total instances: 18*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

242:         if (gasPrice == 0) {
```
*GitHub: [242](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L242-L242)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

108:         if (msg.value == 0) revert InputCantBeZero();

133:         if (inputTokenAmount == 0) revert InputCantBeZero();

157:         if (zetaTokenAmount == 0) revert InputCantBeZero();

191:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```
*GitHub: [108](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L108-L108), [133](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L133-L133), [157](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L157-L157), [191](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191-L191)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

79:         if (msg.value == 0) revert InputCantBeZero();

106:         if (inputTokenAmount == 0) revert InputCantBeZero();

142:         if (zetaTokenAmount == 0) revert InputCantBeZero();

173:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```
*GitHub: [79](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L79-L79), [106](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L106-L106), [142](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L142-L142), [173](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173-L173)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

79:         if (msg.value == 0) revert InputCantBeZero();

105:         if (inputTokenAmount == 0) revert InputCantBeZero();

130:         if (zetaTokenAmount == 0) revert InputCantBeZero();

165:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```
*GitHub: [79](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79-L79), [105](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105-L105), [130](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130-L130), [165](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165-L165)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

93:         if (zetaFee_ == 0) {
```
*GitHub: [93](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L93-L93)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

39:         if (msg.value == 0) revert InputCantBeZero();

65:         if (inputTokenAmount == 0) revert InputCantBeZero();

101:         if (zetaTokenAmount == 0) revert InputCantBeZero();

131:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```
*GitHub: [39](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L39-L39), [65](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L65-L65), [101](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L101-L101), [131](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131-L131)*


</details>


### [N&#x2011;11] Prefix boolean variables with `is` or `has`
This helps to make their purpose clear (e.g., `isOwner`, `hasAccess`).

*Total instances: 10*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

69:     bool internal _locked;

178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```
*GitHub: [69](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L69-L69), [178](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178-L178)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

43:     bool internal _locked;
```
*GitHub: [43](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L43-L43)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

40:     bool internal _locked;

152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```
*GitHub: [40](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L40-L40), [152](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152-L152)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

24:     bool public paused;
```
*GitHub: [24](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L24-L24)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```
*GitHub: [96](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96-L96)*
```solidity
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

32:         bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas);

60:         bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);

86:         bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
```
*GitHub: [32](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L32-L32), [60](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L60-L60), [86](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L86-L86)*
### [N&#x2011;12] Prefix interfaces with capital I
It's a good practice used, for example, by [OpenZeppelin contracts](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/GUIDELINES.md).

*Total instances: 22*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

8: interface ZRC20Errors {
```
*GitHub: [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8-L8)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {
```
*GitHub: [12](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20-L20)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

12: interface ZetaTokenConsumerTridentErrors {

20: interface WETH9 {
```
*GitHub: [12](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20-L20)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {
```
*GitHub: [12](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12), [20](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

10: interface ZetaTokenConsumerUniV2Errors {
```
*GitHub: [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

10: interface SystemContractErrors {
```
*GitHub: [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10-L10)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

4: interface ZetaInterfaces {

49: interface WZETA {
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L4), [49](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49)*
```solidity
// File: contracts/evm/interfaces/ZetaInterfaces.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol

4: interface ZetaInterfaces {

49: interface ZetaConnector {

56: interface ZetaReceiver {

77: interface ZetaTokenConsumer {

108: interface ZetaCommonErrors {
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4-L4), [49](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49-L49), [56](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L56), [77](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77-L77), [108](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108-L108)*
```solidity
// File: contracts/evm/interfaces/ZetaErrors.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol

7: interface ZetaErrors {
```
*GitHub: [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7-L7)*
```solidity
// File: contracts/evm/interfaces/ConnectorErrors.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol

7: interface ConnectorErrors {
```
*GitHub: [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7-L7)*
```solidity
// File: contracts/zevm/interfaces/zContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol

10: interface zContract {
```
*GitHub: [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10-L10)*
```solidity
// File: contracts/evm/interfaces/ZetaInteractorErrors.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol

7: interface ZetaInteractorErrors {
```
*GitHub: [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7-L7)*
```solidity
// File: contracts/evm/interfaces/ZetaNonEthInterface.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol

9: interface ZetaNonEthInterface is IERC20 {
```
*GitHub: [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9-L9)*
```solidity
// File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

16: interface ConcentratedLiquidityPoolFactory {
```
*GitHub: [16](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16-L16)*


</details>


### [N&#x2011;13] Global imports should be avoided
According to solidity documentation:

> `import "filename";` This statement imports all global symbols from "filename" (and symbols imported there) into the current global scope (different than in ES6 but backwards-compatible for Solidity). This form is not recommended for use, because it unpredictably pollutes the namespace. If you add new top-level items inside “filename”, they automatically appear in all files that import like this from “filename”. It is better to import specific symbols explicitly.

*Total instances: 49*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

3: import "./Interfaces.sol";
```
*GitHub: [3](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L3-L3)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6: import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

7: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";

8: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

10: import "../interfaces/ZetaInterfaces.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L4-L4), [5](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L8-L8), [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L10-L10)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6: import "@uniswap/v3-periphery/contracts/interfaces/IQuoter.sol";

8: import "../interfaces/ZetaInterfaces.sol";

9: import "./interfaces/TridentConcentratedLiquidityPoolFactory.sol";

10: import "./interfaces/TridentIPoolRouter.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L4-L4), [5](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L6-L6), [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L8-L8), [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L9-L9), [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L10-L10)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6: import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

7: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";

8: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

10: import "../interfaces/ZetaInterfaces.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L4-L4), [5](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L8-L8), [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L10-L10)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

5: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

6: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

7: import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
```
*GitHub: [5](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L7-L7)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6: import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

8: import "../interfaces/ZetaInterfaces.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L4-L4), [5](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L5-L5), [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L6-L6), [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L8-L8)*
```solidity
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

5: import "@openzeppelin/contracts/security/Pausable.sol";

7: import "./interfaces/ConnectorErrors.sol";

8: import "./interfaces/ZetaInterfaces.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L4-L4), [5](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L5-L5), [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L8-L8)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

4: import "./interfaces/zContract.sol";

5: import "./interfaces/IZRC20.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L4-L4), [5](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L5-L5)*
```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

6: import "./ZetaConnector.base.sol";

7: import "./interfaces/ZetaInterfaces.sol";

8: import "./interfaces/ZetaNonEthInterface.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L4-L4), [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L8-L8)*
```solidity
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

6: import "./interfaces/ConnectorErrors.sol";

7: import "./ZetaConnector.base.sol";

8: import "./interfaces/ZetaInterfaces.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L4-L4), [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L7-L7), [8](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L8-L8)*
```solidity
// File: contracts/evm/tools/ZetaInteractor.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

4: import "@openzeppelin/contracts/access/Ownable2Step.sol";

6: import "../interfaces/ZetaInterfaces.sol";

7: import "../interfaces/ZetaInteractorErrors.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L4-L4), [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L6-L6), [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L7-L7)*
```solidity
// File: contracts/evm/Zeta.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol

4: import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L4-L4)*
```solidity
// File: contracts/zevm/interfaces/IUniswapV2Router02.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol

4: import "./IUniswapV2Router01.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L4-L4)*
```solidity
// File: contracts/zevm/Uniswap.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol

4: import "@uniswap/v2-core/contracts/UniswapV2Pair.sol";

5: import "@uniswap/v2-core/contracts/UniswapV2Factory.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L4-L4), [5](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L5-L5)*
```solidity
// File: contracts/evm/interfaces/ZetaNonEthInterface.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol

4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L4-L4)*
```solidity
// File: contracts/zevm/UniswapPeriphery.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol

4: import "@uniswap/v2-periphery/contracts/UniswapV2Router02.sol";
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L4-L4)*


</details>


### [N&#x2011;14] Long functions should be refactored into multiple functions
Consider splitting long functions into multiple, smaller functions to improve the code readability.

*Total instances: 8*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

//@audit: 31 lines
151:     function getEthFromZeta(
152:         address destinationAddress,
153:         uint256 minAmountOut,
154:         uint256 zetaTokenAmount
155:     ) external override returns (uint256) {
```
*GitHub: [151](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L155)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

//@audit: 35 lines
99:     function getZetaFromToken(
100:         address destinationAddress,
101:         uint256 minAmountOut,
102:         address inputToken,
103:         uint256 inputTokenAmount
104:     ) external override returns (uint256) {

//@audit: 35 lines
166:     function getTokenFromZeta(
167:         address destinationAddress,
168:         uint256 minAmountOut,
169:         address outputToken,
170:         uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {
```
*GitHub: [99](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L104), [166](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L171)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

//@audit: 32 lines
124:     function getEthFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         uint256 zetaTokenAmount
128:     ) external override returns (uint256) {
```
*GitHub: [124](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L128)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

//@audit: 35 lines
58:     function getZetaFromToken(
59:         address destinationAddress,
60:         uint256 minAmountOut,
61:         address inputToken,
62:         uint256 inputTokenAmount
63:     ) external override returns (uint256) {

//@audit: 36 lines
124:     function getTokenFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         address outputToken,
128:         uint256 zetaTokenAmount
129:     ) external override returns (uint256) {
```
*GitHub: [58](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L63), [124](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L129)*
```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

//@audit: 35 lines
87:     function onRevert(
88:         address zetaTxSenderAddress,
89:         uint256 sourceChainId,
90:         bytes calldata destinationAddress,
91:         uint256 destinationChainId,
92:         uint256 remainingZetaValue,
93:         bytes calldata message,
94:         bytes32 internalSendHash
95:     ) external override whenNotPaused onlyTssAddress {
```
*GitHub: [87](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L95)*
```solidity
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

//@audit: 34 lines
77:     function onRevert(
78:         address zetaTxSenderAddress,
79:         uint256 sourceChainId,
80:         bytes calldata destinationAddress,
81:         uint256 destinationChainId,
82:         uint256 remainingZetaValue,
83:         bytes calldata message,
84:         bytes32 internalSendHash
85:     ) external override whenNotPaused onlyTssAddress {
```
*GitHub: [77](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L85)*
### [N&#x2011;15] Use of floating pragma
Contracts should be deployed using the same compiler version and flags with which they have undergone thorough testing. Setting a fixed pragma version helps ensure that contracts are not inadvertently deployed using an outdated compiler version. Such outdated versions could potentially introduce bugs that negatively impact the contract system.

[SWC-103](https://swcregistry.io/docs/SWC-103), [Consensys Development Recommendations](https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/locking-pragmas/)

*Total instances: 1*

```solidity
// File: contracts/zevm/WZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol

1: pragma solidity ^0.4.18;
```
*GitHub: [1](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1-L1)*
### [N&#x2011;16] Non-interface files should use fixed compiler versions
To prevent the actual contracts being deployed from behaving differently depending on the compiler version, it is recommended to use fixed solidity versions for contracts and libraries.

Although we can configure a specific version through config (like hardhat, forge config files), it is recommended to set the fixed version in the solidity pragma directly before deploying to the mainnet.

*Total instances: 1*

```solidity
// File: contracts/zevm/WZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol

1: pragma solidity ^0.4.18;
```
*GitHub: [1](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1-L1)*
### [N&#x2011;17] Use a more recent version of solidity
Upgrading to the latest solidity version can optimize gas usage, take advantage of new features and improve overall contract efficiency. Where possible, based on compatibility requirements, it is recommended to use newer/latest solidity version to take advantage of the latest optimizations and features.

*Total instances: 29*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L2-L2)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L2-L2)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L2-L2)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L2-L2)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

3: pragma solidity 0.8.7;
```
*GitHub: [3](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L3-L3)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L2-L2)*
```solidity
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L2-L2)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L2-L2)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L2-L2)*
```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L2-L2)*
```solidity
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L2-L2)*
```solidity
// File: contracts/zevm/WZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol

1: pragma solidity ^0.4.18;
```
*GitHub: [1](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1-L1)*
```solidity
// File: contracts/evm/tools/ZetaInteractor.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L2-L2)*
```solidity
// File: contracts/evm/interfaces/ZetaInterfaces.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2-L2)*
```solidity
// File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol

14: pragma solidity >=0.8.0;
```
*GitHub: [14](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14-L14)*
```solidity
// File: contracts/zevm/Interfaces.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L2-L2)*
```solidity
// File: contracts/evm/interfaces/ZetaErrors.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L2-L2)*
```solidity
// File: contracts/evm/interfaces/ConnectorErrors.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L2-L2)*
```solidity
// File: contracts/zevm/interfaces/zContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L2-L2)*
```solidity
// File: contracts/zevm/interfaces/IWZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L2-L2)*
```solidity
// File: contracts/evm/Zeta.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L2-L2)*
```solidity
// File: contracts/evm/interfaces/ZetaInteractorErrors.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L2-L2)*
```solidity
// File: contracts/zevm/interfaces/IUniswapV2Router02.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L2-L2)*
```solidity
// File: contracts/zevm/Uniswap.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol

2: pragma solidity 0.5.16;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L2-L2)*
```solidity
// File: contracts/evm/interfaces/ZetaNonEthInterface.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2-L2)*
```solidity
// File: contracts/zevm/interfaces/IZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L2-L2)*
```solidity
// File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

14: pragma solidity >=0.8.0;
```
*GitHub: [14](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L14-L14)*
```solidity
// File: contracts/zevm/UniswapPeriphery.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol

2: pragma solidity 0.6.6;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L2-L2)*
```solidity
// File: contracts/zevm/interfaces/IUniswapV2Router01.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol

2: pragma solidity 0.8.7;
```
*GitHub: [2](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L2-L2)*


</details>


### [N&#x2011;18] Redundant double casts


*Total instances: 1*

```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

197:         IERC20(asset).safeTransfer(recipient, amount);
```
*GitHub: [197](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L197-L197)*
### [N&#x2011;19] [Style Guide] Maximum suggested line length is 120 characters
[Solidity Style Guide > Maximum Line Length](https://docs.soliditylang.org/en/latest/style-guide.html#maximum-line-length)

*Total instances: 14*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

234:      * @return returns the ZRC20 address for gas on the same chain of this ZRC20, and calculates the gas fee for withdraw()

250:      * @dev Withraws ZRC20 tokens to external chains, this function causes cctx module to send out outbound tx to the outbound chain
```
*GitHub: [234](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L234-L234), [250](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L250-L250)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

183:         // and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount.
```
*GitHub: [183](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L183-L183)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

27:     // @dev: Map to know uniswap V2 pool of ZETA/ZRC20 given a chain id. This refer to the build in uniswap deployed at genesis.
```
*GitHub: [27](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L27-L27)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

9:         /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id

43:         /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
```
*GitHub: [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L9-L9), [43](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L43-L43)*
```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

13:  * This version is for every chain but Etherum network because in the other chains we mint and burn and in Etherum we lock and unlock
```
*GitHub: [13](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L13-L13)*
```solidity
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

13:  * This version is only for Ethereum network because in the other chains we mint and burn and in this one we lock and unlock.
```
*GitHub: [13](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L13-L13)*
```solidity
// File: contracts/evm/interfaces/ZetaInterfaces.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol

9:         /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id

43:         /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
```
*GitHub: [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L9-L9), [43](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L43-L43)*
```solidity
// File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol

18:         address tokenIn; /// @dev the input token address. If tokenIn is address(0), msg.value will be wrapped and used as input token

27:         address tokenIn; /// @dev the token address to swap-in. If tokenIn is address(0), msg.value will be wrapped and used as input token

36:         address tokenIn; /// @dev the input token address. If tokenIn is address(0), msg.value will be wrapped and used as input token

45:         address tokenIn; /// @dev the token address to swap-in. If tokenIn is address(0), msg.value will be wrapped and used as input token
```
*GitHub: [18](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L18-L18), [27](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L27-L27), [36](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L36-L36), [45](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L45-L45)*


</details>


### [N&#x2011;20] [Style Guide] Functions should be grouped according to their visibility and ordered
Functions should be grouped according to their visibility and ordered:

- constructor

- receive function (if exists)

- fallback function (if exists)

- external

- public

- internal

- private

Within a grouping, place the `view` and `pure` functions last.


[Solidity Style Guide > Order of Functions](https://docs.soliditylang.org/en/latest/style-guide.html#order-of-functions)

*Total instances: 9*

```diff
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

diff --git a/private/OriginalRIDTtw b/private/ModifiedhVwE3x
index 38dddb2..7cdf320 100644
--- a/private/OriginalRIDTtw
+++ b/private/ModifiedhVwE3x
@@ -1,24 +1,24 @@
-_msgSender (...) internal view
-_msgData (...) internal view
 constructor (...) internal
+burn (...) external
+deposit (...) external
+withdraw (...) external
+updateSystemContractAddress (...) external
+updateGasLimit (...) external
+updateProtocolFlatFee (...) external
+transfer (...) public
+approve (...) public
+transferFrom (...) public
 name (...) public view
 symbol (...) public view
 decimals (...) public view
 totalSupply (...) public view
 balanceOf (...) public view
-transfer (...) public
 allowance (...) public view
-approve (...) public
-transferFrom (...) public
-burn (...) external
+withdrawGasFee (...) public view
 _transfer (...) internal
 _mint (...) internal
 _burn (...) internal
 _approve (...) internal
-deposit (...) external
-withdrawGasFee (...) public view
-withdraw (...) external
-updateSystemContractAddress (...) external
-updateGasLimit (...) external
-updateProtocolFlatFee (...) external
+_msgSender (...) internal view
+_msgData (...) internal view

```
[contracts/zevm/ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol)
```diff
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

diff --git a/private/Original18zy8A b/private/Modified7UoQJB
index 1aaf0ed..be6e10e 100644
--- a/private/Original18zy8A
+++ b/private/Modified7UoQJB
@@ -1,8 +1,8 @@
 constructor (...) internal
 receive (...) external payable
-getZetaFromEth (...) external payable
 getZetaFromToken (...) external
 getEthFromZeta (...) external
 getTokenFromZeta (...) external
+getZetaFromEth (...) external payable
 hasZetaLiquidity (...) external view

```
[contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol)
```diff
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

diff --git a/private/OriginalKnulre b/private/ModifiedbILQAw
index a1188b7..bab8fb9 100644
--- a/private/OriginalKnulre
+++ b/private/ModifiedbILQAw
@@ -1,9 +1,9 @@
 constructor (...) internal
 receive (...) external payable
-getPair (...) internal pure
-getZetaFromEth (...) external payable
 getZetaFromToken (...) external
 getEthFromZeta (...) external
 getTokenFromZeta (...) external
+getZetaFromEth (...) external payable
 hasZetaLiquidity (...) external view
+getPair (...) internal pure

```
[contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol)
```diff
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

diff --git a/private/OriginalUYHo3K b/private/Modified0jRPtm
index 1aaf0ed..be6e10e 100644
--- a/private/OriginalUYHo3K
+++ b/private/Modified0jRPtm
@@ -1,8 +1,8 @@
 constructor (...) internal
 receive (...) external payable
-getZetaFromEth (...) external payable
 getZetaFromToken (...) external
 getEthFromZeta (...) external
 getTokenFromZeta (...) external
+getZetaFromEth (...) external payable
 hasZetaLiquidity (...) external view

```
[contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol)
```diff
// File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

diff --git a/private/OriginalMJLqlz b/private/Modified1DSF1C
index a1d54cd..8516d4f 100644
--- a/private/OriginalMJLqlz
+++ b/private/Modified1DSF1C
@@ -1,7 +1,7 @@
 constructor (...) internal
-getZetaFromEth (...) external payable
 getZetaFromToken (...) external
 getEthFromZeta (...) external
 getTokenFromZeta (...) external
+getZetaFromEth (...) external payable
 hasZetaLiquidity (...) external view

```
[contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol)
```diff
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

diff --git a/private/Original75r1K4 b/private/Modifiedl4sY6I
index 3eb6e20..9fcc65e 100644
--- a/private/Original75r1K4
+++ b/private/Modifiedl4sY6I
@@ -1,10 +1,10 @@
 constructor (...) internal
 depositAndCall (...) external
-sortTokens (...) internal pure
-uniswapv2PairFor (...) public pure
 setGasPrice (...) external
 setGasCoinZRC20 (...) external
 setGasZetaPool (...) external
 setWZETAContractAddress (...) external
 setConnectorZEVMAddress (...) external
+uniswapv2PairFor (...) public pure
+sortTokens (...) internal pure

```
[contracts/zevm/SystemContract.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol)
```diff
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

diff --git a/private/OriginalC4796z b/private/ModifiedsmTTKH
index e860a04..ff073f6 100644
--- a/private/OriginalC4796z
+++ b/private/ModifiedsmTTKH
@@ -1,7 +1,7 @@
 constructor (...) internal
-getLockedAmount (...) external view
 setMaxSupply (...) external
 send (...) external
 onReceive (...) external
 onRevert (...) external
+getLockedAmount (...) external view

```
[contracts/evm/ZetaConnector.non-eth.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol)
```diff
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

diff --git a/private/OriginalmA252e b/private/Modifiedzh2un8
index 1150416..a26affc 100644
--- a/private/OriginalmA252e
+++ b/private/Modifiedzh2un8
@@ -1,6 +1,6 @@
 constructor (...) internal
-getLockedAmount (...) external view
 send (...) external
 onReceive (...) external
 onRevert (...) external
+getLockedAmount (...) external view

```
[contracts/evm/ZetaConnector.eth.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol)
```diff
// File: contracts/evm/tools/ZetaInteractor.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

diff --git a/private/OriginaloRpV9d b/private/ModifiedYNDpiB
index 19dc9ba..f6c5189 100644
--- a/private/OriginaloRpV9d
+++ b/private/ModifiedYNDpiB
@@ -1,5 +1,5 @@
 constructor (...) internal
-_isValidCaller (...) private view
-_isValidChainId (...) internal view
 setInteractorByChainId (...) external
+_isValidChainId (...) internal view
+_isValidCaller (...) private view

```
[contracts/evm/tools/ZetaInteractor.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol)
### [N&#x2011;21] [Style Guide] Contract and library names should match their filenames
> - Contract and library names should also match their filenames.

> - If a contract file includes multiple contracts and/or libraries, then the filename should match the core contract. This is not recommended however if it can be avoided.

[Solidity Style Guide > Contract and Library Names](https://docs.soliditylang.org/en/latest/style-guide.html#contract-and-library-names)

*Total instances: 11*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

56: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
*GitHub: [56](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56-L56)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```
*GitHub: [33](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

27: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
*GitHub: [27](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27-L27)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

17: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```
*GitHub: [17](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17-L17)*
```solidity
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

15: contract ZetaConnectorBase is ConnectorErrors, Pausable {
```
*GitHub: [15](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15)*
```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

15: contract ZetaConnectorNonEth is ZetaConnectorBase {
```
*GitHub: [15](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15-L15)*
```solidity
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

15: contract ZetaConnectorEth is ZetaConnectorBase {
```
*GitHub: [15](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15-L15)*
```solidity
// File: contracts/zevm/WZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol

3: contract WETH9 {
```
*GitHub: [3](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L3-L3)*
```solidity
// File: contracts/evm/Zeta.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol

9: contract ZetaEth is ERC20("Zeta", "ZETA") {
```
*GitHub: [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9-L9)*
```solidity
// File: contracts/zevm/Uniswap.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol

7: contract UniswapImports {}
```
*GitHub: [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L7-L7)*
```solidity
// File: contracts/zevm/UniswapPeriphery.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol

6: contract UniswapImports {}
```
*GitHub: [6](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6-L6)*


</details>


### [N&#x2011;22] [Style Guide] Inconsistent struct naming
In Solidity, there are no strict guidelines for contract naming, but it's important to be consistent and stick to one style.

The naming recommendations given here are intended to improve the readability.

Structs should be named using the `CapWords` style. Examples: `MyCoin`, `Position`, `PositionXY`.


[Solidity Style Guide > Struct Names](https://docs.soliditylang.org/en/latest/style-guide.html#struct-names)


Most frequently used style in the project: CapWords

Below are examples of other styles used in the project.

*Total instances: 2*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

//@audit: CapWords
25:     struct ExactInputSingleParams {
```
*GitHub: [25](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L25-L25)*
```solidity
// File: contracts/zevm/interfaces/zContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol

//@audit: mixedCase
4: struct zContext {
```
*GitHub: [4](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L4-L4)*
### [N&#x2011;23] [Style Guide] Underscore Prefix for Non-external Functions
- `_singleLeadingUnderscore`

This convention is suggested for non-external functions.

*Total instances: 2*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

68:     function getPair(address token0, address token1) internal pure returns (address, address) {
```
*GitHub: [68](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L68)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

87:     function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
```
*GitHub: [87](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87-L87)*
### [N&#x2011;24] [Style Guide] Underscore Prefix for Non-external Variables
- `_singleLeadingUnderscore`

This convention is suggested for non-external state variables (`private` or `internal`). State variables without a specified visibility are `internal` by default.

*Total instances: 4*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

37:     address internal immutable WETH9Address;
```
*GitHub: [37](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37-L37)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol

21:     address internal immutable wETH;

24:     IUniswapV2Router02 internal immutable uniswapV2Router;
```
*GitHub: [21](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21-L21), [24](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24-L24)*
```solidity
// File: contracts/evm/tools/ZetaInteractor.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

11:     uint256 internal immutable currentChainId;
```
*GitHub: [11](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11-L11)*
### [N&#x2011;25] [Style Guide] Incorrect arrangement of contract body elements
Layout contract elements in the following order:

1. Type declarations

1. State variables

1. Events

1. Errors

1. Modifiers

1. Functions


[Solidity Style Guide > Order of Layout](https://docs.soliditylang.org/en/latest/style-guide.html#order-of-layout)

*Total instances: 8*

```diff
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

diff --git a/private/Original5XSgnV b/private/ModifiedD4LCaj
index 29d0a37..00c50f2 100644
--- a/private/Original5XSgnV
+++ b/private/ModifiedD4LCaj
@@ -22,12 +22,12 @@

     uint8 private _decimals;

+    modifier onlyFungible() {
+
     function _msgSender() internal view virtual returns (address) {

     function _msgData() internal view virtual returns (bytes calldata) {

-    modifier onlyFungible() {
-
     constructor(

     function name() public view virtual override returns (string memory) {
```
[contracts/zevm/ZRC20.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol)
```diff
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

diff --git a/private/OriginaloE49xz b/private/Modified7Une8j
index 08038db..08efd5d 100644
--- a/private/OriginaloE49xz
+++ b/private/Modified7Une8j
@@ -14,10 +14,10 @@

     bool internal _locked;

-    constructor(
-
     modifier nonReentrant() {

+    constructor(
+
     receive() external payable {}

     function getZetaFromEth(
```
[contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol)
```diff
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

diff --git a/private/OriginalLm9Ogx b/private/ModifiedmZ2IKv
index 4c9584d..53db7a3 100644
--- a/private/OriginalLm9Ogx
+++ b/private/ModifiedmZ2IKv
@@ -10,10 +10,10 @@

     bool internal _locked;

-    constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
-
     modifier nonReentrant() {

+    constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
+
     receive() external payable {}

     function getPair(address token0, address token1) internal pure returns (address, address) {
```
[contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol)
```diff
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

diff --git a/private/Originalt98gfR b/private/ModifiedSFxmIG
index 7b83739..6e9c2de 100644
--- a/private/Originalt98gfR
+++ b/private/ModifiedSFxmIG
@@ -14,10 +14,10 @@

     bool internal _locked;

-    constructor(
-
     modifier nonReentrant() {

+    constructor(
+
     receive() external payable {}

     function getZetaFromEth(
```
[contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol)
```diff
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

diff --git a/private/Originalo3qZ46 b/private/ModifiedLctrSl
index 2d75325..88d95b4 100644
--- a/private/Originalo3qZ46
+++ b/private/ModifiedLctrSl
@@ -1,19 +1,3 @@
-    error NotWhitelisted();
-
-    error NotPaused();
-
-    error InvalidSender();
-
-    error InvalidTSSUpdater();
-
-    error ZeroAddress();
-
-    error IsPaused();
-
-    error ZetaMaxFeeExceeded();
-
-    error ZeroFee();
-
     bool public paused;

     address public TSSAddress;
@@ -46,6 +30,22 @@

     event UpdatedZetaFee(uint256 zetaFee_);

+    error NotWhitelisted();
+
+    error NotPaused();
+
+    error InvalidSender();
+
+    error InvalidTSSUpdater();
+
+    error ZeroAddress();
+
+    error IsPaused();
+
+    error ZetaMaxFeeExceeded();
+
+    error ZeroFee();
+
     modifier onlyTSS() {

     modifier onlyTSSUpdater() {
```
[contracts/evm/ERC20Custody.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol)
```diff
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

diff --git a/private/OriginalQtQPcY b/private/ModifiedPI14Fk
index d1eb6f9..c88a5e7 100644
--- a/private/OriginalQtQPcY
+++ b/private/ModifiedPI14Fk
@@ -18,14 +18,14 @@

     event PauserAddressUpdated(address callerAddress, address newTssAddress);

-    constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
-
     modifier onlyPauser() {

     modifier onlyTssAddress() {

     modifier onlyTssUpdater() {

+    constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
+
     function updatePauserAddress(address pauserAddress_) external onlyPauser {

     function updateTssAddress(address tssAddress_) external {
```
[contracts/evm/ZetaConnector.base.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol)
```diff
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

diff --git a/private/OriginaljQnQBO b/private/ModifiedJ3rLrx
index 93bbac2..4c492dd 100644
--- a/private/OriginaljQnQBO
+++ b/private/ModifiedJ3rLrx
@@ -1,11 +1,3 @@
-    error OnlyWZETA();
-
-    error WZETATransferFailed();
-
-    error OnlyFungibleModule();
-
-    error FailedZetaSent();
-
     address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);

     address public wzeta;
@@ -14,6 +6,14 @@

     event SetWZETA(address wzeta_);

+    error OnlyWZETA();
+
+    error WZETATransferFailed();
+
+    error OnlyFungibleModule();
+
+    error FailedZetaSent();
+
     constructor(address wzeta_) {

     receive() external payable {
```
[contracts/zevm/ZetaConnectorZEVM.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol)
```diff
// File: contracts/zevm/WZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol

diff --git a/private/OriginalRMoPwz b/private/ModifiedI7K1Wk
index 3162681..3b76e4a 100644
--- a/private/OriginalRMoPwz
+++ b/private/ModifiedI7K1Wk
@@ -4,6 +4,13 @@

     uint8 public decimals = 18;

+    mapping(address => uint) public balanceOf;
+
+    mapping(address => mapping(address => uint)) public allowance;
+
+    function() public payable {
+        deposit();
+
     event Approval(address indexed src, address indexed guy, uint wad);

     event Transfer(address indexed src, address indexed dst, uint wad);
@@ -12,11 +19,4 @@

     event Withdrawal(address indexed src, uint wad);

-    mapping(address => uint) public balanceOf;
-
-    mapping(address => mapping(address => uint)) public allowance;
-
-    function() public payable {
-        deposit();
-

```
[contracts/zevm/WZETA.sol](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol)
### [N&#x2011;26] Unresolved `TODOs` in comments
Some features might not be properly implemented, as there are commented TODOs. Review the comments to ensure that everything is implemented, and remove them before deploying.

*Total instances: 1*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

204:         //@TODO: Implement
```
*GitHub: [204](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L204-L204)*
### [N&#x2011;27] Consider using `delete` rather than assigning zero/false to clear values
The delete keyword more closely matches the semantics of what is being done, and draws more attention to the changing of state, which may lead to a more thorough audit of its associated logic.

*Total instances: 5*

```solidity
// File: contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol

98:         _locked = false;
```
*GitHub: [98](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L98-L98)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

63:         _locked = false;
```
*GitHub: [63](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L63-L63)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol

69:         _locked = false;
```
*GitHub: [69](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L69-L69)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

136:         paused = false;

154:         whitelisted[asset] = false;
```
*GitHub: [136](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L136-L136), [154](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L154-L154)*
### [N&#x2011;28] Use `immutable` for expressions rather than `constant`
Choosing the right tool for the task at hand is crucial. Constants should be used for literal values in the code, and immutable variables should be employed for expressions or values used in constructors.

*Total instances: 1*

```solidity
// File: contracts/evm/tools/ZetaInteractor.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol

10:     bytes32 constant ZERO_BYTES = keccak256(new bytes(0));
```
*GitHub: [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10-L10)*
### [N&#x2011;29] Use `type(X).max` instead of constant formulas like `2**n`
Earlier versions of solidity can use `uint<n>(-1)` instead. Expressions `2**n -1` can often be rewritten to accommodate the change.

*Total instances: 1*

```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

16:     uint256 public maxSupply = 2 ** 256 - 1;
```
*GitHub: [16](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16-L16)*
### [N&#x2011;30] Missing checks for address(0) in the function
Adding a zero address check for each address type parameter can prevent errors.

*Total instances: 76*

<details>
<summary>see instances</summary>


```solidity
// File: contracts/zevm/ZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol

//@audit: account
116:     function balanceOf(address account) public view virtual override returns (uint256) {

//@audit: recipient
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {

//@audit: owner, spender
135:     function allowance(address owner, address spender) public view virtual override returns (uint256) {

//@audit: spender
145:     function approve(address spender, uint256 amount) public virtual override returns (bool) {

//@audit: sender, recipient
157:     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
//@audit: to
225:     function deposit(address to, uint256 amount) external override returns (bool) {

//@audit: addr
270:     function updateSystemContractAddress(address addr) external onlyFungible {
```
*GitHub: [116](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L116-L116), [125](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125-L125), [135](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135-L135), [145](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145-L145), [157](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157-L157), [225](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225-L225), [270](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270-L270)*
```solidity
// File: contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol

//@audit: to
25:     function depositTo(address to) external payable;

//@audit: to
27:     function withdrawTo(address payable to, uint256 value) external;

//@audit: token0, token1
68:     function getPair(address token0, address token1) internal pure returns (address, address) {
```
*GitHub: [25](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L25-L25), [27](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L27-L27), [68](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L68)*
```solidity
// File: contracts/evm/ERC20Custody.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol

//@audit: asset
144:     function whitelist(IERC20 asset) external onlyTSS {

//@audit: asset
153:     function unwhitelist(IERC20 asset) external onlyTSS {

//@audit: recipient
193:     function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
```
*GitHub: [144](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144-L144), [153](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153-L153), [193](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193-L193)*
```solidity
// File: contracts/evm/ZetaConnector.base.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol

//@audit: destinationAddress
172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

//@audit: zetaTxSenderAddress
185:     function onRevert(
186:         address zetaTxSenderAddress,
187:         uint256 sourceChainId,
188:         bytes calldata destinationAddress,
189:         uint256 destinationChainId,
190:         uint256 remainingZetaValue,
191:         bytes calldata message,
192:         bytes32 internalSendHash
193:     ) external virtual {}
```
*GitHub: [172](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)*
```solidity
// File: contracts/zevm/SystemContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol

//@audit: zrc20
67:     function depositAndCall(
68:         zContext calldata context,
69:         address zrc20,
70:         uint256 amount,
71:         address target,
72:         bytes calldata message
73:     ) external {

//@audit: factory, tokenA, tokenB
100:     function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {

//@audit: zrc20
134:     function setGasCoinZRC20(uint256 chainID, address zrc20) external {

//@audit: erc20
145:     function setGasZetaPool(uint256 chainID, address erc20) external {
```
*GitHub: [67](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L73), [100](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L100-L100), [134](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134-L134), [145](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L145-L145)*
```solidity
// File: contracts/zevm/ZetaConnectorZEVM.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol

//@audit: src, dst
50:     function transferFrom(address src, address dst, uint wad) external returns (bool);

//@audit: wzeta_
114:     function setWzetaAddress(address wzeta_) external {
```
*GitHub: [50](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50-L50), [114](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114-L114)*
```solidity
// File: contracts/evm/ZetaConnector.non-eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol

//@audit: destinationAddress
61:     function onReceive(
62:         bytes calldata zetaTxSenderAddress,
63:         uint256 sourceChainId,
64:         address destinationAddress,
65:         uint256 zetaValue,
66:         bytes calldata message,
67:         bytes32 internalSendHash
68:     ) external override onlyTssAddress {

//@audit: zetaTxSenderAddress
87:     function onRevert(
88:         address zetaTxSenderAddress,
89:         uint256 sourceChainId,
90:         bytes calldata destinationAddress,
91:         uint256 destinationChainId,
92:         uint256 remainingZetaValue,
93:         bytes calldata message,
94:         bytes32 internalSendHash
95:     ) external override whenNotPaused onlyTssAddress {
```
*GitHub: [61](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L68), [87](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L95)*
```solidity
// File: contracts/evm/ZetaConnector.eth.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol

//@audit: destinationAddress
52:     function onReceive(
53:         bytes calldata zetaTxSenderAddress,
54:         uint256 sourceChainId,
55:         address destinationAddress,
56:         uint256 zetaValue,
57:         bytes calldata message,
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress {

//@audit: zetaTxSenderAddress
77:     function onRevert(
78:         address zetaTxSenderAddress,
79:         uint256 sourceChainId,
80:         bytes calldata destinationAddress,
81:         uint256 destinationChainId,
82:         uint256 remainingZetaValue,
83:         bytes calldata message,
84:         bytes32 internalSendHash
85:     ) external override whenNotPaused onlyTssAddress {
```
*GitHub: [52](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L59), [77](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L85)*
```solidity
// File: contracts/zevm/WZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol

//@audit: guy
36:     function approve(address guy, uint wad) public returns (bool) {

//@audit: dst
42:     function transfer(address dst, uint wad) public returns (bool) {

//@audit: dst
46:     function transferFrom(address src, address dst, uint wad) public returns (bool) {
```
*GitHub: [36](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36-L36), [42](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L42-L42), [46](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L46-L46)*
```solidity
// File: contracts/evm/interfaces/ZetaInterfaces.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol

//@audit: destinationAddress
83:     function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

//@audit: destinationAddress, inputToken
85:     function getZetaFromToken(
86:         address destinationAddress,
87:         uint256 minAmountOut,
88:         address inputToken,
89:         uint256 inputTokenAmount
90:     ) external returns (uint256);

//@audit: destinationAddress
92:     function getEthFromZeta(
93:         address destinationAddress,
94:         uint256 minAmountOut,
95:         uint256 zetaTokenAmount
96:     ) external returns (uint256);

//@audit: destinationAddress, outputToken
98:     function getTokenFromZeta(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address outputToken,
102:         uint256 zetaTokenAmount
103:     ) external returns (uint256);
```
*GitHub: [83](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83-L83), [85](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85-L90), [92](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92-L96), [98](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98-L103)*
```solidity
// File: contracts/evm/tools/interfaces/TridentIPoolRouter.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol

//@audit: token, recipient
70:     function sweep(address token, uint256 amount, address recipient) external payable;
```
*GitHub: [70](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L70-L70)*
```solidity
// File: contracts/zevm/Interfaces.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol

//@audit: account
24:     function balanceOf(address account) external view returns (uint256);

//@audit: recipient
26:     function transfer(address recipient, uint256 amount) external returns (bool);

//@audit: owner, spender
28:     function allowance(address owner, address spender) external view returns (uint256);

//@audit: spender
30:     function approve(address spender, uint256 amount) external returns (bool);

//@audit: sender, recipient
32:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
//@audit: to
34:     function deposit(address to, uint256 amount) external returns (bool);
```
*GitHub: [24](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24-L24), [26](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26-L26), [28](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28-L28), [30](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30-L30), [32](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32-L32), [34](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34-L34)*
```solidity
// File: contracts/zevm/interfaces/zContract.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol

//@audit: zrc20
11:     function onCrossChainCall(
12:         zContext calldata context,
13:         address zrc20,
14:         uint256 amount,
15:         bytes calldata message
16:     ) external;
```
*GitHub: [11](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11-L16)*
```solidity
// File: contracts/zevm/interfaces/IWZETA.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol

//@audit: owner
12:     function balanceOf(address owner) external view returns (uint);

//@audit: owner, spender
14:     function allowance(address owner, address spender) external view returns (uint);

//@audit: spender
16:     function approve(address spender, uint wad) external returns (bool);

//@audit: to
18:     function transfer(address to, uint wad) external returns (bool);

//@audit: from, to
20:     function transferFrom(address from, address to, uint wad) external returns (bool);
```
*GitHub: [12](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12-L12), [14](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14-L14), [16](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16-L16), [18](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18-L18), [20](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20-L20)*
```solidity
// File: contracts/zevm/interfaces/IUniswapV2Router02.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol

//@audit: token, to
7:     function removeLiquidityETHSupportingFeeOnTransferTokens(
8:         address token,
9:         uint liquidity,
10:         uint amountTokenMin,
11:         uint amountETHMin,
12:         address to,
13:         uint deadline
14:     ) external returns (uint amountETH);

//@audit: token, to
16:     function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17:         address token,
18:         uint liquidity,
19:         uint amountTokenMin,
20:         uint amountETHMin,
21:         address to,
22:         uint deadline,
23:         bool approveMax,
24:         uint8 v,
25:         bytes32 r,
26:         bytes32 s
27:     ) external returns (uint amountETH);

//@audit: path, to
29:     function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30:         uint amountIn,
31:         uint amountOutMin,
32:         address[] calldata path,
33:         address to,
34:         uint deadline
35:     ) external;

//@audit: path, to
37:     function swapExactETHForTokensSupportingFeeOnTransferTokens(
38:         uint amountOutMin,
39:         address[] calldata path,
40:         address to,
41:         uint deadline
42:     ) external payable;

//@audit: path, to
44:     function swapExactTokensForETHSupportingFeeOnTransferTokens(
45:         uint amountIn,
46:         uint amountOutMin,
47:         address[] calldata path,
48:         address to,
49:         uint deadline
50:     ) external;
```
*GitHub: [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7-L14), [16](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L27), [29](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29-L35), [37](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37-L42), [44](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44-L50)*
```solidity
// File: contracts/evm/interfaces/ZetaNonEthInterface.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol

//@audit: account
10:     function burnFrom(address account, uint256 amount) external;

//@audit: mintee
12:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external;
```
*GitHub: [10](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L10-L10), [12](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12-L12)*
```solidity
// File: contracts/zevm/interfaces/IZRC20.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol

//@audit: account
7:     function balanceOf(address account) external view returns (uint256);

//@audit: recipient
9:     function transfer(address recipient, uint256 amount) external returns (bool);

//@audit: owner, spender
11:     function allowance(address owner, address spender) external view returns (uint256);

//@audit: spender
13:     function approve(address spender, uint256 amount) external returns (bool);

//@audit: spender
15:     function decreaseAllowance(address spender, uint256 amount) external returns (bool);
//@audit: spender
17:     function increaseAllowance(address spender, uint256 amount) external returns (bool);

//@audit: sender, recipient
19:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
//@audit: to
21:     function deposit(address to, uint256 amount) external returns (bool);

//@audit: account
23:     function burn(address account, uint256 amount) external returns (bool);
```
*GitHub: [7](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7-L7), [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9-L9), [11](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11-L11), [13](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13-L13), [15](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15-L15), [17](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17-L17), [19](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19-L19), [21](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21-L21), [23](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23-L23)*
```solidity
// File: contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol

//@audit: token0, token1
17:     function getPools(
18:         address token0,
19:         address token1,
20:         uint256 startIndex,
21:         uint256 count
22:     ) external view returns (address[] memory pairPools);
```
*GitHub: [17](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17-L22)*
```solidity
// File: contracts/zevm/interfaces/IUniswapV2Router01.sol
// https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol

//@audit: tokenA, tokenB, to
9:     function addLiquidity(
10:         address tokenA,
11:         address tokenB,
12:         uint amountADesired,
13:         uint amountBDesired,
14:         uint amountAMin,
15:         uint amountBMin,
16:         address to,
17:         uint deadline
18:     ) external returns (uint amountA, uint amountB, uint liquidity);

//@audit: token, to
20:     function addLiquidityETH(
21:         address token,
22:         uint amountTokenDesired,
23:         uint amountTokenMin,
24:         uint amountETHMin,
25:         address to,
26:         uint deadline
27:     ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

//@audit: tokenA, tokenB, to
29:     function removeLiquidity(
30:         address tokenA,
31:         address tokenB,
32:         uint liquidity,
33:         uint amountAMin,
34:         uint amountBMin,
35:         address to,
36:         uint deadline
37:     ) external returns (uint amountA, uint amountB);

//@audit: token, to
39:     function removeLiquidityETH(
40:         address token,
41:         uint liquidity,
42:         uint amountTokenMin,
43:         uint amountETHMin,
44:         address to,
45:         uint deadline
46:     ) external returns (uint amountToken, uint amountETH);

//@audit: tokenA, tokenB, to
48:     function removeLiquidityWithPermit(
49:         address tokenA,
50:         address tokenB,
51:         uint liquidity,
52:         uint amountAMin,
53:         uint amountBMin,
54:         address to,
55:         uint deadline,
56:         bool approveMax,
57:         uint8 v,
58:         bytes32 r,
59:         bytes32 s
60:     ) external returns (uint amountA, uint amountB);
//@audit: token, to
62:     function removeLiquidityETHWithPermit(
63:         address token,
64:         uint liquidity,
65:         uint amountTokenMin,
66:         uint amountETHMin,
67:         address to,
68:         uint deadline,
69:         bool approveMax,
70:         uint8 v,
71:         bytes32 r,
72:         bytes32 s
73:     ) external returns (uint amountToken, uint amountETH);

//@audit: path, to
75:     function swapExactTokensForTokens(
76:         uint amountIn,
77:         uint amountOutMin,
78:         address[] calldata path,
79:         address to,
80:         uint deadline
81:     ) external returns (uint[] memory amounts);
//@audit: path, to
83:     function swapTokensForExactTokens(
84:         uint amountOut,
85:         uint amountInMax,
86:         address[] calldata path,
87:         address to,
88:         uint deadline
89:     ) external returns (uint[] memory amounts);

//@audit: path, to
91:     function swapExactETHForTokens(
92:         uint amountOutMin,
93:         address[] calldata path,
94:         address to,
95:         uint deadline
96:     ) external payable returns (uint[] memory amounts);
//@audit: path, to
98:     function swapTokensForExactETH(
99:         uint amountOut,
100:         uint amountInMax,
101:         address[] calldata path,
102:         address to,
103:         uint deadline
104:     ) external returns (uint[] memory amounts);

//@audit: path, to
106:     function swapExactTokensForETH(
107:         uint amountIn,
108:         uint amountOutMin,
109:         address[] calldata path,
110:         address to,
111:         uint deadline
112:     ) external returns (uint[] memory amounts);
//@audit: path, to
114:     function swapETHForExactTokens(
115:         uint amountOut,
116:         address[] calldata path,
117:         address to,
118:         uint deadline
119:     ) external payable returns (uint[] memory amounts);

//@audit: path
127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
//@audit: path
129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);
```
*GitHub: [9](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18), [20](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27), [29](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L37), [39](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L46), [48](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60), [62](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73), [75](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L81), [83](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L89), [91](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91-L96), [98](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L104), [106](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L112), [114](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114-L119), [127](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127-L127), [129](https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129-L129)*


</details>

