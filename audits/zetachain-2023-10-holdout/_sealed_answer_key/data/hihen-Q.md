# QA Report

## Summary

### Low Issues

Total **104 instances** over **23 issues**:

|ID|Issue|Instances|
|:--:|:---|:--:|
| [[L-01]](#l-01-use-increaseallowancedecreaseallowance-instead-of-approvesafeapprove) | Use `increaseAllowance()`/`decreaseAllowance()` instead of `approve()`/`safeApprove()` | 4 |
| [[L-02]](#l-02-external-call-recipient-can-consume-all-remaining-gas) | External call recipient can consume all remaining gas | 3 |
| [[L-03]](#l-03-missing-zero-address-check-in-constructor) | Missing zero address check in constructor | 9 |
| [[L-04]](#l-04-owner-can-renounce-while-system-is-paused) | Owner can renounce while system is paused | 1 |
| [[L-05]](#l-05-function-receivepayable-fallback-does-not-authorize-sender) | Function `receive()`/`payable fallback()` does not authorize sender | 3 |
| [[L-06]](#l-06-revert-on-transfer-to-the-zero-address) | Revert on transfer to the zero address | 3 |
| [[L-07]](#l-07-using--without-specifying-an-upper-bound-in-version-pragma-is-unsafe) | Using `>`/`>=` without specifying an upper bound in version pragma is unsafe | 2 |
| [[L-08]](#l-08-state-variables-not-limited-to-reasonable-values) | State variables not limited to reasonable values | 3 |
| [[L-09]](#l-09-consider-implementing-two-step-procedure-for-updating-protocol-addresses) | Consider implementing two-step procedure for updating protocol addresses | 1 |
| [[L-10]](#l-10-downcasting-other-types-to-an-address-can-cause-collisions) | Downcasting other types to an address can cause collisions | 1 |
| [[L-11]](#l-11-vulnerable-versions-of-packages-are-being-used) | Vulnerable versions of packages are being used | 3 |
| [[L-12]](#l-12-missing-checks-for-address0-when-setting-address-state-variables) | Missing checks for `address(0)` when setting address state variables | 10 |
| [[L-13]](#l-13-unsafe-solidity-low-level-call-can-cause-gas-grief-attack) | Unsafe solidity low-level call can cause gas grief attack | 3 |
| [[L-14]](#l-14-owner-can-renounce-ownership) | Owner can renounce Ownership | 1 |
| [[L-15]](#l-15-constructor--initialization-function-lacks-parameter-validation) | Constructor / initialization function lacks parameter validation | 13 |
| [[L-16]](#l-16-contracts-are-vulnerable-to-fee-on-transfer-accounting-related-issues) | Contracts are vulnerable to fee-on-transfer accounting-related issues | 6 |
| [[L-17]](#l-17-functions-calling-contractsaddresses-with-transfer-hooks-should-be-protected-by-reentrancy-guard) | Functions calling contracts/addresses with transfer hooks should be protected by reentrancy guard | 5 |
| [[L-18]](#l-18-critical-functions-should-be-controlled-by-time-locks) | Critical functions should be controlled by time locks | 10 |
| [[L-19]](#l-19-the-safeapprove-function-is-deprecated) | The safeApprove() function is deprecated | 12 |
| [[L-20]](#l-20-tokens-may-be-minted-to-the-zero-address) | Tokens may be minted to the zero address | 1 |
| [[L-21]](#l-21-some-tokens-may-revert-when-zero-value-transfers-are-made) | Some tokens may revert when zero value transfers are made | 3 |
| [[L-22]](#l-22-use-safecast-to-downcast-safely) | Use `SafeCast` to downcast safely | 1 |
| [[L-23]](#l-23-use-descriptive-constant-instead-of-0-as-a-parameter) | Use descriptive constant instead of 0 as a parameter | 6 |

### Non Critical Issues

Total **2805 instances** over **102 issues**:

|ID|Issue|Instances|
|:--:|:---|:--:|
| [[N-01]](#n-01-custom-errors-has-no-error-details) | Custom errors has no error details | 42 |
| [[N-02]](#n-02-import-declarations-should-import-specific-identifiers-rather-than-the-whole-file) | Import declarations should import specific identifiers, rather than the whole file | 50 |
| [[N-03]](#n-03-event-should-include-parameters) | Event should include parameters | 1 |
| [[N-04]](#n-04-visibility-of-state-variables-is-not-explicitly-defined) | Visibility of state variables is not explicitly defined | 1 |
| [[N-05]](#n-05-natspec-documentation-for-contract-is-missing) | NatSpec documentation for contract is missing | 28 |
| [[N-06]](#n-06-names-of-privateinternal-functions-should-be-prefixed-with-an-underscore) | Names of `private`/`internal` functions should be prefixed with an underscore | 2 |
| [[N-07]](#n-07-names-of-privateinternal-state-variables-should-be-prefixed-with-an-underscore) | Names of `private`/`internal` state variables should be prefixed with an underscore | 9 |
| [[N-08]](#n-08-order-of-functions-does-not-follow-the-solidity-style-guide) | Order of functions does not follow the Solidity Style Guide | 48 |
| [[N-09]](#n-09-redundant-inheritance-specifier) | Redundant inheritance specifier | 1 |
| [[N-10]](#n-10-unused-errors) | Unused errors | 1 |
| [[N-11]](#n-11-unused-internal-functions-can-be-removed) | Unused `internal` functions can be removed | 1 |
| [[N-12]](#n-12-use-uint256int256-instead-of-uintint) | Use `uint256`/`int256` instead of `uint`/`int` | 108 |
| [[N-13]](#n-13-consider-moving-msgsender-checks-to-modifiers) | Consider moving `msg.sender` checks to `modifier`s | 19 |
| [[N-14]](#n-14-missing-checks-for-empty-bytes-when-updating-bytes-state-variables) | Missing checks for empty bytes when updating bytes state variables | 1 |
| [[N-15]](#n-15-consider-adding-a-blockdeny-list) | Consider adding a block/deny-list | 8 |
| [[N-16]](#n-16-constantsimmutables-redefined-elsewhere) | Constants/Immutables redefined elsewhere | 21 |
| [[N-17]](#n-17-contracts-should-each-be-defined-in-separate-files) | Contracts should each be defined in separate files | 9 |
| [[N-18]](#n-18-contract-name-does-not-match-its-filename) | Contract name does not match its filename | 9 |
| [[N-19]](#n-19-upper_case-names-should-be-reserved-for-constantimmutable-variables) | UPPER_CASE names should be reserved for `constant`/`immutable` variables | 3 |
| [[N-20]](#n-20-do-not-use-literal-numbers-for-array-indexes) | Do not use literal numbers for array indexes | 26 |
| [[N-21]](#n-21-events-should-be-emitted-before-external-calls) | Events should be emitted before external calls | 26 |
| [[N-22]](#n-22-empty-function-body-without-comments) | Empty function body without comments | 6 |
| [[N-23]](#n-23-events-are-emitted-without-the-sender-information) | Events are emitted without the sender information | 34 |
| [[N-24]](#n-24-event-is-missing-indexed-fields) | Event is missing `indexed` fields | 23 |
| [[N-25]](#n-25-inconsistent-floating-version-pragma) | Inconsistent floating version pragma | 2 |
| [[N-26]](#n-26-function-state-mutability-can-be-restricted-to-pure) | Function state mutability can be restricted to pure | 5 |
| [[N-27]](#n-27-imports-could-be-organized-more-systematically) | Imports could be organized more systematically | 10 |
| [[N-28]](#n-28-interfaces-should-be-indicated-with-an-i-prefix-in-the-contract-name) | Interfaces should be indicated with an `I` prefix in the contract name | 22 |
| [[N-29]](#n-29-invalid-natspec-comment-style) | Invalid NatSpec comment style | 20 |
| [[N-30]](#n-30-openzeppelincontracts-should-be-upgraded-to-a-newer-version) | @openzeppelin/contracts should be upgraded to a newer version | 24 |
| [[N-31]](#n-31-lines-are-too-long) | Lines are too long | 14 |
| [[N-32]](#n-32-magic-numbers-should-be-replaced-with-constants) | Magic numbers should be replaced with constants | 3 |
| [[N-33]](#n-33-expressions-for-constant-values-should-use-immutable-rather-than-constant) | Expressions for constant values should use `immutable` rather than `constant` | 1 |
| [[N-34]](#n-34-functions-not-used-internally-could-be-marked-external) | Functions not used internally could be marked external | 10 |
| [[N-35]](#n-35-contracts-containing-only-utility-functions-should-be-made-into-libraries) | Contracts containing only utility functions should be made into libraries | 1 |
| [[N-36]](#n-36-use-inheritdoc-for-overridden-functions) | Use `@inheritdoc` for overridden functions | 33 |
| [[N-37]](#n-37-contracts-should-have-natspec-author-tags) | Contracts should have NatSpec `@author` tags | 46 |
| [[N-38]](#n-38-contracts-should-have-notice-tags) | Contracts should have `@notice` tags | 28 |
| [[N-39]](#n-39-contracts-should-have-natspec-title-tags) | Contracts should have NatSpec `@title` tags | 45 |
| [[N-40]](#n-40-events-missing-natspec-param-tag) | Events missing NatSpec `@param` tag | 117 |
| [[N-41]](#n-41-event-declarations-should-have-natspec-descriptions) | Event declarations should have NatSpec descriptions | 50 |
| [[N-42]](#n-42-functions-missing-natspec-param-tag) | Functions missing NatSpec `@param` tag | 381 |
| [[N-43]](#n-43-natspec-documentation-for-function-is-missing) | NatSpec documentation for function is missing | 129 |
| [[N-44]](#n-44-modifiers-missing-natspec-param-tag) | Modifiers missing NatSpec `@param` tag | 2 |
| [[N-45]](#n-45-functions-missing-natspec-return-tag) | Functions missing NatSpec `@return` tag | 97 |
| [[N-46]](#n-46-state-variables-should-have-natspec-descriptions) | State variables should have NatSpec descriptions | 12 |
| [[N-47]](#n-47-struct-names-should-use-capwords-style) | Struct names should use CapWords style | 1 |
| [[N-48]](#n-48-contract-name-does-not-follow-the-solidity-style-guide) | Contract name does not follow the Solidity Style Guide | 1 |
| [[N-49]](#n-49-functions-should-be-named-in-mixedcase-style) | Functions should be named in mixedCase style | 9 |
| [[N-50]](#n-50-variable-names-for-immutables-should-use-upper_case_with_underscores) | Variable names for `immutable`s should use UPPER_CASE_WITH_UNDERSCORES | 26 |
| [[N-51]](#n-51-modifiers-should-be-named-in-mixedcase-style) | Modifiers should be named in mixedCase style | 2 |
| [[N-52]](#n-52-order-of-contract-layout-does-not-follow-the-solidity-style-guide) | Order of contract layout does not follow the Solidity Style Guide | 9 |
| [[N-53]](#n-53-missing-zero-address-check-in-functions-with-address-parameters) | Missing zero address check in functions with address parameters | 23 |
| [[N-54]](#n-54-named-imports-of-parent-contracts-are-missing) | Named imports of parent contracts are missing | 20 |
| [[N-55]](#n-55-constants-should-be-put-on-the-left-side-of-comparisons) | Constants should be put on the left side of comparisons | 97 |
| [[N-56]](#n-56-each-interfaces-should-be-defined-in-a-separate-file) | Each interfaces should be defined in a separate file | 20 |
| [[N-57]](#n-57-put-all-system-wide-constants-in-one-file) | Put all system-wide constants in one file | 3 |
| [[N-58]](#n-58-spdx-license-identifier-not-provided) | SPDX-License-Identifier not provided | 2 |
| [[N-59]](#n-59-spdx-identifier-should-be-the-in-the-first-line-of-a-solidity-file) | SPDX identifier should be the in the first line of a solidity file | 2 |
| [[N-60]](#n-60-todos-left-in-the-code) | `TODO`s left in the code | 1 |
| [[N-61]](#n-61-typos) | Typos | 1 |
| [[N-62]](#n-62-unnecessary-casting) | Unnecessary casting | 1 |
| [[N-63]](#n-63-unused-contract-variables) | Unused contract variables | 2 |
| [[N-64]](#n-64-unused-function-parameters) | Unused function parameters | 14 |
| [[N-65]](#n-65-unused-modifiers) | Unused modifiers | 2 |
| [[N-66]](#n-66-use-delete-instead-of-assigning-values-to-false) | Use delete instead of assigning values to `false` | 5 |
| [[N-67]](#n-67-use-the-latest-solidity-version) | Use the latest Solidity version | 29 |
| [[N-68]](#n-68-named-mappings-are-recommended) | Named mappings are recommended | 8 |
| [[N-69]](#n-69-use-transfer-libraries-instead-of-low-level-calls-to-transfer-native-tokens) | Use transfer libraries instead of low level calls to transfer native tokens | 3 |
| [[N-70]](#n-70-use-typexmax-instead-of-constant-formulas-like-2n) | Use `type(X).max` instead of constant formulas like `2**n` | 1 |
| [[N-71]](#n-71-using-underscore-at-the-end-of-variable-name) | Using underscore at the end of variable name | 60 |
| [[N-72]](#n-72-whitespace-in-expressions) | Whitespace in Expressions | 3 |
| [[N-73]](#n-73-use-a-struct-to-encapsulate-multiple-function-parameters) | Use a struct to encapsulate multiple function parameters | 8 |
| [[N-74]](#n-74-returning-a-struct-instead-of-a-bunch-of-variables-is-better) | Returning a struct instead of a bunch of variables is better | 5 |
| [[N-75]](#n-75-events-that-mark-critical-parameter-changes-should-contain-both-the-old-and-the-new-value) | Events that mark critical parameter changes should contain both the old and the new value | 11 |
| [[N-76]](#n-76-contract-variables-should-have-comments) | Contract variables should have comments | 13 |
| [[N-77]](#n-77-file-is-missing-natspec) | File is missing NatSpec | 7 |
| [[N-78]](#n-78-modifier-declarations-should-have-natspec-descriptions) | Modifier declarations should have NatSpec descriptions | 5 |
| [[N-79]](#n-79-empty-bytes-check-is-missing) | Empty bytes check is missing | 13 |
| [[N-80]](#n-80-contract-functions-should-use-an-interface) | Contract functions should use an `interface` | 42 |
| [[N-81]](#n-81-interface-files-should-not-use-fixed-compiler-versions) | Interface files should not use fixed compiler versions | 13 |
| [[N-82]](#n-82-addresses-shouldnt-be-hard-coded) | Addresses shouldn't be hard-coded | 3 |
| [[N-83]](#n-83-control-structures-do-not-follow-the-solidity-style-guide) | Control structures do not follow the Solidity Style Guide | 98 |
| [[N-84]](#n-84-functions-contain-the-same-code) | Functions contain the same code | 2 |
| [[N-85]](#n-85-inconsistent-spacing-in-comments) | Inconsistent spacing in comments | 2 |
| [[N-86]](#n-86-missing-event-for-critical-changes) | Missing event for critical changes | 1 |
| [[N-87]](#n-87-duplicated-requirerevert-checks-should-be-refactored) | Duplicated `require()`/`revert()` checks should be refactored | 12 |
| [[N-88]](#n-88-consider-adding-emergency-stop-functionality) | Consider adding emergency-stop functionality | 14 |
| [[N-89]](#n-89-avoid-the-use-of-sensitive-terms) | Avoid the use of sensitive terms | 18 |
| [[N-90]](#n-90-enable-ir-based-code-generation) | Enable IR-based code generation | 1 |
| [[N-91]](#n-91-contracts-should-have-natspec-dev-tags) | Contracts should have NatSpec `@dev` tags | 29 |
| [[N-92]](#n-92-error-declarations-should-have-natspec-descriptions) | Error declarations should have NatSpec descriptions | 51 |
| [[N-93]](#n-93-missing-natspec-dev-from-event-declaration) | Missing NatSpec `@dev` from event declaration | 51 |
| [[N-94]](#n-94-missing-natspec-notice-from-event-declaration) | Missing NatSpec `@notice` from event declaration | 50 |
| [[N-95]](#n-95-missing-natspec-dev-from-function-declaration) | Missing NatSpec `@dev` from function declaration | 136 |
| [[N-96]](#n-96-missing-natspec-notice-from-function-declaration) | Missing NatSpec `@notice` from function declaration | 187 |
| [[N-97]](#n-97-missing-natspec-dev-from-modifier-declaration) | Missing NatSpec `@dev` from modifier declaration | 5 |
| [[N-98]](#n-98-missing-natspec-notice-from-modifier-declaration) | Missing NatSpec `@notice` from modifier declaration | 11 |
| [[N-99]](#n-99-large-or-complicated-code-bases-should-implement-invariant-tests) | Large or complicated code bases should implement invariant tests | 1 |
| [[N-100]](#n-100-top-level-declarations-should-be-separated-by-at-least-two-lines) | Top-level declarations should be separated by at least two lines | 95 |
| [[N-101]](#n-101-consider-adding-formal-verification-proofs) | Consider adding formal verification proofs | 31 |
| [[N-102]](#n-102-prevent-re-setting-a-state-variable-with-the-same-value) | Prevent re-setting a state variable with the same value | 16 |

## Low Issues

### [L-01] Use `increaseAllowance()`/`decreaseAllowance()` instead of `approve()`/`safeApprove()`

Changing an allowance with `approve()` brings the risk that someone may use both the old and the new allowance by unfortunate transaction ordering. Refer to [ERC20 API: An Attack Vector on the Approve/TransferFrom Methods](https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM).
It is recommended to use the `increaseAllowance()`/`decreaseAllowance()` to avoid ths problem.

There are 4 instances:

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L136) ):

```solidity
136:         IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [109](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L109) ):

```solidity
109:         IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L68) ):

```solidity
68:         IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L108) ):

```solidity
108:         IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);
```

### [L-02] External call recipient can consume all remaining gas

There is no limit specified on the amount of gas used, so the recipient can use up all of the remaining gas(`gasleft()`), causing it to revert. Therefore, when calling an external contract, it is necessary to specify a limited amount of gas to forward.

There are 3 instances:

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178) ):

```solidity
178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [152](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152) ):

```solidity
152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

- *ZetaConnectorZEVM.sol* ( [96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96) ):

```solidity
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```

### [L-03] Missing zero address check in constructor

Constructors often take address parameters to initialize important components of a contract, such as owner or linked contracts. However, without a checking, there's a risk that an address parameter could be mistakenly set to the zero address (0x0). This could be due to an error or oversight during contract deployment. A zero address in a crucial role can cause serious issues, as it cannot perform actions like a normal address, and any funds sent to it will be irretrievable. It's therefore crucial to include a zero address check in constructors to prevent such potential problems. If a zero address is detected, the constructor should revert the transaction.

<details>
<summary>There are 9 instances (click to show):</summary>

- *ERC20Custody.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68) ):

```solidity
/// @audit `TSSAddress_ not checked`
/// @audit `TSSAddressUpdater_ not checked`
/// @audit `zeta_ not checked`
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
```

- *Zeta.eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10) ):

```solidity
/// @audit `creator not checked`
10:     constructor(address creator, uint256 initialSupply) {
```

- *SystemContract.sol* ( [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51) ):

```solidity
/// @audit `wzeta_ not checked`
/// @audit `uniswapv2Factory_ not checked`
/// @audit `uniswapv2Router02_ not checked`
51:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
```

- *ZRC20.sol* ( [60-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L68) ):

```solidity
/// @audit `systemContractAddress_ not checked`
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

- *ZetaConnectorZEVM.sol* ( [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79) ):

```solidity
/// @audit `wzeta_ not checked`
79:     constructor(address wzeta_) {
```

</details>

### [L-04] Owner can renounce while system is paused

The contract owner or pauser with a role is not prevented from renouncing the role/ownership while the contract is paused, which would cause any user assets stored in the protocol, to be locked indefinitely.

There is 1 instance:

- *ZetaConnector.base.sol* ( [151-153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L151-L153) ):

```solidity
151:     function pause() external onlyPauser {
152:         _pause();
153:     }
```

### [L-05] Function `receive()`/`payable fallback()` does not authorize sender

Users may send ETH by mistake to these contracts. As there is no access control on these functions, the funds will be permanently lost.

There are 3 instances:

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101) ):

```solidity
101:     receive() external payable {}
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66) ):

```solidity
66:     receive() external payable {}
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72) ):

```solidity
72:     receive() external payable {}
```

### [L-06] Revert on transfer to the zero address

It's good practice to revert a token transfer transaction if the recipient's address is the zero address. This can prevent unintentional transfers to the zero address due to accidental operations or programming errors. Many token contracts implement such a safeguard, such as [OpenZeppelin - ERC20](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/9e3f4d60c581010c4a3979480e07cc7752f124cc/contracts/token/ERC20/ERC20.sol#L232), [OpenZeppelin - ERC721](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/9e3f4d60c581010c4a3979480e07cc7752f124cc/contracts/token/ERC721/ERC721.sol#L142).

There are 3 instances:

- *ERC20Custody.sol* ( [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L178), [197](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L197) ):

```solidity
178:             zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);

197:         IERC20(asset).safeTransfer(recipient, amount);
```

- *ZRC20.sol* ( [258](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258) ):

```solidity
258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
```

### [L-07] Using `>`/`>=` without specifying an upper bound in version pragma is unsafe

There **will** be breaking changes in future versions of solidity, and at that point your code will no longer be compatible. While you may have the specific version to use in a configuration file, others that include your source files may not.

There are 2 instances:

- *TridentConcentratedLiquidityPoolFactory.sol* ( [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L14) ):

```solidity
14: pragma solidity >=0.8.0;
```

- *TridentIPoolRouter.sol* ( [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14) ):

```solidity
14: pragma solidity >=0.8.0;
```

### [L-08] State variables not limited to reasonable values

Consider adding appropriate minimum/maximum value checks to ensure that the following state variables can never be used to excessively harm users, including via griefing.

There are 3 instances:

- *ZetaConnector.non-eth.sol* ( [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L32) ):

```solidity
32:         maxSupply = maxSupply_;
```

- *ZRC20.sol* ( [280](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L280), [289](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L289) ):

```solidity
280:         GAS_LIMIT = gasLimit;

289:         PROTOCOL_FLAT_FEE = protocolFlatFee;
```

### [L-09] Consider implementing two-step procedure for updating protocol addresses

A copy-paste error or a typo may end up bricking protocol functionality, or sending tokens to an address with no known private key. Consider implementing a two-step procedure for updating protocol addresses, where the recipient is set as pending, and must 'accept' the assignment by making an affirmative call. A straight forward way of doing this would be to have the target contracts implement [EIP-165](https://eips.ethereum.org/EIPS/eip-165), and to have the 'set' functions ensure that the recipient is of the right interface type.

There is 1 instance:

- *ZetaConnector.base.sol* ( [117-123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117-L123) ):

```solidity
117:     function updatePauserAddress(address pauserAddress_) external onlyPauser {
118:         if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
119: 
120:         pauserAddress = pauserAddress_;
121: 
122:         emit PauserAddressUpdated(msg.sender, pauserAddress_);
123:     }
```

### [L-10] Downcasting other types to an address can cause collisions

Downcasting other types to an address will truncates the upper bytes, which means that multiple values can be mapped to an address, i.e. address collisions can occur.

There is 1 instance:

- *SystemContract.sol* ( [102-115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L102-L115) ):

```solidity
102:         pair = address(
103:             uint160(
104:                 uint256(
105:                     keccak256(
106:                         abi.encodePacked(
107:                             hex"ff",
108:                             factory,
109:                             keccak256(abi.encodePacked(token0, token1)),
110:                             hex"96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f" // init code hash
111:                         )
112:                     )
113:                 )
114:             )
115:         );
```

### [L-11] Vulnerable versions of packages are being used

This project is using specific package versions which are vulnerable to the specific CVEs listed below. Consider switching to more recent versions of these packages that don't have these vulnerabilities.
- [CVE-2023-40014](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-40014) - **MEDIUM** - (`@openzeppelin/contracts 4.9.4`): OpenZeppelin Contracts is a library for smart contract development. A merge issue when porting the 5.0.1 patch to the 4.9 branch caused a line duplication. In the version of `Multicall.sol` released in `@openzeppelin/contracts@4.9.4` and `@openzeppelin/contracts-upgradeable@4.9.4`, all subcalls are executed twice. Concretely, this exposes a user to unintentionally duplicate operations like asset transfers. The duplicated delegatecall was removed in version 4.9.5. The 4.9.4 version is marked as deprecated. Users are advised to upgrade. There are no known workarounds for this issue.

- [CVE-2023-40014](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-40014) - **MEDIUM** - (`@openzeppelin/contracts >=4.0.0 <4.9.3`): OpenZeppelin Contracts is a library for secure smart contract development. Starting in version 4.0.0 and prior to version 4.9.3, contracts using `ERC2771Context` along with a custom trusted forwarder may see `_msgSender` return `address(0)` in calls that originate from the forwarder with calldata shorter than 20 bytes. This combination of circumstances does not appear to be common, in particular it is not the case for `MinimalForwarder` from OpenZeppelin Contracts, or any deployed forwarder the team is aware of, given that the signer address is appended to all calls that originate from these forwarders. The problem has been patched in v4.9.3.

- [CVE-2023-34459](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-34459) - **MEDIUM** - (`@openzeppelin/contracts >=4.7.0 <4.9.2`): OpenZeppelin Contracts is a library for smart contract development. Starting in version 4.7.0 and prior to version 4.9.2, when the `verifyMultiProof`, `verifyMultiProofCalldata`, `procesprocessMultiProof`, or `processMultiProofCalldat` functions are in use, it is possible to construct merkle trees that allow forging a valid multiproof for an arbitrary set of leaves. A contract may be vulnerable if it uses multiproofs for verification and the merkle tree that is processed includes a node with value 0 at depth 1 (just under the root). This could happen inadvertedly for balanced trees with 3 leaves or less, if the leaves are not hashed. This could happen deliberately if a malicious tree builder includes such a node in the tree. A contract is not vulnerable if it uses single-leaf proving (`verify`, `verifyCalldata`, `processProof`, or `processProofCalldata`), or if it uses multiproofs with a known tree that has hashed leaves. Standard merkle trees produced or validated with the @openzeppelin/merkle-tree library are safe. The problem has been patched in version 4.9.2. Some workarounds are available. For those using multiproofs: When constructing merkle trees hash the leaves and do not insert empty nodes in your trees. Using the @openzeppelin/merkle-tree package eliminates this issue. Do not accept user-provided merkle roots without reconstructing at least the first level of the tree. Verify the merkle tree structure by reconstructing it from the leaves.

There are 3 instances:

- Global finding

### [L-12] Missing checks for `address(0)` when setting address state variables

Consider adding a zero address check when setting address state variables.

<details>
<summary>There are 10 instances (click to show):</summary>

- *ERC20Custody.sol* ( [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L69), [70](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L70), [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L72) ):

```solidity
69:         TSSAddress = TSSAddress_;

70:         TSSAddressUpdater = TSSAddressUpdater_;

72:         zeta = zeta_;
```

- *SystemContract.sol* ( [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L53), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L54), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L55) ):

```solidity
53:         wZetaContractAddress = wzeta_;

54:         uniswapv2FactoryAddress = uniswapv2Factory_;

55:         uniswapv2Router02Address = uniswapv2Router02_;
```

- *ZRC20.sol* ( [76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L76), [271](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L271) ):

```solidity
76:         SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;

271:         SYSTEM_CONTRACT_ADDRESS = addr;
```

- *ZetaConnectorZEVM.sol* ( [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L80), [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L116) ):

```solidity
80:         wzeta = wzeta_;

116:         wzeta = wzeta_;
```

</details>

### [L-13] Unsafe solidity low-level call can cause gas grief attack

Using the low-level calls of a solidity address can leave the contract open to gas grief attacks. These attacks occur when the called contract returns a large amount of data.
So when calling an external contract, it is necessary to check the length of the return data before reading/copying it (using `returndatasize()`).

There are 3 instances:

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178) ):

```solidity
178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [152](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152) ):

```solidity
152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

- *ZetaConnectorZEVM.sol* ( [96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96) ):

```solidity
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```

### [L-14] Owner can renounce Ownership

Each of the following contracts implements or inherits the `renounceOwnership()` function. This can represent a certain risk if the ownership is renounced for any other reason than by design. Renouncing ownership will leave the contract without an owner, thereby removing any functionality that is only available to the owner.

There is 1 instance:

- *ZetaInteractor.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9) ):

```solidity
9: abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```

### [L-15] Constructor / initialization function lacks parameter validation

Constructors and initialization functions play a critical role in contracts by setting important initial states when the contract is first deployed before the system starts. The parameters passed to the constructor and initialization functions directly affect the behavior of the contract / protocol. If incorrect parameters are provided, the system may fail to run, behave abnormally, be unstable, or lack security. Therefore, it's crucial to carefully check each parameter in the constructor and initialization functions. If an exception is found, the transaction should be rolled back.

<details>
<summary>There are 13 instances (click to show):</summary>

- *ERC20Custody.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68) ):

```solidity
/// @audit `zetaFee_`
/// @audit `zetaMaxFee_`
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
```

- *Zeta.eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10) ):

```solidity
/// @audit `initialSupply`
10:     constructor(address creator, uint256 initialSupply) {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [71-78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L78) ):

```solidity
/// @audit `zetaPoolFee_`
/// @audit `tokenPoolFee_`
71:     constructor(
72:         address zetaToken_,
73:         address pancakeV3Router_,
74:         address uniswapV3Factory_,
75:         address WETH9Address_,
76:         uint24 zetaPoolFee_,
77:         uint24 tokenPoolFee_
78:     ) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [42-49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L49) ):

```solidity
/// @audit `zetaPoolFee_`
/// @audit `tokenPoolFee_`
42:     constructor(
43:         address zetaToken_,
44:         address uniswapV3Router_,
45:         address uniswapV3Factory_,
46:         address WETH9Address_,
47:         uint24 zetaPoolFee_,
48:         uint24 tokenPoolFee_
49:     ) {
```

- *ZRC20.sol* ( [60-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L68) ):

```solidity
/// @audit `name_`
/// @audit `symbol_`
/// @audit `decimals_`
/// @audit `chainid_`
/// @audit `coinType_`
/// @audit `gasLimit_`
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

</details>

### [L-16] Contracts are vulnerable to fee-on-transfer accounting-related issues

Some tokens take a transfer fee (e.g. STA, PAXG), some do not currently charge a fee but may do so in the future (e.g. USDT, USDC).
The functions below transfer funds from the caller to the receiver via `transferFrom()`, but do not ensure that the actual number of tokens received is the same as the input amount to the transfer. If the token is a fee-on-transfer token, the balance after the transfer will be smaller than expected, leading to accounting issues. Even if there are checks later, related to a secondary transfer, an attacker may be able to use latent funds (e.g. mistakenly sent by another user) in order to get a free credit.
One way to solve this problem is to measure the balance before and after the transfer, and use the difference as the amount, rather than the stated amount.

<details>
<summary>There are 6 instances (click to show):</summary>

- *ERC20Custody.sol* ( [197](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L197) ):

```solidity
197:         IERC20(asset).safeTransfer(recipient, amount);
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L135) ):

```solidity
135:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L108) ):

```solidity
108:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L67) ):

```solidity
67:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L107) ):

```solidity
107:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

- *ZRC20.sol* ( [258](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258) ):

```solidity
258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
```

</details>

### [L-17] Functions calling contracts/addresses with transfer hooks should be protected by reentrancy guard

Even if the function follows the best practice of check-effects-interaction, not using a reentrancy guard when there may be transfer hooks opens the users of this protocol up to [read-only reentrancy vulnerability](https://chainsecurity.com/curve-lp-oracle-manipulation-post-mortem/) with no way to protect them except by block-listing the entire protocol.

There are 5 instances:

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L135) ):

```solidity
135:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L108) ):

```solidity
108:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L67) ):

```solidity
67:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L107) ):

```solidity
107:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

- *ZRC20.sol* ( [258](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258) ):

```solidity
258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
```

### [L-18] Critical functions should be controlled by time locks

It is a good practice to give time for users to react and adjust to critical changes. A timelock provides more guarantees and reduces the level of trust required, thus decreasing risk for users. It also indicates that the project is legitimate (less risk of a malicious owner making a sandwich attack on a user).

<details>
<summary>There are 10 instances (click to show):</summary>

- *ERC20Custody.sol* ( [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80) ):

```solidity
80:     function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {
```

- *Zeta.non-eth.sol* ( [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40) ):

```solidity
40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {
```

- *ZetaConnector.base.sol* ( [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117) ):

```solidity
117:     function updatePauserAddress(address pauserAddress_) external onlyPauser {
```

- *ZetaInteractor.sol* ( [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54) ):

```solidity
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```

- *SystemContract.sol* ( [134](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L145), [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L156), [167](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L167) ):

```solidity
134:     function setGasCoinZRC20(uint256 chainID, address zrc20) external {

145:     function setGasZetaPool(uint256 chainID, address erc20) external {

156:     function setWZETAContractAddress(address addr) external {

167:     function setConnectorZEVMAddress(address addr) external {
```

- *ZRC20.sol* ( [270](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270) ):

```solidity
270:     function updateSystemContractAddress(address addr) external onlyFungible {
```

- *ZetaConnectorZEVM.sol* ( [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114) ):

```solidity
114:     function setWzetaAddress(address wzeta_) external {
```

</details>

### [L-19] The safeApprove() function is deprecated

The `safeApprove()` like function [is deprecated](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/bfff03c0d2a59bcd8e2ead1da9aed9edf0080d05/contracts/token/ERC20/utils/SafeERC20.sol#L38-L49).
It is encouraged to use `safeIncreaseAllowance()` and `safeDecreaseAllowance()` instead.

<details>
<summary>There are 12 instances (click to show):</summary>

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L136), [160](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L160), [194](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L194) ):

```solidity
136:         IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);

160:         IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);

194:         IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [109](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L109), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L145), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L176) ):

```solidity
109:         IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);

145:         IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);

176:         IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L68), [104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L104), [134](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L134) ):

```solidity
68:         IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);

104:         IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);

134:         IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L108), [133](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L133), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L168) ):

```solidity
108:         IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);

133:         IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);

168:         IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
```

</details>

### [L-20] Tokens may be minted to the zero address

The target address is not checked in the mint function.

There is 1 instance:

- *Zeta.non-eth.sol* ( [62-71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L71) ):

```solidity
62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
63:         /**
64:          * @dev Only Connector can mint. Minting requires burning the equivalent amount on another chain
65:          */
66:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
67: 
68:         _mint(mintee, value);
69: 
70:         emit Minted(mintee, value, internalSendHash);
71:     }
```

### [L-21] Some tokens may revert when zero value transfers are made

Despite the fact that [EIP-20 states](https://github.com/ethereum/EIPs/blob/7500ac4fc1bbdfaf684e7ef851f798f6b667b2fe/EIPS/eip-20.md?plain=1#L116) that zero-value transfers must be accepted, some tokens, such as LEND, will revert if this is attempted, which may cause transactions that involve other tokens (such as batch operations) to fully revert. Consider skipping the transfer if the amount is zero, which will also save gas.

There are 3 instances:

- *ERC20Custody.sol* ( [181](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L181), [197](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L197) ):

```solidity
181:         asset.safeTransferFrom(msg.sender, address(this), amount);

197:         IERC20(asset).safeTransfer(recipient, amount);
```

- *ZRC20.sol* ( [258](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258) ):

```solidity
258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
```

### [L-22] Use `SafeCast` to downcast safely

When a type is downcast to a smaller type, the higher order bits are truncated, effectively applying a modulo to the original value. The loss of data may cause incorrect calculations, unexpected state changes, or other unexpected behavior.
It is recommended to use the [SafeCast library](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/math/SafeCast.sol).

There is 1 instance:

- *SystemContract.sol* ( [103-114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L103-L114) ):

```solidity
103:             uint160(
104:                 uint256(
105:                     keccak256(
106:                         abi.encodePacked(
107:                             hex"ff",
108:                             factory,
109:                             keccak256(abi.encodePacked(token0, token1)),
110:                             hex"96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f" // init code hash
111:                         )
112:                     )
113:                 )
114:             )
```

### [L-23] Use descriptive constant instead of 0 as a parameter

Passing `0` or `0x0` as a function argument can sometimes result in a security issue(e.g. passing zero as the slippage parameter). A historical example is the infamous `0x0` address bug where numerous tokens were lost. This happens because `0` can be interpreted as an uninitialized `address`, leading to transfers to the `0x0` `address`, effectively burning tokens. Moreover, `0` as a denominator in division operations would cause a runtime exception. It's also often indicative of a logical error in the caller's code.

Consider using a constant variable with a descriptive name, so it's clear that the argument is intentionally being used, and for the right reasons.

There are 6 instances:

- *ZetaTokenConsumerTrident.strategy.sol* ( [82](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L82), [112](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L112), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L115), [148](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L148), [179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L179), [182](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L182) ):

```solidity
82:         address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);

112:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);

115:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);

148:         address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);

179:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);

182:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
```

## Non Critical Issues

### [N-01] Custom errors has no error details

Consider adding parameters to the error to indicate which user or values caused the failure.

<details>
<summary>There are 42 instances (click to show):</summary>

- *ERC20Custody.sol* ( [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L17), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L18), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L19), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L20), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L21) ):

```solidity
14:     error NotWhitelisted();

15:     error NotPaused();

16:     error InvalidSender();

17:     error InvalidTSSUpdater();

18:     error ZeroAddress();

19:     error IsPaused();

20:     error ZetaMaxFeeExceeded();

21:     error ZeroFee();
```

- *ConnectorErrors.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L21) ):

```solidity
21:     error ZetaTransferError();
```

- *ZetaErrors.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L24) ):

```solidity
21:     error InvalidAddress();

24:     error ZetaTransferError();
```

- *ZetaInteractorErrors.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L9), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L18) ):

```solidity
9:     error InvalidDestinationChainId();

15:     error InvalidZetaMessageCall();

18:     error InvalidZetaRevertCall();
```

- *ZetaInterfaces.sol* ( [109](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L109) ):

```solidity
109:     error InvalidAddress();
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L17) ):

```solidity
13:     error InputCantBeZero();

15:     error ErrorSendingETH();

17:     error ReentrancyError();
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L17) ):

```solidity
13:     error InputCantBeZero();

15:     error ErrorSendingETH();

17:     error ReentrancyError();
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L11) ):

```solidity
11:     error InputCantBeZero();
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L17) ):

```solidity
13:     error InputCantBeZero();

15:     error ErrorSendingETH();

17:     error ReentrancyError();
```

- *SystemContract.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L15) ):

```solidity
11:     error CallerIsNotFungibleModule();

12:     error InvalidTarget();

13:     error CantBeIdenticalAddresses();

14:     error CantBeZeroAddress();

15:     error ZeroAddress();
```

- *ZRC20.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L17) ):

```solidity
10:     error CallerIsNotFungibleModule();

11:     error InvalidSender();

12:     error GasFeeTransferFailed();

13:     error ZeroGasCoin();

14:     error ZeroGasPrice();

15:     error LowAllowance();

16:     error LowBalance();

17:     error ZeroAddress();
```

- *ZetaConnectorZEVM.sol* ( [57](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L57), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L58), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L59), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L60) ):

```solidity
57:     error OnlyWZETA();

58:     error WZETATransferFailed();

59:     error OnlyFungibleModule();

60:     error FailedZetaSent();
```

</details>

### [N-02] Import declarations should import specific identifiers, rather than the whole file

Using import declarations of the form `import {<identifier_name>} from "some/file.sol"` avoids polluting the symbol namespace making flattened files smaller, and speeds up compilation (but does not save any gas).

<details>
<summary>There are 50 instances (click to show):</summary>

- *ERC20Custody.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L7) ):

```solidity
5: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

6: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

7: import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
```

- *Zeta.eth.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
```

- *Zeta.non-eth.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L6), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L8) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

6: import "./interfaces/ZetaErrors.sol";

8: import "./interfaces/ZetaNonEthInterface.sol";
```

- *ZetaConnector.base.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L8) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

5: import "@openzeppelin/contracts/security/Pausable.sol";

7: import "./interfaces/ConnectorErrors.sol";

8: import "./interfaces/ZetaInterfaces.sol";
```

- *ZetaConnector.eth.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L8) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

6: import "./interfaces/ConnectorErrors.sol";

7: import "./ZetaConnector.base.sol";

8: import "./interfaces/ZetaInterfaces.sol";
```

- *ZetaConnector.non-eth.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L8) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

6: import "./ZetaConnector.base.sol";

7: import "./interfaces/ZetaInterfaces.sol";

8: import "./interfaces/ZetaNonEthInterface.sol";
```

- *ZetaNonEthInterface.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

- *ZetaInteractor.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L4), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L7) ):

```solidity
4: import "@openzeppelin/contracts/access/Ownable2Step.sol";

6: import "../interfaces/ZetaInterfaces.sol";

7: import "../interfaces/ZetaInteractorErrors.sol";
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L10) ):

```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6: import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

7: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";

8: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

10: import "../interfaces/ZetaInterfaces.sol";
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L6), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L8), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L9), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L10) ):

```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6: import "@uniswap/v3-periphery/contracts/interfaces/IQuoter.sol";

8: import "../interfaces/ZetaInterfaces.sol";

9: import "./interfaces/TridentConcentratedLiquidityPoolFactory.sol";

10: import "./interfaces/TridentIPoolRouter.sol";
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L6), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L8) ):

```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6: import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

8: import "../interfaces/ZetaInterfaces.sol";
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L10) ):

```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

6: import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

7: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";

8: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

10: import "../interfaces/ZetaInterfaces.sol";
```

- *SystemContract.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L4), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L5) ):

```solidity
4: import "./interfaces/zContract.sol";

5: import "./interfaces/IZRC20.sol";
```

- *UniswapPeriphery.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L4) ):

```solidity
4: import "@uniswap/v2-periphery/contracts/UniswapV2Router02.sol";
```

- *ZRC20.sol* ( [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L3) ):

```solidity
3: import "./Interfaces.sol";
```

- *IUniswapV2Router02.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L4) ):

```solidity
4: import "./IUniswapV2Router01.sol";
```

</details>

### [N-03] Event should include parameters

It is beneficial for events to include parameters. Including parameters in events allows you to provide additional information and context when emitting the event. This can be valuable for logging important state changes, or recording related accounts, or capturing relevant data.

There is 1 instance:

- *SystemContract.sol* ( [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L41) ):

```solidity
41:     event SystemContractDeployed();
```

### [N-04] Visibility of state variables is not explicitly defined

To avoid misunderstandings and unexpected state accesses, it is recommended to explicitly define the visibility of each state variable.

There is 1 instance:

- *ZetaInteractor.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10) ):

```solidity
10:     bytes32 constant ZERO_BYTES = keccak256(new bytes(0));
```

### [N-05] NatSpec documentation for contract is missing

e.g. `@dev` or `@notice`, and it must appear above the contract definition braces in order to be identified by the compiler as NatSpec.

<details>
<summary>There are 28 instances (click to show):</summary>

- *Zeta.non-eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10) ):

```solidity
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```

- *ZetaInterfaces.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108) ):

```solidity
4: interface ZetaInterfaces {

49: interface ZetaConnector {

56: interface ZetaReceiver {

108: interface ZetaCommonErrors {
```

- *ZetaInteractor.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9) ):

```solidity
9: abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {

24: interface ISwapRouterPancake is IUniswapV3SwapCallback {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerTridentErrors {

20: interface WETH9 {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10) ):

```solidity
10: interface ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16) ):

```solidity
16: interface ConcentratedLiquidityPoolFactory {
```

- *TridentIPoolRouter.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16) ):

```solidity
16: interface IPoolRouter {
```

- *Interfaces.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49) ):

```solidity
21: interface IZRC20 {

49: interface IZRC20Metadata is IZRC20 {
```

- *UniswapPeriphery.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6) ):

```solidity
6: contract UniswapImports {}
```

- *ZRC20.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20) ):

```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

- *ZetaConnectorZEVM.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55) ):

```solidity
4: interface ZetaInterfaces {

49: interface WZETA {

55: contract ZetaConnectorZEVM is ZetaInterfaces {
```

- *IUniswapV2Router01.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4) ):

```solidity
4: interface IUniswapV2Router01 {
```

- *IUniswapV2Router02.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6) ):

```solidity
6: interface IUniswapV2Router02 is IUniswapV2Router01 {
```

- *IWZETA.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4) ):

```solidity
4: interface IWETH9 {
```

- *IZRC20.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4) ):

```solidity
4: interface IZRC20 {
```

- *zContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10) ):

```solidity
10: interface zContract {
```

</details>

### [N-06] Names of `private`/`internal` functions should be prefixed with an underscore

It is recommended by the [Solidity Style Guide](https://docs.soliditylang.org/en/v0.8.20/style-guide.html#underscore-prefix-for-non-external-functions-and-variables).

There are 2 instances:

- *ZetaTokenConsumerTrident.strategy.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68) ):

```solidity
68:     function getPair(address token0, address token1) internal pure returns (address, address) {
```

- *SystemContract.sol* ( [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87) ):

```solidity
87:     function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
```

### [N-07] Names of `private`/`internal` state variables should be prefixed with an underscore

It is recommended by the [Solidity Style Guide](https://docs.soliditylang.org/en/v0.8.20/style-guide.html#underscore-prefix-for-non-external-functions-and-variables).

<details>
<summary>There are 9 instances (click to show):</summary>

- *ZetaInteractor.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11) ):

```solidity
10:     bytes32 constant ZERO_BYTES = keccak256(new bytes(0));

11:     uint256 internal immutable currentChainId;
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58) ):

```solidity
58:     uint256 internal constant MAX_DEADLINE = 200;
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37) ):

```solidity
35:     uint256 internal constant MAX_DEADLINE = 200;

37:     address internal immutable WETH9Address;
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24) ):

```solidity
19:     uint256 internal constant MAX_DEADLINE = 200;

21:     address internal immutable wETH;

24:     IUniswapV2Router02 internal immutable uniswapV2Router;
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29) ):

```solidity
29:     uint256 internal constant MAX_DEADLINE = 200;
```

</details>

### [N-08] Order of functions does not follow the Solidity Style Guide

According to the [Solidity Style Guide](https://docs.soliditylang.org/en/v0.8.20/style-guide.html#order-of-functions), functions should be grouped according to their visibility and ordered: `constructor`, `receive`, `fallback`, `external`, `public`, `internal`, `private`. Within a grouping, place the view and pure functions last.

<details>
<summary>There are 48 instances (click to show):</summary>

- *ZetaInteractor.sol* ( [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L43), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L50), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54) ):

```solidity
/// @audit ↓↓ Out of order with `_isValidChainId()`
43:     function _isValidCaller() private view {

/// @audit ↑↑ Out of order with `_isValidCaller()`
50:     function _isValidChainId(uint256 chainId) internal view returns (bool) {

/// @audit ↑↑ Out of order with `_isValidChainId()`
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68), [74-77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L77) ):

```solidity
/// @audit ↓↓ Out of order with `getZetaFromEth()`
68:     function getPair(address token0, address token1) internal pure returns (address, address) {

/// @audit ↑↑ Out of order with `getPair()`
74:     function getZetaFromEth(
75:         address destinationAddress,
76:         uint256 minAmountOut
77:     ) external payable override returns (uint256) {
```

- *Interfaces.sol* ( [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36) ):

```solidity
/// @audit ↓↓ Out of order with `transfer()`
24:     function balanceOf(address account) external view returns (uint256);

/// @audit ↑↑ Out of order with `balanceOf()`
26:     function transfer(address recipient, uint256 amount) external returns (bool);

/// @audit ↓↓ Out of order with `approve()`
28:     function allowance(address owner, address spender) external view returns (uint256);

/// @audit ↑↑ Out of order with `allowance()`
30:     function approve(address spender, uint256 amount) external returns (bool);

/// @audit ↑↑ Out of order with `approve()`
32:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

/// @audit ↑↑ Out of order with `transferFrom()`
34:     function deposit(address to, uint256 amount) external returns (bool);

/// @audit ↑↑ Out of order with `deposit()`
36:     function withdraw(bytes memory to, uint256 amount) external returns (bool);
```

- *SystemContract.sol* ( [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L100), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123) ):

```solidity
/// @audit ↓↓ Out of order with `uniswapv2PairFor()`
87:     function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {

/// @audit ↑↑ Out of order with `sortTokens()`
100:     function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {

/// @audit ↑↑ Out of order with `uniswapv2PairFor()`
123:     function setGasPrice(uint256 chainID, uint256 price) external {
```

- *ZRC20.sol* ( [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L45), [60-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L68), [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L116), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173), [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L178), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L191), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L199), [211](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L211), [225](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225), [236](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236), [256](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256), [270](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270), [279](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L279), [288](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L288) ):

```solidity
/// @audit ↓↓ Out of order with `constructor()`
45:     function _msgData() internal view virtual returns (bytes calldata) {

/// @audit ↑↑ Out of order with `_msgData()`
60:     constructor(
61:         string memory name_,
62:         string memory symbol_,
63:         uint8 decimals_,
64:         uint256 chainid_,
65:         CoinType coinType_,
66:         uint256 gasLimit_,
67:         address systemContractAddress_
68:     ) {

/// @audit ↓↓ Out of order with `transfer()`
116:     function balanceOf(address account) public view virtual override returns (uint256) {

/// @audit ↑↑ Out of order with `balanceOf()`
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {

/// @audit ↓↓ Out of order with `approve()`
135:     function allowance(address owner, address spender) public view virtual override returns (uint256) {

/// @audit ↑↑ Out of order with `allowance()`
145:     function approve(address spender, uint256 amount) public virtual override returns (bool) {

/// @audit ↑↑ Out of order with `approve()`
157:     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {

/// @audit ↑↑ Out of order with `transferFrom()`
173:     function burn(uint256 amount) external returns (bool) {

/// @audit ↓↓ Out of order with `_mint()`
178:     function _transfer(address sender, address recipient, uint256 amount) internal virtual {

/// @audit ↑↑ Out of order with `_transfer()`
191:     function _mint(address account, uint256 amount) internal virtual {

/// @audit ↑↑ Out of order with `_mint()`
199:     function _burn(address account, uint256 amount) internal virtual {

/// @audit ↑↑ Out of order with `_burn()`
211:     function _approve(address owner, address spender, uint256 amount) internal virtual {

/// @audit ↑↑ Out of order with `_approve()`
225:     function deposit(address to, uint256 amount) external override returns (bool) {

/// @audit ↓↓ Out of order with `withdraw()`
236:     function withdrawGasFee() public view override returns (address, uint256) {

/// @audit ↑↑ Out of order with `withdrawGasFee()`
256:     function withdraw(bytes memory to, uint256 amount) external override returns (bool) {

/// @audit ↑↑ Out of order with `withdraw()`
270:     function updateSystemContractAddress(address addr) external onlyFungible {

/// @audit ↑↑ Out of order with `updateSystemContractAddress()`
279:     function updateGasLimit(uint256 gasLimit) external onlyFungible {

/// @audit ↑↑ Out of order with `updateGasLimit()`
288:     function updateProtocolFlatFee(uint256 protocolFlatFee) external onlyFungible {
```

- *IUniswapV2Router01.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7), [9-18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18), [20-27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27), [29-37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L37), [39-46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L46), [48-60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60), [62-73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73), [75-81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L81), [83-89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L89), [91-96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91-L96), [98-104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L104), [106-112](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L112), [114-119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114-L119) ):

```solidity
/// @audit ↓↓ Out of order with `addLiquidity()`
7:     function WETH() external pure returns (address);

/// @audit ↑↑ Out of order with `WETH()`
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

/// @audit ↑↑ Out of order with `addLiquidity()`
20:     function addLiquidityETH(
21:         address token,
22:         uint amountTokenDesired,
23:         uint amountTokenMin,
24:         uint amountETHMin,
25:         address to,
26:         uint deadline
27:     ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

/// @audit ↑↑ Out of order with `addLiquidityETH()`
29:     function removeLiquidity(
30:         address tokenA,
31:         address tokenB,
32:         uint liquidity,
33:         uint amountAMin,
34:         uint amountBMin,
35:         address to,
36:         uint deadline
37:     ) external returns (uint amountA, uint amountB);

/// @audit ↑↑ Out of order with `removeLiquidity()`
39:     function removeLiquidityETH(
40:         address token,
41:         uint liquidity,
42:         uint amountTokenMin,
43:         uint amountETHMin,
44:         address to,
45:         uint deadline
46:     ) external returns (uint amountToken, uint amountETH);

/// @audit ↑↑ Out of order with `removeLiquidityETH()`
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

/// @audit ↑↑ Out of order with `removeLiquidityWithPermit()`
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

/// @audit ↑↑ Out of order with `removeLiquidityETHWithPermit()`
75:     function swapExactTokensForTokens(
76:         uint amountIn,
77:         uint amountOutMin,
78:         address[] calldata path,
79:         address to,
80:         uint deadline
81:     ) external returns (uint[] memory amounts);

/// @audit ↑↑ Out of order with `swapExactTokensForTokens()`
83:     function swapTokensForExactTokens(
84:         uint amountOut,
85:         uint amountInMax,
86:         address[] calldata path,
87:         address to,
88:         uint deadline
89:     ) external returns (uint[] memory amounts);

/// @audit ↑↑ Out of order with `swapTokensForExactTokens()`
91:     function swapExactETHForTokens(
92:         uint amountOutMin,
93:         address[] calldata path,
94:         address to,
95:         uint deadline
96:     ) external payable returns (uint[] memory amounts);

/// @audit ↑↑ Out of order with `swapExactETHForTokens()`
98:     function swapTokensForExactETH(
99:         uint amountOut,
100:         uint amountInMax,
101:         address[] calldata path,
102:         address to,
103:         uint deadline
104:     ) external returns (uint[] memory amounts);

/// @audit ↑↑ Out of order with `swapTokensForExactETH()`
106:     function swapExactTokensForETH(
107:         uint amountIn,
108:         uint amountOutMin,
109:         address[] calldata path,
110:         address to,
111:         uint deadline
112:     ) external returns (uint[] memory amounts);

/// @audit ↑↑ Out of order with `swapExactTokensForETH()`
114:     function swapETHForExactTokens(
115:         uint amountOut,
116:         address[] calldata path,
117:         address to,
118:         uint deadline
119:     ) external payable returns (uint[] memory amounts);
```

- *IWZETA.sol* ( [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24) ):

```solidity
/// @audit ↓↓ Out of order with `approve()`
14:     function allowance(address owner, address spender) external view returns (uint);

/// @audit ↑↑ Out of order with `allowance()`
16:     function approve(address spender, uint wad) external returns (bool);

/// @audit ↑↑ Out of order with `approve()`
18:     function transfer(address to, uint wad) external returns (bool);

/// @audit ↑↑ Out of order with `transfer()`
20:     function transferFrom(address from, address to, uint wad) external returns (bool);

/// @audit ↑↑ Out of order with `transferFrom()`
22:     function deposit() external payable;

/// @audit ↑↑ Out of order with `deposit()`
24:     function withdraw(uint wad) external;
```

- *IZRC20.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25) ):

```solidity
/// @audit ↓↓ Out of order with `transfer()`
7:     function balanceOf(address account) external view returns (uint256);

/// @audit ↑↑ Out of order with `balanceOf()`
9:     function transfer(address recipient, uint256 amount) external returns (bool);

/// @audit ↓↓ Out of order with `approve()`
11:     function allowance(address owner, address spender) external view returns (uint256);

/// @audit ↑↑ Out of order with `allowance()`
13:     function approve(address spender, uint256 amount) external returns (bool);

/// @audit ↑↑ Out of order with `approve()`
15:     function decreaseAllowance(address spender, uint256 amount) external returns (bool);

/// @audit ↑↑ Out of order with `decreaseAllowance()`
17:     function increaseAllowance(address spender, uint256 amount) external returns (bool);

/// @audit ↑↑ Out of order with `increaseAllowance()`
19:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

/// @audit ↑↑ Out of order with `transferFrom()`
21:     function deposit(address to, uint256 amount) external returns (bool);

/// @audit ↑↑ Out of order with `deposit()`
23:     function burn(address account, uint256 amount) external returns (bool);

/// @audit ↑↑ Out of order with `burn()`
25:     function withdraw(bytes memory to, uint256 amount) external returns (bool);
```

</details>

### [N-09] Redundant inheritance specifier

The contracts below already extend the specified contract, so there is no need to list it in the inheritance list again.

There is 1 instance:

- *ZRC20.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20) ):

```solidity
/// @audit IZRC20Metadata already extends IZRC20
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

### [N-10] Unused errors

The following `error`s are defined but not used. It is recommended to check the code for logical omissions that cause them not to be used. If it's determined that they are not needed anywhere, it's best to remove them from the codebase to improve code clarity and minimize confusion.
Note that there may be cases where an error appears to be used because it has multiple definitions in different files. In such cases, the definitions should be moved to a separate file.

There is 1 instance:

- *ZetaInteractorErrors.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L9) ):

```solidity
9:     error InvalidDestinationChainId();
```

### [N-11] Unused `internal` functions can be removed

All unused code should be removed or commented out. If the functions are required by an interface, the contract should inherit from that interface and use the override keyword.

There is 1 instance:

- *ZetaInteractor.sol* ( [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L50) ):

```solidity
50:     function _isValidChainId(uint256 chainId) internal view returns (bool) {
```

### [N-12] Use `uint256`/`int256` instead of `uint`/`int`

It is recommended to use `uint256`/`int256` instead of `uint`/`int` in function parameters, since they are used for function signatures.

<details>
<summary>There are 108 instances (click to show):</summary>

- *ZetaConnectorZEVM.sol* ( [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52) ):

```solidity
/// @audit uint wad
50:     function transferFrom(address src, address dst, uint wad) external returns (bool);

/// @audit uint wad
52:     function withdraw(uint wad) external;
```

- *IUniswapV2Router01.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L17), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L22), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L23), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L26), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L27), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L37), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L43), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L46), [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L51), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L52), [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L53), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L55), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L60), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L64), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L65), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L68), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L73), [76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L77), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L80), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L81), [84](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L84), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L85), [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L88), [89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L89), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L92), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L95), [96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L96), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L99), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L100), [103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L103), [104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L104), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L107), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L108), [111](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L111), [112](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L112), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L115), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L118), [119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L119), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129) ):

```solidity
/// @audit uint amountADesired
12:         uint amountADesired,

/// @audit uint amountBDesired
13:         uint amountBDesired,

/// @audit uint amountAMin
14:         uint amountAMin,

/// @audit uint amountBMin
15:         uint amountBMin,

/// @audit uint deadline
17:         uint deadline

/// @audit uint amountA
/// @audit uint amountB
/// @audit uint liquidity
18:     ) external returns (uint amountA, uint amountB, uint liquidity);

/// @audit uint amountTokenDesired
22:         uint amountTokenDesired,

/// @audit uint amountTokenMin
23:         uint amountTokenMin,

/// @audit uint amountETHMin
24:         uint amountETHMin,

/// @audit uint deadline
26:         uint deadline

/// @audit uint amountToken
/// @audit uint amountETH
/// @audit uint liquidity
27:     ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

/// @audit uint liquidity
32:         uint liquidity,

/// @audit uint amountAMin
33:         uint amountAMin,

/// @audit uint amountBMin
34:         uint amountBMin,

/// @audit uint deadline
36:         uint deadline

/// @audit uint amountA
/// @audit uint amountB
37:     ) external returns (uint amountA, uint amountB);

/// @audit uint liquidity
41:         uint liquidity,

/// @audit uint amountTokenMin
42:         uint amountTokenMin,

/// @audit uint amountETHMin
43:         uint amountETHMin,

/// @audit uint deadline
45:         uint deadline

/// @audit uint amountToken
/// @audit uint amountETH
46:     ) external returns (uint amountToken, uint amountETH);

/// @audit uint liquidity
51:         uint liquidity,

/// @audit uint amountAMin
52:         uint amountAMin,

/// @audit uint amountBMin
53:         uint amountBMin,

/// @audit uint deadline
55:         uint deadline,

/// @audit uint amountA
/// @audit uint amountB
60:     ) external returns (uint amountA, uint amountB);

/// @audit uint liquidity
64:         uint liquidity,

/// @audit uint amountTokenMin
65:         uint amountTokenMin,

/// @audit uint amountETHMin
66:         uint amountETHMin,

/// @audit uint deadline
68:         uint deadline,

/// @audit uint amountToken
/// @audit uint amountETH
73:     ) external returns (uint amountToken, uint amountETH);

/// @audit uint amountIn
76:         uint amountIn,

/// @audit uint amountOutMin
77:         uint amountOutMin,

/// @audit uint deadline
80:         uint deadline

/// @audit uint[] memory amounts
81:     ) external returns (uint[] memory amounts);

/// @audit uint amountOut
84:         uint amountOut,

/// @audit uint amountInMax
85:         uint amountInMax,

/// @audit uint deadline
88:         uint deadline

/// @audit uint[] memory amounts
89:     ) external returns (uint[] memory amounts);

/// @audit uint amountOutMin
92:         uint amountOutMin,

/// @audit uint deadline
95:         uint deadline

/// @audit uint[] memory amounts
96:     ) external payable returns (uint[] memory amounts);

/// @audit uint amountOut
99:         uint amountOut,

/// @audit uint amountInMax
100:         uint amountInMax,

/// @audit uint deadline
103:         uint deadline

/// @audit uint[] memory amounts
104:     ) external returns (uint[] memory amounts);

/// @audit uint amountIn
107:         uint amountIn,

/// @audit uint amountOutMin
108:         uint amountOutMin,

/// @audit uint deadline
111:         uint deadline

/// @audit uint[] memory amounts
112:     ) external returns (uint[] memory amounts);

/// @audit uint amountOut
115:         uint amountOut,

/// @audit uint deadline
118:         uint deadline

/// @audit uint[] memory amounts
119:     ) external payable returns (uint[] memory amounts);

/// @audit uint amountA
/// @audit uint reserveA
/// @audit uint reserveB
/// @audit uint amountB
121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

/// @audit uint amountIn
/// @audit uint reserveIn
/// @audit uint reserveOut
/// @audit uint amountOut
123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

/// @audit uint amountOut
/// @audit uint reserveIn
/// @audit uint reserveOut
/// @audit uint amountIn
125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

/// @audit uint amountIn
/// @audit uint[] memory amounts
127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

/// @audit uint amountOut
/// @audit uint[] memory amounts
129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);
```

- *IUniswapV2Router02.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L9), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L14), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L18), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L19), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L22), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L27), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L30), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L31), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L34), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L38), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L41), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L46), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L49) ):

```solidity
/// @audit uint liquidity
9:         uint liquidity,

/// @audit uint amountTokenMin
10:         uint amountTokenMin,

/// @audit uint amountETHMin
11:         uint amountETHMin,

/// @audit uint deadline
13:         uint deadline

/// @audit uint amountETH
14:     ) external returns (uint amountETH);

/// @audit uint liquidity
18:         uint liquidity,

/// @audit uint amountTokenMin
19:         uint amountTokenMin,

/// @audit uint amountETHMin
20:         uint amountETHMin,

/// @audit uint deadline
22:         uint deadline,

/// @audit uint amountETH
27:     ) external returns (uint amountETH);

/// @audit uint amountIn
30:         uint amountIn,

/// @audit uint amountOutMin
31:         uint amountOutMin,

/// @audit uint deadline
34:         uint deadline

/// @audit uint amountOutMin
38:         uint amountOutMin,

/// @audit uint deadline
41:         uint deadline

/// @audit uint amountIn
45:         uint amountIn,

/// @audit uint amountOutMin
46:         uint amountOutMin,

/// @audit uint deadline
49:         uint deadline
```

- *IWZETA.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24) ):

```solidity
/// @audit uint value
5:     event Approval(address indexed owner, address indexed spender, uint value);

/// @audit uint value
6:     event Transfer(address indexed from, address indexed to, uint value);

/// @audit uint wad
7:     event Deposit(address indexed dst, uint wad);

/// @audit uint wad
8:     event Withdrawal(address indexed src, uint wad);

/// @audit uint
10:     function totalSupply() external view returns (uint);

/// @audit uint
12:     function balanceOf(address owner) external view returns (uint);

/// @audit uint
14:     function allowance(address owner, address spender) external view returns (uint);

/// @audit uint wad
16:     function approve(address spender, uint wad) external returns (bool);

/// @audit uint wad
18:     function transfer(address to, uint wad) external returns (bool);

/// @audit uint wad
20:     function transferFrom(address from, address to, uint wad) external returns (bool);

/// @audit uint wad
24:     function withdraw(uint wad) external;
```

</details>

### [N-13] Consider moving `msg.sender` checks to `modifier`s

If some functions are only allowed to be called by some specific users, consider using a modifier instead of checking with a require statement, especially if this check is done in multiple functions.

<details>
<summary>There are 19 instances (click to show):</summary>

- *Zeta.non-eth.sol* ( [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L41), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L55), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L66), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L77) ):

```solidity
41:         if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);

55:         if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);

66:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);

77:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
```

- *ZetaConnector.base.sol* ( [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L129) ):

```solidity
129:         if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);
```

- *ZetaInteractor.sol* ( [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L44) ):

```solidity
44:         if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
```

- *SystemContract.sol* ( [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135), [146](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168) ):

```solidity
52:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

74:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

124:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

135:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

146:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

157:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

168:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

- *ZRC20.sol* ( [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69), [226](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226), [258-260](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258-L260) ):

```solidity
69:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();

258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
259:             revert GasFeeTransferFailed();
260:         }
```

- *ZetaConnectorZEVM.sol* ( [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L85), [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L94), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115) ):

```solidity
85:         if (msg.sender != wzeta) revert OnlyWZETA();

94:         if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();

115:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
```

</details>

### [N-14] Missing checks for empty bytes when updating bytes state variables

Unless the code is attempting to `delete` the state variable, the caller shouldn't have to write `""` to the state variable

There is 1 instance:

- *ZetaInteractor.sol* ( [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L55) ):

```solidity
55:         interactorsByChainId[destinationChainId] = contractAddress;
```

### [N-15] Consider adding a block/deny-list

Doing so will significantly increase centralization, but will help to prevent hackers from using stolen tokens

<details>
<summary>There are 8 instances (click to show):</summary>

- *ERC20Custody.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11) ):

```solidity
11: contract ERC20Custody is ReentrancyGuard {
```

- *ZetaConnector.eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15) ):

```solidity
15: contract ZetaConnectorEth is ZetaConnectorBase {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56) ):

```solidity
56: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33) ):

```solidity
33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17) ):

```solidity
17: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27) ):

```solidity
27: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *ZRC20.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20) ):

```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

- *ZetaConnectorZEVM.sol* ( [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55) ):

```solidity
55: contract ZetaConnectorZEVM is ZetaInterfaces {
```

</details>

### [N-16] Constants/Immutables redefined elsewhere

Consider defining in only one contract so that values cannot become out of sync when only one location is updated. A [cheap way](https://medium.com/coinmonks/gas-cost-of-solidity-library-functions-dbe0cedd4678) to store constants/immutables in a single location is to create an `internal constant` in a `library`. If the variable is a local cache of another contract's value, consider making the cache variable internal or private, which will require external users to query the contract with the source of truth, so that callers don't get out of sync.

<details>
<summary>There are 21 instances (click to show):</summary>

- *ZetaConnector.base.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L16) ):

```solidity
/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#22
16:     address public immutable zetaToken;
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L60), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L61), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L63), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L64), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L67) ):

```solidity
/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#35
58:     uint256 internal constant MAX_DEADLINE = 200;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#31
60:     uint24 public immutable zetaPoolFee;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#32
61:     uint24 public immutable tokenPoolFee;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#37
63:     address public immutable WETH9Address;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#38
64:     address public immutable zetaToken;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#38
67:     IUniswapV3Factory public immutable uniswapV3Factory;
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L38) ):

```solidity
/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#58
35:     uint256 internal constant MAX_DEADLINE = 200;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#63
37:     address internal immutable WETH9Address;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#64
38:     address public immutable zetaToken;
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L22) ):

```solidity
/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#29
19:     uint256 internal constant MAX_DEADLINE = 200;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#35
22:     address public immutable zetaToken;
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L35), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L38) ):

```solidity
/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#35
29:     uint256 internal constant MAX_DEADLINE = 200;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#60
31:     uint24 public immutable zetaPoolFee;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#61
32:     uint24 public immutable tokenPoolFee;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#37
34:     address public immutable WETH9Address;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#38
35:     address public immutable zetaToken;

/// @audit Seen in contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#67
38:     IUniswapV3Factory public immutable uniswapV3Factory;
```

- *SystemContract.sol* ( [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L31) ):

```solidity
/// @audit Seen in contracts/zevm/ZRC20.sol#22
31:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

- *ZRC20.sol* ( [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22) ):

```solidity
/// @audit Seen in contracts/zevm/SystemContract.sol#31
22:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

- *ZetaConnectorZEVM.sol* ( [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63) ):

```solidity
/// @audit Seen in contracts/zevm/SystemContract.sol#31
63:     address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
```

</details>

### [N-17] Contracts should each be defined in separate files

Keeping each contract in a separate file makes it easier to work with multiple people, makes the code easier to maintain, and is a common practice on most projects. The following files each contains more than one contract/library/interface.

There are 9 instances:

- [*ZetaInterfaces.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol)

- [*ZetaTokenConsumerPancakeV3.strategy.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol)

- [*ZetaTokenConsumerTrident.strategy.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol)

- [*ZetaTokenConsumerUniV2.strategy.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol)

- [*ZetaTokenConsumerUniV3.strategy.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol)

- [*Interfaces.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol)

- [*SystemContract.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol)

- [*ZRC20.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol)

- [*ZetaConnectorZEVM.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol)

### [N-18] Contract name does not match its filename

According to the [Solidity Style Guide](https://docs.soliditylang.org/en/latest/style-guide.html#contract-and-library-names), contract and library names should also match their filenames.

<details>
<summary>There are 9 instances (click to show):</summary>

- *Zeta.eth.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9) ):

```solidity
/// @audit Not match filename `Zeta.eth.sol`
9: contract ZetaEth is ERC20("Zeta", "ZETA") {
```

- *Zeta.non-eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10) ):

```solidity
/// @audit Not match filename `Zeta.non-eth.sol`
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```

- *ZetaConnector.base.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15) ):

```solidity
/// @audit Not match filename `ZetaConnector.base.sol`
15: contract ZetaConnectorBase is ConnectorErrors, Pausable {
```

- *ZetaConnector.eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15) ):

```solidity
/// @audit Not match filename `ZetaConnector.eth.sol`
15: contract ZetaConnectorEth is ZetaConnectorBase {
```

- *ZetaConnector.non-eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15) ):

```solidity
/// @audit Not match filename `ZetaConnector.non-eth.sol`
15: contract ZetaConnectorNonEth is ZetaConnectorBase {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16) ):

```solidity
/// @audit Not match filename `TridentConcentratedLiquidityPoolFactory.sol`
16: interface ConcentratedLiquidityPoolFactory {
```

- *TridentIPoolRouter.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16) ):

```solidity
/// @audit Not match filename `TridentIPoolRouter.sol`
16: interface IPoolRouter {
```

- *UniswapPeriphery.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6) ):

```solidity
/// @audit Not match filename `UniswapPeriphery.sol`
6: contract UniswapImports {}
```

- *IWZETA.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4) ):

```solidity
/// @audit Not match filename `IWZETA.sol`
4: interface IWETH9 {
```

</details>

### [N-19] UPPER_CASE names should be reserved for `constant`/`immutable` variables

If the variable needs to be different based on which class it comes from, a `view`/`pure` _function_ should be used instead (e.g. like [this](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/76eee35971c2541585e05cbf258510dda7b2fbc6/contracts/token/ERC20/extensions/draft-IERC20Permit.sol#L59)).

There are 3 instances:

- *ZRC20.sol* ( [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L32) ):

```solidity
28:     address public SYSTEM_CONTRACT_ADDRESS;

30:     uint256 public GAS_LIMIT;

32:     uint256 public PROTOCOL_FLAT_FEE;
```

### [N-20] Do not use literal numbers for array indexes

Indexing arrays using enums or meaningfully named constants instead of literals can make code easier to read and maintain.

<details>
<summary>There are 26 instances (click to show):</summary>

- *ZetaTokenConsumerTrident.strategy.sol* ( [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L88), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L118), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L118), [119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L119), [119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L119), [154](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L154), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L185), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L185), [186](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L186), [186](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L186) ):

```solidity
88:             pool: pairPools[0],

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

- *ZetaTokenConsumerUniV2.strategy.sol* ( [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L43), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L73), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L74), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L77), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L79), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L107), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L108), [139](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L139), [140](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L140), [143](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L143), [144](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L144), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L145), [164](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L164), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L165) ):

```solidity
42:         path[0] = wETH;

43:         path[1] = zetaToken;

73:             path[0] = wETH;

74:             path[1] = zetaToken;

77:             path[0] = inputToken;

78:             path[1] = wETH;

79:             path[2] = zetaToken;

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

</details>

### [N-21] Events should be emitted before external calls

Ensure that events follow the best practice of check-effects-interaction, and are emitted before external calls.

<details>
<summary>There are 26 instances (click to show):</summary>

- *ERC20Custody.sol* ( [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L184), [198](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L198) ):

```solidity
/// @audit `safeTransferFrom()` is called on line 181
184:         emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);

/// @audit `safeTransfer()` is called on line 197
198:         emit Withdrawn(recipient, asset, amount);
```

- *ZetaConnector.eth.sol* ( [35-44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L35-L44), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L69), [102-110](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L102-L110) ):

```solidity
/// @audit `transferFrom()` is called on line 32
35:         emit ZetaSent(
36:             tx.origin,
37:             msg.sender,
38:             input.destinationChainId,
39:             input.destinationAddress,
40:             input.zetaValueAndGas,
41:             input.destinationGasLimit,
42:             input.message,
43:             input.zetaParams
44:         );

/// @audit `transfer()` is called on line 60
69:         emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);

/// @audit `transfer()` is called on line 86
102:         emit ZetaReverted(
103:             zetaTxSenderAddress,
104:             sourceChainId,
105:             destinationChainId,
106:             destinationAddress,
107:             remainingZetaValue,
108:             message,
109:             internalSendHash
110:         );
```

- *ZetaConnector.non-eth.sol* ( [43-52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L43-L52), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L78), [113-121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L113-L121) ):

```solidity
/// @audit `burnFrom()` is called on line 41
43:         emit ZetaSent(
44:             tx.origin,
45:             msg.sender,
46:             input.destinationChainId,
47:             input.destinationAddress,
48:             input.zetaValueAndGas,
49:             input.destinationGasLimit,
50:             input.message,
51:             input.zetaParams
52:         );

/// @audit `mint()` is called on line 70
78:         emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);

/// @audit `mint()` is called on line 98
113:         emit ZetaReverted(
114:             zetaTxSenderAddress,
115:             sourceChainId,
116:             destinationChainId,
117:             destinationAddress,
118:             remainingZetaValue,
119:             message,
120:             internalSendHash
121:         );
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [122](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L122), [147](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L147), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176), [205](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L205) ):

```solidity
/// @audit `exactInputSingle()` is called on line 120
122:         emit EthExchangedForZeta(msg.value, amountOut);

/// @audit `safeTransferFrom()` is called on line 135
147:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

/// @audit `safeTransferFrom()` is called on line 159
176:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

/// @audit `safeTransferFrom()` is called on line 193
205:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L95), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L132), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L161), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L199) ):

```solidity
/// @audit `exactInputSingle()` is called on line 93
95:         emit EthExchangedForZeta(msg.value, amountOut);

/// @audit `safeTransferFrom()` is called on line 108
132:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

/// @audit `safeTransferFrom()` is called on line 144
161:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

/// @audit `safeTransferFrom()` is called on line 175
199:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L54), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L91), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L120), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L158) ):

```solidity
/// @audit `swapExactETHForTokens()` is called on line 45
54:         emit EthExchangedForZeta(msg.value, amountOut);

/// @audit `safeTransferFrom()` is called on line 67
91:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

/// @audit `safeTransferFrom()` is called on line 103
120:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

/// @audit `safeTransferFrom()` is called on line 133
158:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L94), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L120), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L180) ):

```solidity
/// @audit `exactInputSingle()` is called on line 92
94:         emit EthExchangedForZeta(msg.value, amountOut);

/// @audit `safeTransferFrom()` is called on line 107
120:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

/// @audit `safeTransferFrom()` is called on line 132
150:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

/// @audit `safeTransferFrom()` is called on line 167
180:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```

- *ZRC20.sol* ( [262](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L262) ):

```solidity
/// @audit `transferFrom()` is called on line 258
262:         emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);
```

- *ZetaConnectorZEVM.sol* ( [98-107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L98-L107) ):

```solidity
/// @audit `withdraw()` is called on line 95
98:         emit ZetaSent(
99:             tx.origin,
100:             msg.sender,
101:             input.destinationChainId,
102:             input.destinationAddress,
103:             input.zetaValueAndGas,
104:             input.destinationGasLimit,
105:             input.message,
106:             input.zetaParams
107:         );
```

</details>

### [N-22] Empty function body without comments

Empty function body in solidity is not recommended, consider adding some comments to the body.

<details>
<summary>There are 6 instances (click to show):</summary>

- *ZetaConnector.base.sol* ( [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166), [172-179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185-193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193) ):

```solidity
166:     function send(ZetaInterfaces.SendInput calldata input) external virtual {}

172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

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

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101) ):

```solidity
101:     receive() external payable {}
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66) ):

```solidity
66:     receive() external payable {}
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72) ):

```solidity
72:     receive() external payable {}
```

</details>

### [N-23] Events are emitted without the sender information

When an action is triggered based on a user's action, not being able to filter based on who triggered the action makes event processing a lot more cumbersome. Including the `msg.sender` the events of these types of action will make events much more useful to end users, especially when `msg.sender` is not `tx.origin`.

<details>
<summary>There are 34 instances (click to show):</summary>

- *ERC20Custody.sol* ( [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L85), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L100), [146](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L146), [155](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L155), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L184), [198](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L198) ):

```solidity
85:         emit UpdatedTSSAddress(TSSAddress_);

100:         emit UpdatedZetaFee(zetaFee_);

146:         emit Whitelisted(asset);

155:         emit Unwhitelisted(asset);

184:         emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);

198:         emit Withdrawn(recipient, asset, amount);
```

- *Zeta.non-eth.sol* ( [70](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L70), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L81) ):

```solidity
70:         emit Minted(mintee, value, internalSendHash);

81:         emit Burnt(account, amount);
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [122](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L122), [147](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L147), [176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176), [205](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L205) ):

```solidity
122:         emit EthExchangedForZeta(msg.value, amountOut);

147:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

176:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

205:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L95), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L132), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L161), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L199) ):

```solidity
95:         emit EthExchangedForZeta(msg.value, amountOut);

132:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

161:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

199:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L54), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L91), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L120), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L158) ):

```solidity
54:         emit EthExchangedForZeta(msg.value, amountOut);

91:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

120:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

158:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L94), [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L120), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L180) ):

```solidity
94:         emit EthExchangedForZeta(msg.value, amountOut);

120:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);

150:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);

180:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```

- *SystemContract.sol* ( [126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L126), [137](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L137), [149](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L149), [160](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L160), [171](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L171) ):

```solidity
126:         emit SetGasPrice(chainID, price);

137:         emit SetGasCoin(chainID, zrc20);

149:         emit SetGasZetaPool(chainID, pool);

160:         emit SetWZeta(wZetaContractAddress);

171:         emit SetConnectorZEVM(zetaConnectorZEVMAddress);
```

- *ZRC20.sol* ( [228](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L228), [272](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L272), [281](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L281), [290](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L290) ):

```solidity
228:         emit Deposit(abi.encodePacked(FUNGIBLE_MODULE_ADDRESS), to, amount);

272:         emit UpdatedSystemContract(addr);

281:         emit UpdatedGasLimit(gasLimit);

290:         emit UpdatedProtocolFlatFee(protocolFlatFee);
```

- *ZetaConnectorZEVM.sol* ( [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L117) ):

```solidity
117:         emit SetWZETA(wzeta_);
```

</details>

### [N-24] Event is missing `indexed` fields

Index event fields makes the field more quickly accessible to [off-chain tools](https://ethereum.stackexchange.com/questions/40396/can-somebody-please-explain-the-concept-of-event-indexing) that parse events. However, note that each indexed field costs extra gas during emission, so it's not necessarily best to index the maximum allowed per event (three fields). Each event should use three indexed fields if there are three or more fields, and gas usage is not particularly of concern for the events in question. If there are fewer than three fields, all of the fields should be indexed.

<details>
<summary>There are 23 instances (click to show):</summary>

- *ERC20Custody.sol* ( [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45) ):

```solidity
38:     event Paused(address sender);

39:     event Unpaused(address sender);

44:     event RenouncedTSSUpdater(address TSSAddressUpdater_);

45:     event UpdatedTSSAddress(address TSSAddress_);
```

- *Zeta.non-eth.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31) ):

```solidity
27:     event TSSAddressUpdated(address callerAddress, address newTssAddress);

29:     event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

31:     event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);
```

- *ZetaConnector.base.sol* ( [34-43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34-L43), [54-62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L62), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68) ):

```solidity
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

- *ZetaConnector.non-eth.sol* ( [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18) ):

```solidity
18:     event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
```

- *ZetaInterfaces.sol* ( [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81) ):

```solidity
79:     event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

81:     event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
```

- *Interfaces.sol* ( [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44) ):

```solidity
44:     event UpdatedSystemContract(address systemContract);
```

- *SystemContract.sol* ( [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46) ):

```solidity
43:     event SetGasCoin(uint256, address);

44:     event SetGasZetaPool(uint256, address);

45:     event SetWZeta(address);

46:     event SetConnectorZEVM(address);
```

- *ZetaConnectorZEVM.sol* ( [67-76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77) ):

```solidity
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

- *IZRC20.sol* ( [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35) ):

```solidity
35:     event UpdatedSystemContract(address systemContract);
```

</details>

### [N-25] Inconsistent floating version pragma

Source files are using different floating version syntax, this is prone to compilation errors, and is not conducive to the code reliability and maintainability.

There are 2 instances:

- *TridentIPoolRouter.sol* ( [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14) ):

```solidity
14: pragma solidity >=0.8.0;
```

- [*WZETA.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol)

### [N-26] Function state mutability can be restricted to pure

Function state mutability can be restricted to pure

<details>
<summary>There are 5 instances (click to show):</summary>

- *ZetaConnector.base.sol* ( [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166), [172-179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185-193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193) ):

```solidity
166:     function send(ZetaInterfaces.SendInput calldata input) external virtual {}

172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

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

- *ZetaTokenConsumerTrident.strategy.sol* ( [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203) ):

```solidity
203:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZRC20.sol* ( [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L45) ):

```solidity
45:     function _msgData() internal view virtual returns (bytes calldata) {
```

</details>

### [N-27] Imports could be organized more systematically

The contract's interface should be imported first, followed by each of the interfaces it uses, followed by all other files. The examples below do not follow this layout.

<details>
<summary>There are 10 instances (click to show):</summary>

- *Zeta.non-eth.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L8) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
8: import "./interfaces/ZetaNonEthInterface.sol";
```

- *ZetaConnector.base.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L8) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
8: import "./interfaces/ZetaInterfaces.sol";
```

- *ZetaConnector.eth.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L8) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
8: import "./interfaces/ZetaInterfaces.sol";
```

- *ZetaConnector.non-eth.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L7) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
7: import "./interfaces/ZetaInterfaces.sol";
```

- *ZetaInteractor.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L6) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
6: import "../interfaces/ZetaInterfaces.sol";
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L6) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
6: import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L6) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
6: import "@uniswap/v3-periphery/contracts/interfaces/IQuoter.sol";
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L6) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
6: import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L6) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
6: import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
```

- *SystemContract.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L5) ):

```solidity
/// @audit Out of order with the prev import️ ⬆
5: import "./interfaces/IZRC20.sol";
```

</details>

### [N-28] Interfaces should be indicated with an `I` prefix in the contract name

Interfaces should be indicated with an `I` prefix in the contract name

<details>
<summary>There are 22 instances (click to show):</summary>

- *ConnectorErrors.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7) ):

```solidity
7: interface ConnectorErrors {
```

- *ZetaErrors.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7) ):

```solidity
7: interface ZetaErrors {
```

- *ZetaInteractorErrors.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7) ):

```solidity
7: interface ZetaInteractorErrors {
```

- *ZetaInterfaces.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108) ):

```solidity
4: interface ZetaInterfaces {

49: interface ZetaConnector {

56: interface ZetaReceiver {

77: interface ZetaTokenConsumer {

108: interface ZetaCommonErrors {
```

- *ZetaNonEthInterface.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9) ):

```solidity
9: interface ZetaNonEthInterface is IERC20 {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerTridentErrors {

20: interface WETH9 {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10) ):

```solidity
10: interface ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16) ):

```solidity
16: interface ConcentratedLiquidityPoolFactory {
```

- *SystemContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10) ):

```solidity
10: interface SystemContractErrors {
```

- *ZRC20.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8) ):

```solidity
8: interface ZRC20Errors {
```

- *ZetaConnectorZEVM.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49) ):

```solidity
4: interface ZetaInterfaces {

49: interface WZETA {
```

- *zContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10) ):

```solidity
10: interface zContract {
```

</details>

### [N-29] Invalid NatSpec comment style

NatSpec comment in solidity should use `///` or `/* ... */` syntax.

<details>
<summary>There are 20 instances (click to show):</summary>

- *ConnectorErrors.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L8), [10-11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L10-L11), [13-14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L13-L14), [16-17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L16-L17), [19-20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L19-L20), [22-23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L22-L23) ):

```solidity
8:     // @dev Thrown when caller is not the address defined as paused address

10: 
11:     // @dev Thrown when caller is not the address defined as TSS address

13: 
14:     // @dev Thrown when caller is not the address defined as TSS Updater address

16: 
17:     // @dev Thrown when caller is not the address defined as TSS or TSS Updater address

19: 
20:     // @dev Thrown when Zeta can't be transferred for some reason

22: 
23:     // @dev Thrown when maxSupply will be exceed if minting will proceed
```

- *ZetaErrors.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L8), [10-11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L10-L11), [13-14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L13-L14), [16-17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L16-L17), [19-20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L19-L20), [22-23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L22-L23) ):

```solidity
8:     // @dev Thrown when caller is not the address defined as TSS address

10: 
11:     // @dev Thrown when caller is not the address defined as connector address

13: 
14:     // @dev Thrown when caller is not the address defined as TSS Updater address

16: 
17:     // @dev Thrown when caller is not the address defined as TSS or TSS Updater address

19: 
20:     // @dev Thrown when a contract receives an invalid address param, mostly zero address validation

22: 
23:     // @dev Thrown when Zeta can't be transferred for some reason
```

- *ZetaInteractorErrors.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L8), [10-11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L10-L11), [13-14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L13-L14), [16-17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L16-L17) ):

```solidity
8:     // @dev Thrown when try to send a message or tokens to a non whitelisted chain

10: 
11:     // @dev Thrown when the caller is invalid. e.g.: if onZetaMessage or onZetaRevert are not called by Connector

13: 
14:     // @dev Thrown when message on onZetaMessage has the wrong format

16: 
17:     // @dev Thrown when message on onZetaRevert has the wrong format
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [215-216](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L215-L216) ):

```solidity
215: 
216:         //@dev: if pool does exist, get its liquidity
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [190-191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L190-L191) ):

```solidity
190: 
191:         //@dev: if pool does exist, get its liquidity
```

- *SystemContract.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L27) ):

```solidity
27:     // @dev: Map to know uniswap V2 pool of ZETA/ZRC20 given a chain id. This refer to the build in uniswap deployed at genesis.
```

- *ZRC20.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L9) ):

```solidity
9:     // @dev: Error thrown when caller is not the fungible module
```

</details>

### [N-30] @openzeppelin/contracts should be upgraded to a newer version

These contracts import contracts from `@openzeppelin/contracts`, but they are not using [the latest version](https://github.com/OpenZeppelin/openzeppelin-contracts/releases).

The imported version is `^4.8.3`.

<details>
<summary>There are 24 instances (click to show):</summary>

- *ERC20Custody.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L5), [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L5) ):

```solidity
5: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

5: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

- *Zeta.eth.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

4: import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
```

- *Zeta.non-eth.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

4: import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
```

- *ZetaConnector.base.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

- *ZetaConnector.eth.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

- *ZetaConnector.non-eth.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

- *ZetaNonEthInterface.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

- *ZetaInteractor.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/access/Ownable2Step.sol";

4: import "@openzeppelin/contracts/access/Ownable2Step.sol";
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

4: import "@openzeppelin/contracts/interfaces/IERC20.sol";
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

4: import "@openzeppelin/contracts/interfaces/IERC20.sol";
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

4: import "@openzeppelin/contracts/interfaces/IERC20.sol";
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L4), [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L4) ):

```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

4: import "@openzeppelin/contracts/interfaces/IERC20.sol";
```

</details>

### [N-31] Lines are too long

The [solidity style guide](https://docs.soliditylang.org/en/v0.8.17/style-guide.html#maximum-line-length) recommends a maximum line length of 120 characters. Lines of code that are longer than 120 should be wrapped.

<details>
<summary>There are 14 instances (click to show):</summary>

- *ERC20Custody.sol* ( [183](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L183) ):

```solidity
183:         // and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount.
```

- *ZetaConnector.eth.sol* ( [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L13) ):

```solidity
13:  * This version is only for Ethereum network because in the other chains we mint and burn and in this one we lock and unlock.
```

- *ZetaConnector.non-eth.sol* ( [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L13) ):

```solidity
13:  * This version is for every chain but Etherum network because in the other chains we mint and burn and in Etherum we lock and unlock
```

- *ZetaInterfaces.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L9), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L43) ):

```solidity
9:         /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id

43:         /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
```

- *TridentIPoolRouter.sol* ( [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L18), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L27), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L36), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L45) ):

```solidity
18:         address tokenIn; /// @dev the input token address. If tokenIn is address(0), msg.value will be wrapped and used as input token

27:         address tokenIn; /// @dev the token address to swap-in. If tokenIn is address(0), msg.value will be wrapped and used as input token

36:         address tokenIn; /// @dev the input token address. If tokenIn is address(0), msg.value will be wrapped and used as input token

45:         address tokenIn; /// @dev the token address to swap-in. If tokenIn is address(0), msg.value will be wrapped and used as input token
```

- *SystemContract.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L27) ):

```solidity
27:     // @dev: Map to know uniswap V2 pool of ZETA/ZRC20 given a chain id. This refer to the build in uniswap deployed at genesis.
```

- *ZRC20.sol* ( [234](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L234), [250](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L250) ):

```solidity
234:      * @return returns the ZRC20 address for gas on the same chain of this ZRC20, and calculates the gas fee for withdraw()

250:      * @dev Withraws ZRC20 tokens to external chains, this function causes cctx module to send out outbound tx to the outbound chain
```

- *ZetaConnectorZEVM.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L9), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L43) ):

```solidity
9:         /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id

43:         /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
```

</details>

### [N-32] Magic numbers should be replaced with constants

Magic numbers are hard-coded values in code that can make it difficult for developers and maintainers to understand the code, and can also cause confusion or errors. To improve the readability and maintainability of code, it is recommended to replace magic numbers with constants that have good readability.

There are 3 instances:

- *ZetaConnector.non-eth.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16) ):

```solidity
/// @audit 256
16:     uint256 public maxSupply = 2 ** 256 - 1;
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L76), [142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L142) ):

```solidity
/// @audit 3
76:             path = new address[](3);

/// @audit 3
142:             path = new address[](3);
```

### [N-33] Expressions for constant values should use `immutable` rather than `constant`

While it doesn't save any gas because the compiler knows that developers often make this mistake, it's still best to use the right tool for the task at hand. There is a difference between `constant` variables and `immutable` variables, and they should each be used in their appropriate contexts. `constants` should be used for literal values written into the code, and `immutable` variables should be used for expressions, or values calculated in, or passed into the constructor.

There is 1 instance:

- *ZetaInteractor.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10) ):

```solidity
10:     bytes32 constant ZERO_BYTES = keccak256(new bytes(0));
```

### [N-34] Functions not used internally could be marked external

If desired, sub contracts can change the visibility from `external` to `public` by [overriding](https://docs.soliditylang.org/en/v0.8.20/contracts.html#function-overriding) the functions of their parents.

There are 10 instances:

- *Zeta.non-eth.sol* ( [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73) ):

```solidity
73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```

- *ZRC20.sol* ( [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L107), [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L116), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157) ):

```solidity
83:     function name() public view virtual override returns (string memory) {

91:     function symbol() public view virtual override returns (string memory) {

99:     function decimals() public view virtual override returns (uint8) {

107:     function totalSupply() public view virtual override returns (uint256) {

116:     function balanceOf(address account) public view virtual override returns (uint256) {

125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {

135:     function allowance(address owner, address spender) public view virtual override returns (uint256) {

145:     function approve(address spender, uint256 amount) public virtual override returns (bool) {

157:     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
```

### [N-35] Contracts containing only utility functions should be made into libraries

Consider using a `library` instead of a `contract` to provide utility functions.

There is 1 instance:

- *UniswapPeriphery.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6) ):

```solidity
6: contract UniswapImports {}
```

### [N-36] Use `@inheritdoc` for overridden functions

It is recommended to use `@inheritdoc` for overridden functions.

<details>
<summary>There are 33 instances (click to show):</summary>

- *Zeta.non-eth.sol* ( [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73) ):

```solidity
62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```

- *ZetaConnector.eth.sol* ( [27-31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L27-L31), [47-59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L47-L59), [72-85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L72-L85) ):

```solidity
27:     /**
28:      * @dev Entrypoint to send data through ZetaChain
29:      * This call locks the token on the contract and emits an event with all the data needed by the protocol.
30:      */
31:     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

47:     /**
48:      * @dev Handler to receive data from other chain.
49:      * This method can be called only by TSS.
50:      * Transfers the Zeta tokens to destination and calls onZetaMessage if it's needed.
51:      */
52:     function onReceive(
53:         bytes calldata zetaTxSenderAddress,
54:         uint256 sourceChainId,
55:         address destinationAddress,
56:         uint256 zetaValue,
57:         bytes calldata message,
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress {

72:     /**
73:      * @dev Handler to receive errors from other chain.
74:      * This method can be called only by TSS.
75:      * Transfers the Zeta tokens to destination and calls onZetaRevert if it's needed.
76:      */
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

- *ZetaConnector.non-eth.sol* ( [36-40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L36-L40), [55-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L55-L68), [81-95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L81-L95) ):

```solidity
36:     /**
37:      * @dev Entry point to send data to protocol
38:      * This call burn the token and emit an event with all the data needed by the protocol
39:      */
40:     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

55:     /**
56:      * @dev Handler to receive data from other chain.
57:      * This method can be called only by TSS.
58:      * Transfer the Zeta tokens to destination and calls onZetaMessage if it's needed.
59:      * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
60:      */
61:     function onReceive(
62:         bytes calldata zetaTxSenderAddress,
63:         uint256 sourceChainId,
64:         address destinationAddress,
65:         uint256 zetaValue,
66:         bytes calldata message,
67:         bytes32 internalSendHash
68:     ) external override onlyTssAddress {

81:     /**
82:      * @dev Handler to receive errors from other chain.
83:      * This method can be called only by TSS.
84:      * Transfer the Zeta tokens to destination and calls onZetaRevert if it's needed.
85:      * To perform the transfer mint new tokens, validating first the maxSupply allowed in the current chain.
86:      */
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

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [103-106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L106), [126-131](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L131), [151-155](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L155), [184-189](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L189), [209](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209) ):

```solidity
103:     function getZetaFromEth(
104:         address destinationAddress,
105:         uint256 minAmountOut
106:     ) external payable override returns (uint256) {

126:     function getZetaFromToken(
127:         address destinationAddress,
128:         uint256 minAmountOut,
129:         address inputToken,
130:         uint256 inputTokenAmount
131:     ) external override returns (uint256) {

151:     function getEthFromZeta(
152:         address destinationAddress,
153:         uint256 minAmountOut,
154:         uint256 zetaTokenAmount
155:     ) external override returns (uint256) {

184:     function getTokenFromZeta(
185:         address destinationAddress,
186:         uint256 minAmountOut,
187:         address outputToken,
188:         uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {

209:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [74-77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L77), [99-104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L104), [136-140](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L140), [166-171](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L171), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203) ):

```solidity
74:     function getZetaFromEth(
75:         address destinationAddress,
76:         uint256 minAmountOut
77:     ) external payable override returns (uint256) {

99:     function getZetaFromToken(
100:         address destinationAddress,
101:         uint256 minAmountOut,
102:         address inputToken,
103:         uint256 inputTokenAmount
104:     ) external override returns (uint256) {

136:     function getEthFromZeta(
137:         address destinationAddress,
138:         uint256 minAmountOut,
139:         uint256 zetaTokenAmount
140:     ) external override returns (uint256) {

166:     function getTokenFromZeta(
167:         address destinationAddress,
168:         uint256 minAmountOut,
169:         address outputToken,
170:         uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {

203:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [34-37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34-L37), [58-63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L63), [95-99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L99), [124-129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L129), [162](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162) ):

```solidity
34:     function getZetaFromEth(
35:         address destinationAddress,
36:         uint256 minAmountOut
37:     ) external payable override returns (uint256) {

58:     function getZetaFromToken(
59:         address destinationAddress,
60:         uint256 minAmountOut,
61:         address inputToken,
62:         uint256 inputTokenAmount
63:     ) external override returns (uint256) {

95:     function getEthFromZeta(
96:         address destinationAddress,
97:         uint256 minAmountOut,
98:         uint256 zetaTokenAmount
99:     ) external override returns (uint256) {

124:     function getTokenFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         address outputToken,
128:         uint256 zetaTokenAmount
129:     ) external override returns (uint256) {

162:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [74-77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L77), [98-103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L103), [124-128](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L128), [158-163](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L163), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184) ):

```solidity
74:     function getZetaFromEth(
75:         address destinationAddress,
76:         uint256 minAmountOut
77:     ) external payable override returns (uint256) {

98:     function getZetaFromToken(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address inputToken,
102:         uint256 inputTokenAmount
103:     ) external override returns (uint256) {

124:     function getEthFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         uint256 zetaTokenAmount
128:     ) external override returns (uint256) {

158:     function getTokenFromZeta(
159:         address destinationAddress,
160:         uint256 minAmountOut,
161:         address outputToken,
162:         uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {

184:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZRC20.sol* ( [79-83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L79-L83), [87-91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L87-L91), [95-99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L95-L99), [103-107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L103-L107), [232-236](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L232-L236) ):

```solidity
79:     /**
80:      * @dev ZRC20 name
81:      * @return name as string
82:      */
83:     function name() public view virtual override returns (string memory) {

87:     /**
88:      * @dev ZRC20 symbol.
89:      * @return symbol as string.
90:      */
91:     function symbol() public view virtual override returns (string memory) {

95:     /**
96:      * @dev ZRC20 decimals.
97:      * @return returns uint8 decimals.
98:      */
99:     function decimals() public view virtual override returns (uint8) {

103:     /**
104:      * @dev ZRC20 total supply.
105:      * @return returns uint256 total supply.
106:      */
107:     function totalSupply() public view virtual override returns (uint256) {

232:     /**
233:      * @dev Withdraws gas fees.
234:      * @return returns the ZRC20 address for gas on the same chain of this ZRC20, and calculates the gas fee for withdraw()
235:      */
236:     function withdrawGasFee() public view override returns (address, uint256) {
```

</details>

### [N-37] Contracts should have NatSpec `@author` tags

Contracts should have NatSpec `@author` tags

<details>
<summary>There are 46 instances (click to show):</summary>

- *ERC20Custody.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11) ):

```solidity
11: contract ERC20Custody is ReentrancyGuard {
```

- *Zeta.eth.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9) ):

```solidity
9: contract ZetaEth is ERC20("Zeta", "ZETA") {
```

- *Zeta.non-eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10) ):

```solidity
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```

- *ZetaConnector.base.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15) ):

```solidity
15: contract ZetaConnectorBase is ConnectorErrors, Pausable {
```

- *ZetaConnector.eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15) ):

```solidity
15: contract ZetaConnectorEth is ZetaConnectorBase {
```

- *ZetaConnector.non-eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15) ):

```solidity
15: contract ZetaConnectorNonEth is ZetaConnectorBase {
```

- *ConnectorErrors.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7) ):

```solidity
7: interface ConnectorErrors {
```

- *ZetaErrors.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7) ):

```solidity
7: interface ZetaErrors {
```

- *ZetaInteractorErrors.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7) ):

```solidity
7: interface ZetaInteractorErrors {
```

- *ZetaInterfaces.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108) ):

```solidity
4: interface ZetaInterfaces {

49: interface ZetaConnector {

56: interface ZetaReceiver {

77: interface ZetaTokenConsumer {

108: interface ZetaCommonErrors {
```

- *ZetaNonEthInterface.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9) ):

```solidity
9: interface ZetaNonEthInterface is IERC20 {
```

- *ZetaInteractor.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9) ):

```solidity
9: abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {

24: interface ISwapRouterPancake is IUniswapV3SwapCallback {

56: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33) ):

```solidity
12: interface ZetaTokenConsumerTridentErrors {

20: interface WETH9 {

33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17) ):

```solidity
10: interface ZetaTokenConsumerUniV2Errors {

17: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {

27: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16) ):

```solidity
16: interface ConcentratedLiquidityPoolFactory {
```

- *TridentIPoolRouter.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16) ):

```solidity
16: interface IPoolRouter {
```

- *Interfaces.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L7), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49) ):

```solidity
7: interface ISystem {

21: interface IZRC20 {

49: interface IZRC20Metadata is IZRC20 {
```

- *SystemContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22) ):

```solidity
10: interface SystemContractErrors {

22: contract SystemContract is SystemContractErrors {
```

- *UniswapPeriphery.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6) ):

```solidity
6: contract UniswapImports {}
```

- *ZRC20.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20) ):

```solidity
8: interface ZRC20Errors {

20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

- *ZetaConnectorZEVM.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55) ):

```solidity
4: interface ZetaInterfaces {

49: interface WZETA {

55: contract ZetaConnectorZEVM is ZetaInterfaces {
```

- *IUniswapV2Router01.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4) ):

```solidity
4: interface IUniswapV2Router01 {
```

- *IUniswapV2Router02.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6) ):

```solidity
6: interface IUniswapV2Router02 is IUniswapV2Router01 {
```

- *IWZETA.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4) ):

```solidity
4: interface IWETH9 {
```

- *IZRC20.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4) ):

```solidity
4: interface IZRC20 {
```

- *zContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10) ):

```solidity
10: interface zContract {
```

</details>

### [N-38] Contracts should have `@notice` tags

The `@notice` is used to explain to users what the contract does. The compiler interprets `///` or `/**` comments [as this tag](https://docs.soliditylang.org/en/latest/natspec-format.html#tags) if one wasn't explicitly provided.

<details>
<summary>There are 28 instances (click to show):</summary>

- *Zeta.non-eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10) ):

```solidity
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```

- *ZetaInterfaces.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108) ):

```solidity
4: interface ZetaInterfaces {

49: interface ZetaConnector {

56: interface ZetaReceiver {

108: interface ZetaCommonErrors {
```

- *ZetaInteractor.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9) ):

```solidity
9: abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {

24: interface ISwapRouterPancake is IUniswapV3SwapCallback {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerTridentErrors {

20: interface WETH9 {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10) ):

```solidity
10: interface ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16) ):

```solidity
16: interface ConcentratedLiquidityPoolFactory {
```

- *TridentIPoolRouter.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16) ):

```solidity
16: interface IPoolRouter {
```

- *Interfaces.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49) ):

```solidity
21: interface IZRC20 {

49: interface IZRC20Metadata is IZRC20 {
```

- *UniswapPeriphery.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6) ):

```solidity
6: contract UniswapImports {}
```

- *ZRC20.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20) ):

```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

- *ZetaConnectorZEVM.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55) ):

```solidity
4: interface ZetaInterfaces {

49: interface WZETA {

55: contract ZetaConnectorZEVM is ZetaInterfaces {
```

- *IUniswapV2Router01.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4) ):

```solidity
4: interface IUniswapV2Router01 {
```

- *IUniswapV2Router02.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6) ):

```solidity
6: interface IUniswapV2Router02 is IUniswapV2Router01 {
```

- *IWZETA.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4) ):

```solidity
4: interface IWETH9 {
```

- *IZRC20.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4) ):

```solidity
4: interface IZRC20 {
```

- *zContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10) ):

```solidity
10: interface zContract {
```

</details>

### [N-39] Contracts should have NatSpec `@title` tags

Some contract definitions have an incomplete NatSpec: add a `@title` notation to describe the contract to improve the code documentation.

<details>
<summary>There are 45 instances (click to show):</summary>

- *Zeta.eth.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9) ):

```solidity
9: contract ZetaEth is ERC20("Zeta", "ZETA") {
```

- *Zeta.non-eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10) ):

```solidity
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```

- *ZetaConnector.base.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15) ):

```solidity
15: contract ZetaConnectorBase is ConnectorErrors, Pausable {
```

- *ZetaConnector.eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15) ):

```solidity
15: contract ZetaConnectorEth is ZetaConnectorBase {
```

- *ZetaConnector.non-eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15) ):

```solidity
15: contract ZetaConnectorNonEth is ZetaConnectorBase {
```

- *ConnectorErrors.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7) ):

```solidity
7: interface ConnectorErrors {
```

- *ZetaErrors.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7) ):

```solidity
7: interface ZetaErrors {
```

- *ZetaInteractorErrors.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7) ):

```solidity
7: interface ZetaInteractorErrors {
```

- *ZetaInterfaces.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108) ):

```solidity
4: interface ZetaInterfaces {

49: interface ZetaConnector {

56: interface ZetaReceiver {

77: interface ZetaTokenConsumer {

108: interface ZetaCommonErrors {
```

- *ZetaNonEthInterface.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9) ):

```solidity
9: interface ZetaNonEthInterface is IERC20 {
```

- *ZetaInteractor.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9) ):

```solidity
9: abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {

24: interface ISwapRouterPancake is IUniswapV3SwapCallback {

56: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33) ):

```solidity
12: interface ZetaTokenConsumerTridentErrors {

20: interface WETH9 {

33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17) ):

```solidity
10: interface ZetaTokenConsumerUniV2Errors {

17: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {

27: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16) ):

```solidity
16: interface ConcentratedLiquidityPoolFactory {
```

- *TridentIPoolRouter.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16) ):

```solidity
16: interface IPoolRouter {
```

- *Interfaces.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L7), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49) ):

```solidity
7: interface ISystem {

21: interface IZRC20 {

49: interface IZRC20Metadata is IZRC20 {
```

- *SystemContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22) ):

```solidity
10: interface SystemContractErrors {

22: contract SystemContract is SystemContractErrors {
```

- *UniswapPeriphery.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6) ):

```solidity
6: contract UniswapImports {}
```

- *ZRC20.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20) ):

```solidity
8: interface ZRC20Errors {

20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

- *ZetaConnectorZEVM.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55) ):

```solidity
4: interface ZetaInterfaces {

49: interface WZETA {

55: contract ZetaConnectorZEVM is ZetaInterfaces {
```

- *IUniswapV2Router01.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4) ):

```solidity
4: interface IUniswapV2Router01 {
```

- *IUniswapV2Router02.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6) ):

```solidity
6: interface IUniswapV2Router02 is IUniswapV2Router01 {
```

- *IWZETA.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4) ):

```solidity
4: interface IWETH9 {
```

- *IZRC20.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4) ):

```solidity
4: interface IZRC20 {
```

- *zContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10) ):

```solidity
10: interface zContract {
```

</details>

### [N-40] Events missing NatSpec `@param` tag

Each modifier parameter should have a `@param` notation to improve the code documentation.

<details>
<summary>There are 117 instances (click to show):</summary>

- *ERC20Custody.sol* ( [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46) ):

```solidity
/// @audit Missing @param for `sender`
38:     event Paused(address sender);

/// @audit Missing @param for `sender`
39:     event Unpaused(address sender);

/// @audit Missing @param for `asset`
40:     event Whitelisted(IERC20 indexed asset);

/// @audit Missing @param for `asset`
41:     event Unwhitelisted(IERC20 indexed asset);

/// @audit Missing @param for `recipient`, `asset`, `amount`, `message`
42:     event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);

/// @audit Missing @param for `recipient`, `asset`, `amount`
43:     event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);

/// @audit Missing @param for `TSSAddressUpdater_`
44:     event RenouncedTSSUpdater(address TSSAddressUpdater_);

/// @audit Missing @param for `TSSAddress_`
45:     event UpdatedTSSAddress(address TSSAddress_);

/// @audit Missing @param for `zetaFee_`
46:     event UpdatedZetaFee(uint256 zetaFee_);
```

- *Zeta.non-eth.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31) ):

```solidity
/// @audit Missing @param for `mintee`, `amount`, `internalSendHash`
23:     event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);

/// @audit Missing @param for `burnee`, `amount`
25:     event Burnt(address indexed burnee, uint256 amount);

/// @audit Missing @param for `callerAddress`, `newTssAddress`
27:     event TSSAddressUpdated(address callerAddress, address newTssAddress);

/// @audit Missing @param for `callerAddress`, `newTssUpdaterAddress`
29:     event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

/// @audit Missing @param for `callerAddress`, `newConnectorAddress`
31:     event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);
```

- *ZetaConnector.base.sol* ( [34-43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34-L43), [45-52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L45-L52), [54-62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L62), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68) ):

```solidity
/// @audit Missing @param for `sourceTxOriginAddress`, `zetaTxSenderAddress`, `destinationChainId`, `destinationAddress`, `zetaValueAndGas`, `destinationGasLimit`, `message`, `zetaParams`
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

/// @audit Missing @param for `zetaTxSenderAddress`, `sourceChainId`, `destinationAddress`, `zetaValue`, `message`, `internalSendHash`
45:     event ZetaReceived(
46:         bytes zetaTxSenderAddress,
47:         uint256 indexed sourceChainId,
48:         address indexed destinationAddress,
49:         uint256 zetaValue,
50:         bytes message,
51:         bytes32 indexed internalSendHash
52:     );

/// @audit Missing @param for `zetaTxSenderAddress`, `sourceChainId`, `destinationChainId`, `destinationAddress`, `remainingZetaValue`, `message`, `internalSendHash`
54:     event ZetaReverted(
55:         address zetaTxSenderAddress,
56:         uint256 sourceChainId,
57:         uint256 indexed destinationChainId,
58:         bytes destinationAddress,
59:         uint256 remainingZetaValue,
60:         bytes message,
61:         bytes32 indexed internalSendHash
62:     );

/// @audit Missing @param for `callerAddress`, `newTssAddress`
64:     event TSSAddressUpdated(address callerAddress, address newTssAddress);

/// @audit Missing @param for `callerAddress`, `newTssUpdaterAddress`
66:     event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

/// @audit Missing @param for `callerAddress`, `newTssAddress`
68:     event PauserAddressUpdated(address callerAddress, address newTssAddress);
```

- *ZetaConnector.non-eth.sol* ( [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18) ):

```solidity
/// @audit Missing @param for `callerAddress`, `newMaxSupply`
18:     event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
```

- *ZetaInterfaces.sol* ( [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L80), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81) ):

```solidity
/// @audit Missing @param for `amountIn`, `amountOut`
78:     event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);

/// @audit Missing @param for `token`, `amountIn`, `amountOut`
79:     event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

/// @audit Missing @param for `amountIn`, `amountOut`
80:     event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);

/// @audit Missing @param for `token`, `amountIn`, `amountOut`
81:     event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
```

- *Interfaces.sol* ( [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L46) ):

```solidity
/// @audit Missing @param for `from`, `to`, `value`
40:     event Transfer(address indexed from, address indexed to, uint256 value);

/// @audit Missing @param for `owner`, `spender`, `value`
41:     event Approval(address indexed owner, address indexed spender, uint256 value);

/// @audit Missing @param for `from`, `to`, `value`
42:     event Deposit(bytes from, address indexed to, uint256 value);

/// @audit Missing @param for `from`, `to`, `value`, `gasfee`, `protocolFlatFee`
43:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);

/// @audit Missing @param for `systemContract`
44:     event UpdatedSystemContract(address systemContract);

/// @audit Missing @param for `gasLimit`
45:     event UpdatedGasLimit(uint256 gasLimit);

/// @audit Missing @param for `protocolFlatFee`
46:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```

- *ZetaConnectorZEVM.sol* ( [67-76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77) ):

```solidity
/// @audit Missing @param for `sourceTxOriginAddress`, `zetaTxSenderAddress`, `destinationChainId`, `destinationAddress`, `zetaValueAndGas`, `destinationGasLimit`, `message`, `zetaParams`
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

/// @audit Missing @param for `wzeta_`
77:     event SetWZETA(address wzeta_);
```

- *IWZETA.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8) ):

```solidity
/// @audit Missing @param for `owner`, `spender`, `value`
5:     event Approval(address indexed owner, address indexed spender, uint value);

/// @audit Missing @param for `from`, `to`, `value`
6:     event Transfer(address indexed from, address indexed to, uint value);

/// @audit Missing @param for `dst`, `wad`
7:     event Deposit(address indexed dst, uint wad);

/// @audit Missing @param for `src`, `wad`
8:     event Withdrawal(address indexed src, uint wad);
```

- *IZRC20.sol* ( [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37) ):

```solidity
/// @audit Missing @param for `from`, `to`, `value`
31:     event Transfer(address indexed from, address indexed to, uint256 value);

/// @audit Missing @param for `owner`, `spender`, `value`
32:     event Approval(address indexed owner, address indexed spender, uint256 value);

/// @audit Missing @param for `from`, `to`, `value`
33:     event Deposit(bytes from, address indexed to, uint256 value);

/// @audit Missing @param for `from`, `to`, `value`, `gasFee`, `protocolFlatFee`
34:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

/// @audit Missing @param for `systemContract`
35:     event UpdatedSystemContract(address systemContract);

/// @audit Missing @param for `gasLimit`
36:     event UpdatedGasLimit(uint256 gasLimit);

/// @audit Missing @param for `protocolFlatFee`
37:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```

</details>

### [N-41] Event declarations should have NatSpec descriptions

Event declarations should have NatSpec descriptions

<details>
<summary>There are 50 instances (click to show):</summary>

- *ERC20Custody.sol* ( [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46) ):

```solidity
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

- *Zeta.non-eth.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31) ):

```solidity
23:     event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);

25:     event Burnt(address indexed burnee, uint256 amount);

27:     event TSSAddressUpdated(address callerAddress, address newTssAddress);

29:     event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

31:     event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);
```

- *ZetaConnector.base.sol* ( [34-43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34-L43), [45-52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L45-L52), [54-62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L62), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68) ):

```solidity
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

45:     event ZetaReceived(
46:         bytes zetaTxSenderAddress,
47:         uint256 indexed sourceChainId,
48:         address indexed destinationAddress,
49:         uint256 zetaValue,
50:         bytes message,
51:         bytes32 indexed internalSendHash
52:     );

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

- *ZetaConnector.non-eth.sol* ( [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18) ):

```solidity
18:     event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
```

- *ZetaInterfaces.sol* ( [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L80), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81) ):

```solidity
78:     event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);

79:     event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

80:     event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);

81:     event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
```

- *Interfaces.sol* ( [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L46) ):

```solidity
40:     event Transfer(address indexed from, address indexed to, uint256 value);

41:     event Approval(address indexed owner, address indexed spender, uint256 value);

42:     event Deposit(bytes from, address indexed to, uint256 value);

43:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);

44:     event UpdatedSystemContract(address systemContract);

45:     event UpdatedGasLimit(uint256 gasLimit);

46:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```

- *SystemContract.sol* ( [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46) ):

```solidity
42:     event SetGasPrice(uint256, uint256);

43:     event SetGasCoin(uint256, address);

44:     event SetGasZetaPool(uint256, address);

45:     event SetWZeta(address);

46:     event SetConnectorZEVM(address);
```

- *ZetaConnectorZEVM.sol* ( [67-76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77) ):

```solidity
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

- *IWZETA.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8) ):

```solidity
5:     event Approval(address indexed owner, address indexed spender, uint value);

6:     event Transfer(address indexed from, address indexed to, uint value);

7:     event Deposit(address indexed dst, uint wad);

8:     event Withdrawal(address indexed src, uint wad);
```

- *IZRC20.sol* ( [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37) ):

```solidity
31:     event Transfer(address indexed from, address indexed to, uint256 value);

32:     event Approval(address indexed owner, address indexed spender, uint256 value);

33:     event Deposit(bytes from, address indexed to, uint256 value);

34:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

35:     event UpdatedSystemContract(address systemContract);

36:     event UpdatedGasLimit(uint256 gasLimit);

37:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```

</details>

### [N-42] Functions missing NatSpec `@param` tag

Each function parameter should have a `@param` notation to improve the code documentation.

<details>
<summary>There are 381 instances (click to show):</summary>

- *ERC20Custody.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68) ):

```solidity
/// @audit Missing @param for `TSSAddress_`, `TSSAddressUpdater_`, `zetaFee_`, `zetaMaxFee_`, `zeta_`
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
```

- *Zeta.eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10) ):

```solidity
/// @audit Missing @param for `creator`, `initialSupply`
10:     constructor(address creator, uint256 initialSupply) {
```

- *Zeta.non-eth.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73) ):

```solidity
/// @audit Missing @param for `tssAddress_`, `tssAddressUpdater_`
33:     constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

/// @audit Missing @param for `tssAddress_`, `connectorAddress_`
40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

/// @audit Missing @param for `mintee`, `value`, `internalSendHash`
62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

/// @audit Missing @param for `account`, `amount`
73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```

- *ZetaConnector.base.sol* ( [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74), [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117), [128](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L128), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166), [172-179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185-193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193) ):

```solidity
/// @audit Missing @param for `zetaToken_`, `tssAddress_`, `tssAddressUpdater_`, `pauserAddress_`
74:     constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {

/// @audit Missing @param for `pauserAddress_`
117:     function updatePauserAddress(address pauserAddress_) external onlyPauser {

/// @audit Missing @param for `tssAddress_`
128:     function updateTssAddress(address tssAddress_) external {

/// @audit Missing @param for `input`
166:     function send(ZetaInterfaces.SendInput calldata input) external virtual {}

/// @audit Missing @param for `zetaTxSenderAddress`, `sourceChainId`, `destinationAddress`, `zetaValue`, `message`, `internalSendHash`
172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

/// @audit Missing @param for `zetaTxSenderAddress`, `sourceChainId`, `destinationAddress`, `destinationChainId`, `remainingZetaValue`, `message`, `internalSendHash`
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

- *ZetaConnector.eth.sol* ( [16-21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31), [52-59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L59), [77-85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L85) ):

```solidity
/// @audit Missing @param for `zetaToken_`, `tssAddress_`, `tssAddressUpdater_`, `pauserAddress_`
16:     constructor(
17:         address zetaToken_,
18:         address tssAddress_,
19:         address tssAddressUpdater_,
20:         address pauserAddress_
21:     ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

/// @audit Missing @param for `input`
31:     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

/// @audit Missing @param for `zetaTxSenderAddress`, `sourceChainId`, `destinationAddress`, `zetaValue`, `message`, `internalSendHash`
52:     function onReceive(
53:         bytes calldata zetaTxSenderAddress,
54:         uint256 sourceChainId,
55:         address destinationAddress,
56:         uint256 zetaValue,
57:         bytes calldata message,
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress {

/// @audit Missing @param for `zetaTxSenderAddress`, `sourceChainId`, `destinationAddress`, `destinationChainId`, `remainingZetaValue`, `message`, `internalSendHash`
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

- *ZetaConnector.non-eth.sol* ( [20-25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40), [61-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L68), [87-95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L95) ):

```solidity
/// @audit Missing @param for `zetaTokenAddress_`, `tssAddress_`, `tssAddressUpdater_`, `pauserAddress_`
20:     constructor(
21:         address zetaTokenAddress_,
22:         address tssAddress_,
23:         address tssAddressUpdater_,
24:         address pauserAddress_
25:     ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}

/// @audit Missing @param for `maxSupply_`
31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {

/// @audit Missing @param for `input`
40:     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

/// @audit Missing @param for `zetaTxSenderAddress`, `sourceChainId`, `destinationAddress`, `zetaValue`, `message`, `internalSendHash`
61:     function onReceive(
62:         bytes calldata zetaTxSenderAddress,
63:         uint256 sourceChainId,
64:         address destinationAddress,
65:         uint256 zetaValue,
66:         bytes calldata message,
67:         bytes32 internalSendHash
68:     ) external override onlyTssAddress {

/// @audit Missing @param for `zetaTxSenderAddress`, `sourceChainId`, `destinationAddress`, `destinationChainId`, `remainingZetaValue`, `message`, `internalSendHash`
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

- *ZetaInterfaces.sol* ( [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L53), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L60), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L66), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83), [85-90](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85-L90), [92-96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92-L96), [98-103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98-L103) ):

```solidity
/// @audit Missing @param for `input`
53:     function send(ZetaInterfaces.SendInput calldata input) external;

/// @audit Missing @param for `zetaMessage`
60:     function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external;

/// @audit Missing @param for `zetaRevert`
66:     function onZetaRevert(ZetaInterfaces.ZetaRevert calldata zetaRevert) external;

/// @audit Missing @param for `destinationAddress`, `minAmountOut`
83:     function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `inputToken`, `inputTokenAmount`
85:     function getZetaFromToken(
86:         address destinationAddress,
87:         uint256 minAmountOut,
88:         address inputToken,
89:         uint256 inputTokenAmount
90:     ) external returns (uint256);

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `zetaTokenAmount`
92:     function getEthFromZeta(
93:         address destinationAddress,
94:         uint256 minAmountOut,
95:         uint256 zetaTokenAmount
96:     ) external returns (uint256);

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `outputToken`, `zetaTokenAmount`
98:     function getTokenFromZeta(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address outputToken,
102:         uint256 zetaTokenAmount
103:     ) external returns (uint256);
```

- *ZetaNonEthInterface.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12) ):

```solidity
/// @audit Missing @param for `account`, `amount`
10:     function burnFrom(address account, uint256 amount) external;

/// @audit Missing @param for `mintee`, `value`, `internalSendHash`
12:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external;
```

- *ZetaInteractor.sol* ( [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L37), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L50), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54) ):

```solidity
/// @audit Missing @param for `zetaConnectorAddress`
37:     constructor(address zetaConnectorAddress) {

/// @audit Missing @param for `chainId`
50:     function _isValidChainId(uint256 chainId) internal view returns (bool) {

/// @audit Missing @param for `destinationChainId`, `contractAddress`
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L21), [71-78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L78), [103-106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L106), [126-131](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L131), [151-155](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L155), [184-189](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L189) ):

```solidity
/// @audit Missing @param for `wad`
21:     function withdraw(uint256 wad) external;

/// @audit Missing @param for `zetaToken_`, `pancakeV3Router_`, `uniswapV3Factory_`, `WETH9Address_`, `zetaPoolFee_`, `tokenPoolFee_`
71:     constructor(
72:         address zetaToken_,
73:         address pancakeV3Router_,
74:         address uniswapV3Factory_,
75:         address WETH9Address_,
76:         uint24 zetaPoolFee_,
77:         uint24 tokenPoolFee_
78:     ) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`
103:     function getZetaFromEth(
104:         address destinationAddress,
105:         uint256 minAmountOut
106:     ) external payable override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `inputToken`, `inputTokenAmount`
126:     function getZetaFromToken(
127:         address destinationAddress,
128:         uint256 minAmountOut,
129:         address inputToken,
130:         uint256 inputTokenAmount
131:     ) external override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `zetaTokenAmount`
151:     function getEthFromZeta(
152:         address destinationAddress,
153:         uint256 minAmountOut,
154:         uint256 zetaTokenAmount
155:     ) external override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `outputToken`, `zetaTokenAmount`
184:     function getTokenFromZeta(
185:         address destinationAddress,
186:         uint256 minAmountOut,
187:         address outputToken,
188:         uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L27), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68), [74-77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L77), [99-104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L104), [136-140](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L140), [166-171](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L171) ):

```solidity
/// @audit Missing @param for `wad`
23:     function withdraw(uint256 wad) external;

/// @audit Missing @param for `to`
25:     function depositTo(address to) external payable;

/// @audit Missing @param for `to`, `value`
27:     function withdrawTo(address payable to, uint256 value) external;

/// @audit Missing @param for `zetaToken_`, `uniswapV3Router_`, `WETH9Address_`, `poolFactory_`
45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

/// @audit Missing @param for `token0`, `token1`
68:     function getPair(address token0, address token1) internal pure returns (address, address) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`
74:     function getZetaFromEth(
75:         address destinationAddress,
76:         uint256 minAmountOut
77:     ) external payable override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `inputToken`, `inputTokenAmount`
99:     function getZetaFromToken(
100:         address destinationAddress,
101:         uint256 minAmountOut,
102:         address inputToken,
103:         uint256 inputTokenAmount
104:     ) external override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `zetaTokenAmount`
136:     function getEthFromZeta(
137:         address destinationAddress,
138:         uint256 minAmountOut,
139:         uint256 zetaTokenAmount
140:     ) external override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `outputToken`, `zetaTokenAmount`
166:     function getTokenFromZeta(
167:         address destinationAddress,
168:         uint256 minAmountOut,
169:         address outputToken,
170:         uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26), [34-37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34-L37), [58-63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L63), [95-99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L99), [124-129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L129) ):

```solidity
/// @audit Missing @param for `zetaToken_`, `uniswapV2Router_`
26:     constructor(address zetaToken_, address uniswapV2Router_) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`
34:     function getZetaFromEth(
35:         address destinationAddress,
36:         uint256 minAmountOut
37:     ) external payable override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `inputToken`, `inputTokenAmount`
58:     function getZetaFromToken(
59:         address destinationAddress,
60:         uint256 minAmountOut,
61:         address inputToken,
62:         uint256 inputTokenAmount
63:     ) external override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `zetaTokenAmount`
95:     function getEthFromZeta(
96:         address destinationAddress,
97:         uint256 minAmountOut,
98:         uint256 zetaTokenAmount
99:     ) external override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `outputToken`, `zetaTokenAmount`
124:     function getTokenFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         address outputToken,
128:         uint256 zetaTokenAmount
129:     ) external override returns (uint256) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L21), [42-49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L49), [74-77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L77), [98-103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L103), [124-128](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L128), [158-163](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L163) ):

```solidity
/// @audit Missing @param for `wad`
21:     function withdraw(uint256 wad) external;

/// @audit Missing @param for `zetaToken_`, `uniswapV3Router_`, `uniswapV3Factory_`, `WETH9Address_`, `zetaPoolFee_`, `tokenPoolFee_`
42:     constructor(
43:         address zetaToken_,
44:         address uniswapV3Router_,
45:         address uniswapV3Factory_,
46:         address WETH9Address_,
47:         uint24 zetaPoolFee_,
48:         uint24 tokenPoolFee_
49:     ) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`
74:     function getZetaFromEth(
75:         address destinationAddress,
76:         uint256 minAmountOut
77:     ) external payable override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `inputToken`, `inputTokenAmount`
98:     function getZetaFromToken(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address inputToken,
102:         uint256 inputTokenAmount
103:     ) external override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `zetaTokenAmount`
124:     function getEthFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         uint256 zetaTokenAmount
128:     ) external override returns (uint256) {

/// @audit Missing @param for `destinationAddress`, `minAmountOut`, `outputToken`, `zetaTokenAmount`
158:     function getTokenFromZeta(
159:         address destinationAddress,
160:         uint256 minAmountOut,
161:         address outputToken,
162:         uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [17-22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17-L22) ):

```solidity
/// @audit Missing @param for `token0`, `token1`, `startIndex`, `count`
17:     function getPools(
18:         address token0,
19:         address token1,
20:         uint256 startIndex,
21:         uint256 count
22:     ) external view returns (address[] memory pairPools);
```

- *TridentIPoolRouter.sol* ( [70](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L70) ):

```solidity
/// @audit Missing @param for `token`, `amount`, `recipient`
70:     function sweep(address token, uint256 amount, address recipient) external payable;
```

- *Interfaces.sol* ( [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36) ):

```solidity
/// @audit Missing @param for `chainID`
14:     function gasPriceByChainId(uint256 chainID) external view returns (uint256);

/// @audit Missing @param for `chainID`
16:     function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

/// @audit Missing @param for `chainID`
18:     function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

/// @audit Missing @param for `account`
24:     function balanceOf(address account) external view returns (uint256);

/// @audit Missing @param for `recipient`, `amount`
26:     function transfer(address recipient, uint256 amount) external returns (bool);

/// @audit Missing @param for `owner`, `spender`
28:     function allowance(address owner, address spender) external view returns (uint256);

/// @audit Missing @param for `spender`, `amount`
30:     function approve(address spender, uint256 amount) external returns (bool);

/// @audit Missing @param for `sender`, `recipient`, `amount`
32:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

/// @audit Missing @param for `to`, `amount`
34:     function deposit(address to, uint256 amount) external returns (bool);

/// @audit Missing @param for `to`, `amount`
36:     function withdraw(bytes memory to, uint256 amount) external returns (bool);
```

- *SystemContract.sol* ( [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51) ):

```solidity
/// @audit Missing @param for `wzeta_`, `uniswapv2Factory_`, `uniswapv2Router02_`
51:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
```

- *ZRC20.sol* ( [60-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L68), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135), [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L178), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L191), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L199), [211](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L211) ):

```solidity
/// @audit Missing @param for `name_`, `symbol_`, `decimals_`, `chainid_`, `coinType_`, `gasLimit_`, `systemContractAddress_`
60:     constructor(
61:         string memory name_,
62:         string memory symbol_,
63:         uint8 decimals_,
64:         uint256 chainid_,
65:         CoinType coinType_,
66:         uint256 gasLimit_,
67:         address systemContractAddress_
68:     ) {

/// @audit Missing @param for `amount`
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {

/// @audit Missing @param for `spender`
135:     function allowance(address owner, address spender) public view virtual override returns (uint256) {

/// @audit Missing @param for `sender`, `recipient`, `amount`
178:     function _transfer(address sender, address recipient, uint256 amount) internal virtual {

/// @audit Missing @param for `account`, `amount`
191:     function _mint(address account, uint256 amount) internal virtual {

/// @audit Missing @param for `account`, `amount`
199:     function _burn(address account, uint256 amount) internal virtual {

/// @audit Missing @param for `owner`, `spender`, `amount`
211:     function _approve(address owner, address spender, uint256 amount) internal virtual {
```

- *ZetaConnectorZEVM.sol* ( [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79) ):

```solidity
/// @audit Missing @param for `src`, `dst`, `wad`
50:     function transferFrom(address src, address dst, uint wad) external returns (bool);

/// @audit Missing @param for `wad`
52:     function withdraw(uint wad) external;

/// @audit Missing @param for `wzeta_`
79:     constructor(address wzeta_) {
```

- *IUniswapV2Router01.sol* ( [9-18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18), [20-27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27), [29-37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L37), [39-46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L46), [48-60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60), [62-73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73), [75-81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L81), [83-89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L89), [91-96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91-L96), [98-104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L104), [106-112](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L112), [114-119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114-L119), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129) ):

```solidity
/// @audit Missing @param for `tokenA`, `tokenB`, `amountADesired`, `amountBDesired`, `amountAMin`, `amountBMin`, `to`, `deadline`
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

/// @audit Missing @param for `token`, `amountTokenDesired`, `amountTokenMin`, `amountETHMin`, `to`, `deadline`
20:     function addLiquidityETH(
21:         address token,
22:         uint amountTokenDesired,
23:         uint amountTokenMin,
24:         uint amountETHMin,
25:         address to,
26:         uint deadline
27:     ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

/// @audit Missing @param for `tokenA`, `tokenB`, `liquidity`, `amountAMin`, `amountBMin`, `to`, `deadline`
29:     function removeLiquidity(
30:         address tokenA,
31:         address tokenB,
32:         uint liquidity,
33:         uint amountAMin,
34:         uint amountBMin,
35:         address to,
36:         uint deadline
37:     ) external returns (uint amountA, uint amountB);

/// @audit Missing @param for `token`, `liquidity`, `amountTokenMin`, `amountETHMin`, `to`, `deadline`
39:     function removeLiquidityETH(
40:         address token,
41:         uint liquidity,
42:         uint amountTokenMin,
43:         uint amountETHMin,
44:         address to,
45:         uint deadline
46:     ) external returns (uint amountToken, uint amountETH);

/// @audit Missing @param for `tokenA`, `tokenB`, `liquidity`, `amountAMin`, `amountBMin`, `to`, `deadline`, `approveMax`, `v`, `r`, `s`
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

/// @audit Missing @param for `token`, `liquidity`, `amountTokenMin`, `amountETHMin`, `to`, `deadline`, `approveMax`, `v`, `r`, `s`
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

/// @audit Missing @param for `amountIn`, `amountOutMin`, `path`, `to`, `deadline`
75:     function swapExactTokensForTokens(
76:         uint amountIn,
77:         uint amountOutMin,
78:         address[] calldata path,
79:         address to,
80:         uint deadline
81:     ) external returns (uint[] memory amounts);

/// @audit Missing @param for `amountOut`, `amountInMax`, `path`, `to`, `deadline`
83:     function swapTokensForExactTokens(
84:         uint amountOut,
85:         uint amountInMax,
86:         address[] calldata path,
87:         address to,
88:         uint deadline
89:     ) external returns (uint[] memory amounts);

/// @audit Missing @param for `amountOutMin`, `path`, `to`, `deadline`
91:     function swapExactETHForTokens(
92:         uint amountOutMin,
93:         address[] calldata path,
94:         address to,
95:         uint deadline
96:     ) external payable returns (uint[] memory amounts);

/// @audit Missing @param for `amountOut`, `amountInMax`, `path`, `to`, `deadline`
98:     function swapTokensForExactETH(
99:         uint amountOut,
100:         uint amountInMax,
101:         address[] calldata path,
102:         address to,
103:         uint deadline
104:     ) external returns (uint[] memory amounts);

/// @audit Missing @param for `amountIn`, `amountOutMin`, `path`, `to`, `deadline`
106:     function swapExactTokensForETH(
107:         uint amountIn,
108:         uint amountOutMin,
109:         address[] calldata path,
110:         address to,
111:         uint deadline
112:     ) external returns (uint[] memory amounts);

/// @audit Missing @param for `amountOut`, `path`, `to`, `deadline`
114:     function swapETHForExactTokens(
115:         uint amountOut,
116:         address[] calldata path,
117:         address to,
118:         uint deadline
119:     ) external payable returns (uint[] memory amounts);

/// @audit Missing @param for `amountA`, `reserveA`, `reserveB`
121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

/// @audit Missing @param for `amountIn`, `reserveIn`, `reserveOut`
123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

/// @audit Missing @param for `amountOut`, `reserveIn`, `reserveOut`
125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

/// @audit Missing @param for `amountIn`, `path`
127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

/// @audit Missing @param for `amountOut`, `path`
129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);
```

- *IUniswapV2Router02.sol* ( [7-14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7-L14), [16-27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L27), [29-35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29-L35), [37-42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37-L42), [44-50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44-L50) ):

```solidity
/// @audit Missing @param for `token`, `liquidity`, `amountTokenMin`, `amountETHMin`, `to`, `deadline`
7:     function removeLiquidityETHSupportingFeeOnTransferTokens(
8:         address token,
9:         uint liquidity,
10:         uint amountTokenMin,
11:         uint amountETHMin,
12:         address to,
13:         uint deadline
14:     ) external returns (uint amountETH);

/// @audit Missing @param for `token`, `liquidity`, `amountTokenMin`, `amountETHMin`, `to`, `deadline`, `approveMax`, `v`, `r`, `s`
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

/// @audit Missing @param for `amountIn`, `amountOutMin`, `path`, `to`, `deadline`
29:     function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30:         uint amountIn,
31:         uint amountOutMin,
32:         address[] calldata path,
33:         address to,
34:         uint deadline
35:     ) external;

/// @audit Missing @param for `amountOutMin`, `path`, `to`, `deadline`
37:     function swapExactETHForTokensSupportingFeeOnTransferTokens(
38:         uint amountOutMin,
39:         address[] calldata path,
40:         address to,
41:         uint deadline
42:     ) external payable;

/// @audit Missing @param for `amountIn`, `amountOutMin`, `path`, `to`, `deadline`
44:     function swapExactTokensForETHSupportingFeeOnTransferTokens(
45:         uint amountIn,
46:         uint amountOutMin,
47:         address[] calldata path,
48:         address to,
49:         uint deadline
50:     ) external;
```

- *IWZETA.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24) ):

```solidity
/// @audit Missing @param for `owner`
12:     function balanceOf(address owner) external view returns (uint);

/// @audit Missing @param for `owner`, `spender`
14:     function allowance(address owner, address spender) external view returns (uint);

/// @audit Missing @param for `spender`, `wad`
16:     function approve(address spender, uint wad) external returns (bool);

/// @audit Missing @param for `to`, `wad`
18:     function transfer(address to, uint wad) external returns (bool);

/// @audit Missing @param for `from`, `to`, `wad`
20:     function transferFrom(address from, address to, uint wad) external returns (bool);

/// @audit Missing @param for `wad`
24:     function withdraw(uint wad) external;
```

- *IZRC20.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25) ):

```solidity
/// @audit Missing @param for `account`
7:     function balanceOf(address account) external view returns (uint256);

/// @audit Missing @param for `recipient`, `amount`
9:     function transfer(address recipient, uint256 amount) external returns (bool);

/// @audit Missing @param for `owner`, `spender`
11:     function allowance(address owner, address spender) external view returns (uint256);

/// @audit Missing @param for `spender`, `amount`
13:     function approve(address spender, uint256 amount) external returns (bool);

/// @audit Missing @param for `spender`, `amount`
15:     function decreaseAllowance(address spender, uint256 amount) external returns (bool);

/// @audit Missing @param for `spender`, `amount`
17:     function increaseAllowance(address spender, uint256 amount) external returns (bool);

/// @audit Missing @param for `sender`, `recipient`, `amount`
19:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

/// @audit Missing @param for `to`, `amount`
21:     function deposit(address to, uint256 amount) external returns (bool);

/// @audit Missing @param for `account`, `amount`
23:     function burn(address account, uint256 amount) external returns (bool);

/// @audit Missing @param for `to`, `amount`
25:     function withdraw(bytes memory to, uint256 amount) external returns (bool);
```

- *zContract.sol* ( [11-16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11-L16) ):

```solidity
/// @audit Missing @param for `context`, `zrc20`, `amount`, `message`
11:     function onCrossChainCall(
12:         zContext calldata context,
13:         address zrc20,
14:         uint256 amount,
15:         bytes calldata message
16:     ) external;
```

</details>

### [N-43] NatSpec documentation for function is missing

It is recommended that Solidity contracts are fully annotated using NatSpec for all public interfaces (everything in the ABI). It is clearly stated in the Solidity official documentation.
In complex projects such as DeFi, the interpretation of all functions and their arguments and returns is important for code readability and auditability.

<details>
<summary>There are 129 instances (click to show):</summary>

- *ERC20Custody.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68) ):

```solidity
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
```

- *Zeta.eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10) ):

```solidity
10:     constructor(address creator, uint256 initialSupply) {
```

- *Zeta.non-eth.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73) ):

```solidity
33:     constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```

- *ZetaConnector.eth.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23) ):

```solidity
16:     constructor(

23:     function getLockedAmount() external view returns (uint256) {
```

- *ZetaConnector.non-eth.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31) ):

```solidity
20:     constructor(

27:     function getLockedAmount() external view returns (uint256) {

31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
```

- *ZetaInterfaces.sol* ( [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L105) ):

```solidity
83:     function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

85:     function getZetaFromToken(

92:     function getEthFromZeta(

98:     function getTokenFromZeta(

105:     function hasZetaLiquidity() external view returns (bool);
```

- *ZetaNonEthInterface.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12) ):

```solidity
10:     function burnFrom(address account, uint256 amount) external;

12:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external;
```

- *ZetaInteractor.sol* ( [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L37), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L43), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54) ):

```solidity
37:     constructor(address zetaConnectorAddress) {

43:     function _isValidCaller() private view {

54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L21), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101), [103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103), [126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184), [209](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209) ):

```solidity
21:     function withdraw(uint256 wad) external;

71:     constructor(

101:     receive() external payable {}

103:     function getZetaFromEth(

126:     function getZetaFromToken(

151:     function getEthFromZeta(

184:     function getTokenFromZeta(

209:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L27), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99), [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203) ):

```solidity
21:     function deposit() external payable;

23:     function withdraw(uint256 wad) external;

25:     function depositTo(address to) external payable;

27:     function withdrawTo(address payable to, uint256 value) external;

45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

66:     receive() external payable {}

68:     function getPair(address token0, address token1) internal pure returns (address, address) {

74:     function getZetaFromEth(

99:     function getZetaFromToken(

136:     function getEthFromZeta(

166:     function getTokenFromZeta(

203:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124), [162](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162) ):

```solidity
26:     constructor(address zetaToken_, address uniswapV2Router_) {

34:     function getZetaFromEth(

58:     function getZetaFromToken(

95:     function getEthFromZeta(

124:     function getTokenFromZeta(

162:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L21), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42), [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184) ):

```solidity
21:     function withdraw(uint256 wad) external;

42:     constructor(

72:     receive() external payable {}

74:     function getZetaFromEth(

98:     function getZetaFromToken(

124:     function getEthFromZeta(

158:     function getTokenFromZeta(

184:     function hasZetaLiquidity() external view override returns (bool) {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17) ):

```solidity
17:     function getPools(
```

- *Interfaces.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L54) ):

```solidity
8:     function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

10:     function wZetaContractAddress() external view returns (address);

12:     function uniswapv2FactoryAddress() external view returns (address);

14:     function gasPriceByChainId(uint256 chainID) external view returns (uint256);

16:     function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

18:     function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

22:     function totalSupply() external view returns (uint256);

24:     function balanceOf(address account) external view returns (uint256);

26:     function transfer(address recipient, uint256 amount) external returns (bool);

28:     function allowance(address owner, address spender) external view returns (uint256);

30:     function approve(address spender, uint256 amount) external returns (bool);

32:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

34:     function deposit(address to, uint256 amount) external returns (bool);

36:     function withdraw(bytes memory to, uint256 amount) external returns (bool);

38:     function withdrawGasFee() external view returns (address, uint256);

50:     function name() external view returns (string memory);

52:     function symbol() external view returns (string memory);

54:     function decimals() external view returns (uint8);
```

- *ZRC20.sol* ( [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L41), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L45), [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L178), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L191), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L199), [211](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L211) ):

```solidity
41:     function _msgSender() internal view virtual returns (address) {

45:     function _msgData() internal view virtual returns (bytes calldata) {

178:     function _transfer(address sender, address recipient, uint256 amount) internal virtual {

191:     function _mint(address account, uint256 amount) internal virtual {

199:     function _burn(address account, uint256 amount) internal virtual {

211:     function _approve(address owner, address spender, uint256 amount) internal virtual {
```

- *ZetaConnectorZEVM.sol* ( [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79) ):

```solidity
50:     function transferFrom(address src, address dst, uint wad) external returns (bool);

52:     function withdraw(uint wad) external;

79:     constructor(address wzeta_) {
```

- *IUniswapV2Router01.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129) ):

```solidity
5:     function factory() external pure returns (address);

7:     function WETH() external pure returns (address);

9:     function addLiquidity(

20:     function addLiquidityETH(

29:     function removeLiquidity(

39:     function removeLiquidityETH(

48:     function removeLiquidityWithPermit(

62:     function removeLiquidityETHWithPermit(

75:     function swapExactTokensForTokens(

83:     function swapTokensForExactTokens(

91:     function swapExactETHForTokens(

98:     function swapTokensForExactETH(

106:     function swapExactTokensForETH(

114:     function swapETHForExactTokens(

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);
```

- *IUniswapV2Router02.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44) ):

```solidity
7:     function removeLiquidityETHSupportingFeeOnTransferTokens(

16:     function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(

29:     function swapExactTokensForTokensSupportingFeeOnTransferTokens(

37:     function swapExactETHForTokensSupportingFeeOnTransferTokens(

44:     function swapExactTokensForETHSupportingFeeOnTransferTokens(
```

- *IWZETA.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24) ):

```solidity
10:     function totalSupply() external view returns (uint);

12:     function balanceOf(address owner) external view returns (uint);

14:     function allowance(address owner, address spender) external view returns (uint);

16:     function approve(address spender, uint wad) external returns (bool);

18:     function transfer(address to, uint wad) external returns (bool);

20:     function transferFrom(address from, address to, uint wad) external returns (bool);

22:     function deposit() external payable;

24:     function withdraw(uint wad) external;
```

- *IZRC20.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29) ):

```solidity
5:     function totalSupply() external view returns (uint256);

7:     function balanceOf(address account) external view returns (uint256);

9:     function transfer(address recipient, uint256 amount) external returns (bool);

11:     function allowance(address owner, address spender) external view returns (uint256);

13:     function approve(address spender, uint256 amount) external returns (bool);

15:     function decreaseAllowance(address spender, uint256 amount) external returns (bool);

17:     function increaseAllowance(address spender, uint256 amount) external returns (bool);

19:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

21:     function deposit(address to, uint256 amount) external returns (bool);

23:     function burn(address account, uint256 amount) external returns (bool);

25:     function withdraw(bytes memory to, uint256 amount) external returns (bool);

27:     function withdrawGasFee() external view returns (address, uint256);

29:     function PROTOCOL_FEE() external view returns (uint256);
```

- *zContract.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11) ):

```solidity
11:     function onCrossChainCall(
```

</details>

### [N-44] Modifiers missing NatSpec `@param` tag

Each modifier parameter should have a `@param` notation to improve the code documentation.

There are 2 instances:

- *ZetaInteractor.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30) ):

```solidity
/// @audit Missing @param for `zetaMessage`
23:     modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {

/// @audit Missing @param for `zetaRevert`
30:     modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
```

### [N-45] Functions missing NatSpec `@return` tag

Functions missing NatSpec `@return` tag

<details>
<summary>There are 97 instances (click to show):</summary>

- *ZetaConnector.eth.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23) ):

```solidity
23:     function getLockedAmount() external view returns (uint256) {
```

- *ZetaConnector.non-eth.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27) ):

```solidity
27:     function getLockedAmount() external view returns (uint256) {
```

- *ZetaInterfaces.sol* ( [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83), [85-90](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85-L90), [92-96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92-L96), [98-103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98-L103), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L105) ):

```solidity
83:     function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

85:     function getZetaFromToken(
86:         address destinationAddress,
87:         uint256 minAmountOut,
88:         address inputToken,
89:         uint256 inputTokenAmount
90:     ) external returns (uint256);

92:     function getEthFromZeta(
93:         address destinationAddress,
94:         uint256 minAmountOut,
95:         uint256 zetaTokenAmount
96:     ) external returns (uint256);

98:     function getTokenFromZeta(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address outputToken,
102:         uint256 zetaTokenAmount
103:     ) external returns (uint256);

105:     function hasZetaLiquidity() external view returns (bool);
```

- *ZetaInteractor.sol* ( [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L50) ):

```solidity
50:     function _isValidChainId(uint256 chainId) internal view returns (bool) {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [103-106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L106), [126-131](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L131), [151-155](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L155), [184-189](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L189), [209](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209) ):

```solidity
103:     function getZetaFromEth(
104:         address destinationAddress,
105:         uint256 minAmountOut
106:     ) external payable override returns (uint256) {

126:     function getZetaFromToken(
127:         address destinationAddress,
128:         uint256 minAmountOut,
129:         address inputToken,
130:         uint256 inputTokenAmount
131:     ) external override returns (uint256) {

151:     function getEthFromZeta(
152:         address destinationAddress,
153:         uint256 minAmountOut,
154:         uint256 zetaTokenAmount
155:     ) external override returns (uint256) {

184:     function getTokenFromZeta(
185:         address destinationAddress,
186:         uint256 minAmountOut,
187:         address outputToken,
188:         uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {

209:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68), [74-77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L77), [99-104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L104), [136-140](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L140), [166-171](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L171), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203) ):

```solidity
68:     function getPair(address token0, address token1) internal pure returns (address, address) {

74:     function getZetaFromEth(
75:         address destinationAddress,
76:         uint256 minAmountOut
77:     ) external payable override returns (uint256) {

99:     function getZetaFromToken(
100:         address destinationAddress,
101:         uint256 minAmountOut,
102:         address inputToken,
103:         uint256 inputTokenAmount
104:     ) external override returns (uint256) {

136:     function getEthFromZeta(
137:         address destinationAddress,
138:         uint256 minAmountOut,
139:         uint256 zetaTokenAmount
140:     ) external override returns (uint256) {

166:     function getTokenFromZeta(
167:         address destinationAddress,
168:         uint256 minAmountOut,
169:         address outputToken,
170:         uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {

203:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [34-37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34-L37), [58-63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L63), [95-99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L99), [124-129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L129), [162](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162) ):

```solidity
34:     function getZetaFromEth(
35:         address destinationAddress,
36:         uint256 minAmountOut
37:     ) external payable override returns (uint256) {

58:     function getZetaFromToken(
59:         address destinationAddress,
60:         uint256 minAmountOut,
61:         address inputToken,
62:         uint256 inputTokenAmount
63:     ) external override returns (uint256) {

95:     function getEthFromZeta(
96:         address destinationAddress,
97:         uint256 minAmountOut,
98:         uint256 zetaTokenAmount
99:     ) external override returns (uint256) {

124:     function getTokenFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         address outputToken,
128:         uint256 zetaTokenAmount
129:     ) external override returns (uint256) {

162:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [74-77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L77), [98-103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L103), [124-128](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L128), [158-163](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L163), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184) ):

```solidity
74:     function getZetaFromEth(
75:         address destinationAddress,
76:         uint256 minAmountOut
77:     ) external payable override returns (uint256) {

98:     function getZetaFromToken(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address inputToken,
102:         uint256 inputTokenAmount
103:     ) external override returns (uint256) {

124:     function getEthFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         uint256 zetaTokenAmount
128:     ) external override returns (uint256) {

158:     function getTokenFromZeta(
159:         address destinationAddress,
160:         uint256 minAmountOut,
161:         address outputToken,
162:         uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {

184:     function hasZetaLiquidity() external view override returns (bool) {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [17-22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17-L22) ):

```solidity
17:     function getPools(
18:         address token0,
19:         address token1,
20:         uint256 startIndex,
21:         uint256 count
22:     ) external view returns (address[] memory pairPools);
```

- *TridentIPoolRouter.sol* ( [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L55), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L59), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L63), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L67) ):

```solidity
55:     function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);

59:     function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);

63:     function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn);

67:     function exactOutput(ExactOutputParams calldata params) external payable returns (uint256 amountIn);
```

- *Interfaces.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L54) ):

```solidity
8:     function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

10:     function wZetaContractAddress() external view returns (address);

12:     function uniswapv2FactoryAddress() external view returns (address);

14:     function gasPriceByChainId(uint256 chainID) external view returns (uint256);

16:     function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

18:     function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

22:     function totalSupply() external view returns (uint256);

24:     function balanceOf(address account) external view returns (uint256);

26:     function transfer(address recipient, uint256 amount) external returns (bool);

28:     function allowance(address owner, address spender) external view returns (uint256);

30:     function approve(address spender, uint256 amount) external returns (bool);

32:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

34:     function deposit(address to, uint256 amount) external returns (bool);

36:     function withdraw(bytes memory to, uint256 amount) external returns (bool);

38:     function withdrawGasFee() external view returns (address, uint256);

50:     function name() external view returns (string memory);

52:     function symbol() external view returns (string memory);

54:     function decimals() external view returns (uint8);
```

- *SystemContract.sol* ( [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87) ):

```solidity
87:     function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
```

- *ZRC20.sol* ( [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L41), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L45), [236](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236) ):

```solidity
41:     function _msgSender() internal view virtual returns (address) {

45:     function _msgData() internal view virtual returns (bytes calldata) {

236:     function withdrawGasFee() public view override returns (address, uint256) {
```

- *ZetaConnectorZEVM.sol* ( [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50) ):

```solidity
50:     function transferFrom(address src, address dst, uint wad) external returns (bool);
```

- *IUniswapV2Router01.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7), [9-18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18), [20-27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27), [29-37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L37), [39-46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L46), [48-60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60), [62-73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73), [75-81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L81), [83-89](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L89), [91-96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91-L96), [98-104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L104), [106-112](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L112), [114-119](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114-L119), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129) ):

```solidity
5:     function factory() external pure returns (address);

7:     function WETH() external pure returns (address);

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

20:     function addLiquidityETH(
21:         address token,
22:         uint amountTokenDesired,
23:         uint amountTokenMin,
24:         uint amountETHMin,
25:         address to,
26:         uint deadline
27:     ) external payable returns (uint amountToken, uint amountETH, uint liquidity);

29:     function removeLiquidity(
30:         address tokenA,
31:         address tokenB,
32:         uint liquidity,
33:         uint amountAMin,
34:         uint amountBMin,
35:         address to,
36:         uint deadline
37:     ) external returns (uint amountA, uint amountB);

39:     function removeLiquidityETH(
40:         address token,
41:         uint liquidity,
42:         uint amountTokenMin,
43:         uint amountETHMin,
44:         address to,
45:         uint deadline
46:     ) external returns (uint amountToken, uint amountETH);

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

75:     function swapExactTokensForTokens(
76:         uint amountIn,
77:         uint amountOutMin,
78:         address[] calldata path,
79:         address to,
80:         uint deadline
81:     ) external returns (uint[] memory amounts);

83:     function swapTokensForExactTokens(
84:         uint amountOut,
85:         uint amountInMax,
86:         address[] calldata path,
87:         address to,
88:         uint deadline
89:     ) external returns (uint[] memory amounts);

91:     function swapExactETHForTokens(
92:         uint amountOutMin,
93:         address[] calldata path,
94:         address to,
95:         uint deadline
96:     ) external payable returns (uint[] memory amounts);

98:     function swapTokensForExactETH(
99:         uint amountOut,
100:         uint amountInMax,
101:         address[] calldata path,
102:         address to,
103:         uint deadline
104:     ) external returns (uint[] memory amounts);

106:     function swapExactTokensForETH(
107:         uint amountIn,
108:         uint amountOutMin,
109:         address[] calldata path,
110:         address to,
111:         uint deadline
112:     ) external returns (uint[] memory amounts);

114:     function swapETHForExactTokens(
115:         uint amountOut,
116:         address[] calldata path,
117:         address to,
118:         uint deadline
119:     ) external payable returns (uint[] memory amounts);

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);
```

- *IUniswapV2Router02.sol* ( [7-14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7-L14), [16-27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L27) ):

```solidity
7:     function removeLiquidityETHSupportingFeeOnTransferTokens(
8:         address token,
9:         uint liquidity,
10:         uint amountTokenMin,
11:         uint amountETHMin,
12:         address to,
13:         uint deadline
14:     ) external returns (uint amountETH);

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
```

- *IWZETA.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20) ):

```solidity
10:     function totalSupply() external view returns (uint);

12:     function balanceOf(address owner) external view returns (uint);

14:     function allowance(address owner, address spender) external view returns (uint);

16:     function approve(address spender, uint wad) external returns (bool);

18:     function transfer(address to, uint wad) external returns (bool);

20:     function transferFrom(address from, address to, uint wad) external returns (bool);
```

- *IZRC20.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29) ):

```solidity
5:     function totalSupply() external view returns (uint256);

7:     function balanceOf(address account) external view returns (uint256);

9:     function transfer(address recipient, uint256 amount) external returns (bool);

11:     function allowance(address owner, address spender) external view returns (uint256);

13:     function approve(address spender, uint256 amount) external returns (bool);

15:     function decreaseAllowance(address spender, uint256 amount) external returns (bool);

17:     function increaseAllowance(address spender, uint256 amount) external returns (bool);

19:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

21:     function deposit(address to, uint256 amount) external returns (bool);

23:     function burn(address account, uint256 amount) external returns (bool);

25:     function withdraw(bytes memory to, uint256 amount) external returns (bool);

27:     function withdrawGasFee() external view returns (address, uint256);

29:     function PROTOCOL_FEE() external view returns (uint256);
```

</details>

### [N-46] State variables should have NatSpec descriptions

It is [recommended](https://docs.soliditylang.org/en/v0.8.20/natspec-format.html#tags) to use the NatSpec tags `@notice`, `@dev`, `@return`, `@inheritdoc` for public state variables, and `@dev` for non-public state variables.

<details>
<summary>There are 12 instances (click to show):</summary>

- *Zeta.non-eth.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L11) ):

```solidity
11:     address public connectorAddress;
```

- *ZetaConnector.non-eth.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16) ):

```solidity
16:     uint256 public maxSupply = 2 ** 256 - 1;
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L69) ):

```solidity
69:     bool internal _locked;
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L43) ):

```solidity
43:     bool internal _locked;
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L40) ):

```solidity
40:     bool internal _locked;
```

- *SystemContract.sol* ( [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L28) ):

```solidity
28:     mapping(uint256 => address) public gasZetaPoolByChainId;
```

- *ZRC20.sol* ( [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L39) ):

```solidity
34:     mapping(address => uint256) private _balances;

35:     mapping(address => mapping(address => uint256)) private _allowances;

36:     uint256 private _totalSupply;

37:     string private _name;

38:     string private _symbol;

39:     uint8 private _decimals;
```

</details>

### [N-47] Struct names should use CapWords style

It is recommended by the [Solidity Style Guide](https://docs.soliditylang.org/en/latest/style-guide.html#struct-names).

There is 1 instance:

- *zContract.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L4) ):

```solidity
4: struct zContext {
```

### [N-48] Contract name does not follow the Solidity Style Guide

According to the [Solidity Style Guide](https://docs.soliditylang.org/en/latest/style-guide.html#contract-and-library-names), contracts and libraries should be named using the CapWords style.

There is 1 instance:

- *zContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10) ):

```solidity
10: interface zContract {
```

### [N-49] Functions should be named in mixedCase style

As the [Solidity Style Guide](https://docs.soliditylang.org/en/v0.8.21/style-guide.html#function-names) suggests: functions should be named in mixedCase style.

<details>
<summary>There are 9 instances (click to show):</summary>

- *ERC20Custody.sol* ( [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L107) ):

```solidity
80:     function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {

107:     function renounceTSSAddressUpdater() external onlyTSSUpdater {
```

- *Interfaces.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16) ):

```solidity
8:     function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

16:     function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);
```

- *SystemContract.sol* ( [134](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134), [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L156), [167](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L167) ):

```solidity
134:     function setGasCoinZRC20(uint256 chainID, address zrc20) external {

156:     function setWZETAContractAddress(address addr) external {

167:     function setConnectorZEVMAddress(address addr) external {
```

- *IUniswapV2Router01.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7) ):

```solidity
7:     function WETH() external pure returns (address);
```

- *IZRC20.sol* ( [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29) ):

```solidity
29:     function PROTOCOL_FEE() external view returns (uint256);
```

</details>

### [N-50] Variable names for `immutable`s should use UPPER_CASE_WITH_UNDERSCORES

For `immutable` variable names, each word should use all capital letters, with underscores separating each word (UPPER_CASE_WITH_UNDERSCORES)

<details>
<summary>There are 26 instances (click to show):</summary>

- *ERC20Custody.sol* ( [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L34) ):

```solidity
32:     uint256 public immutable zetaMaxFee;

34:     IERC20 public immutable zeta;
```

- *ZetaConnector.base.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L16) ):

```solidity
16:     address public immutable zetaToken;
```

- *ZetaInteractor.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L12) ):

```solidity
11:     uint256 internal immutable currentChainId;

12:     ZetaConnector public immutable connector;
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L60), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L61), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L63), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L66), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L67) ):

```solidity
60:     uint24 public immutable zetaPoolFee;

61:     uint24 public immutable tokenPoolFee;

63:     address public immutable WETH9Address;

64:     address public immutable zetaToken;

66:     ISwapRouterPancake public immutable pancakeV3Router;

67:     IUniswapV3Factory public immutable uniswapV3Factory;
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L38), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L41) ):

```solidity
37:     address internal immutable WETH9Address;

38:     address public immutable zetaToken;

40:     IPoolRouter public immutable tridentRouter;

41:     ConcentratedLiquidityPoolFactory public immutable poolFactory;
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24) ):

```solidity
21:     address internal immutable wETH;

22:     address public immutable zetaToken;

24:     IUniswapV2Router02 internal immutable uniswapV2Router;
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L35), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L38) ):

```solidity
31:     uint24 public immutable zetaPoolFee;

32:     uint24 public immutable tokenPoolFee;

34:     address public immutable WETH9Address;

35:     address public immutable zetaToken;

37:     ISwapRouter public immutable uniswapV3Router;

38:     IUniswapV3Factory public immutable uniswapV3Factory;
```

- *SystemContract.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L34) ):

```solidity
33:     address public immutable uniswapv2FactoryAddress;

34:     address public immutable uniswapv2Router02Address;
```

</details>

### [N-51] Modifiers should be named in mixedCase style

As the [Solidity Style Guide](https://docs.soliditylang.org/en/latest/style-guide.html#modifier-names) suggests: modifiers should be named in mixedCase style. Use mixedCase. Examples: `onlyBy`, `onlyAfter`, `onlyDuringThePreSale`.

There are 2 instances:

- *ERC20Custody.sol* ( [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L51), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L61) ):

```solidity
51:     modifier onlyTSS() {

61:     modifier onlyTSSUpdater() {
```

### [N-52] Order of contract layout does not follow the Solidity Style Guide

As suggested by the [Solidity Style Guide](https://docs.soliditylang.org/en/v0.8.20/style-guide.html#order-of-layout):
- Layout contract elements in the following order: `pragma statements`, `import statements`, `interfaces`, `libraries`, `contracts`.
- Inside each contract, library or interface, use the following order: `type declarations`, `state variables`, `events`, `errors`, `modifiers`, `functions`.

<details>
<summary>There are 9 instances (click to show):</summary>

- *ERC20Custody.sol* ( [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L24) ):

```solidity
/// @audit ↑ Out of order with error ZeroFee
24:     bool public paused;
```

- *ZetaConnector.base.sol* ( [93](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L93) ):

```solidity
/// @audit ↑ Out of order with constructor ()
93:     modifier onlyPauser() {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94) ):

```solidity
/// @audit ↑ Out of order with constructor ()
94:     modifier nonReentrant() {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59) ):

```solidity
/// @audit ↑ Out of order with constructor ()
59:     modifier nonReentrant() {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65) ):

```solidity
/// @audit ↑ Out of order with constructor ()
65:     modifier nonReentrant() {
```

- *Interfaces.sol* ( [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40) ):

```solidity
/// @audit ↑ Out of order with function withdrawGasFee()
40:     event Transfer(address indexed from, address indexed to, uint256 value);
```

- *ZRC20.sol* ( [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L52) ):

```solidity
/// @audit ↑ Out of order with function _msgData()
52:     modifier onlyFungible() {
```

- *ZetaConnectorZEVM.sol* ( [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63) ):

```solidity
/// @audit ↑ Out of order with error FailedZetaSent
63:     address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
```

- *IZRC20.sol* ( [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31) ):

```solidity
/// @audit ↑ Out of order with function PROTOCOL_FEE()
31:     event Transfer(address indexed from, address indexed to, uint256 value);
```

</details>

### [N-53] Missing zero address check in functions with address parameters

Adding a zero address check for each address type parameter can prevent errors.

<details>
<summary>There are 23 instances (click to show):</summary>

- *ERC20Custody.sol* ( [144](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144), [153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153), [165-170](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L170), [193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193) ):

```solidity
/// @audit `asset not checked`
144:     function whitelist(IERC20 asset) external onlyTSS {

/// @audit `asset not checked`
153:     function unwhitelist(IERC20 asset) external onlyTSS {

/// @audit `asset not checked`
165:     function deposit(
166:         bytes calldata recipient,
167:         IERC20 asset,
168:         uint256 amount,
169:         bytes calldata message
170:     ) external nonReentrant {

/// @audit `recipient not checked`
/// @audit `asset not checked`
193:     function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
```

- *Zeta.non-eth.sol* ( [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73) ):

```solidity
/// @audit `mintee not checked`
62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

/// @audit `account not checked`
73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```

- *ZetaConnector.base.sol* ( [172-179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185-193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193) ):

```solidity
/// @audit `destinationAddress not checked`
172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

/// @audit `zetaTxSenderAddress not checked`
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

- *ZetaConnector.eth.sol* ( [52-59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L59), [77-85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L85) ):

```solidity
/// @audit `destinationAddress not checked`
52:     function onReceive(
53:         bytes calldata zetaTxSenderAddress,
54:         uint256 sourceChainId,
55:         address destinationAddress,
56:         uint256 zetaValue,
57:         bytes calldata message,
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress {

/// @audit `zetaTxSenderAddress not checked`
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

- *ZetaConnector.non-eth.sol* ( [61-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L68), [87-95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L95) ):

```solidity
/// @audit `destinationAddress not checked`
61:     function onReceive(
62:         bytes calldata zetaTxSenderAddress,
63:         uint256 sourceChainId,
64:         address destinationAddress,
65:         uint256 zetaValue,
66:         bytes calldata message,
67:         bytes32 internalSendHash
68:     ) external override onlyTssAddress {

/// @audit `zetaTxSenderAddress not checked`
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

- *SystemContract.sol* ( [67-73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L73), [134](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L145) ):

```solidity
/// @audit `zrc20 not checked`
67:     function depositAndCall(
68:         zContext calldata context,
69:         address zrc20,
70:         uint256 amount,
71:         address target,
72:         bytes calldata message
73:     ) external {

/// @audit `zrc20 not checked`
134:     function setGasCoinZRC20(uint256 chainID, address zrc20) external {

/// @audit `erc20 not checked`
145:     function setGasZetaPool(uint256 chainID, address erc20) external {
```

- *ZRC20.sol* ( [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157), [225](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225), [270](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270) ):

```solidity
/// @audit `recipient not checked`
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {

/// @audit `spender not checked`
145:     function approve(address spender, uint256 amount) public virtual override returns (bool) {

/// @audit `sender not checked`
/// @audit `recipient not checked`
157:     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {

/// @audit `to not checked`
225:     function deposit(address to, uint256 amount) external override returns (bool) {

/// @audit `addr not checked`
270:     function updateSystemContractAddress(address addr) external onlyFungible {
```

- *ZetaConnectorZEVM.sol* ( [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114) ):

```solidity
/// @audit `wzeta_ not checked`
114:     function setWzetaAddress(address wzeta_) external {
```

</details>

### [N-54] Named imports of parent contracts are missing

Consider adding named imports for all parent contracts.

<details>
<summary>There are 20 instances (click to show):</summary>

- *ERC20Custody.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11) ):

```solidity
/// @audit ReentrancyGuard
11: contract ERC20Custody is ReentrancyGuard {
```

- *Zeta.eth.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9) ):

```solidity
/// @audit ERC20
9: contract ZetaEth is ERC20("Zeta", "ZETA") {
```

- *Zeta.non-eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10) ):

```solidity
/// @audit ZetaNonEthInterface
/// @audit ERC20Burnable
/// @audit ZetaErrors
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```

- *ZetaConnector.base.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15) ):

```solidity
/// @audit ConnectorErrors
/// @audit Pausable
15: contract ZetaConnectorBase is ConnectorErrors, Pausable {
```

- *ZetaConnector.eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15) ):

```solidity
/// @audit ZetaConnectorBase
15: contract ZetaConnectorEth is ZetaConnectorBase {
```

- *ZetaConnector.non-eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15) ):

```solidity
/// @audit ZetaConnectorBase
15: contract ZetaConnectorNonEth is ZetaConnectorBase {
```

- *ZetaNonEthInterface.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9) ):

```solidity
/// @audit IERC20
9: interface ZetaNonEthInterface is IERC20 {
```

- *ZetaInteractor.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9) ):

```solidity
/// @audit Ownable2Step
/// @audit ZetaInteractorErrors
9: abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56) ):

```solidity
/// @audit IUniswapV3SwapCallback
24: interface ISwapRouterPancake is IUniswapV3SwapCallback {

/// @audit ZetaTokenConsumer
56: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33) ):

```solidity
/// @audit ZetaTokenConsumer
33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17) ):

```solidity
/// @audit ZetaTokenConsumer
17: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27) ):

```solidity
/// @audit ZetaTokenConsumer
27: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *ZRC20.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20) ):

```solidity
/// @audit IZRC20
/// @audit IZRC20Metadata
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

- *IUniswapV2Router02.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6) ):

```solidity
/// @audit IUniswapV2Router01
6: interface IUniswapV2Router02 is IUniswapV2Router01 {
```

</details>

### [N-55] Constants should be put on the left side of comparisons

Putting constants on the left side of comparison statements is a best practice known as [Yoda conditions](https://en.wikipedia.org/wiki/Yoda_conditions).
Although solidity's static typing system prevents accidental assignments within conditionals, adopting this practice can improve code readability and consistency, especially when working across multiple languages.

<details>
<summary>There are 97 instances (click to show):</summary>

- *ERC20Custody.sol* ( [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L81), [93](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L93), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L108), [122](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L122), [177](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L177) ):

```solidity
/// @audit put `address(0)` on the left
81:         if (TSSAddress_ == address(0)) {

/// @audit put `0` on the left
93:         if (zetaFee_ == 0) {

/// @audit put `address(0)` on the left
108:         if (TSSAddress == address(0)) {

/// @audit put `address(0)` on the left
122:         if (TSSAddress == address(0)) {

/// @audit put `0` on the left
177:         if (zetaFee != 0 && address(zeta) != address(0)) {
```

- *Zeta.non-eth.sol* ( [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L34), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L34), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L42), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L42), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L56) ):

```solidity
/// @audit put `address(0)` on the left
34:         if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();

/// @audit put `address(0)` on the left
34:         if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();

/// @audit put `address(0)` on the left
42:         if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();

/// @audit put `address(0)` on the left
42:         if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();

/// @audit put `address(0)` on the left
56:         if (tssAddress == address(0)) revert InvalidAddress();
```

- *ZetaConnector.base.sol* ( [76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L77), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L79), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L118), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L130), [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L141) ):

```solidity
/// @audit put `address(0)` on the left
76:             zetaToken_ == address(0) ||

/// @audit put `address(0)` on the left
77:             tssAddress_ == address(0) ||

/// @audit put `address(0)` on the left
78:             tssAddressUpdater_ == address(0) ||

/// @audit put `address(0)` on the left
79:             pauserAddress_ == address(0)

/// @audit put `address(0)` on the left
118:         if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
130:         if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
141:         if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

- *ZetaInteractor.sol* ( [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L38) ):

```solidity
/// @audit put `address(0)` on the left
38:         if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L80), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L81), [82](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L82), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L83), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L107), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L108), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L132), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L132), [133](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L133), [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L156), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L157), [190](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L190), [190](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L190), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191), [212](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L212) ):

```solidity
/// @audit put `address(0)` on the left
80:             zetaToken_ == address(0) ||

/// @audit put `address(0)` on the left
81:             pancakeV3Router_ == address(0) ||

/// @audit put `address(0)` on the left
82:             uniswapV3Factory_ == address(0) ||

/// @audit put `address(0)` on the left
83:             WETH9Address_ == address(0)

/// @audit put `address(0)` on the left
107:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
108:         if (msg.value == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
133:         if (inputTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
156:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
157:         if (zetaTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
190:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
190:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
191:         if (zetaTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
212:         if (poolAddress == address(0)) {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L47), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L48), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L49), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L50), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L79), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L105), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L105), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L106), [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L141), [142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L142), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L172), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L172), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173) ):

```solidity
/// @audit put `address(0)` on the left
47:             zetaToken_ == address(0) ||

/// @audit put `address(0)` on the left
48:             uniswapV3Router_ == address(0) ||

/// @audit put `address(0)` on the left
49:             WETH9Address_ == address(0) ||

/// @audit put `address(0)` on the left
50:             poolFactory_ == address(0)

/// @audit put `address(0)` on the left
78:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
79:         if (msg.value == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
106:         if (inputTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
141:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
142:         if (zetaTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
172:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
172:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
173:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L39), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L64), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L64), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L65), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L100), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L101), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L130), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L130), [131](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131) ):

```solidity
/// @audit put `address(0)` on the left
27:         if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
27:         if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
38:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
39:         if (msg.value == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
65:         if (inputTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
100:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
101:         if (zetaTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
130:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
130:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
131:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L51), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L52), [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L53), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L54), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79), [104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104), [104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L129), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130), [164](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164), [164](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165), [187](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L187) ):

```solidity
/// @audit put `address(0)` on the left
51:             zetaToken_ == address(0) ||

/// @audit put `address(0)` on the left
52:             uniswapV3Router_ == address(0) ||

/// @audit put `address(0)` on the left
53:             uniswapV3Factory_ == address(0) ||

/// @audit put `address(0)` on the left
54:             WETH9Address_ == address(0)

/// @audit put `address(0)` on the left
78:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
79:         if (msg.value == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
105:         if (inputTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
129:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
130:         if (zetaTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `address(0)` on the left
164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

/// @audit put `0` on the left
165:         if (zetaTokenAmount == 0) revert InputCantBeZero();

/// @audit put `address(0)` on the left
187:         if (poolAddress == address(0)) {
```

- *SystemContract.sol* ( [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L75), [90](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L90), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135), [146](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L158), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168), [169](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L169) ):

```solidity
/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
52:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
74:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
75:         if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();

/// @audit put `address(0)` on the left
90:         if (token0 == address(0)) revert CantBeZeroAddress();

/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
124:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
135:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
146:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
157:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

/// @audit put `address(0)` on the left
158:         if (addr == address(0)) revert ZeroAddress();

/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
168:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

/// @audit put `address(0)` on the left
169:         if (addr == address(0)) revert ZeroAddress();
```

- *ZRC20.sol* ( [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69), [179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L179), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L180), [192](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L192), [200](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L200), [212](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L212), [213](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L213), [226](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226), [238](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L238), [242](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L242) ):

```solidity
/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
53:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
69:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

/// @audit put `address(0)` on the left
179:         if (sender == address(0)) revert ZeroAddress();

/// @audit put `address(0)` on the left
180:         if (recipient == address(0)) revert ZeroAddress();

/// @audit put `address(0)` on the left
192:         if (account == address(0)) revert ZeroAddress();

/// @audit put `address(0)` on the left
200:         if (account == address(0)) revert ZeroAddress();

/// @audit put `address(0)` on the left
212:         if (owner == address(0)) revert ZeroAddress();

/// @audit put `address(0)` on the left
213:         if (spender == address(0)) revert ZeroAddress();

/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();

/// @audit put `address(0)` on the left
238:         if (gasZRC20 == address(0)) {

/// @audit put `0` on the left
242:         if (gasPrice == 0) {
```

- *ZetaConnectorZEVM.sol* ( [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115) ):

```solidity
/// @audit put `FUNGIBLE_MODULE_ADDRESS` on the left
115:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
```

</details>

### [N-56] Each interfaces should be defined in a separate file

Each interface should be defined in a separate file, making it easier to import, and easier to develop and maintain. This is the strategy adopted by most popular libraries.

<details>
<summary>There are 20 instances (click to show):</summary>

- *ZetaInterfaces.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108) ):

```solidity
4: interface ZetaInterfaces {

49: interface ZetaConnector {

56: interface ZetaReceiver {

77: interface ZetaTokenConsumer {

108: interface ZetaCommonErrors {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {

24: interface ISwapRouterPancake is IUniswapV3SwapCallback {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerTridentErrors {

20: interface WETH9 {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10) ):

```solidity
10: interface ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {
```

- *Interfaces.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L7), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49) ):

```solidity
7: interface ISystem {

21: interface IZRC20 {

49: interface IZRC20Metadata is IZRC20 {
```

- *SystemContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10) ):

```solidity
10: interface SystemContractErrors {
```

- *ZRC20.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8) ):

```solidity
8: interface ZRC20Errors {
```

- *ZetaConnectorZEVM.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49) ):

```solidity
4: interface ZetaInterfaces {

49: interface WZETA {
```

</details>

### [N-57] Put all system-wide constants in one file

Putting all the system-wide constants in a single file improves code readability, makes it easier to understand the basic configuration and limitations of the system, and makes maintenance easier.

There are 3 instances:

- *SystemContract.sol* ( [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L31) ):

```solidity
31:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

- *ZRC20.sol* ( [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22) ):

```solidity
22:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

- *ZetaConnectorZEVM.sol* ( [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63) ):

```solidity
63:     address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
```

### [N-58] SPDX-License-Identifier not provided

Before publishing, consider adding a comment containing "SPDX-License-Identifier: <SPDX-License>" to each source file. Use "SPDX-License-Identifier: UNLICENSED" for non-open-source code. Please see https://spdx.org for more information.

There are 2 instances:

- [*ImmutableCreate2Factory.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol)

- [*WZETA.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol)

### [N-59] SPDX identifier should be the in the first line of a solidity file

SPDX identifier should be the in the first line of a solidity file.

There are 2 instances:

- *ImmutableCreate2Factory.sol* ( [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L1) ):

```solidity
1: pragma solidity 0.5.10; // optimization enabled, 99999 runs, evm: petersburg
```

- *WZETA.sol* ( [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1) ):

```solidity
1: pragma solidity ^0.4.18;
```

### [N-60] `TODO`s left in the code

TODOs may signal that a feature is missing or not ready for audit, consider resolving the issue and removing the TODO comment

There is 1 instance:

- *ZetaTokenConsumerTrident.strategy.sol* ( [204](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L204) ):

```solidity
204:         //@TODO: Implement
```

### [N-61] Typos

All typos should be corrected.

There is 1 instance:

- *ERC20Custody.sol* ( [182](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L182) ):

```solidity
/// @audit exepected
182:         // In case if there is a fee on a token transfer, we might not receive a full exepected amount
```

### [N-62] Unnecessary casting

Unnecessary castings can be removed.

There is 1 instance:

- *ERC20Custody.sol* ( [197](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L197) ):

```solidity
/// @audit IERC20(asset)
197:         IERC20(asset).safeTransfer(recipient, amount);
```

### [N-63] Unused contract variables

The following state variables are defined but not used.
It is recommended to check the code for logical omissions that cause them not to be used. If it's determined that they are not needed anywhere, it's best to remove them from the codebase to improve code clarity and minimize confusion.

There are 2 instances:

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58) ):

```solidity
58:     uint256 internal constant MAX_DEADLINE = 200;
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35) ):

```solidity
35:     uint256 internal constant MAX_DEADLINE = 200;
```

### [N-64] Unused function parameters

Function parameters that are defined but not used may be logical errors and need to be checked to see if any logic is missing.
If the parameter is not really needed, it should be removed, otherwise it will repeatedly cause confusion and make code maintenance difficult.
If the parameter cannot be removed directly (for example, if it is an override function), its name should be removed and some comment can be appended.

<details>
<summary>There are 14 instances (click to show):</summary>

- *ZetaConnector.base.sol* ( [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166), [172-179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185-193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193) ):

```solidity
/// @audit input
166:     function send(ZetaInterfaces.SendInput calldata input) external virtual {}

/// @audit zetaTxSenderAddress
/// @audit sourceChainId
/// @audit destinationAddress
/// @audit zetaValue
/// @audit message
/// @audit internalSendHash
172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

/// @audit zetaTxSenderAddress
/// @audit sourceChainId
/// @audit destinationAddress
/// @audit destinationChainId
/// @audit remainingZetaValue
/// @audit message
/// @audit internalSendHash
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

</details>

### [N-65] Unused modifiers

The following `modifier`s are not used. It is recommended to check the code for logical omissions that cause them not to be used. If it's determined that they are not needed anywhere, it's best to remove them from the codebase to improve code clarity and minimize confusion.

There are 2 instances:

- *ZetaInteractor.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30) ):

```solidity
23:     modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {

30:     modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
```

### [N-66] Use delete instead of assigning values to `false`

The `delete` keyword more closely matches the semantics of what is being done, and draws more attention to the changing of state, which may lead to a more thorough audit of its associated logic.

There are 5 instances:

- *ERC20Custody.sol* ( [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L136), [154](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L154) ):

```solidity
136:         paused = false;

154:         whitelisted[asset] = false;
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L98) ):

```solidity
98:         _locked = false;
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L63) ):

```solidity
63:         _locked = false;
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L69) ):

```solidity
69:         _locked = false;
```

### [N-67] Use the latest Solidity version

Upgrading to the [latest solidity version](https://github.com/ethereum/solc-js/tags) (0.8.19 for L2s) can optimize gas usage, take advantage of new features and improve overall contract efficiency. Where possible, based on compatibility requirements, it is recommended to use newer/latest solidity version to take advantage of the latest optimizations and features.

<details>
<summary>There are 29 instances (click to show):</summary>

- *ERC20Custody.sol* ( [3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L3) ):

```solidity
3: pragma solidity 0.8.7;
```

- *Zeta.eth.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *Zeta.non-eth.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaConnector.base.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaConnector.eth.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaConnector.non-eth.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ConnectorErrors.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaErrors.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaInteractorErrors.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaInterfaces.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaNonEthInterface.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- [*ImmutableCreate2Factory.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol)

- *ZetaInteractor.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *Interfaces.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *SystemContract.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- [*Uniswap.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Uniswap.sol)

- *UniswapPeriphery.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L2) ):

```solidity
2: pragma solidity 0.6.6;
```

- [*WZETA.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol)

- *ZRC20.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaConnectorZEVM.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *IUniswapV2Router01.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *IUniswapV2Router02.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *IWZETA.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *IZRC20.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *zContract.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

</details>

### [N-68] Named mappings are recommended

[Named mappings](https://docs.soliditylang.org/en/v0.8.18/types.html#mapping-types) (with syntax `mapping(KeyType KeyName? => ValueType ValueName?)`) are recommended.It can make the mapping variables clearer, more readable and easier to maintain.

<details>
<summary>There are 8 instances (click to show):</summary>

- *ERC20Custody.sol* ( [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36) ):

```solidity
36:     mapping(IERC20 => bool) public whitelisted;
```

- *ZetaInteractor.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L21) ):

```solidity
21:     mapping(uint256 => bytes) public interactorsByChainId;
```

- *SystemContract.sol* ( [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L28) ):

```solidity
24:     mapping(uint256 => uint256) public gasPriceByChainId;

26:     mapping(uint256 => address) public gasCoinZRC20ByChainId;

28:     mapping(uint256 => address) public gasZetaPoolByChainId;
```

- *ZRC20.sol* ( [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35) ):

```solidity
34:     mapping(address => uint256) private _balances;

35:     mapping(address => mapping(address => uint256)) private _allowances;

35:     mapping(address => mapping(address => uint256)) private _allowances;
```

</details>

### [N-69] Use transfer libraries instead of low level calls to transfer native tokens

Consider using [`SafeTransferLib.safeTransferETH`](https://github.com/transmissions11/solmate/blob/fadb2e2778adbf01c80275bfb99e5c14969d964b/src/utils/SafeTransferLib.sol#L15) or [`Address.sendValue`](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/9e3f4d60c581010c4a3979480e07cc7752f124cc/contracts/utils/Address.sol#L41) for clearer semantic meaning instead of using a low level `call`.

There are 3 instances:

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178) ):

```solidity
178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [152](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152) ):

```solidity
152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

- *ZetaConnectorZEVM.sol* ( [96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96) ):

```solidity
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```

### [N-70] Use `type(X).max` instead of constant formulas like `2**n`

Earlier versions of solidity can use `uint<n>(-1)` instead. Expressions `2**n -1` can often be rewritten to accommodate the change (e.g. by using a `>` instead of a `>=`, which will also saves gas).

There is 1 instance:

- *ZetaConnector.non-eth.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16) ):

```solidity
16:     uint256 public maxSupply = 2 ** 256 - 1;
```

### [N-71] Using underscore at the end of variable name

The use of the underscore at the end of the variable name is unusual, consider refactoring it.

<details>
<summary>There are 60 instances (click to show):</summary>

- *ERC20Custody.sol* ( [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L92) ):

```solidity
/// @audit TSSAddressUpdater_
44:     event RenouncedTSSUpdater(address TSSAddressUpdater_);

/// @audit TSSAddress_
45:     event UpdatedTSSAddress(address TSSAddress_);

/// @audit zetaFee_
46:     event UpdatedZetaFee(uint256 zetaFee_);

/// @audit TSSAddress_
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

/// @audit TSSAddressUpdater_
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

/// @audit zetaFee_
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

/// @audit zetaMaxFee_
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

/// @audit zeta_
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

/// @audit TSSAddress_
80:     function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {

/// @audit zetaFee_
92:     function updateZetaFee(uint256 zetaFee_) external onlyTSS {
```

- *Zeta.non-eth.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40) ):

```solidity
/// @audit tssAddress_
33:     constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

/// @audit tssAddressUpdater_
33:     constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

/// @audit tssAddress_
40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

/// @audit connectorAddress_
40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {
```

- *ZetaConnector.base.sol* ( [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74), [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117), [128](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L128) ):

```solidity
/// @audit zetaToken_
74:     constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {

/// @audit tssAddress_
74:     constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {

/// @audit tssAddressUpdater_
74:     constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {

/// @audit pauserAddress_
74:     constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {

/// @audit pauserAddress_
117:     function updatePauserAddress(address pauserAddress_) external onlyPauser {

/// @audit tssAddress_
128:     function updateTssAddress(address tssAddress_) external {
```

- *ZetaConnector.eth.sol* ( [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L17), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L18), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L19), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L20) ):

```solidity
/// @audit zetaToken_
17:         address zetaToken_,

/// @audit tssAddress_
18:         address tssAddress_,

/// @audit tssAddressUpdater_
19:         address tssAddressUpdater_,

/// @audit pauserAddress_
20:         address pauserAddress_
```

- *ZetaConnector.non-eth.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L21), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L22), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L23), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L24), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31) ):

```solidity
/// @audit zetaTokenAddress_
21:         address zetaTokenAddress_,

/// @audit tssAddress_
22:         address tssAddress_,

/// @audit tssAddressUpdater_
23:         address tssAddressUpdater_,

/// @audit pauserAddress_
24:         address pauserAddress_

/// @audit maxSupply_
31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L72), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L73), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L74), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L75), [76](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L76), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L77) ):

```solidity
/// @audit zetaToken_
72:         address zetaToken_,

/// @audit pancakeV3Router_
73:         address pancakeV3Router_,

/// @audit uniswapV3Factory_
74:         address uniswapV3Factory_,

/// @audit WETH9Address_
75:         address WETH9Address_,

/// @audit zetaPoolFee_
76:         uint24 zetaPoolFee_,

/// @audit tokenPoolFee_
77:         uint24 tokenPoolFee_
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45) ):

```solidity
/// @audit zetaToken_
45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

/// @audit uniswapV3Router_
45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

/// @audit WETH9Address_
45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

/// @audit poolFactory_
45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26) ):

```solidity
/// @audit zetaToken_
26:     constructor(address zetaToken_, address uniswapV2Router_) {

/// @audit uniswapV2Router_
26:     constructor(address zetaToken_, address uniswapV2Router_) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L46), [47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L47), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L48) ):

```solidity
/// @audit zetaToken_
43:         address zetaToken_,

/// @audit uniswapV3Router_
44:         address uniswapV3Router_,

/// @audit uniswapV3Factory_
45:         address uniswapV3Factory_,

/// @audit WETH9Address_
46:         address WETH9Address_,

/// @audit zetaPoolFee_
47:         uint24 zetaPoolFee_,

/// @audit tokenPoolFee_
48:         uint24 tokenPoolFee_
```

- *SystemContract.sol* ( [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51), [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51), [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51) ):

```solidity
/// @audit wzeta_
51:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {

/// @audit uniswapv2Factory_
51:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {

/// @audit uniswapv2Router02_
51:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
```

- *ZRC20.sol* ( [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L61), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L62), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L63), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L64), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L65), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L66), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L67) ):

```solidity
/// @audit name_
61:         string memory name_,

/// @audit symbol_
62:         string memory symbol_,

/// @audit decimals_
63:         uint8 decimals_,

/// @audit chainid_
64:         uint256 chainid_,

/// @audit coinType_
65:         CoinType coinType_,

/// @audit gasLimit_
66:         uint256 gasLimit_,

/// @audit systemContractAddress_
67:         address systemContractAddress_
```

- *ZetaConnectorZEVM.sol* ( [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114) ):

```solidity
/// @audit wzeta_
77:     event SetWZETA(address wzeta_);

/// @audit wzeta_
79:     constructor(address wzeta_) {

/// @audit wzeta_
114:     function setWzetaAddress(address wzeta_) external {
```

</details>

### [N-72] Whitespace in Expressions

See the [Whitespace in Expressions](https://docs.soliditylang.org/en/latest/style-guide.html#whitespace-in-expressions) section of the Solidity Style Guide.

There are 3 instances:

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L178) ):

```solidity
/// @audit Whitespace inside parenthesis
178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [152](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152) ):

```solidity
/// @audit Whitespace inside parenthesis
152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
```

- *ZetaConnectorZEVM.sol* ( [96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96) ):

```solidity
/// @audit Whitespace inside parenthesis
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}("");
```

### [N-73] Use a struct to encapsulate multiple function parameters

If a function has too many parameters, replacing them with a struct can improve code readability and maintainability, increase reusability, and reduce the likelihood of errors when passing the parameters.

<details>
<summary>There are 8 instances (click to show):</summary>

- *ERC20Custody.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68) ):

```solidity
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
```

- *ZetaConnector.base.sol* ( [172-179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185-193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193) ):

```solidity
172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

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

- *ZetaConnector.non-eth.sol* ( [61-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L68) ):

```solidity
61:     function onReceive(
62:         bytes calldata zetaTxSenderAddress,
63:         uint256 sourceChainId,
64:         address destinationAddress,
65:         uint256 zetaValue,
66:         bytes calldata message,
67:         bytes32 internalSendHash
68:     ) external override onlyTssAddress {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [71-78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L78) ):

```solidity
71:     constructor(
72:         address zetaToken_,
73:         address pancakeV3Router_,
74:         address uniswapV3Factory_,
75:         address WETH9Address_,
76:         uint24 zetaPoolFee_,
77:         uint24 tokenPoolFee_
78:     ) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [42-49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L49) ):

```solidity
42:     constructor(
43:         address zetaToken_,
44:         address uniswapV3Router_,
45:         address uniswapV3Factory_,
46:         address WETH9Address_,
47:         uint24 zetaPoolFee_,
48:         uint24 tokenPoolFee_
49:     ) {
```

- *SystemContract.sol* ( [67-73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L73) ):

```solidity
67:     function depositAndCall(
68:         zContext calldata context,
69:         address zrc20,
70:         uint256 amount,
71:         address target,
72:         bytes calldata message
73:     ) external {
```

- *ZRC20.sol* ( [60-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L68) ):

```solidity
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

</details>

### [N-74] Returning a struct instead of a bunch of variables is better

If a function returns [too many variables](https://docs.soliditylang.org/en/v0.8.21/contracts.html#returning-multiple-values), replacing them with a struct can improve code readability, maintainability and reusability.

There are 5 instances:

- *ZetaTokenConsumerTrident.strategy.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68) ):

```solidity
68:     function getPair(address token0, address token1) internal pure returns (address, address) {
```

- *Interfaces.sol* ( [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L38) ):

```solidity
38:     function withdrawGasFee() external view returns (address, uint256);
```

- *SystemContract.sol* ( [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87) ):

```solidity
87:     function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
```

- *ZRC20.sol* ( [236](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236) ):

```solidity
236:     function withdrawGasFee() public view override returns (address, uint256) {
```

- *IZRC20.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27) ):

```solidity
27:     function withdrawGasFee() external view returns (address, uint256);
```

### [N-75] Events that mark critical parameter changes should contain both the old and the new value

This should especially be done if the new value is not required to be different from the old value.

<details>
<summary>There are 11 instances (click to show):</summary>

- *ERC20Custody.sol* ( [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L85), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L100) ):

```solidity
85:         emit UpdatedTSSAddress(TSSAddress_);

100:         emit UpdatedZetaFee(zetaFee_);
```

- *ZetaConnector.non-eth.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L33) ):

```solidity
33:         emit MaxSupplyUpdated(msg.sender, maxSupply_);
```

- *SystemContract.sol* ( [137](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L137), [149](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L149), [160](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L160), [171](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L171) ):

```solidity
137:         emit SetGasCoin(chainID, zrc20);

149:         emit SetGasZetaPool(chainID, pool);

160:         emit SetWZeta(wZetaContractAddress);

171:         emit SetConnectorZEVM(zetaConnectorZEVMAddress);
```

- *ZRC20.sol* ( [272](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L272), [281](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L281), [290](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L290) ):

```solidity
272:         emit UpdatedSystemContract(addr);

281:         emit UpdatedGasLimit(gasLimit);

290:         emit UpdatedProtocolFlatFee(protocolFlatFee);
```

- *ZetaConnectorZEVM.sol* ( [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L117) ):

```solidity
117:         emit SetWZETA(wzeta_);
```

</details>

### [N-76] Contract variables should have comments

Consider adding some comments on non-public contract variables to explain what they are supposed to do. This will help for future code reviews.

<details>
<summary>There are 13 instances (click to show):</summary>

- *ZetaInteractor.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11) ):

```solidity
11:     uint256 internal immutable currentChainId;
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L69) ):

```solidity
69:     bool internal _locked;
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L43) ):

```solidity
37:     address internal immutable WETH9Address;

43:     bool internal _locked;
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24) ):

```solidity
21:     address internal immutable wETH;

24:     IUniswapV2Router02 internal immutable uniswapV2Router;
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L40) ):

```solidity
40:     bool internal _locked;
```

- *ZRC20.sol* ( [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L37), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L39) ):

```solidity
34:     mapping(address => uint256) private _balances;

35:     mapping(address => mapping(address => uint256)) private _allowances;

36:     uint256 private _totalSupply;

37:     string private _name;

38:     string private _symbol;

39:     uint8 private _decimals;
```

</details>

### [N-77] File is missing NatSpec

It is recommended that Solidity contracts are fully annotated using NatSpec

There are 7 instances:

- [*TridentConcentratedLiquidityPoolFactory.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol)

- [*UniswapPeriphery.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol)

- [*IUniswapV2Router01.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol)

- [*IUniswapV2Router02.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol)

- [*IWZETA.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol)

- [*IZRC20.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol)

- [*zContract.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol)

### [N-78] Modifier declarations should have NatSpec descriptions

Modifier declarations should have NatSpec descriptions

There are 5 instances:

- *ZetaInteractor.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30) ):

```solidity
23:     modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {

30:     modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94) ):

```solidity
94:     modifier nonReentrant() {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59) ):

```solidity
59:     modifier nonReentrant() {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65) ):

```solidity
65:     modifier nonReentrant() {
```

### [N-79] Empty bytes check is missing

Passing empty bytes to a function can cause unexpected behavior, such as certain operations failing, producing incorrect results, or wasting gas. It is recommended to check that all byte parameters are not empty.

<details>
<summary>There are 13 instances (click to show):</summary>

- *ERC20Custody.sol* ( [165-170](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L170) ):

```solidity
/// @audit recipient
/// @audit message
165:     function deposit(
166:         bytes calldata recipient,
167:         IERC20 asset,
168:         uint256 amount,
169:         bytes calldata message
170:     ) external nonReentrant {
```

- *ZetaConnector.base.sol* ( [172-179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185-193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193) ):

```solidity
/// @audit zetaTxSenderAddress
/// @audit message
172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

/// @audit destinationAddress
/// @audit message
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

- *ZetaConnector.eth.sol* ( [52-59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L59), [77-85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L85) ):

```solidity
/// @audit zetaTxSenderAddress
52:     function onReceive(
53:         bytes calldata zetaTxSenderAddress,
54:         uint256 sourceChainId,
55:         address destinationAddress,
56:         uint256 zetaValue,
57:         bytes calldata message,
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress {

/// @audit destinationAddress
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

- *ZetaConnector.non-eth.sol* ( [61-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L68), [87-95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L95) ):

```solidity
/// @audit zetaTxSenderAddress
61:     function onReceive(
62:         bytes calldata zetaTxSenderAddress,
63:         uint256 sourceChainId,
64:         address destinationAddress,
65:         uint256 zetaValue,
66:         bytes calldata message,
67:         bytes32 internalSendHash
68:     ) external override onlyTssAddress {

/// @audit destinationAddress
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

- *ZetaInteractor.sol* ( [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54) ):

```solidity
/// @audit contractAddress
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```

- *SystemContract.sol* ( [67-73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L73) ):

```solidity
/// @audit message
67:     function depositAndCall(
68:         zContext calldata context,
69:         address zrc20,
70:         uint256 amount,
71:         address target,
72:         bytes calldata message
73:     ) external {
```

- *ZRC20.sol* ( [256](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256) ):

```solidity
/// @audit to
256:     function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
```

</details>

### [N-80] Contract functions should use an `interface`

All `external`/`public` functions should extend an `interface`. This is useful to ensure that the whole API is extracted and can be more easily integrated by other projects.

<details>
<summary>There are 42 instances (click to show):</summary>

- *ERC20Custody.sol* ( [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L92), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L107), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L118), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L132), [144](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144), [153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153), [165-170](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L170), [193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193) ):

```solidity
80:     function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {

92:     function updateZetaFee(uint256 zetaFee_) external onlyTSS {

107:     function renounceTSSAddressUpdater() external onlyTSSUpdater {

118:     function pause() external onlyTSS {

132:     function unpause() external onlyTSS {

144:     function whitelist(IERC20 asset) external onlyTSS {

153:     function unwhitelist(IERC20 asset) external onlyTSS {

165:     function deposit(
166:         bytes calldata recipient,
167:         IERC20 asset,
168:         uint256 amount,
169:         bytes calldata message
170:     ) external nonReentrant {

193:     function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
```

- *Zeta.non-eth.sol* ( [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L54) ):

```solidity
40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

54:     function renounceTssAddressUpdater() external {
```

- *ZetaConnector.base.sol* ( [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117), [128](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L128), [140](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L140), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L151), [159](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L159), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166), [172-179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185-193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193) ):

```solidity
117:     function updatePauserAddress(address pauserAddress_) external onlyPauser {

128:     function updateTssAddress(address tssAddress_) external {

140:     function renounceTssAddressUpdater() external onlyTssUpdater {

151:     function pause() external onlyPauser {

159:     function unpause() external onlyPauser {

166:     function send(ZetaInterfaces.SendInput calldata input) external virtual {}

172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

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

- *ZetaConnector.eth.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31), [52-59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L59), [77-85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L85) ):

```solidity
23:     function getLockedAmount() external view returns (uint256) {

31:     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

52:     function onReceive(
53:         bytes calldata zetaTxSenderAddress,
54:         uint256 sourceChainId,
55:         address destinationAddress,
56:         uint256 zetaValue,
57:         bytes calldata message,
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress {

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

- *ZetaConnector.non-eth.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40), [61-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L68), [87-95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L95) ):

```solidity
27:     function getLockedAmount() external view returns (uint256) {

31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {

40:     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

61:     function onReceive(
62:         bytes calldata zetaTxSenderAddress,
63:         uint256 sourceChainId,
64:         address destinationAddress,
65:         uint256 zetaValue,
66:         bytes calldata message,
67:         bytes32 internalSendHash
68:     ) external override onlyTssAddress {

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

- *ZetaInteractor.sol* ( [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54) ):

```solidity
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```

- *SystemContract.sol* ( [67-73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L73), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L100), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123), [134](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L145), [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L156), [167](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L167) ):

```solidity
67:     function depositAndCall(
68:         zContext calldata context,
69:         address zrc20,
70:         uint256 amount,
71:         address target,
72:         bytes calldata message
73:     ) external {

100:     function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {

123:     function setGasPrice(uint256 chainID, uint256 price) external {

134:     function setGasCoinZRC20(uint256 chainID, address zrc20) external {

145:     function setGasZetaPool(uint256 chainID, address erc20) external {

156:     function setWZETAContractAddress(address addr) external {

167:     function setConnectorZEVMAddress(address addr) external {
```

- *ZRC20.sol* ( [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173), [270](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270), [279](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L279), [288](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L288) ):

```solidity
173:     function burn(uint256 amount) external returns (bool) {

270:     function updateSystemContractAddress(address addr) external onlyFungible {

279:     function updateGasLimit(uint256 gasLimit) external onlyFungible {

288:     function updateProtocolFlatFee(uint256 protocolFlatFee) external onlyFungible {
```

- *ZetaConnectorZEVM.sol* ( [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114) ):

```solidity
92:     function send(ZetaInterfaces.SendInput calldata input) external {

114:     function setWzetaAddress(address wzeta_) external {
```

</details>

### [N-81] Interface files should not use fixed compiler versions

Interfaces should not use fixed compiler versions, since they may be used by projects using a different version.

<details>
<summary>There are 13 instances (click to show):</summary>

- *ConnectorErrors.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaErrors.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaInteractorErrors.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaInterfaces.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *ZetaNonEthInterface.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- [*ImmutableCreate2Factory.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol)

- *Interfaces.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- [*Uniswap.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Uniswap.sol)

- *IUniswapV2Router01.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *IUniswapV2Router02.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *IWZETA.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *IZRC20.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

- *zContract.sol* ( [2](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L2) ):

```solidity
2: pragma solidity 0.8.7;
```

</details>

### [N-82] Addresses shouldn't be hard-coded

It is often better to declare `address`es as `constant` or `immutable` which can be assigned in constructor. This allows the code to remain the same across deployments on different networks, and avoids recompilation when addresses need to change.

There are 3 instances:

- *SystemContract.sol* ( [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L31) ):

```solidity
31:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

- *ZRC20.sol* ( [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22) ):

```solidity
22:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

- *ZetaConnectorZEVM.sol* ( [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63) ):

```solidity
63:     address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
```

### [N-83] Control structures do not follow the Solidity Style Guide

Refer to the [Solidity style guide - Control Structures](https://docs.soliditylang.org/en/v0.8.20/style-guide.html#control-structures).

<details>
<summary>There are 98 instances (click to show):</summary>

- *Zeta.non-eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L54), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73) ):

```solidity
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {

40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

54:     function renounceTssAddressUpdater() external {

62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```

- *ZetaConnector.base.sol* ( [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L75), [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L94), [102](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L102), [110](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L110), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L118), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L129), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L130), [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L141), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166), [172-179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179), [185-193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193) ):

```solidity
75:         if (

94:         if (msg.sender != pauserAddress) revert CallerIsNotPauser(msg.sender);

102:         if (msg.sender != tssAddress) revert CallerIsNotTss(msg.sender);

110:         if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);

118:         if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

129:         if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);

130:         if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

141:         if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

166:     function send(ZetaInterfaces.SendInput calldata input) external virtual {}

172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual {}

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

- *ZetaConnector.eth.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L33), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L61), [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L87) ):

```solidity
33:         if (!success) revert ZetaTransferError();

61:         if (!success) revert ZetaTransferError();

87:         if (!success) revert ZetaTransferError();
```

- *ZetaConnector.non-eth.sol* ( [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L69), [96](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L96) ):

```solidity
69:         if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);

96:         if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
```

- *ZetaInteractor.sol* ( [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L25), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L33), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L38), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L44) ):

```solidity
25:         if (keccak256(zetaMessage.zetaTxSenderAddress) != keccak256(interactorsByChainId[zetaMessage.sourceChainId]))

32:         if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();

33:         if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();

38:         if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

44:         if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L79), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L95), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L107), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L108), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L132), [133](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L133), [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L156), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L157), [179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L179), [190](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L190), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191) ):

```solidity
79:         if (

95:         if (_locked) revert ReentrancyError();

107:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

108:         if (msg.value == 0) revert InputCantBeZero();

132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

133:         if (inputTokenAmount == 0) revert InputCantBeZero();

156:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

157:         if (zetaTokenAmount == 0) revert InputCantBeZero();

179:         if (!sent) revert ErrorSendingETH();

190:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

191:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L46), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L60), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L69), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L79), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L105), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L106), [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L141), [142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L142), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L172), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173) ):

```solidity
46:         if (

60:         if (_locked) revert ReentrancyError();

69:         if (token0 < token1) return (token0, token1);

78:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

79:         if (msg.value == 0) revert InputCantBeZero();

105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

106:         if (inputTokenAmount == 0) revert InputCantBeZero();

141:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

142:         if (zetaTokenAmount == 0) revert InputCantBeZero();

172:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

173:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L39), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L64), [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L65), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L100), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L101), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L130), [131](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131) ):

```solidity
27:         if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();

38:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

39:         if (msg.value == 0) revert InputCantBeZero();

64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

65:         if (inputTokenAmount == 0) revert InputCantBeZero();

100:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

101:         if (zetaTokenAmount == 0) revert InputCantBeZero();

130:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

131:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L50), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L66), [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79), [104](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L129), [130](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130), [153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L153), [164](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165) ):

```solidity
50:         if (

66:         if (_locked) revert ReentrancyError();

78:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

79:         if (msg.value == 0) revert InputCantBeZero();

104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

105:         if (inputTokenAmount == 0) revert InputCantBeZero();

129:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();

130:         if (zetaTokenAmount == 0) revert InputCantBeZero();

153:         if (!sent) revert ErrorSendingETH();

164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();

165:         if (zetaTokenAmount == 0) revert InputCantBeZero();
```

- *SystemContract.sol* ( [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L75), [88](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L88), [90](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L90), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135), [146](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L158), [168](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168), [169](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L169) ):

```solidity
52:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

74:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

75:         if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();

88:         if (tokenA == tokenB) revert CantBeIdenticalAddresses();

90:         if (token0 == address(0)) revert CantBeZeroAddress();

124:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

135:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

146:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

157:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

158:         if (addr == address(0)) revert ZeroAddress();

168:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

169:         if (addr == address(0)) revert ZeroAddress();
```

- *Uniswap.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L7) ):

```solidity
7: contract UniswapImports {}
```

- *UniswapPeriphery.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6) ):

```solidity
6: contract UniswapImports {}
```

- *ZRC20.sol* ( [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53), [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69), [161](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L161), [179](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L179), [180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L180), [183](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L183), [192](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L192), [200](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L200), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L203), [212](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L212), [213](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L213), [226](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226) ):

```solidity
53:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

69:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

161:         if (currentAllowance < amount) revert LowAllowance();

179:         if (sender == address(0)) revert ZeroAddress();

180:         if (recipient == address(0)) revert ZeroAddress();

183:         if (senderBalance < amount) revert LowBalance();

192:         if (account == address(0)) revert ZeroAddress();

200:         if (account == address(0)) revert ZeroAddress();

203:         if (accountBalance < amount) revert LowBalance();

212:         if (owner == address(0)) revert ZeroAddress();

213:         if (spender == address(0)) revert ZeroAddress();

226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();
```

- *ZetaConnectorZEVM.sol* ( [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L85), [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L94), [97](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L97), [115](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115) ):

```solidity
85:         if (msg.sender != wzeta) revert OnlyWZETA();

94:         if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();

97:         if (!sent) revert FailedZetaSent();

115:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
```

</details>

### [N-84] Functions contain the same code

The functions below have the same implementation as is seen in other files. The functions should be refactored into functions of a common base contract.

<details>
<summary>There are 2 instances (click to show):</summary>

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [209-219](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209-L219) ):

```solidity
/// @audit Seen on line 184 of contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
209:     function hasZetaLiquidity() external view override returns (bool) {
210:         address poolAddress = uniswapV3Factory.getPool(WETH9Address, zetaToken, zetaPoolFee);
211: 
212:         if (poolAddress == address(0)) {
213:             return false;
214:         }
215: 
216:         //@dev: if pool does exist, get its liquidity
217:         IUniswapV3Pool pool = IUniswapV3Pool(poolAddress);
218:         return pool.liquidity() > 0;
219:     }
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [184-194](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184-L194) ):

```solidity
/// @audit Seen on line 209 of contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
184:     function hasZetaLiquidity() external view override returns (bool) {
185:         address poolAddress = uniswapV3Factory.getPool(WETH9Address, zetaToken, zetaPoolFee);
186: 
187:         if (poolAddress == address(0)) {
188:             return false;
189:         }
190: 
191:         //@dev: if pool does exist, get its liquidity
192:         IUniswapV3Pool pool = IUniswapV3Pool(poolAddress);
193:         return pool.liquidity() > 0;
194:     }
```

</details>

### [N-85] Inconsistent spacing in comments

The comments below are in the `//x` format, which differs from the commonly used idiomatic comment syntax of `//<space>x`. It is recommended to use a consistent comment syntax throughout.

There are 2 instances:

- *Uniswap.sol* ( [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L1) ):

```solidity
1: //SPDX-License-Identifier: MIT
```

- *UniswapPeriphery.sol* ( [1](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L1) ):

```solidity
1: //SPDX-License-Identifier: MIT
```

### [N-86] Missing event for critical changes

Events should be emitted when critical changes are made to the contracts.

There is 1 instance:

- *ZetaInteractor.sol* ( [54-56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L56) ):

```solidity
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
55:         interactorsByChainId[destinationChainId] = contractAddress;
56:     }
```

### [N-87] Duplicated `require()`/`revert()` checks should be refactored

Refactoring duplicate `require()`/`revert()` checks into a modifier or function can make the code more concise, readable and maintainable, and less likely to make errors or omissions when modifying the `require()` or `revert()`.

<details>
<summary>There are 12 instances (click to show):</summary>

- *ERC20Custody.sol* ( [175](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L175) ):

```solidity
/// @audit Duplicated on line 195
175:             revert NotWhitelisted();
```

- *Zeta.non-eth.sol* ( [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L66) ):

```solidity
/// @audit Duplicated on line 77
66:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
```

- *ZetaConnector.eth.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L33) ):

```solidity
/// @audit Duplicated on line 61, 87
33:         if (!success) revert ZetaTransferError();
```

- *ZetaConnector.non-eth.sol* ( [69](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L69) ):

```solidity
/// @audit Duplicated on line 97
69:         if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
```

- *SystemContract.sol* ( [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52) ):

```solidity
/// @audit Duplicated on line 74, 124, 135, 146, 157, 168
52:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

- *ZRC20.sol* ( [183](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L183) ):

```solidity
/// @audit Duplicated on line 203
183:         if (senderBalance < amount) revert LowBalance();
```

</details>

### [N-88] Consider adding emergency-stop functionality

Adding a way to quickly halt protocol functionality in an emergency, rather than having to pause individual contracts one-by-one, will make in-progress hack mitigation faster and much less stressful.

<details>
<summary>There are 14 instances (click to show):</summary>

- *ERC20Custody.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11) ):

```solidity
11: contract ERC20Custody is ReentrancyGuard {
```

- *Zeta.eth.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9) ):

```solidity
9: contract ZetaEth is ERC20("Zeta", "ZETA") {
```

- *Zeta.non-eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10) ):

```solidity
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```

- *ZetaConnector.base.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15) ):

```solidity
15: contract ZetaConnectorBase is ConnectorErrors, Pausable {
```

- *ZetaConnector.eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15) ):

```solidity
15: contract ZetaConnectorEth is ZetaConnectorBase {
```

- *ZetaConnector.non-eth.sol* ( [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15) ):

```solidity
15: contract ZetaConnectorNonEth is ZetaConnectorBase {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56) ):

```solidity
56: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33) ):

```solidity
33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17) ):

```solidity
17: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27) ):

```solidity
27: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```

- *SystemContract.sol* ( [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22) ):

```solidity
22: contract SystemContract is SystemContractErrors {
```

- *UniswapPeriphery.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6) ):

```solidity
6: contract UniswapImports {}
```

- *ZRC20.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20) ):

```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

- *ZetaConnectorZEVM.sol* ( [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55) ):

```solidity
55: contract ZetaConnectorZEVM is ZetaInterfaces {
```

</details>

### [N-89] Avoid the use of sensitive terms

Use [alternative variants](https://www.zdnet.com/article/mysql-drops-master-slave-and-blacklist-whitelist-terminology/), e.g. allowlist/denylist instead of whitelist/blacklist.

<details>
<summary>There are 18 instances (click to show):</summary>

- *ERC20Custody.sol* ( [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41), [141](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L141), [144](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L145), [146](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L146), [150](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L150), [153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153), [154](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L154), [155](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L155), [174](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L174), [175](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L175), [194](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L194), [195](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L195) ):

```solidity
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

- *ZetaInteractorErrors.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L8) ):

```solidity
8:     // @dev Thrown when try to send a message or tokens to a non whitelisted chain
```

</details>

### [N-90] Enable IR-based code generation

The IR-based code generator was introduced with an aim to not only allow code generation to be more transparent and auditable but also to enable more powerful optimization passes that span across functions.
You can enable it on the command line using `--via-ir` or with the option `{"viaIR": true}`.
This will take longer to compile, but you can just simple test it before deploying and if you got a better benchmark then you can add --via-ir to your deploy command
More on: https://docs.soliditylang.org/en/v0.8.17/ir-breaking-changes.html

There is 1 instance:

- Global finding

### [N-91] Contracts should have NatSpec `@dev` tags

The `@dev` tag is used to explain extra details to developers.

<details>
<summary>There are 29 instances (click to show):</summary>

- *ERC20Custody.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11) ):

```solidity
11: contract ERC20Custody is ReentrancyGuard {
```

- *Zeta.non-eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10) ):

```solidity
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```

- *ZetaInterfaces.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49), [56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56), [108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108) ):

```solidity
4: interface ZetaInterfaces {

49: interface ZetaConnector {

56: interface ZetaReceiver {

108: interface ZetaCommonErrors {
```

- *ZetaInteractor.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9) ):

```solidity
9: abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {

24: interface ISwapRouterPancake is IUniswapV3SwapCallback {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerTridentErrors {

20: interface WETH9 {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10) ):

```solidity
10: interface ZetaTokenConsumerUniV2Errors {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20) ):

```solidity
12: interface ZetaTokenConsumerUniV3Errors {

20: interface WETH9 {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16) ):

```solidity
16: interface ConcentratedLiquidityPoolFactory {
```

- *TridentIPoolRouter.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16) ):

```solidity
16: interface IPoolRouter {
```

- *Interfaces.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L21), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49) ):

```solidity
21: interface IZRC20 {

49: interface IZRC20Metadata is IZRC20 {
```

- *UniswapPeriphery.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6) ):

```solidity
6: contract UniswapImports {}
```

- *ZRC20.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20) ):

```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```

- *ZetaConnectorZEVM.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4), [49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49), [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55) ):

```solidity
4: interface ZetaInterfaces {

49: interface WZETA {

55: contract ZetaConnectorZEVM is ZetaInterfaces {
```

- *IUniswapV2Router01.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4) ):

```solidity
4: interface IUniswapV2Router01 {
```

- *IUniswapV2Router02.sol* ( [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6) ):

```solidity
6: interface IUniswapV2Router02 is IUniswapV2Router01 {
```

- *IWZETA.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4) ):

```solidity
4: interface IWETH9 {
```

- *IZRC20.sol* ( [4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4) ):

```solidity
4: interface IZRC20 {
```

- *zContract.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10) ):

```solidity
10: interface zContract {
```

</details>

### [N-92] Error declarations should have NatSpec descriptions

Error declarations should have NatSpec descriptions

<details>
<summary>There are 51 instances (click to show):</summary>

- *ERC20Custody.sol* ( [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L17), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L18), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L19), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L20), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L21) ):

```solidity
14:     error NotWhitelisted();

15:     error NotPaused();

16:     error InvalidSender();

17:     error InvalidTSSUpdater();

18:     error ZeroAddress();

19:     error IsPaused();

20:     error ZetaMaxFeeExceeded();

21:     error ZeroFee();
```

- *ConnectorErrors.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L18), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L24) ):

```solidity
9:     error CallerIsNotPauser(address caller);

12:     error CallerIsNotTss(address caller);

15:     error CallerIsNotTssUpdater(address caller);

18:     error CallerIsNotTssOrUpdater(address caller);

21:     error ZetaTransferError();

24:     error ExceedsMaxSupply(uint256 maxSupply);
```

- *ZetaErrors.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L18), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L21), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L24) ):

```solidity
9:     error CallerIsNotTss(address caller);

12:     error CallerIsNotConnector(address caller);

15:     error CallerIsNotTssUpdater(address caller);

18:     error CallerIsNotTssOrUpdater(address caller);

21:     error InvalidAddress();

24:     error ZetaTransferError();
```

- *ZetaInteractorErrors.sol* ( [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L9), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L12), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L15), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L18) ):

```solidity
9:     error InvalidDestinationChainId();

12:     error InvalidCaller(address caller);

15:     error InvalidZetaMessageCall();

18:     error InvalidZetaRevertCall();
```

- *ZetaInterfaces.sol* ( [109](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L109) ):

```solidity
109:     error InvalidAddress();
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L17) ):

```solidity
13:     error InputCantBeZero();

15:     error ErrorSendingETH();

17:     error ReentrancyError();
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L17) ):

```solidity
13:     error InputCantBeZero();

15:     error ErrorSendingETH();

17:     error ReentrancyError();
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L11) ):

```solidity
11:     error InputCantBeZero();
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L17) ):

```solidity
13:     error InputCantBeZero();

15:     error ErrorSendingETH();

17:     error ReentrancyError();
```

- *SystemContract.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L15) ):

```solidity
11:     error CallerIsNotFungibleModule();

12:     error InvalidTarget();

13:     error CantBeIdenticalAddresses();

14:     error CantBeZeroAddress();

15:     error ZeroAddress();
```

- *ZRC20.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L10), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L11), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L12), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L13), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L14), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L15), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L16), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L17) ):

```solidity
10:     error CallerIsNotFungibleModule();

11:     error InvalidSender();

12:     error GasFeeTransferFailed();

13:     error ZeroGasCoin();

14:     error ZeroGasPrice();

15:     error LowAllowance();

16:     error LowBalance();

17:     error ZeroAddress();
```

- *ZetaConnectorZEVM.sol* ( [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L58), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L59), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L60) ):

```solidity
58:     error WZETATransferFailed();

59:     error OnlyFungibleModule();

60:     error FailedZetaSent();
```

</details>

### [N-93] Missing NatSpec `@dev` from event declaration

Some events have an incomplete NatSpec: add a `@dev` notation to describe the event to improve the code documentation.

<details>
<summary>There are 51 instances (click to show):</summary>

- *ERC20Custody.sol* ( [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46) ):

```solidity
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

- *Zeta.non-eth.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31) ):

```solidity
23:     event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);

25:     event Burnt(address indexed burnee, uint256 amount);

27:     event TSSAddressUpdated(address callerAddress, address newTssAddress);

29:     event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

31:     event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);
```

- *ZetaConnector.base.sol* ( [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L45), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68) ):

```solidity
34:     event ZetaSent(

45:     event ZetaReceived(

54:     event ZetaReverted(

64:     event TSSAddressUpdated(address callerAddress, address newTssAddress);

66:     event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

68:     event PauserAddressUpdated(address callerAddress, address newTssAddress);
```

- *ZetaConnector.non-eth.sol* ( [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18) ):

```solidity
18:     event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
```

- *ZetaInterfaces.sol* ( [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L80), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81) ):

```solidity
78:     event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);

79:     event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

80:     event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);

81:     event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
```

- *Interfaces.sol* ( [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L46) ):

```solidity
40:     event Transfer(address indexed from, address indexed to, uint256 value);

41:     event Approval(address indexed owner, address indexed spender, uint256 value);

42:     event Deposit(bytes from, address indexed to, uint256 value);

43:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);

44:     event UpdatedSystemContract(address systemContract);

45:     event UpdatedGasLimit(uint256 gasLimit);

46:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```

- *SystemContract.sol* ( [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46) ):

```solidity
41:     event SystemContractDeployed();

42:     event SetGasPrice(uint256, uint256);

43:     event SetGasCoin(uint256, address);

44:     event SetGasZetaPool(uint256, address);

45:     event SetWZeta(address);

46:     event SetConnectorZEVM(address);
```

- *ZetaConnectorZEVM.sol* ( [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77) ):

```solidity
67:     event ZetaSent(

77:     event SetWZETA(address wzeta_);
```

- *IWZETA.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8) ):

```solidity
5:     event Approval(address indexed owner, address indexed spender, uint value);

6:     event Transfer(address indexed from, address indexed to, uint value);

7:     event Deposit(address indexed dst, uint wad);

8:     event Withdrawal(address indexed src, uint wad);
```

- *IZRC20.sol* ( [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37) ):

```solidity
31:     event Transfer(address indexed from, address indexed to, uint256 value);

32:     event Approval(address indexed owner, address indexed spender, uint256 value);

33:     event Deposit(bytes from, address indexed to, uint256 value);

34:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

35:     event UpdatedSystemContract(address systemContract);

36:     event UpdatedGasLimit(uint256 gasLimit);

37:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```

</details>

### [N-94] Missing NatSpec `@notice` from event declaration

Some events have an incomplete NatSpec: add a @notice notation to describe the event to improve the code documentation.

<details>
<summary>There are 50 instances (click to show):</summary>

- *ERC20Custody.sol* ( [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46) ):

```solidity
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

- *Zeta.non-eth.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31) ):

```solidity
23:     event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);

25:     event Burnt(address indexed burnee, uint256 amount);

27:     event TSSAddressUpdated(address callerAddress, address newTssAddress);

29:     event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

31:     event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);
```

- *ZetaConnector.base.sol* ( [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L45), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54), [64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68) ):

```solidity
34:     event ZetaSent(

45:     event ZetaReceived(

54:     event ZetaReverted(

64:     event TSSAddressUpdated(address callerAddress, address newTssAddress);

66:     event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);

68:     event PauserAddressUpdated(address callerAddress, address newTssAddress);
```

- *ZetaConnector.non-eth.sol* ( [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18) ):

```solidity
18:     event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
```

- *ZetaInterfaces.sol* ( [78](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L80), [81](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81) ):

```solidity
78:     event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);

79:     event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);

80:     event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);

81:     event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
```

- *Interfaces.sol* ( [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40), [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L41), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L46) ):

```solidity
40:     event Transfer(address indexed from, address indexed to, uint256 value);

41:     event Approval(address indexed owner, address indexed spender, uint256 value);

42:     event Deposit(bytes from, address indexed to, uint256 value);

43:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);

44:     event UpdatedSystemContract(address systemContract);

45:     event UpdatedGasLimit(uint256 gasLimit);

46:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```

- *SystemContract.sol* ( [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45), [46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46) ):

```solidity
42:     event SetGasPrice(uint256, uint256);

43:     event SetGasCoin(uint256, address);

44:     event SetGasZetaPool(uint256, address);

45:     event SetWZeta(address);

46:     event SetConnectorZEVM(address);
```

- *ZetaConnectorZEVM.sol* ( [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77) ):

```solidity
67:     event ZetaSent(

77:     event SetWZETA(address wzeta_);
```

- *IWZETA.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5), [6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7), [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8) ):

```solidity
5:     event Approval(address indexed owner, address indexed spender, uint value);

6:     event Transfer(address indexed from, address indexed to, uint value);

7:     event Deposit(address indexed dst, uint wad);

8:     event Withdrawal(address indexed src, uint wad);
```

- *IZRC20.sol* ( [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32), [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34), [35](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37) ):

```solidity
31:     event Transfer(address indexed from, address indexed to, uint256 value);

32:     event Approval(address indexed owner, address indexed spender, uint256 value);

33:     event Deposit(bytes from, address indexed to, uint256 value);

34:     event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);

35:     event UpdatedSystemContract(address systemContract);

36:     event UpdatedGasLimit(uint256 gasLimit);

37:     event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```

</details>

### [N-95] Missing NatSpec `@dev` from function declaration

Some functions have an incomplete NatSpec: add a `@dev` notation to describe the function to improve the code documentation.

<details>
<summary>There are 136 instances (click to show):</summary>

- *ERC20Custody.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68) ):

```solidity
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
```

- *Zeta.eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10) ):

```solidity
10:     constructor(address creator, uint256 initialSupply) {
```

- *Zeta.non-eth.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73) ):

```solidity
33:     constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```

- *ZetaConnector.eth.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23) ):

```solidity
16:     constructor(

23:     function getLockedAmount() external view returns (uint256) {
```

- *ZetaConnector.non-eth.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31) ):

```solidity
20:     constructor(

27:     function getLockedAmount() external view returns (uint256) {

31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
```

- *ZetaInterfaces.sol* ( [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L105) ):

```solidity
83:     function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

85:     function getZetaFromToken(

92:     function getEthFromZeta(

98:     function getTokenFromZeta(

105:     function hasZetaLiquidity() external view returns (bool);
```

- *ZetaNonEthInterface.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12) ):

```solidity
10:     function burnFrom(address account, uint256 amount) external;

12:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external;
```

- *ZetaInteractor.sol* ( [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L37), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L43), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54) ):

```solidity
37:     constructor(address zetaConnectorAddress) {

43:     function _isValidCaller() private view {

54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L21), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L50), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101), [103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103), [126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184), [209](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209) ):

```solidity
21:     function withdraw(uint256 wad) external;

38:     function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);

50:     function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);

71:     constructor(

101:     receive() external payable {}

103:     function getZetaFromEth(

126:     function getZetaFromToken(

151:     function getEthFromZeta(

184:     function getTokenFromZeta(

209:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L27), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99), [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203) ):

```solidity
21:     function deposit() external payable;

23:     function withdraw(uint256 wad) external;

25:     function depositTo(address to) external payable;

27:     function withdrawTo(address payable to, uint256 value) external;

45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

66:     receive() external payable {}

68:     function getPair(address token0, address token1) internal pure returns (address, address) {

74:     function getZetaFromEth(

99:     function getZetaFromToken(

136:     function getEthFromZeta(

166:     function getTokenFromZeta(

203:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124), [162](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162) ):

```solidity
26:     constructor(address zetaToken_, address uniswapV2Router_) {

34:     function getZetaFromEth(

58:     function getZetaFromToken(

95:     function getEthFromZeta(

124:     function getTokenFromZeta(

162:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L21), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42), [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184) ):

```solidity
21:     function withdraw(uint256 wad) external;

42:     constructor(

72:     receive() external payable {}

74:     function getZetaFromEth(

98:     function getZetaFromToken(

124:     function getEthFromZeta(

158:     function getTokenFromZeta(

184:     function hasZetaLiquidity() external view override returns (bool) {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17) ):

```solidity
17:     function getPools(
```

- *TridentIPoolRouter.sol* ( [55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L55), [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L59), [63](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L63), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L67), [70](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L70) ):

```solidity
55:     function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);

59:     function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);

63:     function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn);

67:     function exactOutput(ExactOutputParams calldata params) external payable returns (uint256 amountIn);

70:     function sweep(address token, uint256 amount, address recipient) external payable;
```

- *Interfaces.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L54) ):

```solidity
8:     function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

10:     function wZetaContractAddress() external view returns (address);

12:     function uniswapv2FactoryAddress() external view returns (address);

14:     function gasPriceByChainId(uint256 chainID) external view returns (uint256);

16:     function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

18:     function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

22:     function totalSupply() external view returns (uint256);

24:     function balanceOf(address account) external view returns (uint256);

26:     function transfer(address recipient, uint256 amount) external returns (bool);

28:     function allowance(address owner, address spender) external view returns (uint256);

30:     function approve(address spender, uint256 amount) external returns (bool);

32:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

34:     function deposit(address to, uint256 amount) external returns (bool);

36:     function withdraw(bytes memory to, uint256 amount) external returns (bool);

38:     function withdrawGasFee() external view returns (address, uint256);

50:     function name() external view returns (string memory);

52:     function symbol() external view returns (string memory);

54:     function decimals() external view returns (uint8);
```

- *ZRC20.sol* ( [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L41), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L45), [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L178), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L191), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L199), [211](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L211) ):

```solidity
41:     function _msgSender() internal view virtual returns (address) {

45:     function _msgData() internal view virtual returns (bytes calldata) {

178:     function _transfer(address sender, address recipient, uint256 amount) internal virtual {

191:     function _mint(address account, uint256 amount) internal virtual {

199:     function _burn(address account, uint256 amount) internal virtual {

211:     function _approve(address owner, address spender, uint256 amount) internal virtual {
```

- *ZetaConnectorZEVM.sol* ( [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79) ):

```solidity
50:     function transferFrom(address src, address dst, uint wad) external returns (bool);

52:     function withdraw(uint wad) external;

79:     constructor(address wzeta_) {
```

- *IUniswapV2Router01.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129) ):

```solidity
5:     function factory() external pure returns (address);

7:     function WETH() external pure returns (address);

9:     function addLiquidity(

20:     function addLiquidityETH(

29:     function removeLiquidity(

39:     function removeLiquidityETH(

48:     function removeLiquidityWithPermit(

62:     function removeLiquidityETHWithPermit(

75:     function swapExactTokensForTokens(

83:     function swapTokensForExactTokens(

91:     function swapExactETHForTokens(

98:     function swapTokensForExactETH(

106:     function swapExactTokensForETH(

114:     function swapETHForExactTokens(

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);
```

- *IUniswapV2Router02.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44) ):

```solidity
7:     function removeLiquidityETHSupportingFeeOnTransferTokens(

16:     function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(

29:     function swapExactTokensForTokensSupportingFeeOnTransferTokens(

37:     function swapExactETHForTokensSupportingFeeOnTransferTokens(

44:     function swapExactTokensForETHSupportingFeeOnTransferTokens(
```

- *IWZETA.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24) ):

```solidity
10:     function totalSupply() external view returns (uint);

12:     function balanceOf(address owner) external view returns (uint);

14:     function allowance(address owner, address spender) external view returns (uint);

16:     function approve(address spender, uint wad) external returns (bool);

18:     function transfer(address to, uint wad) external returns (bool);

20:     function transferFrom(address from, address to, uint wad) external returns (bool);

22:     function deposit() external payable;

24:     function withdraw(uint wad) external;
```

- *IZRC20.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29) ):

```solidity
5:     function totalSupply() external view returns (uint256);

7:     function balanceOf(address account) external view returns (uint256);

9:     function transfer(address recipient, uint256 amount) external returns (bool);

11:     function allowance(address owner, address spender) external view returns (uint256);

13:     function approve(address spender, uint256 amount) external returns (bool);

15:     function decreaseAllowance(address spender, uint256 amount) external returns (bool);

17:     function increaseAllowance(address spender, uint256 amount) external returns (bool);

19:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

21:     function deposit(address to, uint256 amount) external returns (bool);

23:     function burn(address account, uint256 amount) external returns (bool);

25:     function withdraw(bytes memory to, uint256 amount) external returns (bool);

27:     function withdrawGasFee() external view returns (address, uint256);

29:     function PROTOCOL_FEE() external view returns (uint256);
```

- *zContract.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11) ):

```solidity
11:     function onCrossChainCall(
```

</details>

### [N-96] Missing NatSpec `@notice` from function declaration

Some functions have an incomplete NatSpec: add a `@notice` notation to describe the function to improve the code documentation.

<details>
<summary>There are 187 instances (click to show):</summary>

- *ERC20Custody.sol* ( [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68), [80](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L92), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L107), [118](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L118), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L132), [144](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144), [153](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153), [165](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165), [193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193) ):

```solidity
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {

80:     function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {

92:     function updateZetaFee(uint256 zetaFee_) external onlyTSS {

107:     function renounceTSSAddressUpdater() external onlyTSSUpdater {

118:     function pause() external onlyTSS {

132:     function unpause() external onlyTSS {

144:     function whitelist(IERC20 asset) external onlyTSS {

153:     function unwhitelist(IERC20 asset) external onlyTSS {

165:     function deposit(

193:     function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
```

- *Zeta.eth.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10) ):

```solidity
10:     constructor(address creator, uint256 initialSupply) {
```

- *Zeta.non-eth.sol* ( [33](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L54), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62), [73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73) ):

```solidity
33:     constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {

40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {

54:     function renounceTssAddressUpdater() external {

62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {

73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```

- *ZetaConnector.base.sol* ( [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74), [117](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117), [128](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L128), [140](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L140), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L151), [159](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L159), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166), [172](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172), [185](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185) ):

```solidity
74:     constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {

117:     function updatePauserAddress(address pauserAddress_) external onlyPauser {

128:     function updateTssAddress(address tssAddress_) external {

140:     function renounceTssAddressUpdater() external onlyTssUpdater {

151:     function pause() external onlyPauser {

159:     function unpause() external onlyPauser {

166:     function send(ZetaInterfaces.SendInput calldata input) external virtual {}

172:     function onReceive(

185:     function onRevert(
```

- *ZetaConnector.eth.sol* ( [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52), [77](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77) ):

```solidity
16:     constructor(

23:     function getLockedAmount() external view returns (uint256) {

31:     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

52:     function onReceive(

77:     function onRevert(
```

- *ZetaConnector.non-eth.sol* ( [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27), [31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31), [40](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61), [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87) ):

```solidity
20:     constructor(

27:     function getLockedAmount() external view returns (uint256) {

31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {

40:     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {

61:     function onReceive(

87:     function onRevert(
```

- *ZetaInterfaces.sol* ( [53](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L53), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L60), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L66), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L83), [85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L92), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98), [105](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L105) ):

```solidity
53:     function send(ZetaInterfaces.SendInput calldata input) external;

60:     function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external;

66:     function onZetaRevert(ZetaInterfaces.ZetaRevert calldata zetaRevert) external;

83:     function getZetaFromEth(address destinationAddress, uint256 minAmountOut) external payable returns (uint256);

85:     function getZetaFromToken(

92:     function getEthFromZeta(

98:     function getTokenFromZeta(

105:     function hasZetaLiquidity() external view returns (bool);
```

- *ZetaNonEthInterface.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12) ):

```solidity
10:     function burnFrom(address account, uint256 amount) external;

12:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external;
```

- *ZetaInteractor.sol* ( [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L37), [43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L43), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L50), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54) ):

```solidity
37:     constructor(address zetaConnectorAddress) {

43:     function _isValidCaller() private view {

50:     function _isValidChainId(uint256 chainId) internal view returns (bool) {

54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L21), [71](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101), [103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103), [126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126), [151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184), [209](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209) ):

```solidity
21:     function withdraw(uint256 wad) external;

71:     constructor(

101:     receive() external payable {}

103:     function getZetaFromEth(

126:     function getZetaFromToken(

151:     function getEthFromZeta(

184:     function getTokenFromZeta(

209:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L27), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45), [66](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66), [68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99), [136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136), [166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166), [203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203) ):

```solidity
21:     function deposit() external payable;

23:     function withdraw(uint256 wad) external;

25:     function depositTo(address to) external payable;

27:     function withdrawTo(address payable to, uint256 value) external;

45:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {

66:     receive() external payable {}

68:     function getPair(address token0, address token1) internal pure returns (address, address) {

74:     function getZetaFromEth(

99:     function getZetaFromToken(

136:     function getEthFromZeta(

166:     function getTokenFromZeta(

203:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58), [95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124), [162](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162) ):

```solidity
26:     constructor(address zetaToken_, address uniswapV2Router_) {

34:     function getZetaFromEth(

58:     function getZetaFromToken(

95:     function getEthFromZeta(

124:     function getTokenFromZeta(

162:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L21), [42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42), [72](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72), [74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98), [124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124), [158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158), [184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184) ):

```solidity
21:     function withdraw(uint256 wad) external;

42:     constructor(

72:     receive() external payable {}

74:     function getZetaFromEth(

98:     function getZetaFromToken(

124:     function getEthFromZeta(

158:     function getTokenFromZeta(

184:     function hasZetaLiquidity() external view override returns (bool) {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17) ):

```solidity
17:     function getPools(
```

- *Interfaces.sol* ( [8](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8), [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L18), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L24), [26](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26), [28](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30), [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L32), [34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34), [36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36), [38](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L38), [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L52), [54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L54) ):

```solidity
8:     function FUNGIBLE_MODULE_ADDRESS() external view returns (address);

10:     function wZetaContractAddress() external view returns (address);

12:     function uniswapv2FactoryAddress() external view returns (address);

14:     function gasPriceByChainId(uint256 chainID) external view returns (uint256);

16:     function gasCoinZRC20ByChainId(uint256 chainID) external view returns (address);

18:     function gasZetaPoolByChainId(uint256 chainID) external view returns (address);

22:     function totalSupply() external view returns (uint256);

24:     function balanceOf(address account) external view returns (uint256);

26:     function transfer(address recipient, uint256 amount) external returns (bool);

28:     function allowance(address owner, address spender) external view returns (uint256);

30:     function approve(address spender, uint256 amount) external returns (bool);

32:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

34:     function deposit(address to, uint256 amount) external returns (bool);

36:     function withdraw(bytes memory to, uint256 amount) external returns (bool);

38:     function withdrawGasFee() external view returns (address, uint256);

50:     function name() external view returns (string memory);

52:     function symbol() external view returns (string memory);

54:     function decimals() external view returns (uint8);
```

- *SystemContract.sol* ( [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51), [67](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67), [87](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87), [100](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L100), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123), [134](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L145), [156](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L156), [167](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L167) ):

```solidity
51:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {

67:     function depositAndCall(

87:     function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {

100:     function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {

123:     function setGasPrice(uint256 chainID, uint256 price) external {

134:     function setGasCoinZRC20(uint256 chainID, address zrc20) external {

145:     function setGasZetaPool(uint256 chainID, address erc20) external {

156:     function setWZETAContractAddress(address addr) external {

167:     function setConnectorZEVMAddress(address addr) external {
```

- *ZRC20.sol* ( [41](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L41), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L45), [60](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99), [107](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L107), [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L116), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125), [135](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135), [145](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145), [157](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157), [173](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173), [178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L178), [191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L191), [199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L199), [211](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L211), [225](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225), [236](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236), [256](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256), [270](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270), [279](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L279), [288](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L288) ):

```solidity
41:     function _msgSender() internal view virtual returns (address) {

45:     function _msgData() internal view virtual returns (bytes calldata) {

60:     constructor(

83:     function name() public view virtual override returns (string memory) {

91:     function symbol() public view virtual override returns (string memory) {

99:     function decimals() public view virtual override returns (uint8) {

107:     function totalSupply() public view virtual override returns (uint256) {

116:     function balanceOf(address account) public view virtual override returns (uint256) {

125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {

135:     function allowance(address owner, address spender) public view virtual override returns (uint256) {

145:     function approve(address spender, uint256 amount) public virtual override returns (bool) {

157:     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {

173:     function burn(uint256 amount) external returns (bool) {

178:     function _transfer(address sender, address recipient, uint256 amount) internal virtual {

191:     function _mint(address account, uint256 amount) internal virtual {

199:     function _burn(address account, uint256 amount) internal virtual {

211:     function _approve(address owner, address spender, uint256 amount) internal virtual {

225:     function deposit(address to, uint256 amount) external override returns (bool) {

236:     function withdrawGasFee() public view override returns (address, uint256) {

256:     function withdraw(bytes memory to, uint256 amount) external override returns (bool) {

270:     function updateSystemContractAddress(address addr) external onlyFungible {

279:     function updateGasLimit(uint256 gasLimit) external onlyFungible {

288:     function updateProtocolFlatFee(uint256 protocolFlatFee) external onlyFungible {
```

- *ZetaConnectorZEVM.sol* ( [50](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50), [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52), [79](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79), [84](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L84), [92](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114) ):

```solidity
50:     function transferFrom(address src, address dst, uint wad) external returns (bool);

52:     function withdraw(uint wad) external;

79:     constructor(address wzeta_) {

84:     receive() external payable {

92:     function send(ZetaInterfaces.SendInput calldata input) external {

114:     function setWzetaAddress(address wzeta_) external {
```

- *IUniswapV2Router01.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29), [39](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39), [48](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48), [62](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62), [75](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75), [83](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83), [91](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91), [98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98), [106](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106), [114](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114), [121](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121), [123](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L123), [125](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L125), [127](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L127), [129](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L129) ):

```solidity
5:     function factory() external pure returns (address);

7:     function WETH() external pure returns (address);

9:     function addLiquidity(

20:     function addLiquidityETH(

29:     function removeLiquidity(

39:     function removeLiquidityETH(

48:     function removeLiquidityWithPermit(

62:     function removeLiquidityETHWithPermit(

75:     function swapExactTokensForTokens(

83:     function swapTokensForExactTokens(

91:     function swapExactETHForTokens(

98:     function swapTokensForExactETH(

106:     function swapExactTokensForETH(

114:     function swapETHForExactTokens(

121:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);

123:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut);

125:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn);

127:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);

129:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts);
```

- *IUniswapV2Router02.sol* ( [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29), [37](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37), [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44) ):

```solidity
7:     function removeLiquidityETHSupportingFeeOnTransferTokens(

16:     function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(

29:     function swapExactTokensForTokensSupportingFeeOnTransferTokens(

37:     function swapExactETHForTokensSupportingFeeOnTransferTokens(

44:     function swapExactTokensForETHSupportingFeeOnTransferTokens(
```

- *IWZETA.sol* ( [10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L10), [12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L12), [14](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14), [16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16), [18](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18), [20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L20), [22](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L22), [24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24) ):

```solidity
10:     function totalSupply() external view returns (uint);

12:     function balanceOf(address owner) external view returns (uint);

14:     function allowance(address owner, address spender) external view returns (uint);

16:     function approve(address spender, uint wad) external returns (bool);

18:     function transfer(address to, uint wad) external returns (bool);

20:     function transferFrom(address from, address to, uint wad) external returns (bool);

22:     function deposit() external payable;

24:     function withdraw(uint wad) external;
```

- *IZRC20.sol* ( [5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L5), [7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L7), [9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9), [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11), [13](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13), [15](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L15), [17](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L17), [19](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L19), [21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21), [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23), [25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25), [27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L27), [29](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29) ):

```solidity
5:     function totalSupply() external view returns (uint256);

7:     function balanceOf(address account) external view returns (uint256);

9:     function transfer(address recipient, uint256 amount) external returns (bool);

11:     function allowance(address owner, address spender) external view returns (uint256);

13:     function approve(address spender, uint256 amount) external returns (bool);

15:     function decreaseAllowance(address spender, uint256 amount) external returns (bool);

17:     function increaseAllowance(address spender, uint256 amount) external returns (bool);

19:     function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

21:     function deposit(address to, uint256 amount) external returns (bool);

23:     function burn(address account, uint256 amount) external returns (bool);

25:     function withdraw(bytes memory to, uint256 amount) external returns (bool);

27:     function withdrawGasFee() external view returns (address, uint256);

29:     function PROTOCOL_FEE() external view returns (uint256);
```

- *zContract.sol* ( [11](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11) ):

```solidity
11:     function onCrossChainCall(
```

</details>

### [N-97] Missing NatSpec `@dev` from modifier declaration

Some modifiers have an incomplete NatSpec: add a `@dev` notation to describe the modifier to improve the code documentation.

There are 5 instances:

- *ZetaInteractor.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30) ):

```solidity
23:     modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {

30:     modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94) ):

```solidity
94:     modifier nonReentrant() {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59) ):

```solidity
59:     modifier nonReentrant() {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65) ):

```solidity
65:     modifier nonReentrant() {
```

### [N-98] Missing NatSpec `@notice` from modifier declaration

Some modifiers have an incomplete NatSpec: add a `@notice` notation to describe the modifier to improve the code documentation.

<details>
<summary>There are 11 instances (click to show):</summary>

- *ERC20Custody.sol* ( [51](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L51), [61](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L61) ):

```solidity
51:     modifier onlyTSS() {

61:     modifier onlyTSSUpdater() {
```

- *ZetaConnector.base.sol* ( [93](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L93), [101](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L101), [109](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L109) ):

```solidity
93:     modifier onlyPauser() {

101:     modifier onlyTssAddress() {

109:     modifier onlyTssUpdater() {
```

- *ZetaInteractor.sol* ( [23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23), [30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30) ):

```solidity
23:     modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) {

30:     modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L94) ):

```solidity
94:     modifier nonReentrant() {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L59) ):

```solidity
59:     modifier nonReentrant() {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65) ):

```solidity
65:     modifier nonReentrant() {
```

- *ZRC20.sol* ( [52](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L52) ):

```solidity
52:     modifier onlyFungible() {
```

</details>

### [N-99] Large or complicated code bases should implement invariant tests

This includes: large code bases, or code with lots of inline-assembly, complicated math, or complicated interactions between multiple contracts.
Invariant fuzzers such as Echidna require the test writer to come up with invariants which should not be violated under any circumstances, and the fuzzer tests various inputs and function calls to ensure that the invariants always hold.
Even code with 100% code coverage can still have bugs due to the order of the operations a user performs, and invariant fuzzers may help significantly.

There is 1 instance:

- Global finding

### [N-100] Top-level declarations should be separated by at least two lines

-

<details>
<summary>There are 95 instances (click to show):</summary>

- *ERC20Custody.sol* ( [3-5](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L3-L5) ):

```solidity
3: pragma solidity 0.8.7;
4: 
5: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

- *Zeta.eth.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L2-L4) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
```

- *ZetaConnector.base.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L2-L4) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

- *ZetaConnector.eth.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L2-L4), [21-23](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L21-L23) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

21:     ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
22: 
23:     function getLockedAmount() external view returns (uint256) {
```

- *ZetaConnector.non-eth.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L2-L4), [25-27](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L25-L27), [29-31](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L29-L31) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

25:     ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
26: 
27:     function getLockedAmount() external view returns (uint256) {

29:     }
30: 
31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
```

- *ZetaInterfaces.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2-L4), [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L2-L4), [47-49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L47-L49), [54-56](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L54-L56), [106-108](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L106-L108) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: interface ZetaInterfaces {

2: pragma solidity 0.8.7;
3: 
4: interface ZetaInterfaces {

47: }
48: 
49: interface ZetaConnector {

54: }
55: 
56: interface ZetaReceiver {

106: }
107: 
108: interface ZetaCommonErrors {
```

- *ZetaNonEthInterface.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2-L4) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

- *ImmutableCreate2Factory.sol* ( [200-202](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L200-L202) ):

```solidity
200:     }
201: 
202:     function safeCreate2AndTransfer(
```

- *ZetaInteractor.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L2-L4), [7-9](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L7-L9), [28-30](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L28-L30), [41-43](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L41-L43), [52-54](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L52-L54) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/access/Ownable2Step.sol";

7: import "../interfaces/ZetaInteractorErrors.sol";
8: 
9: abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {

28:     }
29: 
30:     modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) {

41:     }
42: 
43:     function _isValidCaller() private view {

52:     }
53: 
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```

- *ZetaTokenConsumerPancakeV3.strategy.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L2-L4), [10-12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L10-L12), [18-20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L18-L20), [22-24](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L22-L24), [92-94](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L92-L94), [101-103](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101-L103), [124-126](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L124-L126), [149-151](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L149-L151), [182-184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L182-L184), [207-209](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L207-L209) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

10: import "../interfaces/ZetaInterfaces.sol";
11: 
12: interface ZetaTokenConsumerUniV3Errors {

18: }
19: 
20: interface WETH9 {

22: }
23: 
24: interface ISwapRouterPancake is IUniswapV3SwapCallback {

92:     }
93: 
94:     modifier nonReentrant() {

101:     receive() external payable {}
102: 
103:     function getZetaFromEth(

124:     }
125: 
126:     function getZetaFromToken(

149:     }
150: 
151:     function getEthFromZeta(

182:     }
183: 
184:     function getTokenFromZeta(

207:     }
208: 
209:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerTrident.strategy.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L2-L4), [10-12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L10-L12), [18-20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L18-L20), [57-59](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L57-L59), [66-68](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66-L68), [72-74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L72-L74), [97-99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L97-L99), [134-136](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L134-L136), [164-166](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L164-L166), [201-203](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L201-L203) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

10: import "./interfaces/TridentIPoolRouter.sol";
11: 
12: interface ZetaTokenConsumerTridentErrors {

18: }
19: 
20: interface WETH9 {

57:     }
58: 
59:     modifier nonReentrant() {

66:     receive() external payable {}
67: 
68:     function getPair(address token0, address token1) internal pure returns (address, address) {

72:     }
73: 
74:     function getZetaFromEth(

97:     }
98: 
99:     function getZetaFromToken(

134:     }
135: 
136:     function getEthFromZeta(

164:     }
165: 
166:     function getTokenFromZeta(

201:     }
202: 
203:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV2.strategy.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L2-L4), [8-10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L8-L10), [32-34](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L32-L34), [56-58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L56-L58), [93-95](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L93-L95), [122-124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L122-L124), [160-162](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L160-L162) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

8: import "../interfaces/ZetaInterfaces.sol";
9: 
10: interface ZetaTokenConsumerUniV2Errors {

32:     }
33: 
34:     function getZetaFromEth(

56:     }
57: 
58:     function getZetaFromToken(

93:     }
94: 
95:     function getEthFromZeta(

122:     }
123: 
124:     function getTokenFromZeta(

160:     }
161: 
162:     function hasZetaLiquidity() external view override returns (bool) {
```

- *ZetaTokenConsumerUniV3.strategy.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L2-L4), [10-12](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L10-L12), [18-20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L18-L20), [63-65](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L63-L65), [72-74](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72-L74), [96-98](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L96-L98), [122-124](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L122-L124), [156-158](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L156-L158), [182-184](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L182-L184) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

10: import "../interfaces/ZetaInterfaces.sol";
11: 
12: interface ZetaTokenConsumerUniV3Errors {

18: }
19: 
20: interface WETH9 {

63:     }
64: 
65:     modifier nonReentrant() {

72:     receive() external payable {}
73: 
74:     function getZetaFromEth(

96:     }
97: 
98:     function getZetaFromToken(

122:     }
123: 
124:     function getEthFromZeta(

156:     }
157: 
158:     function getTokenFromZeta(

182:     }
183: 
184:     function hasZetaLiquidity() external view override returns (bool) {
```

- *TridentConcentratedLiquidityPoolFactory.sol* ( [14-16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L14-L16), [14-16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L14-L16) ):

```solidity
14: pragma solidity >=0.8.0;
15: 
16: interface ConcentratedLiquidityPoolFactory {

14: pragma solidity >=0.8.0;
15: 
16: interface ConcentratedLiquidityPoolFactory {
```

- *TridentIPoolRouter.sol* ( [14-16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14-L16), [14-16](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L14-L16) ):

```solidity
14: pragma solidity >=0.8.0;
15: 
16: interface IPoolRouter {

14: pragma solidity >=0.8.0;
15: 
16: interface IPoolRouter {
```

- *Interfaces.sol* ( [19-21](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L19-L21), [47-49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L47-L49) ):

```solidity
19: }
20: 
21: interface IZRC20 {

47: }
48: 
49: interface IZRC20Metadata is IZRC20 {
```

- *SystemContract.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L2-L4) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "./interfaces/zContract.sol";
```

- *Uniswap.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L2-L4), [5-7](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L5-L7) ):

```solidity
2: pragma solidity 0.5.16;
3: 
4: import "@uniswap/v2-core/contracts/UniswapV2Pair.sol";

5: import "@uniswap/v2-core/contracts/UniswapV2Factory.sol";
6: 
7: contract UniswapImports {}
```

- *UniswapPeriphery.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L2-L4), [4-6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L4-L6) ):

```solidity
2: pragma solidity 0.6.6;
3: 
4: import "@uniswap/v2-periphery/contracts/UniswapV2Router02.sol";

4: import "@uniswap/v2-periphery/contracts/UniswapV2Router02.sol";
5: 
6: contract UniswapImports {}
```

- *WZETA.sol* ( [1-3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1-L3), [1-3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1-L3), [18-20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L18-L20), [23-25](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L23-L25), [30-32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L30-L32), [34-36](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L34-L36), [40-42](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L40-L42), [44-46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol#L44-L46) ):

```solidity
1: pragma solidity ^0.4.18;
2: 
3: contract WETH9 {

1: pragma solidity ^0.4.18;
2: 
3: contract WETH9 {

18:     }
19: 
20:     function deposit() public payable {

23:     }
24: 
25:     function withdraw(uint wad) public {

30:     }
31: 
32:     function totalSupply() public view returns (uint) {

34:     }
35: 
36:     function approve(address guy, uint wad) public returns (bool) {

40:     }
41: 
42:     function transfer(address dst, uint wad) public returns (bool) {

44:     }
45: 
46:     function transferFrom(address src, address dst, uint wad) public returns (bool) {
```

- *ZRC20.sol* ( [2-3](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L2-L3), [18-20](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L18-L20), [43-45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L43-L45), [176-178](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L176-L178), [189-191](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L189-L191), [197-199](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L197-L199), [209-211](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L209-L211) ):

```solidity
2: pragma solidity 0.8.7;
3: import "./Interfaces.sol";

18: }
19: 
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {

43:     }
44: 
45:     function _msgData() internal view virtual returns (bytes calldata) {

176:     }
177: 
178:     function _transfer(address sender, address recipient, uint256 amount) internal virtual {

189:     }
190: 
191:     function _mint(address account, uint256 amount) internal virtual {

197:     }
198: 
199:     function _burn(address account, uint256 amount) internal virtual {

209:     }
210: 
211:     function _approve(address owner, address spender, uint256 amount) internal virtual {
```

- *ZetaConnectorZEVM.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L2-L4), [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L2-L4), [47-49](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L47-L49), [53-55](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L53-L55) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: interface ZetaInterfaces {

2: pragma solidity 0.8.7;
3: 
4: interface ZetaInterfaces {

47: }
48: 
49: interface WZETA {

53: }
54: 
55: contract ZetaConnectorZEVM is ZetaInterfaces {
```

- *IUniswapV2Router01.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L2-L4), [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L2-L4) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: interface IUniswapV2Router01 {

2: pragma solidity 0.8.7;
3: 
4: interface IUniswapV2Router01 {
```

- *IUniswapV2Router02.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L2-L4), [4-6](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L4-L6) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: import "./IUniswapV2Router01.sol";

4: import "./IUniswapV2Router01.sol";
5: 
6: interface IUniswapV2Router02 is IUniswapV2Router01 {
```

- *IWZETA.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L2-L4), [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L2-L4) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: interface IWETH9 {

2: pragma solidity 0.8.7;
3: 
4: interface IWETH9 {
```

- *IZRC20.sol* ( [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L2-L4), [2-4](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L2-L4) ):

```solidity
2: pragma solidity 0.8.7;
3: 
4: interface IZRC20 {

2: pragma solidity 0.8.7;
3: 
4: interface IZRC20 {
```

- *zContract.sol* ( [8-10](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L8-L10) ):

```solidity
8: }
9: 
10: interface zContract {
```

</details>

### [N-101] Consider adding formal verification proofs

Formal verification is the act of proving or disproving the correctness of intended algorithms underlying a system with respect to a certain formal specification/property/invariant, using formal methods of mathematics.

Some tools that are currently available to perform these tests on smart contracts are [SMTChecker](https://docs.soliditylang.org/en/latest/smtchecker.html) and [Certora Prover](https://www.certora.com/).

<details>
<summary>There are 31 instances (click to show):</summary>

- [*ERC20Custody.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol)

- [*Zeta.eth.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.eth.sol)

- [*Zeta.non-eth.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol)

- [*ZetaConnector.base.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol)

- [*ZetaConnector.eth.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol)

- [*ZetaConnector.non-eth.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol)

- [*ConnectorErrors.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol)

- [*ZetaErrors.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol)

- [*ZetaInteractorErrors.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol)

- [*ZetaInterfaces.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol)

- [*ZetaNonEthInterface.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol)

- [*ImmutableCreate2Factory.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol)

- [*ZetaInteractor.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol)

- [*ZetaTokenConsumerPancakeV3.strategy.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol)

- [*ZetaTokenConsumerTrident.strategy.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol)

- [*ZetaTokenConsumerUniV2.strategy.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol)

- [*ZetaTokenConsumerUniV3.strategy.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol)

- [*TridentConcentratedLiquidityPoolFactory.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol)

- [*TridentIPoolRouter.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol)

- [*Interfaces.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol)

- [*SystemContract.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol)

- [*Uniswap.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Uniswap.sol)

- [*UniswapPeriphery.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol)

- [*WZETA.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/WZETA.sol)

- [*ZRC20.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol)

- [*ZetaConnectorZEVM.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol)

- [*IUniswapV2Router01.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol)

- [*IUniswapV2Router02.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol)

- [*IWZETA.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol)

- [*IZRC20.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol)

- [*zContract.sol*](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol)

</details>

### [N-102] Prevent re-setting a state variable with the same value

This especially problematic when the setter also emits the same value, which may be confusing to offline parsers.

<details>
<summary>There are 16 instances (click to show):</summary>

- *ERC20Custody.sol* ( [84](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L84), [99](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L99), [111](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L111) ):

```solidity
84:         TSSAddress = TSSAddress_;

99:         zetaFee = zetaFee_;

111:         TSSAddressUpdater = TSSAddress;
```

- *Zeta.non-eth.sol* ( [44](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L44), [45](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L45), [58](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L58) ):

```solidity
44:         tssAddress = tssAddress_;

45:         connectorAddress = connectorAddress_;

58:         tssAddressUpdater = tssAddress;
```

- *ZetaConnector.base.sol* ( [120](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L120), [132](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L132), [143](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L143) ):

```solidity
120:         pauserAddress = pauserAddress_;

132:         tssAddress = tssAddress_;

143:         tssAddressUpdater = tssAddress;
```

- *ZetaConnector.non-eth.sol* ( [32](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L32) ):

```solidity
32:         maxSupply = maxSupply_;
```

- *SystemContract.sol* ( [159](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L159), [170](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L170) ):

```solidity
159:         wZetaContractAddress = addr;

170:         zetaConnectorZEVMAddress = addr;
```

- *ZRC20.sol* ( [271](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L271), [280](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L280), [289](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L289) ):

```solidity
271:         SYSTEM_CONTRACT_ADDRESS = addr;

280:         GAS_LIMIT = gasLimit;

289:         PROTOCOL_FLAT_FEE = protocolFlatFee;
```

- *ZetaConnectorZEVM.sol* ( [116](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L116) ):

```solidity
116:         wzeta = wzeta_;
```

</details>

