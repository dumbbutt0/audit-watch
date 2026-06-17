|ID|Title|Category|Severity|
|-|:-|:-:|:-:|
| [L-1] | `abi.encodePacked()` should not be used with dynamic types when passing the result to a hash function such as `keccak256()` | Data Flow | Low |
| [L-2] | Insufficient Gas Griefing | Control Flow | Low |
| [L-3] | MISSING ZERO ADDRESS VALIDATION | Volatile Code | Low |
| [L-4] | Missing Contract-Existence Checks Before Low-Level Calls | Control Flow | Low |
| [L-5] | Owner can renounce while system is paused | Control Flow | Low |
| [L-6] | State variables not capped at reasonable values | Coding Style | Low |
| [L-7] | Functions calling contracts with transfer hooks are missing reentrancy guards | Control Flow | Low |
| [L-8] | Use `safeTransferOwnership` instead of `transferOwnership` function | Control Flow | Low |
| [L-9] | MISSING ZERO ADDRESS VALIDATION in constructor | Volatile Code | Low |
| [NC-1] | Assembly code blocks should be thoroughly commented | Control Flow | Informational |
| [NC-2] | Burn functions should be protected with a modifier | Control Flow | Informational |
| [NC-3] | Inconsistent spacing in comments | Coding Style | Informational |
| [NC-4] | Constants in comparisons should appear on the left side | Coding Style | Informational |
| [NC-5] | Use a single file for all system-wide constants | Coding Style | Informational |
| [NC-6] | Visibility should be set explicitly rather than defaulting to `internal` | Coding Style | Informational |
| [NC-7] | Contracts and libraries should be named using the `CapWords` style | Coding Style | Informational |
| [NC-8] | Control structures do not follow the Solidity Style Guide | Coding Style | Informational |
| [NC-9] | Constructor visibility is ignored | Coding Style | Informational |
| [NC-10] | Use Custom Errors | Coding Style | Informational |
| [NC-11] | Use delete instead of assigning values to false | Coding Style | Informational |
| [NC-12] | Duplicated require statements should be refactored | Coding Style | Informational |
| [NC-13] | Event is missing msg.sender parameter | Coding Style | Informational |
| [NC-14] | Emitting storage values instead of the memory one. | Coding Style | Informational |
| [NC-15] | Empty Event | Coding Style | Informational |
| [NC-16] | Custom errors has no error details | Coding Style | Informational |
| [NC-17] | Missing event for critical changes | Coding Style | Informational |
| [NC-18] | Event is not properly indexed | Coding Style | Informational |
| [NC-19] | Events that mark critical parameter changes should contain both the old and the new value | Coding Style | Informational |
| [NC-20] | Events may be emitted out of order due to reentranc | Logical Issue | Informational |
| [NC-21] | Contract functions should use an interface | Coding Style | Informational |
| [NC-22] | Consider moving msg.sender checks to modifiers | Coding Style | Informational |
| [NC-23] | Functions should use `mixedCase` | Coding Style | Informational |
| [NC-24] | Imports could be organized more systematically | Coding Style | Informational |
| [NC-25] | internal functions only called once can be inlined | Coding Style | Informational |
| [NC-26] | Declare interfaces on separate files | Coding Style | Informational |
| [NC-27] | Interfaces should have an I prefix in the contract name | Coding Style | Informational |
| [NC-28] | internal functions not called by the contract should be removed | Coding Style | Informational |
| [NC-29] | Multiple mappings with same keys can be combined into a single struct mapping for readability | Coding Style | Informational |
| [NC-30] | Contract declarations should have NatSpec `@author` annotations | Coding Style | Informational |
| [NC-31] | Contract declarations should have NatSpec `@dev` annotations | Coding Style | Informational |
| [NC-32] | Missing events in sensitive functions | Coding Style | Informational |
| [NC-33] | File is miss SPDX-License-Identifier | Coding Style | Informational |
| [NC-34] | Contract declarations should have NatSpec `@title` annotations | Coding Style | Informational |
| [NC-35] | Named imports of parent contracts are missing | Coding Style | Informational |
| [NC-36] |  Names of `private`/`internal` state variables should be prefixed with an underscore | Coding Style | Informational |
| [NC-37] |  Names of `private`/`internal` function should be prefixed with an underscore | Coding Style | Informational |
| [NC-38] | Empty function body | Coding Style | Informational |
| [NC-39] | Non-library/interface files should use fixed compiler versions, not floating ones | Coding Style | Informational |
| [NC-40] | Contract declarations should have NatSpec `@notice` annotations | Coding Style | Informational |
| [NC-41] | Incomplete NatSpec @param from function declaration | Coding Style | Informational |
| [NC-42] | Incomplete NatSpec @return from function declaration | Coding Style | Informational |
| [NC-43] | Use of override is unnecessary | Coding Style | Informational |
| [NC-44] | Missing underscore prefix for non-external functions | Coding Style | Informational |
| [NC-45] | Missing Error Messages | Coding Style | Informational |
| [NC-46] | Implement Value Comparison Checks in Setter Functions to Prevent Redundant State Updates | Coding Style | Informational |
| [NC-47] | Order of function | Coding Style | Informational |
| [NC-48] | Order of layout | Coding Style | Informational |
| [NC-49] | Use a struct to encapsulate multiple function parameters | Coding Style | Informational |
| [NC-50] | Take advantage of Custom Error's return value property | Coding Style | Informational |
| [NC-51] | Top level pragma declarations should be separated by two blank lines | Coding Style | Informational |
| [NC-52] | Unused Function Parameter | Coding Style | Informational |
| [NC-53] | Unused named return | Coding Style | Informational |
| [NC-54] | Enum values should be used in place of constant array indexes | Coding Style | Informational |
| [NC-55] | Variable Names Not in `mixedCase` | Coding Style | Informational |
| [NC-56] | Avoid the use of sensitive terms | Coding Style | Informational |
| [NC-57] | MISSING Non-Empty Check for Bytes in Function Parameters | Volatile Code | Informational |

## M-1 | Centralization Risk for trusted owners

#### **Description** :-

Contracts have owners with privileged rights to perform admin tasks and need to be trusted to not perform malicious updates or drain funds.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
3:interface Ownable {
```

```solidity
207:        Ownable(deploymentAddress).transferOwnership(msg.sender);
```
[[ImmutableCreate2Factory.sol#L3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L3)] 
[[ImmutableCreate2Factory.sol#L207](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L207)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
9:abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```

```solidity
54:    function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
```
[[ZetaInteractor.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9)] 
[[ZetaInteractor.sol#L54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54)] 
## L-1 | `abi.encodePacked()` should not be used with dynamic types when passing the result to a hash function such as `keccak256()`

#### **Description** :-

Use `abi.encode()` instead which will pad items to 32 bytes, which will [prevent hash collisions](https://docs.soliditylang.org/en/v0.8.13/abi-spec.html#non-standard-packed-mode) (e.g. `abi.encodePacked(0x123,0x456)` => `0x123456` => `abi.encodePacked(0x1,0x23456)`, but `abi.encode(0x123,0x456)` => `0x0...1230...456`). Unless there is a compelling reason, `abi.encode` should be preferred. If there is only one argument to `abi.encodePacked()` it can often be cast to `bytes()` or `bytes32()` [instead](https://ethereum.stackexchange.com/questions/30912/how-to-compare-strings-in-solidity#answer-82739).
If all arguments are strings and or bytes, `bytes.concat()` should be used instead


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
42:                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
```

```solidity
121:                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
```
[[ImmutableCreate2Factory.sol#L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L42)] 
[[ImmutableCreate2Factory.sol#L121](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L121)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
109:                            keccak256(abi.encodePacked(token0, token1)),
```
[[SystemContract.sol#L109](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L109)] 
## L-2 | Insufficient Gas Griefing

#### **Description** :-

External calls in your code don't specify a gas limit, which can lead to scenarios where the recipient consumes all transaction's gas causing it to revert. Consider using addr.call{gas: <amount>}("") to set a gas limit and prevent potential reversion due to gas consumption.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
151:    function getEthFromZeta(
152:        address destinationAddress,
153:        uint256 minAmountOut,
154:        uint256 zetaTokenAmount
155:    ) external override returns (uint256) {
156:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
157:        if (zetaTokenAmount == 0) revert InputCantBeZero();
158:
159:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
160:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
161:
162:        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
163:            tokenIn: zetaToken,
164:            tokenOut: WETH9Address,
165:            fee: zetaPoolFee,
166:            recipient: address(this),
167:            amountIn: zetaTokenAmount,
168:            amountOutMinimum: minAmountOut,
169:            sqrtPriceLimitX96: 0
170:        });
171:
172:        uint256 amountOut = pancakeV3Router.exactInputSingle(params);
173:
174:        WETH9(WETH9Address).withdraw(amountOut);
175:
176:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
177:
178:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
179:        if (!sent) revert ErrorSendingETH();
180:
181:        return amountOut;
182:    }
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
124:    function getEthFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        uint256 zetaTokenAmount
128:    ) external override returns (uint256) {
129:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
130:        if (zetaTokenAmount == 0) revert InputCantBeZero();
131:
132:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
133:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
134:
135:        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
136:            deadline: block.timestamp + MAX_DEADLINE,
137:            tokenIn: zetaToken,
138:            tokenOut: WETH9Address,
139:            fee: zetaPoolFee,
140:            recipient: address(this),
141:            amountIn: zetaTokenAmount,
142:            amountOutMinimum: minAmountOut,
143:            sqrtPriceLimitX96: 0
144:        });
145:
146:        uint256 amountOut = uniswapV3Router.exactInputSingle(params);
147:
148:        WETH9(WETH9Address).withdraw(amountOut);
149:
150:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151:
152:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
153:        if (!sent) revert ErrorSendingETH();
154:
155:        return amountOut;
156:    }
```
[[ZetaTokenConsumerUniV3.strategy.sol#L124-L156](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L156)] 
## L-3 | MISSING ZERO ADDRESS VALIDATION

#### **Description** :-

The given input is missing the check for the non-zero address.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
271:        SYSTEM_CONTRACT_ADDRESS = addr;
```
[[ZRC20.sol#L271](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L271)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
86:        zetaToken = zetaToken_;
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L86](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L86)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
53:        zetaToken = zetaToken_;
```
[[ZetaTokenConsumerTrident.strategy.sol#L53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L53)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
57:        zetaToken = zetaToken_;
```
[[ZetaTokenConsumerUniV3.strategy.sol#L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L57)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
69:        TSSAddress = TSSAddress_;
```
[[ERC20Custody.sol#L69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L69)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
29:        zetaToken = zetaToken_;
```
[[ZetaTokenConsumerUniV2.strategy.sol#L29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L29)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
84:        zetaToken = zetaToken_;
```
[[ZetaConnector.base.sol#L84](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L84)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
53:        wZetaContractAddress = wzeta_;
```
[[SystemContract.sol#L53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L53)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
80:        wzeta = wzeta_;
```
[[ZetaConnectorZEVM.sol#L80](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L80)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
36:        tssAddress = tssAddress_;
```
[[Zeta.non-eth.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L36)] 
## L-4 | Missing Contract-Existence Checks Before Low-Level Calls

#### **Description** :-

Low-level calls return success if there is no code present at the specified address.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
151:    function getEthFromZeta(
152:        address destinationAddress,
153:        uint256 minAmountOut,
154:        uint256 zetaTokenAmount
155:    ) external override returns (uint256) {
156:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
157:        if (zetaTokenAmount == 0) revert InputCantBeZero();
158:
159:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
160:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
161:
162:        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
163:            tokenIn: zetaToken,
164:            tokenOut: WETH9Address,
165:            fee: zetaPoolFee,
166:            recipient: address(this),
167:            amountIn: zetaTokenAmount,
168:            amountOutMinimum: minAmountOut,
169:            sqrtPriceLimitX96: 0
170:        });
171:
172:        uint256 amountOut = pancakeV3Router.exactInputSingle(params);
173:
174:        WETH9(WETH9Address).withdraw(amountOut);
175:
176:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
177:
178:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
179:        if (!sent) revert ErrorSendingETH();
180:
181:        return amountOut;
182:    }
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
124:    function getEthFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        uint256 zetaTokenAmount
128:    ) external override returns (uint256) {
129:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
130:        if (zetaTokenAmount == 0) revert InputCantBeZero();
131:
132:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
133:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
134:
135:        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
136:            deadline: block.timestamp + MAX_DEADLINE,
137:            tokenIn: zetaToken,
138:            tokenOut: WETH9Address,
139:            fee: zetaPoolFee,
140:            recipient: address(this),
141:            amountIn: zetaTokenAmount,
142:            amountOutMinimum: minAmountOut,
143:            sqrtPriceLimitX96: 0
144:        });
145:
146:        uint256 amountOut = uniswapV3Router.exactInputSingle(params);
147:
148:        WETH9(WETH9Address).withdraw(amountOut);
149:
150:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151:
152:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
153:        if (!sent) revert ErrorSendingETH();
154:
155:        return amountOut;
156:    }
```
[[ZetaTokenConsumerUniV3.strategy.sol#L124-L156](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L156)] 
## L-5 | Owner can renounce while system is paused

#### **Description** :-

The contract owner or single user with a role is not prevented from renouncing the role/ownership while the contract is paused, which would cause any user assets stored in the protocol, to be locked indefinitely


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
118:    function pause() external onlyTSS {
119:        if (paused) {
120:            revert IsPaused();
121:        }
122:        if (TSSAddress == address(0)) {
123:            revert ZeroAddress();
124:        }
125:        paused = true;
126:        emit Paused(msg.sender);
127:    }
```
[[ERC20Custody.sol#L118-L127](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L118-L127)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
151:    function pause() external onlyPauser {
152:        _pause();
153:    }
```
[[ZetaConnector.base.sol#L151-L153](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L151-L153)] 
## L-6 | State variables not capped at reasonable values

#### **Description** :-

Consider adding appropriate minimum/maximum value checks to ensure that the following state variables can never be used to excessively harm users, including via griefing.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
125:        gasPriceByChainId[chainID] = price;
```

```solidity
136:        gasCoinZRC20ByChainId[chainID] = zrc20;
```

```solidity
148:        gasZetaPoolByChainId[chainID] = pool;
```

```solidity
159:        wZetaContractAddress = addr;
```

```solidity
170:        zetaConnectorZEVMAddress = addr;
```
[[SystemContract.sol#L125](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L125)] 
[[SystemContract.sol#L136](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L136)] 
[[SystemContract.sol#L148](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L148)] 
[[SystemContract.sol#L159](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L159)] 
[[SystemContract.sol#L170](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L170)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
116:        wzeta = wzeta_;
```
[[ZetaConnectorZEVM.sol#L116](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L116)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
32:        maxSupply = maxSupply_;
```
[[ZetaConnector.non-eth.sol#L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L32)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
55:        interactorsByChainId[destinationChainId] = contractAddress;
```
[[ZetaInteractor.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L55)] 
## L-7 | Functions calling contracts with transfer hooks are missing reentrancy guards

#### **Description** :-

Even if the function follows the best practice of check-effects-interaction, not using a reentrancy guard when there may be transfer hooks will open the users of this protocol up to read-only reentrancies with no way to protect against it, except by block-listing the whole protocol.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
135:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

```solidity
159:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

```solidity
193:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L135)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L159](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L159)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L193)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
108:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

```solidity
144:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

```solidity
175:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```
[[ZetaTokenConsumerTrident.strategy.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L108)] 
[[ZetaTokenConsumerTrident.strategy.sol#L144](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L144)] 
[[ZetaTokenConsumerTrident.strategy.sol#L175](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L175)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
107:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

```solidity
132:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

```solidity
167:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```
[[ZetaTokenConsumerUniV3.strategy.sol#L107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L107)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L132)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L167](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L167)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
181:        asset.safeTransferFrom(msg.sender, address(this), amount);
```

```solidity
197:        IERC20(asset).safeTransfer(recipient, amount);
```
[[ERC20Custody.sol#L181](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L181)] 
[[ERC20Custody.sol#L197](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L197)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
67:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
```

```solidity
103:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```

```solidity
133:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
```
[[ZetaTokenConsumerUniV2.strategy.sol#L67](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L67)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L103](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L103)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L133](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L133)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
28:        msg.sender.transfer(wad);
```
[[WZETA.sol#L28](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L28)] 
## L-8 | Use `safeTransferOwnership` instead of `transferOwnership` function

#### **Description** :-

`transferOwnership` function is used to change Ownership from Ownable.sol. Use a 2 structure `transferOwnership` which is safer. `safeTransferOwnership`, use it is more secure due to 2-stage ownership transfer.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
4:    function transferOwnership(address newOwner) external;
```

```solidity
207:        Ownable(deploymentAddress).transferOwnership(msg.sender);
```
[[ImmutableCreate2Factory.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L4)] 
[[ImmutableCreate2Factory.sol#L207](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L207)] 
## L-9 | MISSING ZERO ADDRESS VALIDATION in constructor

#### **Description** :-

 Missing checks for zero-addresses may lead to infunctional protocol, if the variable addresses are updated incorrectly


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
71:    constructor(
72:        address zetaToken_,
73:        address pancakeV3Router_,
74:        address uniswapV3Factory_,
75:        address WETH9Address_,
76:        uint24 zetaPoolFee_,
77:        uint24 tokenPoolFee_
78:    ) {
79:        if (
80:            zetaToken_ == address(0) ||
81:            pancakeV3Router_ == address(0) ||
82:            uniswapV3Factory_ == address(0) ||
83:            WETH9Address_ == address(0)
84:        ) revert ZetaCommonErrors.InvalidAddress();
85:
86:        zetaToken = zetaToken_;
87:        pancakeV3Router = ISwapRouterPancake(pancakeV3Router_);
88:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
89:        WETH9Address = WETH9Address_;
90:        zetaPoolFee = zetaPoolFee_;
91:        tokenPoolFee = tokenPoolFee_;
92:    }
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
45:    constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
46:        if (
47:            zetaToken_ == address(0) ||
48:            uniswapV3Router_ == address(0) ||
49:            WETH9Address_ == address(0) ||
50:            poolFactory_ == address(0)
51:        ) revert ZetaCommonErrors.InvalidAddress();
52:
53:        zetaToken = zetaToken_;
54:        tridentRouter = IPoolRouter(uniswapV3Router_);
55:        poolFactory = ConcentratedLiquidityPoolFactory(poolFactory_);
56:        WETH9Address = WETH9Address_;
57:    }
```
[[ZetaTokenConsumerTrident.strategy.sol#L45-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L57)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
42:    constructor(
43:        address zetaToken_,
44:        address uniswapV3Router_,
45:        address uniswapV3Factory_,
46:        address WETH9Address_,
47:        uint24 zetaPoolFee_,
48:        uint24 tokenPoolFee_
49:    ) {
50:        if (
51:            zetaToken_ == address(0) ||
52:            uniswapV3Router_ == address(0) ||
53:            uniswapV3Factory_ == address(0) ||
54:            WETH9Address_ == address(0)
55:        ) revert ZetaCommonErrors.InvalidAddress();
56:
57:        zetaToken = zetaToken_;
58:        uniswapV3Router = ISwapRouter(uniswapV3Router_);
59:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
60:        WETH9Address = WETH9Address_;
61:        zetaPoolFee = zetaPoolFee_;
62:        tokenPoolFee = tokenPoolFee_;
63:    }
```
[[ZetaTokenConsumerUniV3.strategy.sol#L42-L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L63)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
68:    constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
69:        TSSAddress = TSSAddress_;
70:        TSSAddressUpdater = TSSAddressUpdater_;
71:        zetaFee = zetaFee_;
72:        zeta = zeta_;
73:        zetaMaxFee = zetaMaxFee_;
74:    }
```
[[ERC20Custody.sol#L68-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
26:    constructor(address zetaToken_, address uniswapV2Router_) {
27:        if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
28:
29:        zetaToken = zetaToken_;
30:        uniswapV2Router = IUniswapV2Router02(uniswapV2Router_);
31:        wETH = IUniswapV2Router02(uniswapV2Router_).WETH();
32:    }
```
[[ZetaTokenConsumerUniV2.strategy.sol#L26-L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26-L32)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
74:    constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
75:        if (
76:            zetaToken_ == address(0) ||
77:            tssAddress_ == address(0) ||
78:            tssAddressUpdater_ == address(0) ||
79:            pauserAddress_ == address(0)
80:        ) {
81:            revert ZetaCommonErrors.InvalidAddress();
82:        }
83:
84:        zetaToken = zetaToken_;
85:        tssAddress = tssAddress_;
86:        tssAddressUpdater = tssAddressUpdater_;
87:        pauserAddress = pauserAddress_;
88:    }
```
[[ZetaConnector.base.sol#L74-L88](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74-L88)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
51:    constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
52:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
53:        wZetaContractAddress = wzeta_;
54:        uniswapv2FactoryAddress = uniswapv2Factory_;
55:        uniswapv2Router02Address = uniswapv2Router02_;
56:        emit SystemContractDeployed();
57:    }
```
[[SystemContract.sol#L51-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51-L57)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
79:    constructor(address wzeta_) {
80:        wzeta = wzeta_;
81:    }
```
[[ZetaConnectorZEVM.sol#L79-L81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L81)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
20:    constructor(
21:        address zetaTokenAddress_,
22:        address tssAddress_,
23:        address tssAddressUpdater_,
24:        address pauserAddress_
25:    ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```
[[ZetaConnector.non-eth.sol#L20-L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
16:    constructor(
17:        address zetaToken_,
18:        address tssAddress_,
19:        address tssAddressUpdater_,
20:        address pauserAddress_
21:    ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```
[[ZetaConnector.eth.sol#L16-L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
33:    constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {
34:        if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();
35:
36:        tssAddress = tssAddress_;
37:        tssAddressUpdater = tssAddressUpdater_;
38:    }
```
[[Zeta.non-eth.sol#L33-L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L38)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
10:    constructor(address creator, uint256 initialSupply) {
11:        _mint(creator, initialSupply * (10 ** uint256(decimals())));
12:    }
```
[[Zeta.eth.sol#L10-L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L12)] 
## NC-1 | Assembly code blocks should be thoroughly commented

#### **Description** :-

In Solidity, assembly blocks are often harder to read and understand due to their low-level nature. Detailed comments can make the code's purpose and functionality clear, aiding in maintenance, debugging, and reviews. Moreover, comments can be crucial for auditors and other developers to understand the contract's security implications, reducing the risk of oversights and vulnerabilities.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
53:        assembly {
54:            // solhint-disable-line
55:            let encoded_data := add(0x20, initCode) // load initialization code.
56:            let encoded_size := mload(initCode) // load the init code's length.
57:            deploymentAddress := create2(
58:                // call CREATE2 with 4 arguments.
59:                callvalue, // forward any attached value.
60:                encoded_data, // pass in initialization code.
61:                encoded_size, // pass in init code's length.
62:                salt // pass in the salt value.
63:            )
64:        }
```
[[ImmutableCreate2Factory.sol#L53-L64](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L53-L64)] 
## NC-2 | Burn functions should be protected with a modifier

#### **Description** :-

Burn function lake a protected modifier Consider adding a modifier


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
173:    function burn(uint256 amount) external returns (bool) {
174:        _burn(msg.sender, amount);
175:        return true;
176:    }
```
[[ZRC20.sol#L173-L176](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173-L176)] 
## NC-3 | Inconsistent spacing in comments

#### **Description** :-

Some lines use `// x` and some use `//x`. The instances below point out the usages that don't follow the majority, within each file


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
9:        /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id
```
[[ZetaConnectorZEVM.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
9:        /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id
```
[[ZetaInterfaces.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Uniswap.sol
```


```solidity
1://SPDX-License-Identifier: MIT
```
[[Uniswap.sol#L1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L1)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol
```


```solidity
1://SPDX-License-Identifier: MIT
```
[[UniswapPeriphery.sol#L1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L1)] 
## NC-4 | Constants in comparisons should appear on the left side

#### **Description** :-

This is useful to avoid doing some [typo bugs](https://www.moserware.com/2008/01/constants-on-left-are-better-but-this.html).


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
242:        if (gasPrice == 0) {
```
[[ZRC20.sol#L242](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L242)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
108:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
133:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
157:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
191:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L108)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L133](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L133)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L157)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L191](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
79:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
106:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
142:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
173:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```
[[ZetaTokenConsumerTrident.strategy.sol#L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L79)] 
[[ZetaTokenConsumerTrident.strategy.sol#L106](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L106)] 
[[ZetaTokenConsumerTrident.strategy.sol#L142](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L142)] 
[[ZetaTokenConsumerTrident.strategy.sol#L173](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
79:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
105:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
130:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
165:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```
[[ZetaTokenConsumerUniV3.strategy.sol#L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L105](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L165](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
93:        if (zetaFee_ == 0) {
```
[[ERC20Custody.sol#L93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L93)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
39:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
65:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
101:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
131:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```
[[ZetaTokenConsumerUniV2.strategy.sol#L39](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L39)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L65](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L65)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L101](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L101)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L131](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131)] 
## NC-5 | Use a single file for all system-wide constants

#### **Description** :-

Consider defining in only one contract so that values cannot become out of sync when only one location is updated. A [cheap way](https://medium.com/coinmonks/gas-cost-of-solidity-library-functions-dbe0cedd4678) to store constants in a single location is to create an internal constant in a library. If the variable is a local cache of another contract’s value, consider making the cache variable internal or private, which will require external users to query the contract with the source of truth, so that callers don’t get out of sync.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
22:    address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```
[[ZRC20.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
58:    uint256 internal constant MAX_DEADLINE = 200;
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
35:    uint256 internal constant MAX_DEADLINE = 200;
```
[[ZetaTokenConsumerTrident.strategy.sol#L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
29:    uint256 internal constant MAX_DEADLINE = 200;
```
[[ZetaTokenConsumerUniV3.strategy.sol#L29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
19:    uint256 internal constant MAX_DEADLINE = 200;
```
[[ZetaTokenConsumerUniV2.strategy.sol#L19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
31:    address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```
[[SystemContract.sol#L31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L31)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
63:    address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
```
[[ZetaConnectorZEVM.sol#L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
10:    bytes32 constant ZERO_BYTES = keccak256(new bytes(0));
```
[[ZetaInteractor.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10)] 
## NC-6 | Visibility should be set explicitly rather than defaulting to `internal`

#### **Description** :-

State variables that never used can be removed.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
10:    bytes32 constant ZERO_BYTES = keccak256(new bytes(0));
```
[[ZetaInteractor.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10)] 
## NC-7 | Contracts and libraries should be named using the `CapWords` style

#### **Description** :-

See [Contract and Library Names](https://docs.soliditylang.org/en/latest/style-guide.html#contract-and-library-names).


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol
```


```solidity
10:interface zContract {
```
[[zContract.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10)] 
## NC-8 | Control structures do not follow the Solidity Style Guide

#### **Description** :-

See the control structures section of the Solidity [Style Guide](https://docs.soliditylang.org/en/latest/style-guide.html#control-structures)


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
53:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
161:        if (currentAllowance < amount) revert LowAllowance();
```

```solidity
179:        if (sender == address(0)) revert ZeroAddress();
```

```solidity
180:        if (recipient == address(0)) revert ZeroAddress();
```

```solidity
183:        if (senderBalance < amount) revert LowBalance();
```

```solidity
192:        if (account == address(0)) revert ZeroAddress();
```

```solidity
200:        if (account == address(0)) revert ZeroAddress();
```

```solidity
203:        if (accountBalance < amount) revert LowBalance();
```

```solidity
212:        if (owner == address(0)) revert ZeroAddress();
```

```solidity
213:        if (spender == address(0)) revert ZeroAddress();
```

```solidity
226:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();
```

```solidity
238:        if (gasZRC20 == address(0)) {
```

```solidity
242:        if (gasPrice == 0) {
```

```solidity
258:        if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
```
[[ZRC20.sol#L53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53)] 
[[ZRC20.sol#L69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69)] 
[[ZRC20.sol#L161](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L161)] 
[[ZRC20.sol#L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L179)] 
[[ZRC20.sol#L180](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L180)] 
[[ZRC20.sol#L183](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L183)] 
[[ZRC20.sol#L192](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L192)] 
[[ZRC20.sol#L200](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L200)] 
[[ZRC20.sol#L203](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L203)] 
[[ZRC20.sol#L212](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L212)] 
[[ZRC20.sol#L213](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L213)] 
[[ZRC20.sol#L226](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226)] 
[[ZRC20.sol#L238](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L238)] 
[[ZRC20.sol#L242](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L242)] 
[[ZRC20.sol#L258](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
79:        if (
```

```solidity
95:        if (_locked) revert ReentrancyError();
```

```solidity
107:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
108:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
132:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
133:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
156:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
157:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
179:        if (!sent) revert ErrorSendingETH();
```

```solidity
190:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
191:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
212:        if (poolAddress == address(0)) {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L79)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L95](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L95)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L107)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L108)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L132)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L133](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L133)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L156](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L156)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L157)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L179)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L190](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L190)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L191](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L212](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L212)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
46:        if (
```

```solidity
60:        if (_locked) revert ReentrancyError();
```

```solidity
69:        if (token0 < token1) return (token0, token1);
```

```solidity
78:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
79:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
105:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
106:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
141:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
142:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
172:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
173:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```
[[ZetaTokenConsumerTrident.strategy.sol#L46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L46)] 
[[ZetaTokenConsumerTrident.strategy.sol#L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L60)] 
[[ZetaTokenConsumerTrident.strategy.sol#L69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L69)] 
[[ZetaTokenConsumerTrident.strategy.sol#L78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L78)] 
[[ZetaTokenConsumerTrident.strategy.sol#L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L79)] 
[[ZetaTokenConsumerTrident.strategy.sol#L105](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L105)] 
[[ZetaTokenConsumerTrident.strategy.sol#L106](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L106)] 
[[ZetaTokenConsumerTrident.strategy.sol#L141](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L141)] 
[[ZetaTokenConsumerTrident.strategy.sol#L142](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L142)] 
[[ZetaTokenConsumerTrident.strategy.sol#L172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L172)] 
[[ZetaTokenConsumerTrident.strategy.sol#L173](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
50:        if (
```

```solidity
66:        if (_locked) revert ReentrancyError();
```

```solidity
78:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
79:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
104:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
105:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
129:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
130:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
153:        if (!sent) revert ErrorSendingETH();
```

```solidity
164:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
165:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
187:        if (poolAddress == address(0)) {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L50)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L66)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L78)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L104](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L105](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L129](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L129)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L153](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L153)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L164](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L165](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L187](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L187)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
52:        if (msg.sender != TSSAddress) {
```

```solidity
62:        if (msg.sender != TSSAddressUpdater) {
```

```solidity
81:        if (TSSAddress_ == address(0)) {
```

```solidity
93:        if (zetaFee_ == 0) {
```

```solidity
96:        if (zetaFee_ > zetaMaxFee) {
```

```solidity
108:        if (TSSAddress == address(0)) {
```

```solidity
119:        if (paused) {
```

```solidity
122:        if (TSSAddress == address(0)) {
```

```solidity
133:        if (!paused) {
```

```solidity
171:        if (paused) {
```

```solidity
174:        if (!whitelisted[asset]) {
```

```solidity
177:        if (zetaFee != 0 && address(zeta) != address(0)) {
```

```solidity
194:        if (!whitelisted[asset]) {
```
[[ERC20Custody.sol#L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L52)] 
[[ERC20Custody.sol#L62](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L62)] 
[[ERC20Custody.sol#L81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L81)] 
[[ERC20Custody.sol#L93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L93)] 
[[ERC20Custody.sol#L96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L96)] 
[[ERC20Custody.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L108)] 
[[ERC20Custody.sol#L119](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L119)] 
[[ERC20Custody.sol#L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L122)] 
[[ERC20Custody.sol#L133](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L133)] 
[[ERC20Custody.sol#L171](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L171)] 
[[ERC20Custody.sol#L174](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L174)] 
[[ERC20Custody.sol#L177](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L177)] 
[[ERC20Custody.sol#L194](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L194)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
27:        if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
38:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
39:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
64:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
65:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
71:        if (inputToken == wETH) {
```

```solidity
100:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
101:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
130:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
131:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
137:        if (outputToken == wETH) {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L38)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L39](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L39)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L64](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L64)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L65](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L65)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L71](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L71)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L100](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L100)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L101](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L101)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L130)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L131](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L137](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L137)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
129:        if (_deployed[deploymentAddress]) {
```

```solidity
169:        if (_deployed[deploymentAddress]) {
```
[[ImmutableCreate2Factory.sol#L129](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L129)] 
[[ImmutableCreate2Factory.sol#L169](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L169)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
75:        if (
```

```solidity
94:        if (msg.sender != pauserAddress) revert CallerIsNotPauser(msg.sender);
```

```solidity
102:        if (msg.sender != tssAddress) revert CallerIsNotTss(msg.sender);
```

```solidity
110:        if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);
```

```solidity
118:        if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
129:        if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);
```

```solidity
130:        if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
141:        if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```
[[ZetaConnector.base.sol#L75](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L75)] 
[[ZetaConnector.base.sol#L94](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L94)] 
[[ZetaConnector.base.sol#L102](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L102)] 
[[ZetaConnector.base.sol#L110](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L110)] 
[[ZetaConnector.base.sol#L118](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L118)] 
[[ZetaConnector.base.sol#L129](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L129)] 
[[ZetaConnector.base.sol#L130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L130)] 
[[ZetaConnector.base.sol#L141](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L141)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
52:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
74:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
75:        if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();
```

```solidity
88:        if (tokenA == tokenB) revert CantBeIdenticalAddresses();
```

```solidity
90:        if (token0 == address(0)) revert CantBeZeroAddress();
```

```solidity
124:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
135:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
146:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
157:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
158:        if (addr == address(0)) revert ZeroAddress();
```

```solidity
168:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
169:        if (addr == address(0)) revert ZeroAddress();
```
[[SystemContract.sol#L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52)] 
[[SystemContract.sol#L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74)] 
[[SystemContract.sol#L75](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L75)] 
[[SystemContract.sol#L88](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L88)] 
[[SystemContract.sol#L90](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L90)] 
[[SystemContract.sol#L124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124)] 
[[SystemContract.sol#L135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135)] 
[[SystemContract.sol#L146](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146)] 
[[SystemContract.sol#L157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157)] 
[[SystemContract.sol#L158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L158)] 
[[SystemContract.sol#L168](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168)] 
[[SystemContract.sol#L169](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L169)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
85:        if (msg.sender != wzeta) revert OnlyWZETA();
```

```solidity
94:        if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();
```

```solidity
97:        if (!sent) revert FailedZetaSent();
```

```solidity
115:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
```
[[ZetaConnectorZEVM.sol#L85](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L85)] 
[[ZetaConnectorZEVM.sol#L94](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L94)] 
[[ZetaConnectorZEVM.sol#L97](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L97)] 
[[ZetaConnectorZEVM.sol#L115](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
```

```solidity
72:        if (message.length > 0) {
```

```solidity
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
```

```solidity
100:        if (message.length > 0) {
```
[[ZetaConnector.non-eth.sol#L69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L69)] 
[[ZetaConnector.non-eth.sol#L72](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L72)] 
[[ZetaConnector.non-eth.sol#L96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L96)] 
[[ZetaConnector.non-eth.sol#L100](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L100)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
33:        if (!success) revert ZetaTransferError();
```

```solidity
61:        if (!success) revert ZetaTransferError();
```

```solidity
63:        if (message.length > 0) {
```

```solidity
87:        if (!success) revert ZetaTransferError();
```

```solidity
89:        if (message.length > 0) {
```
[[ZetaConnector.eth.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L33)] 
[[ZetaConnector.eth.sol#L61](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L61)] 
[[ZetaConnector.eth.sol#L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L63)] 
[[ZetaConnector.eth.sol#L87](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L87)] 
[[ZetaConnector.eth.sol#L89](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L89)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
49:        if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
```
[[WZETA.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L49)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
34:        if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();
```

```solidity
41:        if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);
```

```solidity
42:        if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();
```

```solidity
55:        if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);
```

```solidity
56:        if (tssAddress == address(0)) revert InvalidAddress();
```

```solidity
66:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
```

```solidity
77:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
```
[[Zeta.non-eth.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L34)] 
[[Zeta.non-eth.sol#L41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L41)] 
[[Zeta.non-eth.sol#L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L42)] 
[[Zeta.non-eth.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L55)] 
[[Zeta.non-eth.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L56)] 
[[Zeta.non-eth.sol#L66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L66)] 
[[Zeta.non-eth.sol#L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
25:        if (keccak256(zetaMessage.zetaTxSenderAddress) != keccak256(interactorsByChainId[zetaMessage.sourceChainId]))
```

```solidity
32:        if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
```

```solidity
33:        if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();
```

```solidity
38:        if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
44:        if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
```
[[ZetaInteractor.sol#L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L25)] 
[[ZetaInteractor.sol#L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L32)] 
[[ZetaInteractor.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L33)] 
[[ZetaInteractor.sol#L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L38)] 
[[ZetaInteractor.sol#L44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L44)] 
## NC-9 | Constructor visibility is ignored

#### **Description** :-

The following functions visibility is ignored.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
71:    constructor(
72:        address zetaToken_,
73:        address pancakeV3Router_,
74:        address uniswapV3Factory_,
75:        address WETH9Address_,
76:        uint24 zetaPoolFee_,
77:        uint24 tokenPoolFee_
78:    ) {
79:        if (
80:            zetaToken_ == address(0) ||
81:            pancakeV3Router_ == address(0) ||
82:            uniswapV3Factory_ == address(0) ||
83:            WETH9Address_ == address(0)
84:        ) revert ZetaCommonErrors.InvalidAddress();
85:
86:        zetaToken = zetaToken_;
87:        pancakeV3Router = ISwapRouterPancake(pancakeV3Router_);
88:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
89:        WETH9Address = WETH9Address_;
90:        zetaPoolFee = zetaPoolFee_;
91:        tokenPoolFee = tokenPoolFee_;
92:    }
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
45:    constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
46:        if (
47:            zetaToken_ == address(0) ||
48:            uniswapV3Router_ == address(0) ||
49:            WETH9Address_ == address(0) ||
50:            poolFactory_ == address(0)
51:        ) revert ZetaCommonErrors.InvalidAddress();
52:
53:        zetaToken = zetaToken_;
54:        tridentRouter = IPoolRouter(uniswapV3Router_);
55:        poolFactory = ConcentratedLiquidityPoolFactory(poolFactory_);
56:        WETH9Address = WETH9Address_;
57:    }
```
[[ZetaTokenConsumerTrident.strategy.sol#L45-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L57)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
42:    constructor(
43:        address zetaToken_,
44:        address uniswapV3Router_,
45:        address uniswapV3Factory_,
46:        address WETH9Address_,
47:        uint24 zetaPoolFee_,
48:        uint24 tokenPoolFee_
49:    ) {
50:        if (
51:            zetaToken_ == address(0) ||
52:            uniswapV3Router_ == address(0) ||
53:            uniswapV3Factory_ == address(0) ||
54:            WETH9Address_ == address(0)
55:        ) revert ZetaCommonErrors.InvalidAddress();
56:
57:        zetaToken = zetaToken_;
58:        uniswapV3Router = ISwapRouter(uniswapV3Router_);
59:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
60:        WETH9Address = WETH9Address_;
61:        zetaPoolFee = zetaPoolFee_;
62:        tokenPoolFee = tokenPoolFee_;
63:    }
```
[[ZetaTokenConsumerUniV3.strategy.sol#L42-L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L63)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
68:    constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
69:        TSSAddress = TSSAddress_;
70:        TSSAddressUpdater = TSSAddressUpdater_;
71:        zetaFee = zetaFee_;
72:        zeta = zeta_;
73:        zetaMaxFee = zetaMaxFee_;
74:    }
```
[[ERC20Custody.sol#L68-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
26:    constructor(address zetaToken_, address uniswapV2Router_) {
27:        if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
28:
29:        zetaToken = zetaToken_;
30:        uniswapV2Router = IUniswapV2Router02(uniswapV2Router_);
31:        wETH = IUniswapV2Router02(uniswapV2Router_).WETH();
32:    }
```
[[ZetaTokenConsumerUniV2.strategy.sol#L26-L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26-L32)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
74:    constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
75:        if (
76:            zetaToken_ == address(0) ||
77:            tssAddress_ == address(0) ||
78:            tssAddressUpdater_ == address(0) ||
79:            pauserAddress_ == address(0)
80:        ) {
81:            revert ZetaCommonErrors.InvalidAddress();
82:        }
83:
84:        zetaToken = zetaToken_;
85:        tssAddress = tssAddress_;
86:        tssAddressUpdater = tssAddressUpdater_;
87:        pauserAddress = pauserAddress_;
88:    }
```
[[ZetaConnector.base.sol#L74-L88](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74-L88)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
51:    constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
52:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
53:        wZetaContractAddress = wzeta_;
54:        uniswapv2FactoryAddress = uniswapv2Factory_;
55:        uniswapv2Router02Address = uniswapv2Router02_;
56:        emit SystemContractDeployed();
57:    }
```
[[SystemContract.sol#L51-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51-L57)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
79:    constructor(address wzeta_) {
80:        wzeta = wzeta_;
81:    }
```
[[ZetaConnectorZEVM.sol#L79-L81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L81)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
20:    constructor(
21:        address zetaTokenAddress_,
22:        address tssAddress_,
23:        address tssAddressUpdater_,
24:        address pauserAddress_
25:    ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```
[[ZetaConnector.non-eth.sol#L20-L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
16:    constructor(
17:        address zetaToken_,
18:        address tssAddress_,
19:        address tssAddressUpdater_,
20:        address pauserAddress_
21:    ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```
[[ZetaConnector.eth.sol#L16-L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
33:    constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {
34:        if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();
35:
36:        tssAddress = tssAddress_;
37:        tssAddressUpdater = tssAddressUpdater_;
38:    }
```
[[Zeta.non-eth.sol#L33-L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L38)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
37:    constructor(address zetaConnectorAddress) {
38:        if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
39:        currentChainId = block.chainid;
40:        connector = ZetaConnector(zetaConnectorAddress);
41:    }
```
[[ZetaInteractor.sol#L37-L41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L37-L41)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
10:    constructor(address creator, uint256 initialSupply) {
11:        _mint(creator, initialSupply * (10 ** uint256(decimals())));
12:    }
```
[[Zeta.eth.sol#L10-L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L12)] 
## NC-10 | Use Custom Errors

#### **Description** :-

Instead of using error strings, to reduce deployment and runtime cost, you should use Custom Errors. This would save both deployment and runtime cost.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
50:        require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
```

```solidity
67:        require(
68:            deploymentAddress == targetDeploymentAddress,
69:            "Failed to deploy contract using provided salt and initialization code."
70:        );
```
[[ImmutableCreate2Factory.sol#L50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L50)] 
[[ImmutableCreate2Factory.sol#L67-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L67-L70)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
26:        require(balanceOf[msg.sender] >= wad);
```

```solidity
47:        require(balanceOf[src] >= wad);
```
[[WZETA.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L26)] 
[[WZETA.sol#L47](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L47)] 
## NC-11 | Use delete instead of assigning values to false

#### **Description** :-

The use of the delete keyword is recommended over simply assigning values to false when you intend to reset the state of a variable. The delete keyword more closely aligns with the semantic intent of clearing or resetting a variable. This practice also makes the code more readable and highlights the change in state, which may encourage a more thorough audit of the surrounding logic.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
154:        whitelisted[asset] = false;
```
[[ERC20Custody.sol#L154](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L154)] 
## NC-12 | Duplicated require statements should be refactored

#### **Description** :-

These statements should be refactored to a separate function, as there are multiple parts of the codebase that use the same logic, to improve the code readability and reduce code duplication.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
50:        require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
```

```solidity
67:        require(
68:            deploymentAddress == targetDeploymentAddress,
69:            "Failed to deploy contract using provided salt and initialization code."
70:        );
```
[[ImmutableCreate2Factory.sol#L50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L50)] 
[[ImmutableCreate2Factory.sol#L67-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L67-L70)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
26:        require(balanceOf[msg.sender] >= wad);
```

```solidity
47:        require(balanceOf[src] >= wad);
```
[[WZETA.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L26)] 
[[WZETA.sol#L47](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L47)] 
## NC-13 | Event is missing msg.sender parameter

#### **Description** :-

The following functions are missing some parameters when emitting an event: when dealing with a source address which uses the value of msg.sender, the msg.sender value should be specified in every event.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
188:        emit Transfer(sender, recipient, amount);
```

```solidity
196:        emit Transfer(address(0), account, amount);
```

```solidity
208:        emit Transfer(account, address(0), amount);
```

```solidity
216:        emit Approval(owner, spender, amount);
```

```solidity
228:        emit Deposit(abi.encodePacked(FUNGIBLE_MODULE_ADDRESS), to, amount);
```

```solidity
262:        emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);
```

```solidity
272:        emit UpdatedSystemContract(addr);
```

```solidity
281:        emit UpdatedGasLimit(gasLimit);
```

```solidity
290:        emit UpdatedProtocolFlatFee(protocolFlatFee);
```
[[ZRC20.sol#L188](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L188)] 
[[ZRC20.sol#L196](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L196)] 
[[ZRC20.sol#L208](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L208)] 
[[ZRC20.sol#L216](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L216)] 
[[ZRC20.sol#L228](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L228)] 
[[ZRC20.sol#L262](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L262)] 
[[ZRC20.sol#L272](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L272)] 
[[ZRC20.sol#L281](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L281)] 
[[ZRC20.sol#L290](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L290)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
122:        emit EthExchangedForZeta(msg.value, amountOut);
```

```solidity
147:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
```

```solidity
176:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
```

```solidity
205:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L122)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L147](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L147)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L176](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L176)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L205](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L205)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
95:        emit EthExchangedForZeta(msg.value, amountOut);
```

```solidity
132:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
```

```solidity
161:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
```

```solidity
199:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```
[[ZetaTokenConsumerTrident.strategy.sol#L95](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L95)] 
[[ZetaTokenConsumerTrident.strategy.sol#L132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L132)] 
[[ZetaTokenConsumerTrident.strategy.sol#L161](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L161)] 
[[ZetaTokenConsumerTrident.strategy.sol#L199](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L199)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
94:        emit EthExchangedForZeta(msg.value, amountOut);
```

```solidity
120:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
```

```solidity
150:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
```

```solidity
180:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```
[[ZetaTokenConsumerUniV3.strategy.sol#L94](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L94)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L120](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L120)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L150](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L150)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L180](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L180)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
85:        emit UpdatedTSSAddress(TSSAddress_);
```

```solidity
100:        emit UpdatedZetaFee(zetaFee_);
```

```solidity
112:        emit RenouncedTSSUpdater(msg.sender);
```

```solidity
126:        emit Paused(msg.sender);
```

```solidity
137:        emit Unpaused(msg.sender);
```

```solidity
146:        emit Whitelisted(asset);
```

```solidity
155:        emit Unwhitelisted(asset);
```

```solidity
184:        emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
```

```solidity
198:        emit Withdrawn(recipient, asset, amount);
```
[[ERC20Custody.sol#L85](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L85)] 
[[ERC20Custody.sol#L100](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L100)] 
[[ERC20Custody.sol#L112](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L112)] 
[[ERC20Custody.sol#L126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L126)] 
[[ERC20Custody.sol#L137](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L137)] 
[[ERC20Custody.sol#L146](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L146)] 
[[ERC20Custody.sol#L155](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L155)] 
[[ERC20Custody.sol#L184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L184)] 
[[ERC20Custody.sol#L198](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L198)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
54:        emit EthExchangedForZeta(msg.value, amountOut);
```

```solidity
91:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
```

```solidity
120:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
```

```solidity
158:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```
[[ZetaTokenConsumerUniV2.strategy.sol#L54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L54)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L91)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L120](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L120)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L158)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
122:        emit PauserAddressUpdated(msg.sender, pauserAddress_);
```

```solidity
134:        emit TSSAddressUpdated(msg.sender, tssAddress_);
```

```solidity
144:        emit TSSAddressUpdaterUpdated(msg.sender, tssAddressUpdater);
```
[[ZetaConnector.base.sol#L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L122)] 
[[ZetaConnector.base.sol#L134](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L134)] 
[[ZetaConnector.base.sol#L144](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L144)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
56:        emit SystemContractDeployed();
```

```solidity
126:        emit SetGasPrice(chainID, price);
```

```solidity
137:        emit SetGasCoin(chainID, zrc20);
```

```solidity
149:        emit SetGasZetaPool(chainID, pool);
```

```solidity
160:        emit SetWZeta(wZetaContractAddress);
```

```solidity
171:        emit SetConnectorZEVM(zetaConnectorZEVMAddress);
```
[[SystemContract.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L56)] 
[[SystemContract.sol#L126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L126)] 
[[SystemContract.sol#L137](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L137)] 
[[SystemContract.sol#L149](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L149)] 
[[SystemContract.sol#L160](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L160)] 
[[SystemContract.sol#L171](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L171)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
98:        emit ZetaSent(
99:            tx.origin,
100:            msg.sender,
101:            input.destinationChainId,
102:            input.destinationAddress,
103:            input.zetaValueAndGas,
104:            input.destinationGasLimit,
105:            input.message,
106:            input.zetaParams
107:        );
```

```solidity
117:        emit SetWZETA(wzeta_);
```
[[ZetaConnectorZEVM.sol#L98-L107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L98-L107)] 
[[ZetaConnectorZEVM.sol#L117](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L117)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
33:        emit MaxSupplyUpdated(msg.sender, maxSupply_);
```

```solidity
43:        emit ZetaSent(
44:            tx.origin,
45:            msg.sender,
46:            input.destinationChainId,
47:            input.destinationAddress,
48:            input.zetaValueAndGas,
49:            input.destinationGasLimit,
50:            input.message,
51:            input.zetaParams
52:        );
```

```solidity
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
```

```solidity
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
```
[[ZetaConnector.non-eth.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L33)] 
[[ZetaConnector.non-eth.sol#L43-L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L43-L52)] 
[[ZetaConnector.non-eth.sol#L78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L78)] 
[[ZetaConnector.non-eth.sol#L113-L121](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L113-L121)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
35:        emit ZetaSent(
36:            tx.origin,
37:            msg.sender,
38:            input.destinationChainId,
39:            input.destinationAddress,
40:            input.zetaValueAndGas,
41:            input.destinationGasLimit,
42:            input.message,
43:            input.zetaParams
44:        );
```

```solidity
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
```

```solidity
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
```
[[ZetaConnector.eth.sol#L35-L44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L35-L44)] 
[[ZetaConnector.eth.sol#L69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L69)] 
[[ZetaConnector.eth.sol#L102-L110](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L102-L110)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
47:        emit TSSAddressUpdated(msg.sender, tssAddress_);
```

```solidity
48:        emit ConnectorAddressUpdated(msg.sender, connectorAddress_);
```

```solidity
59:        emit TSSAddressUpdaterUpdated(msg.sender, tssAddress);
```

```solidity
70:        emit Minted(mintee, value, internalSendHash);
```

```solidity
81:        emit Burnt(account, amount);
```
[[Zeta.non-eth.sol#L47](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L47)] 
[[Zeta.non-eth.sol#L48](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L48)] 
[[Zeta.non-eth.sol#L59](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L59)] 
[[Zeta.non-eth.sol#L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L70)] 
[[Zeta.non-eth.sol#L81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L81)] 
## NC-14 | Emitting storage values instead of the memory one.

#### **Description** :-

Caching of a state variable replaces each Gwarmaccess (100 gas) with a much cheaper stack read. We can avoid unecessary SLOADs by caching storage values that were previously accessed and emitting those cached values.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
262:        emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);
```
[[ZRC20.sol#L262](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L262)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
144:        emit TSSAddressUpdaterUpdated(msg.sender, tssAddressUpdater);
```
[[ZetaConnector.base.sol#L144](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L144)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
160:        emit SetWZeta(wZetaContractAddress);
```

```solidity
171:        emit SetConnectorZEVM(zetaConnectorZEVMAddress);
```
[[SystemContract.sol#L160](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L160)] 
[[SystemContract.sol#L171](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L171)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
59:        emit TSSAddressUpdaterUpdated(msg.sender, tssAddress);
```
[[Zeta.non-eth.sol#L59](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L59)] 
## NC-15 | Empty Event

#### **Description** :-

The following event has no parameter in it to emit anything. Consider refactoring or removing this unusable line of code.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
41:    event SystemContractDeployed();
```
[[SystemContract.sol#L41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L41)] 
## NC-16 | Custom errors has no error details

#### **Description** :-




```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
10:    error CallerIsNotFungibleModule();
```

```solidity
11:    error InvalidSender();
```

```solidity
12:    error GasFeeTransferFailed();
```

```solidity
13:    error ZeroGasCoin();
```

```solidity
14:    error ZeroGasPrice();
```

```solidity
15:    error LowAllowance();
```

```solidity
16:    error LowBalance();
```

```solidity
17:    error ZeroAddress();
```
[[ZRC20.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L10)] 
[[ZRC20.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L11)] 
[[ZRC20.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L12)] 
[[ZRC20.sol#L13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L13)] 
[[ZRC20.sol#L14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L14)] 
[[ZRC20.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L15)] 
[[ZRC20.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L16)] 
[[ZRC20.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
13:    error InputCantBeZero();
```

```solidity
15:    error ErrorSendingETH();
```

```solidity
17:    error ReentrancyError();
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L13)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L15)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
13:    error InputCantBeZero();
```

```solidity
15:    error ErrorSendingETH();
```

```solidity
17:    error ReentrancyError();
```
[[ZetaTokenConsumerTrident.strategy.sol#L13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L13)] 
[[ZetaTokenConsumerTrident.strategy.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L15)] 
[[ZetaTokenConsumerTrident.strategy.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
13:    error InputCantBeZero();
```

```solidity
15:    error ErrorSendingETH();
```

```solidity
17:    error ReentrancyError();
```
[[ZetaTokenConsumerUniV3.strategy.sol#L13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L13)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L15)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
14:    error NotWhitelisted();
```

```solidity
15:    error NotPaused();
```

```solidity
16:    error InvalidSender();
```

```solidity
17:    error InvalidTSSUpdater();
```

```solidity
18:    error ZeroAddress();
```

```solidity
19:    error IsPaused();
```

```solidity
20:    error ZetaMaxFeeExceeded();
```

```solidity
21:    error ZeroFee();
```
[[ERC20Custody.sol#L14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14)] 
[[ERC20Custody.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L15)] 
[[ERC20Custody.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L16)] 
[[ERC20Custody.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L17)] 
[[ERC20Custody.sol#L18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L18)] 
[[ERC20Custody.sol#L19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L19)] 
[[ERC20Custody.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L20)] 
[[ERC20Custody.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L21)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
11:    error InputCantBeZero();
```
[[ZetaTokenConsumerUniV2.strategy.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L11)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
11:    error CallerIsNotFungibleModule();
```

```solidity
12:    error InvalidTarget();
```

```solidity
13:    error CantBeIdenticalAddresses();
```

```solidity
14:    error CantBeZeroAddress();
```

```solidity
15:    error ZeroAddress();
```
[[SystemContract.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L11)] 
[[SystemContract.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L12)] 
[[SystemContract.sol#L13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L13)] 
[[SystemContract.sol#L14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L14)] 
[[SystemContract.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
57:    error OnlyWZETA();
```

```solidity
58:    error WZETATransferFailed();
```

```solidity
59:    error OnlyFungibleModule();
```

```solidity
60:    error FailedZetaSent();
```
[[ZetaConnectorZEVM.sol#L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L57)] 
[[ZetaConnectorZEVM.sol#L58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L58)] 
[[ZetaConnectorZEVM.sol#L59](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L59)] 
[[ZetaConnectorZEVM.sol#L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L60)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
109:    error InvalidAddress();
```
[[ZetaInterfaces.sol#L109](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L109)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol
```


```solidity
9:    error CallerIsNotTss(address caller);
```

```solidity
12:    error CallerIsNotConnector(address caller);
```

```solidity
15:    error CallerIsNotTssUpdater(address caller);
```

```solidity
18:    error CallerIsNotTssOrUpdater(address caller);
```

```solidity
21:    error InvalidAddress();
```

```solidity
24:    error ZetaTransferError();
```
[[ZetaErrors.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L9)] 
[[ZetaErrors.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L12)] 
[[ZetaErrors.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L15)] 
[[ZetaErrors.sol#L18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L18)] 
[[ZetaErrors.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L21)] 
[[ZetaErrors.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L24)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol
```


```solidity
9:    error CallerIsNotPauser(address caller);
```

```solidity
12:    error CallerIsNotTss(address caller);
```

```solidity
15:    error CallerIsNotTssUpdater(address caller);
```

```solidity
18:    error CallerIsNotTssOrUpdater(address caller);
```

```solidity
21:    error ZetaTransferError();
```

```solidity
24:    error ExceedsMaxSupply(uint256 maxSupply);
```
[[ConnectorErrors.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L9)] 
[[ConnectorErrors.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L12)] 
[[ConnectorErrors.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L15)] 
[[ConnectorErrors.sol#L18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L18)] 
[[ConnectorErrors.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L21)] 
[[ConnectorErrors.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L24)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol
```


```solidity
9:    error InvalidDestinationChainId();
```

```solidity
12:    error InvalidCaller(address caller);
```

```solidity
15:    error InvalidZetaMessageCall();
```

```solidity
18:    error InvalidZetaRevertCall();
```
[[ZetaInteractorErrors.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L9)] 
[[ZetaInteractorErrors.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L12)] 
[[ZetaInteractorErrors.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L15)] 
[[ZetaInteractorErrors.sol#L18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L18)] 
## NC-17 | Missing event for critical changes

#### **Description** :-

Events should be emitted when critical changes are made to the contracts.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
54:    function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
55:        interactorsByChainId[destinationChainId] = contractAddress;
56:    }
```
[[ZetaInteractor.sol#L54-L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L56)] 
## NC-18 | Event is not properly indexed

#### **Description** :-

The emitted events are not indexed, making off-chain scripts such as front-ends of dApps difficult to filter the events efficiently.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
38:    event Paused(address sender);
```

```solidity
39:    event Unpaused(address sender);
```

```solidity
42:    event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message);
```

```solidity
43:    event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount);
```

```solidity
44:    event RenouncedTSSUpdater(address TSSAddressUpdater_);
```

```solidity
45:    event UpdatedTSSAddress(address TSSAddress_);
```

```solidity
46:    event UpdatedZetaFee(uint256 zetaFee_);
```
[[ERC20Custody.sol#L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38)] 
[[ERC20Custody.sol#L39](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39)] 
[[ERC20Custody.sol#L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42)] 
[[ERC20Custody.sol#L43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43)] 
[[ERC20Custody.sol#L44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44)] 
[[ERC20Custody.sol#L45](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45)] 
[[ERC20Custody.sol#L46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
34:    event ZetaSent(
35:        address sourceTxOriginAddress,
36:        address indexed zetaTxSenderAddress,
37:        uint256 indexed destinationChainId,
38:        bytes destinationAddress,
39:        uint256 zetaValueAndGas,
40:        uint256 destinationGasLimit,
41:        bytes message,
42:        bytes zetaParams
43:    );
```

```solidity
45:    event ZetaReceived(
46:        bytes zetaTxSenderAddress,
47:        uint256 indexed sourceChainId,
48:        address indexed destinationAddress,
49:        uint256 zetaValue,
50:        bytes message,
51:        bytes32 indexed internalSendHash
52:    );
```

```solidity
54:    event ZetaReverted(
55:        address zetaTxSenderAddress,
56:        uint256 sourceChainId,
57:        uint256 indexed destinationChainId,
58:        bytes destinationAddress,
59:        uint256 remainingZetaValue,
60:        bytes message,
61:        bytes32 indexed internalSendHash
62:    );
```

```solidity
64:    event TSSAddressUpdated(address callerAddress, address newTssAddress);
```

```solidity
66:    event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);
```

```solidity
68:    event PauserAddressUpdated(address callerAddress, address newTssAddress);
```
[[ZetaConnector.base.sol#L34-L43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L34-L43)] 
[[ZetaConnector.base.sol#L45-L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L45-L52)] 
[[ZetaConnector.base.sol#L54-L62](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L62)] 
[[ZetaConnector.base.sol#L64](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L64)] 
[[ZetaConnector.base.sol#L66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L66)] 
[[ZetaConnector.base.sol#L68](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
42:    event SetGasPrice(uint256, uint256);
```

```solidity
43:    event SetGasCoin(uint256, address);
```

```solidity
44:    event SetGasZetaPool(uint256, address);
```

```solidity
45:    event SetWZeta(address);
```

```solidity
46:    event SetConnectorZEVM(address);
```
[[SystemContract.sol#L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42)] 
[[SystemContract.sol#L43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43)] 
[[SystemContract.sol#L44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44)] 
[[SystemContract.sol#L45](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45)] 
[[SystemContract.sol#L46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
67:    event ZetaSent(
68:        address sourceTxOriginAddress,
69:        address indexed zetaTxSenderAddress,
70:        uint256 indexed destinationChainId,
71:        bytes destinationAddress,
72:        uint256 zetaValueAndGas,
73:        uint256 destinationGasLimit,
74:        bytes message,
75:        bytes zetaParams
76:    );
```

```solidity
77:    event SetWZETA(address wzeta_);
```
[[ZetaConnectorZEVM.sol#L67-L76](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L76)] 
[[ZetaConnectorZEVM.sol#L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
18:    event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply);
```
[[ZetaConnector.non-eth.sol#L18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
8:    event Approval(address indexed src, address indexed guy, uint wad);
```

```solidity
9:    event Transfer(address indexed src, address indexed dst, uint wad);
```

```solidity
10:    event Deposit(address indexed dst, uint wad);
```

```solidity
11:    event Withdrawal(address indexed src, uint wad);
```
[[WZETA.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L8)] 
[[WZETA.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L9)] 
[[WZETA.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L10)] 
[[WZETA.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L11)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
23:    event Minted(address indexed mintee, uint256 amount, bytes32 indexed internalSendHash);
```

```solidity
25:    event Burnt(address indexed burnee, uint256 amount);
```

```solidity
27:    event TSSAddressUpdated(address callerAddress, address newTssAddress);
```

```solidity
29:    event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress);
```

```solidity
31:    event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress);
```
[[Zeta.non-eth.sol#L23](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L23)] 
[[Zeta.non-eth.sol#L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L25)] 
[[Zeta.non-eth.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27)] 
[[Zeta.non-eth.sol#L29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29)] 
[[Zeta.non-eth.sol#L31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
78:    event EthExchangedForZeta(uint256 amountIn, uint256 amountOut);
```

```solidity
79:    event TokenExchangedForZeta(address token, uint256 amountIn, uint256 amountOut);
```

```solidity
80:    event ZetaExchangedForEth(uint256 amountIn, uint256 amountOut);
```

```solidity
81:    event ZetaExchangedForToken(address token, uint256 amountIn, uint256 amountOut);
```
[[ZetaInterfaces.sol#L78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L78)] 
[[ZetaInterfaces.sol#L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L79)] 
[[ZetaInterfaces.sol#L80](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L80)] 
[[ZetaInterfaces.sol#L81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L81)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Interfaces.sol
```


```solidity
40:    event Transfer(address indexed from, address indexed to, uint256 value);
```

```solidity
41:    event Approval(address indexed owner, address indexed spender, uint256 value);
```

```solidity
42:    event Deposit(bytes from, address indexed to, uint256 value);
```

```solidity
43:    event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasfee, uint256 protocolFlatFee);
```

```solidity
44:    event UpdatedSystemContract(address systemContract);
```

```solidity
45:    event UpdatedGasLimit(uint256 gasLimit);
```

```solidity
46:    event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```
[[Interfaces.sol#L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L40)] 
[[Interfaces.sol#L41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L41)] 
[[Interfaces.sol#L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L42)] 
[[Interfaces.sol#L43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43)] 
[[Interfaces.sol#L44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L44)] 
[[Interfaces.sol#L45](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45)] 
[[Interfaces.sol#L46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L46)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol
```


```solidity
5:    event Approval(address indexed owner, address indexed spender, uint value);
```

```solidity
6:    event Transfer(address indexed from, address indexed to, uint value);
```

```solidity
7:    event Deposit(address indexed dst, uint wad);
```

```solidity
8:    event Withdrawal(address indexed src, uint wad);
```
[[IWZETA.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5)] 
[[IWZETA.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6)] 
[[IWZETA.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L7)] 
[[IWZETA.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L8)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
```


```solidity
31:    event Transfer(address indexed from, address indexed to, uint256 value);
```

```solidity
32:    event Approval(address indexed owner, address indexed spender, uint256 value);
```

```solidity
33:    event Deposit(bytes from, address indexed to, uint256 value);
```

```solidity
34:    event Withdrawal(address indexed from, bytes to, uint256 value, uint256 gasFee, uint256 protocolFlatFee);
```

```solidity
35:    event UpdatedSystemContract(address systemContract);
```

```solidity
36:    event UpdatedGasLimit(uint256 gasLimit);
```

```solidity
37:    event UpdatedProtocolFlatFee(uint256 protocolFlatFee);
```
[[IZRC20.sol#L31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L31)] 
[[IZRC20.sol#L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L32)] 
[[IZRC20.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L33)] 
[[IZRC20.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L34)] 
[[IZRC20.sol#L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L35)] 
[[IZRC20.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L36)] 
[[IZRC20.sol#L37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L37)] 
## NC-19 | Events that mark critical parameter changes should contain both the old and the new value

#### **Description** :-

This should especially be done if the new value is not required to be different from the old value.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
54:    function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
55:        interactorsByChainId[destinationChainId] = contractAddress;
56:    }
```
[[ZetaInteractor.sol#L54-L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L56)] 
## NC-20 | Events may be emitted out of order due to reentranc

#### **Description** :-

Ensure that events follow the best practice of check-effects-interaction, and are emitted before external calls


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
205:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L205](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L205)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
199:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```
[[ZetaTokenConsumerTrident.strategy.sol#L199](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L199)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
180:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
```
[[ZetaTokenConsumerUniV3.strategy.sol#L180](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L180)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
184:        emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
```

```solidity
198:        emit Withdrawn(recipient, asset, amount);
```
[[ERC20Custody.sol#L184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L184)] 
[[ERC20Custody.sol#L198](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L198)] 
## NC-21 | Contract functions should use an interface

#### **Description** :-

All external/public functions should extend an interface. This is useful to make sure that the whole API is extracted.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
83:    function name() public view virtual override returns (string memory) {
```

```solidity
91:    function symbol() public view virtual override returns (string memory) {
```

```solidity
99:    function decimals() public view virtual override returns (uint8) {
```

```solidity
107:    function totalSupply() public view virtual override returns (uint256) {
```

```solidity
116:    function balanceOf(address account) public view virtual override returns (uint256) {
```

```solidity
125:    function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
```

```solidity
135:    function allowance(address owner, address spender) public view virtual override returns (uint256) {
```

```solidity
145:    function approve(address spender, uint256 amount) public virtual override returns (bool) {
```

```solidity
157:    function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
```

```solidity
173:    function burn(uint256 amount) external returns (bool) {
```

```solidity
225:    function deposit(address to, uint256 amount) external override returns (bool) {
```

```solidity
236:    function withdrawGasFee() public view override returns (address, uint256) {
```

```solidity
256:    function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
```

```solidity
270:    function updateSystemContractAddress(address addr) external onlyFungible {
```

```solidity
279:    function updateGasLimit(uint256 gasLimit) external onlyFungible {
```

```solidity
288:    function updateProtocolFlatFee(uint256 protocolFlatFee) external onlyFungible {
```
[[ZRC20.sol#L83](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83)] 
[[ZRC20.sol#L91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91)] 
[[ZRC20.sol#L99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99)] 
[[ZRC20.sol#L107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L107)] 
[[ZRC20.sol#L116](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L116)] 
[[ZRC20.sol#L125](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125)] 
[[ZRC20.sol#L135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135)] 
[[ZRC20.sol#L145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145)] 
[[ZRC20.sol#L157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157)] 
[[ZRC20.sol#L173](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173)] 
[[ZRC20.sol#L225](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225)] 
[[ZRC20.sol#L236](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236)] 
[[ZRC20.sol#L256](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256)] 
[[ZRC20.sol#L270](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270)] 
[[ZRC20.sol#L279](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L279)] 
[[ZRC20.sol#L288](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L288)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
101:    receive() external payable {}
```

```solidity
103:    function getZetaFromEth(
```

```solidity
126:    function getZetaFromToken(
```

```solidity
151:    function getEthFromZeta(
```

```solidity
184:    function getTokenFromZeta(
```

```solidity
209:    function hasZetaLiquidity() external view override returns (bool) {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L101](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L103](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L151](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L209](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
66:    receive() external payable {}
```

```solidity
74:    function getZetaFromEth(
```

```solidity
99:    function getZetaFromToken(
```

```solidity
136:    function getEthFromZeta(
```

```solidity
166:    function getTokenFromZeta(
```

```solidity
203:    function hasZetaLiquidity() external view override returns (bool) {
```
[[ZetaTokenConsumerTrident.strategy.sol#L66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66)] 
[[ZetaTokenConsumerTrident.strategy.sol#L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74)] 
[[ZetaTokenConsumerTrident.strategy.sol#L99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99)] 
[[ZetaTokenConsumerTrident.strategy.sol#L136](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136)] 
[[ZetaTokenConsumerTrident.strategy.sol#L166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166)] 
[[ZetaTokenConsumerTrident.strategy.sol#L203](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
72:    receive() external payable {}
```

```solidity
74:    function getZetaFromEth(
```

```solidity
98:    function getZetaFromToken(
```

```solidity
124:    function getEthFromZeta(
```

```solidity
158:    function getTokenFromZeta(
```

```solidity
184:    function hasZetaLiquidity() external view override returns (bool) {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L72](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L98](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
80:    function updateTSSAddress(address TSSAddress_) external onlyTSSUpdater {
```

```solidity
92:    function updateZetaFee(uint256 zetaFee_) external onlyTSS {
```

```solidity
107:    function renounceTSSAddressUpdater() external onlyTSSUpdater {
```

```solidity
118:    function pause() external onlyTSS {
```

```solidity
132:    function unpause() external onlyTSS {
```

```solidity
144:    function whitelist(IERC20 asset) external onlyTSS {
```

```solidity
153:    function unwhitelist(IERC20 asset) external onlyTSS {
```

```solidity
165:    function deposit(
```

```solidity
193:    function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
```
[[ERC20Custody.sol#L80](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L80)] 
[[ERC20Custody.sol#L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L92)] 
[[ERC20Custody.sol#L107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L107)] 
[[ERC20Custody.sol#L118](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L118)] 
[[ERC20Custody.sol#L132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L132)] 
[[ERC20Custody.sol#L144](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144)] 
[[ERC20Custody.sol#L153](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153)] 
[[ERC20Custody.sol#L165](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165)] 
[[ERC20Custody.sol#L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
34:    function getZetaFromEth(
```

```solidity
58:    function getZetaFromToken(
```

```solidity
95:    function getEthFromZeta(
```

```solidity
124:    function getTokenFromZeta(
```

```solidity
162:    function hasZetaLiquidity() external view override returns (bool) {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L95](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L162](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
87:    function safeCreate2(
```

```solidity
108:    function findCreate2Address(
```

```solidity
148:    function findCreate2AddressViaHash(
```

```solidity
180:    function hasBeenDeployed(address deploymentAddress) external view returns (bool) {
```

```solidity
202:    function safeCreate2AndTransfer(
```
[[ImmutableCreate2Factory.sol#L87](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L87)] 
[[ImmutableCreate2Factory.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L108)] 
[[ImmutableCreate2Factory.sol#L148](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L148)] 
[[ImmutableCreate2Factory.sol#L180](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L180)] 
[[ImmutableCreate2Factory.sol#L202](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L202)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
117:    function updatePauserAddress(address pauserAddress_) external onlyPauser {
```

```solidity
128:    function updateTssAddress(address tssAddress_) external {
```

```solidity
140:    function renounceTssAddressUpdater() external onlyTssUpdater {
```

```solidity
151:    function pause() external onlyPauser {
```

```solidity
159:    function unpause() external onlyPauser {
```

```solidity
166:    function send(ZetaInterfaces.SendInput calldata input) external virtual {}
```

```solidity
172:    function onReceive(
```

```solidity
185:    function onRevert(
```
[[ZetaConnector.base.sol#L117](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117)] 
[[ZetaConnector.base.sol#L128](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L128)] 
[[ZetaConnector.base.sol#L140](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L140)] 
[[ZetaConnector.base.sol#L151](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L151)] 
[[ZetaConnector.base.sol#L159](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L159)] 
[[ZetaConnector.base.sol#L166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166)] 
[[ZetaConnector.base.sol#L172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172)] 
[[ZetaConnector.base.sol#L185](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
67:    function depositAndCall(
```

```solidity
100:    function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {
```

```solidity
123:    function setGasPrice(uint256 chainID, uint256 price) external {
```

```solidity
134:    function setGasCoinZRC20(uint256 chainID, address zrc20) external {
```

```solidity
145:    function setGasZetaPool(uint256 chainID, address erc20) external {
```

```solidity
156:    function setWZETAContractAddress(address addr) external {
```

```solidity
167:    function setConnectorZEVMAddress(address addr) external {
```
[[SystemContract.sol#L67](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67)] 
[[SystemContract.sol#L100](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L100)] 
[[SystemContract.sol#L123](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123)] 
[[SystemContract.sol#L134](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134)] 
[[SystemContract.sol#L145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L145)] 
[[SystemContract.sol#L156](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L156)] 
[[SystemContract.sol#L167](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L167)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
84:    receive() external payable {
```

```solidity
92:    function send(ZetaInterfaces.SendInput calldata input) external {
```

```solidity
114:    function setWzetaAddress(address wzeta_) external {
```
[[ZetaConnectorZEVM.sol#L84](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L84)] 
[[ZetaConnectorZEVM.sol#L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92)] 
[[ZetaConnectorZEVM.sol#L114](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
27:    function getLockedAmount() external view returns (uint256) {
```

```solidity
31:    function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
```

```solidity
40:    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
```

```solidity
61:    function onReceive(
```

```solidity
87:    function onRevert(
```
[[ZetaConnector.non-eth.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L27)] 
[[ZetaConnector.non-eth.sol#L31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31)] 
[[ZetaConnector.non-eth.sol#L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40)] 
[[ZetaConnector.non-eth.sol#L61](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61)] 
[[ZetaConnector.non-eth.sol#L87](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
23:    function getLockedAmount() external view returns (uint256) {
```

```solidity
31:    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
```

```solidity
52:    function onReceive(
```

```solidity
77:    function onRevert(
```
[[ZetaConnector.eth.sol#L23](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23)] 
[[ZetaConnector.eth.sol#L31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31)] 
[[ZetaConnector.eth.sol#L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52)] 
[[ZetaConnector.eth.sol#L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
16:    function() public payable {
```

```solidity
20:    function deposit() public payable {
```

```solidity
25:    function withdraw(uint wad) public {
```

```solidity
32:    function totalSupply() public view returns (uint) {
```

```solidity
36:    function approve(address guy, uint wad) public returns (bool) {
```

```solidity
42:    function transfer(address dst, uint wad) public returns (bool) {
```

```solidity
46:    function transferFrom(address src, address dst, uint wad) public returns (bool) {
```
[[WZETA.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L16)] 
[[WZETA.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L20)] 
[[WZETA.sol#L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L25)] 
[[WZETA.sol#L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L32)] 
[[WZETA.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36)] 
[[WZETA.sol#L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L42)] 
[[WZETA.sol#L46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L46)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
40:    function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {
```

```solidity
54:    function renounceTssAddressUpdater() external {
```

```solidity
62:    function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
```

```solidity
73:    function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```
[[Zeta.non-eth.sol#L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40)] 
[[Zeta.non-eth.sol#L54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L54)] 
[[Zeta.non-eth.sol#L62](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62)] 
[[Zeta.non-eth.sol#L73](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73)] 
## NC-22 | Consider moving msg.sender checks to modifiers

#### **Description** :-

If some functions are only allowed to be called by some specific users, consider using a modifier instead of checking with a require statement, especially if this check is done in multiple functions.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
53:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
226:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();
```

```solidity
258:        if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
```
[[ZRC20.sol#L53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53)] 
[[ZRC20.sol#L69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69)] 
[[ZRC20.sol#L226](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226)] 
[[ZRC20.sol#L258](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L258)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
52:        if (msg.sender != TSSAddress) {
```

```solidity
62:        if (msg.sender != TSSAddressUpdater) {
```
[[ERC20Custody.sol#L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L52)] 
[[ERC20Custody.sol#L62](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L62)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
94:        if (msg.sender != pauserAddress) revert CallerIsNotPauser(msg.sender);
```

```solidity
102:        if (msg.sender != tssAddress) revert CallerIsNotTss(msg.sender);
```

```solidity
110:        if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);
```

```solidity
129:        if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);
```
[[ZetaConnector.base.sol#L94](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L94)] 
[[ZetaConnector.base.sol#L102](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L102)] 
[[ZetaConnector.base.sol#L110](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L110)] 
[[ZetaConnector.base.sol#L129](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L129)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
52:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
74:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
124:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
135:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
146:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
157:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
168:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```
[[SystemContract.sol#L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52)] 
[[SystemContract.sol#L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74)] 
[[SystemContract.sol#L124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124)] 
[[SystemContract.sol#L135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135)] 
[[SystemContract.sol#L146](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146)] 
[[SystemContract.sol#L157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157)] 
[[SystemContract.sol#L168](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
85:        if (msg.sender != wzeta) revert OnlyWZETA();
```

```solidity
94:        if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();
```

```solidity
115:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
```
[[ZetaConnectorZEVM.sol#L85](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L85)] 
[[ZetaConnectorZEVM.sol#L94](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L94)] 
[[ZetaConnectorZEVM.sol#L115](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
49:        if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
```
[[WZETA.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L49)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
41:        if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);
```

```solidity
55:        if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender);
```

```solidity
66:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
```

```solidity
77:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
```
[[Zeta.non-eth.sol#L41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L41)] 
[[Zeta.non-eth.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L55)] 
[[Zeta.non-eth.sol#L66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L66)] 
[[Zeta.non-eth.sol#L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
44:        if (msg.sender != address(connector)) revert InvalidCaller(msg.sender);
```
[[ZetaInteractor.sol#L44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L44)] 
## NC-23 | Functions should use `mixedCase`

#### **Description** :-

See [Function Names](https://docs.soliditylang.org/en/latest/style-guide.html#function-names).


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
83:    function name() public view virtual override returns (string memory) {
```

```solidity
91:    function symbol() public view virtual override returns (string memory) {
```

```solidity
99:    function decimals() public view virtual override returns (uint8) {
```

```solidity
125:    function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
```

```solidity
135:    function allowance(address owner, address spender) public view virtual override returns (uint256) {
```

```solidity
145:    function approve(address spender, uint256 amount) public virtual override returns (bool) {
```

```solidity
173:    function burn(uint256 amount) external returns (bool) {
```

```solidity
225:    function deposit(address to, uint256 amount) external override returns (bool) {
```

```solidity
256:    function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
```
[[ZRC20.sol#L83](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83)] 
[[ZRC20.sol#L91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91)] 
[[ZRC20.sol#L99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99)] 
[[ZRC20.sol#L125](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125)] 
[[ZRC20.sol#L135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135)] 
[[ZRC20.sol#L145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145)] 
[[ZRC20.sol#L173](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173)] 
[[ZRC20.sol#L225](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225)] 
[[ZRC20.sol#L256](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
21:    function withdraw(uint256 wad) external;
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L21)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
21:    function deposit() external payable;
```

```solidity
23:    function withdraw(uint256 wad) external;
```
[[ZetaTokenConsumerTrident.strategy.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L21)] 
[[ZetaTokenConsumerTrident.strategy.sol#L23](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L23)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
21:    function withdraw(uint256 wad) external;
```
[[ZetaTokenConsumerUniV3.strategy.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L21)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
118:    function pause() external onlyTSS {
```

```solidity
132:    function unpause() external onlyTSS {
```

```solidity
144:    function whitelist(IERC20 asset) external onlyTSS {
```

```solidity
153:    function unwhitelist(IERC20 asset) external onlyTSS {
```

```solidity
165:    function deposit(
```

```solidity
193:    function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
```
[[ERC20Custody.sol#L118](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L118)] 
[[ERC20Custody.sol#L132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L132)] 
[[ERC20Custody.sol#L144](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144)] 
[[ERC20Custody.sol#L153](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153)] 
[[ERC20Custody.sol#L165](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165)] 
[[ERC20Custody.sol#L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
151:    function pause() external onlyPauser {
```

```solidity
159:    function unpause() external onlyPauser {
```

```solidity
166:    function send(ZetaInterfaces.SendInput calldata input) external virtual {}
```
[[ZetaConnector.base.sol#L151](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L151)] 
[[ZetaConnector.base.sol#L159](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L159)] 
[[ZetaConnector.base.sol#L166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
100:    function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {
```
[[SystemContract.sol#L100](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L100)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
52:    function withdraw(uint wad) external;
```

```solidity
92:    function send(ZetaInterfaces.SendInput calldata input) external {
```
[[ZetaConnectorZEVM.sol#L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L52)] 
[[ZetaConnectorZEVM.sol#L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
40:    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
```
[[ZetaConnector.non-eth.sol#L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
31:    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
```
[[ZetaConnector.eth.sol#L31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
16:    function() public payable {
```

```solidity
20:    function deposit() public payable {
```

```solidity
25:    function withdraw(uint wad) public {
```

```solidity
36:    function approve(address guy, uint wad) public returns (bool) {
```

```solidity
42:    function transfer(address dst, uint wad) public returns (bool) {
```
[[WZETA.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L16)] 
[[WZETA.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L20)] 
[[WZETA.sol#L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L25)] 
[[WZETA.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36)] 
[[WZETA.sol#L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L42)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
62:    function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
```
[[Zeta.non-eth.sol#L62](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
53:    function send(ZetaInterfaces.SendInput calldata input) external;
```
[[ZetaInterfaces.sol#L53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L53)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol
```


```solidity
70:    function sweep(address token, uint256 amount, address recipient) external payable;
```
[[TridentIPoolRouter.sol#L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L70)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Interfaces.sol
```


```solidity
8:    function FUNGIBLE_MODULE_ADDRESS() external view returns (address);
```

```solidity
12:    function uniswapv2FactoryAddress() external view returns (address);
```

```solidity
26:    function transfer(address recipient, uint256 amount) external returns (bool);
```

```solidity
28:    function allowance(address owner, address spender) external view returns (uint256);
```

```solidity
30:    function approve(address spender, uint256 amount) external returns (bool);
```

```solidity
34:    function deposit(address to, uint256 amount) external returns (bool);
```

```solidity
36:    function withdraw(bytes memory to, uint256 amount) external returns (bool);
```

```solidity
50:    function name() external view returns (string memory);
```

```solidity
52:    function symbol() external view returns (string memory);
```

```solidity
54:    function decimals() external view returns (uint8);
```
[[Interfaces.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L8)] 
[[Interfaces.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L12)] 
[[Interfaces.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L26)] 
[[Interfaces.sol#L28](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L28)] 
[[Interfaces.sol#L30](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L30)] 
[[Interfaces.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L34)] 
[[Interfaces.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36)] 
[[Interfaces.sol#L50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L50)] 
[[Interfaces.sol#L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L52)] 
[[Interfaces.sol#L54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L54)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol
```


```solidity
14:    function allowance(address owner, address spender) external view returns (uint);
```

```solidity
16:    function approve(address spender, uint wad) external returns (bool);
```

```solidity
18:    function transfer(address to, uint wad) external returns (bool);
```

```solidity
22:    function deposit() external payable;
```

```solidity
24:    function withdraw(uint wad) external;
```
[[IWZETA.sol#L14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L14)] 
[[IWZETA.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L16)] 
[[IWZETA.sol#L18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L18)] 
[[IWZETA.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L22)] 
[[IWZETA.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L24)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
12:    function mint(address mintee, uint256 value, bytes32 internalSendHash) external;
```
[[ZetaNonEthInterface.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
```


```solidity
9:    function transfer(address recipient, uint256 amount) external returns (bool);
```

```solidity
11:    function allowance(address owner, address spender) external view returns (uint256);
```

```solidity
13:    function approve(address spender, uint256 amount) external returns (bool);
```

```solidity
21:    function deposit(address to, uint256 amount) external returns (bool);
```

```solidity
23:    function burn(address account, uint256 amount) external returns (bool);
```

```solidity
25:    function withdraw(bytes memory to, uint256 amount) external returns (bool);
```

```solidity
29:    function PROTOCOL_FEE() external view returns (uint256);
```
[[IZRC20.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L9)] 
[[IZRC20.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L11)] 
[[IZRC20.sol#L13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L13)] 
[[IZRC20.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L21)] 
[[IZRC20.sol#L23](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L23)] 
[[IZRC20.sol#L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25)] 
[[IZRC20.sol#L29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L29)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol
```


```solidity
5:    function factory() external pure returns (address);
```

```solidity
7:    function WETH() external pure returns (address);
```

```solidity
121:    function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB);
```
[[IUniswapV2Router01.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L5)] 
[[IUniswapV2Router01.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L7)] 
[[IUniswapV2Router01.sol#L121](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L121)] 
## NC-24 | Imports could be organized more systematically

#### **Description** :-

the contract's interface should be imported first, followed by each of the interfaces it uses, followed by all other files. The examples below do not follow this layout.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
3:import "./Interfaces.sol";
```
[[ZRC20.sol#L3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L3)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
4:import "@openzeppelin/contracts/interfaces/IERC20.sol";
```

```solidity
5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```

```solidity
6:import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
```

```solidity
7:import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";
```

```solidity
8:import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
```

```solidity
10:import "../interfaces/ZetaInterfaces.sol";
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L4)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L5)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L6)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L7)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L8)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
4:import "@openzeppelin/contracts/interfaces/IERC20.sol";
```

```solidity
5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```

```solidity
6:import "@uniswap/v3-periphery/contracts/interfaces/IQuoter.sol";
```

```solidity
8:import "../interfaces/ZetaInterfaces.sol";
```

```solidity
9:import "./interfaces/TridentConcentratedLiquidityPoolFactory.sol";
```

```solidity
10:import "./interfaces/TridentIPoolRouter.sol";
```
[[ZetaTokenConsumerTrident.strategy.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L4)] 
[[ZetaTokenConsumerTrident.strategy.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L5)] 
[[ZetaTokenConsumerTrident.strategy.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L6)] 
[[ZetaTokenConsumerTrident.strategy.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L8)] 
[[ZetaTokenConsumerTrident.strategy.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L9)] 
[[ZetaTokenConsumerTrident.strategy.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
4:import "@openzeppelin/contracts/interfaces/IERC20.sol";
```

```solidity
5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```

```solidity
6:import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
```

```solidity
7:import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";
```

```solidity
8:import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
```

```solidity
10:import "../interfaces/ZetaInterfaces.sol";
```
[[ZetaTokenConsumerUniV3.strategy.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L4)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L5)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L6)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L7)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L8)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
5:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

```solidity
6:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```

```solidity
7:import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
```
[[ERC20Custody.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L5)] 
[[ERC20Custody.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L6)] 
[[ERC20Custody.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
4:import "@openzeppelin/contracts/interfaces/IERC20.sol";
```

```solidity
5:import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```

```solidity
6:import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
```

```solidity
8:import "../interfaces/ZetaInterfaces.sol";
```
[[ZetaTokenConsumerUniV2.strategy.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L4)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L5)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L6)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L8)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

```solidity
5:import "@openzeppelin/contracts/security/Pausable.sol";
```

```solidity
7:import "./interfaces/ConnectorErrors.sol";
```

```solidity
8:import "./interfaces/ZetaInterfaces.sol";
```
[[ZetaConnector.base.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L4)] 
[[ZetaConnector.base.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L5)] 
[[ZetaConnector.base.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L7)] 
[[ZetaConnector.base.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L8)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
4:import "./interfaces/zContract.sol";
```

```solidity
5:import "./interfaces/IZRC20.sol";
```
[[SystemContract.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L4)] 
[[SystemContract.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L5)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

```solidity
6:import "./ZetaConnector.base.sol";
```

```solidity
7:import "./interfaces/ZetaInterfaces.sol";
```

```solidity
8:import "./interfaces/ZetaNonEthInterface.sol";
```
[[ZetaConnector.non-eth.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L4)] 
[[ZetaConnector.non-eth.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L6)] 
[[ZetaConnector.non-eth.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L7)] 
[[ZetaConnector.non-eth.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L8)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

```solidity
6:import "./interfaces/ConnectorErrors.sol";
```

```solidity
7:import "./ZetaConnector.base.sol";
```

```solidity
8:import "./interfaces/ZetaInterfaces.sol";
```
[[ZetaConnector.eth.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L4)] 
[[ZetaConnector.eth.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L6)] 
[[ZetaConnector.eth.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L7)] 
[[ZetaConnector.eth.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L8)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
4:import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
```

```solidity
6:import "./interfaces/ZetaErrors.sol";
```

```solidity
8:import "./interfaces/ZetaNonEthInterface.sol";
```
[[Zeta.non-eth.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L4)] 
[[Zeta.non-eth.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L6)] 
[[Zeta.non-eth.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L8)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
4:import "@openzeppelin/contracts/access/Ownable2Step.sol";
```

```solidity
6:import "../interfaces/ZetaInterfaces.sol";
```

```solidity
7:import "../interfaces/ZetaInteractorErrors.sol";
```
[[ZetaInteractor.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L4)] 
[[ZetaInteractor.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L6)] 
[[ZetaInteractor.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
4:import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
```
[[Zeta.eth.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
4:import "./IUniswapV2Router01.sol";
```
[[IUniswapV2Router02.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Uniswap.sol
```


```solidity
4:import "@uniswap/v2-core/contracts/UniswapV2Pair.sol";
```

```solidity
5:import "@uniswap/v2-core/contracts/UniswapV2Factory.sol";
```
[[Uniswap.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L4)] 
[[Uniswap.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L5)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```
[[ZetaNonEthInterface.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol
```


```solidity
4:import "@uniswap/v2-periphery/contracts/UniswapV2Router02.sol";
```
[[UniswapPeriphery.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L4)] 
## NC-25 | internal functions only called once can be inlined

#### **Description** :-

Not inlining costs 20 to 40 gas because of two extra JUMP instructions and additional stack operations needed for function calls.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
191:    function _mint(address account, uint256 amount) internal virtual {
192:        if (account == address(0)) revert ZeroAddress();
193:
194:        _totalSupply += amount;
195:        _balances[account] += amount;
196:        emit Transfer(address(0), account, amount);
197:    }
```
[[ZRC20.sol#L191-L197](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L191-L197)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
87:    function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
88:        if (tokenA == tokenB) revert CantBeIdenticalAddresses();
89:        (token0, token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
90:        if (token0 == address(0)) revert CantBeZeroAddress();
91:    }
```
[[SystemContract.sol#L87-L91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87-L91)] 
## NC-26 | Declare interfaces on separate files

#### **Description** :-

Interfaces should be declared on a separate file and not on the same file where the contract resides in.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
8:interface ZRC20Errors {
```
[[ZRC20.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
24:interface ISwapRouterPancake is IUniswapV3SwapCallback {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L24)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
20:interface WETH9 {
```
[[ZetaTokenConsumerTrident.strategy.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
20:interface WETH9 {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
10:interface ZetaTokenConsumerUniV2Errors {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
3:interface Ownable {
```
[[ImmutableCreate2Factory.sol#L3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L3)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
10:interface SystemContractErrors {
```
[[SystemContract.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
49:interface WZETA {
```
[[ZetaConnectorZEVM.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49)] 
## NC-27 | Interfaces should have an I prefix in the contract name

#### **Description** :-

As a best practice, any interface should have an I as a prefix in their contract name..


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
8:interface ZRC20Errors {
```
[[ZRC20.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
12:interface ZetaTokenConsumerUniV3Errors {
```

```solidity
20:interface WETH9 {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L12)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
12:interface ZetaTokenConsumerTridentErrors {
```

```solidity
20:interface WETH9 {
```
[[ZetaTokenConsumerTrident.strategy.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12)] 
[[ZetaTokenConsumerTrident.strategy.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
12:interface ZetaTokenConsumerUniV3Errors {
```

```solidity
20:interface WETH9 {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
10:interface ZetaTokenConsumerUniV2Errors {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
3:interface Ownable {
```
[[ImmutableCreate2Factory.sol#L3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L3)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
10:interface SystemContractErrors {
```
[[SystemContract.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
4:interface ZetaInterfaces {
```

```solidity
49:interface WZETA {
```
[[ZetaConnectorZEVM.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4)] 
[[ZetaConnectorZEVM.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
4:interface ZetaInterfaces {
```

```solidity
49:interface ZetaConnector {
```

```solidity
56:interface ZetaReceiver {
```

```solidity
77:interface ZetaTokenConsumer {
```

```solidity
108:interface ZetaCommonErrors {
```
[[ZetaInterfaces.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L4)] 
[[ZetaInterfaces.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49)] 
[[ZetaInterfaces.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56)] 
[[ZetaInterfaces.sol#L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77)] 
[[ZetaInterfaces.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol
```


```solidity
7:interface ZetaErrors {
```
[[ZetaErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol
```


```solidity
7:interface ConnectorErrors {
```
[[ConnectorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol
```


```solidity
10:interface zContract {
```
[[zContract.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol
```


```solidity
7:interface ZetaInteractorErrors {
```
[[ZetaInteractorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
9:interface ZetaNonEthInterface is IERC20 {
```
[[ZetaNonEthInterface.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
```


```solidity
16:interface ConcentratedLiquidityPoolFactory {
```
[[TridentConcentratedLiquidityPoolFactory.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16)] 
## NC-28 | internal functions not called by the contract should be removed

#### **Description** :-

If the functions are required by an interface, the contract should inherit from that interface and use the override keyword


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
45:    function _msgData() internal view virtual returns (bytes calldata) {
46:        return msg.data;
47:    }
```
[[ZRC20.sol#L45-L47](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L45-L47)] 
## NC-29 | Multiple mappings with same keys can be combined into a single struct mapping for readability

#### **Description** :-

Well-organized data structures make code reviews easier, which may lead to fewer bugs. Consider combining related mappings into mappings to structs, so it's clear what data is related.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
35:    mapping(address => mapping(address => uint256)) private _allowances;
```
[[ZRC20.sol#L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
26:    mapping(uint256 => address) public gasCoinZRC20ByChainId;
```

```solidity
28:    mapping(uint256 => address) public gasZetaPoolByChainId;
```
[[SystemContract.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L26)] 
[[SystemContract.sol#L28](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L28)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
14:    mapping(address => mapping(address => uint)) public allowance;
```
[[WZETA.sol#L14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L14)] 
## NC-30 | Contract declarations should have NatSpec `@author` annotations

#### **Description** :-

Contract declarations should have NatSpec @author annotations to provide a clear and concise description of the contract's purpose and functionality. NatSpec, short for Natural Language Specification, allows developers to document their smart contracts using human-readable comments.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
20:contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```
[[ZRC20.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
56:contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
33:contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```
[[ZetaTokenConsumerTrident.strategy.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
27:contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
11:contract ERC20Custody is ReentrancyGuard {
```
[[ERC20Custody.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
17:contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
22:contract ImmutableCreate2Factory {
```
[[ImmutableCreate2Factory.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
15:contract ZetaConnectorBase is ConnectorErrors, Pausable {
```
[[ZetaConnector.base.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
22:contract SystemContract is SystemContractErrors {
```
[[SystemContract.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
55:contract ZetaConnectorZEVM is ZetaInterfaces {
```
[[ZetaConnectorZEVM.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
15:contract ZetaConnectorNonEth is ZetaConnectorBase {
```
[[ZetaConnector.non-eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
15:contract ZetaConnectorEth is ZetaConnectorBase {
```
[[ZetaConnector.eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
3:contract WETH9 {
```
[[WZETA.sol#L3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L3)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
10:contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```
[[Zeta.non-eth.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
9:abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```
[[ZetaInteractor.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
108:interface ZetaCommonErrors {
```
[[ZetaInterfaces.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol
```


```solidity
16:interface IPoolRouter {
```
[[TridentIPoolRouter.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Interfaces.sol
```


```solidity
49:interface IZRC20Metadata is IZRC20 {
```
[[Interfaces.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol
```


```solidity
7:interface ZetaErrors {
```
[[ZetaErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol
```


```solidity
7:interface ConnectorErrors {
```
[[ConnectorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol
```


```solidity
10:interface zContract {
```
[[zContract.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol
```


```solidity
4:interface IWETH9 {
```
[[IWZETA.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
9:contract ZetaEth is ERC20("Zeta", "ZETA") {
```
[[Zeta.eth.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol
```


```solidity
7:interface ZetaInteractorErrors {
```
[[ZetaInteractorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
6:interface IUniswapV2Router02 is IUniswapV2Router01 {
```
[[IUniswapV2Router02.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Uniswap.sol
```


```solidity
7:contract UniswapImports {}
```
[[Uniswap.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
9:interface ZetaNonEthInterface is IERC20 {
```
[[ZetaNonEthInterface.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
```


```solidity
4:interface IZRC20 {
```
[[IZRC20.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
```


```solidity
16:interface ConcentratedLiquidityPoolFactory {
```
[[TridentConcentratedLiquidityPoolFactory.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol
```


```solidity
6:contract UniswapImports {}
```
[[UniswapPeriphery.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol
```


```solidity
4:interface IUniswapV2Router01 {
```
[[IUniswapV2Router01.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4)] 
## NC-31 | Contract declarations should have NatSpec `@dev` annotations

#### **Description** :-

Contract declarations should have NatSpec @dev annotations to provide a clear and concise description of the contract's purpose and functionality. NatSpec, short for Natural Language Specification, allows developers to document their smart contracts using human-readable comments.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
20:contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```
[[ZRC20.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
56:contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
33:contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```
[[ZetaTokenConsumerTrident.strategy.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
27:contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
11:contract ERC20Custody is ReentrancyGuard {
```
[[ERC20Custody.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
17:contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
22:contract ImmutableCreate2Factory {
```
[[ImmutableCreate2Factory.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
15:contract ZetaConnectorBase is ConnectorErrors, Pausable {
```
[[ZetaConnector.base.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
22:contract SystemContract is SystemContractErrors {
```
[[SystemContract.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
55:contract ZetaConnectorZEVM is ZetaInterfaces {
```
[[ZetaConnectorZEVM.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
15:contract ZetaConnectorNonEth is ZetaConnectorBase {
```
[[ZetaConnector.non-eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
15:contract ZetaConnectorEth is ZetaConnectorBase {
```
[[ZetaConnector.eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
3:contract WETH9 {
```
[[WZETA.sol#L3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L3)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
10:contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```
[[Zeta.non-eth.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
9:abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```
[[ZetaInteractor.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
108:interface ZetaCommonErrors {
```
[[ZetaInterfaces.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol
```


```solidity
16:interface IPoolRouter {
```
[[TridentIPoolRouter.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Interfaces.sol
```


```solidity
49:interface IZRC20Metadata is IZRC20 {
```
[[Interfaces.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol
```


```solidity
7:interface ZetaErrors {
```
[[ZetaErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol
```


```solidity
7:interface ConnectorErrors {
```
[[ConnectorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol
```


```solidity
10:interface zContract {
```
[[zContract.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol
```


```solidity
4:interface IWETH9 {
```
[[IWZETA.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
9:contract ZetaEth is ERC20("Zeta", "ZETA") {
```
[[Zeta.eth.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol
```


```solidity
7:interface ZetaInteractorErrors {
```
[[ZetaInteractorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
6:interface IUniswapV2Router02 is IUniswapV2Router01 {
```
[[IUniswapV2Router02.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Uniswap.sol
```


```solidity
7:contract UniswapImports {}
```
[[Uniswap.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
9:interface ZetaNonEthInterface is IERC20 {
```
[[ZetaNonEthInterface.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
```


```solidity
4:interface IZRC20 {
```
[[IZRC20.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
```


```solidity
16:interface ConcentratedLiquidityPoolFactory {
```
[[TridentConcentratedLiquidityPoolFactory.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol
```


```solidity
6:contract UniswapImports {}
```
[[UniswapPeriphery.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol
```


```solidity
4:interface IUniswapV2Router01 {
```
[[IUniswapV2Router01.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4)] 
## NC-32 | Missing events in sensitive functions

#### **Description** :-

Events should be emitted when sensitive changes are made to the contracts, but some functions lack them.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
54:    function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
55:        interactorsByChainId[destinationChainId] = contractAddress;
56:    }
```
[[ZetaInteractor.sol#L54-L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L56)] 
## NC-33 | File is miss SPDX-License-Identifier

#### **Description** :-

contract is missing an SPDX identifier which correctly licenses the contract for open source development.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
1:pragma solidity 0.5.10; // optimization enabled, 99999 runs, evm: petersburg
```
[[ImmutableCreate2Factory.sol#L1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L1)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
1:pragma solidity ^0.4.18;
```
[[WZETA.sol#L1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1)] 
## NC-34 | Contract declarations should have NatSpec `@title` annotations

#### **Description** :-

Contract declarations should have NatSpec @title annotations to provide a clear and concise description of the contract's purpose and functionality. NatSpec, short for Natural Language Specification, allows developers to document their smart contracts using human-readable comments.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
20:contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```
[[ZRC20.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
56:contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
33:contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```
[[ZetaTokenConsumerTrident.strategy.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
27:contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
11:contract ERC20Custody is ReentrancyGuard {
```
[[ERC20Custody.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
17:contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
22:contract ImmutableCreate2Factory {
```
[[ImmutableCreate2Factory.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
15:contract ZetaConnectorBase is ConnectorErrors, Pausable {
```
[[ZetaConnector.base.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
22:contract SystemContract is SystemContractErrors {
```
[[SystemContract.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
55:contract ZetaConnectorZEVM is ZetaInterfaces {
```
[[ZetaConnectorZEVM.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
15:contract ZetaConnectorNonEth is ZetaConnectorBase {
```
[[ZetaConnector.non-eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
15:contract ZetaConnectorEth is ZetaConnectorBase {
```
[[ZetaConnector.eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
3:contract WETH9 {
```
[[WZETA.sol#L3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L3)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
10:contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```
[[Zeta.non-eth.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
9:abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```
[[ZetaInteractor.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
108:interface ZetaCommonErrors {
```
[[ZetaInterfaces.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol
```


```solidity
16:interface IPoolRouter {
```
[[TridentIPoolRouter.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Interfaces.sol
```


```solidity
49:interface IZRC20Metadata is IZRC20 {
```
[[Interfaces.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol
```


```solidity
7:interface ZetaErrors {
```
[[ZetaErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol
```


```solidity
7:interface ConnectorErrors {
```
[[ConnectorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol
```


```solidity
10:interface zContract {
```
[[zContract.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol
```


```solidity
4:interface IWETH9 {
```
[[IWZETA.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
9:contract ZetaEth is ERC20("Zeta", "ZETA") {
```
[[Zeta.eth.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol
```


```solidity
7:interface ZetaInteractorErrors {
```
[[ZetaInteractorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
6:interface IUniswapV2Router02 is IUniswapV2Router01 {
```
[[IUniswapV2Router02.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Uniswap.sol
```


```solidity
7:contract UniswapImports {}
```
[[Uniswap.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
9:interface ZetaNonEthInterface is IERC20 {
```
[[ZetaNonEthInterface.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
```


```solidity
4:interface IZRC20 {
```
[[IZRC20.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
```


```solidity
16:interface ConcentratedLiquidityPoolFactory {
```
[[TridentConcentratedLiquidityPoolFactory.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol
```


```solidity
6:contract UniswapImports {}
```
[[UniswapPeriphery.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol
```


```solidity
4:interface IUniswapV2Router01 {
```
[[IUniswapV2Router01.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4)] 
## NC-35 | Named imports of parent contracts are missing

#### **Description** :-




```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
11:contract ERC20Custody is ReentrancyGuard {
```
[[ERC20Custody.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
15:contract ZetaConnectorBase is ConnectorErrors, Pausable {
```
[[ZetaConnector.base.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
10:contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```
[[Zeta.non-eth.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
9:contract ZetaEth is ERC20("Zeta", "ZETA") {
```
[[Zeta.eth.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9)] 
## NC-36 |  Names of `private`/`internal` state variables should be prefixed with an underscore

#### **Description** :-

According to the Solidity Style Guide, Non-external/public variable and function names should begin with an [underscore](https://docs.soliditylang.org/en/latest/style-guide.html#underscore-prefix-for-non-external-functions-and-variables).


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
58:    uint256 internal constant MAX_DEADLINE = 200;
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
35:    uint256 internal constant MAX_DEADLINE = 200;
```

```solidity
37:    address internal immutable WETH9Address;
```
[[ZetaTokenConsumerTrident.strategy.sol#L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35)] 
[[ZetaTokenConsumerTrident.strategy.sol#L37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
29:    uint256 internal constant MAX_DEADLINE = 200;
```
[[ZetaTokenConsumerUniV3.strategy.sol#L29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
19:    uint256 internal constant MAX_DEADLINE = 200;
```

```solidity
21:    address internal immutable wETH;
```

```solidity
24:    IUniswapV2Router02 internal immutable uniswapV2Router;
```
[[ZetaTokenConsumerUniV2.strategy.sol#L19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
11:    uint256 internal immutable currentChainId;
```
[[ZetaInteractor.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11)] 
## NC-37 |  Names of `private`/`internal` function should be prefixed with an underscore

#### **Description** :-

According to the Solidity Style Guide, Non-external/public variable and function names should begin with an [underscore](https://docs.soliditylang.org/en/latest/style-guide.html#underscore-prefix-for-non-external-functions-and-variables).


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
68:    function getPair(address token0, address token1) internal pure returns (address, address) {
69:        if (token0 < token1) return (token0, token1);
70:
71:        return (token1, token0);
72:    }
```
[[ZetaTokenConsumerTrident.strategy.sol#L68-L72](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L72)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
26:    function safeCreate2Internal(
27:        bytes32 salt,
28:        bytes memory initializationCode
29:    ) internal returns (address deploymentAddress) {
30:        // move the initialization code from calldata to memory.
31:        bytes memory initCode = initializationCode;
32:
33:        // determine the target address for contract deployment.
34:        address targetDeploymentAddress = address(
35:            uint160( // downcast to match the address type.
36:                uint256( // convert to uint to truncate upper digits.
37:                    keccak256( // compute the CREATE2 hash using 4 inputs.
38:                        abi.encodePacked( // pack all inputs to the hash together.
39:                            hex"ff", // start with 0xff to distinguish from RLP.
40:                            address(this), // this contract will be the caller.
41:                            salt, // pass in the supplied salt value.
42:                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
43:                        )
44:                    )
45:                )
46:            )
47:        );
48:
49:        // ensure that a contract hasn't been previously deployed to target address.
50:        require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
51:
52:        // using inline assembly: load data and length of data, then call CREATE2.
53:        assembly {
54:            // solhint-disable-line
55:            let encoded_data := add(0x20, initCode) // load initialization code.
56:            let encoded_size := mload(initCode) // load the init code's length.
57:            deploymentAddress := create2(
58:                // call CREATE2 with 4 arguments.
59:                callvalue, // forward any attached value.
60:                encoded_data, // pass in initialization code.
61:                encoded_size, // pass in init code's length.
62:                salt // pass in the salt value.
63:            )
64:        }
65:
66:        // check address against target to ensure that deployment was successful.
67:        require(
68:            deploymentAddress == targetDeploymentAddress,
69:            "Failed to deploy contract using provided salt and initialization code."
70:        );
71:
72:        // record the deployment of the contract to prevent redeploys.
73:        _deployed[deploymentAddress] = true;
74:    }
```
[[ImmutableCreate2Factory.sol#L26-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L26-L74)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
87:    function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
88:        if (tokenA == tokenB) revert CantBeIdenticalAddresses();
89:        (token0, token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
90:        if (token0 == address(0)) revert CantBeZeroAddress();
91:    }
```
[[SystemContract.sol#L87-L91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87-L91)] 
## NC-38 | Empty function body

#### **Description** :-

Consider adding a comment about why the function body is empty.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
101:    receive() external payable {}
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L101](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L101)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
66:    receive() external payable {}
```
[[ZetaTokenConsumerTrident.strategy.sol#L66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L66)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
72:    receive() external payable {}
```
[[ZetaTokenConsumerUniV3.strategy.sol#L72](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
166:    function send(ZetaInterfaces.SendInput calldata input) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```
[[ZetaConnector.base.sol#L166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
20:    constructor(
21:        address zetaTokenAddress_,
22:        address tssAddress_,
23:        address tssAddressUpdater_,
24:        address pauserAddress_
25:    ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```
[[ZetaConnector.non-eth.sol#L20-L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
16:    constructor(
17:        address zetaToken_,
18:        address tssAddress_,
19:        address tssAddressUpdater_,
20:        address pauserAddress_
21:    ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```
[[ZetaConnector.eth.sol#L16-L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21)] 
## NC-39 | Non-library/interface files should use fixed compiler versions, not floating ones

#### **Description** :-




```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
1:pragma solidity ^0.4.18;
```
[[WZETA.sol#L1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1)] 
## NC-40 | Contract declarations should have NatSpec `@notice` annotations

#### **Description** :-

Contract declarations should have NatSpec @notice annotations to provide a clear and concise description of the contract's purpose and functionality. NatSpec, short for Natural Language Specification, allows developers to document their smart contracts using human-readable comments.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
20:contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```
[[ZRC20.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
56:contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
33:contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```
[[ZetaTokenConsumerTrident.strategy.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
27:contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
11:contract ERC20Custody is ReentrancyGuard {
```
[[ERC20Custody.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
17:contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
22:contract ImmutableCreate2Factory {
```
[[ImmutableCreate2Factory.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
15:contract ZetaConnectorBase is ConnectorErrors, Pausable {
```
[[ZetaConnector.base.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
22:contract SystemContract is SystemContractErrors {
```
[[SystemContract.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
55:contract ZetaConnectorZEVM is ZetaInterfaces {
```
[[ZetaConnectorZEVM.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
15:contract ZetaConnectorNonEth is ZetaConnectorBase {
```
[[ZetaConnector.non-eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
15:contract ZetaConnectorEth is ZetaConnectorBase {
```
[[ZetaConnector.eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
3:contract WETH9 {
```
[[WZETA.sol#L3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L3)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
10:contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```
[[Zeta.non-eth.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
9:abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```
[[ZetaInteractor.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
108:interface ZetaCommonErrors {
```
[[ZetaInterfaces.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol
```


```solidity
16:interface IPoolRouter {
```
[[TridentIPoolRouter.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Interfaces.sol
```


```solidity
49:interface IZRC20Metadata is IZRC20 {
```
[[Interfaces.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol
```


```solidity
7:interface ZetaErrors {
```
[[ZetaErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol
```


```solidity
7:interface ConnectorErrors {
```
[[ConnectorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol
```


```solidity
10:interface zContract {
```
[[zContract.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol
```


```solidity
4:interface IWETH9 {
```
[[IWZETA.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
9:contract ZetaEth is ERC20("Zeta", "ZETA") {
```
[[Zeta.eth.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol
```


```solidity
7:interface ZetaInteractorErrors {
```
[[ZetaInteractorErrors.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
6:interface IUniswapV2Router02 is IUniswapV2Router01 {
```
[[IUniswapV2Router02.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Uniswap.sol
```


```solidity
7:contract UniswapImports {}
```
[[Uniswap.sol#L7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L7)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
9:interface ZetaNonEthInterface is IERC20 {
```
[[ZetaNonEthInterface.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
```


```solidity
4:interface IZRC20 {
```
[[IZRC20.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
```


```solidity
16:interface ConcentratedLiquidityPoolFactory {
```
[[TridentConcentratedLiquidityPoolFactory.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol
```


```solidity
6:contract UniswapImports {}
```
[[UniswapPeriphery.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol
```


```solidity
4:interface IUniswapV2Router01 {
```
[[IUniswapV2Router01.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4)] 
## NC-41 | Incomplete NatSpec @param from function declaration

#### **Description** :-

Some functions have an incomplete NatSpec: add a @param notation to describe the function parameters to improve the code documentation.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```

```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```

```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```

```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```

```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```

```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```

```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
71:    constructor(
72:        address zetaToken_,
73:        address pancakeV3Router_,
74:        address uniswapV3Factory_,
75:        address WETH9Address_,
76:        uint24 zetaPoolFee_,
77:        uint24 tokenPoolFee_
78:    ) {
79:        if (
80:            zetaToken_ == address(0) ||
81:            pancakeV3Router_ == address(0) ||
82:            uniswapV3Factory_ == address(0) ||
83:            WETH9Address_ == address(0)
84:        ) revert ZetaCommonErrors.InvalidAddress();
85:
86:        zetaToken = zetaToken_;
87:        pancakeV3Router = ISwapRouterPancake(pancakeV3Router_);
88:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
89:        WETH9Address = WETH9Address_;
90:        zetaPoolFee = zetaPoolFee_;
91:        tokenPoolFee = tokenPoolFee_;
92:    }
```

```solidity
71:    constructor(
72:        address zetaToken_,
73:        address pancakeV3Router_,
74:        address uniswapV3Factory_,
75:        address WETH9Address_,
76:        uint24 zetaPoolFee_,
77:        uint24 tokenPoolFee_
78:    ) {
79:        if (
80:            zetaToken_ == address(0) ||
81:            pancakeV3Router_ == address(0) ||
82:            uniswapV3Factory_ == address(0) ||
83:            WETH9Address_ == address(0)
84:        ) revert ZetaCommonErrors.InvalidAddress();
85:
86:        zetaToken = zetaToken_;
87:        pancakeV3Router = ISwapRouterPancake(pancakeV3Router_);
88:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
89:        WETH9Address = WETH9Address_;
90:        zetaPoolFee = zetaPoolFee_;
91:        tokenPoolFee = tokenPoolFee_;
92:    }
```

```solidity
71:    constructor(
72:        address zetaToken_,
73:        address pancakeV3Router_,
74:        address uniswapV3Factory_,
75:        address WETH9Address_,
76:        uint24 zetaPoolFee_,
77:        uint24 tokenPoolFee_
78:    ) {
79:        if (
80:            zetaToken_ == address(0) ||
81:            pancakeV3Router_ == address(0) ||
82:            uniswapV3Factory_ == address(0) ||
83:            WETH9Address_ == address(0)
84:        ) revert ZetaCommonErrors.InvalidAddress();
85:
86:        zetaToken = zetaToken_;
87:        pancakeV3Router = ISwapRouterPancake(pancakeV3Router_);
88:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
89:        WETH9Address = WETH9Address_;
90:        zetaPoolFee = zetaPoolFee_;
91:        tokenPoolFee = tokenPoolFee_;
92:    }
```

```solidity
71:    constructor(
72:        address zetaToken_,
73:        address pancakeV3Router_,
74:        address uniswapV3Factory_,
75:        address WETH9Address_,
76:        uint24 zetaPoolFee_,
77:        uint24 tokenPoolFee_
78:    ) {
79:        if (
80:            zetaToken_ == address(0) ||
81:            pancakeV3Router_ == address(0) ||
82:            uniswapV3Factory_ == address(0) ||
83:            WETH9Address_ == address(0)
84:        ) revert ZetaCommonErrors.InvalidAddress();
85:
86:        zetaToken = zetaToken_;
87:        pancakeV3Router = ISwapRouterPancake(pancakeV3Router_);
88:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
89:        WETH9Address = WETH9Address_;
90:        zetaPoolFee = zetaPoolFee_;
91:        tokenPoolFee = tokenPoolFee_;
92:    }
```

```solidity
71:    constructor(
72:        address zetaToken_,
73:        address pancakeV3Router_,
74:        address uniswapV3Factory_,
75:        address WETH9Address_,
76:        uint24 zetaPoolFee_,
77:        uint24 tokenPoolFee_
78:    ) {
79:        if (
80:            zetaToken_ == address(0) ||
81:            pancakeV3Router_ == address(0) ||
82:            uniswapV3Factory_ == address(0) ||
83:            WETH9Address_ == address(0)
84:        ) revert ZetaCommonErrors.InvalidAddress();
85:
86:        zetaToken = zetaToken_;
87:        pancakeV3Router = ISwapRouterPancake(pancakeV3Router_);
88:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
89:        WETH9Address = WETH9Address_;
90:        zetaPoolFee = zetaPoolFee_;
91:        tokenPoolFee = tokenPoolFee_;
92:    }
```

```solidity
71:    constructor(
72:        address zetaToken_,
73:        address pancakeV3Router_,
74:        address uniswapV3Factory_,
75:        address WETH9Address_,
76:        uint24 zetaPoolFee_,
77:        uint24 tokenPoolFee_
78:    ) {
79:        if (
80:            zetaToken_ == address(0) ||
81:            pancakeV3Router_ == address(0) ||
82:            uniswapV3Factory_ == address(0) ||
83:            WETH9Address_ == address(0)
84:        ) revert ZetaCommonErrors.InvalidAddress();
85:
86:        zetaToken = zetaToken_;
87:        pancakeV3Router = ISwapRouterPancake(pancakeV3Router_);
88:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
89:        WETH9Address = WETH9Address_;
90:        zetaPoolFee = zetaPoolFee_;
91:        tokenPoolFee = tokenPoolFee_;
92:    }
```

```solidity
103:    function getZetaFromEth(
104:        address destinationAddress,
105:        uint256 minAmountOut
106:    ) external payable override returns (uint256) {
107:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
108:        if (msg.value == 0) revert InputCantBeZero();
109:
110:        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
111:            tokenIn: WETH9Address,
112:            tokenOut: zetaToken,
113:            fee: zetaPoolFee,
114:            recipient: destinationAddress,
115:            amountIn: msg.value,
116:            amountOutMinimum: minAmountOut,
117:            sqrtPriceLimitX96: 0
118:        });
119:
120:        uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);
121:
122:        emit EthExchangedForZeta(msg.value, amountOut);
123:        return amountOut;
124:    }
```

```solidity
103:    function getZetaFromEth(
104:        address destinationAddress,
105:        uint256 minAmountOut
106:    ) external payable override returns (uint256) {
107:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
108:        if (msg.value == 0) revert InputCantBeZero();
109:
110:        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
111:            tokenIn: WETH9Address,
112:            tokenOut: zetaToken,
113:            fee: zetaPoolFee,
114:            recipient: destinationAddress,
115:            amountIn: msg.value,
116:            amountOutMinimum: minAmountOut,
117:            sqrtPriceLimitX96: 0
118:        });
119:
120:        uint256 amountOut = pancakeV3Router.exactInputSingle{value: msg.value}(params);
121:
122:        emit EthExchangedForZeta(msg.value, amountOut);
123:        return amountOut;
124:    }
```

```solidity
126:    function getZetaFromToken(
127:        address destinationAddress,
128:        uint256 minAmountOut,
129:        address inputToken,
130:        uint256 inputTokenAmount
131:    ) external override returns (uint256) {
132:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:        if (inputTokenAmount == 0) revert InputCantBeZero();
134:
135:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
136:        IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);
137:
138:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
140:            recipient: destinationAddress,
141:            amountIn: inputTokenAmount,
142:            amountOutMinimum: minAmountOut
143:        });
144:
145:        uint256 amountOut = pancakeV3Router.exactInput(params);
146:
147:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148:        return amountOut;
149:    }
```

```solidity
126:    function getZetaFromToken(
127:        address destinationAddress,
128:        uint256 minAmountOut,
129:        address inputToken,
130:        uint256 inputTokenAmount
131:    ) external override returns (uint256) {
132:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:        if (inputTokenAmount == 0) revert InputCantBeZero();
134:
135:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
136:        IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);
137:
138:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
140:            recipient: destinationAddress,
141:            amountIn: inputTokenAmount,
142:            amountOutMinimum: minAmountOut
143:        });
144:
145:        uint256 amountOut = pancakeV3Router.exactInput(params);
146:
147:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148:        return amountOut;
149:    }
```

```solidity
126:    function getZetaFromToken(
127:        address destinationAddress,
128:        uint256 minAmountOut,
129:        address inputToken,
130:        uint256 inputTokenAmount
131:    ) external override returns (uint256) {
132:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:        if (inputTokenAmount == 0) revert InputCantBeZero();
134:
135:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
136:        IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);
137:
138:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
140:            recipient: destinationAddress,
141:            amountIn: inputTokenAmount,
142:            amountOutMinimum: minAmountOut
143:        });
144:
145:        uint256 amountOut = pancakeV3Router.exactInput(params);
146:
147:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148:        return amountOut;
149:    }
```

```solidity
126:    function getZetaFromToken(
127:        address destinationAddress,
128:        uint256 minAmountOut,
129:        address inputToken,
130:        uint256 inputTokenAmount
131:    ) external override returns (uint256) {
132:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:        if (inputTokenAmount == 0) revert InputCantBeZero();
134:
135:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
136:        IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);
137:
138:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
140:            recipient: destinationAddress,
141:            amountIn: inputTokenAmount,
142:            amountOutMinimum: minAmountOut
143:        });
144:
145:        uint256 amountOut = pancakeV3Router.exactInput(params);
146:
147:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148:        return amountOut;
149:    }
```

```solidity
151:    function getEthFromZeta(
152:        address destinationAddress,
153:        uint256 minAmountOut,
154:        uint256 zetaTokenAmount
155:    ) external override returns (uint256) {
156:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
157:        if (zetaTokenAmount == 0) revert InputCantBeZero();
158:
159:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
160:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
161:
162:        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
163:            tokenIn: zetaToken,
164:            tokenOut: WETH9Address,
165:            fee: zetaPoolFee,
166:            recipient: address(this),
167:            amountIn: zetaTokenAmount,
168:            amountOutMinimum: minAmountOut,
169:            sqrtPriceLimitX96: 0
170:        });
171:
172:        uint256 amountOut = pancakeV3Router.exactInputSingle(params);
173:
174:        WETH9(WETH9Address).withdraw(amountOut);
175:
176:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
177:
178:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
179:        if (!sent) revert ErrorSendingETH();
180:
181:        return amountOut;
182:    }
```

```solidity
151:    function getEthFromZeta(
152:        address destinationAddress,
153:        uint256 minAmountOut,
154:        uint256 zetaTokenAmount
155:    ) external override returns (uint256) {
156:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
157:        if (zetaTokenAmount == 0) revert InputCantBeZero();
158:
159:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
160:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
161:
162:        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
163:            tokenIn: zetaToken,
164:            tokenOut: WETH9Address,
165:            fee: zetaPoolFee,
166:            recipient: address(this),
167:            amountIn: zetaTokenAmount,
168:            amountOutMinimum: minAmountOut,
169:            sqrtPriceLimitX96: 0
170:        });
171:
172:        uint256 amountOut = pancakeV3Router.exactInputSingle(params);
173:
174:        WETH9(WETH9Address).withdraw(amountOut);
175:
176:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
177:
178:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
179:        if (!sent) revert ErrorSendingETH();
180:
181:        return amountOut;
182:    }
```

```solidity
151:    function getEthFromZeta(
152:        address destinationAddress,
153:        uint256 minAmountOut,
154:        uint256 zetaTokenAmount
155:    ) external override returns (uint256) {
156:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
157:        if (zetaTokenAmount == 0) revert InputCantBeZero();
158:
159:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
160:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
161:
162:        ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
163:            tokenIn: zetaToken,
164:            tokenOut: WETH9Address,
165:            fee: zetaPoolFee,
166:            recipient: address(this),
167:            amountIn: zetaTokenAmount,
168:            amountOutMinimum: minAmountOut,
169:            sqrtPriceLimitX96: 0
170:        });
171:
172:        uint256 amountOut = pancakeV3Router.exactInputSingle(params);
173:
174:        WETH9(WETH9Address).withdraw(amountOut);
175:
176:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
177:
178:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
179:        if (!sent) revert ErrorSendingETH();
180:
181:        return amountOut;
182:    }
```

```solidity
184:    function getTokenFromZeta(
185:        address destinationAddress,
186:        uint256 minAmountOut,
187:        address outputToken,
188:        uint256 zetaTokenAmount
189:    ) external override nonReentrant returns (uint256) {
190:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
191:        if (zetaTokenAmount == 0) revert InputCantBeZero();
192:
193:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
194:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
195:
196:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
197:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
198:            recipient: destinationAddress,
199:            amountIn: zetaTokenAmount,
200:            amountOutMinimum: minAmountOut
201:        });
202:
203:        uint256 amountOut = pancakeV3Router.exactInput(params);
204:
205:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
206:        return amountOut;
207:    }
```

```solidity
184:    function getTokenFromZeta(
185:        address destinationAddress,
186:        uint256 minAmountOut,
187:        address outputToken,
188:        uint256 zetaTokenAmount
189:    ) external override nonReentrant returns (uint256) {
190:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
191:        if (zetaTokenAmount == 0) revert InputCantBeZero();
192:
193:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
194:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
195:
196:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
197:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
198:            recipient: destinationAddress,
199:            amountIn: zetaTokenAmount,
200:            amountOutMinimum: minAmountOut
201:        });
202:
203:        uint256 amountOut = pancakeV3Router.exactInput(params);
204:
205:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
206:        return amountOut;
207:    }
```

```solidity
184:    function getTokenFromZeta(
185:        address destinationAddress,
186:        uint256 minAmountOut,
187:        address outputToken,
188:        uint256 zetaTokenAmount
189:    ) external override nonReentrant returns (uint256) {
190:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
191:        if (zetaTokenAmount == 0) revert InputCantBeZero();
192:
193:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
194:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
195:
196:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
197:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
198:            recipient: destinationAddress,
199:            amountIn: zetaTokenAmount,
200:            amountOutMinimum: minAmountOut
201:        });
202:
203:        uint256 amountOut = pancakeV3Router.exactInput(params);
204:
205:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
206:        return amountOut;
207:    }
```

```solidity
184:    function getTokenFromZeta(
185:        address destinationAddress,
186:        uint256 minAmountOut,
187:        address outputToken,
188:        uint256 zetaTokenAmount
189:    ) external override nonReentrant returns (uint256) {
190:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
191:        if (zetaTokenAmount == 0) revert InputCantBeZero();
192:
193:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
194:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
195:
196:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
197:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
198:            recipient: destinationAddress,
199:            amountIn: zetaTokenAmount,
200:            amountOutMinimum: minAmountOut
201:        });
202:
203:        uint256 amountOut = pancakeV3Router.exactInput(params);
204:
205:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
206:        return amountOut;
207:    }
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L103-L124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L124)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L103-L124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103-L124)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L182)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
45:    constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
46:        if (
47:            zetaToken_ == address(0) ||
48:            uniswapV3Router_ == address(0) ||
49:            WETH9Address_ == address(0) ||
50:            poolFactory_ == address(0)
51:        ) revert ZetaCommonErrors.InvalidAddress();
52:
53:        zetaToken = zetaToken_;
54:        tridentRouter = IPoolRouter(uniswapV3Router_);
55:        poolFactory = ConcentratedLiquidityPoolFactory(poolFactory_);
56:        WETH9Address = WETH9Address_;
57:    }
```

```solidity
45:    constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
46:        if (
47:            zetaToken_ == address(0) ||
48:            uniswapV3Router_ == address(0) ||
49:            WETH9Address_ == address(0) ||
50:            poolFactory_ == address(0)
51:        ) revert ZetaCommonErrors.InvalidAddress();
52:
53:        zetaToken = zetaToken_;
54:        tridentRouter = IPoolRouter(uniswapV3Router_);
55:        poolFactory = ConcentratedLiquidityPoolFactory(poolFactory_);
56:        WETH9Address = WETH9Address_;
57:    }
```

```solidity
45:    constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
46:        if (
47:            zetaToken_ == address(0) ||
48:            uniswapV3Router_ == address(0) ||
49:            WETH9Address_ == address(0) ||
50:            poolFactory_ == address(0)
51:        ) revert ZetaCommonErrors.InvalidAddress();
52:
53:        zetaToken = zetaToken_;
54:        tridentRouter = IPoolRouter(uniswapV3Router_);
55:        poolFactory = ConcentratedLiquidityPoolFactory(poolFactory_);
56:        WETH9Address = WETH9Address_;
57:    }
```

```solidity
45:    constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
46:        if (
47:            zetaToken_ == address(0) ||
48:            uniswapV3Router_ == address(0) ||
49:            WETH9Address_ == address(0) ||
50:            poolFactory_ == address(0)
51:        ) revert ZetaCommonErrors.InvalidAddress();
52:
53:        zetaToken = zetaToken_;
54:        tridentRouter = IPoolRouter(uniswapV3Router_);
55:        poolFactory = ConcentratedLiquidityPoolFactory(poolFactory_);
56:        WETH9Address = WETH9Address_;
57:    }
```

```solidity
68:    function getPair(address token0, address token1) internal pure returns (address, address) {
69:        if (token0 < token1) return (token0, token1);
70:
71:        return (token1, token0);
72:    }
```

```solidity
68:    function getPair(address token0, address token1) internal pure returns (address, address) {
69:        if (token0 < token1) return (token0, token1);
70:
71:        return (token1, token0);
72:    }
```

```solidity
74:    function getZetaFromEth(
75:        address destinationAddress,
76:        uint256 minAmountOut
77:    ) external payable override returns (uint256) {
78:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
79:        if (msg.value == 0) revert InputCantBeZero();
80:
81:        (address token0, address token1) = getPair(WETH9Address, zetaToken);
82:        address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
83:
84:        IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
85:            tokenIn: address(0),
86:            amountIn: msg.value,
87:            amountOutMinimum: minAmountOut,
88:            pool: pairPools[0],
89:            to: destinationAddress,
90:            unwrap: false
91:        });
92:
93:        uint256 amountOut = tridentRouter.exactInputSingle{value: msg.value}(params);
94:
95:        emit EthExchangedForZeta(msg.value, amountOut);
96:        return amountOut;
97:    }
```

```solidity
74:    function getZetaFromEth(
75:        address destinationAddress,
76:        uint256 minAmountOut
77:    ) external payable override returns (uint256) {
78:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
79:        if (msg.value == 0) revert InputCantBeZero();
80:
81:        (address token0, address token1) = getPair(WETH9Address, zetaToken);
82:        address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
83:
84:        IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
85:            tokenIn: address(0),
86:            amountIn: msg.value,
87:            amountOutMinimum: minAmountOut,
88:            pool: pairPools[0],
89:            to: destinationAddress,
90:            unwrap: false
91:        });
92:
93:        uint256 amountOut = tridentRouter.exactInputSingle{value: msg.value}(params);
94:
95:        emit EthExchangedForZeta(msg.value, amountOut);
96:        return amountOut;
97:    }
```

```solidity
99:    function getZetaFromToken(
100:        address destinationAddress,
101:        uint256 minAmountOut,
102:        address inputToken,
103:        uint256 inputTokenAmount
104:    ) external override returns (uint256) {
105:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:        if (inputTokenAmount == 0) revert InputCantBeZero();
107:
108:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
109:        IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
110:
111:        (address token0, address token1) = getPair(inputToken, WETH9Address);
112:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
113:
114:        (token0, token1) = getPair(WETH9Address, zetaToken);
115:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
116:
117:        address[] memory path = new address[](2);
118:        path[0] = pairPools1[0];
119:        path[1] = pairPools2[0];
120:
121:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:            tokenIn: inputToken,
123:            amountIn: inputTokenAmount,
124:            amountOutMinimum: minAmountOut,
125:            path: path,
126:            to: destinationAddress,
127:            unwrap: false
128:        });
129:
130:        uint256 amountOut = tridentRouter.exactInput(params);
131:
132:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133:        return amountOut;
134:    }
```

```solidity
99:    function getZetaFromToken(
100:        address destinationAddress,
101:        uint256 minAmountOut,
102:        address inputToken,
103:        uint256 inputTokenAmount
104:    ) external override returns (uint256) {
105:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:        if (inputTokenAmount == 0) revert InputCantBeZero();
107:
108:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
109:        IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
110:
111:        (address token0, address token1) = getPair(inputToken, WETH9Address);
112:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
113:
114:        (token0, token1) = getPair(WETH9Address, zetaToken);
115:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
116:
117:        address[] memory path = new address[](2);
118:        path[0] = pairPools1[0];
119:        path[1] = pairPools2[0];
120:
121:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:            tokenIn: inputToken,
123:            amountIn: inputTokenAmount,
124:            amountOutMinimum: minAmountOut,
125:            path: path,
126:            to: destinationAddress,
127:            unwrap: false
128:        });
129:
130:        uint256 amountOut = tridentRouter.exactInput(params);
131:
132:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133:        return amountOut;
134:    }
```

```solidity
99:    function getZetaFromToken(
100:        address destinationAddress,
101:        uint256 minAmountOut,
102:        address inputToken,
103:        uint256 inputTokenAmount
104:    ) external override returns (uint256) {
105:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:        if (inputTokenAmount == 0) revert InputCantBeZero();
107:
108:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
109:        IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
110:
111:        (address token0, address token1) = getPair(inputToken, WETH9Address);
112:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
113:
114:        (token0, token1) = getPair(WETH9Address, zetaToken);
115:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
116:
117:        address[] memory path = new address[](2);
118:        path[0] = pairPools1[0];
119:        path[1] = pairPools2[0];
120:
121:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:            tokenIn: inputToken,
123:            amountIn: inputTokenAmount,
124:            amountOutMinimum: minAmountOut,
125:            path: path,
126:            to: destinationAddress,
127:            unwrap: false
128:        });
129:
130:        uint256 amountOut = tridentRouter.exactInput(params);
131:
132:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133:        return amountOut;
134:    }
```

```solidity
99:    function getZetaFromToken(
100:        address destinationAddress,
101:        uint256 minAmountOut,
102:        address inputToken,
103:        uint256 inputTokenAmount
104:    ) external override returns (uint256) {
105:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:        if (inputTokenAmount == 0) revert InputCantBeZero();
107:
108:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
109:        IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
110:
111:        (address token0, address token1) = getPair(inputToken, WETH9Address);
112:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
113:
114:        (token0, token1) = getPair(WETH9Address, zetaToken);
115:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
116:
117:        address[] memory path = new address[](2);
118:        path[0] = pairPools1[0];
119:        path[1] = pairPools2[0];
120:
121:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:            tokenIn: inputToken,
123:            amountIn: inputTokenAmount,
124:            amountOutMinimum: minAmountOut,
125:            path: path,
126:            to: destinationAddress,
127:            unwrap: false
128:        });
129:
130:        uint256 amountOut = tridentRouter.exactInput(params);
131:
132:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133:        return amountOut;
134:    }
```

```solidity
136:    function getEthFromZeta(
137:        address destinationAddress,
138:        uint256 minAmountOut,
139:        uint256 zetaTokenAmount
140:    ) external override returns (uint256) {
141:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
142:        if (zetaTokenAmount == 0) revert InputCantBeZero();
143:
144:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
145:        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
146:
147:        (address token0, address token1) = getPair(zetaToken, WETH9Address);
148:        address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
149:
150:        IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
151:            tokenIn: zetaToken,
152:            amountIn: zetaTokenAmount,
153:            amountOutMinimum: minAmountOut,
154:            pool: pairPools[0],
155:            to: destinationAddress,
156:            unwrap: true
157:        });
158:
159:        uint256 amountOut = tridentRouter.exactInputSingle(params);
160:
161:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162:
163:        return amountOut;
164:    }
```

```solidity
136:    function getEthFromZeta(
137:        address destinationAddress,
138:        uint256 minAmountOut,
139:        uint256 zetaTokenAmount
140:    ) external override returns (uint256) {
141:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
142:        if (zetaTokenAmount == 0) revert InputCantBeZero();
143:
144:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
145:        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
146:
147:        (address token0, address token1) = getPair(zetaToken, WETH9Address);
148:        address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
149:
150:        IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
151:            tokenIn: zetaToken,
152:            amountIn: zetaTokenAmount,
153:            amountOutMinimum: minAmountOut,
154:            pool: pairPools[0],
155:            to: destinationAddress,
156:            unwrap: true
157:        });
158:
159:        uint256 amountOut = tridentRouter.exactInputSingle(params);
160:
161:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162:
163:        return amountOut;
164:    }
```

```solidity
136:    function getEthFromZeta(
137:        address destinationAddress,
138:        uint256 minAmountOut,
139:        uint256 zetaTokenAmount
140:    ) external override returns (uint256) {
141:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
142:        if (zetaTokenAmount == 0) revert InputCantBeZero();
143:
144:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
145:        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
146:
147:        (address token0, address token1) = getPair(zetaToken, WETH9Address);
148:        address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
149:
150:        IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
151:            tokenIn: zetaToken,
152:            amountIn: zetaTokenAmount,
153:            amountOutMinimum: minAmountOut,
154:            pool: pairPools[0],
155:            to: destinationAddress,
156:            unwrap: true
157:        });
158:
159:        uint256 amountOut = tridentRouter.exactInputSingle(params);
160:
161:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162:
163:        return amountOut;
164:    }
```

```solidity
166:    function getTokenFromZeta(
167:        address destinationAddress,
168:        uint256 minAmountOut,
169:        address outputToken,
170:        uint256 zetaTokenAmount
171:    ) external override nonReentrant returns (uint256) {
172:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
173:        if (zetaTokenAmount == 0) revert InputCantBeZero();
174:
175:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
176:        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
177:
178:        (address token0, address token1) = getPair(zetaToken, WETH9Address);
179:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
180:
181:        (token0, token1) = getPair(WETH9Address, outputToken);
182:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
183:
184:        address[] memory path = new address[](2);
185:        path[0] = pairPools1[0];
186:        path[1] = pairPools2[0];
187:
188:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
189:            tokenIn: zetaToken,
190:            amountIn: zetaTokenAmount,
191:            amountOutMinimum: minAmountOut,
192:            path: path,
193:            to: destinationAddress,
194:            unwrap: false
195:        });
196:
197:        uint256 amountOut = tridentRouter.exactInput(params);
198:
199:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
200:        return amountOut;
201:    }
```

```solidity
166:    function getTokenFromZeta(
167:        address destinationAddress,
168:        uint256 minAmountOut,
169:        address outputToken,
170:        uint256 zetaTokenAmount
171:    ) external override nonReentrant returns (uint256) {
172:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
173:        if (zetaTokenAmount == 0) revert InputCantBeZero();
174:
175:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
176:        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
177:
178:        (address token0, address token1) = getPair(zetaToken, WETH9Address);
179:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
180:
181:        (token0, token1) = getPair(WETH9Address, outputToken);
182:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
183:
184:        address[] memory path = new address[](2);
185:        path[0] = pairPools1[0];
186:        path[1] = pairPools2[0];
187:
188:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
189:            tokenIn: zetaToken,
190:            amountIn: zetaTokenAmount,
191:            amountOutMinimum: minAmountOut,
192:            path: path,
193:            to: destinationAddress,
194:            unwrap: false
195:        });
196:
197:        uint256 amountOut = tridentRouter.exactInput(params);
198:
199:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
200:        return amountOut;
201:    }
```

```solidity
166:    function getTokenFromZeta(
167:        address destinationAddress,
168:        uint256 minAmountOut,
169:        address outputToken,
170:        uint256 zetaTokenAmount
171:    ) external override nonReentrant returns (uint256) {
172:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
173:        if (zetaTokenAmount == 0) revert InputCantBeZero();
174:
175:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
176:        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
177:
178:        (address token0, address token1) = getPair(zetaToken, WETH9Address);
179:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
180:
181:        (token0, token1) = getPair(WETH9Address, outputToken);
182:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
183:
184:        address[] memory path = new address[](2);
185:        path[0] = pairPools1[0];
186:        path[1] = pairPools2[0];
187:
188:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
189:            tokenIn: zetaToken,
190:            amountIn: zetaTokenAmount,
191:            amountOutMinimum: minAmountOut,
192:            path: path,
193:            to: destinationAddress,
194:            unwrap: false
195:        });
196:
197:        uint256 amountOut = tridentRouter.exactInput(params);
198:
199:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
200:        return amountOut;
201:    }
```

```solidity
166:    function getTokenFromZeta(
167:        address destinationAddress,
168:        uint256 minAmountOut,
169:        address outputToken,
170:        uint256 zetaTokenAmount
171:    ) external override nonReentrant returns (uint256) {
172:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
173:        if (zetaTokenAmount == 0) revert InputCantBeZero();
174:
175:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
176:        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
177:
178:        (address token0, address token1) = getPair(zetaToken, WETH9Address);
179:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
180:
181:        (token0, token1) = getPair(WETH9Address, outputToken);
182:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
183:
184:        address[] memory path = new address[](2);
185:        path[0] = pairPools1[0];
186:        path[1] = pairPools2[0];
187:
188:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
189:            tokenIn: zetaToken,
190:            amountIn: zetaTokenAmount,
191:            amountOutMinimum: minAmountOut,
192:            path: path,
193:            to: destinationAddress,
194:            unwrap: false
195:        });
196:
197:        uint256 amountOut = tridentRouter.exactInput(params);
198:
199:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
200:        return amountOut;
201:    }
```
[[ZetaTokenConsumerTrident.strategy.sol#L45-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L57)] 
[[ZetaTokenConsumerTrident.strategy.sol#L45-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L57)] 
[[ZetaTokenConsumerTrident.strategy.sol#L45-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L57)] 
[[ZetaTokenConsumerTrident.strategy.sol#L45-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L45-L57)] 
[[ZetaTokenConsumerTrident.strategy.sol#L68-L72](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L72)] 
[[ZetaTokenConsumerTrident.strategy.sol#L68-L72](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L72)] 
[[ZetaTokenConsumerTrident.strategy.sol#L74-L97](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L97)] 
[[ZetaTokenConsumerTrident.strategy.sol#L74-L97](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L97)] 
[[ZetaTokenConsumerTrident.strategy.sol#L99-L134](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L134)] 
[[ZetaTokenConsumerTrident.strategy.sol#L99-L134](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L134)] 
[[ZetaTokenConsumerTrident.strategy.sol#L99-L134](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L134)] 
[[ZetaTokenConsumerTrident.strategy.sol#L99-L134](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L134)] 
[[ZetaTokenConsumerTrident.strategy.sol#L136-L164](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L164)] 
[[ZetaTokenConsumerTrident.strategy.sol#L136-L164](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L164)] 
[[ZetaTokenConsumerTrident.strategy.sol#L136-L164](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L164)] 
[[ZetaTokenConsumerTrident.strategy.sol#L166-L201](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L201)] 
[[ZetaTokenConsumerTrident.strategy.sol#L166-L201](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L201)] 
[[ZetaTokenConsumerTrident.strategy.sol#L166-L201](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L201)] 
[[ZetaTokenConsumerTrident.strategy.sol#L166-L201](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L201)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
42:    constructor(
43:        address zetaToken_,
44:        address uniswapV3Router_,
45:        address uniswapV3Factory_,
46:        address WETH9Address_,
47:        uint24 zetaPoolFee_,
48:        uint24 tokenPoolFee_
49:    ) {
50:        if (
51:            zetaToken_ == address(0) ||
52:            uniswapV3Router_ == address(0) ||
53:            uniswapV3Factory_ == address(0) ||
54:            WETH9Address_ == address(0)
55:        ) revert ZetaCommonErrors.InvalidAddress();
56:
57:        zetaToken = zetaToken_;
58:        uniswapV3Router = ISwapRouter(uniswapV3Router_);
59:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
60:        WETH9Address = WETH9Address_;
61:        zetaPoolFee = zetaPoolFee_;
62:        tokenPoolFee = tokenPoolFee_;
63:    }
```

```solidity
42:    constructor(
43:        address zetaToken_,
44:        address uniswapV3Router_,
45:        address uniswapV3Factory_,
46:        address WETH9Address_,
47:        uint24 zetaPoolFee_,
48:        uint24 tokenPoolFee_
49:    ) {
50:        if (
51:            zetaToken_ == address(0) ||
52:            uniswapV3Router_ == address(0) ||
53:            uniswapV3Factory_ == address(0) ||
54:            WETH9Address_ == address(0)
55:        ) revert ZetaCommonErrors.InvalidAddress();
56:
57:        zetaToken = zetaToken_;
58:        uniswapV3Router = ISwapRouter(uniswapV3Router_);
59:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
60:        WETH9Address = WETH9Address_;
61:        zetaPoolFee = zetaPoolFee_;
62:        tokenPoolFee = tokenPoolFee_;
63:    }
```

```solidity
42:    constructor(
43:        address zetaToken_,
44:        address uniswapV3Router_,
45:        address uniswapV3Factory_,
46:        address WETH9Address_,
47:        uint24 zetaPoolFee_,
48:        uint24 tokenPoolFee_
49:    ) {
50:        if (
51:            zetaToken_ == address(0) ||
52:            uniswapV3Router_ == address(0) ||
53:            uniswapV3Factory_ == address(0) ||
54:            WETH9Address_ == address(0)
55:        ) revert ZetaCommonErrors.InvalidAddress();
56:
57:        zetaToken = zetaToken_;
58:        uniswapV3Router = ISwapRouter(uniswapV3Router_);
59:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
60:        WETH9Address = WETH9Address_;
61:        zetaPoolFee = zetaPoolFee_;
62:        tokenPoolFee = tokenPoolFee_;
63:    }
```

```solidity
42:    constructor(
43:        address zetaToken_,
44:        address uniswapV3Router_,
45:        address uniswapV3Factory_,
46:        address WETH9Address_,
47:        uint24 zetaPoolFee_,
48:        uint24 tokenPoolFee_
49:    ) {
50:        if (
51:            zetaToken_ == address(0) ||
52:            uniswapV3Router_ == address(0) ||
53:            uniswapV3Factory_ == address(0) ||
54:            WETH9Address_ == address(0)
55:        ) revert ZetaCommonErrors.InvalidAddress();
56:
57:        zetaToken = zetaToken_;
58:        uniswapV3Router = ISwapRouter(uniswapV3Router_);
59:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
60:        WETH9Address = WETH9Address_;
61:        zetaPoolFee = zetaPoolFee_;
62:        tokenPoolFee = tokenPoolFee_;
63:    }
```

```solidity
42:    constructor(
43:        address zetaToken_,
44:        address uniswapV3Router_,
45:        address uniswapV3Factory_,
46:        address WETH9Address_,
47:        uint24 zetaPoolFee_,
48:        uint24 tokenPoolFee_
49:    ) {
50:        if (
51:            zetaToken_ == address(0) ||
52:            uniswapV3Router_ == address(0) ||
53:            uniswapV3Factory_ == address(0) ||
54:            WETH9Address_ == address(0)
55:        ) revert ZetaCommonErrors.InvalidAddress();
56:
57:        zetaToken = zetaToken_;
58:        uniswapV3Router = ISwapRouter(uniswapV3Router_);
59:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
60:        WETH9Address = WETH9Address_;
61:        zetaPoolFee = zetaPoolFee_;
62:        tokenPoolFee = tokenPoolFee_;
63:    }
```

```solidity
42:    constructor(
43:        address zetaToken_,
44:        address uniswapV3Router_,
45:        address uniswapV3Factory_,
46:        address WETH9Address_,
47:        uint24 zetaPoolFee_,
48:        uint24 tokenPoolFee_
49:    ) {
50:        if (
51:            zetaToken_ == address(0) ||
52:            uniswapV3Router_ == address(0) ||
53:            uniswapV3Factory_ == address(0) ||
54:            WETH9Address_ == address(0)
55:        ) revert ZetaCommonErrors.InvalidAddress();
56:
57:        zetaToken = zetaToken_;
58:        uniswapV3Router = ISwapRouter(uniswapV3Router_);
59:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
60:        WETH9Address = WETH9Address_;
61:        zetaPoolFee = zetaPoolFee_;
62:        tokenPoolFee = tokenPoolFee_;
63:    }
```

```solidity
74:    function getZetaFromEth(
75:        address destinationAddress,
76:        uint256 minAmountOut
77:    ) external payable override returns (uint256) {
78:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
79:        if (msg.value == 0) revert InputCantBeZero();
80:
81:        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
82:            deadline: block.timestamp + MAX_DEADLINE,
83:            tokenIn: WETH9Address,
84:            tokenOut: zetaToken,
85:            fee: zetaPoolFee,
86:            recipient: destinationAddress,
87:            amountIn: msg.value,
88:            amountOutMinimum: minAmountOut,
89:            sqrtPriceLimitX96: 0
90:        });
91:
92:        uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);
93:
94:        emit EthExchangedForZeta(msg.value, amountOut);
95:        return amountOut;
96:    }
```

```solidity
74:    function getZetaFromEth(
75:        address destinationAddress,
76:        uint256 minAmountOut
77:    ) external payable override returns (uint256) {
78:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
79:        if (msg.value == 0) revert InputCantBeZero();
80:
81:        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
82:            deadline: block.timestamp + MAX_DEADLINE,
83:            tokenIn: WETH9Address,
84:            tokenOut: zetaToken,
85:            fee: zetaPoolFee,
86:            recipient: destinationAddress,
87:            amountIn: msg.value,
88:            amountOutMinimum: minAmountOut,
89:            sqrtPriceLimitX96: 0
90:        });
91:
92:        uint256 amountOut = uniswapV3Router.exactInputSingle{value: msg.value}(params);
93:
94:        emit EthExchangedForZeta(msg.value, amountOut);
95:        return amountOut;
96:    }
```

```solidity
98:    function getZetaFromToken(
99:        address destinationAddress,
100:        uint256 minAmountOut,
101:        address inputToken,
102:        uint256 inputTokenAmount
103:    ) external override returns (uint256) {
104:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:        if (inputTokenAmount == 0) revert InputCantBeZero();
106:
107:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
108:        IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);
109:
110:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:            deadline: block.timestamp + MAX_DEADLINE,
112:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
113:            recipient: destinationAddress,
114:            amountIn: inputTokenAmount,
115:            amountOutMinimum: minAmountOut
116:        });
117:
118:        uint256 amountOut = uniswapV3Router.exactInput(params);
119:
120:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121:        return amountOut;
122:    }
```

```solidity
98:    function getZetaFromToken(
99:        address destinationAddress,
100:        uint256 minAmountOut,
101:        address inputToken,
102:        uint256 inputTokenAmount
103:    ) external override returns (uint256) {
104:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:        if (inputTokenAmount == 0) revert InputCantBeZero();
106:
107:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
108:        IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);
109:
110:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:            deadline: block.timestamp + MAX_DEADLINE,
112:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
113:            recipient: destinationAddress,
114:            amountIn: inputTokenAmount,
115:            amountOutMinimum: minAmountOut
116:        });
117:
118:        uint256 amountOut = uniswapV3Router.exactInput(params);
119:
120:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121:        return amountOut;
122:    }
```

```solidity
98:    function getZetaFromToken(
99:        address destinationAddress,
100:        uint256 minAmountOut,
101:        address inputToken,
102:        uint256 inputTokenAmount
103:    ) external override returns (uint256) {
104:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:        if (inputTokenAmount == 0) revert InputCantBeZero();
106:
107:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
108:        IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);
109:
110:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:            deadline: block.timestamp + MAX_DEADLINE,
112:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
113:            recipient: destinationAddress,
114:            amountIn: inputTokenAmount,
115:            amountOutMinimum: minAmountOut
116:        });
117:
118:        uint256 amountOut = uniswapV3Router.exactInput(params);
119:
120:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121:        return amountOut;
122:    }
```

```solidity
98:    function getZetaFromToken(
99:        address destinationAddress,
100:        uint256 minAmountOut,
101:        address inputToken,
102:        uint256 inputTokenAmount
103:    ) external override returns (uint256) {
104:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:        if (inputTokenAmount == 0) revert InputCantBeZero();
106:
107:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
108:        IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);
109:
110:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:            deadline: block.timestamp + MAX_DEADLINE,
112:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
113:            recipient: destinationAddress,
114:            amountIn: inputTokenAmount,
115:            amountOutMinimum: minAmountOut
116:        });
117:
118:        uint256 amountOut = uniswapV3Router.exactInput(params);
119:
120:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121:        return amountOut;
122:    }
```

```solidity
124:    function getEthFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        uint256 zetaTokenAmount
128:    ) external override returns (uint256) {
129:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
130:        if (zetaTokenAmount == 0) revert InputCantBeZero();
131:
132:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
133:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
134:
135:        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
136:            deadline: block.timestamp + MAX_DEADLINE,
137:            tokenIn: zetaToken,
138:            tokenOut: WETH9Address,
139:            fee: zetaPoolFee,
140:            recipient: address(this),
141:            amountIn: zetaTokenAmount,
142:            amountOutMinimum: minAmountOut,
143:            sqrtPriceLimitX96: 0
144:        });
145:
146:        uint256 amountOut = uniswapV3Router.exactInputSingle(params);
147:
148:        WETH9(WETH9Address).withdraw(amountOut);
149:
150:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151:
152:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
153:        if (!sent) revert ErrorSendingETH();
154:
155:        return amountOut;
156:    }
```

```solidity
124:    function getEthFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        uint256 zetaTokenAmount
128:    ) external override returns (uint256) {
129:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
130:        if (zetaTokenAmount == 0) revert InputCantBeZero();
131:
132:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
133:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
134:
135:        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
136:            deadline: block.timestamp + MAX_DEADLINE,
137:            tokenIn: zetaToken,
138:            tokenOut: WETH9Address,
139:            fee: zetaPoolFee,
140:            recipient: address(this),
141:            amountIn: zetaTokenAmount,
142:            amountOutMinimum: minAmountOut,
143:            sqrtPriceLimitX96: 0
144:        });
145:
146:        uint256 amountOut = uniswapV3Router.exactInputSingle(params);
147:
148:        WETH9(WETH9Address).withdraw(amountOut);
149:
150:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151:
152:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
153:        if (!sent) revert ErrorSendingETH();
154:
155:        return amountOut;
156:    }
```

```solidity
124:    function getEthFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        uint256 zetaTokenAmount
128:    ) external override returns (uint256) {
129:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
130:        if (zetaTokenAmount == 0) revert InputCantBeZero();
131:
132:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
133:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
134:
135:        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
136:            deadline: block.timestamp + MAX_DEADLINE,
137:            tokenIn: zetaToken,
138:            tokenOut: WETH9Address,
139:            fee: zetaPoolFee,
140:            recipient: address(this),
141:            amountIn: zetaTokenAmount,
142:            amountOutMinimum: minAmountOut,
143:            sqrtPriceLimitX96: 0
144:        });
145:
146:        uint256 amountOut = uniswapV3Router.exactInputSingle(params);
147:
148:        WETH9(WETH9Address).withdraw(amountOut);
149:
150:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151:
152:        (bool sent, ) = destinationAddress.call{value: amountOut}("");
153:        if (!sent) revert ErrorSendingETH();
154:
155:        return amountOut;
156:    }
```

```solidity
158:    function getTokenFromZeta(
159:        address destinationAddress,
160:        uint256 minAmountOut,
161:        address outputToken,
162:        uint256 zetaTokenAmount
163:    ) external override nonReentrant returns (uint256) {
164:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
165:        if (zetaTokenAmount == 0) revert InputCantBeZero();
166:
167:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
168:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
169:
170:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
171:            deadline: block.timestamp + MAX_DEADLINE,
172:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
173:            recipient: destinationAddress,
174:            amountIn: zetaTokenAmount,
175:            amountOutMinimum: minAmountOut
176:        });
177:
178:        uint256 amountOut = uniswapV3Router.exactInput(params);
179:
180:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
181:        return amountOut;
182:    }
```

```solidity
158:    function getTokenFromZeta(
159:        address destinationAddress,
160:        uint256 minAmountOut,
161:        address outputToken,
162:        uint256 zetaTokenAmount
163:    ) external override nonReentrant returns (uint256) {
164:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
165:        if (zetaTokenAmount == 0) revert InputCantBeZero();
166:
167:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
168:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
169:
170:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
171:            deadline: block.timestamp + MAX_DEADLINE,
172:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
173:            recipient: destinationAddress,
174:            amountIn: zetaTokenAmount,
175:            amountOutMinimum: minAmountOut
176:        });
177:
178:        uint256 amountOut = uniswapV3Router.exactInput(params);
179:
180:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
181:        return amountOut;
182:    }
```

```solidity
158:    function getTokenFromZeta(
159:        address destinationAddress,
160:        uint256 minAmountOut,
161:        address outputToken,
162:        uint256 zetaTokenAmount
163:    ) external override nonReentrant returns (uint256) {
164:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
165:        if (zetaTokenAmount == 0) revert InputCantBeZero();
166:
167:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
168:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
169:
170:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
171:            deadline: block.timestamp + MAX_DEADLINE,
172:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
173:            recipient: destinationAddress,
174:            amountIn: zetaTokenAmount,
175:            amountOutMinimum: minAmountOut
176:        });
177:
178:        uint256 amountOut = uniswapV3Router.exactInput(params);
179:
180:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
181:        return amountOut;
182:    }
```

```solidity
158:    function getTokenFromZeta(
159:        address destinationAddress,
160:        uint256 minAmountOut,
161:        address outputToken,
162:        uint256 zetaTokenAmount
163:    ) external override nonReentrant returns (uint256) {
164:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
165:        if (zetaTokenAmount == 0) revert InputCantBeZero();
166:
167:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
168:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
169:
170:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
171:            deadline: block.timestamp + MAX_DEADLINE,
172:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
173:            recipient: destinationAddress,
174:            amountIn: zetaTokenAmount,
175:            amountOutMinimum: minAmountOut
176:        });
177:
178:        uint256 amountOut = uniswapV3Router.exactInput(params);
179:
180:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
181:        return amountOut;
182:    }
```
[[ZetaTokenConsumerUniV3.strategy.sol#L42-L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L63)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L42-L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L63)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L42-L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L63)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L42-L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L63)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L42-L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L63)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L42-L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L63)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L74-L96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L96)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L74-L96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L96)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L98-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L122)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L98-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L122)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L98-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L122)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L98-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L122)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L124-L156](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L156)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L124-L156](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L156)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L124-L156](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L156)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L158-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L182)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L158-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L182)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L158-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L182)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L158-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L182)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
68:    constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
69:        TSSAddress = TSSAddress_;
70:        TSSAddressUpdater = TSSAddressUpdater_;
71:        zetaFee = zetaFee_;
72:        zeta = zeta_;
73:        zetaMaxFee = zetaMaxFee_;
74:    }
```

```solidity
68:    constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
69:        TSSAddress = TSSAddress_;
70:        TSSAddressUpdater = TSSAddressUpdater_;
71:        zetaFee = zetaFee_;
72:        zeta = zeta_;
73:        zetaMaxFee = zetaMaxFee_;
74:    }
```

```solidity
68:    constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
69:        TSSAddress = TSSAddress_;
70:        TSSAddressUpdater = TSSAddressUpdater_;
71:        zetaFee = zetaFee_;
72:        zeta = zeta_;
73:        zetaMaxFee = zetaMaxFee_;
74:    }
```
[[ERC20Custody.sol#L68-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74)] 
[[ERC20Custody.sol#L68-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74)] 
[[ERC20Custody.sol#L68-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
26:    constructor(address zetaToken_, address uniswapV2Router_) {
27:        if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
28:
29:        zetaToken = zetaToken_;
30:        uniswapV2Router = IUniswapV2Router02(uniswapV2Router_);
31:        wETH = IUniswapV2Router02(uniswapV2Router_).WETH();
32:    }
```

```solidity
26:    constructor(address zetaToken_, address uniswapV2Router_) {
27:        if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
28:
29:        zetaToken = zetaToken_;
30:        uniswapV2Router = IUniswapV2Router02(uniswapV2Router_);
31:        wETH = IUniswapV2Router02(uniswapV2Router_).WETH();
32:    }
```

```solidity
34:    function getZetaFromEth(
35:        address destinationAddress,
36:        uint256 minAmountOut
37:    ) external payable override returns (uint256) {
38:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
39:        if (msg.value == 0) revert InputCantBeZero();
40:
41:        address[] memory path = new address[](2);
42:        path[0] = wETH;
43:        path[1] = zetaToken;
44:
45:        uint256[] memory amounts = uniswapV2Router.swapExactETHForTokens{value: msg.value}(
46:            minAmountOut,
47:            path,
48:            destinationAddress,
49:            block.timestamp + MAX_DEADLINE
50:        );
51:
52:        uint256 amountOut = amounts[path.length - 1];
53:
54:        emit EthExchangedForZeta(msg.value, amountOut);
55:        return amountOut;
56:    }
```

```solidity
34:    function getZetaFromEth(
35:        address destinationAddress,
36:        uint256 minAmountOut
37:    ) external payable override returns (uint256) {
38:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
39:        if (msg.value == 0) revert InputCantBeZero();
40:
41:        address[] memory path = new address[](2);
42:        path[0] = wETH;
43:        path[1] = zetaToken;
44:
45:        uint256[] memory amounts = uniswapV2Router.swapExactETHForTokens{value: msg.value}(
46:            minAmountOut,
47:            path,
48:            destinationAddress,
49:            block.timestamp + MAX_DEADLINE
50:        );
51:
52:        uint256 amountOut = amounts[path.length - 1];
53:
54:        emit EthExchangedForZeta(msg.value, amountOut);
55:        return amountOut;
56:    }
```

```solidity
58:    function getZetaFromToken(
59:        address destinationAddress,
60:        uint256 minAmountOut,
61:        address inputToken,
62:        uint256 inputTokenAmount
63:    ) external override returns (uint256) {
64:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:        if (inputTokenAmount == 0) revert InputCantBeZero();
66:
67:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
68:        IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);
69:
70:        address[] memory path;
71:        if (inputToken == wETH) {
72:            path = new address[](2);
73:            path[0] = wETH;
74:            path[1] = zetaToken;
75:        } else {
76:            path = new address[](3);
77:            path[0] = inputToken;
78:            path[1] = wETH;
79:            path[2] = zetaToken;
80:        }
81:
82:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:            inputTokenAmount,
84:            minAmountOut,
85:            path,
86:            destinationAddress,
87:            block.timestamp + MAX_DEADLINE
88:        );
89:        uint256 amountOut = amounts[path.length - 1];
90:
91:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92:        return amountOut;
93:    }
```

```solidity
58:    function getZetaFromToken(
59:        address destinationAddress,
60:        uint256 minAmountOut,
61:        address inputToken,
62:        uint256 inputTokenAmount
63:    ) external override returns (uint256) {
64:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:        if (inputTokenAmount == 0) revert InputCantBeZero();
66:
67:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
68:        IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);
69:
70:        address[] memory path;
71:        if (inputToken == wETH) {
72:            path = new address[](2);
73:            path[0] = wETH;
74:            path[1] = zetaToken;
75:        } else {
76:            path = new address[](3);
77:            path[0] = inputToken;
78:            path[1] = wETH;
79:            path[2] = zetaToken;
80:        }
81:
82:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:            inputTokenAmount,
84:            minAmountOut,
85:            path,
86:            destinationAddress,
87:            block.timestamp + MAX_DEADLINE
88:        );
89:        uint256 amountOut = amounts[path.length - 1];
90:
91:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92:        return amountOut;
93:    }
```

```solidity
58:    function getZetaFromToken(
59:        address destinationAddress,
60:        uint256 minAmountOut,
61:        address inputToken,
62:        uint256 inputTokenAmount
63:    ) external override returns (uint256) {
64:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:        if (inputTokenAmount == 0) revert InputCantBeZero();
66:
67:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
68:        IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);
69:
70:        address[] memory path;
71:        if (inputToken == wETH) {
72:            path = new address[](2);
73:            path[0] = wETH;
74:            path[1] = zetaToken;
75:        } else {
76:            path = new address[](3);
77:            path[0] = inputToken;
78:            path[1] = wETH;
79:            path[2] = zetaToken;
80:        }
81:
82:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:            inputTokenAmount,
84:            minAmountOut,
85:            path,
86:            destinationAddress,
87:            block.timestamp + MAX_DEADLINE
88:        );
89:        uint256 amountOut = amounts[path.length - 1];
90:
91:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92:        return amountOut;
93:    }
```

```solidity
58:    function getZetaFromToken(
59:        address destinationAddress,
60:        uint256 minAmountOut,
61:        address inputToken,
62:        uint256 inputTokenAmount
63:    ) external override returns (uint256) {
64:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:        if (inputTokenAmount == 0) revert InputCantBeZero();
66:
67:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
68:        IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);
69:
70:        address[] memory path;
71:        if (inputToken == wETH) {
72:            path = new address[](2);
73:            path[0] = wETH;
74:            path[1] = zetaToken;
75:        } else {
76:            path = new address[](3);
77:            path[0] = inputToken;
78:            path[1] = wETH;
79:            path[2] = zetaToken;
80:        }
81:
82:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:            inputTokenAmount,
84:            minAmountOut,
85:            path,
86:            destinationAddress,
87:            block.timestamp + MAX_DEADLINE
88:        );
89:        uint256 amountOut = amounts[path.length - 1];
90:
91:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92:        return amountOut;
93:    }
```

```solidity
95:    function getEthFromZeta(
96:        address destinationAddress,
97:        uint256 minAmountOut,
98:        uint256 zetaTokenAmount
99:    ) external override returns (uint256) {
100:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
101:        if (zetaTokenAmount == 0) revert InputCantBeZero();
102:
103:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
104:        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
105:
106:        address[] memory path = new address[](2);
107:        path[0] = zetaToken;
108:        path[1] = wETH;
109:
110:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForETH(
111:            zetaTokenAmount,
112:            minAmountOut,
113:            path,
114:            destinationAddress,
115:            block.timestamp + MAX_DEADLINE
116:        );
117:
118:        uint256 amountOut = amounts[path.length - 1];
119:
120:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121:        return amountOut;
122:    }
```

```solidity
95:    function getEthFromZeta(
96:        address destinationAddress,
97:        uint256 minAmountOut,
98:        uint256 zetaTokenAmount
99:    ) external override returns (uint256) {
100:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
101:        if (zetaTokenAmount == 0) revert InputCantBeZero();
102:
103:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
104:        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
105:
106:        address[] memory path = new address[](2);
107:        path[0] = zetaToken;
108:        path[1] = wETH;
109:
110:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForETH(
111:            zetaTokenAmount,
112:            minAmountOut,
113:            path,
114:            destinationAddress,
115:            block.timestamp + MAX_DEADLINE
116:        );
117:
118:        uint256 amountOut = amounts[path.length - 1];
119:
120:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121:        return amountOut;
122:    }
```

```solidity
95:    function getEthFromZeta(
96:        address destinationAddress,
97:        uint256 minAmountOut,
98:        uint256 zetaTokenAmount
99:    ) external override returns (uint256) {
100:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
101:        if (zetaTokenAmount == 0) revert InputCantBeZero();
102:
103:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
104:        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
105:
106:        address[] memory path = new address[](2);
107:        path[0] = zetaToken;
108:        path[1] = wETH;
109:
110:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForETH(
111:            zetaTokenAmount,
112:            minAmountOut,
113:            path,
114:            destinationAddress,
115:            block.timestamp + MAX_DEADLINE
116:        );
117:
118:        uint256 amountOut = amounts[path.length - 1];
119:
120:        emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121:        return amountOut;
122:    }
```

```solidity
124:    function getTokenFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        address outputToken,
128:        uint256 zetaTokenAmount
129:    ) external override returns (uint256) {
130:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
131:        if (zetaTokenAmount == 0) revert InputCantBeZero();
132:
133:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
134:        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
135:
136:        address[] memory path;
137:        if (outputToken == wETH) {
138:            path = new address[](2);
139:            path[0] = zetaToken;
140:            path[1] = wETH;
141:        } else {
142:            path = new address[](3);
143:            path[0] = zetaToken;
144:            path[1] = wETH;
145:            path[2] = outputToken;
146:        }
147:
148:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
149:            zetaTokenAmount,
150:            minAmountOut,
151:            path,
152:            destinationAddress,
153:            block.timestamp + MAX_DEADLINE
154:        );
155:
156:        uint256 amountOut = amounts[path.length - 1];
157:
158:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
159:        return amountOut;
160:    }
```

```solidity
124:    function getTokenFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        address outputToken,
128:        uint256 zetaTokenAmount
129:    ) external override returns (uint256) {
130:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
131:        if (zetaTokenAmount == 0) revert InputCantBeZero();
132:
133:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
134:        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
135:
136:        address[] memory path;
137:        if (outputToken == wETH) {
138:            path = new address[](2);
139:            path[0] = zetaToken;
140:            path[1] = wETH;
141:        } else {
142:            path = new address[](3);
143:            path[0] = zetaToken;
144:            path[1] = wETH;
145:            path[2] = outputToken;
146:        }
147:
148:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
149:            zetaTokenAmount,
150:            minAmountOut,
151:            path,
152:            destinationAddress,
153:            block.timestamp + MAX_DEADLINE
154:        );
155:
156:        uint256 amountOut = amounts[path.length - 1];
157:
158:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
159:        return amountOut;
160:    }
```

```solidity
124:    function getTokenFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        address outputToken,
128:        uint256 zetaTokenAmount
129:    ) external override returns (uint256) {
130:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
131:        if (zetaTokenAmount == 0) revert InputCantBeZero();
132:
133:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
134:        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
135:
136:        address[] memory path;
137:        if (outputToken == wETH) {
138:            path = new address[](2);
139:            path[0] = zetaToken;
140:            path[1] = wETH;
141:        } else {
142:            path = new address[](3);
143:            path[0] = zetaToken;
144:            path[1] = wETH;
145:            path[2] = outputToken;
146:        }
147:
148:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
149:            zetaTokenAmount,
150:            minAmountOut,
151:            path,
152:            destinationAddress,
153:            block.timestamp + MAX_DEADLINE
154:        );
155:
156:        uint256 amountOut = amounts[path.length - 1];
157:
158:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
159:        return amountOut;
160:    }
```

```solidity
124:    function getTokenFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        address outputToken,
128:        uint256 zetaTokenAmount
129:    ) external override returns (uint256) {
130:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
131:        if (zetaTokenAmount == 0) revert InputCantBeZero();
132:
133:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
134:        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
135:
136:        address[] memory path;
137:        if (outputToken == wETH) {
138:            path = new address[](2);
139:            path[0] = zetaToken;
140:            path[1] = wETH;
141:        } else {
142:            path = new address[](3);
143:            path[0] = zetaToken;
144:            path[1] = wETH;
145:            path[2] = outputToken;
146:        }
147:
148:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
149:            zetaTokenAmount,
150:            minAmountOut,
151:            path,
152:            destinationAddress,
153:            block.timestamp + MAX_DEADLINE
154:        );
155:
156:        uint256 amountOut = amounts[path.length - 1];
157:
158:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
159:        return amountOut;
160:    }
```
[[ZetaTokenConsumerUniV2.strategy.sol#L26-L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26-L32)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L26-L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L26-L32)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L34-L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34-L56)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L34-L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34-L56)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L58-L93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L93)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L58-L93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L93)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L58-L93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L93)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L58-L93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L93)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L95-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L122)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L95-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L122)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L95-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L122)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L124-L160](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L160)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L124-L160](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L160)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L124-L160](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L160)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L124-L160](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L160)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
74:    constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
75:        if (
76:            zetaToken_ == address(0) ||
77:            tssAddress_ == address(0) ||
78:            tssAddressUpdater_ == address(0) ||
79:            pauserAddress_ == address(0)
80:        ) {
81:            revert ZetaCommonErrors.InvalidAddress();
82:        }
83:
84:        zetaToken = zetaToken_;
85:        tssAddress = tssAddress_;
86:        tssAddressUpdater = tssAddressUpdater_;
87:        pauserAddress = pauserAddress_;
88:    }
```

```solidity
74:    constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
75:        if (
76:            zetaToken_ == address(0) ||
77:            tssAddress_ == address(0) ||
78:            tssAddressUpdater_ == address(0) ||
79:            pauserAddress_ == address(0)
80:        ) {
81:            revert ZetaCommonErrors.InvalidAddress();
82:        }
83:
84:        zetaToken = zetaToken_;
85:        tssAddress = tssAddress_;
86:        tssAddressUpdater = tssAddressUpdater_;
87:        pauserAddress = pauserAddress_;
88:    }
```

```solidity
74:    constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
75:        if (
76:            zetaToken_ == address(0) ||
77:            tssAddress_ == address(0) ||
78:            tssAddressUpdater_ == address(0) ||
79:            pauserAddress_ == address(0)
80:        ) {
81:            revert ZetaCommonErrors.InvalidAddress();
82:        }
83:
84:        zetaToken = zetaToken_;
85:        tssAddress = tssAddress_;
86:        tssAddressUpdater = tssAddressUpdater_;
87:        pauserAddress = pauserAddress_;
88:    }
```

```solidity
74:    constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
75:        if (
76:            zetaToken_ == address(0) ||
77:            tssAddress_ == address(0) ||
78:            tssAddressUpdater_ == address(0) ||
79:            pauserAddress_ == address(0)
80:        ) {
81:            revert ZetaCommonErrors.InvalidAddress();
82:        }
83:
84:        zetaToken = zetaToken_;
85:        tssAddress = tssAddress_;
86:        tssAddressUpdater = tssAddressUpdater_;
87:        pauserAddress = pauserAddress_;
88:    }
```

```solidity
117:    function updatePauserAddress(address pauserAddress_) external onlyPauser {
118:        if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
119:
120:        pauserAddress = pauserAddress_;
121:
122:        emit PauserAddressUpdated(msg.sender, pauserAddress_);
123:    }
```

```solidity
128:    function updateTssAddress(address tssAddress_) external {
129:        if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender);
130:        if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
131:
132:        tssAddress = tssAddress_;
133:
134:        emit TSSAddressUpdated(msg.sender, tssAddress_);
135:    }
```

```solidity
166:    function send(ZetaInterfaces.SendInput calldata input) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```
[[ZetaConnector.base.sol#L74-L88](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74-L88)] 
[[ZetaConnector.base.sol#L74-L88](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74-L88)] 
[[ZetaConnector.base.sol#L74-L88](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74-L88)] 
[[ZetaConnector.base.sol#L74-L88](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74-L88)] 
[[ZetaConnector.base.sol#L117-L123](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L117-L123)] 
[[ZetaConnector.base.sol#L128-L135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L128-L135)] 
[[ZetaConnector.base.sol#L166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
51:    constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
52:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
53:        wZetaContractAddress = wzeta_;
54:        uniswapv2FactoryAddress = uniswapv2Factory_;
55:        uniswapv2Router02Address = uniswapv2Router02_;
56:        emit SystemContractDeployed();
57:    }
```

```solidity
51:    constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
52:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
53:        wZetaContractAddress = wzeta_;
54:        uniswapv2FactoryAddress = uniswapv2Factory_;
55:        uniswapv2Router02Address = uniswapv2Router02_;
56:        emit SystemContractDeployed();
57:    }
```

```solidity
51:    constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
52:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
53:        wZetaContractAddress = wzeta_;
54:        uniswapv2FactoryAddress = uniswapv2Factory_;
55:        uniswapv2Router02Address = uniswapv2Router02_;
56:        emit SystemContractDeployed();
57:    }
```
[[SystemContract.sol#L51-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51-L57)] 
[[SystemContract.sol#L51-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51-L57)] 
[[SystemContract.sol#L51-L57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51-L57)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
20:    constructor(
21:        address zetaTokenAddress_,
22:        address tssAddress_,
23:        address tssAddressUpdater_,
24:        address pauserAddress_
25:    ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

```solidity
20:    constructor(
21:        address zetaTokenAddress_,
22:        address tssAddress_,
23:        address tssAddressUpdater_,
24:        address pauserAddress_
25:    ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

```solidity
20:    constructor(
21:        address zetaTokenAddress_,
22:        address tssAddress_,
23:        address tssAddressUpdater_,
24:        address pauserAddress_
25:    ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

```solidity
20:    constructor(
21:        address zetaTokenAddress_,
22:        address tssAddress_,
23:        address tssAddressUpdater_,
24:        address pauserAddress_
25:    ) ZetaConnectorBase(zetaTokenAddress_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

```solidity
31:    function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
32:        maxSupply = maxSupply_;
33:        emit MaxSupplyUpdated(msg.sender, maxSupply_);
34:    }
```

```solidity
40:    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
41:        ZetaNonEthInterface(zetaToken).burnFrom(msg.sender, input.zetaValueAndGas);
42:
43:        emit ZetaSent(
44:            tx.origin,
45:            msg.sender,
46:            input.destinationChainId,
47:            input.destinationAddress,
48:            input.zetaValueAndGas,
49:            input.destinationGasLimit,
50:            input.message,
51:            input.zetaParams
52:        );
53:    }
```

```solidity
61:    function onReceive(
62:        bytes calldata zetaTxSenderAddress,
63:        uint256 sourceChainId,
64:        address destinationAddress,
65:        uint256 zetaValue,
66:        bytes calldata message,
67:        bytes32 internalSendHash
68:    ) external override onlyTssAddress {
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71:
72:        if (message.length > 0) {
73:            ZetaReceiver(destinationAddress).onZetaMessage(
74:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:            );
76:        }
77:
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79:    }
```

```solidity
61:    function onReceive(
62:        bytes calldata zetaTxSenderAddress,
63:        uint256 sourceChainId,
64:        address destinationAddress,
65:        uint256 zetaValue,
66:        bytes calldata message,
67:        bytes32 internalSendHash
68:    ) external override onlyTssAddress {
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71:
72:        if (message.length > 0) {
73:            ZetaReceiver(destinationAddress).onZetaMessage(
74:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:            );
76:        }
77:
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79:    }
```

```solidity
61:    function onReceive(
62:        bytes calldata zetaTxSenderAddress,
63:        uint256 sourceChainId,
64:        address destinationAddress,
65:        uint256 zetaValue,
66:        bytes calldata message,
67:        bytes32 internalSendHash
68:    ) external override onlyTssAddress {
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71:
72:        if (message.length > 0) {
73:            ZetaReceiver(destinationAddress).onZetaMessage(
74:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:            );
76:        }
77:
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79:    }
```

```solidity
61:    function onReceive(
62:        bytes calldata zetaTxSenderAddress,
63:        uint256 sourceChainId,
64:        address destinationAddress,
65:        uint256 zetaValue,
66:        bytes calldata message,
67:        bytes32 internalSendHash
68:    ) external override onlyTssAddress {
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71:
72:        if (message.length > 0) {
73:            ZetaReceiver(destinationAddress).onZetaMessage(
74:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:            );
76:        }
77:
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79:    }
```

```solidity
61:    function onReceive(
62:        bytes calldata zetaTxSenderAddress,
63:        uint256 sourceChainId,
64:        address destinationAddress,
65:        uint256 zetaValue,
66:        bytes calldata message,
67:        bytes32 internalSendHash
68:    ) external override onlyTssAddress {
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71:
72:        if (message.length > 0) {
73:            ZetaReceiver(destinationAddress).onZetaMessage(
74:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:            );
76:        }
77:
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79:    }
```

```solidity
61:    function onReceive(
62:        bytes calldata zetaTxSenderAddress,
63:        uint256 sourceChainId,
64:        address destinationAddress,
65:        uint256 zetaValue,
66:        bytes calldata message,
67:        bytes32 internalSendHash
68:    ) external override onlyTssAddress {
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71:
72:        if (message.length > 0) {
73:            ZetaReceiver(destinationAddress).onZetaMessage(
74:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:            );
76:        }
77:
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```
[[ZetaConnector.non-eth.sol#L20-L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25)] 
[[ZetaConnector.non-eth.sol#L20-L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25)] 
[[ZetaConnector.non-eth.sol#L20-L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25)] 
[[ZetaConnector.non-eth.sol#L20-L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L20-L25)] 
[[ZetaConnector.non-eth.sol#L31-L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31-L34)] 
[[ZetaConnector.non-eth.sol#L40-L53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40-L53)] 
[[ZetaConnector.non-eth.sol#L61-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79)] 
[[ZetaConnector.non-eth.sol#L61-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79)] 
[[ZetaConnector.non-eth.sol#L61-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79)] 
[[ZetaConnector.non-eth.sol#L61-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79)] 
[[ZetaConnector.non-eth.sol#L61-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79)] 
[[ZetaConnector.non-eth.sol#L61-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
16:    constructor(
17:        address zetaToken_,
18:        address tssAddress_,
19:        address tssAddressUpdater_,
20:        address pauserAddress_
21:    ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

```solidity
16:    constructor(
17:        address zetaToken_,
18:        address tssAddress_,
19:        address tssAddressUpdater_,
20:        address pauserAddress_
21:    ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

```solidity
16:    constructor(
17:        address zetaToken_,
18:        address tssAddress_,
19:        address tssAddressUpdater_,
20:        address pauserAddress_
21:    ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

```solidity
16:    constructor(
17:        address zetaToken_,
18:        address tssAddress_,
19:        address tssAddressUpdater_,
20:        address pauserAddress_
21:    ) ZetaConnectorBase(zetaToken_, tssAddress_, tssAddressUpdater_, pauserAddress_) {}
```

```solidity
31:    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
32:        bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas);
33:        if (!success) revert ZetaTransferError();
34:
35:        emit ZetaSent(
36:            tx.origin,
37:            msg.sender,
38:            input.destinationChainId,
39:            input.destinationAddress,
40:            input.zetaValueAndGas,
41:            input.destinationGasLimit,
42:            input.message,
43:            input.zetaParams
44:        );
45:    }
```

```solidity
52:    function onReceive(
53:        bytes calldata zetaTxSenderAddress,
54:        uint256 sourceChainId,
55:        address destinationAddress,
56:        uint256 zetaValue,
57:        bytes calldata message,
58:        bytes32 internalSendHash
59:    ) external override onlyTssAddress {
60:        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:        if (!success) revert ZetaTransferError();
62:
63:        if (message.length > 0) {
64:            ZetaReceiver(destinationAddress).onZetaMessage(
65:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:            );
67:        }
68:
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70:    }
```

```solidity
52:    function onReceive(
53:        bytes calldata zetaTxSenderAddress,
54:        uint256 sourceChainId,
55:        address destinationAddress,
56:        uint256 zetaValue,
57:        bytes calldata message,
58:        bytes32 internalSendHash
59:    ) external override onlyTssAddress {
60:        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:        if (!success) revert ZetaTransferError();
62:
63:        if (message.length > 0) {
64:            ZetaReceiver(destinationAddress).onZetaMessage(
65:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:            );
67:        }
68:
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70:    }
```

```solidity
52:    function onReceive(
53:        bytes calldata zetaTxSenderAddress,
54:        uint256 sourceChainId,
55:        address destinationAddress,
56:        uint256 zetaValue,
57:        bytes calldata message,
58:        bytes32 internalSendHash
59:    ) external override onlyTssAddress {
60:        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:        if (!success) revert ZetaTransferError();
62:
63:        if (message.length > 0) {
64:            ZetaReceiver(destinationAddress).onZetaMessage(
65:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:            );
67:        }
68:
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70:    }
```

```solidity
52:    function onReceive(
53:        bytes calldata zetaTxSenderAddress,
54:        uint256 sourceChainId,
55:        address destinationAddress,
56:        uint256 zetaValue,
57:        bytes calldata message,
58:        bytes32 internalSendHash
59:    ) external override onlyTssAddress {
60:        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:        if (!success) revert ZetaTransferError();
62:
63:        if (message.length > 0) {
64:            ZetaReceiver(destinationAddress).onZetaMessage(
65:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:            );
67:        }
68:
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70:    }
```

```solidity
52:    function onReceive(
53:        bytes calldata zetaTxSenderAddress,
54:        uint256 sourceChainId,
55:        address destinationAddress,
56:        uint256 zetaValue,
57:        bytes calldata message,
58:        bytes32 internalSendHash
59:    ) external override onlyTssAddress {
60:        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:        if (!success) revert ZetaTransferError();
62:
63:        if (message.length > 0) {
64:            ZetaReceiver(destinationAddress).onZetaMessage(
65:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:            );
67:        }
68:
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70:    }
```

```solidity
52:    function onReceive(
53:        bytes calldata zetaTxSenderAddress,
54:        uint256 sourceChainId,
55:        address destinationAddress,
56:        uint256 zetaValue,
57:        bytes calldata message,
58:        bytes32 internalSendHash
59:    ) external override onlyTssAddress {
60:        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:        if (!success) revert ZetaTransferError();
62:
63:        if (message.length > 0) {
64:            ZetaReceiver(destinationAddress).onZetaMessage(
65:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:            );
67:        }
68:
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```
[[ZetaConnector.eth.sol#L16-L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21)] 
[[ZetaConnector.eth.sol#L16-L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21)] 
[[ZetaConnector.eth.sol#L16-L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21)] 
[[ZetaConnector.eth.sol#L16-L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L16-L21)] 
[[ZetaConnector.eth.sol#L31-L45](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31-L45)] 
[[ZetaConnector.eth.sol#L52-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70)] 
[[ZetaConnector.eth.sol#L52-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70)] 
[[ZetaConnector.eth.sol#L52-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70)] 
[[ZetaConnector.eth.sol#L52-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70)] 
[[ZetaConnector.eth.sol#L52-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70)] 
[[ZetaConnector.eth.sol#L52-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
25:    function withdraw(uint wad) public {
26:        require(balanceOf[msg.sender] >= wad);
27:        balanceOf[msg.sender] -= wad;
28:        msg.sender.transfer(wad);
29:        Withdrawal(msg.sender, wad);
30:    }
```

```solidity
36:    function approve(address guy, uint wad) public returns (bool) {
37:        allowance[msg.sender][guy] = wad;
38:        Approval(msg.sender, guy, wad);
39:        return true;
40:    }
```

```solidity
36:    function approve(address guy, uint wad) public returns (bool) {
37:        allowance[msg.sender][guy] = wad;
38:        Approval(msg.sender, guy, wad);
39:        return true;
40:    }
```

```solidity
42:    function transfer(address dst, uint wad) public returns (bool) {
43:        return transferFrom(msg.sender, dst, wad);
44:    }
```

```solidity
42:    function transfer(address dst, uint wad) public returns (bool) {
43:        return transferFrom(msg.sender, dst, wad);
44:    }
```

```solidity
46:    function transferFrom(address src, address dst, uint wad) public returns (bool) {
47:        require(balanceOf[src] >= wad);
48:
49:        if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
50:            require(allowance[src][msg.sender] >= wad);
51:            allowance[src][msg.sender] -= wad;
52:        }
53:
54:        balanceOf[src] -= wad;
55:        balanceOf[dst] += wad;
56:
57:        Transfer(src, dst, wad);
58:
59:        return true;
60:    }
```

```solidity
46:    function transferFrom(address src, address dst, uint wad) public returns (bool) {
47:        require(balanceOf[src] >= wad);
48:
49:        if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
50:            require(allowance[src][msg.sender] >= wad);
51:            allowance[src][msg.sender] -= wad;
52:        }
53:
54:        balanceOf[src] -= wad;
55:        balanceOf[dst] += wad;
56:
57:        Transfer(src, dst, wad);
58:
59:        return true;
60:    }
```

```solidity
46:    function transferFrom(address src, address dst, uint wad) public returns (bool) {
47:        require(balanceOf[src] >= wad);
48:
49:        if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
50:            require(allowance[src][msg.sender] >= wad);
51:            allowance[src][msg.sender] -= wad;
52:        }
53:
54:        balanceOf[src] -= wad;
55:        balanceOf[dst] += wad;
56:
57:        Transfer(src, dst, wad);
58:
59:        return true;
60:    }
```
[[WZETA.sol#L25-L30](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L25-L30)] 
[[WZETA.sol#L36-L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36-L40)] 
[[WZETA.sol#L36-L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36-L40)] 
[[WZETA.sol#L42-L44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L42-L44)] 
[[WZETA.sol#L42-L44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L42-L44)] 
[[WZETA.sol#L46-L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L46-L60)] 
[[WZETA.sol#L46-L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L46-L60)] 
[[WZETA.sol#L46-L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L46-L60)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
33:    constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {
34:        if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();
35:
36:        tssAddress = tssAddress_;
37:        tssAddressUpdater = tssAddressUpdater_;
38:    }
```

```solidity
33:    constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {
34:        if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();
35:
36:        tssAddress = tssAddress_;
37:        tssAddressUpdater = tssAddressUpdater_;
38:    }
```

```solidity
40:    function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {
41:        if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);
42:        if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();
43:
44:        tssAddress = tssAddress_;
45:        connectorAddress = connectorAddress_;
46:
47:        emit TSSAddressUpdated(msg.sender, tssAddress_);
48:        emit ConnectorAddressUpdated(msg.sender, connectorAddress_);
49:    }
```

```solidity
40:    function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {
41:        if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);
42:        if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();
43:
44:        tssAddress = tssAddress_;
45:        connectorAddress = connectorAddress_;
46:
47:        emit TSSAddressUpdated(msg.sender, tssAddress_);
48:        emit ConnectorAddressUpdated(msg.sender, connectorAddress_);
49:    }
```

```solidity
62:    function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
63:        /**
64:         * @dev Only Connector can mint. Minting requires burning the equivalent amount on another chain
65:         */
66:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
67:
68:        _mint(mintee, value);
69:
70:        emit Minted(mintee, value, internalSendHash);
71:    }
```

```solidity
62:    function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
63:        /**
64:         * @dev Only Connector can mint. Minting requires burning the equivalent amount on another chain
65:         */
66:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
67:
68:        _mint(mintee, value);
69:
70:        emit Minted(mintee, value, internalSendHash);
71:    }
```

```solidity
62:    function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
63:        /**
64:         * @dev Only Connector can mint. Minting requires burning the equivalent amount on another chain
65:         */
66:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
67:
68:        _mint(mintee, value);
69:
70:        emit Minted(mintee, value, internalSendHash);
71:    }
```

```solidity
73:    function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
74:        /**
75:         * @dev Only Connector can burn.
76:         */
77:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
78:
79:        ERC20Burnable.burnFrom(account, amount);
80:
81:        emit Burnt(account, amount);
82:    }
```

```solidity
73:    function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
74:        /**
75:         * @dev Only Connector can burn.
76:         */
77:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
78:
79:        ERC20Burnable.burnFrom(account, amount);
80:
81:        emit Burnt(account, amount);
82:    }
```
[[Zeta.non-eth.sol#L33-L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L38)] 
[[Zeta.non-eth.sol#L33-L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L38)] 
[[Zeta.non-eth.sol#L40-L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40-L49)] 
[[Zeta.non-eth.sol#L40-L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40-L49)] 
[[Zeta.non-eth.sol#L62-L71](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L71)] 
[[Zeta.non-eth.sol#L62-L71](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L71)] 
[[Zeta.non-eth.sol#L62-L71](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L71)] 
[[Zeta.non-eth.sol#L73-L82](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73-L82)] 
[[Zeta.non-eth.sol#L73-L82](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73-L82)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
37:    constructor(address zetaConnectorAddress) {
38:        if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
39:        currentChainId = block.chainid;
40:        connector = ZetaConnector(zetaConnectorAddress);
41:    }
```

```solidity
50:    function _isValidChainId(uint256 chainId) internal view returns (bool) {
51:        return (keccak256(interactorsByChainId[chainId]) != ZERO_BYTES);
52:    }
```

```solidity
54:    function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
55:        interactorsByChainId[destinationChainId] = contractAddress;
56:    }
```

```solidity
54:    function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
55:        interactorsByChainId[destinationChainId] = contractAddress;
56:    }
```
[[ZetaInteractor.sol#L37-L41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L37-L41)] 
[[ZetaInteractor.sol#L50-L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L50-L52)] 
[[ZetaInteractor.sol#L54-L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L56)] 
[[ZetaInteractor.sol#L54-L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L56)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
10:    constructor(address creator, uint256 initialSupply) {
11:        _mint(creator, initialSupply * (10 ** uint256(decimals())));
12:    }
```

```solidity
10:    constructor(address creator, uint256 initialSupply) {
11:        _mint(creator, initialSupply * (10 ** uint256(decimals())));
12:    }
```
[[Zeta.eth.sol#L10-L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L12)] 
[[Zeta.eth.sol#L10-L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L12)] 
## NC-42 | Incomplete NatSpec @return from function declaration

#### **Description** :-

Some functions have an incomplete NatSpec: add a @return notation to describe the function return value to improve the code documentation.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
26:    function safeCreate2Internal(
27:        bytes32 salt,
28:        bytes memory initializationCode
29:    ) internal returns (address deploymentAddress) {
30:        // move the initialization code from calldata to memory.
31:        bytes memory initCode = initializationCode;
32:
33:        // determine the target address for contract deployment.
34:        address targetDeploymentAddress = address(
35:            uint160( // downcast to match the address type.
36:                uint256( // convert to uint to truncate upper digits.
37:                    keccak256( // compute the CREATE2 hash using 4 inputs.
38:                        abi.encodePacked( // pack all inputs to the hash together.
39:                            hex"ff", // start with 0xff to distinguish from RLP.
40:                            address(this), // this contract will be the caller.
41:                            salt, // pass in the supplied salt value.
42:                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
43:                        )
44:                    )
45:                )
46:            )
47:        );
48:
49:        // ensure that a contract hasn't been previously deployed to target address.
50:        require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
51:
52:        // using inline assembly: load data and length of data, then call CREATE2.
53:        assembly {
54:            // solhint-disable-line
55:            let encoded_data := add(0x20, initCode) // load initialization code.
56:            let encoded_size := mload(initCode) // load the init code's length.
57:            deploymentAddress := create2(
58:                // call CREATE2 with 4 arguments.
59:                callvalue, // forward any attached value.
60:                encoded_data, // pass in initialization code.
61:                encoded_size, // pass in init code's length.
62:                salt // pass in the salt value.
63:            )
64:        }
65:
66:        // check address against target to ensure that deployment was successful.
67:        require(
68:            deploymentAddress == targetDeploymentAddress,
69:            "Failed to deploy contract using provided salt and initialization code."
70:        );
71:
72:        // record the deployment of the contract to prevent redeploys.
73:        _deployed[deploymentAddress] = true;
74:    }
```

```solidity
87:    function safeCreate2(
88:        bytes32 salt,
89:        bytes memory initializationCode
90:    ) public payable containsCaller(salt) returns (address deploymentAddress) {
91:        return safeCreate2Internal(salt, initializationCode);
92:    }
```

```solidity
108:    function findCreate2Address(
109:        bytes32 salt,
110:        bytes calldata initCode
111:    ) external view returns (address deploymentAddress) {
112:        // determine the address where the contract will be deployed.
113:        deploymentAddress = address(
114:            uint160( // downcast to match the address type.
115:                uint256( // convert to uint to truncate upper digits.
116:                    keccak256( // compute the CREATE2 hash using 4 inputs.
117:                        abi.encodePacked( // pack all inputs to the hash together.
118:                            hex"ff", // start with 0xff to distinguish from RLP.
119:                            address(this), // this contract will be the caller.
120:                            salt, // pass in the supplied salt value.
121:                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
122:                        )
123:                    )
124:                )
125:            )
126:        );
127:
128:        // return null address to signify failure if contract has been deployed.
129:        if (_deployed[deploymentAddress]) {
130:            return address(0);
131:        }
132:    }
```

```solidity
148:    function findCreate2AddressViaHash(
149:        bytes32 salt,
150:        bytes32 initCodeHash
151:    ) external view returns (address deploymentAddress) {
152:        // determine the address where the contract will be deployed.
153:        deploymentAddress = address(
154:            uint160( // downcast to match the address type.
155:                uint256( // convert to uint to truncate upper digits.
156:                    keccak256( // compute the CREATE2 hash using 4 inputs.
157:                        abi.encodePacked( // pack all inputs to the hash together.
158:                            hex"ff", // start with 0xff to distinguish from RLP.
159:                            address(this), // this contract will be the caller.
160:                            salt, // pass in the supplied salt value.
161:                            initCodeHash // pass in the hash of initialization code.
162:                        )
163:                    )
164:                )
165:            )
166:        );
167:
168:        // return null address to signify failure if contract has been deployed.
169:        if (_deployed[deploymentAddress]) {
170:            return address(0);
171:        }
172:    }
```

```solidity
202:    function safeCreate2AndTransfer(
203:        bytes32 salt,
204:        bytes calldata initializationCode
205:    ) external payable containsCaller(salt) returns (address deploymentAddress) {
206:        deploymentAddress = safeCreate2Internal(salt, initializationCode);
207:        Ownable(deploymentAddress).transferOwnership(msg.sender);
208:    }
```
[[ImmutableCreate2Factory.sol#L26-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L26-L74)] 
[[ImmutableCreate2Factory.sol#L87-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L87-L92)] 
[[ImmutableCreate2Factory.sol#L108-L132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L108-L132)] 
[[ImmutableCreate2Factory.sol#L148-L172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L148-L172)] 
[[ImmutableCreate2Factory.sol#L202-L208](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L202-L208)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
87:    function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
88:        if (tokenA == tokenB) revert CantBeIdenticalAddresses();
89:        (token0, token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
90:        if (token0 == address(0)) revert CantBeZeroAddress();
91:    }
```
[[SystemContract.sol#L87-L91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87-L91)] 
## NC-43 | Use of override is unnecessary

#### **Description** :-

Starting with Solidity version [0.8.8](https://docs.soliditylang.org/en/latest/contracts.html#function-overriding), using the override keyword when the function solely overrides an interface function, and the function doesn't exist in multiple base contracts, is unnecessary.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
83:    function name() public view virtual override returns (string memory) {
```

```solidity
91:    function symbol() public view virtual override returns (string memory) {
```

```solidity
99:    function decimals() public view virtual override returns (uint8) {
```

```solidity
107:    function totalSupply() public view virtual override returns (uint256) {
```

```solidity
116:    function balanceOf(address account) public view virtual override returns (uint256) {
```

```solidity
125:    function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
```

```solidity
135:    function allowance(address owner, address spender) public view virtual override returns (uint256) {
```

```solidity
145:    function approve(address spender, uint256 amount) public virtual override returns (bool) {
```

```solidity
157:    function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
```

```solidity
225:    function deposit(address to, uint256 amount) external override returns (bool) {
```

```solidity
236:    function withdrawGasFee() public view override returns (address, uint256) {
```

```solidity
256:    function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
```
[[ZRC20.sol#L83](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83)] 
[[ZRC20.sol#L91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91)] 
[[ZRC20.sol#L99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99)] 
[[ZRC20.sol#L107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L107)] 
[[ZRC20.sol#L116](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L116)] 
[[ZRC20.sol#L125](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125)] 
[[ZRC20.sol#L135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135)] 
[[ZRC20.sol#L145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145)] 
[[ZRC20.sol#L157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157)] 
[[ZRC20.sol#L225](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225)] 
[[ZRC20.sol#L236](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236)] 
[[ZRC20.sol#L256](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
103:    function getZetaFromEth(
```

```solidity
126:    function getZetaFromToken(
```

```solidity
151:    function getEthFromZeta(
```

```solidity
184:    function getTokenFromZeta(
```

```solidity
209:    function hasZetaLiquidity() external view override returns (bool) {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L103](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L103)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L151](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L209](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L209)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
74:    function getZetaFromEth(
```

```solidity
99:    function getZetaFromToken(
```

```solidity
136:    function getEthFromZeta(
```

```solidity
166:    function getTokenFromZeta(
```

```solidity
203:    function hasZetaLiquidity() external view override returns (bool) {
```
[[ZetaTokenConsumerTrident.strategy.sol#L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74)] 
[[ZetaTokenConsumerTrident.strategy.sol#L99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99)] 
[[ZetaTokenConsumerTrident.strategy.sol#L136](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136)] 
[[ZetaTokenConsumerTrident.strategy.sol#L166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166)] 
[[ZetaTokenConsumerTrident.strategy.sol#L203](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
74:    function getZetaFromEth(
```

```solidity
98:    function getZetaFromToken(
```

```solidity
124:    function getEthFromZeta(
```

```solidity
158:    function getTokenFromZeta(
```

```solidity
184:    function hasZetaLiquidity() external view override returns (bool) {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L98](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
34:    function getZetaFromEth(
```

```solidity
58:    function getZetaFromToken(
```

```solidity
95:    function getEthFromZeta(
```

```solidity
124:    function getTokenFromZeta(
```

```solidity
162:    function hasZetaLiquidity() external view override returns (bool) {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L34)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L95](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L162](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
40:    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
```

```solidity
61:    function onReceive(
```

```solidity
87:    function onRevert(
```
[[ZetaConnector.non-eth.sol#L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L40)] 
[[ZetaConnector.non-eth.sol#L61](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61)] 
[[ZetaConnector.non-eth.sol#L87](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
31:    function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
```

```solidity
52:    function onReceive(
```

```solidity
77:    function onRevert(
```
[[ZetaConnector.eth.sol#L31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31)] 
[[ZetaConnector.eth.sol#L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52)] 
[[ZetaConnector.eth.sol#L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
62:    function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
```

```solidity
73:    function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
```
[[Zeta.non-eth.sol#L62](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62)] 
[[Zeta.non-eth.sol#L73](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L73)] 
## NC-44 | Missing underscore prefix for non-external functions

#### **Description** :-

See [Function Names](https://docs.soliditylang.org/en/latest/style-guide.html#function-names).


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
68:    function getPair(address token0, address token1) internal pure returns (address, address) {
```
[[ZetaTokenConsumerTrident.strategy.sol#L68](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
26:    function safeCreate2Internal(
```
[[ImmutableCreate2Factory.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L26)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
87:    function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
```
[[SystemContract.sol#L87](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87)] 
## NC-45 | Missing Error Messages

#### **Description** :-

The require statement can be used to check for conditions and throw an exception if the condition is not met. It is better toprovide a string message containing details about the error that will be passed back to the caller.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
26:        require(balanceOf[msg.sender] >= wad);
```

```solidity
47:        require(balanceOf[src] >= wad);
```
[[WZETA.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L26)] 
[[WZETA.sol#L47](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L47)] 
## NC-46 | Implement Value Comparison Checks in Setter Functions to Prevent Redundant State Updates

#### **Description** :-

Consider adding appropriate minimum/maximum value checks to ensure that the following state variables can never be used to excessively harm users, including via griefing.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
117:        emit SetWZETA(wzeta_);
```
[[ZetaConnectorZEVM.sol#L117](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L117)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
33:        emit MaxSupplyUpdated(msg.sender, maxSupply_);
```
[[ZetaConnector.non-eth.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L33)] 
## NC-47 | Order of function

#### **Description** :-

According to the Solidity style guide, functions should be laid out in the following order :constructor(), receive(), fallback(), external, public, internal, private, but the cases below do not follow this pattern


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
20:contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```
[[ZRC20.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
56:contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
33:contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```
[[ZetaTokenConsumerTrident.strategy.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
27:contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
11:contract ERC20Custody is ReentrancyGuard {
```
[[ERC20Custody.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
17:contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
22:contract ImmutableCreate2Factory {
```
[[ImmutableCreate2Factory.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
15:contract ZetaConnectorBase is ConnectorErrors, Pausable {
```
[[ZetaConnector.base.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
22:contract SystemContract is SystemContractErrors {
```
[[SystemContract.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
55:contract ZetaConnectorZEVM is ZetaInterfaces {
```
[[ZetaConnectorZEVM.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
15:contract ZetaConnectorNonEth is ZetaConnectorBase {
```
[[ZetaConnector.non-eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
15:contract ZetaConnectorEth is ZetaConnectorBase {
```
[[ZetaConnector.eth.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
10:contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors {
```
[[Zeta.non-eth.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
9:abstract contract ZetaInteractor is Ownable2Step, ZetaInteractorErrors {
```
[[ZetaInteractor.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
77:interface ZetaTokenConsumer {
```
[[ZetaInterfaces.sol#L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol
```


```solidity
16:interface IPoolRouter {
```
[[TridentIPoolRouter.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Interfaces.sol
```


```solidity
49:interface IZRC20Metadata is IZRC20 {
```
[[Interfaces.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol
```


```solidity
10:interface zContract {
```
[[zContract.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol
```


```solidity
4:interface IWETH9 {
```
[[IWZETA.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
9:contract ZetaEth is ERC20("Zeta", "ZETA") {
```
[[Zeta.eth.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
6:interface IUniswapV2Router02 is IUniswapV2Router01 {
```
[[IUniswapV2Router02.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L6)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
9:interface ZetaNonEthInterface is IERC20 {
```
[[ZetaNonEthInterface.sol#L9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
```


```solidity
4:interface IZRC20 {
```
[[IZRC20.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
```


```solidity
16:interface ConcentratedLiquidityPoolFactory {
```
[[TridentConcentratedLiquidityPoolFactory.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol
```


```solidity
4:interface IUniswapV2Router01 {
```
[[IUniswapV2Router01.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L4)] 
## NC-48 | Order of layout

#### **Description** :-

According to the Solidity style guide, Inside each contract, library or interface, use the following order: Type declarations,State variables,Events,Errors,Modifiers ,Functions ,but the cases below do not follow this pattern


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
20:contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
```
[[ZRC20.sol#L20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
56:contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
33:contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
```
[[ZetaTokenConsumerTrident.strategy.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
27:contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
```
[[ZetaTokenConsumerUniV3.strategy.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
11:contract ERC20Custody is ReentrancyGuard {
```
[[ERC20Custody.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
17:contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
```
[[ZetaTokenConsumerUniV2.strategy.sol#L17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
22:contract ImmutableCreate2Factory {
```
[[ImmutableCreate2Factory.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
15:contract ZetaConnectorBase is ConnectorErrors, Pausable {
```
[[ZetaConnector.base.sol#L15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
22:contract SystemContract is SystemContractErrors {
```
[[SystemContract.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
55:contract ZetaConnectorZEVM is ZetaInterfaces {
```
[[ZetaConnectorZEVM.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
3:contract WETH9 {
```
[[WZETA.sol#L3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L3)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
108:interface ZetaCommonErrors {
```
[[ZetaInterfaces.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Interfaces.sol
```


```solidity
49:interface IZRC20Metadata is IZRC20 {
```
[[Interfaces.sol#L49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L49)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
```


```solidity
4:interface IZRC20 {
```
[[IZRC20.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L4)] 
## NC-49 | Use a struct to encapsulate multiple function parameters

#### **Description** :-

If a function has too many parameters, replacing them with a struct can improve code readability and maintainability, increase reusability, and reduce the likelihood of errors when passing the parameters.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
126:    function getZetaFromToken(
127:        address destinationAddress,
128:        uint256 minAmountOut,
129:        address inputToken,
130:        uint256 inputTokenAmount
131:    ) external override returns (uint256) {
132:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:        if (inputTokenAmount == 0) revert InputCantBeZero();
134:
135:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
136:        IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);
137:
138:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
140:            recipient: destinationAddress,
141:            amountIn: inputTokenAmount,
142:            amountOutMinimum: minAmountOut
143:        });
144:
145:        uint256 amountOut = pancakeV3Router.exactInput(params);
146:
147:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148:        return amountOut;
149:    }
```

```solidity
184:    function getTokenFromZeta(
185:        address destinationAddress,
186:        uint256 minAmountOut,
187:        address outputToken,
188:        uint256 zetaTokenAmount
189:    ) external override nonReentrant returns (uint256) {
190:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
191:        if (zetaTokenAmount == 0) revert InputCantBeZero();
192:
193:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
194:        IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
195:
196:        ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
197:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
198:            recipient: destinationAddress,
199:            amountIn: zetaTokenAmount,
200:            amountOutMinimum: minAmountOut
201:        });
202:
203:        uint256 amountOut = pancakeV3Router.exactInput(params);
204:
205:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
206:        return amountOut;
207:    }
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L149)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L207)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
99:    function getZetaFromToken(
100:        address destinationAddress,
101:        uint256 minAmountOut,
102:        address inputToken,
103:        uint256 inputTokenAmount
104:    ) external override returns (uint256) {
105:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:        if (inputTokenAmount == 0) revert InputCantBeZero();
107:
108:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
109:        IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
110:
111:        (address token0, address token1) = getPair(inputToken, WETH9Address);
112:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
113:
114:        (token0, token1) = getPair(WETH9Address, zetaToken);
115:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
116:
117:        address[] memory path = new address[](2);
118:        path[0] = pairPools1[0];
119:        path[1] = pairPools2[0];
120:
121:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:            tokenIn: inputToken,
123:            amountIn: inputTokenAmount,
124:            amountOutMinimum: minAmountOut,
125:            path: path,
126:            to: destinationAddress,
127:            unwrap: false
128:        });
129:
130:        uint256 amountOut = tridentRouter.exactInput(params);
131:
132:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133:        return amountOut;
134:    }
```

```solidity
166:    function getTokenFromZeta(
167:        address destinationAddress,
168:        uint256 minAmountOut,
169:        address outputToken,
170:        uint256 zetaTokenAmount
171:    ) external override nonReentrant returns (uint256) {
172:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
173:        if (zetaTokenAmount == 0) revert InputCantBeZero();
174:
175:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
176:        IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
177:
178:        (address token0, address token1) = getPair(zetaToken, WETH9Address);
179:        address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
180:
181:        (token0, token1) = getPair(WETH9Address, outputToken);
182:        address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
183:
184:        address[] memory path = new address[](2);
185:        path[0] = pairPools1[0];
186:        path[1] = pairPools2[0];
187:
188:        IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
189:            tokenIn: zetaToken,
190:            amountIn: zetaTokenAmount,
191:            amountOutMinimum: minAmountOut,
192:            path: path,
193:            to: destinationAddress,
194:            unwrap: false
195:        });
196:
197:        uint256 amountOut = tridentRouter.exactInput(params);
198:
199:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
200:        return amountOut;
201:    }
```
[[ZetaTokenConsumerTrident.strategy.sol#L99-L134](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L134)] 
[[ZetaTokenConsumerTrident.strategy.sol#L166-L201](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L201)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
98:    function getZetaFromToken(
99:        address destinationAddress,
100:        uint256 minAmountOut,
101:        address inputToken,
102:        uint256 inputTokenAmount
103:    ) external override returns (uint256) {
104:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:        if (inputTokenAmount == 0) revert InputCantBeZero();
106:
107:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
108:        IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);
109:
110:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:            deadline: block.timestamp + MAX_DEADLINE,
112:            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
113:            recipient: destinationAddress,
114:            amountIn: inputTokenAmount,
115:            amountOutMinimum: minAmountOut
116:        });
117:
118:        uint256 amountOut = uniswapV3Router.exactInput(params);
119:
120:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121:        return amountOut;
122:    }
```

```solidity
158:    function getTokenFromZeta(
159:        address destinationAddress,
160:        uint256 minAmountOut,
161:        address outputToken,
162:        uint256 zetaTokenAmount
163:    ) external override nonReentrant returns (uint256) {
164:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
165:        if (zetaTokenAmount == 0) revert InputCantBeZero();
166:
167:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
168:        IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
169:
170:        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
171:            deadline: block.timestamp + MAX_DEADLINE,
172:            path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
173:            recipient: destinationAddress,
174:            amountIn: zetaTokenAmount,
175:            amountOutMinimum: minAmountOut
176:        });
177:
178:        uint256 amountOut = uniswapV3Router.exactInput(params);
179:
180:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
181:        return amountOut;
182:    }
```
[[ZetaTokenConsumerUniV3.strategy.sol#L98-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L122)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L158-L182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L182)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
165:    function deposit(
166:        bytes calldata recipient,
167:        IERC20 asset,
168:        uint256 amount,
169:        bytes calldata message
170:    ) external nonReentrant {
171:        if (paused) {
172:            revert IsPaused();
173:        }
174:        if (!whitelisted[asset]) {
175:            revert NotWhitelisted();
176:        }
177:        if (zetaFee != 0 && address(zeta) != address(0)) {
178:            zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
179:        }
180:        uint256 oldBalance = asset.balanceOf(address(this));
181:        asset.safeTransferFrom(msg.sender, address(this), amount);
182:        // In case if there is a fee on a token transfer, we might not receive a full exepected amount
183:        // and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount.
184:        emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
185:    }
```
[[ERC20Custody.sol#L165-L185](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L185)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
58:    function getZetaFromToken(
59:        address destinationAddress,
60:        uint256 minAmountOut,
61:        address inputToken,
62:        uint256 inputTokenAmount
63:    ) external override returns (uint256) {
64:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:        if (inputTokenAmount == 0) revert InputCantBeZero();
66:
67:        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
68:        IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);
69:
70:        address[] memory path;
71:        if (inputToken == wETH) {
72:            path = new address[](2);
73:            path[0] = wETH;
74:            path[1] = zetaToken;
75:        } else {
76:            path = new address[](3);
77:            path[0] = inputToken;
78:            path[1] = wETH;
79:            path[2] = zetaToken;
80:        }
81:
82:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:            inputTokenAmount,
84:            minAmountOut,
85:            path,
86:            destinationAddress,
87:            block.timestamp + MAX_DEADLINE
88:        );
89:        uint256 amountOut = amounts[path.length - 1];
90:
91:        emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92:        return amountOut;
93:    }
```

```solidity
124:    function getTokenFromZeta(
125:        address destinationAddress,
126:        uint256 minAmountOut,
127:        address outputToken,
128:        uint256 zetaTokenAmount
129:    ) external override returns (uint256) {
130:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
131:        if (zetaTokenAmount == 0) revert InputCantBeZero();
132:
133:        IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
134:        IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
135:
136:        address[] memory path;
137:        if (outputToken == wETH) {
138:            path = new address[](2);
139:            path[0] = zetaToken;
140:            path[1] = wETH;
141:        } else {
142:            path = new address[](3);
143:            path[0] = zetaToken;
144:            path[1] = wETH;
145:            path[2] = outputToken;
146:        }
147:
148:        uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
149:            zetaTokenAmount,
150:            minAmountOut,
151:            path,
152:            destinationAddress,
153:            block.timestamp + MAX_DEADLINE
154:        );
155:
156:        uint256 amountOut = amounts[path.length - 1];
157:
158:        emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
159:        return amountOut;
160:    }
```
[[ZetaTokenConsumerUniV2.strategy.sol#L58-L93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L93)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L124-L160](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L160)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
67:    function depositAndCall(
68:        zContext calldata context,
69:        address zrc20,
70:        uint256 amount,
71:        address target,
72:        bytes calldata message
73:    ) external {
74:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
75:        if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();
76:
77:        IZRC20(zrc20).deposit(target, amount);
78:        zContract(target).onCrossChainCall(context, zrc20, amount, message);
79:    }
```
[[SystemContract.sol#L67-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L79)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
61:    function onReceive(
62:        bytes calldata zetaTxSenderAddress,
63:        uint256 sourceChainId,
64:        address destinationAddress,
65:        uint256 zetaValue,
66:        bytes calldata message,
67:        bytes32 internalSendHash
68:    ) external override onlyTssAddress {
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71:
72:        if (message.length > 0) {
73:            ZetaReceiver(destinationAddress).onZetaMessage(
74:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:            );
76:        }
77:
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```
[[ZetaConnector.non-eth.sol#L61-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
52:    function onReceive(
53:        bytes calldata zetaTxSenderAddress,
54:        uint256 sourceChainId,
55:        address destinationAddress,
56:        uint256 zetaValue,
57:        bytes calldata message,
58:        bytes32 internalSendHash
59:    ) external override onlyTssAddress {
60:        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:        if (!success) revert ZetaTransferError();
62:
63:        if (message.length > 0) {
64:            ZetaReceiver(destinationAddress).onZetaMessage(
65:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:            );
67:        }
68:
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```
[[ZetaConnector.eth.sol#L52-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol
```


```solidity
85:    function getZetaFromToken(
86:        address destinationAddress,
87:        uint256 minAmountOut,
88:        address inputToken,
89:        uint256 inputTokenAmount
90:    ) external returns (uint256);
```

```solidity
98:    function getTokenFromZeta(
99:        address destinationAddress,
100:        uint256 minAmountOut,
101:        address outputToken,
102:        uint256 zetaTokenAmount
103:    ) external returns (uint256);
```
[[ZetaInterfaces.sol#L85-L90](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L85-L90)] 
[[ZetaInterfaces.sol#L98-L103](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L98-L103)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol
```


```solidity
11:    function onCrossChainCall(
12:        zContext calldata context,
13:        address zrc20,
14:        uint256 amount,
15:        bytes calldata message
16:    ) external;
```
[[zContract.sol#L11-L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11-L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
7:    function removeLiquidityETHSupportingFeeOnTransferTokens(
8:        address token,
9:        uint liquidity,
10:        uint amountTokenMin,
11:        uint amountETHMin,
12:        address to,
13:        uint deadline
14:    ) external returns (uint amountETH);
```

```solidity
16:    function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17:        address token,
18:        uint liquidity,
19:        uint amountTokenMin,
20:        uint amountETHMin,
21:        address to,
22:        uint deadline,
23:        bool approveMax,
24:        uint8 v,
25:        bytes32 r,
26:        bytes32 s
27:    ) external returns (uint amountETH);
```

```solidity
29:    function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30:        uint amountIn,
31:        uint amountOutMin,
32:        address[] calldata path,
33:        address to,
34:        uint deadline
35:    ) external;
```

```solidity
37:    function swapExactETHForTokensSupportingFeeOnTransferTokens(
38:        uint amountOutMin,
39:        address[] calldata path,
40:        address to,
41:        uint deadline
42:    ) external payable;
```

```solidity
44:    function swapExactTokensForETHSupportingFeeOnTransferTokens(
45:        uint amountIn,
46:        uint amountOutMin,
47:        address[] calldata path,
48:        address to,
49:        uint deadline
50:    ) external;
```
[[IUniswapV2Router02.sol#L7-L14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7-L14)] 
[[IUniswapV2Router02.sol#L16-L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L27)] 
[[IUniswapV2Router02.sol#L29-L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29-L35)] 
[[IUniswapV2Router02.sol#L37-L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L37-L42)] 
[[IUniswapV2Router02.sol#L44-L50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44-L50)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol
```


```solidity
17:    function getPools(
18:        address token0,
19:        address token1,
20:        uint256 startIndex,
21:        uint256 count
22:    ) external view returns (address[] memory pairPools);
```
[[TridentConcentratedLiquidityPoolFactory.sol#L17-L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L17-L22)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol
```


```solidity
9:    function addLiquidity(
10:        address tokenA,
11:        address tokenB,
12:        uint amountADesired,
13:        uint amountBDesired,
14:        uint amountAMin,
15:        uint amountBMin,
16:        address to,
17:        uint deadline
18:    ) external returns (uint amountA, uint amountB, uint liquidity);
```

```solidity
20:    function addLiquidityETH(
21:        address token,
22:        uint amountTokenDesired,
23:        uint amountTokenMin,
24:        uint amountETHMin,
25:        address to,
26:        uint deadline
27:    ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
```

```solidity
29:    function removeLiquidity(
30:        address tokenA,
31:        address tokenB,
32:        uint liquidity,
33:        uint amountAMin,
34:        uint amountBMin,
35:        address to,
36:        uint deadline
37:    ) external returns (uint amountA, uint amountB);
```

```solidity
39:    function removeLiquidityETH(
40:        address token,
41:        uint liquidity,
42:        uint amountTokenMin,
43:        uint amountETHMin,
44:        address to,
45:        uint deadline
46:    ) external returns (uint amountToken, uint amountETH);
```

```solidity
48:    function removeLiquidityWithPermit(
49:        address tokenA,
50:        address tokenB,
51:        uint liquidity,
52:        uint amountAMin,
53:        uint amountBMin,
54:        address to,
55:        uint deadline,
56:        bool approveMax,
57:        uint8 v,
58:        bytes32 r,
59:        bytes32 s
60:    ) external returns (uint amountA, uint amountB);
```

```solidity
62:    function removeLiquidityETHWithPermit(
63:        address token,
64:        uint liquidity,
65:        uint amountTokenMin,
66:        uint amountETHMin,
67:        address to,
68:        uint deadline,
69:        bool approveMax,
70:        uint8 v,
71:        bytes32 r,
72:        bytes32 s
73:    ) external returns (uint amountToken, uint amountETH);
```

```solidity
75:    function swapExactTokensForTokens(
76:        uint amountIn,
77:        uint amountOutMin,
78:        address[] calldata path,
79:        address to,
80:        uint deadline
81:    ) external returns (uint[] memory amounts);
```

```solidity
83:    function swapTokensForExactTokens(
84:        uint amountOut,
85:        uint amountInMax,
86:        address[] calldata path,
87:        address to,
88:        uint deadline
89:    ) external returns (uint[] memory amounts);
```

```solidity
91:    function swapExactETHForTokens(
92:        uint amountOutMin,
93:        address[] calldata path,
94:        address to,
95:        uint deadline
96:    ) external payable returns (uint[] memory amounts);
```

```solidity
98:    function swapTokensForExactETH(
99:        uint amountOut,
100:        uint amountInMax,
101:        address[] calldata path,
102:        address to,
103:        uint deadline
104:    ) external returns (uint[] memory amounts);
```

```solidity
106:    function swapExactTokensForETH(
107:        uint amountIn,
108:        uint amountOutMin,
109:        address[] calldata path,
110:        address to,
111:        uint deadline
112:    ) external returns (uint[] memory amounts);
```

```solidity
114:    function swapETHForExactTokens(
115:        uint amountOut,
116:        address[] calldata path,
117:        address to,
118:        uint deadline
119:    ) external payable returns (uint[] memory amounts);
```
[[IUniswapV2Router01.sol#L9-L18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18)] 
[[IUniswapV2Router01.sol#L20-L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27)] 
[[IUniswapV2Router01.sol#L29-L37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L37)] 
[[IUniswapV2Router01.sol#L39-L46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L46)] 
[[IUniswapV2Router01.sol#L48-L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60)] 
[[IUniswapV2Router01.sol#L62-L73](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73)] 
[[IUniswapV2Router01.sol#L75-L81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L81)] 
[[IUniswapV2Router01.sol#L83-L89](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L89)] 
[[IUniswapV2Router01.sol#L91-L96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L91-L96)] 
[[IUniswapV2Router01.sol#L98-L104](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L104)] 
[[IUniswapV2Router01.sol#L106-L112](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L112)] 
[[IUniswapV2Router01.sol#L114-L119](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L114-L119)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
60:    constructor(
61:        string memory name_,
62:        string memory symbol_,
63:        uint8 decimals_,
64:        uint256 chainid_,
65:        CoinType coinType_,
66:        uint256 gasLimit_,
67:        address systemContractAddress_
68:    ) {
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:        _name = name_;
71:        _symbol = symbol_;
72:        _decimals = decimals_;
73:        CHAIN_ID = chainid_;
74:        COIN_TYPE = coinType_;
75:        GAS_LIMIT = gasLimit_;
76:        SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:    }
```
[[ZRC20.sol#L60-L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L77)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
71:    constructor(
72:        address zetaToken_,
73:        address pancakeV3Router_,
74:        address uniswapV3Factory_,
75:        address WETH9Address_,
76:        uint24 zetaPoolFee_,
77:        uint24 tokenPoolFee_
78:    ) {
79:        if (
80:            zetaToken_ == address(0) ||
81:            pancakeV3Router_ == address(0) ||
82:            uniswapV3Factory_ == address(0) ||
83:            WETH9Address_ == address(0)
84:        ) revert ZetaCommonErrors.InvalidAddress();
85:
86:        zetaToken = zetaToken_;
87:        pancakeV3Router = ISwapRouterPancake(pancakeV3Router_);
88:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
89:        WETH9Address = WETH9Address_;
90:        zetaPoolFee = zetaPoolFee_;
91:        tokenPoolFee = tokenPoolFee_;
92:    }
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L71-L92)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
42:    constructor(
43:        address zetaToken_,
44:        address uniswapV3Router_,
45:        address uniswapV3Factory_,
46:        address WETH9Address_,
47:        uint24 zetaPoolFee_,
48:        uint24 tokenPoolFee_
49:    ) {
50:        if (
51:            zetaToken_ == address(0) ||
52:            uniswapV3Router_ == address(0) ||
53:            uniswapV3Factory_ == address(0) ||
54:            WETH9Address_ == address(0)
55:        ) revert ZetaCommonErrors.InvalidAddress();
56:
57:        zetaToken = zetaToken_;
58:        uniswapV3Router = ISwapRouter(uniswapV3Router_);
59:        uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
60:        WETH9Address = WETH9Address_;
61:        zetaPoolFee = zetaPoolFee_;
62:        tokenPoolFee = tokenPoolFee_;
63:    }
```
[[ZetaTokenConsumerUniV3.strategy.sol#L42-L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L42-L63)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
68:    constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
69:        TSSAddress = TSSAddress_;
70:        TSSAddressUpdater = TSSAddressUpdater_;
71:        zetaFee = zetaFee_;
72:        zeta = zeta_;
73:        zetaMaxFee = zetaMaxFee_;
74:    }
```
[[ERC20Custody.sol#L68-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L74)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
67:    function depositAndCall(
68:        zContext calldata context,
69:        address zrc20,
70:        uint256 amount,
71:        address target,
72:        bytes calldata message
73:    ) external {
74:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
75:        if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();
76:
77:        IZRC20(zrc20).deposit(target, amount);
78:        zContract(target).onCrossChainCall(context, zrc20, amount, message);
79:    }
```
[[SystemContract.sol#L67-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L79)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
61:    function onReceive(
62:        bytes calldata zetaTxSenderAddress,
63:        uint256 sourceChainId,
64:        address destinationAddress,
65:        uint256 zetaValue,
66:        bytes calldata message,
67:        bytes32 internalSendHash
68:    ) external override onlyTssAddress {
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71:
72:        if (message.length > 0) {
73:            ZetaReceiver(destinationAddress).onZetaMessage(
74:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:            );
76:        }
77:
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```
[[ZetaConnector.non-eth.sol#L61-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
52:    function onReceive(
53:        bytes calldata zetaTxSenderAddress,
54:        uint256 sourceChainId,
55:        address destinationAddress,
56:        uint256 zetaValue,
57:        bytes calldata message,
58:        bytes32 internalSendHash
59:    ) external override onlyTssAddress {
60:        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:        if (!success) revert ZetaTransferError();
62:
63:        if (message.length > 0) {
64:            ZetaReceiver(destinationAddress).onZetaMessage(
65:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:            );
67:        }
68:
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```
[[ZetaConnector.eth.sol#L52-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
7:    function removeLiquidityETHSupportingFeeOnTransferTokens(
8:        address token,
9:        uint liquidity,
10:        uint amountTokenMin,
11:        uint amountETHMin,
12:        address to,
13:        uint deadline
14:    ) external returns (uint amountETH);
```

```solidity
16:    function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17:        address token,
18:        uint liquidity,
19:        uint amountTokenMin,
20:        uint amountETHMin,
21:        address to,
22:        uint deadline,
23:        bool approveMax,
24:        uint8 v,
25:        bytes32 r,
26:        bytes32 s
27:    ) external returns (uint amountETH);
```

```solidity
29:    function swapExactTokensForTokensSupportingFeeOnTransferTokens(
30:        uint amountIn,
31:        uint amountOutMin,
32:        address[] calldata path,
33:        address to,
34:        uint deadline
35:    ) external;
```

```solidity
44:    function swapExactTokensForETHSupportingFeeOnTransferTokens(
45:        uint amountIn,
46:        uint amountOutMin,
47:        address[] calldata path,
48:        address to,
49:        uint deadline
50:    ) external;
```
[[IUniswapV2Router02.sol#L7-L14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L7-L14)] 
[[IUniswapV2Router02.sol#L16-L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L27)] 
[[IUniswapV2Router02.sol#L29-L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L29-L35)] 
[[IUniswapV2Router02.sol#L44-L50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L44-L50)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol
```


```solidity
9:    function addLiquidity(
10:        address tokenA,
11:        address tokenB,
12:        uint amountADesired,
13:        uint amountBDesired,
14:        uint amountAMin,
15:        uint amountBMin,
16:        address to,
17:        uint deadline
18:    ) external returns (uint amountA, uint amountB, uint liquidity);
```

```solidity
20:    function addLiquidityETH(
21:        address token,
22:        uint amountTokenDesired,
23:        uint amountTokenMin,
24:        uint amountETHMin,
25:        address to,
26:        uint deadline
27:    ) external payable returns (uint amountToken, uint amountETH, uint liquidity);
```

```solidity
29:    function removeLiquidity(
30:        address tokenA,
31:        address tokenB,
32:        uint liquidity,
33:        uint amountAMin,
34:        uint amountBMin,
35:        address to,
36:        uint deadline
37:    ) external returns (uint amountA, uint amountB);
```

```solidity
39:    function removeLiquidityETH(
40:        address token,
41:        uint liquidity,
42:        uint amountTokenMin,
43:        uint amountETHMin,
44:        address to,
45:        uint deadline
46:    ) external returns (uint amountToken, uint amountETH);
```

```solidity
48:    function removeLiquidityWithPermit(
49:        address tokenA,
50:        address tokenB,
51:        uint liquidity,
52:        uint amountAMin,
53:        uint amountBMin,
54:        address to,
55:        uint deadline,
56:        bool approveMax,
57:        uint8 v,
58:        bytes32 r,
59:        bytes32 s
60:    ) external returns (uint amountA, uint amountB);
```

```solidity
62:    function removeLiquidityETHWithPermit(
63:        address token,
64:        uint liquidity,
65:        uint amountTokenMin,
66:        uint amountETHMin,
67:        address to,
68:        uint deadline,
69:        bool approveMax,
70:        uint8 v,
71:        bytes32 r,
72:        bytes32 s
73:    ) external returns (uint amountToken, uint amountETH);
```

```solidity
75:    function swapExactTokensForTokens(
76:        uint amountIn,
77:        uint amountOutMin,
78:        address[] calldata path,
79:        address to,
80:        uint deadline
81:    ) external returns (uint[] memory amounts);
```

```solidity
83:    function swapTokensForExactTokens(
84:        uint amountOut,
85:        uint amountInMax,
86:        address[] calldata path,
87:        address to,
88:        uint deadline
89:    ) external returns (uint[] memory amounts);
```

```solidity
98:    function swapTokensForExactETH(
99:        uint amountOut,
100:        uint amountInMax,
101:        address[] calldata path,
102:        address to,
103:        uint deadline
104:    ) external returns (uint[] memory amounts);
```

```solidity
106:    function swapExactTokensForETH(
107:        uint amountIn,
108:        uint amountOutMin,
109:        address[] calldata path,
110:        address to,
111:        uint deadline
112:    ) external returns (uint[] memory amounts);
```
[[IUniswapV2Router01.sol#L9-L18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L9-L18)] 
[[IUniswapV2Router01.sol#L20-L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L20-L27)] 
[[IUniswapV2Router01.sol#L29-L37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L29-L37)] 
[[IUniswapV2Router01.sol#L39-L46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L39-L46)] 
[[IUniswapV2Router01.sol#L48-L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60)] 
[[IUniswapV2Router01.sol#L62-L73](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73)] 
[[IUniswapV2Router01.sol#L75-L81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L75-L81)] 
[[IUniswapV2Router01.sol#L83-L89](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L83-L89)] 
[[IUniswapV2Router01.sol#L98-L104](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L98-L104)] 
[[IUniswapV2Router01.sol#L106-L112](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L106-L112)] 
## NC-50 | Take advantage of Custom Error's return value property

#### **Description** :-

An important feature of Custom Error is that values such as address, tokenID, msg.value can be written inside the () sign, this kind of approach provides a serious advantage in debugging and examining the revert details of dapps such as tenderly.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
53:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
69:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
161:        if (currentAllowance < amount) revert LowAllowance();
```

```solidity
179:        if (sender == address(0)) revert ZeroAddress();
```

```solidity
180:        if (recipient == address(0)) revert ZeroAddress();
```

```solidity
183:        if (senderBalance < amount) revert LowBalance();
```

```solidity
192:        if (account == address(0)) revert ZeroAddress();
```

```solidity
200:        if (account == address(0)) revert ZeroAddress();
```

```solidity
203:        if (accountBalance < amount) revert LowBalance();
```

```solidity
212:        if (owner == address(0)) revert ZeroAddress();
```

```solidity
213:        if (spender == address(0)) revert ZeroAddress();
```

```solidity
226:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();
```

```solidity
239:            revert ZeroGasCoin();
```

```solidity
243:            revert ZeroGasPrice();
```

```solidity
259:            revert GasFeeTransferFailed();
```
[[ZRC20.sol#L53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53)] 
[[ZRC20.sol#L69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L69)] 
[[ZRC20.sol#L161](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L161)] 
[[ZRC20.sol#L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L179)] 
[[ZRC20.sol#L180](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L180)] 
[[ZRC20.sol#L183](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L183)] 
[[ZRC20.sol#L192](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L192)] 
[[ZRC20.sol#L200](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L200)] 
[[ZRC20.sol#L203](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L203)] 
[[ZRC20.sol#L212](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L212)] 
[[ZRC20.sol#L213](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L213)] 
[[ZRC20.sol#L226](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226)] 
[[ZRC20.sol#L239](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L239)] 
[[ZRC20.sol#L243](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L243)] 
[[ZRC20.sol#L259](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L259)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
84:        ) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
95:        if (_locked) revert ReentrancyError();
```

```solidity
107:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
108:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
132:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
133:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
156:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
157:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
179:        if (!sent) revert ErrorSendingETH();
```

```solidity
190:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
191:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L84](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L84)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L95](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L95)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L107)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L108)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L132)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L133](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L133)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L156](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L156)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L157)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L179)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L190](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L190)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L191](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L191)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
51:        ) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
60:        if (_locked) revert ReentrancyError();
```

```solidity
78:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
79:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
105:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
106:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
141:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
142:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
172:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
173:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```
[[ZetaTokenConsumerTrident.strategy.sol#L51](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L51)] 
[[ZetaTokenConsumerTrident.strategy.sol#L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L60)] 
[[ZetaTokenConsumerTrident.strategy.sol#L78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L78)] 
[[ZetaTokenConsumerTrident.strategy.sol#L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L79)] 
[[ZetaTokenConsumerTrident.strategy.sol#L105](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L105)] 
[[ZetaTokenConsumerTrident.strategy.sol#L106](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L106)] 
[[ZetaTokenConsumerTrident.strategy.sol#L141](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L141)] 
[[ZetaTokenConsumerTrident.strategy.sol#L142](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L142)] 
[[ZetaTokenConsumerTrident.strategy.sol#L172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L172)] 
[[ZetaTokenConsumerTrident.strategy.sol#L173](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L173)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
55:        ) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
66:        if (_locked) revert ReentrancyError();
```

```solidity
78:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
79:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
104:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
105:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
129:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
130:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
153:        if (!sent) revert ErrorSendingETH();
```

```solidity
164:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
165:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```
[[ZetaTokenConsumerUniV3.strategy.sol#L55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L55)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L66)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L78)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L104](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L105](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L129](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L129)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L153](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L153)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L164](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L165](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L165)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
53:            revert InvalidSender();
```

```solidity
63:            revert InvalidTSSUpdater();
```

```solidity
82:            revert ZeroAddress();
```

```solidity
94:            revert ZeroFee();
```

```solidity
97:            revert ZetaMaxFeeExceeded();
```

```solidity
109:            revert ZeroAddress();
```

```solidity
120:            revert IsPaused();
```

```solidity
123:            revert ZeroAddress();
```

```solidity
134:            revert NotPaused();
```

```solidity
172:            revert IsPaused();
```

```solidity
175:            revert NotWhitelisted();
```

```solidity
195:            revert NotWhitelisted();
```
[[ERC20Custody.sol#L53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L53)] 
[[ERC20Custody.sol#L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L63)] 
[[ERC20Custody.sol#L82](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L82)] 
[[ERC20Custody.sol#L94](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L94)] 
[[ERC20Custody.sol#L97](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L97)] 
[[ERC20Custody.sol#L109](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L109)] 
[[ERC20Custody.sol#L120](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L120)] 
[[ERC20Custody.sol#L123](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L123)] 
[[ERC20Custody.sol#L134](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L134)] 
[[ERC20Custody.sol#L172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L172)] 
[[ERC20Custody.sol#L175](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L175)] 
[[ERC20Custody.sol#L195](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L195)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
27:        if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
38:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
39:        if (msg.value == 0) revert InputCantBeZero();
```

```solidity
64:        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
65:        if (inputTokenAmount == 0) revert InputCantBeZero();
```

```solidity
100:        if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
101:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```

```solidity
130:        if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
131:        if (zetaTokenAmount == 0) revert InputCantBeZero();
```
[[ZetaTokenConsumerUniV2.strategy.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L38)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L39](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L39)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L64](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L64)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L65](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L65)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L100](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L100)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L101](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L101)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L130)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L131](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L131)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
81:            revert ZetaCommonErrors.InvalidAddress();
```

```solidity
118:        if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
130:        if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
```

```solidity
141:        if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```
[[ZetaConnector.base.sol#L81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L81)] 
[[ZetaConnector.base.sol#L118](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L118)] 
[[ZetaConnector.base.sol#L130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L130)] 
[[ZetaConnector.base.sol#L141](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L141)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
52:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
74:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
75:        if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();
```

```solidity
88:        if (tokenA == tokenB) revert CantBeIdenticalAddresses();
```

```solidity
90:        if (token0 == address(0)) revert CantBeZeroAddress();
```

```solidity
124:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
135:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
146:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
157:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
158:        if (addr == address(0)) revert ZeroAddress();
```

```solidity
168:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
```

```solidity
169:        if (addr == address(0)) revert ZeroAddress();
```
[[SystemContract.sol#L52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L52)] 
[[SystemContract.sol#L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L74)] 
[[SystemContract.sol#L75](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L75)] 
[[SystemContract.sol#L88](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L88)] 
[[SystemContract.sol#L90](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L90)] 
[[SystemContract.sol#L124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124)] 
[[SystemContract.sol#L135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135)] 
[[SystemContract.sol#L146](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146)] 
[[SystemContract.sol#L157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157)] 
[[SystemContract.sol#L158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L158)] 
[[SystemContract.sol#L168](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168)] 
[[SystemContract.sol#L169](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L169)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
85:        if (msg.sender != wzeta) revert OnlyWZETA();
```

```solidity
94:        if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();
```

```solidity
97:        if (!sent) revert FailedZetaSent();
```

```solidity
115:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
```
[[ZetaConnectorZEVM.sol#L85](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L85)] 
[[ZetaConnectorZEVM.sol#L94](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L94)] 
[[ZetaConnectorZEVM.sol#L97](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L97)] 
[[ZetaConnectorZEVM.sol#L115](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
33:        if (!success) revert ZetaTransferError();
```

```solidity
61:        if (!success) revert ZetaTransferError();
```

```solidity
87:        if (!success) revert ZetaTransferError();
```
[[ZetaConnector.eth.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L33)] 
[[ZetaConnector.eth.sol#L61](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L61)] 
[[ZetaConnector.eth.sol#L87](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L87)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
34:        if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();
```

```solidity
42:        if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();
```

```solidity
56:        if (tssAddress == address(0)) revert InvalidAddress();
```
[[Zeta.non-eth.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L34)] 
[[Zeta.non-eth.sol#L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L42)] 
[[Zeta.non-eth.sol#L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L56)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
26:            revert InvalidZetaMessageCall();
```

```solidity
32:        if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
```

```solidity
33:        if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();
```

```solidity
38:        if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
```
[[ZetaInteractor.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L26)] 
[[ZetaInteractor.sol#L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L32)] 
[[ZetaInteractor.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L33)] 
[[ZetaInteractor.sol#L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L38)] 
## NC-51 | Top level pragma declarations should be separated by two blank lines

#### **Description** :-

Surround top level declarations in Solidity source with two blank lines. [Documentation](https://docs.soliditylang.org/en/latest/style-guide.html#blank-lines)


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/interfaces/IERC20.sol";
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/interfaces/IERC20.sol";
```
[[ZetaTokenConsumerTrident.strategy.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/interfaces/IERC20.sol";
```
[[ZetaTokenConsumerUniV3.strategy.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
3:pragma solidity 0.8.7;
4:
5:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```
[[ERC20Custody.sol#L3-L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L3-L5)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/interfaces/IERC20.sol";
```
[[ZetaTokenConsumerUniV2.strategy.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```
[[ZetaConnector.base.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "./interfaces/zContract.sol";
```
[[SystemContract.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```
[[ZetaConnector.non-eth.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```
[[ZetaConnector.eth.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
```
[[Zeta.non-eth.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/access/Ownable2Step.sol";
```
[[ZetaInteractor.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.eth.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
```
[[Zeta.eth.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "./IUniswapV2Router01.sol";
```
[[IUniswapV2Router02.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Uniswap.sol
```


```solidity
2:pragma solidity 0.5.16;
3:
4:import "@uniswap/v2-core/contracts/UniswapV2Pair.sol";
```
[[Uniswap.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
2:pragma solidity 0.8.7;
3:
4:import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```
[[ZetaNonEthInterface.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2-L4)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol
```


```solidity
2:pragma solidity 0.6.6;
3:
4:import "@uniswap/v2-periphery/contracts/UniswapV2Router02.sol";
```
[[UniswapPeriphery.sol#L2-L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L2-L4)] 
## NC-52 | Unused Function Parameter

#### **Description** :-

Consider removing unused function Parameter.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
166:    function send(ZetaInterfaces.SendInput calldata input) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```
[[ZetaConnector.base.sol#L166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
## NC-53 | Unused named return

#### **Description** :-

Declaring named returns, but not using them, is confusing to the reader. Consider either completely removing them (by declaring just the type without a name), or remove the return statement and do a variable assignment. This would improve the readability of the code, and it may also help reduce regressions during future code refactors.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
26:    function safeCreate2Internal(
27:        bytes32 salt,
28:        bytes memory initializationCode
29:    ) internal returns (address deploymentAddress) {
30:        // move the initialization code from calldata to memory.
31:        bytes memory initCode = initializationCode;
32:
33:        // determine the target address for contract deployment.
34:        address targetDeploymentAddress = address(
35:            uint160( // downcast to match the address type.
36:                uint256( // convert to uint to truncate upper digits.
37:                    keccak256( // compute the CREATE2 hash using 4 inputs.
38:                        abi.encodePacked( // pack all inputs to the hash together.
39:                            hex"ff", // start with 0xff to distinguish from RLP.
40:                            address(this), // this contract will be the caller.
41:                            salt, // pass in the supplied salt value.
42:                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
43:                        )
44:                    )
45:                )
46:            )
47:        );
48:
49:        // ensure that a contract hasn't been previously deployed to target address.
50:        require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
51:
52:        // using inline assembly: load data and length of data, then call CREATE2.
53:        assembly {
54:            // solhint-disable-line
55:            let encoded_data := add(0x20, initCode) // load initialization code.
56:            let encoded_size := mload(initCode) // load the init code's length.
57:            deploymentAddress := create2(
58:                // call CREATE2 with 4 arguments.
59:                callvalue, // forward any attached value.
60:                encoded_data, // pass in initialization code.
61:                encoded_size, // pass in init code's length.
62:                salt // pass in the salt value.
63:            )
64:        }
65:
66:        // check address against target to ensure that deployment was successful.
67:        require(
68:            deploymentAddress == targetDeploymentAddress,
69:            "Failed to deploy contract using provided salt and initialization code."
70:        );
71:
72:        // record the deployment of the contract to prevent redeploys.
73:        _deployed[deploymentAddress] = true;
74:    }
```

```solidity
87:    function safeCreate2(
88:        bytes32 salt,
89:        bytes memory initializationCode
90:    ) public payable containsCaller(salt) returns (address deploymentAddress) {
91:        return safeCreate2Internal(salt, initializationCode);
92:    }
```

```solidity
108:    function findCreate2Address(
109:        bytes32 salt,
110:        bytes calldata initCode
111:    ) external view returns (address deploymentAddress) {
112:        // determine the address where the contract will be deployed.
113:        deploymentAddress = address(
114:            uint160( // downcast to match the address type.
115:                uint256( // convert to uint to truncate upper digits.
116:                    keccak256( // compute the CREATE2 hash using 4 inputs.
117:                        abi.encodePacked( // pack all inputs to the hash together.
118:                            hex"ff", // start with 0xff to distinguish from RLP.
119:                            address(this), // this contract will be the caller.
120:                            salt, // pass in the supplied salt value.
121:                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
122:                        )
123:                    )
124:                )
125:            )
126:        );
127:
128:        // return null address to signify failure if contract has been deployed.
129:        if (_deployed[deploymentAddress]) {
130:            return address(0);
131:        }
132:    }
```

```solidity
148:    function findCreate2AddressViaHash(
149:        bytes32 salt,
150:        bytes32 initCodeHash
151:    ) external view returns (address deploymentAddress) {
152:        // determine the address where the contract will be deployed.
153:        deploymentAddress = address(
154:            uint160( // downcast to match the address type.
155:                uint256( // convert to uint to truncate upper digits.
156:                    keccak256( // compute the CREATE2 hash using 4 inputs.
157:                        abi.encodePacked( // pack all inputs to the hash together.
158:                            hex"ff", // start with 0xff to distinguish from RLP.
159:                            address(this), // this contract will be the caller.
160:                            salt, // pass in the supplied salt value.
161:                            initCodeHash // pass in the hash of initialization code.
162:                        )
163:                    )
164:                )
165:            )
166:        );
167:
168:        // return null address to signify failure if contract has been deployed.
169:        if (_deployed[deploymentAddress]) {
170:            return address(0);
171:        }
172:    }
```

```solidity
202:    function safeCreate2AndTransfer(
203:        bytes32 salt,
204:        bytes calldata initializationCode
205:    ) external payable containsCaller(salt) returns (address deploymentAddress) {
206:        deploymentAddress = safeCreate2Internal(salt, initializationCode);
207:        Ownable(deploymentAddress).transferOwnership(msg.sender);
208:    }
```
[[ImmutableCreate2Factory.sol#L26-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L26-L74)] 
[[ImmutableCreate2Factory.sol#L87-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L87-L92)] 
[[ImmutableCreate2Factory.sol#L108-L132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L108-L132)] 
[[ImmutableCreate2Factory.sol#L148-L172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L148-L172)] 
[[ImmutableCreate2Factory.sol#L202-L208](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L202-L208)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
87:    function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) {
88:        if (tokenA == tokenB) revert CantBeIdenticalAddresses();
89:        (token0, token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
90:        if (token0 == address(0)) revert CantBeZeroAddress();
91:    }
```

```solidity
100:    function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {
101:        (address token0, address token1) = sortTokens(tokenA, tokenB);
102:        pair = address(
103:            uint160(
104:                uint256(
105:                    keccak256(
106:                        abi.encodePacked(
107:                            hex"ff",
108:                            factory,
109:                            keccak256(abi.encodePacked(token0, token1)),
110:                            hex"96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f" // init code hash
111:                        )
112:                    )
113:                )
114:            )
115:        );
116:    }
```
[[SystemContract.sol#L87-L91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87-L91)] 
[[SystemContract.sol#L100-L116](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L100-L116)] 
## NC-54 | Enum values should be used in place of constant array indexes

#### **Description** :-

Consider using an enum instead of hardcoding an index access to make the code easier to understand.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
118:        path[0] = pairPools1[0];
```

```solidity
119:        path[1] = pairPools2[0];
```

```solidity
185:        path[0] = pairPools1[0];
```

```solidity
186:        path[1] = pairPools2[0];
```
[[ZetaTokenConsumerTrident.strategy.sol#L118](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L118)] 
[[ZetaTokenConsumerTrident.strategy.sol#L119](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L119)] 
[[ZetaTokenConsumerTrident.strategy.sol#L185](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L185)] 
[[ZetaTokenConsumerTrident.strategy.sol#L186](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L186)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
42:        path[0] = wETH;
```

```solidity
43:        path[1] = zetaToken;
```

```solidity
73:            path[0] = wETH;
```

```solidity
74:            path[1] = zetaToken;
```

```solidity
77:            path[0] = inputToken;
```

```solidity
78:            path[1] = wETH;
```

```solidity
79:            path[2] = zetaToken;
```

```solidity
107:        path[0] = zetaToken;
```

```solidity
108:        path[1] = wETH;
```

```solidity
139:            path[0] = zetaToken;
```

```solidity
140:            path[1] = wETH;
```

```solidity
143:            path[0] = zetaToken;
```

```solidity
144:            path[1] = wETH;
```

```solidity
145:            path[2] = outputToken;
```

```solidity
164:        path[0] = wETH;
```

```solidity
165:        path[1] = zetaToken;
```
[[ZetaTokenConsumerUniV2.strategy.sol#L42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L42)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L43)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L73](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L73)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L74)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L77)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L78)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L79)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L107)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L108)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L139](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L139)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L140](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L140)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L143](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L143)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L144](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L144)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L145)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L164](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L164)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L165](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L165)] 
## NC-55 | Variable Names Not in `mixedCase`

#### **Description** :-

See [Function Names](https://docs.soliditylang.org/en/latest/style-guide.html#function-names).


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
22:    address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

```solidity
24:    uint256 public immutable CHAIN_ID;
```

```solidity
26:    CoinType public immutable COIN_TYPE;
```

```solidity
28:    address public SYSTEM_CONTRACT_ADDRESS;
```

```solidity
30:    uint256 public GAS_LIMIT;
```

```solidity
32:    uint256 public PROTOCOL_FLAT_FEE;
```

```solidity
34:    mapping(address => uint256) private _balances;
```

```solidity
35:    mapping(address => mapping(address => uint256)) private _allowances;
```

```solidity
36:    uint256 private _totalSupply;
```

```solidity
37:    string private _name;
```

```solidity
38:    string private _symbol;
```

```solidity
39:    uint8 private _decimals;
```
[[ZRC20.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22)] 
[[ZRC20.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L24)] 
[[ZRC20.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L26)] 
[[ZRC20.sol#L28](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L28)] 
[[ZRC20.sol#L30](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L30)] 
[[ZRC20.sol#L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L32)] 
[[ZRC20.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L34)] 
[[ZRC20.sol#L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35)] 
[[ZRC20.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L36)] 
[[ZRC20.sol#L37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L37)] 
[[ZRC20.sol#L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L38)] 
[[ZRC20.sol#L39](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L39)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol
```


```solidity
58:    uint256 internal constant MAX_DEADLINE = 200;
```

```solidity
60:    uint24 public immutable zetaPoolFee;
```

```solidity
61:    uint24 public immutable tokenPoolFee;
```

```solidity
63:    address public immutable WETH9Address;
```

```solidity
64:    address public immutable zetaToken;
```

```solidity
66:    ISwapRouterPancake public immutable pancakeV3Router;
```

```solidity
67:    IUniswapV3Factory public immutable uniswapV3Factory;
```

```solidity
69:    bool internal _locked;
```
[[ZetaTokenConsumerPancakeV3.strategy.sol#L58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L60)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L61](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L61)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L63)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L64](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L64)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L66)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L67](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L67)] 
[[ZetaTokenConsumerPancakeV3.strategy.sol#L69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L69)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
```


```solidity
35:    uint256 internal constant MAX_DEADLINE = 200;
```

```solidity
37:    address internal immutable WETH9Address;
```

```solidity
38:    address public immutable zetaToken;
```

```solidity
40:    IPoolRouter public immutable tridentRouter;
```

```solidity
41:    ConcentratedLiquidityPoolFactory public immutable poolFactory;
```

```solidity
43:    bool internal _locked;
```
[[ZetaTokenConsumerTrident.strategy.sol#L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35)] 
[[ZetaTokenConsumerTrident.strategy.sol#L37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37)] 
[[ZetaTokenConsumerTrident.strategy.sol#L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L38)] 
[[ZetaTokenConsumerTrident.strategy.sol#L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L40)] 
[[ZetaTokenConsumerTrident.strategy.sol#L41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L41)] 
[[ZetaTokenConsumerTrident.strategy.sol#L43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L43)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol
```


```solidity
29:    uint256 internal constant MAX_DEADLINE = 200;
```

```solidity
31:    uint24 public immutable zetaPoolFee;
```

```solidity
32:    uint24 public immutable tokenPoolFee;
```

```solidity
34:    address public immutable WETH9Address;
```

```solidity
35:    address public immutable zetaToken;
```

```solidity
37:    ISwapRouter public immutable uniswapV3Router;
```

```solidity
38:    IUniswapV3Factory public immutable uniswapV3Factory;
```

```solidity
40:    bool internal _locked;
```
[[ZetaTokenConsumerUniV3.strategy.sol#L29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L31)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L32)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L34)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L35)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L37)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L38)] 
[[ZetaTokenConsumerUniV3.strategy.sol#L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L40)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
24:    bool public paused;
```

```solidity
26:    address public TSSAddress;
```

```solidity
28:    address public TSSAddressUpdater;
```

```solidity
30:    uint256 public zetaFee;
```

```solidity
32:    uint256 public immutable zetaMaxFee;
```

```solidity
34:    IERC20 public immutable zeta;
```

```solidity
36:    mapping(IERC20 => bool) public whitelisted;
```
[[ERC20Custody.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L24)] 
[[ERC20Custody.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L26)] 
[[ERC20Custody.sol#L28](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L28)] 
[[ERC20Custody.sol#L30](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L30)] 
[[ERC20Custody.sol#L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L32)] 
[[ERC20Custody.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L34)] 
[[ERC20Custody.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol
```


```solidity
19:    uint256 internal constant MAX_DEADLINE = 200;
```

```solidity
21:    address internal immutable wETH;
```

```solidity
22:    address public immutable zetaToken;
```

```solidity
24:    IUniswapV2Router02 internal immutable uniswapV2Router;
```
[[ZetaTokenConsumerUniV2.strategy.sol#L19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L22)] 
[[ZetaTokenConsumerUniV2.strategy.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
24:    mapping(address => bool) private _deployed;
```
[[ImmutableCreate2Factory.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L24)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
16:    address public immutable zetaToken;
```

```solidity
22:    address public pauserAddress;
```

```solidity
27:    address public tssAddress;
```

```solidity
32:    address public tssAddressUpdater;
```
[[ZetaConnector.base.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L16)] 
[[ZetaConnector.base.sol#L22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L22)] 
[[ZetaConnector.base.sol#L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L27)] 
[[ZetaConnector.base.sol#L32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L32)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
24:    mapping(uint256 => uint256) public gasPriceByChainId;
```

```solidity
26:    mapping(uint256 => address) public gasCoinZRC20ByChainId;
```

```solidity
28:    mapping(uint256 => address) public gasZetaPoolByChainId;
```

```solidity
31:    address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
```

```solidity
33:    address public immutable uniswapv2FactoryAddress;
```

```solidity
34:    address public immutable uniswapv2Router02Address;
```

```solidity
36:    address public wZetaContractAddress;
```

```solidity
38:    address public zetaConnectorZEVMAddress;
```
[[SystemContract.sol#L24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L24)] 
[[SystemContract.sol#L26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L26)] 
[[SystemContract.sol#L28](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L28)] 
[[SystemContract.sol#L31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L31)] 
[[SystemContract.sol#L33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L33)] 
[[SystemContract.sol#L34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L34)] 
[[SystemContract.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L36)] 
[[SystemContract.sol#L38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L38)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol
```


```solidity
63:    address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB);
```

```solidity
65:    address public wzeta;
```
[[ZetaConnectorZEVM.sol#L63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63)] 
[[ZetaConnectorZEVM.sol#L65](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L65)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
16:    uint256 public maxSupply = 2 ** 256 - 1;
```
[[ZetaConnector.non-eth.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/WZETA.sol
```


```solidity
4:    string public name = "Wrapped Zeta";
```

```solidity
5:    string public symbol = "WZETA";
```

```solidity
6:    uint8 public decimals = 18;
```

```solidity
13:    mapping(address => uint) public balanceOf;
```

```solidity
14:    mapping(address => mapping(address => uint)) public allowance;
```
[[WZETA.sol#L4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L4)] 
[[WZETA.sol#L5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L5)] 
[[WZETA.sol#L6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L6)] 
[[WZETA.sol#L13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L13)] 
[[WZETA.sol#L14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L14)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
11:    address public connectorAddress;
```

```solidity
16:    address public tssAddress;
```

```solidity
21:    address public tssAddressUpdater;
```
[[Zeta.non-eth.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L11)] 
[[Zeta.non-eth.sol#L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L16)] 
[[Zeta.non-eth.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L21)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
10:    bytes32 constant ZERO_BYTES = keccak256(new bytes(0));
```

```solidity
11:    uint256 internal immutable currentChainId;
```

```solidity
12:    ZetaConnector public immutable connector;
```

```solidity
21:    mapping(uint256 => bytes) public interactorsByChainId;
```
[[ZetaInteractor.sol#L10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L10)] 
[[ZetaInteractor.sol#L11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11)] 
[[ZetaInteractor.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L12)] 
[[ZetaInteractor.sol#L21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L21)] 
## NC-56 | Avoid the use of sensitive terms

#### **Description** :-

Use [alternative variants](https://www.zdnet.com/article/mysql-drops-master-slave-and-blacklist-whitelist-terminology/), e.g. allowlist/denylist instead of whitelist/blacklist.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
14:    error NotWhitelisted();
```

```solidity
35:    /// @notice Mapping of whitelisted token => true/false.
```

```solidity
36:    mapping(IERC20 => bool) public whitelisted;
```

```solidity
40:    event Whitelisted(IERC20 indexed asset);
```

```solidity
41:    event Unwhitelisted(IERC20 indexed asset);
```

```solidity
141:     * @dev Whitelist asset.
```

```solidity
144:    function whitelist(IERC20 asset) external onlyTSS {
```

```solidity
145:        whitelisted[asset] = true;
```

```solidity
146:        emit Whitelisted(asset);
```

```solidity
150:     * @dev Unwhitelist asset.
```

```solidity
153:    function unwhitelist(IERC20 asset) external onlyTSS {
```

```solidity
154:        whitelisted[asset] = false;
```

```solidity
155:        emit Unwhitelisted(asset);
```

```solidity
174:        if (!whitelisted[asset]) {
```

```solidity
175:            revert NotWhitelisted();
```

```solidity
194:        if (!whitelisted[asset]) {
```

```solidity
195:            revert NotWhitelisted();
```
[[ERC20Custody.sol#L14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14)] 
[[ERC20Custody.sol#L35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L35)] 
[[ERC20Custody.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36)] 
[[ERC20Custody.sol#L40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40)] 
[[ERC20Custody.sol#L41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41)] 
[[ERC20Custody.sol#L141](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L141)] 
[[ERC20Custody.sol#L144](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L144)] 
[[ERC20Custody.sol#L145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L145)] 
[[ERC20Custody.sol#L146](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L146)] 
[[ERC20Custody.sol#L150](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L150)] 
[[ERC20Custody.sol#L153](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153)] 
[[ERC20Custody.sol#L154](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L154)] 
[[ERC20Custody.sol#L155](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L155)] 
[[ERC20Custody.sol#L174](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L174)] 
[[ERC20Custody.sol#L175](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L175)] 
[[ERC20Custody.sol#L194](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L194)] 
[[ERC20Custody.sol#L195](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L195)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol
```


```solidity
8:    // @dev Thrown when try to send a message or tokens to a non whitelisted chain
```
[[ZetaInteractorErrors.sol#L8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L8)] 
## NC-57 | MISSING Non-Empty Check for Bytes in Function Parameters

#### **Description** :-

To avoid mistakenly accepting empty bytes as valid parameters, it is advisable to implement checks for non-empty bytes within functions. This ensures that empty bytes are not treated as valid inputs, preventing potential issues.


```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/ZRC20.sol
```


```solidity
256:    function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
257:        (address gasZRC20, uint256 gasFee) = withdrawGasFee();
258:        if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
259:            revert GasFeeTransferFailed();
260:        }
261:        _burn(msg.sender, amount);
262:        emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);
263:        return true;
264:    }
```
[[ZRC20.sol#L256-L264](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256-L264)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ERC20Custody.sol
```


```solidity
165:    function deposit(
166:        bytes calldata recipient,
167:        IERC20 asset,
168:        uint256 amount,
169:        bytes calldata message
170:    ) external nonReentrant {
171:        if (paused) {
172:            revert IsPaused();
173:        }
174:        if (!whitelisted[asset]) {
175:            revert NotWhitelisted();
176:        }
177:        if (zetaFee != 0 && address(zeta) != address(0)) {
178:            zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
179:        }
180:        uint256 oldBalance = asset.balanceOf(address(this));
181:        asset.safeTransferFrom(msg.sender, address(this), amount);
182:        // In case if there is a fee on a token transfer, we might not receive a full exepected amount
183:        // and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount.
184:        emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
185:    }
```
[[ERC20Custody.sol#L165-L185](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L185)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol
```


```solidity
26:    function safeCreate2Internal(
27:        bytes32 salt,
28:        bytes memory initializationCode
29:    ) internal returns (address deploymentAddress) {
30:        // move the initialization code from calldata to memory.
31:        bytes memory initCode = initializationCode;
32:
33:        // determine the target address for contract deployment.
34:        address targetDeploymentAddress = address(
35:            uint160( // downcast to match the address type.
36:                uint256( // convert to uint to truncate upper digits.
37:                    keccak256( // compute the CREATE2 hash using 4 inputs.
38:                        abi.encodePacked( // pack all inputs to the hash together.
39:                            hex"ff", // start with 0xff to distinguish from RLP.
40:                            address(this), // this contract will be the caller.
41:                            salt, // pass in the supplied salt value.
42:                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
43:                        )
44:                    )
45:                )
46:            )
47:        );
48:
49:        // ensure that a contract hasn't been previously deployed to target address.
50:        require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
51:
52:        // using inline assembly: load data and length of data, then call CREATE2.
53:        assembly {
54:            // solhint-disable-line
55:            let encoded_data := add(0x20, initCode) // load initialization code.
56:            let encoded_size := mload(initCode) // load the init code's length.
57:            deploymentAddress := create2(
58:                // call CREATE2 with 4 arguments.
59:                callvalue, // forward any attached value.
60:                encoded_data, // pass in initialization code.
61:                encoded_size, // pass in init code's length.
62:                salt // pass in the salt value.
63:            )
64:        }
65:
66:        // check address against target to ensure that deployment was successful.
67:        require(
68:            deploymentAddress == targetDeploymentAddress,
69:            "Failed to deploy contract using provided salt and initialization code."
70:        );
71:
72:        // record the deployment of the contract to prevent redeploys.
73:        _deployed[deploymentAddress] = true;
74:    }
```

```solidity
87:    function safeCreate2(
88:        bytes32 salt,
89:        bytes memory initializationCode
90:    ) public payable containsCaller(salt) returns (address deploymentAddress) {
91:        return safeCreate2Internal(salt, initializationCode);
92:    }
```

```solidity
108:    function findCreate2Address(
109:        bytes32 salt,
110:        bytes calldata initCode
111:    ) external view returns (address deploymentAddress) {
112:        // determine the address where the contract will be deployed.
113:        deploymentAddress = address(
114:            uint160( // downcast to match the address type.
115:                uint256( // convert to uint to truncate upper digits.
116:                    keccak256( // compute the CREATE2 hash using 4 inputs.
117:                        abi.encodePacked( // pack all inputs to the hash together.
118:                            hex"ff", // start with 0xff to distinguish from RLP.
119:                            address(this), // this contract will be the caller.
120:                            salt, // pass in the supplied salt value.
121:                            keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
122:                        )
123:                    )
124:                )
125:            )
126:        );
127:
128:        // return null address to signify failure if contract has been deployed.
129:        if (_deployed[deploymentAddress]) {
130:            return address(0);
131:        }
132:    }
```

```solidity
148:    function findCreate2AddressViaHash(
149:        bytes32 salt,
150:        bytes32 initCodeHash
151:    ) external view returns (address deploymentAddress) {
152:        // determine the address where the contract will be deployed.
153:        deploymentAddress = address(
154:            uint160( // downcast to match the address type.
155:                uint256( // convert to uint to truncate upper digits.
156:                    keccak256( // compute the CREATE2 hash using 4 inputs.
157:                        abi.encodePacked( // pack all inputs to the hash together.
158:                            hex"ff", // start with 0xff to distinguish from RLP.
159:                            address(this), // this contract will be the caller.
160:                            salt, // pass in the supplied salt value.
161:                            initCodeHash // pass in the hash of initialization code.
162:                        )
163:                    )
164:                )
165:            )
166:        );
167:
168:        // return null address to signify failure if contract has been deployed.
169:        if (_deployed[deploymentAddress]) {
170:            return address(0);
171:        }
172:    }
```

```solidity
202:    function safeCreate2AndTransfer(
203:        bytes32 salt,
204:        bytes calldata initializationCode
205:    ) external payable containsCaller(salt) returns (address deploymentAddress) {
206:        deploymentAddress = safeCreate2Internal(salt, initializationCode);
207:        Ownable(deploymentAddress).transferOwnership(msg.sender);
208:    }
```
[[ImmutableCreate2Factory.sol#L26-L74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L26-L74)] 
[[ImmutableCreate2Factory.sol#L87-L92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L87-L92)] 
[[ImmutableCreate2Factory.sol#L108-L132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L108-L132)] 
[[ImmutableCreate2Factory.sol#L148-L172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L148-L172)] 
[[ImmutableCreate2Factory.sol#L202-L208](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L202-L208)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol
```


```solidity
172:    function onReceive(
173:        bytes calldata zetaTxSenderAddress,
174:        uint256 sourceChainId,
175:        address destinationAddress,
176:        uint256 zetaValue,
177:        bytes calldata message,
178:        bytes32 internalSendHash
179:    ) external virtual {}
```

```solidity
185:    function onRevert(
186:        address zetaTxSenderAddress,
187:        uint256 sourceChainId,
188:        bytes calldata destinationAddress,
189:        uint256 destinationChainId,
190:        uint256 remainingZetaValue,
191:        bytes calldata message,
192:        bytes32 internalSendHash
193:    ) external virtual {}
```
[[ZetaConnector.base.sol#L172-L179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L179)] 
[[ZetaConnector.base.sol#L185-L193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L193)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/SystemContract.sol
```


```solidity
67:    function depositAndCall(
68:        zContext calldata context,
69:        address zrc20,
70:        uint256 amount,
71:        address target,
72:        bytes calldata message
73:    ) external {
74:        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
75:        if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();
76:
77:        IZRC20(zrc20).deposit(target, amount);
78:        zContract(target).onCrossChainCall(context, zrc20, amount, message);
79:    }
```
[[SystemContract.sol#L67-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L79)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol
```


```solidity
61:    function onReceive(
62:        bytes calldata zetaTxSenderAddress,
63:        uint256 sourceChainId,
64:        address destinationAddress,
65:        uint256 zetaValue,
66:        bytes calldata message,
67:        bytes32 internalSendHash
68:    ) external override onlyTssAddress {
69:        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71:
72:        if (message.length > 0) {
73:            ZetaReceiver(destinationAddress).onZetaMessage(
74:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:            );
76:        }
77:
78:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
79:    }
```

```solidity
87:    function onRevert(
88:        address zetaTxSenderAddress,
89:        uint256 sourceChainId,
90:        bytes calldata destinationAddress,
91:        uint256 destinationChainId,
92:        uint256 remainingZetaValue,
93:        bytes calldata message,
94:        bytes32 internalSendHash
95:    ) external override whenNotPaused onlyTssAddress {
96:        if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
97:            revert ExceedsMaxSupply(maxSupply);
98:        ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);
99:
100:        if (message.length > 0) {
101:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
102:                ZetaInterfaces.ZetaRevert(
103:                    zetaTxSenderAddress,
104:                    sourceChainId,
105:                    destinationAddress,
106:                    destinationChainId,
107:                    remainingZetaValue,
108:                    message
109:                )
110:            );
111:        }
112:
113:        emit ZetaReverted(
114:            zetaTxSenderAddress,
115:            sourceChainId,
116:            destinationChainId,
117:            destinationAddress,
118:            remainingZetaValue,
119:            message,
120:            internalSendHash
121:        );
122:    }
```
[[ZetaConnector.non-eth.sol#L61-L79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L79)] 
[[ZetaConnector.non-eth.sol#L87-L122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol
```


```solidity
52:    function onReceive(
53:        bytes calldata zetaTxSenderAddress,
54:        uint256 sourceChainId,
55:        address destinationAddress,
56:        uint256 zetaValue,
57:        bytes calldata message,
58:        bytes32 internalSendHash
59:    ) external override onlyTssAddress {
60:        bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:        if (!success) revert ZetaTransferError();
62:
63:        if (message.length > 0) {
64:            ZetaReceiver(destinationAddress).onZetaMessage(
65:                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:            );
67:        }
68:
69:        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70:    }
```

```solidity
77:    function onRevert(
78:        address zetaTxSenderAddress,
79:        uint256 sourceChainId,
80:        bytes calldata destinationAddress,
81:        uint256 destinationChainId,
82:        uint256 remainingZetaValue,
83:        bytes calldata message,
84:        bytes32 internalSendHash
85:    ) external override whenNotPaused onlyTssAddress {
86:        bool success = IERC20(zetaToken).transfer(zetaTxSenderAddress, remainingZetaValue);
87:        if (!success) revert ZetaTransferError();
88:
89:        if (message.length > 0) {
90:            ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
91:                ZetaInterfaces.ZetaRevert(
92:                    zetaTxSenderAddress,
93:                    sourceChainId,
94:                    destinationAddress,
95:                    destinationChainId,
96:                    remainingZetaValue,
97:                    message
98:                )
99:            );
100:        }
101:
102:        emit ZetaReverted(
103:            zetaTxSenderAddress,
104:            sourceChainId,
105:            destinationChainId,
106:            destinationAddress,
107:            remainingZetaValue,
108:            message,
109:            internalSendHash
110:        );
111:    }
```
[[ZetaConnector.eth.sol#L52-L70](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70)] 
[[ZetaConnector.eth.sol#L77-L111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L111)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol
```


```solidity
62:    function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
63:        /**
64:         * @dev Only Connector can mint. Minting requires burning the equivalent amount on another chain
65:         */
66:        if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
67:
68:        _mint(mintee, value);
69:
70:        emit Minted(mintee, value, internalSendHash);
71:    }
```
[[Zeta.non-eth.sol#L62-L71](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L71)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol
```


```solidity
54:    function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
55:        interactorsByChainId[destinationChainId] = contractAddress;
56:    }
```
[[ZetaInteractor.sol#L54-L56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L56)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/Interfaces.sol
```


```solidity
36:    function withdraw(bytes memory to, uint256 amount) external returns (bool);
```
[[Interfaces.sol#L36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L36)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol
```


```solidity
11:    function onCrossChainCall(
12:        zContext calldata context,
13:        address zrc20,
14:        uint256 amount,
15:        bytes calldata message
16:    ) external;
```
[[zContract.sol#L11-L16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L11-L16)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol
```


```solidity
16:    function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
17:        address token,
18:        uint liquidity,
19:        uint amountTokenMin,
20:        uint amountETHMin,
21:        address to,
22:        uint deadline,
23:        bool approveMax,
24:        uint8 v,
25:        bytes32 r,
26:        bytes32 s
27:    ) external returns (uint amountETH);
```
[[IUniswapV2Router02.sol#L16-L27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L16-L27)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol
```


```solidity
12:    function mint(address mintee, uint256 value, bytes32 internalSendHash) external;
```
[[ZetaNonEthInterface.sol#L12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L12)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
```


```solidity
25:    function withdraw(bytes memory to, uint256 amount) external returns (bool);
```
[[IZRC20.sol#L25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol#L25)] 
```
File:contracts/2023-11-zetachain/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol
```


```solidity
48:    function removeLiquidityWithPermit(
49:        address tokenA,
50:        address tokenB,
51:        uint liquidity,
52:        uint amountAMin,
53:        uint amountBMin,
54:        address to,
55:        uint deadline,
56:        bool approveMax,
57:        uint8 v,
58:        bytes32 r,
59:        bytes32 s
60:    ) external returns (uint amountA, uint amountB);
```

```solidity
62:    function removeLiquidityETHWithPermit(
63:        address token,
64:        uint liquidity,
65:        uint amountTokenMin,
66:        uint amountETHMin,
67:        address to,
68:        uint deadline,
69:        bool approveMax,
70:        uint8 v,
71:        bytes32 r,
72:        bytes32 s
73:    ) external returns (uint amountToken, uint amountETH);
```
[[IUniswapV2Router01.sol#L48-L60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L48-L60)] 
[[IUniswapV2Router01.sol#L62-L73](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L62-L73)] 
