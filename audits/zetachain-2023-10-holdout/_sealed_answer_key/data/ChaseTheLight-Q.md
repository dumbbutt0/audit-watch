## ChaseTheLight

### For: Code4rena ZetaChain

### Date: 2023-12-15

## Total findings: 98

### Total Low findings: 14

### Total NonCritical findings: 84

# Summary for Low findings

| Number | Details | Instances |
|----------|----------|----------|
| [Low-1] | Burn functions must be protected with a modifier  | 1 |
| [Low-2] | Missing events in sensitive functions  | 1 |
| [Low-3] | In functions which accept an address as a parameter, there should be a zero address check to prevent bugs | 7 |
| [Low-4] | Token supply should not be centralised at deployment | 1 |
| [Low-5] | Using > when declaring solidity version without specifying an upperbound can cause future vulnerabilities | 1 |
| [Low-6] | No limits when setting min/max amounts | 1 |
| [Low-7] | Missing zero address check in constructor | 5 |
| [Low-8] | Using zero as a parameter | 4 |
| [Low-10] | Revert on Transfer to the Zero Address | 1 |
| [Low-11] | Critical functions should have a timelock | 1 |
| [Low-12] | Vulnerable version of openzeppelin contracts used | 1 |
| [Low-13] | Inconsistent use of _msgSender() and msg.sender in contract | 1 |
| [Low-14] | Solidity version 0.8.20 won't work on all chains due to PUSH0 | 1 |
| [Low-15] | Contracts inherits pausable without utilising whenNotPaused | 1 |
# Summary for NonCritical findings

| Number | Details | Instances |
|----------|----------|----------|
| [NonCritical-1] | Emits without msg.sender parameter  | 22 |
| [NonCritical-2] | Code does not follow the best practice of check-effects-interaction  | 4 |
| [NonCritical-3] | Events may be emitted out of order due to code not follow the best practice of check-effects-interaction  | 6 |
| [NonCritical-4] | Getting a bool return value does not confirm the existence of a function in an external call  | 2 |
| [NonCritical-5] | Inconsistent comment spacing  | 3 |
| [NonCritical-6] | Employ Explicit Casting to Bytes or Bytes32 for Enhanced Code Clarity and Meaning  | 9 |
| [NonCritical-7] | Duplicated revert() checks should be refactored to a modifier or function  | 14 |
| [NonCritical-8] | Using Low-Level Call for Transfers | 2 |
| [NonCritical-9] | Require statements should have error string | 3 |
| [NonCritical-10] | Critical functions should be a two step procedure | 1 |
| [NonCritical-12] | Upgradeable contract uses non-upgradeable version of the OpenZeppelin libraries/contracts | 8 |
| [NonCritical-14] | Instances should be declared in a separate file | 7 |
| [NonCritical-15] | Open TODO in comments | 1 |
| [NonCritical-17] | Enum values should be used in place of constant array indexes | 15 |
| [NonCritical-18] | Empty receive functions can cause gas issues | 1 |
| [NonCritical-19] | Functions which are either private or internal should have a preceding _ in their name | 3 |
| [NonCritical-20] | Contract lines should not be longer than 120 characters for readability | 10 |
| [NonCritical-21] | Setters should prevent re-setting of the same value | 1 |
| [NonCritical-22] | Specific imports should be used where possible so only used code is imported | 29 |
| [NonCritical-23] | Use newer solidity versions | 6 |
| [NonCritical-24] | Not all event definitions are utilizing indexed variables. | 26 |
| [NonCritical-25] | Function names should differ to make the code more readable | 19 |
| [NonCritical-26] | uint variables should have the bit size defined explicitly | 33 |
| [NonCritical-27] | Functions within contracts are not ordered according to the solidity style guide | 4 |
| [NonCritical-28] | Use SafeCast to safely downcast variables | 4 |
| [NonCritical-29] | Functions which set address state variables should have zero address checks | 1 |
| [NonCritical-30] | Interface imports should be declared first | 5 |
| [NonCritical-31] | All interfaces used within a project should be imported | 1 |
| [NonCritical-32] | A function which defines named returns in it's declaration doesn't need to use return  | 3 |
| [NonCritical-33] | Constant/immutable state variables defined more than once | 7 |
| [NonCritical-34] | SPDX identifier should be the in the first line of a solidity file | 2 |
| [NonCritical-35] | Use allowlist/denylist rather than whitelist/blacklist | 12 |
| [NonCritical-36] | Multiple mappings can be replaced with a single struct mapping | 3 |
| [NonCritical-37] | Having chainId as a parameter can introduce cross chain replay attacks | 3 |
| [NonCritical-38] | Unused modifiers present | 2 |
| [NonCritical-39] | Constants should be on the left side of the  | 4 |
| [NonCritical-40] | Interface names should have an I as the first character | 19 |
| [NonCritical-41] | Both immutable and constant state variables should be CONSTANT_CASE | 18 |
| [NonCritical-42] | Consider using named mappings | 10 |
| [NonCritical-43] | Use type(uint<n>).max in place of 2 ** n - 1 | 1 |
| [NonCritical-44] | Use a single contract or library for system wide constants | 7 |
| [NonCritical-45] | Consider using modifiers for address control | 1 |
| [NonCritical-46] | Default address(0) can be returned | 1 |
| [NonCritical-47] | Mixed usage of int/uint with int256/uint256 | 43 |
| [NonCritical-48] | Custom error has no error variables | 12 |
| [NonCritical-49] | Event emit should emit a parameter | 1 |
| [NonCritical-50] | Unused structs present | 2 |
| [NonCritical-51] | Addresses shouldn't be hard-coded | 1 |
| [NonCritical-52] | Empty bytes check is missing | 10 |
| [NonCritical-53] | Return bool not explicit | 10 |
| [NonCritical-54] | Remove unnecessary solhint-disable | 1 |
| [NonCritical-55] | Do not use underscore at the end of variable name | 11 |
| [NonCritical-56] | Top level declarations should be separated by two blank lines | 16 |
| [NonCritical-57] | Use OpenZeppelin's ReentrancyGuard/ReentrancyGuardUpgradeable rather than writing your own | 1 |
| [NonCritical-58] | Consider using SafeTransferLib.safeTransferETH() or Address.sendValue() for clearer semantic meaning | 2 |
| [NonCritical-59] | Whitespace in expressions | 2 |
| [NonCritical-60] | Consider using named function calls | 17 |
| [NonCritical-61] | Revert should be used on some functions instead of return | 2 |
| [NonCritical-62] | Common functions should be refactored to a common base contract | 3 |
| [NonCritical-63] | Use of override is unnecessary | 13 |
| [NonCritical-64] | No access control on receive/payable fallback | 1 |
| [NonCritical-65] | If statement control structures do not comply with best practices | 51 |
| [NonCritical-66] | Incorrect withdraw declaration | 2 |
| [NonCritical-67] | Contract does not follow the Solidity style guide's suggested layout ordering | 2 |
| [NonCritical-68] | safeApprove()/approve() may revert if the current approval is not zero | 12 |
| [NonCritical-69] | Consider disallowing transfers to "address(this)" | 2 |
| [NonCritical-70] | Don't use assembly for create2 | 1 |
| [NonCritical-71] | Don't only depend on Solidity's arithmetic ordering. | 2 |
| [NonCritical-72] | It is best practice to use linear inheritance | 7 |
| [NonCritical-73] | Contracts with only unimplemented functions can be labeled as abstract | 3 |
| [NonCritical-74] | A event should be emitted if a non immutable state variable is set in a constructor | 5 |
| [NonCritical-75] | gasLimit should be uint64 | 4 |
| [NonCritical-76] | Mint functions should be accompanied by a burn function and vice versa | 1 |
| [NonCritical-77] | Avoid hard coding gasLimit values | 1 |
| [NonCritical-78] | Immutable and constant integer state variables should not be casted | 3 |
| [NonCritical-79] | Use the Modern Upgradeable Contract Paradigm | 16 |
| [NonCritical-80] | Use transfer libraries instead of low level calls | 2 |
| [NonCritical-81] | Use a struct to encapsulate multiple function parameters | 5 |
| [NonCritical-82] | Consider using ERC20Capped | 2 |
| [NonCritical-83] | Floating pragma defined inconsistently | 2 |
| [NonCritical-84] | package.json name variable should only consist of lowercase letters and underscores | 1 |
| [NonCritical-85] | Try catch statement without human readable error | 1 |
| [NonCritical-86] | Avoid revertible function calls in a constructor | 1 |
| [NonCritical-87] | Use the same Solidity version in non library/interface files throughout the project | 5 |
| [NonCritical-88] | Simplify complex revert statements | 3 |

## [NonCritical-1] Emits without msg.sender parameter 

### Resolution 
In Solidity, when `msg.sender` plays a crucial role in a function's logic, it's important for transparency and auditability that any events emitted by this function include `msg.sender` as a parameter. This practice enhances the traceability and accountability of transactions, allowing users and external observers to easily track who initiated a particular action. Including `msg.sender` in event logs helps in creating a clear and verifiable record of interactions with the contract, thereby increasing user trust and facilitating easier debugging and analysis of contract behavior. It's a key aspect of writing clear, transparent, and user-friendly smart contracts.

Num of instances: 22

### Findings 


<details><summary>Click to show findings</summary>

['[226](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226-L228)']
```solidity
225:     function deposit(address to, uint256 amount) external override returns (bool) {
226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender(); // <= FOUND
227:         _mint(to, amount);
228:         emit Deposit(abi.encodePacked(FUNGIBLE_MODULE_ADDRESS), to, amount); // <= FOUND
229:         return true;
230:     }

```
['[135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L135-L147)']
```solidity
126:     function getZetaFromToken(
127:         address destinationAddress,
128:         uint256 minAmountOut,
129:         address inputToken,
130:         uint256 inputTokenAmount
131:     ) external override returns (uint256) {
132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:         if (inputTokenAmount == 0) revert InputCantBeZero();
134: 
135:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
136:         IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);
137: 
138:         ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
140:             recipient: destinationAddress,
141:             amountIn: inputTokenAmount,
142:             amountOutMinimum: minAmountOut
143:         });
144: 
145:         uint256 amountOut = pancakeV3Router.exactInput(params);
146: 
147:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut); // <= FOUND
148:         return amountOut;
149:     }

```
['[108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L108-L132)']
```solidity
99:     function getZetaFromToken(
100:         address destinationAddress,
101:         uint256 minAmountOut,
102:         address inputToken,
103:         uint256 inputTokenAmount
104:     ) external override returns (uint256) {
105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:         if (inputTokenAmount == 0) revert InputCantBeZero();
107: 
108:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
109:         IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
110: 
111:         (address token0, address token1) = getPair(inputToken, WETH9Address);
112:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
113: 
114:         (token0, token1) = getPair(WETH9Address, zetaToken);
115:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
116: 
117:         address[] memory path = new address[](2);
118:         path[0] = pairPools1[0];
119:         path[1] = pairPools2[0];
120: 
121:         IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:             tokenIn: inputToken,
123:             amountIn: inputTokenAmount,
124:             amountOutMinimum: minAmountOut,
125:             path: path,
126:             to: destinationAddress,
127:             unwrap: false
128:         });
129: 
130:         uint256 amountOut = tridentRouter.exactInput(params);
131: 
132:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut); // <= FOUND
133:         return amountOut;
134:     }

```
['[107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L107-L120)']
```solidity
98:     function getZetaFromToken(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address inputToken,
102:         uint256 inputTokenAmount
103:     ) external override returns (uint256) {
104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:         if (inputTokenAmount == 0) revert InputCantBeZero();
106: 
107:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
108:         IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);
109: 
110:         ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:             deadline: block.timestamp + MAX_DEADLINE,
112:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
113:             recipient: destinationAddress,
114:             amountIn: inputTokenAmount,
115:             amountOutMinimum: minAmountOut
116:         });
117: 
118:         uint256 amountOut = uniswapV3Router.exactInput(params);
119: 
120:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut); // <= FOUND
121:         return amountOut;
122:     }

```
['[67](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L67-L91)']
```solidity
58:     function getZetaFromToken(
59:         address destinationAddress,
60:         uint256 minAmountOut,
61:         address inputToken,
62:         uint256 inputTokenAmount
63:     ) external override returns (uint256) {
64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:         if (inputTokenAmount == 0) revert InputCantBeZero();
66: 
67:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
68:         IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount);
69: 
70:         address[] memory path;
71:         if (inputToken == wETH) {
72:             path = new address[](2);
73:             path[0] = wETH;
74:             path[1] = zetaToken;
75:         } else {
76:             path = new address[](3);
77:             path[0] = inputToken;
78:             path[1] = wETH;
79:             path[2] = zetaToken;
80:         }
81: 
82:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:             inputTokenAmount,
84:             minAmountOut,
85:             path,
86:             destinationAddress,
87:             block.timestamp + MAX_DEADLINE
88:         );
89:         uint256 amountOut = amounts[path.length - 1];
90: 
91:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut); // <= FOUND
92:         return amountOut;
93:     }

```
['[159](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L159-L176)']
```solidity
151:     function getEthFromZeta(
152:         address destinationAddress,
153:         uint256 minAmountOut,
154:         uint256 zetaTokenAmount
155:     ) external override returns (uint256) {
156:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
157:         if (zetaTokenAmount == 0) revert InputCantBeZero();
158: 
159:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount); // <= FOUND
160:         IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
161: 
162:         ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
163:             tokenIn: zetaToken,
164:             tokenOut: WETH9Address,
165:             fee: zetaPoolFee,
166:             recipient: address(this),
167:             amountIn: zetaTokenAmount,
168:             amountOutMinimum: minAmountOut,
169:             sqrtPriceLimitX96: 0
170:         });
171: 
172:         uint256 amountOut = pancakeV3Router.exactInputSingle(params);
173: 
174:         WETH9(WETH9Address).withdraw(amountOut);
175: 
176:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut); // <= FOUND
177: 
178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
179:         if (!sent) revert ErrorSendingETH();
180: 
181:         return amountOut;
182:     }

```
['[144](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L144-L161)']
```solidity
136:     function getEthFromZeta(
137:         address destinationAddress,
138:         uint256 minAmountOut,
139:         uint256 zetaTokenAmount
140:     ) external override returns (uint256) {
141:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
142:         if (zetaTokenAmount == 0) revert InputCantBeZero();
143: 
144:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount); // <= FOUND
145:         IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
146: 
147:         (address token0, address token1) = getPair(zetaToken, WETH9Address);
148:         address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
149: 
150:         IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
151:             tokenIn: zetaToken,
152:             amountIn: zetaTokenAmount,
153:             amountOutMinimum: minAmountOut,
154:             pool: pairPools[0],
155:             to: destinationAddress,
156:             unwrap: true
157:         });
158: 
159:         uint256 amountOut = tridentRouter.exactInputSingle(params);
160: 
161:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut); // <= FOUND
162: 
163:         return amountOut;
164:     }

```
['[132](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L132-L150)']
```solidity
124:     function getEthFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         uint256 zetaTokenAmount
128:     ) external override returns (uint256) {
129:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
130:         if (zetaTokenAmount == 0) revert InputCantBeZero();
131: 
132:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount); // <= FOUND
133:         IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
134: 
135:         ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
136:             deadline: block.timestamp + MAX_DEADLINE,
137:             tokenIn: zetaToken,
138:             tokenOut: WETH9Address,
139:             fee: zetaPoolFee,
140:             recipient: address(this),
141:             amountIn: zetaTokenAmount,
142:             amountOutMinimum: minAmountOut,
143:             sqrtPriceLimitX96: 0
144:         });
145: 
146:         uint256 amountOut = uniswapV3Router.exactInputSingle(params);
147: 
148:         WETH9(WETH9Address).withdraw(amountOut);
149: 
150:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut); // <= FOUND
151: 
152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
153:         if (!sent) revert ErrorSendingETH();
154: 
155:         return amountOut;
156:     }

```
['[103](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L103-L120)']
```solidity
95:     function getEthFromZeta(
96:         address destinationAddress,
97:         uint256 minAmountOut,
98:         uint256 zetaTokenAmount
99:     ) external override returns (uint256) {
100:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
101:         if (zetaTokenAmount == 0) revert InputCantBeZero();
102: 
103:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount); // <= FOUND
104:         IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
105: 
106:         address[] memory path = new address[](2);
107:         path[0] = zetaToken;
108:         path[1] = wETH;
109: 
110:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForETH(
111:             zetaTokenAmount,
112:             minAmountOut,
113:             path,
114:             destinationAddress,
115:             block.timestamp + MAX_DEADLINE
116:         );
117: 
118:         uint256 amountOut = amounts[path.length - 1];
119: 
120:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut); // <= FOUND
121:         return amountOut;
122:     }

```
['[193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L193-L205)']
```solidity
184:     function getTokenFromZeta(
185:         address destinationAddress,
186:         uint256 minAmountOut,
187:         address outputToken,
188:         uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {
190:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
191:         if (zetaTokenAmount == 0) revert InputCantBeZero();
192: 
193:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount); // <= FOUND
194:         IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
195: 
196:         ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
197:             path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
198:             recipient: destinationAddress,
199:             amountIn: zetaTokenAmount,
200:             amountOutMinimum: minAmountOut
201:         });
202: 
203:         uint256 amountOut = pancakeV3Router.exactInput(params);
204: 
205:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut); // <= FOUND
206:         return amountOut;
207:     }

```
['[175](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L175-L199)']
```solidity
166:     function getTokenFromZeta(
167:         address destinationAddress,
168:         uint256 minAmountOut,
169:         address outputToken,
170:         uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {
172:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
173:         if (zetaTokenAmount == 0) revert InputCantBeZero();
174: 
175:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount); // <= FOUND
176:         IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
177: 
178:         (address token0, address token1) = getPair(zetaToken, WETH9Address);
179:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
180: 
181:         (token0, token1) = getPair(WETH9Address, outputToken);
182:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
183: 
184:         address[] memory path = new address[](2);
185:         path[0] = pairPools1[0];
186:         path[1] = pairPools2[0];
187: 
188:         IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
189:             tokenIn: zetaToken,
190:             amountIn: zetaTokenAmount,
191:             amountOutMinimum: minAmountOut,
192:             path: path,
193:             to: destinationAddress,
194:             unwrap: false
195:         });
196: 
197:         uint256 amountOut = tridentRouter.exactInput(params);
198: 
199:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut); // <= FOUND
200:         return amountOut;
201:     }

```
['[167](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L167-L180)']
```solidity
158:     function getTokenFromZeta(
159:         address destinationAddress,
160:         uint256 minAmountOut,
161:         address outputToken,
162:         uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {
164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
165:         if (zetaTokenAmount == 0) revert InputCantBeZero();
166: 
167:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount); // <= FOUND
168:         IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
169: 
170:         ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
171:             deadline: block.timestamp + MAX_DEADLINE,
172:             path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
173:             recipient: destinationAddress,
174:             amountIn: zetaTokenAmount,
175:             amountOutMinimum: minAmountOut
176:         });
177: 
178:         uint256 amountOut = uniswapV3Router.exactInput(params);
179: 
180:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut); // <= FOUND
181:         return amountOut;
182:     }

```
['[178](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L178-L184)']
```solidity
165:     function deposit(
166:         bytes calldata recipient,
167:         IERC20 asset,
168:         uint256 amount,
169:         bytes calldata message
170:     ) external nonReentrant {
171:         if (paused) {
172:             revert IsPaused();
173:         }
174:         if (!whitelisted[asset]) {
175:             revert NotWhitelisted();
176:         }
177:         if (zetaFee != 0 && address(zeta) != address(0)) {
178:             zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee); // <= FOUND
179:         }
180:         uint256 oldBalance = asset.balanceOf(address(this));
181:         asset.safeTransferFrom(msg.sender, address(this), amount); // <= FOUND
182:         
183:         
184:         emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message); // <= FOUND
185:     }

```
['[133](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L133-L158)']
```solidity
124:     function getTokenFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         address outputToken,
128:         uint256 zetaTokenAmount
129:     ) external override returns (uint256) {
130:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
131:         if (zetaTokenAmount == 0) revert InputCantBeZero();
132: 
133:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount); // <= FOUND
134:         IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount);
135: 
136:         address[] memory path;
137:         if (outputToken == wETH) {
138:             path = new address[](2);
139:             path[0] = zetaToken;
140:             path[1] = wETH;
141:         } else {
142:             path = new address[](3);
143:             path[0] = zetaToken;
144:             path[1] = wETH;
145:             path[2] = outputToken;
146:         }
147: 
148:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
149:             zetaTokenAmount,
150:             minAmountOut,
151:             path,
152:             destinationAddress,
153:             block.timestamp + MAX_DEADLINE
154:         );
155: 
156:         uint256 amountOut = amounts[path.length - 1];
157: 
158:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut); // <= FOUND
159:         return amountOut;
160:     }

```
['[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L124-L126)']
```solidity
123:     function setGasPrice(uint256 chainID, uint256 price) external {
124:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule(); // <= FOUND
125:         gasPriceByChainId[chainID] = price;
126:         emit SetGasPrice(chainID, price); // <= FOUND
127:     }

```
['[135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L135-L137)']
```solidity
134:     function setGasCoinZRC20(uint256 chainID, address zrc20) external {
135:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule(); // <= FOUND
136:         gasCoinZRC20ByChainId[chainID] = zrc20;
137:         emit SetGasCoin(chainID, zrc20); // <= FOUND
138:     }

```
['[146](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L146-L149)']
```solidity
145:     function setGasZetaPool(uint256 chainID, address erc20) external {
146:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule(); // <= FOUND
147:         address pool = uniswapv2PairFor(uniswapv2FactoryAddress, wZetaContractAddress, erc20);
148:         gasZetaPoolByChainId[chainID] = pool;
149:         emit SetGasZetaPool(chainID, pool); // <= FOUND
150:     }

```
['[157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L157-L160)']
```solidity
156:     function setWZETAContractAddress(address addr) external {
157:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule(); // <= FOUND
158:         if (addr == address(0)) revert ZeroAddress();
159:         wZetaContractAddress = addr;
160:         emit SetWZeta(wZetaContractAddress); // <= FOUND
161:     }

```
['[168](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L168-L171)']
```solidity
167:     function setConnectorZEVMAddress(address addr) external {
168:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule(); // <= FOUND
169:         if (addr == address(0)) revert ZeroAddress();
170:         zetaConnectorZEVMAddress = addr;
171:         emit SetConnectorZEVM(zetaConnectorZEVMAddress); // <= FOUND
172:     }

```
['[115](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115-L117)']
```solidity
114:     function setWzetaAddress(address wzeta_) external {
115:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule(); // <= FOUND
116:         wzeta = wzeta_;
117:         emit SetWZETA(wzeta_); // <= FOUND
118:     }

```
['[66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L66-L70)']
```solidity
62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
63:         
64: 
66:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender); // <= FOUND
67: 
68:         _mint(mintee, value);
69: 
70:         emit Minted(mintee, value, internalSendHash); // <= FOUND
71:     }

```
['[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L77-L81)']
```solidity
73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) {
74:         
75: 
77:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender); // <= FOUND
78: 
79:         ERC20Burnable.burnFrom(account, amount);
80: 
81:         emit Burnt(account, amount); // <= FOUND
82:     }

```


</details>

## [NonCritical-2] Code does not follow the best practice of check-effects-interaction 

### Resolution 
The "check-effects-interaction" pattern is a best practice in smart contract development, emphasizing the order of operations in functions to prevent reentrancy attacks. Violations arise when a function interacts with external contracts before settling internal state changes or checks. This misordering can expose the contract to potential threats. To adhere to this pattern, first ensure all conditions or checks are satisfied, then update any internal states, and only after these steps, interact with external contracts or addresses. Rearranging operations to this recommended sequence bolsters contract security and aligns with established best practices in the Ethereum community.

Num of instances: 4

### Findings 


<details><summary>Click to show findings</summary>

['[126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L136)']
```solidity
126:     function getZetaFromToken(
127:         address destinationAddress,
128:         uint256 minAmountOut,
129:         address inputToken,
130:         uint256 inputTokenAmount
131:     ) external override returns (uint256) {
132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:         if (inputTokenAmount == 0) revert InputCantBeZero();
134: 
135:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
136:         IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount); // <= FOUND
137: 
138:         ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
140:             recipient: destinationAddress,
141:             amountIn: inputTokenAmount,
142:             amountOutMinimum: minAmountOut
143:         });
144: 
145:         uint256 amountOut = pancakeV3Router.exactInput(params);
146: 
147:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148:         return amountOut;
149:     }

```
['[99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L109)']
```solidity
99:     function getZetaFromToken(
100:         address destinationAddress,
101:         uint256 minAmountOut,
102:         address inputToken,
103:         uint256 inputTokenAmount
104:     ) external override returns (uint256) {
105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:         if (inputTokenAmount == 0) revert InputCantBeZero();
107: 
108:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
109:         IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount); // <= FOUND
110: 
111:         (address token0, address token1) = getPair(inputToken, WETH9Address);
112:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
113: 
114:         (token0, token1) = getPair(WETH9Address, zetaToken);
115:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
116: 
117:         address[] memory path = new address[](2);
118:         path[0] = pairPools1[0];
119:         path[1] = pairPools2[0];
120: 
121:         IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:             tokenIn: inputToken,
123:             amountIn: inputTokenAmount,
124:             amountOutMinimum: minAmountOut,
125:             path: path,
126:             to: destinationAddress,
127:             unwrap: false
128:         });
129: 
130:         uint256 amountOut = tridentRouter.exactInput(params);
131: 
132:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133:         return amountOut;
134:     }

```
['[98](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L108)']
```solidity
98:     function getZetaFromToken(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address inputToken,
102:         uint256 inputTokenAmount
103:     ) external override returns (uint256) {
104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:         if (inputTokenAmount == 0) revert InputCantBeZero();
106: 
107:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
108:         IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount); // <= FOUND
109: 
110:         ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:             deadline: block.timestamp + MAX_DEADLINE,
112:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
113:             recipient: destinationAddress,
114:             amountIn: inputTokenAmount,
115:             amountOutMinimum: minAmountOut
116:         });
117: 
118:         uint256 amountOut = uniswapV3Router.exactInput(params);
119: 
120:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121:         return amountOut;
122:     }

```
['[58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L68)']
```solidity
58:     function getZetaFromToken(
59:         address destinationAddress,
60:         uint256 minAmountOut,
61:         address inputToken,
62:         uint256 inputTokenAmount
63:     ) external override returns (uint256) {
64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:         if (inputTokenAmount == 0) revert InputCantBeZero();
66: 
67:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
68:         IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount); // <= FOUND
69: 
70:         address[] memory path;
71:         if (inputToken == wETH) {
72:             path = new address[](2);
73:             path[0] = wETH;
74:             path[1] = zetaToken;
75:         } else {
76:             path = new address[](3);
77:             path[0] = inputToken;
78:             path[1] = wETH;
79:             path[2] = zetaToken;
80:         }
81: 
82:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:             inputTokenAmount,
84:             minAmountOut,
85:             path,
86:             destinationAddress,
87:             block.timestamp + MAX_DEADLINE
88:         );
89:         uint256 amountOut = amounts[path.length - 1];
90: 
91:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92:         return amountOut;
93:     }

```


</details>

## [NonCritical-3] Events may be emitted out of order due to code not follow the best practice of check-effects-interaction 

### Resolution 
The "check-effects-interaction" pattern also impacts event ordering. When a contract doesn't adhere to this pattern, events might be emitted in a sequence that doesn't reflect the actual logical flow of operations. This can cause confusion during event tracking, potentially leading to erroneous off-chain interpretations. To rectify this, always ensure that checks are performed first, state modifications come next, and interactions with external contracts or addresses are done last. This will ensure events are emitted in a logical, consistent manner, providing a clear and accurate chronological record of on-chain actions for off-chain systems and observers.

Num of instances: 6

### Findings 


<details><summary>Click to show findings</summary>

['[126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L147)']
```solidity
126:     function getZetaFromToken(
127:         address destinationAddress,
128:         uint256 minAmountOut,
129:         address inputToken,
130:         uint256 inputTokenAmount
131:     ) external override returns (uint256) {
132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:         if (inputTokenAmount == 0) revert InputCantBeZero();
134: 
135:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
136:         IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount); // <= FOUND
137: 
138:         ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
140:             recipient: destinationAddress,
141:             amountIn: inputTokenAmount,
142:             amountOutMinimum: minAmountOut
143:         });
144: 
145:         uint256 amountOut = pancakeV3Router.exactInput(params);
146: 
147:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut); // <= FOUND
148:         return amountOut;
149:     }

```
['[99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L132)']
```solidity
99:     function getZetaFromToken(
100:         address destinationAddress,
101:         uint256 minAmountOut,
102:         address inputToken,
103:         uint256 inputTokenAmount
104:     ) external override returns (uint256) {
105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:         if (inputTokenAmount == 0) revert InputCantBeZero();
107: 
108:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
109:         IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount); // <= FOUND
110: 
111:         (address token0, address token1) = getPair(inputToken, WETH9Address);
112:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
113: 
114:         (token0, token1) = getPair(WETH9Address, zetaToken);
115:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
116: 
117:         address[] memory path = new address[](2);
118:         path[0] = pairPools1[0];
119:         path[1] = pairPools2[0];
120: 
121:         IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:             tokenIn: inputToken,
123:             amountIn: inputTokenAmount,
124:             amountOutMinimum: minAmountOut,
125:             path: path,
126:             to: destinationAddress,
127:             unwrap: false
128:         });
129: 
130:         uint256 amountOut = tridentRouter.exactInput(params);
131: 
132:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut); // <= FOUND
133:         return amountOut;
134:     }

```
['[98](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L120)']
```solidity
98:     function getZetaFromToken(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address inputToken,
102:         uint256 inputTokenAmount
103:     ) external override returns (uint256) {
104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:         if (inputTokenAmount == 0) revert InputCantBeZero();
106: 
107:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
108:         IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount); // <= FOUND
109: 
110:         ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:             deadline: block.timestamp + MAX_DEADLINE,
112:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
113:             recipient: destinationAddress,
114:             amountIn: inputTokenAmount,
115:             amountOutMinimum: minAmountOut
116:         });
117: 
118:         uint256 amountOut = uniswapV3Router.exactInput(params);
119: 
120:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut); // <= FOUND
121:         return amountOut;
122:     }

```
['[58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L91)']
```solidity
58:     function getZetaFromToken(
59:         address destinationAddress,
60:         uint256 minAmountOut,
61:         address inputToken,
62:         uint256 inputTokenAmount
63:     ) external override returns (uint256) {
64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:         if (inputTokenAmount == 0) revert InputCantBeZero();
66: 
67:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount); // <= FOUND
68:         IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount); // <= FOUND
69: 
70:         address[] memory path;
71:         if (inputToken == wETH) {
72:             path = new address[](2);
73:             path[0] = wETH;
74:             path[1] = zetaToken;
75:         } else {
76:             path = new address[](3);
77:             path[0] = inputToken;
78:             path[1] = wETH;
79:             path[2] = zetaToken;
80:         }
81: 
82:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:             inputTokenAmount,
84:             minAmountOut,
85:             path,
86:             destinationAddress,
87:             block.timestamp + MAX_DEADLINE
88:         );
89:         uint256 amountOut = amounts[path.length - 1];
90: 
91:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut); // <= FOUND
92:         return amountOut;
93:     }

```
['[61](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L61-L78)']
```solidity
61:     function onReceive(
62:         bytes calldata zetaTxSenderAddress,
63:         uint256 sourceChainId,
64:         address destinationAddress,
65:         uint256 zetaValue,
66:         bytes calldata message,
67:         bytes32 internalSendHash
68:     ) external override onlyTssAddress {
69:         if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
70:         ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);
71: 
72:         if (message.length > 0) {
73:             ZetaReceiver(destinationAddress).onZetaMessage( // <= FOUND
74:                 ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
75:             );
76:         }
77: 
78:         emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash); // <= FOUND
79:     }

```
['[52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L69)']
```solidity
52:     function onReceive(
53:         bytes calldata zetaTxSenderAddress,
54:         uint256 sourceChainId,
55:         address destinationAddress,
56:         uint256 zetaValue,
57:         bytes calldata message,
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress {
60:         bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:         if (!success) revert ZetaTransferError();
62: 
63:         if (message.length > 0) {
64:             ZetaReceiver(destinationAddress).onZetaMessage( // <= FOUND
65:                 ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:             );
67:         }
68: 
69:         emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash); // <= FOUND
70:     }

```


</details>

## [NonCritical-4] Getting a bool return value does not confirm the existence of a function in an external call 

### Resolution 
External calls to contracts using `address.call()` might return a boolean indicating success or failure. However, this boolean doesn't guarantee the existence of a called function. If a function isn't present, the call won't revert but will simply return `false`. This behavior might lead developers into mistakenly believing they're interacting with a legitimate or expected function, whereas it might not exist at all—a scenario sometimes termed as "phantom functions". Resolution: Instead of solely relying on the boolean, further validate the contract you're interacting with, or use interfaces or abstract contracts to enforce the existence of expected functions.

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['']
```solidity
     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused { // <= FOUND
         bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas); // <= FOUND
         if (!success) revert ZetaTransferError();
         emit ZetaSent(  tx.origin,  msg.sender,  input.destinationChainId,  input.destinationAddress,  input.zetaValueAndGas,  input.destinationGasLimit,  input.message,  input.zetaParams );
     }

```
['']
```solidity
     function onReceive(  bytes calldata zetaTxSenderAddress,  uint256 sourceChainId,  address destinationAddress,  uint256 zetaValue,  bytes calldata message,  bytes32 internalSendHash ) external override onlyTssAddress {
         bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue); // <= FOUND
         if (!success) revert ZetaTransferError();
         if (message.length > 0) {             ZetaReceiver(destinationAddress).onZetaMessage(  ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message) );
         }
         emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
     }

```


</details>

## [NonCritical-5] Inconsistent comment spacing 

### Resolution 
Some comments use // X and others //X Amend comments to use only use // X or //X consistently

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[191](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L191-L191)']
```solidity
191: //@dev: if pool does exist, get its liquidity

```
['[204](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L204-L204)']
```solidity
204: //@TODO: Implement

```
['[1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L1-L1)']
```solidity
1: //SPDX-License-Identifier: MIT

```


</details>

## [Low-1] Burn functions must be protected with a modifier 

### Resolution 
In Solidity, implementing a burn function requires careful security considerations, as it involves permanently reducing the token supply. It's crucial to protect these functions with appropriate modifiers to prevent unauthorized access. Typically, access control mechanisms like `onlyOwner` or custom modifiers based on specific business logic are used. These modifiers ensure that only authorized addresses can execute the burn function, safeguarding against malicious attempts to disrupt the token's economy. Failing to restrict access to burn functions can lead to unintended token supply manipulation, potentially compromising the token's value and the integrity of the project. Proper implementation of access controls is vital for maintaining a secure and stable token ecosystem.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[173](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173-L173)']
```solidity
173:     function burn(uint256 amount) external returns (bool) { // <= FOUND
174:         _burn(msg.sender, amount);
175:         return true;
176:     }

```


</details>

## [NonCritical-6] Employ Explicit Casting to Bytes or Bytes32 for Enhanced Code Clarity and Meaning 

### Resolution 
Smart contracts are complex entities, and clarity in their operations is fundamental to ensure that they function as intended. Casting a single argument instead of utilizing 'abi.encodePacked()' improves the transparency of the operation. It elucidates the intent of the code, reducing ambiguity and making it easier for auditors and developers to understand the code’s purpose. Such practices promote readability and maintainability, thus reducing the likelihood of errors and misunderstandings. Therefore, it's recommended to employ explicit casts for single arguments where possible, to increase the contract's comprehensibility and ensure a smoother review process.

Num of instances: 9

### Findings 


<details><summary>Click to show findings</summary>

['[228](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L228-L228)']
```solidity
225:     function deposit(address to, uint256 amount) external override returns (bool) {
226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();
227:         _mint(to, amount);
228:         emit Deposit(abi.encodePacked(FUNGIBLE_MODULE_ADDRESS), to, amount); // <= FOUND
229:         return true;
230:     }

```
['[139](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L139-L139)']
```solidity
126:     function getZetaFromToken(
127:         address destinationAddress,
128:         uint256 minAmountOut,
129:         address inputToken,
130:         uint256 inputTokenAmount
131:     ) external override returns (uint256) {
132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:         if (inputTokenAmount == 0) revert InputCantBeZero();
134: 
135:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
136:         IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount);
137: 
138:         ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken), // <= FOUND
140:             recipient: destinationAddress,
141:             amountIn: inputTokenAmount,
142:             amountOutMinimum: minAmountOut
143:         });
144: 
145:         uint256 amountOut = pancakeV3Router.exactInput(params);
146: 
147:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148:         return amountOut;
149:     }

```
['[197](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L197-L197)']
```solidity
184:     function getTokenFromZeta(
185:         address destinationAddress,
186:         uint256 minAmountOut,
187:         address outputToken,
188:         uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {
190:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
191:         if (zetaTokenAmount == 0) revert InputCantBeZero();
192: 
193:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
194:         IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount);
195: 
196:         ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
197:             path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken), // <= FOUND
198:             recipient: destinationAddress,
199:             amountIn: zetaTokenAmount,
200:             amountOutMinimum: minAmountOut
201:         });
202: 
203:         uint256 amountOut = pancakeV3Router.exactInput(params);
204: 
205:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
206:         return amountOut;
207:     }

```
['[112](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L112-L112)']
```solidity
98:     function getZetaFromToken(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address inputToken,
102:         uint256 inputTokenAmount
103:     ) external override returns (uint256) {
104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:         if (inputTokenAmount == 0) revert InputCantBeZero();
106: 
107:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
108:         IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);
109: 
110:         ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:             deadline: block.timestamp + MAX_DEADLINE,
112:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken), // <= FOUND
113:             recipient: destinationAddress,
114:             amountIn: inputTokenAmount,
115:             amountOutMinimum: minAmountOut
116:         });
117: 
118:         uint256 amountOut = uniswapV3Router.exactInput(params);
119: 
120:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121:         return amountOut;
122:     }

```
['[172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L172-L172)']
```solidity
158:     function getTokenFromZeta(
159:         address destinationAddress,
160:         uint256 minAmountOut,
161:         address outputToken,
162:         uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {
164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
165:         if (zetaTokenAmount == 0) revert InputCantBeZero();
166: 
167:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
168:         IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
169: 
170:         ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
171:             deadline: block.timestamp + MAX_DEADLINE,
172:             path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken), // <= FOUND
173:             recipient: destinationAddress,
174:             amountIn: zetaTokenAmount,
175:             amountOutMinimum: minAmountOut
176:         });
177: 
178:         uint256 amountOut = uniswapV3Router.exactInput(params);
179: 
180:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
181:         return amountOut;
182:     }

```
['[38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L38-L42)']
```solidity
26:     function safeCreate2Internal(
27:         bytes32 salt,
28:         bytes memory initializationCode
29:     ) internal returns (address deploymentAddress) {
30:         
31:         bytes memory initCode = initializationCode;
32: 
33:         
34:         address targetDeploymentAddress = address(
35:             uint160( 
36:                 uint256( 
37:                     keccak256( 
38:                         abi.encodePacked(  // <= FOUND
39:                             hex"ff", 
40:                             address(this), 
41:                             salt, 
42:                             keccak256(abi.encodePacked(initCode))  // <= FOUND
43:                         )
44:                     )
45:                 )
46:             )
47:         );
48: 
49:         
50:         require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
51: 
52:         
53:         assembly {
54:             
55:             let encoded_data := add(0x20, initCode) 
56:             let encoded_size := mload(initCode) 
57:             deploymentAddress := create2(
58:                 
59:                 callvalue, 
60:                 encoded_data, 
61:                 encoded_size, 
62:                 salt 
63:             )
64:         }
65: 
66:         
67:         require(
68:             deploymentAddress == targetDeploymentAddress,
69:             "Failed to deploy contract using provided salt and initialization code."
70:         );
71: 
72:         
73:         _deployed[deploymentAddress] = true;
74:     }

```
['[117](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L117-L121)']
```solidity
108:     function findCreate2Address(
109:         bytes32 salt,
110:         bytes calldata initCode
111:     ) external view returns (address deploymentAddress) {
112:         
113:         deploymentAddress = address(
114:             uint160( 
115:                 uint256( 
116:                     keccak256( 
117:                         abi.encodePacked(  // <= FOUND
118:                             hex"ff", 
119:                             address(this), 
120:                             salt, 
121:                             keccak256(abi.encodePacked(initCode))  // <= FOUND
122:                         )
123:                     )
124:                 )
125:             )
126:         );
127: 
128:         
129:         if (_deployed[deploymentAddress]) {
130:             return address(0);
131:         }
132:     }

```
['[157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L157-L157)']
```solidity
148:     function findCreate2AddressViaHash(
149:         bytes32 salt,
150:         bytes32 initCodeHash
151:     ) external view returns (address deploymentAddress) {
152:         
153:         deploymentAddress = address(
154:             uint160( 
155:                 uint256( 
156:                     keccak256( 
157:                         abi.encodePacked(  // <= FOUND
158:                             hex"ff", 
159:                             address(this), 
160:                             salt, 
161:                             initCodeHash 
162:                         )
163:                     )
164:                 )
165:             )
166:         );
167: 
168:         
169:         if (_deployed[deploymentAddress]) {
170:             return address(0);
171:         }
172:     }

```
['[106](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L106-L109)']
```solidity
100:     function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {
101:         (address token0, address token1) = sortTokens(tokenA, tokenB);
102:         pair = address(
103:             uint160(
104:                 uint256(
105:                     keccak256(
106:                         abi.encodePacked( // <= FOUND
107:                             hex"ff",
108:                             factory,
109:                             keccak256(abi.encodePacked(token0, token1)), // <= FOUND
110:                             hex"96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f" 
111:                         )
112:                     )
113:                 )
114:             )
115:         );
116:     }

```


</details>

## [NonCritical-7] Duplicated revert() checks should be refactored to a modifier or function 

Num of instances: 14

### Findings 


<details><summary>Click to show findings</summary>

['[53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53-L53)']
```solidity
53:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule(); // <= FOUND

```
['[192](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L192-L192)']
```solidity
192:         if (account == address(0)) revert ZeroAddress(); // <= FOUND

```
['[66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L66-L66)']
```solidity
66:         if (_locked) revert ReentrancyError(); // <= FOUND

```
['[78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L78-L78)']
```solidity
78:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79-L79)']
```solidity
79:         if (msg.value == 0) revert InputCantBeZero(); // <= FOUND

```
['[104](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104-L104)']
```solidity
104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[105](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105-L105)']
```solidity
105:         if (inputTokenAmount == 0) revert InputCantBeZero(); // <= FOUND

```
['[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130-L130)']
```solidity
130:         if (zetaTokenAmount == 0) revert InputCantBeZero(); // <= FOUND

```
['[153](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L153-L153)']
```solidity
153:         if (!sent) revert ErrorSendingETH(); // <= FOUND

```
['[164](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164-L164)']
```solidity
164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L55-L55)']
```solidity
55:         if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender); // <= FOUND

```
['[158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L158-L158)']
```solidity
158:         if (addr == address(0)) revert ZeroAddress(); // <= FOUND

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L33-L33)']
```solidity
33:         if (!success) revert ZetaTransferError(); // <= FOUND

```
['']
```solidity
66:         
67: 
69:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);

```


</details>

## [Low-2] Missing events in sensitive functions 

### Resolution 
Sensitive setter functions in smart contracts often alter critical state variables. Without events emitted in these functions, external observers or dApps cannot easily track or react to these state changes. Missing events can obscure contract activity, hampering transparency and making integration more challenging. To resolve this, incorporate appropriate event emissions within these functions. Events offer an efficient way to log crucial changes, aiding in real-time tracking and post-transaction verification.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)']
```solidity
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner { // <= FOUND
55:         interactorsByChainId[destinationChainId] = contractAddress;
56:     }

```


</details>

## [NonCritical-8] Using Low-Level Call for Transfers

### Resolution 
Utilizing low-level calls like `.call{value: value}` for Ether transfers in Ethereum can be risky, as it can inadvertently allow malicious contract executions through fallback functions. To mitigate these risks and ensure safer Ether transfers, it is recommended to adopt more secure and explicit methods provided by reputable libraries such as OpenZeppelin. Functions like `Address.sendValue()` from OpenZeppelin provide a clearer and safer alternative for sending Ether, as they encapsulate necessary checks and error handling, ensuring that Ether is transferred securely and any errors are appropriately dealt with. This not only enhances the security of your smart contract but also improves code readability and maintainability, aligning with modern Solidity development practices.

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[152](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152-L153)']
```solidity
152: 
153:         (bool sent, ) = destinationAddress.call{value: amountOut}(""); // <= FOUND

```
['[96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96-L96)']
```solidity
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}(""); // <= FOUND

```


</details>

## [NonCritical-9] Require statements should have error string

### Resolution 
Adding error strings to require statements in Solidity contracts, although not mandatory, enhances error handling, debugging, and overall contract maintainability. Providing a descriptive error message with each require statement helps identify the specific reason for a transaction failure, making it easier for developers to troubleshoot issues and for users to understand the cause of a revert. Including error strings improves code readability and fosters transparency, as the logic and conditions behind each requirement are clearly communicated

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L26-L26)']
```solidity
26: require(balanceOf[msg.sender] >= wad);

```
['[47](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L47-L47)']
```solidity
47: require(balanceOf[src] >= wad);

```
['[50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L50-L50)']
```solidity
50: require(allowance[src][msg.sender] >= wad);

```


</details>

## [Low-3] In functions which accept an address as a parameter, there should be a zero address check to prevent bugs

### Resolution 
Implement a zero address check to ensure input isn't the zero address

Num of instances: 7

### Findings 


<details><summary>Click to show findings</summary>

['[125](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125-L125)']
```solidity
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) 

```
['[145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145-L145)']
```solidity
145:     function approve(address spender, uint256 amount) public virtual override returns (bool) 

```
['[270](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L270-L270)']
```solidity
270:     function updateSystemContractAddress(address addr) external onlyFungible 

```
['[172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L172)']
```solidity
172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual 

```
['[185](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L185)']
```solidity
185:     function onRevert(
186:         address zetaTxSenderAddress,
187:         uint256 sourceChainId,
188:         bytes calldata destinationAddress,
189:         uint256 destinationChainId,
190:         uint256 remainingZetaValue,
191:         bytes calldata message,
192:         bytes32 internalSendHash
193:     ) external virtual 

```
['[36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36-L36)']
```solidity
36:     function approve(address guy, uint wad) public returns (bool) 

```
['[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L42-L42)']
```solidity
42:     function transfer(address dst, uint wad) public returns (bool) 

```


</details>

## [Low-4] Token supply should not be centralised at deployment

### Resolution 
Avoid minting tokens to a single address on deployment, rather have them distributed as intended within the constructor (i.e liquidity pools)

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L11-L11)']
```solidity
10:     constructor(address creator, uint256 initialSupply) {
11:         _mint(creator, initialSupply * (10 ** uint256(decimals()))); // <= FOUND
12:     }

```


</details>

## [Low-5] Using > when declaring solidity version without specifying an upperbound can cause future vulnerabilities

### Resolution 
Such instances should be locked to a particular solidity version or use the ^ attribute instead of > as this is more limited in what versions can be used.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L13-L13)']
```solidity
13: pragma solidity >=0.8.0; // <= FOUND

```


</details>

## [Low-6] No limits when setting min/max amounts

### Resolution 
When settings min/max state variables, ensure there a require checks in place to prevent incorrect values from being set

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31-L31)']
```solidity
31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
32:         maxSupply = maxSupply_;
33:         emit MaxSupplyUpdated(msg.sender, maxSupply_);
34:     }

```


</details>

## [Low-7] Missing zero address check in constructor

### Resolution 
In Solidity, constructors often take address parameters to initialize important components of a contract, such as owner or linked contracts. However, without a check, there's a risk that an address parameter could be mistakenly set to the zero address (0x0). This could occur due to a mistake or oversight during contract deployment. A zero address in a crucial role can cause serious issues, as it cannot perform actions like a normal address, and any funds sent to it are irretrievable. Therefore, it's crucial to include a zero address check in constructors to prevent such potential problems. If a zero address is detected, the constructor should revert the transaction.

Num of instances: 5

### Findings 


<details><summary>Click to show findings</summary>

['[67](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L67-L67)']
```solidity
60:     constructor(
61:         string memory name_,
62:         string memory symbol_,
63:         uint8 decimals_,
64:         uint256 chainid_,
65:         CoinType coinType_,
66:         uint256 gasLimit_,
67:         address systemContractAddress_ // <= FOUND
68:     ) {
69:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:         _name = name_;
71:         _symbol = symbol_;
72:         _decimals = decimals_;
73:         CHAIN_ID = chainid_;
74:         COIN_TYPE = coinType_;
75:         GAS_LIMIT = gasLimit_;
76:         SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:     }

```
['[68](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L68)']
```solidity
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) { // <= FOUND
69:         TSSAddress = TSSAddress_;
70:         TSSAddressUpdater = TSSAddressUpdater_;
71:         zetaFee = zetaFee_;
72:         zeta = zeta_;
73:         zetaMaxFee = zetaMaxFee_;
74:     }

```
['[51](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51-L51)']
```solidity
51:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) { // <= FOUND
52:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
53:         wZetaContractAddress = wzeta_;
54:         uniswapv2FactoryAddress = uniswapv2Factory_;
55:         uniswapv2Router02Address = uniswapv2Router02_;
56:         emit SystemContractDeployed();
57:     }

```
['[79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L79)']
```solidity
79:     constructor(address wzeta_) { // <= FOUND
80:         wzeta = wzeta_;
81:     }

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L10-L10)']
```solidity
10:     constructor(address creator, uint256 initialSupply) { // <= FOUND
11:         _mint(creator, initialSupply * (10 ** uint256(decimals())));
12:     }

```


</details>

## [Low-8] Using zero as a parameter

### Resolution 
Taking 0 as a valid argument in Solidity without checks can lead to severe security issues. A historical example is the infamous 0x0 address bug where numerous tokens were lost. This happens because '0' can be interpreted as an uninitialized address, leading to transfers to the '0x0' address, effectively burning tokens. Moreover, 0 as a denominator in division operations would cause a runtime exception. It's also often indicative of a logical error in the caller's code. It's important to always validate input and handle edge cases like 0 appropriately. Use `require()` statements to enforce conditions and provide clear error messages to facilitate debugging and safer code.

Num of instances: 4

### Findings 


<details><summary>Click to show findings</summary>

['[74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L74-L82)']
```solidity
74:     function getZetaFromEth(
75:         address destinationAddress,
76:         uint256 minAmountOut
77:     ) external payable override returns (uint256) {
78:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
79:         if (msg.value == 0) revert InputCantBeZero();
80: 
81:         (address token0, address token1) = getPair(WETH9Address, zetaToken);
82:         address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1); // <= FOUND
83: 
84:         IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
85:             tokenIn: address(0),
86:             amountIn: msg.value,
87:             amountOutMinimum: minAmountOut,
88:             pool: pairPools[0],
89:             to: destinationAddress,
90:             unwrap: false
91:         });
92: 
93:         uint256 amountOut = tridentRouter.exactInputSingle{value: msg.value}(params);
94: 
95:         emit EthExchangedForZeta(msg.value, amountOut);
96:         return amountOut;
97:     }

```
['[99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L115)']
```solidity
99:     function getZetaFromToken(
100:         address destinationAddress,
101:         uint256 minAmountOut,
102:         address inputToken,
103:         uint256 inputTokenAmount
104:     ) external override returns (uint256) {
105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:         if (inputTokenAmount == 0) revert InputCantBeZero();
107: 
108:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
109:         IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
110: 
111:         (address token0, address token1) = getPair(inputToken, WETH9Address);
112:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1); // <= FOUND
113: 
114:         (token0, token1) = getPair(WETH9Address, zetaToken);
115:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1); // <= FOUND
116: 
117:         address[] memory path = new address[](2);
118:         path[0] = pairPools1[0];
119:         path[1] = pairPools2[0];
120: 
121:         IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:             tokenIn: inputToken,
123:             amountIn: inputTokenAmount,
124:             amountOutMinimum: minAmountOut,
125:             path: path,
126:             to: destinationAddress,
127:             unwrap: false
128:         });
129: 
130:         uint256 amountOut = tridentRouter.exactInput(params);
131: 
132:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133:         return amountOut;
134:     }

```
['[136](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L148)']
```solidity
136:     function getEthFromZeta(
137:         address destinationAddress,
138:         uint256 minAmountOut,
139:         uint256 zetaTokenAmount
140:     ) external override returns (uint256) {
141:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
142:         if (zetaTokenAmount == 0) revert InputCantBeZero();
143: 
144:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
145:         IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
146: 
147:         (address token0, address token1) = getPair(zetaToken, WETH9Address);
148:         address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1); // <= FOUND
149: 
150:         IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
151:             tokenIn: zetaToken,
152:             amountIn: zetaTokenAmount,
153:             amountOutMinimum: minAmountOut,
154:             pool: pairPools[0],
155:             to: destinationAddress,
156:             unwrap: true
157:         });
158: 
159:         uint256 amountOut = tridentRouter.exactInputSingle(params);
160: 
161:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162: 
163:         return amountOut;
164:     }

```
['[166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L182)']
```solidity
166:     function getTokenFromZeta(
167:         address destinationAddress,
168:         uint256 minAmountOut,
169:         address outputToken,
170:         uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {
172:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
173:         if (zetaTokenAmount == 0) revert InputCantBeZero();
174: 
175:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
176:         IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount);
177: 
178:         (address token0, address token1) = getPair(zetaToken, WETH9Address);
179:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1); // <= FOUND
180: 
181:         (token0, token1) = getPair(WETH9Address, outputToken);
182:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1); // <= FOUND
183: 
184:         address[] memory path = new address[](2);
185:         path[0] = pairPools1[0];
186:         path[1] = pairPools2[0];
187: 
188:         IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
189:             tokenIn: zetaToken,
190:             amountIn: zetaTokenAmount,
191:             amountOutMinimum: minAmountOut,
192:             path: path,
193:             to: destinationAddress,
194:             unwrap: false
195:         });
196: 
197:         uint256 amountOut = tridentRouter.exactInput(params);
198: 
199:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
200:         return amountOut;
201:     }

```


</details>

## [NonCritical-10] Critical functions should be a two step procedure

### Resolution 
Critical functions in Solidity contracts should follow a two-step procedure to enhance security, minimize human error, and ensure proper access control. By dividing sensitive operations into distinct phases, such as initiation and confirmation, developers can introduce a safeguard against unintended actions or unauthorized access.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)']
```solidity
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner  // <= FOUND

```


</details>


## [Low-10] Revert on Transfer to the Zero Address

### Resolution 
Many ERC-20 and ERC-721 token contracts implement a safeguard that reverts transactions which attempt to transfer tokens to the zero address. This is because such transfers are often the result of programming errors. The OpenZeppelin library, a popular choice for implementing these standards, includes this safeguard. For token contract developers who want to avoid unintentional transfers to the zero address, it's good practice to include a condition that reverts the transaction if the recipient's address is the zero address. 

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193-L197)']
```solidity
193:     function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS {
194:         if (!whitelisted[asset]) {
195:             revert NotWhitelisted();
196:         }
197:         IERC20(asset).safeTransfer(recipient, amount); // <= FOUND
198:         emit Withdrawn(recipient, asset, amount);
199:     }

```


</details>

## [Low-11] Critical functions should have a timelock

### Resolution 
Critical functions, especially those affecting protocol parameters or user funds, are potential points of failure or exploitation. To mitigate risks, incorporating a timelock on such functions can be beneficial. A timelock requires a waiting period between the time an action is initiated and when it's executed, giving stakeholders time to react, potentially vetoing malicious or erroneous changes. To implement, integrate a smart contract like OpenZeppelin's `TimelockController` or build a custom mechanism. This ensures governance decisions or administrative changes are transparent and allows for community or multi-signature interventions, enhancing protocol security and trustworthiness.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)']
```solidity
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner  // <= FOUND

```


</details>


## [Low-12] Vulnerable version of openzeppelin contracts used

### Resolution 
OpenZeppelin versions of 4.9.2 and below are vulnerable to exploits, please consider upgrading to 4.9.3 or above. See: https://security.snyk.io/package/npm/@openzeppelin%2Fcontracts for more details

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[1](https://github.com/code-423n4/2023-11-zetachain/blob/main/package.json#L1-L13)']
```solidity
1: {
2:   "author": "zetachain",
3:   "devDependencies": {
4:     "@changesets/cli": "^2.23.1",
5:     "@ethersproject/abi": "^5.4.7",
6:     "@ethersproject/providers": "^5.4.7",
7:     "@nomicfoundation/hardhat-chai-matchers": "^1.0.6",
8:     "@nomicfoundation/hardhat-network-helpers": "^1.0.0",
9:     "@nomicfoundation/hardhat-toolbox": "^2.0.0",
10:     "@nomiclabs/hardhat-ethers": "^2.0.5",
11:     "@nomiclabs/hardhat-etherscan": "3.0.3",
12:     "@nomiclabs/hardhat-waffle": "^2.0.3",
13:     "@openzeppelin/contracts": "^4.8.3", // <= FOUND
14:     "@typechain/ethers-v5": "^10.1.0",
15:     "@typechain/hardhat": "^6.1.2",
16:     "@types/chai": "^4.3.1",
17:     "@types/inquirer": "^8.2.1",
18:     "@types/mocha": "^10.0.1",
19:     "@types/node": "^17.0.25",
20:     "@typescript-eslint/eslint-plugin": "^5.20.0",
21:     "@typescript-eslint/parser": "^5.20.0",
22:     "@uniswap/v2-core": "^1.0.1",
23:     "@uniswap/v2-periphery": "^1.1.0-beta.0",
24:     "@uniswap/v3-periphery": "^1.4.3",
25:     "@zetachain/networks": "^2.4.3",
26:     "chai": "^4.3.6",
27:     "cpx": "^1.5.0",
28:     "del-cli": "^5.0.0",
29:     "dotenv": "^16.0.0",
30:     "eslint": "^8.13.0",
31:     "eslint-config-prettier": "^8.5.0",
32:     "eslint-config-standard": "^17.0.0",
33:     "eslint-import-resolver-typescript": "^2.7.1",
34:     "eslint-plugin-import": "^2.26.0",
35:     "eslint-plugin-node": "^11.1.0",
36:     "eslint-plugin-prettier": "^4.0.0",
37:     "eslint-plugin-promise": "^6.0.0",
38:     "eslint-plugin-simple-import-sort": "7.0.0",
39:     "eslint-plugin-sort-keys-fix": "1.1.2",
40:     "eslint-plugin-typescript-sort-keys": "2.1.0",
41:     "ethereum-waffle": "^4.0.9",
42:     "ethereumjs-utils": "^5.2.5",
43:     "ethers": "5.6.8",
44:     "hardhat": "^2.13.1",
45:     "hardhat-abi-exporter": "^2.10.1",
46:     "hardhat-gas-reporter": "^1.0.9",
47:     "inquirer": "^8.2.4",
48:     "mocha": "^10.2.0",
49:     "solidity-coverage": "^0.8.2",
50:     "ts-mocha": "^10.0.0",
51:     "ts-node": "10.8.1",
52:     "tsconfig-paths": "^3.14.1",
53:     "typechain": "^8.1.0",
54:     "typescript": "^4.6.3"
55:   },
56:   "files": [
57:     "contracts",
58:     "abi",
59:     "dist"
60:   ],
61:   "keywords": [],
62:   "license": "MIT",

```


</details>

## [Low-13] Inconsistent use of _msgSender() and msg.sender in contract

### Resolution 
For the sake of consistency, stick to using only one of these values throughout the contract. Not doing so in this case can be quite harmful as _msgSender and msg.sender do have some differences, one being that msgSender cannot be used to determine if an account is a EOA but msg.sender can. Differences like these can introduce vulnerabilities is they are not properly acknowledged by the dev team.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L262)']
```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:     
22:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
23:     
24:     uint256 public immutable CHAIN_ID;
25:     
26:     CoinType public immutable COIN_TYPE;
27:     
28:     address public SYSTEM_CONTRACT_ADDRESS;
29:     
30:     uint256 public GAS_LIMIT;
31:     
32:     uint256 public PROTOCOL_FLAT_FEE;
33: 
34:     mapping(address => uint256) private _balances;
35:     mapping(address => mapping(address => uint256)) private _allowances;
36:     uint256 private _totalSupply;
37:     string private _name;
38:     string private _symbol;
39:     uint8 private _decimals;
40: 
41:     function _msgSender() internal view virtual returns (address) { // <= FOUND
42:         return msg.sender; // <= FOUND
43:     }
44: 
45:     function _msgData() internal view virtual returns (bytes calldata) {
46:         return msg.data;
47:     }
48: 
52:     modifier onlyFungible() {
53:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule(); // <= FOUND
54:         _;
55:     }
56: 
60:     constructor(
61:         string memory name_,
62:         string memory symbol_,
63:         uint8 decimals_,
64:         uint256 chainid_,
65:         CoinType coinType_,
66:         uint256 gasLimit_,
67:         address systemContractAddress_
68:     ) {
69:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule(); // <= FOUND
70:         _name = name_;
71:         _symbol = symbol_;
72:         _decimals = decimals_;
73:         CHAIN_ID = chainid_;
74:         COIN_TYPE = coinType_;
75:         GAS_LIMIT = gasLimit_;
76:         SYSTEM_CONTRACT_ADDRESS = systemContractAddress_;
77:     }
78: 
83:     function name() public view virtual override returns (string memory) {
84:         return _name;
85:     }
86: 
91:     function symbol() public view virtual override returns (string memory) {
92:         return _symbol;
93:     }
94: 
99:     function decimals() public view virtual override returns (uint8) {
100:         return _decimals;
101:     }
102: 
107:     function totalSupply() public view virtual override returns (uint256) {
108:         return _totalSupply;
109:     }
110: 
116:     function balanceOf(address account) public view virtual override returns (uint256) {
117:         return _balances[account];
118:     }
119: 
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
126:         _transfer(_msgSender(), recipient, amount); // <= FOUND
127:         return true;
128:     }
129: 
135:     function allowance(address owner, address spender) public view virtual override returns (uint256) {
136:         return _allowances[owner][spender];
137:     }
138: 
145:     function approve(address spender, uint256 amount) public virtual override returns (bool) {
146:         _approve(_msgSender(), spender, amount); // <= FOUND
147:         return true;
148:     }
149: 
157:     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
158:         _transfer(sender, recipient, amount);
159: 
160:         uint256 currentAllowance = _allowances[sender][_msgSender()]; // <= FOUND
161:         if (currentAllowance < amount) revert LowAllowance();
162: 
163:         _approve(sender, _msgSender(), currentAllowance - amount); // <= FOUND
164: 
165:         return true;
166:     }
167: 
173:     function burn(uint256 amount) external returns (bool) {
174:         _burn(msg.sender, amount); // <= FOUND
175:         return true;
176:     }
177: 
178:     function _transfer(address sender, address recipient, uint256 amount) internal virtual {
179:         if (sender == address(0)) revert ZeroAddress();
180:         if (recipient == address(0)) revert ZeroAddress();
181: 
182:         uint256 senderBalance = _balances[sender];
183:         if (senderBalance < amount) revert LowBalance();
184: 
185:         _balances[sender] = senderBalance - amount;
186:         _balances[recipient] += amount;
187: 
188:         emit Transfer(sender, recipient, amount);
189:     }
190: 
191:     function _mint(address account, uint256 amount) internal virtual {
192:         if (account == address(0)) revert ZeroAddress();
193: 
194:         _totalSupply += amount;
195:         _balances[account] += amount;
196:         emit Transfer(address(0), account, amount);
197:     }
198: 
199:     function _burn(address account, uint256 amount) internal virtual {
200:         if (account == address(0)) revert ZeroAddress();
201: 
202:         uint256 accountBalance = _balances[account];
203:         if (accountBalance < amount) revert LowBalance();
204: 
205:         _balances[account] = accountBalance - amount;
206:         _totalSupply -= amount;
207: 
208:         emit Transfer(account, address(0), amount);
209:     }
210: 
211:     function _approve(address owner, address spender, uint256 amount) internal virtual {
212:         if (owner == address(0)) revert ZeroAddress();
213:         if (spender == address(0)) revert ZeroAddress();
214: 
215:         _allowances[owner][spender] = amount;
216:         emit Approval(owner, spender, amount);
217:     }
218: 
225:     function deposit(address to, uint256 amount) external override returns (bool) {
226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender(); // <= FOUND
227:         _mint(to, amount);
228:         emit Deposit(abi.encodePacked(FUNGIBLE_MODULE_ADDRESS), to, amount);
229:         return true;
230:     }
231: 
236:     function withdrawGasFee() public view override returns (address, uint256) {
237:         address gasZRC20 = ISystem(SYSTEM_CONTRACT_ADDRESS).gasCoinZRC20ByChainId(CHAIN_ID);
238:         if (gasZRC20 == address(0)) {
239:             revert ZeroGasCoin();
240:         }
241:         uint256 gasPrice = ISystem(SYSTEM_CONTRACT_ADDRESS).gasPriceByChainId(CHAIN_ID);
242:         if (gasPrice == 0) {
243:             revert ZeroGasPrice();
244:         }
245:         uint256 gasFee = gasPrice * GAS_LIMIT + PROTOCOL_FLAT_FEE;
246:         return (gasZRC20, gasFee);
247:     }
248: 
256:     function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
257:         (address gasZRC20, uint256 gasFee) = withdrawGasFee();
258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) { // <= FOUND
259:             revert GasFeeTransferFailed();
260:         }
261:         _burn(msg.sender, amount); // <= FOUND
262:         emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE); // <= FOUND
263:         return true;
264:     }
265: 
270:     function updateSystemContractAddress(address addr) external onlyFungible {
271:         SYSTEM_CONTRACT_ADDRESS = addr;
272:         emit UpdatedSystemContract(addr);
273:     }
274: 
279:     function updateGasLimit(uint256 gasLimit) external onlyFungible {
280:         GAS_LIMIT = gasLimit;
281:         emit UpdatedGasLimit(gasLimit);
282:     }
283: 
288:     function updateProtocolFlatFee(uint256 protocolFlatFee) external onlyFungible {
289:         PROTOCOL_FLAT_FEE = protocolFlatFee;
290:         emit UpdatedProtocolFlatFee(protocolFlatFee);
291:     }
292: }

```


</details>

## [NonCritical-12] Upgradeable contract uses non-upgradeable version of the OpenZeppelin libraries/contracts

### Resolution 
Using the upgradeable counterpart of the OpenZeppelin (OZ) library in Solidity is beneficial for creating contracts that can be updated in the future. OpenZeppelin's upgradeable contracts library is designed with proxy patterns in mind, which allow the logic of contracts to be upgraded while preserving the contract's state and address. This can be crucial for long-lived contracts where future requirements or improvements may not be fully known at the time of deployment. The upgradeable OZ contracts also include protection against a class of vulnerabilities related to initialization of storage variables in upgradeable contracts. Hence, it's a good idea to use them when developing contracts that may need to be upgraded in the future, as they provide a solid foundation for secure and upgradeable smart contracts.

Num of instances: 8

### Findings 


<details><summary>Click to show findings</summary>

['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/access/Ownable2Step.sol"; // <= FOUND 'openzeppelin'

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol"; // <= FOUND 'openzeppelin'

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol"; // <= FOUND 'openzeppelin'

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol"; // <= FOUND 'openzeppelin'

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L5-L5)']
```solidity
5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol"; // <= FOUND 'openzeppelin'

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L5-L5)']
```solidity
5: import "@openzeppelin/contracts/security/Pausable.sol"; // <= FOUND 'openzeppelin'

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/token/ERC20/ERC20.sol"; // <= FOUND 'openzeppelin'

```
['[7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L7-L7)']
```solidity
7: import "@openzeppelin/contracts/security/ReentrancyGuard.sol"; // <= FOUND 'openzeppelin'

```


</details>

## [Low-14] Solidity version 0.8.20 won't work on all chains due to PUSH0

### Resolution 
Solidity version 0.8.20 uses the new Shanghai EVM which introduces the PUSH0 opcode, this may not be implemented on all chains and L2 thus reducing the portability and compatability of the code. Consider using a earlier solidity version.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L13-L13)']
```solidity
13: pragma solidity >=0.8.0; // <= FOUND

```


</details>


## [NonCritical-14] Instances should be declared in a separate file

### Resolution 
It is general standard to declare interfaces on files separate from regular contract declarations

Num of instances: 7

### Findings 


<details><summary>Click to show findings</summary>

['[3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L3-L3)']
```solidity
3: interface Ownable  // <= FOUND

```
['[12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12)']
```solidity
12: interface ZetaTokenConsumerUniV3Errors  // <= FOUND

```
['[8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8-L8)']
```solidity
8: interface ZRC20Errors  // <= FOUND

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L4)']
```solidity
4: interface ZetaInterfaces  // <= FOUND

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10)']
```solidity
10: interface ZetaTokenConsumerUniV2Errors  // <= FOUND

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10-L10)']
```solidity
10: interface SystemContractErrors  // <= FOUND

```
['[12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12)']
```solidity
12: interface ZetaTokenConsumerTridentErrors  // <= FOUND

```


</details>

## [NonCritical-15] Open TODO in comments

### Resolution 
Production code should not have open TODOs as this makes code appear incomplete at production deployment

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[204](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L204-L204)']
```solidity
204: //@TODO: Implement // <= FOUND

```


</details>

## [NonCritical-17] Enum values should be used in place of constant array indexes

### Resolution 
Create a commented enum value to use in place of constant array indexes, this makes the code far easier to understand

Num of instances: 15

### Findings 


<details><summary>Click to show findings</summary>

['[85](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L85-L88)']
```solidity
85:             tokenIn: address(0),
86:             amountIn: msg.value,
87:             amountOutMinimum: minAmountOut,
88:             pool: pairPools[0], // <= FOUND
89:             to: destinationAddress,
90:             unwrap: false
91:         });

```
['[118](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L118-L118)']
```solidity
118:         path[0] = pairPools1[0]; // <= FOUND

```
['[119](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L119-L119)']
```solidity
119:         path[1] = pairPools2[0]; // <= FOUND

```
['[151](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L151-L154)']
```solidity
151:             tokenIn: zetaToken,
152:             amountIn: zetaTokenAmount,
153:             amountOutMinimum: minAmountOut,
154:             pool: pairPools[0], // <= FOUND
155:             to: destinationAddress,
156:             unwrap: true
157:         });

```
['[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L42-L42)']
```solidity
42:         path[0] = wETH; // <= FOUND

```
['[73](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L73-L73)']
```solidity
73:             path[0] = wETH; // <= FOUND

```
['[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L77-L77)']
```solidity
77:             path[0] = inputToken; // <= FOUND

```
['[107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L107-L107)']
```solidity
107:         path[0] = zetaToken; // <= FOUND

```
['[139](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L139-L139)']
```solidity
139:             path[0] = zetaToken; // <= FOUND

```
['[43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L43-L43)']
```solidity
43:         path[1] = zetaToken; // <= FOUND

```
['[74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L74-L74)']
```solidity
74:             path[1] = zetaToken; // <= FOUND

```
['[78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L78-L78)']
```solidity
78:             path[1] = wETH; // <= FOUND

```
['[78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L78-L78)']
```solidity
78:         path[1] = wETH; // <= FOUND

```
['[79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L79-L79)']
```solidity
79:             path[2] = zetaToken; // <= FOUND

```
['[145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L145-L145)']
```solidity
145:             path[2] = outputToken; // <= FOUND

```


</details>

## [NonCritical-18] Empty receive functions can cause gas issues

### Resolution 
In Solidity, functions that receive Ether without corresponding functionality to utilize or withdraw these funds can inadvertently lead to a permanent loss of value. This is because if someone sends Ether to the contract, they may be unable to retrieve it. To avoid this, functions receiving Ether should be accompanied by additional methods that process or allow the withdrawal of these funds. If the intent is to use the received Ether, it should trigger a separate function; if not, it should revert the transaction (for instance, via `require(msg.sender == address(weth))`). Access control checks can also prevent unintended Ether transfers, despite the slight gas cost they entail. If concerns over gas costs persist, at minimum, include a rescue function to recover unused Ether. Missteps in handling Ether in smart contracts can lead to irreversible financial losses, hence these precautions are crucial.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[72](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72-L72)']
```solidity
72:     receive() external payable {}

```


</details>

## [NonCritical-19] Functions which are either private or internal should have a preceding _ in their name

### Resolution 
Add a preceding underscore to the function name, take care to refactor where there functions are called

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[68](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L68)']
```solidity
68:     function getPair(address token0, address token1) internal pure returns (address, address) 

```
['[26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L26-L26)']
```solidity
26:     function safeCreate2Internal(
27:         bytes32 salt,
28:         bytes memory initializationCode
29:     ) internal returns (address deploymentAddress) 

```
['[87](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L87-L87)']
```solidity
87:     function sortTokens(address tokenA, address tokenB) internal pure returns (address token0, address token1) 

```


</details>

## [NonCritical-20] Contract lines should not be longer than 120 characters for readability

### Resolution 
Consider spreading these lines over multiple lines to aid in readability and the support of VIM users everywhere.

Num of instances: 10

### Findings 


<details><summary>Click to show findings</summary>

['[234](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L234-L234)']
```solidity
234:      * @return returns the ZRC20 address for gas on the same chain of this ZRC20, and calculates the gas fee for withdraw() // <= FOUND

```
['[250](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L250-L250)']
```solidity
250:      * @dev Withraws ZRC20 tokens to external chains, this function causes cctx module to send out outbound tx to the outbound chain // <= FOUND

```
['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L13-L13)']
```solidity
13:  * This version is only for Ethereum network because in the other chains we mint and burn and in this one we lock and unlock. // <= FOUND

```
['[18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L18-L18)']
```solidity
18:         address tokenIn; /// @dev the input token address. If tokenIn is address(0), msg.value will be wrapped and used as input token // <= FOUND

```
['[27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L27-L27)']
```solidity
27:         address tokenIn; /// @dev the token address to swap-in. If tokenIn is address(0), msg.value will be wrapped and used as input token // <= FOUND

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L9-L9)']
```solidity
9:         /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id // <= FOUND

```
['[43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L43-L43)']
```solidity
43:         /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees // <= FOUND

```
['[27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L27-L27)']
```solidity
27:     // @dev: Map to know uniswap V2 pool of ZETA/ZRC20 given a chain id. This refer to the build in uniswap deployed at genesis. // <= FOUND

```
['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L13-L13)']
```solidity
13:  * This version is for every chain but Etherum network because in the other chains we mint and burn and in Etherum we lock and unlock // <= FOUND

```
['[183](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L183-L183)']
```solidity
183:         // and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount. // <= FOUND

```


</details>

## [NonCritical-21] Setters should prevent re-setting of the same value

### Resolution 
In Solidity, manipulating contract storage comes with significant gas costs. One can optimize gas usage by preventing unnecessary storage updates when the new value is the same as the existing one. If an existing value is the same as the new one, not reassigning it to the storage could potentially save substantial amounts of gas, notably 2900 gas for a 'Gsreset'. This saving may come at the expense of a cold storage load operation ('Gcoldsload'), which costs 2100 gas, or a warm storage access operation ('Gwarmaccess'), which costs 100 gas. Therefore, the gas efficiency of your contract can be significantly improved by adding a check that compares the new value with the current one before any storage update operation. If the values are the same, you can bypass the storage operation, thereby saving gas.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)']
```solidity
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
55:         interactorsByChainId[destinationChainId] = contractAddress;
56:     }

```


</details>

## [NonCritical-22] Specific imports should be used where possible so only used code is imported

### Resolution 
In many cases only some functionality is used from an import. In such cases it makes more sense to use {} to specify what to import and thus save gas whilst improving readability

Num of instances: 29

### Findings 


<details><summary>Click to show findings</summary>

['[3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L3-L3)']
```solidity
3: import "./Interfaces.sol";

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/interfaces/IERC20.sol";

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L5-L5)']
```solidity
5: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

```
['[6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L6-L6)']
```solidity
6: import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

```
['[7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L7-L7)']
```solidity
7: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";

```
['[8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L8-L8)']
```solidity
8: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L10-L10)']
```solidity
10: import "../interfaces/ZetaInterfaces.sol";

```
['[6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L6-L6)']
```solidity
6: import "@uniswap/v3-periphery/contracts/interfaces/IQuoter.sol";

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L9-L9)']
```solidity
9: import "./interfaces/TridentConcentratedLiquidityPoolFactory.sol";

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L10-L10)']
```solidity
10: import "./interfaces/TridentIPoolRouter.sol";

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

```
['[7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L7-L7)']
```solidity
7: import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

```
['[6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L6-L6)']
```solidity
6: import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L5-L5)']
```solidity
5: import "@openzeppelin/contracts/security/Pausable.sol";

```
['[6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L6-L6)']
```solidity
6: import "./interfaces/ConnectorErrors.sol";

```
['[8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L8-L8)']
```solidity
8: import "./interfaces/ZetaInterfaces.sol";

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L4-L4)']
```solidity
4: import "./interfaces/zContract.sol";

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L5-L5)']
```solidity
5: import "./interfaces/IZRC20.sol";

```
['[7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L7-L7)']
```solidity
7: import "./ZetaConnector.base.sol";

```
['[8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L8-L8)']
```solidity
8: import "./interfaces/ZetaNonEthInterface.sol";

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

```
['[6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L6-L6)']
```solidity
6: import "./interfaces/ZetaErrors.sol";

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/access/Ownable2Step.sol";

```
['[7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L7-L7)']
```solidity
7: import "../interfaces/ZetaInteractorErrors.sol";

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L4-L4)']
```solidity
4: import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L4-L4)']
```solidity
4: import "./IUniswapV2Router01.sol";

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L4-L4)']
```solidity
4: import "@uniswap/v2-core/contracts/UniswapV2Pair.sol";

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Uniswap.sol#L5-L5)']
```solidity
5: import "@uniswap/v2-core/contracts/UniswapV2Factory.sol";

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L4-L4)']
```solidity
4: import "@uniswap/v2-periphery/contracts/UniswapV2Router02.sol";

```


</details>

## [NonCritical-23] Use newer solidity versions

### Resolution 
Newer solidity versions have new functionality and are generally more gas efficient too (0.8.19) as such it makes sense to use them provided it is safe to do so

Num of instances: 6

### Findings 


<details><summary>Click to show findings</summary>

['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L13-L13)']
```solidity
13: pragma solidity >=0.8.0; // <= FOUND

```
['']
```solidity
2: pragma solidity 0.8.7;

```
['']
```solidity
1: pragma solidity 0.5.10; 

```
['']
```solidity
1: pragma solidity ^0.4.18;

```
['']
```solidity
2: pragma solidity 0.5.16;

```
['']
```solidity
2: pragma solidity 0.6.6;

```


</details>

## [NonCritical-24] Not all event definitions are utilizing indexed variables.

### Resolution 
Try to index as much as three variables in event declarations as this is more gas efficient when done on value type variables (uint, address etc) however not for bytes and string variables 

Num of instances: 26

### Findings 


<details><summary>Click to show findings</summary>

['[38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L38-L38)']
```solidity
38: event Paused(address sender); // <= FOUND

```
['[39](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L39-L39)']
```solidity
39: event Unpaused(address sender); // <= FOUND

```
['[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L42-L42)']
```solidity
42: event Deposited(bytes recipient, IERC20 indexed asset, uint256 amount, bytes message); // <= FOUND

```
['[43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L43-L43)']
```solidity
43: event Withdrawn(address indexed recipient, IERC20 indexed asset, uint256 amount); // <= FOUND

```
['[44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L44-L44)']
```solidity
44: event RenouncedTSSUpdater(address TSSAddressUpdater_); // <= FOUND

```
['[45](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L45-L45)']
```solidity
45: event UpdatedTSSAddress(address TSSAddress_); // <= FOUND

```
['[46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L46-L46)']
```solidity
46: event UpdatedZetaFee(uint256 zetaFee_); // <= FOUND

```
['[67](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L67-L67)']
```solidity
67: event ZetaSent( // <= FOUND
68:         address sourceTxOriginAddress,
69:         address indexed zetaTxSenderAddress,
70:         uint256 indexed destinationChainId,
71:         bytes destinationAddress,
72:         uint256 zetaValueAndGas,
73:         uint256 destinationGasLimit,
74:         bytes message,
75:         bytes zetaParams
76:     );

```
['[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L54-L54)']
```solidity
54: event ZetaReverted( // <= FOUND
55:         address zetaTxSenderAddress,
56:         uint256 sourceChainId,
57:         uint256 indexed destinationChainId,
58:         bytes destinationAddress,
59:         uint256 remainingZetaValue,
60:         bytes message,
61:         bytes32 indexed internalSendHash
62:     );

```
['[27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L27-L27)']
```solidity
27: event TSSAddressUpdated(address callerAddress, address newTssAddress); // <= FOUND

```
['[29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L29-L29)']
```solidity
29: event TSSAddressUpdaterUpdated(address callerAddress, address newTssUpdaterAddress); // <= FOUND

```
['[68](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L68-L68)']
```solidity
68: event PauserAddressUpdated(address callerAddress, address newTssAddress); // <= FOUND

```
['[41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L41-L41)']
```solidity
41: event SystemContractDeployed(); // <= FOUND

```
['[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L42-L42)']
```solidity
42: event SetGasPrice(uint256, uint256); // <= FOUND

```
['[43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L43-L43)']
```solidity
43: event SetGasCoin(uint256, address); // <= FOUND

```
['[44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L44-L44)']
```solidity
44: event SetGasZetaPool(uint256, address); // <= FOUND

```
['[45](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L45-L45)']
```solidity
45: event SetWZeta(address); // <= FOUND

```
['[46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L46-L46)']
```solidity
46: event SetConnectorZEVM(address); // <= FOUND

```
['[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L77-L77)']
```solidity
77: event SetWZETA(address wzeta_); // <= FOUND

```
['[18](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L18-L18)']
```solidity
18: event MaxSupplyUpdated(address callerAddress, uint256 newMaxSupply); // <= FOUND

```
['[8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L8-L8)']
```solidity
8: event Approval(address indexed src, address indexed guy, uint wad); // <= FOUND

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L9-L9)']
```solidity
9: event Transfer(address indexed src, address indexed dst, uint wad); // <= FOUND

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L10-L10)']
```solidity
10: event Deposit(address indexed dst, uint wad); // <= FOUND

```
['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L11-L11)']
```solidity
11: event Withdrawal(address indexed src, uint wad); // <= FOUND

```
['[25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L25-L25)']
```solidity
25: event Burnt(address indexed burnee, uint256 amount); // <= FOUND

```
['[31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L31-L31)']
```solidity
31: event ConnectorAddressUpdated(address callerAddress, address newConnectorAddress); // <= FOUND

```


</details>

## [NonCritical-25] Function names should differ to make the code more readable

### Resolution 
In Solidity, while function overriding allows for functions with the same name to coexist, it is advisable to avoid this practice to enhance code readability and maintainability. Having multiple functions with the same name, even with different parameters or in inherited contracts, can cause confusion and increase the likelihood of errors during development, testing, and debugging. Using distinct and descriptive function names not only clarifies the purpose and behavior of each function, but also helps prevent unintended function calls or incorrect overriding. By adopting a clear and consistent naming convention, developers can create more comprehensible and maintainable smart contracts.

Num of instances: 19

### Findings 


<details><summary>Click to show findings</summary>

['[74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L74-L74)']
```solidity
74:     function getZetaFromEth( // <= FOUND
75:         address destinationAddress,
76:         uint256 minAmountOut
77:     ) external payable override returns (uint256) 

```
['[98](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L98)']
```solidity
98:     function getZetaFromToken( // <= FOUND
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address inputToken,
102:         uint256 inputTokenAmount
103:     ) external override returns (uint256) 

```
['[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L124)']
```solidity
124:     function getEthFromZeta( // <= FOUND
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         uint256 zetaTokenAmount
128:     ) external override returns (uint256) 

```
['[158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L158)']
```solidity
158:     function getTokenFromZeta( // <= FOUND
159:         address destinationAddress,
160:         uint256 minAmountOut,
161:         address outputToken,
162:         uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) 

```
['[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L124)']
```solidity
124:     function getTokenFromZeta( // <= FOUND
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         address outputToken,
128:         uint256 zetaTokenAmount
129:     ) external override returns (uint256) 

```
['[184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184-L184)']
```solidity
184:     function hasZetaLiquidity() external view override returns (bool)  // <= FOUND

```
['[225](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225-L225)']
```solidity
225:     function deposit(address to, uint256 amount) external override returns (bool)  // <= FOUND

```
['[165](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L165)']
```solidity
165:     function deposit( // <= FOUND
166:         bytes calldata recipient,
167:         IERC20 asset,
168:         uint256 amount,
169:         bytes calldata message
170:     ) external nonReentrant 

```
['[20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L20-L20)']
```solidity
20:     function deposit() public payable  // <= FOUND

```
['[166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L166-L166)']
```solidity
166:     function send(ZetaInterfaces.SendInput calldata input) external virtual  // <= FOUND

```
['[31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31-L31)']
```solidity
31:     function send(ZetaInterfaces.SendInput calldata input) external  // <= FOUND

```
['[31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31-L31)']
```solidity
31:     function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused  // <= FOUND

```
['[172](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L172-L172)']
```solidity
172:     function onReceive( // <= FOUND
173:         bytes calldata zetaTxSenderAddress,
174:         uint256 sourceChainId,
175:         address destinationAddress,
176:         uint256 zetaValue,
177:         bytes calldata message,
178:         bytes32 internalSendHash
179:     ) external virtual 

```
['[52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L52)']
```solidity
52:     function onReceive( // <= FOUND
53:         bytes calldata zetaTxSenderAddress,
54:         uint256 sourceChainId,
55:         address destinationAddress,
56:         uint256 zetaValue,
57:         bytes calldata message,
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress 

```
['[185](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L185-L185)']
```solidity
185:     function onRevert( // <= FOUND
186:         address zetaTxSenderAddress,
187:         uint256 sourceChainId,
188:         bytes calldata destinationAddress,
189:         uint256 destinationChainId,
190:         uint256 remainingZetaValue,
191:         bytes calldata message,
192:         bytes32 internalSendHash
193:     ) external virtual 

```
['[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L77-L77)']
```solidity
77:     function onRevert( // <= FOUND
78:         address zetaTxSenderAddress,
79:         uint256 sourceChainId,
80:         bytes calldata destinationAddress,
81:         uint256 destinationChainId,
82:         uint256 remainingZetaValue,
83:         bytes calldata message,
84:         bytes32 internalSendHash
85:     ) external override whenNotPaused onlyTssAddress 

```
['[23](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L23-L23)']
```solidity
23:     function getLockedAmount() external view returns (uint256)  // <= FOUND

```
['[140](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L140-L140)']
```solidity
140:     function renounceTssAddressUpdater() external onlyTssUpdater  // <= FOUND

```
['[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L54-L54)']
```solidity
54:     function renounceTssAddressUpdater() external  // <= FOUND

```


</details>

## [NonCritical-26] uint variables should have the bit size defined explicitly

### Resolution 
Instead of using uint to declare uint258, explicitly define uint258 to ensure there is no confusion

Num of instances: 33

### Findings 


<details><summary>Click to show findings</summary>

['[50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50-L50)']
```solidity
50:     function transferFrom(address src, address dst, uint wad) external returns (bool); // <= FOUND

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L9-L9)']
```solidity
8: 
9:     event Approval(address indexed src, address indexed guy, uint wad); // <= FOUND

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L9-L9)']
```solidity
9:     event Transfer(address indexed src, address indexed dst, uint wad); // <= FOUND

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L10-L10)']
```solidity
10:     event Deposit(address indexed dst, uint wad); // <= FOUND

```
['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L11-L11)']
```solidity
11:     event Withdrawal(address indexed src, uint wad); // <= FOUND

```
['[37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L37-L37)']
```solidity
36: 
37:     function approve(address guy, uint wad) public returns (bool) { // <= FOUND

```
['[43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L43-L43)']
```solidity
42: 
43:     function transfer(address dst, uint wad) public returns (bool) { // <= FOUND

```
['[47](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L47-L47)']
```solidity
46: 
47:     function transferFrom(address src, address dst, uint wad) public returns (bool) { // <= FOUND

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5-L5)']
```solidity
5:     event Approval(address indexed owner, address indexed spender, uint value); // <= FOUND

```
['[6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L6)']
```solidity
6:     event Transfer(address indexed from, address indexed to, uint value); // <= FOUND

```
['[17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L17-L17)']
```solidity
16: 
17:     function approve(address spender, uint wad) external returns (bool); // <= FOUND

```
['[19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L19-L19)']
```solidity
18: 
19:     function transfer(address to, uint wad) external returns (bool); // <= FOUND

```
['[21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L21-L21)']
```solidity
20: 
21:     function transferFrom(address from, address to, uint wad) external returns (bool); // <= FOUND

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L9-L13)']
```solidity
7:     function removeLiquidityETHSupportingFeeOnTransferTokens(
8:         address token,
9:         uint liquidity, // <= FOUND
10:         uint amountTokenMin, // <= FOUND
11:         uint amountETHMin, // <= FOUND
12:         address to,
13:         uint deadline // <= FOUND
14:     ) external returns (uint amountETH);

```
['[19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L19-L23)']
```solidity
16: 
17:     function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
18:         address token,
19:         uint liquidity, // <= FOUND
20:         uint amountTokenMin, // <= FOUND
21:         uint amountETHMin, // <= FOUND
22:         address to,
23:         uint deadline, // <= FOUND
24:         bool approveMax,
25:         uint8 v,
26:         bytes32 r,
27:         bytes32 s
28:     ) external returns (uint amountETH);

```
['[31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L31-L35)']
```solidity
29: 
30:     function swapExactTokensForTokensSupportingFeeOnTransferTokens(
31:         uint amountIn, // <= FOUND
32:         uint amountOutMin, // <= FOUND
33:         address[] calldata path,
34:         address to,
35:         uint deadline // <= FOUND
36:     ) external;

```
['[39](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L39-L42)']
```solidity
37: 
38:     function swapExactETHForTokensSupportingFeeOnTransferTokens(
39:         uint amountOutMin, // <= FOUND
40:         address[] calldata path,
41:         address to,
42:         uint deadline // <= FOUND
43:     ) external payable;

```
['[46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L46-L50)']
```solidity
44: 
45:     function swapExactTokensForETHSupportingFeeOnTransferTokens(
46:         uint amountIn, // <= FOUND
47:         uint amountOutMin, // <= FOUND
48:         address[] calldata path,
49:         address to,
50:         uint deadline // <= FOUND
51:     ) external;

```
['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L13-L19)']
```solidity
9: 
10:     function addLiquidity(
11:         address tokenA,
12:         address tokenB,
13:         uint amountADesired, // <= FOUND
14:         uint amountBDesired, // <= FOUND
15:         uint amountAMin, // <= FOUND
16:         uint amountBMin, // <= FOUND
17:         address to,
18:         uint deadline // <= FOUND
19:     ) external returns (uint amountA, uint amountB, uint liquidity); // <= FOUND

```
['[23](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L23-L28)']
```solidity
20: 
21:     function addLiquidityETH(
22:         address token,
23:         uint amountTokenDesired, // <= FOUND
24:         uint amountTokenMin, // <= FOUND
25:         uint amountETHMin, // <= FOUND
26:         address to,
27:         uint deadline // <= FOUND
28:     ) external payable returns (uint amountToken, uint amountETH, uint liquidity); // <= FOUND

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L33-L38)']
```solidity
29: 
30:     function removeLiquidity(
31:         address tokenA,
32:         address tokenB,
33:         uint liquidity, // <= FOUND
34:         uint amountAMin, // <= FOUND
35:         uint amountBMin, // <= FOUND
36:         address to,
37:         uint deadline // <= FOUND
38:     ) external returns (uint amountA, uint amountB); // <= FOUND

```
['[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L42-L47)']
```solidity
39: 
40:     function removeLiquidityETH(
41:         address token,
42:         uint liquidity, // <= FOUND
43:         uint amountTokenMin, // <= FOUND
44:         uint amountETHMin, // <= FOUND
45:         address to,
46:         uint deadline // <= FOUND
47:     ) external returns (uint amountToken, uint amountETH); // <= FOUND

```
['[52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L52-L61)']
```solidity
48: 
49:     function removeLiquidityWithPermit(
50:         address tokenA,
51:         address tokenB,
52:         uint liquidity, // <= FOUND
53:         uint amountAMin, // <= FOUND
54:         uint amountBMin, // <= FOUND
55:         address to,
56:         uint deadline, // <= FOUND
57:         bool approveMax,
58:         uint8 v,
59:         bytes32 r,
60:         bytes32 s
61:     ) external returns (uint amountA, uint amountB); // <= FOUND

```
['[65](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L65-L74)']
```solidity
62: 
63:     function removeLiquidityETHWithPermit(
64:         address token,
65:         uint liquidity, // <= FOUND
66:         uint amountTokenMin, // <= FOUND
67:         uint amountETHMin, // <= FOUND
68:         address to,
69:         uint deadline, // <= FOUND
70:         bool approveMax,
71:         uint8 v,
72:         bytes32 r,
73:         bytes32 s
74:     ) external returns (uint amountToken, uint amountETH); // <= FOUND

```
['[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L77-L81)']
```solidity
75: 
76:     function swapExactTokensForTokens(
77:         uint amountIn, // <= FOUND
78:         uint amountOutMin, // <= FOUND
79:         address[] calldata path,
80:         address to,
81:         uint deadline // <= FOUND
82:     ) external returns (uint[] memory amounts);

```
['[85](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L85-L89)']
```solidity
83: 
84:     function swapTokensForExactTokens(
85:         uint amountOut, // <= FOUND
86:         uint amountInMax, // <= FOUND
87:         address[] calldata path,
88:         address to,
89:         uint deadline // <= FOUND
90:     ) external returns (uint[] memory amounts);

```
['[93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L93-L96)']
```solidity
91: 
92:     function swapExactETHForTokens(
93:         uint amountOutMin, // <= FOUND
94:         address[] calldata path,
95:         address to,
96:         uint deadline // <= FOUND
97:     ) external payable returns (uint[] memory amounts);

```
['[100](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L100-L104)']
```solidity
98: 
99:     function swapTokensForExactETH(
100:         uint amountOut, // <= FOUND
101:         uint amountInMax, // <= FOUND
102:         address[] calldata path,
103:         address to,
104:         uint deadline // <= FOUND
105:     ) external returns (uint[] memory amounts);

```
['[108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L108-L112)']
```solidity
106: 
107:     function swapExactTokensForETH(
108:         uint amountIn, // <= FOUND
109:         uint amountOutMin, // <= FOUND
110:         address[] calldata path,
111:         address to,
112:         uint deadline // <= FOUND
113:     ) external returns (uint[] memory amounts);

```
['[116](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L116-L119)']
```solidity
114: 
115:     function swapETHForExactTokens(
116:         uint amountOut, // <= FOUND
117:         address[] calldata path,
118:         address to,
119:         uint deadline // <= FOUND
120:     ) external payable returns (uint[] memory amounts);

```
['[122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L122-L122)']
```solidity
121: 
122:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB); // <= FOUND

```
['[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L124-L124)']
```solidity
123: 
124:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut); // <= FOUND

```
['[126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L126-L126)']
```solidity
125: 
126:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn); // <= FOUND

```


</details>

## [NonCritical-27] Functions within contracts are not ordered according to the solidity style guide

### Resolution 
The following order should be used within contracts

constructor

receive function (if exists)

fallback function (if exists)

external

public

internal

private

Rearrange the contract functions and contructors to fit this ordering

Num of instances: 4

### Findings 


<details><summary>Click to show findings</summary>

['[20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L20)']
```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors  // <= FOUND

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33)']
```solidity
33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors  // <= FOUND

```
['[22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22-L22)']
```solidity
22: contract ImmutableCreate2Factory  // <= FOUND

```
['[22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22-L22)']
```solidity
22: contract SystemContract is SystemContractErrors  // <= FOUND

```


</details>

## [NonCritical-28] Use SafeCast to safely downcast variables

### Resolution 
Downcasting int/uints in Solidity can be unsafe due to the potential for data loss and unintended behavior. When downcasting a larger integer type to a smaller one (e.g., uint256 to uint128), the value may exceed the range of the target type, leading to truncation and loss of significant digits. This data loss can result in unexpected state changes, incorrect calculations, or other contract vulnerabilities, ultimately compromising the contracts functionality and reliability. To prevent these risks, developers should carefully consider the range of values their variables may hold and ensure that proper checks are in place to prevent out-of-range values before performing downcasting. Also consider using OZ SafeCast functionality.

Num of instances: 4

### Findings 


<details><summary>Click to show findings</summary>

['[35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L35-L35)']
```solidity
26:     function safeCreate2Internal(
27:         bytes32 salt,
28:         bytes memory initializationCode
29:     ) internal returns (address deploymentAddress) {
30:         
31:         bytes memory initCode = initializationCode;
32: 
33:         
34:         address targetDeploymentAddress = address(
35:             uint160(  // <= FOUND
36:                 uint256( 
37:                     keccak256( 
38:                         abi.encodePacked( 
39:                             hex"ff", 
40:                             address(this), 
41:                             salt, 
42:                             keccak256(abi.encodePacked(initCode)) 
43:                         )
44:                     )
45:                 )
46:             )
47:         );
48: 
49:         
50:         require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
51: 
52:         
53:         assembly {
54:             
55:             let encoded_data := add(0x20, initCode) 
56:             let encoded_size := mload(initCode) 
57:             deploymentAddress := create2(
58:                 
59:                 callvalue, 
60:                 encoded_data, 
61:                 encoded_size, 
62:                 salt 
63:             )
64:         }
65: 
66:         
67:         require(
68:             deploymentAddress == targetDeploymentAddress,
69:             "Failed to deploy contract using provided salt and initialization code."
70:         );
71: 
72:         
73:         _deployed[deploymentAddress] = true;
74:     }

```
['[114](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L114-L114)']
```solidity
108:     function findCreate2Address(
109:         bytes32 salt,
110:         bytes calldata initCode
111:     ) external view returns (address deploymentAddress) {
112:         
113:         deploymentAddress = address(
114:             uint160(  // <= FOUND
115:                 uint256( 
116:                     keccak256( 
117:                         abi.encodePacked( 
118:                             hex"ff", 
119:                             address(this), 
120:                             salt, 
121:                             keccak256(abi.encodePacked(initCode)) 
122:                         )
123:                     )
124:                 )
125:             )
126:         );
127: 
128:         
129:         if (_deployed[deploymentAddress]) {
130:             return address(0);
131:         }
132:     }

```
['[154](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L154-L154)']
```solidity
148:     function findCreate2AddressViaHash(
149:         bytes32 salt,
150:         bytes32 initCodeHash
151:     ) external view returns (address deploymentAddress) {
152:         
153:         deploymentAddress = address(
154:             uint160(  // <= FOUND
155:                 uint256( 
156:                     keccak256( 
157:                         abi.encodePacked( 
158:                             hex"ff", 
159:                             address(this), 
160:                             salt, 
161:                             initCodeHash 
162:                         )
163:                     )
164:                 )
165:             )
166:         );
167: 
168:         
169:         if (_deployed[deploymentAddress]) {
170:             return address(0);
171:         }
172:     }

```
['[103](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L103-L103)']
```solidity
100:     function uniswapv2PairFor(address factory, address tokenA, address tokenB) public pure returns (address pair) {
101:         (address token0, address token1) = sortTokens(tokenA, tokenB);
102:         pair = address(
103:             uint160( // <= FOUND
104:                 uint256(
105:                     keccak256(
106:                         abi.encodePacked(
107:                             hex"ff",
108:                             factory,
109:                             keccak256(abi.encodePacked(token0, token1)),
110:                             hex"96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f" 
111:                         )
112:                     )
113:                 )
114:             )
115:         );
116:     }

```


</details>

## [NonCritical-29] Functions which set address state variables should have zero address checks

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[114](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L114-L114)']
```solidity
114:     function setWzetaAddress(address wzeta_) external {
115:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule();
116:         wzeta = wzeta_;
117:         emit SetWZETA(wzeta_);
118:     }

```


</details>

## [NonCritical-30] Interface imports should be declared first

### Resolution 
Amend the ordering of imports to import interfaces first followed by other imports

Num of instances: 5

### Findings 


<details><summary>Click to show findings</summary>

['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L5-L11)']
```solidity
2: 
3: pragma solidity 0.8.7;
4: 
5: import "@openzeppelin/contracts/interfaces/IERC20.sol"; // <= FOUND
6: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol"; // <= FOUND
7: import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol"; // <= FOUND
8: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol"; // <= FOUND
9: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol"; // <= FOUND
10: 
11: import "../interfaces/ZetaInterfaces.sol"; // <= FOUND
12: 
13: interface ZetaTokenConsumerUniV3Errors {
14:     error InputCantBeZero();
15: 
16:     error ErrorSendingETH();
17: 
18:     error ReentrancyError();
19: }
20: 
21: interface WETH9 {
22:     function withdraw(uint256 wad) external;
23: }
24: 
28: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
29:     using SafeERC20 for IERC20;
30:     uint256 internal constant MAX_DEADLINE = 200;
31: 
32:     uint24 public immutable zetaPoolFee;
33:     uint24 public immutable tokenPoolFee;
34: 
35:     address public immutable WETH9Address;
36:     address public immutable zetaToken;
37: 
38:     ISwapRouter public immutable uniswapV3Router;
39:     IUniswapV3Factory public immutable uniswapV3Factory;
40: 
41:     bool internal _locked;
42: 
43:     constructor(
44:         address zetaToken_,
45:         address uniswapV3Router_,
46:         address uniswapV3Factory_,
47:         address WETH9Address_,
48:         uint24 zetaPoolFee_,
49:         uint24 tokenPoolFee_
50:     ) {
51:         if (
52:             zetaToken_ == address(0) ||
53:             uniswapV3Router_ == address(0) ||
54:             uniswapV3Factory_ == address(0) ||
55:             WETH9Address_ == address(0)
56:         ) revert ZetaCommonErrors.InvalidAddress();
57: 
58:         zetaToken = zetaToken_;
59:         uniswapV3Router = ISwapRouter(uniswapV3Router_);
60:         uniswapV3Factory = IUniswapV3Factory(uniswapV3Factory_);
61:         WETH9Address = WETH9Address_;
62:         zetaPoolFee = zetaPoolFee_;
63:         tokenPoolFee = tokenPoolFee_;

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L5-L9)']
```solidity
2: 
3: pragma solidity 0.8.7;
4: 
5: import "@openzeppelin/contracts/interfaces/IERC20.sol"; // <= FOUND
6: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol"; // <= FOUND
7: import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol"; // <= FOUND
8: 
9: import "../interfaces/ZetaInterfaces.sol"; // <= FOUND
10: 
11: interface ZetaTokenConsumerUniV2Errors {
12:     error InputCantBeZero();
13: }
14: 
18: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
19:     using SafeERC20 for IERC20;
20:     uint256 internal constant MAX_DEADLINE = 200;
21: 
22:     address internal immutable wETH;
23:     address public immutable zetaToken;
24: 
25:     IUniswapV2Router02 internal immutable uniswapV2Router;
26: 
27:     constructor(address zetaToken_, address uniswapV2Router_) {
28:         if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress();
29: 
30:         zetaToken = zetaToken_;
31:         uniswapV2Router = IUniswapV2Router02(uniswapV2Router_);
32:         wETH = IUniswapV2Router02(uniswapV2Router_).WETH();
33:     }
34: 
35:     function getZetaFromEth(
36:         address destinationAddress,
37:         uint256 minAmountOut
38:     ) external payable override returns (uint256) {
39:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
40:         if (msg.value == 0) revert InputCantBeZero();
41: 
42:         address[] memory path = new address[](2);
43:         path[0] = wETH;
44:         path[1] = zetaToken;
45: 
46:         uint256[] memory amounts = uniswapV2Router.swapExactETHForTokens{value: msg.value}(
47:             minAmountOut,
48:             path,
49:             destinationAddress,
50:             block.timestamp + MAX_DEADLINE
51:         );
52: 
53:         uint256 amountOut = amounts[path.length - 1];
54: 
55:         emit EthExchangedForZeta(msg.value, amountOut);
56:         return amountOut;
57:     }
58: 
59:     function getZetaFromToken(
60:         address destinationAddress,
61:         uint256 minAmountOut,

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L5-L11)']
```solidity
2: 
3: pragma solidity 0.8.7;
4: 
5: import "@openzeppelin/contracts/interfaces/IERC20.sol"; // <= FOUND
6: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol"; // <= FOUND
7: import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol"; // <= FOUND
8: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol"; // <= FOUND
9: import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol"; // <= FOUND
10: 
11: import "../interfaces/ZetaInterfaces.sol"; // <= FOUND
12: 
13: interface ZetaTokenConsumerUniV3Errors {
14:     error InputCantBeZero();
15: 
16:     error ErrorSendingETH();
17: 
18:     error ReentrancyError();
19: }
20: 
21: interface WETH9 {
22:     function withdraw(uint256 wad) external;
23: }
24: 
25: interface ISwapRouterPancake is IUniswapV3SwapCallback {
26:     struct ExactInputSingleParams {
27:         address tokenIn;
28:         address tokenOut;
29:         uint24 fee;
30:         address recipient;
31:         uint256 amountIn;
32:         uint256 amountOutMinimum;
33:         uint160 sqrtPriceLimitX96;
34:     }
35: 
39:     function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
40: 
41:     struct ExactInputParams {
42:         bytes path;
43:         address recipient;
44:         uint256 amountIn;
45:         uint256 amountOutMinimum;
46:     }
47: 
51:     function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut);
52: }
53: 
57: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
58:     using SafeERC20 for IERC20;
59:     uint256 internal constant MAX_DEADLINE = 200;
60: 
61:     uint24 public immutable zetaPoolFee;
62:     uint24 public immutable tokenPoolFee;
63: 
64:     address public immutable WETH9Address;
65:     address public immutable zetaToken;
66: 
67:     ISwapRouterPancake public immutable pancakeV3Router;
68:     IUniswapV3Factory public immutable uniswapV3Factory;
69: 

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L5-L6)']
```solidity
2: 
3: pragma solidity 0.8.7;
4: 
5: import "./interfaces/zContract.sol"; // <= FOUND
6: import "./interfaces/IZRC20.sol"; // <= FOUND
7: 
11: interface SystemContractErrors {
12:     error CallerIsNotFungibleModule();
13:     error InvalidTarget();
14:     error CantBeIdenticalAddresses();
15:     error CantBeZeroAddress();
16:     error ZeroAddress();
17: }
18: 
23: contract SystemContract is SystemContractErrors {
24:     
25:     mapping(uint256 => uint256) public gasPriceByChainId;
26:     
27:     mapping(uint256 => address) public gasCoinZRC20ByChainId;
28:     
29:     mapping(uint256 => address) public gasZetaPoolByChainId;
30: 
32:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
33:     
34:     address public immutable uniswapv2FactoryAddress;
35:     address public immutable uniswapv2Router02Address;
36:     
37:     address public wZetaContractAddress;
38:     
39:     address public zetaConnectorZEVMAddress;
40: 
42:     event SystemContractDeployed();
43:     event SetGasPrice(uint256, uint256);
44:     event SetGasCoin(uint256, address);
45:     event SetGasZetaPool(uint256, address);
46:     event SetWZeta(address);
47:     event SetConnectorZEVM(address);
48: 
52:     constructor(address wzeta_, address uniswapv2Factory_, address uniswapv2Router02_) {
53:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
54:         wZetaContractAddress = wzeta_;
55:         uniswapv2FactoryAddress = uniswapv2Factory_;
56:         uniswapv2Router02Address = uniswapv2Router02_;
57:         emit SystemContractDeployed();
58:     }
59: 
68:     function depositAndCall(
69:         zContext calldata context,
70:         address zrc20,
71:         uint256 amount,
72:         address target,
73:         bytes calldata message
74:     ) external {
75:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L5-L11)']
```solidity
2: 
3: pragma solidity 0.8.7;
4: 
5: import "@openzeppelin/contracts/interfaces/IERC20.sol"; // <= FOUND
6: import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol"; // <= FOUND
7: import "@uniswap/v3-periphery/contracts/interfaces/IQuoter.sol"; // <= FOUND
8: 
9: import "../interfaces/ZetaInterfaces.sol"; // <= FOUND
10: import "./interfaces/TridentConcentratedLiquidityPoolFactory.sol"; // <= FOUND
11: import "./interfaces/TridentIPoolRouter.sol"; // <= FOUND
12: 
13: interface ZetaTokenConsumerTridentErrors {
14:     error InputCantBeZero();
15: 
16:     error ErrorSendingETH();
17: 
18:     error ReentrancyError();
19: }
20: 
21: interface WETH9 {
22:     function deposit() external payable;
23: 
24:     function withdraw(uint256 wad) external;
25: 
26:     function depositTo(address to) external payable;
27: 
28:     function withdrawTo(address payable to, uint256 value) external;
29: }
30: 
34: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
35:     using SafeERC20 for IERC20;
36:     uint256 internal constant MAX_DEADLINE = 200;
37: 
38:     address internal immutable WETH9Address;
39:     address public immutable zetaToken;
40: 
41:     IPoolRouter public immutable tridentRouter;
42:     ConcentratedLiquidityPoolFactory public immutable poolFactory;
43: 
44:     bool internal _locked;
45: 
46:     constructor(address zetaToken_, address uniswapV3Router_, address WETH9Address_, address poolFactory_) {
47:         if (
48:             zetaToken_ == address(0) ||
49:             uniswapV3Router_ == address(0) ||
50:             WETH9Address_ == address(0) ||
51:             poolFactory_ == address(0)
52:         ) revert ZetaCommonErrors.InvalidAddress();
53: 
54:         zetaToken = zetaToken_;
55:         tridentRouter = IPoolRouter(uniswapV3Router_);
56:         poolFactory = ConcentratedLiquidityPoolFactory(poolFactory_);
57:         WETH9Address = WETH9Address_;
58:     }
59: 
60:     modifier nonReentrant() {
61:         if (_locked) revert ReentrancyError();
62:         _locked = true;
63:         _;

```


</details>

## [NonCritical-31] All interfaces used within a project should be imported

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L4-L4)']
```solidity
4: interface IWETH9  // <= FOUND

```


</details>

## [NonCritical-32] A function which defines named returns in it's declaration doesn't need to use return 

### Resolution 
Remove the return statement once ensuring it is safe to do so

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L91-L91)']
```solidity
87:     function safeCreate2(
88:         bytes32 salt,
89:         bytes memory initializationCode
90:     ) public payable containsCaller(salt) returns (address deploymentAddress) {
91:         return safeCreate2Internal(salt, initializationCode); // <= FOUND
92:     }

```
['[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L130-L130)']
```solidity
108:     function findCreate2Address(
109:         bytes32 salt,
110:         bytes calldata initCode
111:     ) external view returns (address deploymentAddress) {
112:         
113:         deploymentAddress = address(
114:             uint160( 
115:                 uint256( 
116:                     keccak256( 
117:                         abi.encodePacked( 
118:                             hex"ff", 
119:                             address(this), 
120:                             salt, 
121:                             keccak256(abi.encodePacked(initCode)) 
122:                         )
123:                     )
124:                 )
125:             )
126:         );
127: 
128:         
129:         if (_deployed[deploymentAddress]) {
130:             return address(0); // <= FOUND
131:         }
132:     }

```
['[170](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L170-L170)']
```solidity
148:     function findCreate2AddressViaHash(
149:         bytes32 salt,
150:         bytes32 initCodeHash
151:     ) external view returns (address deploymentAddress) {
152:         
153:         deploymentAddress = address(
154:             uint160( 
155:                 uint256( 
156:                     keccak256( 
157:                         abi.encodePacked( 
158:                             hex"ff", 
159:                             address(this), 
160:                             salt, 
161:                             initCodeHash 
162:                         )
163:                     )
164:                 )
165:             )
166:         );
167: 
168:         
169:         if (_deployed[deploymentAddress]) {
170:             return address(0); // <= FOUND
171:         }
172:     }

```


</details>

## [NonCritical-33] Constant/immutable state variables defined more than once

### Resolution 
Rather than redefining state variable constant/immutable, consider utilising a library to store all constants as this will prevent data redundancy

Num of instances: 7

### Findings 


<details><summary>Click to show findings</summary>

['[22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22-L22)']
```solidity
22: address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB; // <= FOUND

```
['[29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29-L29)']
```solidity
29: uint256 internal constant MAX_DEADLINE = 200; // <= FOUND

```
['[31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L31-L31)']
```solidity
31: uint24 public immutable zetaPoolFee; // <= FOUND

```
['[32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L32-L32)']
```solidity
32: uint24 public immutable tokenPoolFee; // <= FOUND

```
['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L34-L34)']
```solidity
34: address public immutable WETH9Address; // <= FOUND

```
['[35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L35-L35)']
```solidity
35: address public immutable zetaToken; // <= FOUND

```
['[38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L38-L38)']
```solidity
38: IUniswapV3Factory public immutable uniswapV3Factory; // <= FOUND

```


</details>

## [NonCritical-34] SPDX identifier should be the in the first line of a solidity file

### Resolution 
Ensure the SPDX identifier is defined in the top line of the solidity file

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L1-L1)']
```solidity
1: pragma solidity 0.5.10; // optimization enabled, 99999 runs, evm: petersburg // <= FOUND
2: 
3: interface Ownable {
4:     function transferOwnership(address newOwner) external;
5: }
6: 
7: /**
8:  * @title Immutable Create2 Contract Factory
9:  * @author 0age
10:  * @notice This contract provides a safeCreate2 function that takes a salt value
11:  * and a block of initialization code as arguments and passes them into inline
12:  * assembly. The contract prevents redeploys by maintaining a mapping of all
13:  * contracts that have already been deployed, and prevents frontrunning or other
14:  * collisions by requiring that the first 20 bytes of the salt are equal to the
15:  * address of the caller (this can be bypassed by setting the first 20 bytes to
16:  * the null address). There is also a view function that computes the address of
17:  * the contract that will be created when submitting a given salt or nonce along
18:  * with a given block of initialization code.
19:  * @dev This contract has not yet been fully tested or audited - proceed with
20:  * caution and please share any exploits or optimizations you discover.
21:  */
22: contract ImmutableCreate2Factory {
23:     // mapping to track which addresses have already been deployed.
24:     mapping(address => bool) private _deployed;
25: 
26:     function safeCreate2Internal(
27:         bytes32 salt,
28:         bytes memory initializationCode
29:     ) internal returns (address deploymentAddress) {
30:         // move the initialization code from calldata to memory.
31:         bytes memory initCode = initializationCode;
32: 
33:         // determine the target address for contract deployment.
34:         address targetDeploymentAddress = address(
35:             uint160( // downcast to match the address type.
36:                 uint256( // convert to uint to truncate upper digits.
37:                     keccak256( // compute the CREATE2 hash using 4 inputs.
38:                         abi.encodePacked( // pack all inputs to the hash together.
39:                             hex"ff", // start with 0xff to distinguish from RLP.
40:                             address(this), // this contract will be the caller.
41:                             salt, // pass in the supplied salt value.
42:                             keccak256(abi.encodePacked(initCode)) // pass in the hash of initialization code.
43:                         )
44:                     )
45:                 )
46:             )
47:         );
48: 
49:         // ensure that a contract hasn't been previously deployed to target address.
50:         require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");

```
['[1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1-L1)']
```solidity
1: pragma solidity ^0.4.18; // <= FOUND
2: 
3: contract WETH9 {
4:     string public name = "Wrapped Zeta";
5:     string public symbol = "WZETA";
6:     uint8 public decimals = 18;
7: 
8:     event Approval(address indexed src, address indexed guy, uint wad);
9:     event Transfer(address indexed src, address indexed dst, uint wad);
10:     event Deposit(address indexed dst, uint wad);
11:     event Withdrawal(address indexed src, uint wad);
12: 
13:     mapping(address => uint) public balanceOf;
14:     mapping(address => mapping(address => uint)) public allowance;
15: 
16:     function() public payable {
17:         deposit();
18:     }
19: 
20:     function deposit() public payable {
21:         balanceOf[msg.sender] += msg.value;
22:         Deposit(msg.sender, msg.value);
23:     }
24: 
25:     function withdraw(uint wad) public {
26:         require(balanceOf[msg.sender] >= wad);
27:         balanceOf[msg.sender] -= wad;
28:         msg.sender.transfer(wad);
29:         Withdrawal(msg.sender, wad);
30:     }
31: 
32:     function totalSupply() public view returns (uint) {
33:         return this.balance;
34:     }
35: 
36:     function approve(address guy, uint wad) public returns (bool) {
37:         allowance[msg.sender][guy] = wad;
38:         Approval(msg.sender, guy, wad);
39:         return true;
40:     }
41: 
42:     function transfer(address dst, uint wad) public returns (bool) {
43:         return transferFrom(msg.sender, dst, wad);
44:     }
45: 
46:     function transferFrom(address src, address dst, uint wad) public returns (bool) {
47:         require(balanceOf[src] >= wad);
48: 
49:         if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
50:             require(allowance[src][msg.sender] >= wad);

```


</details>

## [NonCritical-35] Use allowlist/denylist rather than whitelist/blacklist

Num of instances: 12

### Findings 


<details><summary>Click to show findings</summary>

['[37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L37-L37)']
```solidity
36:     
37:     mapping(IERC20 => bool) public whitelisted; // <= FOUND

```
['[41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L41-L41)']
```solidity
41:     event Unwhitelisted(IERC20 indexed asset); // <= FOUND

```
['[149](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L149-L149)']
```solidity
144: 
149:     function whitelist(IERC20 asset) external onlyTSS { // <= FOUND

```
['[145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L145-L145)']
```solidity
145:         whitelisted[asset] = true; // <= FOUND

```
['[158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L158-L158)']
```solidity
153: 
158:     function unwhitelist(IERC20 asset) external onlyTSS { // <= FOUND

```
['[154](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L154-L154)']
```solidity
154:         whitelisted[asset] = false; // <= FOUND

```
['[155](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L155-L155)']
```solidity
155:         emit Unwhitelisted(asset); // <= FOUND

```
['[174](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L174-L174)']
```solidity
174:         if (!whitelisted[asset]) { // <= FOUND

```
['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L15-L15)']
```solidity
14: 
15:     error NotWhitelisted(); // <= FOUND

```
['[40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L40-L40)']
```solidity
40:     event Whitelisted(IERC20 indexed asset); // <= FOUND

```
['[146](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L146-L146)']
```solidity
146:         emit Whitelisted(asset); // <= FOUND

```
['[175](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L175-L175)']
```solidity
175:             revert NotWhitelisted(); // <= FOUND

```


</details>

## [NonCritical-36] Multiple mappings can be replaced with a single struct mapping

### Resolution 
Using a single struct mapping in place of multiple defined mappings in a Solidity contract can lead to improved code organization, better readability, and easier maintainability. By consolidating related data into a single struct, developers can create a more cohesive data structure that logically groups together relevant pieces of information, thus reducing redundancy and clutter. This approach simplifies the codebase, making it easier to understand, navigate, and modify. Additionally, it can result in more efficient gas usage when accessing or updating multiple related data points simultaneously. 

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L34-L35)']
```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:     
22:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
23:     
24:     uint256 public immutable CHAIN_ID;
25:     
26:     CoinType public immutable COIN_TYPE;
27:     
28:     address public SYSTEM_CONTRACT_ADDRESS;
29:     
30:     uint256 public GAS_LIMIT;
31:     
32:     uint256 public PROTOCOL_FLAT_FEE;
33: 
34:     mapping(address => uint256) private _balances; // <= FOUND
35:     mapping(address => mapping(address => uint256)) private _allowances; // <= FOUND
36:     uint256 private _totalSupply;
37:     string private _name;
38:     string private _symbol;
39:     uint8 private _decimals;
40: 
172: }

```
['[24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L24-L28)']
```solidity
22: contract SystemContract is SystemContractErrors {
23:     
24:     mapping(uint256 => uint256) public gasPriceByChainId; // <= FOUND
25:     
26:     mapping(uint256 => address) public gasCoinZRC20ByChainId; // <= FOUND
27:     
28:     mapping(uint256 => address) public gasZetaPoolByChainId; // <= FOUND
29: 
31:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB;
32:     
33:     address public immutable uniswapv2FactoryAddress;
34:     address public immutable uniswapv2Router02Address;
35:     
36:     address public wZetaContractAddress;
37:     
38:     address public zetaConnectorZEVMAddress;
39: 
112: }

```
['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L13-L14)']
```solidity
3: contract WETH9 {
4:     string public name = "Wrapped Zeta";
5:     string public symbol = "WZETA";
6:     uint8 public decimals = 18;
7: 
13:     mapping(address => uint) public balanceOf; // <= FOUND
14:     mapping(address => mapping(address => uint)) public allowance; // <= FOUND
15: 
16:     function() public payable {
17:         deposit();
18:     }
19: 
31: }

```


</details>

## [NonCritical-37] Having chainId as a parameter can introduce cross chain replay attacks

### Resolution 
Accepting chainId as a parameter in a Solidity contract could open up possibilities for cross-chain replay attacks. An attacker could execute a transaction on one chain, then 'replay' it on another chain where the contract has been deployed, leading to unintended consequences. It's crucial to get the chainId within the contract using `block.chainId` to ensure that the transactions are valid and specific to the chain the contract resides on. The `block.chainId` value is provided by the EVM and can be trusted, as it's difficult to manipulate and is unique to each Ethereum-based network. This enhances the security of cross-chain operations.

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[123](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L123-L123)']
```solidity
123:     function setGasPrice(uint256 chainID, uint256 price) external  // <= FOUND

```
['[134](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L134-L134)']
```solidity
134:     function setGasCoinZRC20(uint256 chainID, address zrc20) external  // <= FOUND

```
['[145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L145-L145)']
```solidity
145:     function setGasZetaPool(uint256 chainID, address erc20) external  // <= FOUND

```


</details>

## [NonCritical-38] Unused modifiers present

### Resolution 
If these serve no purpose, they should be safely removed

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[23](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23-L23)']
```solidity
23:     modifier isValidMessageCall(ZetaInterfaces.ZetaMessage calldata zetaMessage) { // <= FOUND
24:         _isValidCaller();
25:         if (keccak256(zetaMessage.zetaTxSenderAddress) != keccak256(interactorsByChainId[zetaMessage.sourceChainId]))
26:             revert InvalidZetaMessageCall();
27:         _;
28:     }

```
['[30](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L30-L30)']
```solidity
30:     modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) { // <= FOUND
31:         _isValidCaller();
32:         if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall();
33:         if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall();
34:         _;
35:     }

```


</details>

## [NonCritical-39] Constants should be on the left side of the 

### Resolution 
Putting constants on the left side of a comparison operator like `==` or `<` is a best practice known as "Yoda conditions", which can help prevent accidental assignment instead of comparison. In some programming languages, if a variable is mistakenly put on the left with a single `=` instead of `==`, it assigns the constant's value to the variable without any compiler error. However, doing this with the constant on the left would generate an error, as constants cannot be assigned values. Although Solidity's static typing system prevents accidental assignments within conditionals, adopting this practice enhances code readability and consistency, especially when developers are working across multiple languages that support this convention.

Num of instances: 4

### Findings 


<details><summary>Click to show findings</summary>

['[242](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L242-L242)']
```solidity
242:         if (gasPrice == 0)  // <= FOUND

```
['[93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L93-L93)']
```solidity
93:        if (zetaFee_ == 0)  // <= FOUND

```
['[177](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L177-L177)']
```solidity
177:         if (zetaFee != 0 && address(zeta) != address(0))  // <= FOUND

```
['[63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L63-L63)']
```solidity
63:         if (message.length > 0)  // <= FOUND

```


</details>

## [NonCritical-40] Interface names should have an I as the first character

### Resolution 
Modify such instances to include a capital I as the first character in the name to signify it is an interface. This improved readability during in

Num of instances: 19

### Findings 


<details><summary>Click to show findings</summary>

['[8](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L8-L8)']
```solidity
8: interface ZRC20Errors 

```
['[12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L12-L12)']
```solidity
12: interface ZetaTokenConsumerUniV3Errors 

```
['[20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L20-L20)']
```solidity
20: interface WETH9 

```
['[12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L12-L12)']
```solidity
12: interface ZetaTokenConsumerTridentErrors 

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L10-L10)']
```solidity
10: interface ZetaTokenConsumerUniV2Errors 

```
['[3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L3-L3)']
```solidity
3: interface Ownable 

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L10-L10)']
```solidity
10: interface SystemContractErrors 

```
['[4](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L4-L4)']
```solidity
4: interface ZetaInterfaces 

```
['[49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L49-L49)']
```solidity
49: interface WZETA 

```
['[49](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L49-L49)']
```solidity
49: interface ZetaConnector 

```
['[56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L56-L56)']
```solidity
56: interface ZetaReceiver 

```
['[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L77-L77)']
```solidity
77: interface ZetaTokenConsumer 

```
['[108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInterfaces.sol#L108-L108)']
```solidity
108: interface ZetaCommonErrors 

```
['[7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaErrors.sol#L7-L7)']
```solidity
7: interface ZetaErrors 

```
['[7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ConnectorErrors.sol#L7-L7)']
```solidity
7: interface ConnectorErrors 

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/zContract.sol#L10-L10)']
```solidity
10: interface zContract 

```
['[7](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaInteractorErrors.sol#L7-L7)']
```solidity
7: interface ZetaInteractorErrors 

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L9-L9)']
```solidity
9: interface ZetaNonEthInterface is IERC20 

```
['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentConcentratedLiquidityPoolFactory.sol#L15-L15)']
```solidity
15: interface ConcentratedLiquidityPoolFactory 

```


</details>

## [NonCritical-41] Both immutable and constant state variables should be CONSTANT_CASE

### Resolution 
Make found instants CAPITAL_CASE

Num of instances: 18

### Findings 


<details><summary>Click to show findings</summary>

['[31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L31-L31)']
```solidity
31: uint24 public immutable zetaPoolFee; // <= FOUND

```
['[35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L35-L35)']
```solidity
35: address public immutable zetaToken; // <= FOUND

```
['[66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L66-L66)']
```solidity
66: ISwapRouterPancake public immutable pancakeV3Router; // <= FOUND

```
['[38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L38-L38)']
```solidity
38: IUniswapV3Factory public immutable uniswapV3Factory; // <= FOUND

```
['[41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L41-L41)']
```solidity
41: ConcentratedLiquidityPoolFactory public immutable poolFactory; // <= FOUND

```
['[37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L37-L37)']
```solidity
37: ISwapRouter public immutable uniswapV3Router; // <= FOUND

```
['[32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L32-L32)']
```solidity
32: uint256 public immutable zetaMaxFee; // <= FOUND

```
['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L34-L34)']
```solidity
34: IERC20 public immutable zeta; // <= FOUND

```
['[24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L24-L24)']
```solidity
24: IUniswapV2Router02 internal immutable uniswapV2Router; // <= FOUND

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L33-L33)']
```solidity
33: address public immutable uniswapv2FactoryAddress; // <= FOUND

```
['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L34-L34)']
```solidity
34: address public immutable uniswapv2Router02Address; // <= FOUND

```
['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L11-L11)']
```solidity
11: uint256 internal immutable currentChainId; // <= FOUND

```
['[12](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L12-L12)']
```solidity
12: ZetaConnector public immutable connector; // <= FOUND

```
['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L34-L34)']
```solidity
34: address public immutable WETH9Address; // <= FOUND

```
['[37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L37-L37)']
```solidity
37: address internal immutable WETH9Address; // <= FOUND

```
['[40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L40-L40)']
```solidity
40: IPoolRouter public immutable tridentRouter; // <= FOUND

```
['[32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L32-L32)']
```solidity
32: uint24 public immutable tokenPoolFee; // <= FOUND

```
['[21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L21-L21)']
```solidity
21: address internal immutable wETH; // <= FOUND

```


</details>

## [NonCritical-42] Consider using named mappings

### Resolution 
In Solidity version 0.8.18 and beyond mapping parameters can be named. This makes the purpose and function of a given mapping far clearer which in turn improves readability.

Num of instances: 10

### Findings 


<details><summary>Click to show findings</summary>

['[36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L36-L36)']
```solidity
36:     mapping(IERC20 => bool) public whitelisted; // <= FOUND

```
['[24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L24-L24)']
```solidity
24:     mapping(address => bool) private _deployed; // <= FOUND

```
['[26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L26-L26)']
```solidity
26:     mapping(uint256 => address) public gasCoinZRC20ByChainId; // <= FOUND

```
['[28](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L28-L28)']
```solidity
28:     mapping(uint256 => address) public gasZetaPoolByChainId; // <= FOUND

```
['[21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L21-L21)']
```solidity
21:     mapping(uint256 => bytes) public interactorsByChainId; // <= FOUND

```
['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L13-L13)']
```solidity
13:     mapping(address => uint) public balanceOf; // <= FOUND

```
['[14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L14-L14)']
```solidity
14:     mapping(address => mapping(address => uint)) public allowance; // <= FOUND

```
['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L34-L34)']
```solidity
34:     mapping(address => uint256) private _balances; // <= FOUND

```
['[35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L35-L35)']
```solidity
35:     mapping(address => mapping(address => uint256)) private _allowances; // <= FOUND

```
['[24](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L24-L24)']
```solidity
24:     mapping(uint256 => uint256) public gasPriceByChainId; // <= FOUND

```


</details>

## [NonCritical-43] Use type(uint<n>).max in place of 2 ** n - 1

### Resolution 
There is an inbuilt functionality to get the max value of a uint, it makes more sense to use this to improve readability

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16-L16)']
```solidity
16:     uint256 public maxSupply = 2 ** 256 - 1; // <= FOUND

```


</details>

## [NonCritical-44] Use a single contract or library for system wide constants

Num of instances: 7

### Findings 


<details><summary>Click to show findings</summary>

['[22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L22-L22)']
```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors {
21:     
22:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB; // <= FOUND
23:     
24:     uint256 public immutable CHAIN_ID;
25:     
26:     CoinType public immutable COIN_TYPE;
27:     
28:     address public SYSTEM_CONTRACT_ADDRESS;
29:     
30:     uint256 public GAS_LIMIT;
31:     
32:     uint256 public PROTOCOL_FLAT_FEE;
33: 
34:     mapping(address => uint256) private _balances;
35:     mapping(address => mapping(address => uint256)) private _allowances;
36:     uint256 private _totalSupply;
37:     string private _name;
38:     string private _symbol;
39:     uint8 private _decimals;
40: 
172: }

```
['[58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L58-L58)']
```solidity
56: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
57:     using SafeERC20 for IERC20;
58:     uint256 internal constant MAX_DEADLINE = 200; // <= FOUND
59: 
60:     uint24 public immutable zetaPoolFee;
61:     uint24 public immutable tokenPoolFee;
62: 
63:     address public immutable WETH9Address;
64:     address public immutable zetaToken;
65: 
66:     ISwapRouterPancake public immutable pancakeV3Router;
67:     IUniswapV3Factory public immutable uniswapV3Factory;
68: 
69:     bool internal _locked;
70: 
86: }

```
['[35](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L35-L35)']
```solidity
33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors {
34:     using SafeERC20 for IERC20;
35:     uint256 internal constant MAX_DEADLINE = 200; // <= FOUND
36: 
37:     address internal immutable WETH9Address;
38:     address public immutable zetaToken;
39: 
40:     IPoolRouter public immutable tridentRouter;
41:     ConcentratedLiquidityPoolFactory public immutable poolFactory;
42: 
43:     bool internal _locked;
44: 
62: }

```
['[29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L29-L29)']
```solidity
27: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors {
28:     using SafeERC20 for IERC20;
29:     uint256 internal constant MAX_DEADLINE = 200; // <= FOUND
30: 
31:     uint24 public immutable zetaPoolFee;
32:     uint24 public immutable tokenPoolFee;
33: 
34:     address public immutable WETH9Address;
35:     address public immutable zetaToken;
36: 
37:     ISwapRouter public immutable uniswapV3Router;
38:     IUniswapV3Factory public immutable uniswapV3Factory;
39: 
40:     bool internal _locked;
41: 
57: }

```
['[19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L19-L19)']
```solidity
17: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors {
18:     using SafeERC20 for IERC20;
19:     uint256 internal constant MAX_DEADLINE = 200; // <= FOUND
20: 
21:     address internal immutable wETH;
22:     address public immutable zetaToken;
23: 
24:     IUniswapV2Router02 internal immutable uniswapV2Router;
25: 
37: }

```
['[31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L31-L31)']
```solidity
22: contract SystemContract is SystemContractErrors {
23:     
24:     mapping(uint256 => uint256) public gasPriceByChainId;
25:     
26:     mapping(uint256 => address) public gasCoinZRC20ByChainId;
27:     
28:     mapping(uint256 => address) public gasZetaPoolByChainId;
29: 
31:     address public constant FUNGIBLE_MODULE_ADDRESS = 0x735b14BB79463307AAcBED86DAf3322B1e6226aB; // <= FOUND
32:     
33:     address public immutable uniswapv2FactoryAddress;
34:     address public immutable uniswapv2Router02Address;
35:     
36:     address public wZetaContractAddress;
37:     
38:     address public zetaConnectorZEVMAddress;
39: 
112: }

```
['[63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63-L63)']
```solidity
55: contract ZetaConnectorZEVM is ZetaInterfaces {
56:     
63:     address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB); // <= FOUND
64:     
65:     address public wzeta;
66: 
86: }

```


</details>

## [NonCritical-45] Consider using modifiers for address control

### Resolution 
Modifiers in Solidity can improve code readability and modularity by encapsulating repetitive checks, such as address validity checks, into a reusable construct. For example, an `onlyOwner` modifier can be used to replace repetitive `require(msg.sender == owner)` checks across several functions, reducing code redundancy and enhancing maintainability. To implement, define a modifier with the check, then apply the modifier to relevant functions.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[195](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L195-L198)']
```solidity
195:         
196:         
197:         require(
198:             (address(bytes20(salt)) == msg.sender) || (bytes20(salt) == bytes20(0)), // <= FOUND
199:             "Invalid salt - first 20 bytes of the salt must match calling address."
200:         );

```


</details>

## [NonCritical-46] Default address(0) can be returned

### Resolution 
Allowing a function in Solidity to return the default address (address(0)) can be problematic as it can represent uninitialized or invalid addresses. If such an address is utilized in transfer operations or other sensitive actions, it could lead to loss of funds or unpredicted behavior. It's prudent to include checks in your functions to prevent the return of the zero address, enhancing contract security.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[68](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L68-L68)']
```solidity
68:     function getPair(address token0, address token1) internal pure returns (address, address) {
69:         if (token0 < token1) return (token0, token1);
70: 
71:         return (token1, token0);
72:     }

```


</details>

## [NonCritical-47] Mixed usage of int/uint with int256/uint256

### Resolution 
Use uint256/int256 in place of uint/int to prevent ambiguity

Num of instances: 43

### Findings 


<details><summary>Click to show findings</summary>

['[50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L50-L50)']
```solidity
50:     function transferFrom(address src, address dst, uint wad) external returns (bool); // <= FOUND

```
['[53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L53-L53)']
```solidity
52: 
53:     function withdraw(uint wad) external; // <= FOUND

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L9-L9)']
```solidity
8: 
9:     event Approval(address indexed src, address indexed guy, uint wad); // <= FOUND

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L9-L9)']
```solidity
9:     event Transfer(address indexed src, address indexed dst, uint wad); // <= FOUND

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L10-L10)']
```solidity
10:     event Deposit(address indexed dst, uint wad); // <= FOUND

```
['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L11-L11)']
```solidity
11:     event Withdrawal(address indexed src, uint wad); // <= FOUND

```
['[26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L26-L26)']
```solidity
25: 
26:     function withdraw(uint wad) public { // <= FOUND

```
['[37](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L37-L37)']
```solidity
36: 
37:     function approve(address guy, uint wad) public returns (bool) { // <= FOUND

```
['[43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L43-L43)']
```solidity
42: 
43:     function transfer(address dst, uint wad) public returns (bool) { // <= FOUND

```
['[47](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L47-L47)']
```solidity
46: 
47:     function transferFrom(address src, address dst, uint wad) public returns (bool) { // <= FOUND

```
['[5](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L5-L5)']
```solidity
5:     event Approval(address indexed owner, address indexed spender, uint value); // <= FOUND

```
['[6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L6-L6)']
```solidity
6:     event Transfer(address indexed from, address indexed to, uint value); // <= FOUND

```
['[17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L17-L17)']
```solidity
16: 
17:     function approve(address spender, uint wad) external returns (bool); // <= FOUND

```
['[19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L19-L19)']
```solidity
18: 
19:     function transfer(address to, uint wad) external returns (bool); // <= FOUND

```
['[21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L21-L21)']
```solidity
20: 
21:     function transferFrom(address from, address to, uint wad) external returns (bool); // <= FOUND

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L9-L14)']
```solidity
7:     function removeLiquidityETHSupportingFeeOnTransferTokens(
8:         address token,
9:         uint liquidity, // <= FOUND
10:         uint amountTokenMin, // <= FOUND
11:         uint amountETHMin, // <= FOUND
12:         address to,
13:         uint deadline // <= FOUND
14:     ) external returns (uint amountETH); // <= FOUND

```
['[19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L19-L28)']
```solidity
16: 
17:     function removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(
18:         address token,
19:         uint liquidity, // <= FOUND
20:         uint amountTokenMin, // <= FOUND
21:         uint amountETHMin, // <= FOUND
22:         address to,
23:         uint deadline, // <= FOUND
24:         bool approveMax,
25:         uint8 v,
26:         bytes32 r,
27:         bytes32 s
28:     ) external returns (uint amountETH); // <= FOUND

```
['[31](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L31-L35)']
```solidity
29: 
30:     function swapExactTokensForTokensSupportingFeeOnTransferTokens(
31:         uint amountIn, // <= FOUND
32:         uint amountOutMin, // <= FOUND
33:         address[] calldata path,
34:         address to,
35:         uint deadline // <= FOUND
36:     ) external;

```
['[39](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L39-L42)']
```solidity
37: 
38:     function swapExactETHForTokensSupportingFeeOnTransferTokens(
39:         uint amountOutMin, // <= FOUND
40:         address[] calldata path,
41:         address to,
42:         uint deadline // <= FOUND
43:     ) external payable;

```
['[46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router02.sol#L46-L50)']
```solidity
44: 
45:     function swapExactTokensForETHSupportingFeeOnTransferTokens(
46:         uint amountIn, // <= FOUND
47:         uint amountOutMin, // <= FOUND
48:         address[] calldata path,
49:         address to,
50:         uint deadline // <= FOUND
51:     ) external;

```
['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L13-L19)']
```solidity
9: 
10:     function addLiquidity(
11:         address tokenA,
12:         address tokenB,
13:         uint amountADesired, // <= FOUND
14:         uint amountBDesired, // <= FOUND
15:         uint amountAMin, // <= FOUND
16:         uint amountBMin, // <= FOUND
17:         address to,
18:         uint deadline // <= FOUND
19:     ) external returns (uint amountA, uint amountB, uint liquidity); // <= FOUND

```
['[23](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L23-L28)']
```solidity
20: 
21:     function addLiquidityETH(
22:         address token,
23:         uint amountTokenDesired, // <= FOUND
24:         uint amountTokenMin, // <= FOUND
25:         uint amountETHMin, // <= FOUND
26:         address to,
27:         uint deadline // <= FOUND
28:     ) external payable returns (uint amountToken, uint amountETH, uint liquidity); // <= FOUND

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L33-L38)']
```solidity
29: 
30:     function removeLiquidity(
31:         address tokenA,
32:         address tokenB,
33:         uint liquidity, // <= FOUND
34:         uint amountAMin, // <= FOUND
35:         uint amountBMin, // <= FOUND
36:         address to,
37:         uint deadline // <= FOUND
38:     ) external returns (uint amountA, uint amountB); // <= FOUND

```
['[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L42-L47)']
```solidity
39: 
40:     function removeLiquidityETH(
41:         address token,
42:         uint liquidity, // <= FOUND
43:         uint amountTokenMin, // <= FOUND
44:         uint amountETHMin, // <= FOUND
45:         address to,
46:         uint deadline // <= FOUND
47:     ) external returns (uint amountToken, uint amountETH); // <= FOUND

```
['[52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L52-L61)']
```solidity
48: 
49:     function removeLiquidityWithPermit(
50:         address tokenA,
51:         address tokenB,
52:         uint liquidity, // <= FOUND
53:         uint amountAMin, // <= FOUND
54:         uint amountBMin, // <= FOUND
55:         address to,
56:         uint deadline, // <= FOUND
57:         bool approveMax,
58:         uint8 v,
59:         bytes32 r,
60:         bytes32 s
61:     ) external returns (uint amountA, uint amountB); // <= FOUND

```
['[65](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L65-L74)']
```solidity
62: 
63:     function removeLiquidityETHWithPermit(
64:         address token,
65:         uint liquidity, // <= FOUND
66:         uint amountTokenMin, // <= FOUND
67:         uint amountETHMin, // <= FOUND
68:         address to,
69:         uint deadline, // <= FOUND
70:         bool approveMax,
71:         uint8 v,
72:         bytes32 r,
73:         bytes32 s
74:     ) external returns (uint amountToken, uint amountETH); // <= FOUND

```
['[77](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L77-L81)']
```solidity
75: 
76:     function swapExactTokensForTokens(
77:         uint amountIn, // <= FOUND
78:         uint amountOutMin, // <= FOUND
79:         address[] calldata path,
80:         address to,
81:         uint deadline // <= FOUND
82:     ) external returns (uint[] memory amounts);

```
['[85](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L85-L89)']
```solidity
83: 
84:     function swapTokensForExactTokens(
85:         uint amountOut, // <= FOUND
86:         uint amountInMax, // <= FOUND
87:         address[] calldata path,
88:         address to,
89:         uint deadline // <= FOUND
90:     ) external returns (uint[] memory amounts);

```
['[93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L93-L96)']
```solidity
91: 
92:     function swapExactETHForTokens(
93:         uint amountOutMin, // <= FOUND
94:         address[] calldata path,
95:         address to,
96:         uint deadline // <= FOUND
97:     ) external payable returns (uint[] memory amounts);

```
['[100](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L100-L104)']
```solidity
98: 
99:     function swapTokensForExactETH(
100:         uint amountOut, // <= FOUND
101:         uint amountInMax, // <= FOUND
102:         address[] calldata path,
103:         address to,
104:         uint deadline // <= FOUND
105:     ) external returns (uint[] memory amounts);

```
['[108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L108-L112)']
```solidity
106: 
107:     function swapExactTokensForETH(
108:         uint amountIn, // <= FOUND
109:         uint amountOutMin, // <= FOUND
110:         address[] calldata path,
111:         address to,
112:         uint deadline // <= FOUND
113:     ) external returns (uint[] memory amounts);

```
['[116](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L116-L119)']
```solidity
114: 
115:     function swapETHForExactTokens(
116:         uint amountOut, // <= FOUND
117:         address[] calldata path,
118:         address to,
119:         uint deadline // <= FOUND
120:     ) external payable returns (uint[] memory amounts);

```
['[122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L122-L122)']
```solidity
121: 
122:     function quote(uint amountA, uint reserveA, uint reserveB) external pure returns (uint amountB); // <= FOUND

```
['[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L124-L124)']
```solidity
123: 
124:     function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut) external pure returns (uint amountOut); // <= FOUND

```
['[126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L126-L126)']
```solidity
125: 
126:     function getAmountIn(uint amountOut, uint reserveIn, uint reserveOut) external pure returns (uint amountIn); // <= FOUND

```
['[128](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L128-L128)']
```solidity
127: 
128:     function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts); // <= FOUND

```
['[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IUniswapV2Router01.sol#L130-L130)']
```solidity
129: 
130:     function getAmountsIn(uint amountOut, address[] calldata path) external view returns (uint[] memory amounts); // <= FOUND

```
['[14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L14-L14)']
```solidity
13: 
14:     mapping(address => uint) public balanceOf; // <= FOUND

```
['[14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L14-L14)']
```solidity
14:     mapping(address => mapping(address => uint)) public allowance; // <= FOUND

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L33-L33)']
```solidity
32: 
33:     function totalSupply() public view returns (uint) { // <= FOUND

```
['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L11-L11)']
```solidity
10: 
11:     function totalSupply() external view returns (uint); // <= FOUND

```
['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L13-L13)']
```solidity
12: 
13:     function balanceOf(address owner) external view returns (uint); // <= FOUND

```
['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/interfaces/IWZETA.sol#L15-L15)']
```solidity
14: 
15:     function allowance(address owner, address spender) external view returns (uint); // <= FOUND

```


</details>

## [NonCritical-48] Custom error has no error variables

### Resolution 
In Solidity, the use of custom error messages provides a valuable method of conveying meaningful information about failures during execution. In the current implementation, the custom errors lack specifics, making it challenging to understand the root cause of a failure. It's advisable to incorporate parameters into your error messages to indicate which user action or specific value caused the exception. This not only enhances error transparency but also aids debugging and fosters a more robust and maintainable codebase. Providing such precise error context greatly helps developers identify and resolve issues faster.

Num of instances: 12

### Findings 


<details><summary>Click to show findings</summary>

['[14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L14-L14)']
```solidity
14: error NotWhitelisted(); // <= FOUND

```
['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L15-L15)']
```solidity
15: error NotPaused(); // <= FOUND

```
['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L11-L11)']
```solidity
11: error InvalidSender(); // <= FOUND

```
['[17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L17-L17)']
```solidity
17: error InvalidTSSUpdater(); // <= FOUND

```
['[17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L17-L17)']
```solidity
17: error ZeroAddress(); // <= FOUND

```
['[19](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L19-L19)']
```solidity
19: error IsPaused(); // <= FOUND

```
['[20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L20-L20)']
```solidity
20: error ZetaMaxFeeExceeded(); // <= FOUND

```
['[21](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L21-L21)']
```solidity
21: error ZeroFee(); // <= FOUND

```
['[57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L57-L57)']
```solidity
57: error OnlyWZETA(); // <= FOUND

```
['[58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L58-L58)']
```solidity
58: error WZETATransferFailed(); // <= FOUND

```
['[59](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L59-L59)']
```solidity
59: error OnlyFungibleModule(); // <= FOUND

```
['[60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L60-L60)']
```solidity
60: error FailedZetaSent(); // <= FOUND

```


</details>

## [NonCritical-49] Event emit should emit a parameter

### Resolution 
Events in Solidity offer valuable insight into the contract's execution as they log specific instances of state changes or value transfers. However, if events do not include any parameters, their usefulness can be significantly reduced. Events without parameters can provide limited information, mainly signaling that a specific operation occurred, but lacking the context of what exactly changed. It's generally recommended to include relevant parameters, such as state changes or value modifications, in the emitted events. 

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L56-L56)']
```solidity
56:         emit SystemContractDeployed(); // <= FOUND

```


</details>

## [NonCritical-50] Unused structs present

### Resolution 
If these serve no purpose, they should be safely removed

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L34-L34)']
```solidity
34:     struct ExactOutputSingleParams { // <= FOUND
35:         address tokenIn; 
36:         uint256 amountOut; 
37:         uint256 amountInMaximum; 
38:         address pool; 
39:         address to; 
40:         bool unwrap; 
41:     }

```
['[43](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L43-L43)']
```solidity
43:     struct ExactOutputParams { // <= FOUND
44:         address tokenIn; 
45:         uint256 amountOut; 
46:         uint256 amountInMaximum; 
47:         address[] path; 
48:         address to; 
49:         bool unwrap; 
50:     }

```


</details>

## [NonCritical-51] Addresses shouldn't be hard-coded

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[63](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L63-L65)']
```solidity
63: 
65:     address public constant FUNGIBLE_MODULE_ADDRESS = payable(0x735b14BB79463307AAcBED86DAf3322B1e6226aB); // <= FOUND

```


</details>

## [NonCritical-52] Empty bytes check is missing

### Resolution 
When developing smart contracts in Solidity, it's crucial to validate the inputs of your functions. This includes ensuring that the bytes parameters are not empty, especially when they represent crucial data such as addresses, identifiers, or raw data that the contract needs to process.

Missing empty bytes checks can lead to unexpected behaviour in your contract. For instance, certain operations might fail, produce incorrect results, or consume unnecessary gas when performed with empty bytes. Moreover, missing input validation can potentially expose your contract to malicious activity, including exploitation of unhandled edge cases.

To mitigate these issues, always validate that bytes parameters are not empty when the logic of your contract requires it.

Num of instances: 10

### Findings 


<details><summary>Click to show findings</summary>

['[256](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256-L256)']
```solidity
256:     function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
257:         (address gasZRC20, uint256 gasFee) = withdrawGasFee();
258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
259:             revert GasFeeTransferFailed();
260:         }
261:         _burn(msg.sender, amount);
262:         emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);
263:         return true;
264:     }

```
['[165](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L165)']
```solidity
165:     function deposit(
166:         bytes calldata recipient,
167:         IERC20 asset,
168:         uint256 amount,
169:         bytes calldata message
170:     ) external nonReentrant {
171:         if (paused) {
172:             revert IsPaused();
173:         }
174:         if (!whitelisted[asset]) {
175:             revert NotWhitelisted();
176:         }
177:         if (zetaFee != 0 && address(zeta) != address(0)) {
178:             zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
179:         }
180:         uint256 oldBalance = asset.balanceOf(address(this));
181:         asset.safeTransferFrom(msg.sender, address(this), amount);
182:         
183:         
184:         emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
185:     }

```
['[26](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L26-L26)']
```solidity
26:     function safeCreate2Internal(
27:         bytes32 salt,
28:         bytes memory initializationCode
29:     ) internal returns (address deploymentAddress) {
30:         
31:         bytes memory initCode = initializationCode;
32: 
33:         
34:         address targetDeploymentAddress = address(
35:             uint160( 
36:                 uint256( 
37:                     keccak256( 
38:                         abi.encodePacked( 
39:                             hex"ff", 
40:                             address(this), 
41:                             salt, 
42:                             keccak256(abi.encodePacked(initCode)) 
43:                         )
44:                     )
45:                 )
46:             )
47:         );
48: 
49:         
50:         require(!_deployed[targetDeploymentAddress], "Invalid contract creation - contract has already been deployed.");
51: 
52:         
53:         assembly {
54:             
55:             let encoded_data := add(0x20, initCode) 
56:             let encoded_size := mload(initCode) 
57:             deploymentAddress := create2(
58:                 
59:                 callvalue, 
60:                 encoded_data, 
61:                 encoded_size, 
62:                 salt 
63:             )
64:         }
65: 
66:         
67:         require(
68:             deploymentAddress == targetDeploymentAddress,
69:             "Failed to deploy contract using provided salt and initialization code."
70:         );
71: 
72:         
73:         _deployed[deploymentAddress] = true;
74:     }

```
['[87](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L87-L87)']
```solidity
87:     function safeCreate2(
88:         bytes32 salt,
89:         bytes memory initializationCode
90:     ) public payable containsCaller(salt) returns (address deploymentAddress) {
91:         return safeCreate2Internal(salt, initializationCode);
92:     }

```
['[108](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L108-L108)']
```solidity
108:     function findCreate2Address(
109:         bytes32 salt,
110:         bytes calldata initCode
111:     ) external view returns (address deploymentAddress) {
112:         
113:         deploymentAddress = address(
114:             uint160( 
115:                 uint256( 
116:                     keccak256( 
117:                         abi.encodePacked( 
118:                             hex"ff", 
119:                             address(this), 
120:                             salt, 
121:                             keccak256(abi.encodePacked(initCode)) 
122:                         )
123:                     )
124:                 )
125:             )
126:         );
127: 
128:         
129:         if (_deployed[deploymentAddress]) {
130:             return address(0);
131:         }
132:     }

```
['[148](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L148-L148)']
```solidity
148:     function findCreate2AddressViaHash(
149:         bytes32 salt,
150:         bytes32 initCodeHash
151:     ) external view returns (address deploymentAddress) {
152:         
153:         deploymentAddress = address(
154:             uint160( 
155:                 uint256( 
156:                     keccak256( 
157:                         abi.encodePacked( 
158:                             hex"ff", 
159:                             address(this), 
160:                             salt, 
161:                             initCodeHash 
162:                         )
163:                     )
164:                 )
165:             )
166:         );
167: 
168:         
169:         if (_deployed[deploymentAddress]) {
170:             return address(0);
171:         }
172:     }

```
['[202](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L202-L202)']
```solidity
202:     function safeCreate2AndTransfer(
203:         bytes32 salt,
204:         bytes calldata initializationCode
205:     ) external payable containsCaller(salt) returns (address deploymentAddress) {
206:         deploymentAddress = safeCreate2Internal(salt, initializationCode);
207:         Ownable(deploymentAddress).transferOwnership(msg.sender);
208:     }

```
['[67](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L67-L67)']
```solidity
67:     function depositAndCall(
68:         zContext calldata context,
69:         address zrc20,
70:         uint256 amount,
71:         address target,
72:         bytes calldata message
73:     ) external {
74:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
75:         if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget();
76: 
77:         IZRC20(zrc20).deposit(target, amount);
78:         zContract(target).onCrossChainCall(context, zrc20, amount, message);
79:     }

```
['[62](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L62)']
```solidity
62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override {
63:         
64: 
66:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
67: 
68:         _mint(mintee, value);
69: 
70:         emit Minted(mintee, value, internalSendHash);
71:     }

```
['[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L54-L54)']
```solidity
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner {
55:         interactorsByChainId[destinationChainId] = contractAddress;
56:     }

```


</details>

## [NonCritical-53] Return bool not explicit

### Resolution 
In Solidity, when designing functions that return boolean values, it's crucial for clarity and maintainability to explicitly handle both `true` and `false` return scenarios. If a function is intended to return `true` under certain conditions, it should also explicitly return `false` when these conditions are not met, and vice versa. This approach eliminates ambiguity and makes the code's intent more transparent. Explicitly handling all possible outcomes of a boolean function ensures that future modifications or extensions of the contract do not unintentionally alter its logic. It contributes to better readability, easier debugging, and reduces the risk of bugs related to unintended fall-through cases.

Num of instances: 10

### Findings 


<details><summary>Click to show findings</summary>

['[125](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125-L127)']
```solidity
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
126:         _transfer(_msgSender(), recipient, amount);
127:         return true; // <= FOUND
128:     }

```
['[145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145-L147)']
```solidity
145:     function approve(address spender, uint256 amount) public virtual override returns (bool) {
146:         _approve(_msgSender(), spender, amount);
147:         return true; // <= FOUND
148:     }

```
['[157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157-L165)']
```solidity
157:     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool) {
158:         _transfer(sender, recipient, amount);
159: 
160:         uint256 currentAllowance = _allowances[sender][_msgSender()];
161:         if (currentAllowance < amount) revert LowAllowance();
162: 
163:         _approve(sender, _msgSender(), currentAllowance - amount);
164: 
165:         return true; // <= FOUND
166:     }

```
['[173](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L173-L175)']
```solidity
173:     function burn(uint256 amount) external returns (bool) {
174:         _burn(msg.sender, amount);
175:         return true; // <= FOUND
176:     }

```
['[225](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225-L229)']
```solidity
225:     function deposit(address to, uint256 amount) external override returns (bool) {
226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender();
227:         _mint(to, amount);
228:         emit Deposit(abi.encodePacked(FUNGIBLE_MODULE_ADDRESS), to, amount);
229:         return true; // <= FOUND
230:     }

```
['[256](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256-L263)']
```solidity
256:     function withdraw(bytes memory to, uint256 amount) external override returns (bool) {
257:         (address gasZRC20, uint256 gasFee) = withdrawGasFee();
258:         if (!IZRC20(gasZRC20).transferFrom(msg.sender, FUNGIBLE_MODULE_ADDRESS, gasFee)) {
259:             revert GasFeeTransferFailed();
260:         }
261:         _burn(msg.sender, amount);
262:         emit Withdrawal(msg.sender, to, amount, gasFee, PROTOCOL_FLAT_FEE);
263:         return true; // <= FOUND
264:     }

```
['[36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L36-L39)']
```solidity
36:     function approve(address guy, uint wad) public returns (bool) {
37:         allowance[msg.sender][guy] = wad;
38:         Approval(msg.sender, guy, wad);
39:         return true; // <= FOUND
40:     }

```
['[46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L46-L59)']
```solidity
46:     function transferFrom(address src, address dst, uint wad) public returns (bool) {
47:         require(balanceOf[src] >= wad);
48: 
49:         if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
50:             require(allowance[src][msg.sender] >= wad);
51:             allowance[src][msg.sender] -= wad;
52:         }
53: 
54:         balanceOf[src] -= wad;
55:         balanceOf[dst] += wad;
56: 
57:         Transfer(src, dst, wad);
58: 
59:         return true; // <= FOUND
60:     }

```
['[184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184-L188)']
```solidity
184:     function hasZetaLiquidity() external view override returns (bool) {
185:         address poolAddress = uniswapV3Factory.getPool(WETH9Address, zetaToken, zetaPoolFee);
186: 
187:         if (poolAddress == address(0)) {
188:             return false; // <= FOUND
189:         }
190: 
191:         
192:         IUniswapV3Pool pool = IUniswapV3Pool(poolAddress);
193:         return pool.liquidity() > 0;
194:     }

```
['[203](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L205)']
```solidity
203:     function hasZetaLiquidity() external view override returns (bool) {
204:         
205:         return false; // <= FOUND
206:     }

```


</details>

## [NonCritical-54] Remove unnecessary solhint-disable

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[54](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L54-L54)']
```solidity
54:             // solhint-disable-line // <= FOUND

```


</details>

## [NonCritical-55] Do not use underscore at the end of variable name

### Resolution 
Adopting a consistent and clear naming convention enhances code readability and maintainability. In Solidity, appending an underscore at the end of a variable name is unconventional and can lead to confusion. It is generally advisable to stick to accepted naming practices to promote ease of understanding and use.


Num of instances: 11

### Findings 


<details><summary>Click to show findings</summary>

['[80](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L80-L83)']
```solidity
79:         if (
80:             zetaToken_ == address(0) || // <= FOUND
81:             pancakeV3Router_ == address(0) || // <= FOUND
82:             uniswapV3Factory_ == address(0) || // <= FOUND
83:             WETH9Address_ == address(0) // <= FOUND
84:         ) revert ZetaCommonErrors.InvalidAddress();

```
['[47](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L47-L50)']
```solidity
46:         if (
47:             zetaToken_ == address(0) || // <= FOUND
48:             uniswapV3Router_ == address(0) || // <= FOUND
49:             WETH9Address_ == address(0) || // <= FOUND
50:             poolFactory_ == address(0) // <= FOUND
51:         ) revert ZetaCommonErrors.InvalidAddress();

```
['[51](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L51-L54)']
```solidity
50:         if (
51:             zetaToken_ == address(0) || // <= FOUND
52:             uniswapV3Router_ == address(0) || // <= FOUND
53:             uniswapV3Factory_ == address(0) || // <= FOUND
54:             WETH9Address_ == address(0) // <= FOUND
55:         ) revert ZetaCommonErrors.InvalidAddress();

```
['[81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L81-L81)']
```solidity
81:         if (TSSAddress_ == address(0)) { // <= FOUND

```
['[93](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L93-L93)']
```solidity
93:         if (zetaFee_ == 0) { // <= FOUND

```
['[27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27-L27)']
```solidity
27:         if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[76](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L76-L79)']
```solidity
75:         if (
76:             zetaToken_ == address(0) || // <= FOUND
77:             tssAddress_ == address(0) || // <= FOUND
78:             tssAddressUpdater_ == address(0) || // <= FOUND
79:             pauserAddress_ == address(0) // <= FOUND
80:         ) {

```
['[118](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L118-L118)']
```solidity
118:         if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L130-L130)']
```solidity
130:         if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L34-L34)']
```solidity
34:         if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress(); // <= FOUND

```
['[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L42-L42)']
```solidity
42:         if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress(); // <= FOUND

```


</details>

## [NonCritical-56] Top level declarations should be separated by two blank lines

Num of instances: 16

### Findings 


<details><summary>Click to show findings</summary>

['[200](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L200-L202)']
```solidity
200:     } // <= FOUND
201: 
202:     function safeCreate2AndTransfer( // <= FOUND

```
['[38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L38-L40)']
```solidity
38:     } // <= FOUND
39: 
40:     function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external { // <= FOUND

```
['[71](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L71-L73)']
```solidity
71:     } // <= FOUND
72: 
73:     function burnFrom(address account, uint256 amount) public override(ZetaNonEthInterface, ERC20Burnable) { // <= FOUND

```
['[122](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L122-L124)']
```solidity
122:     } // <= FOUND
123: 
124:     function getEthFromZeta( // <= FOUND

```
['[182](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L182-L184)']
```solidity
182:     } // <= FOUND
183: 
184:     function hasZetaLiquidity() external view override returns (bool) { // <= FOUND

```
['[52](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L52-L54)']
```solidity
52:     } // <= FOUND
53: 
54:     function setInteractorByChainId(uint256 destinationChainId, bytes calldata contractAddress) external onlyOwner { // <= FOUND

```
['[176](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L176-L178)']
```solidity
176:     } // <= FOUND
177: 
178:     function _transfer(address sender, address recipient, uint256 amount) internal virtual { // <= FOUND

```
['[197](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L197-L199)']
```solidity
197:     } // <= FOUND
198: 
199:     function _burn(address account, uint256 amount) internal virtual { // <= FOUND

```
['[209](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L209-L211)']
```solidity
209:     } // <= FOUND
210: 
211:     function _approve(address owner, address spender, uint256 amount) internal virtual { // <= FOUND

```
['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L34-L36)']
```solidity
34:     } // <= FOUND
35: 
36:     function approve(address guy, uint wad) public returns (bool) { // <= FOUND

```
['[40](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L40-L42)']
```solidity
40:     } // <= FOUND
41: 
42:     function transfer(address dst, uint wad) public returns (bool) { // <= FOUND

```
['[32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L32-L34)']
```solidity
32:     } // <= FOUND
33: 
34:     function getZetaFromEth( // <= FOUND

```
['[96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L96-L98)']
```solidity
96:     } // <= FOUND
97: 
98:     function getZetaFromToken( // <= FOUND

```
['[156](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L156-L158)']
```solidity
156:     } // <= FOUND
157: 
158:     function getTokenFromZeta( // <= FOUND

```
['[29](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L29-L31)']
```solidity
29:     } // <= FOUND
30: 
31:     function setMaxSupply(uint256 maxSupply_) external onlyTssAddress { // <= FOUND

```
['[28](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L28-L30)']
```solidity
28:     } // <= FOUND
29: 
30:     modifier isValidRevertCall(ZetaInterfaces.ZetaRevert calldata zetaRevert) { // <= FOUND

```


</details>

## [NonCritical-57] Use OpenZeppelin's ReentrancyGuard/ReentrancyGuardUpgradeable rather than writing your own

### Resolution 
Leveraging OpenZeppelin's ReentrancyGuard or ReentrancyGuardUpgradeable is generally recommended over creating your own versions. The OpenZeppelin modules have undergone rigorous optimization for gas efficiency and have been comprehensively tested for potential security vulnerabilities. As a result, they provide a high degree of reliability and performance. Writing your own reentrancy guard mechanism might introduce unseen bugs or security loopholes, and likely be less gas efficient. Therefore, it's beneficial to rely on the tried-and-tested solutions offered by OpenZeppelin's established and widely-accepted smart contract library.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[65](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L65-L65)']
```solidity
65:     modifier nonReentrant() { // <= FOUND
66:         if (_locked) revert ReentrancyError();
67:         _locked = true;
68:         _;
69:         _locked = false;
70:     }

```


</details>

## [NonCritical-58] Consider using SafeTransferLib.safeTransferETH() or Address.sendValue() for clearer semantic meaning

### Resolution 
For improved code readability and better semantic understanding, it's recommended to use OpenZeppelin's SafeTransferLib.safeTransferETH() or Address.sendValue(). These functions explicitly describe their operation with their naming convention, increasing the comprehensibility of the code. Their usage over lower-level calls enhances the maintainability of your smart contract code by clearly indicating the purpose of the function. 

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L124)']
```solidity
124:     function getEthFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         uint256 zetaTokenAmount
128:     ) external override returns (uint256) {
129:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
130:         if (zetaTokenAmount == 0) revert InputCantBeZero();
131: 
132:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
133:         IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount);
134: 
135:         ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
136:             deadline: block.timestamp + MAX_DEADLINE,
137:             tokenIn: zetaToken,
138:             tokenOut: WETH9Address,
139:             fee: zetaPoolFee,
140:             recipient: address(this),
141:             amountIn: zetaTokenAmount,
142:             amountOutMinimum: minAmountOut,
143:             sqrtPriceLimitX96: 0
144:         });
145: 
146:         uint256 amountOut = uniswapV3Router.exactInputSingle(params);
147: 
148:         WETH9(WETH9Address).withdraw(amountOut);
149: 
150:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151: 
152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
153:         if (!sent) revert ErrorSendingETH();
154: 
155:         return amountOut;
156:     }

```
['[92](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92-L96)']
```solidity
92:     function send(ZetaInterfaces.SendInput calldata input) external { // <= FOUND
93:         
94:         if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed();
95:         WZETA(wzeta).withdraw(input.zetaValueAndGas);
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}(""); // <= FOUND
97:         if (!sent) revert FailedZetaSent();
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
108:     }

```


</details>

## [NonCritical-59] Whitespace in expressions

### Resolution 
Avoid unnecessary whitespace in contract lines such as ' ;' and ', )' 

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[153](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L153-L153)']
```solidity
152: 
153:         (bool sent, ) = destinationAddress.call{value: amountOut}(""); // <= FOUND

```
['[96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96-L96)']
```solidity
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}(""); // <= FOUND

```


</details>

## [NonCritical-60] Consider using named function calls

### Resolution 
Named function calls in Solidity greatly improve code readability by explicitly mapping arguments to their respective parameter names. This clarity becomes critical when dealing with functions that have numerous or complex parameters, reducing potential errors due to misordered arguments. Therefore, adopting named function calls contributes to more maintainable and less error-prone code.

Num of instances: 17

### Findings 


<details><summary>Click to show findings</summary>

['[126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L126-L126)']
```solidity
126:         _transfer(_msgSender(), recipient, amount); // <= FOUND

```
['[146](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L146-L146)']
```solidity
146:         _approve(_msgSender(), spender, amount); // <= FOUND

```
['[163](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L163-L164)']
```solidity
163: 
164:         _approve(sender, _msgSender(), currentAllowance - amount); // <= FOUND

```
['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L11-L11)']
```solidity
11:         _mint(creator, initialSupply * (10 ** uint256(decimals()))); // <= FOUND

```
['[158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L158-L158)']
```solidity
158:         _transfer(sender, recipient, amount); // <= FOUND

```
['[227](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L227-L227)']
```solidity
227:         _mint(to, amount); // <= FOUND

```
['[68](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L68-L69)']
```solidity
68: 
69:         _mint(mintee, value); // <= FOUND

```
['[257](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L257-L257)']
```solidity
257:         (address gasZRC20, uint256 gasFee) = withdrawGasFee(); // <= FOUND

```
['[81](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L81-L82)']
```solidity
81: 
82:         (address token0, address token1) = getPair(WETH9Address, zetaToken); // <= FOUND

```
['[111](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L111-L112)']
```solidity
111: 
112:         (address token0, address token1) = getPair(inputToken, WETH9Address); // <= FOUND

```
['[114](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L114-L115)']
```solidity
114: 
115:         (token0, token1) = getPair(WETH9Address, zetaToken); // <= FOUND

```
['[147](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L147-L148)']
```solidity
147: 
148:         (address token0, address token1) = getPair(zetaToken, WETH9Address); // <= FOUND

```
['[181](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L181-L182)']
```solidity
181: 
182:         (token0, token1) = getPair(WETH9Address, outputToken); // <= FOUND

```
['[91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L91-L91)']
```solidity
91:         return safeCreate2Internal(salt, initializationCode); // <= FOUND

```
['[206](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L206-L206)']
```solidity
206:         deploymentAddress = safeCreate2Internal(salt, initializationCode); // <= FOUND

```
['[101](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L101-L101)']
```solidity
101:         (address token0, address token1) = sortTokens(tokenA, tokenB); // <= FOUND

```
['[147](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L147-L147)']
```solidity
147:         address pool = uniswapv2PairFor(uniswapv2FactoryAddress, wZetaContractAddress, erc20); // <= FOUND

```


</details>

## [NonCritical-61] Revert should be used on some functions instead of return

### Resolution 
Using the `revert` statement instead of `return` in certain functions is essential for contract integrity in Solidity. While `return` merely exits the function and returns a value, `revert` undoes all changes made in the current function and throughout all its subsequent calls. In scenarios where a failure condition is met, such as incorrect inputs or an unauthorized access attempt, using `revert` ensures that the contract's state is not altered in an unintended way. This preserves consistency and helps prevent logical errors. It also makes the code's intention clear, simplifying debugging and maintenance.

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184-L188)']
```solidity
184:     function hasZetaLiquidity() external view override returns (bool) { // <= FOUND
185:         address poolAddress = uniswapV3Factory.getPool(WETH9Address, zetaToken, zetaPoolFee);
186: 
187:         if (poolAddress == address(0)) {
188:             return false; // <= FOUND
189:         }
190: 
191:         
192:         IUniswapV3Pool pool = IUniswapV3Pool(poolAddress);
193:         return pool.liquidity() > 0;
194:     }

```
['[162](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162-L170)']
```solidity
162:     function hasZetaLiquidity() external view override returns (bool) { // <= FOUND
163:         address[] memory path = new address[](2);
164:         path[0] = wETH;
165:         path[1] = zetaToken;
166: 
167:         try uniswapV2Router.getAmountsOut(1, path) returns (uint256[] memory amounts) {
168:             return amounts[path.length - 1] > 0;
169:         } catch {
170:             return false; // <= FOUND
171:         }
172:     }

```


</details>

## [NonCritical-62] Common functions should be refactored to a common base contract

### Resolution 
In Solidity development, it's advisable to refactor common functions into a shared base contract to enhance code reusability and maintainability. This approach not only promotes clean and organized code but also saves on gas costs when deploying multiple contracts that utilize the same functions. By placing shared logic in a common base contract, it becomes easier to manage updates to those functions, reducing the likelihood of errors across multiple dependent contracts. The resolution is to identify the functions that are used across different contracts, encapsulate them in a base contract, and then inherit from that base contract wherever those functions are needed.

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L184-L184)']
```solidity
184:     function hasZetaLiquidity() external view override returns (bool) { // <= FOUND
185:         address poolAddress = uniswapV3Factory.getPool(WETH9Address, zetaToken, zetaPoolFee);
186: 
187:         if (poolAddress == address(0)) {
188:             return false;
189:         }
190: 
191:         
192:         IUniswapV3Pool pool = IUniswapV3Pool(poolAddress);
193:         return pool.liquidity() > 0;
194:     }

```
['[203](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L203-L203)']
```solidity
203:     function hasZetaLiquidity() external view override returns (bool) { // <= FOUND
204:         
205:         return false;
206:     }

```
['[162](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L162-L162)']
```solidity
162:     function hasZetaLiquidity() external view override returns (bool) { // <= FOUND
163:         address[] memory path = new address[](2);
164:         path[0] = wETH;
165:         path[1] = zetaToken;
166: 
167:         try uniswapV2Router.getAmountsOut(1, path) returns (uint256[] memory amounts) {
168:             return amounts[path.length - 1] > 0;
169:         } catch {
170:             return false;
171:         }
172:     }

```


</details>

## [NonCritical-63] Use of override is unnecessary

### Resolution 
Starting with Solidity version 0.8.8, the use of the `override` keyword is simplified. If a function solely overrides an interface function and does not exist in multiple base contracts, specifying `override` becomes unnecessary. This change streamlines the code and makes it less verbose. Removing unnecessary use of `override` in these situations can make the code cleaner and more maintainable, aligning with the newer Solidity guidelines. It's a good practice to adapt to this updated behavior to stay consistent with the language's evolution and current best practices.

Num of instances: 13

### Findings 


<details><summary>Click to show findings</summary>

['[83](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L83-L83)']
```solidity
83:     function name() public view virtual override returns (string memory)  // <= FOUND

```
['[91](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L91-L91)']
```solidity
91:     function symbol() public view virtual override returns (string memory)  // <= FOUND

```
['[99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L99-L99)']
```solidity
99:     function decimals() public view virtual override returns (uint8)  // <= FOUND

```
['[107](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L107-L107)']
```solidity
107:     function totalSupply() public view virtual override returns (uint256)  // <= FOUND

```
['[116](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L116-L116)']
```solidity
116:     function balanceOf(address account) public view virtual override returns (uint256)  // <= FOUND

```
['[125](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125-L125)']
```solidity
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool)  // <= FOUND

```
['[135](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L135-L135)']
```solidity
135:     function allowance(address owner, address spender) public view virtual override returns (uint256)  // <= FOUND

```
['[145](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L145-L145)']
```solidity
145:     function approve(address spender, uint256 amount) public virtual override returns (bool)  // <= FOUND

```
['[157](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L157-L157)']
```solidity
157:     function transferFrom(address sender, address recipient, uint256 amount) public virtual override returns (bool)  // <= FOUND

```
['[225](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L225-L225)']
```solidity
225:     function deposit(address to, uint256 amount) external override returns (bool)  // <= FOUND

```
['[236](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236-L236)']
```solidity
236:     function withdrawGasFee() public view override returns (address, uint256)  // <= FOUND

```
['[256](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L256-L256)']
```solidity
256:     function withdraw(bytes memory to, uint256 amount) external override returns (bool)  // <= FOUND

```
['[62](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L62)']
```solidity
62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override  // <= FOUND

```


</details>

## [NonCritical-64] No access control on receive/payable fallback

### Resolution 
Without access control on receive/payable fallback functions in a contract, anyone can send Ether (ETH) to the contract's address. If there's no way to withdraw those funds defined within the contract, any Ether sent, whether intentionally or by mistake, will be permanently stuck. This could lead to unintended loss of funds. Implementing proper access control ensures that only authorized addresses can interact with these functions. Resolution could involve adding access control mechanisms, like Ownable or specific permission requirements, or creating a withdrawal function accessible only to the contract's owner, thus preventing unintentional loss of funds.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[72](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L72-L72)']
```solidity
72:     receive() external payable {} // <= FOUND

```


</details>

## [NonCritical-65] If statement control structures do not comply with best practices

### Resolution 
If statements which include a single line do not need to have curly brackets, however according to the Solidiity style guide the line of code executed upon the if statement condition being met should still be on the next line, not on the same line as the if statement declaration.

Num of instances: 51

### Findings 


<details><summary>Click to show findings</summary>

['[53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L53-L53)']
```solidity
53:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule(); // <= FOUND

```
['[161](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L161-L161)']
```solidity
161:         if (currentAllowance < amount) revert LowAllowance(); // <= FOUND

```
['[179](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L179-L179)']
```solidity
179:         if (sender == address(0)) revert ZeroAddress(); // <= FOUND

```
['[180](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L180-L180)']
```solidity
180:         if (recipient == address(0)) revert ZeroAddress(); // <= FOUND

```
['[183](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L183-L183)']
```solidity
183:         if (senderBalance < amount) revert LowBalance(); // <= FOUND

```
['[192](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L192-L192)']
```solidity
192:         if (account == address(0)) revert ZeroAddress(); // <= FOUND

```
['[203](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L203-L203)']
```solidity
203:         if (accountBalance < amount) revert LowBalance(); // <= FOUND

```
['[212](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L212-L212)']
```solidity
212:         if (owner == address(0)) revert ZeroAddress(); // <= FOUND

```
['[213](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L213-L213)']
```solidity
213:         if (spender == address(0)) revert ZeroAddress(); // <= FOUND

```
['[226](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L226-L226)']
```solidity
226:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS && msg.sender != SYSTEM_CONTRACT_ADDRESS) revert InvalidSender(); // <= FOUND

```
['[79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L79-L84)']
```solidity
79:         if ( // <= FOUND
80:             zetaToken_ == address(0) ||
81:             pancakeV3Router_ == address(0) ||
82:             uniswapV3Factory_ == address(0) ||
83:             WETH9Address_ == address(0)
84:         ) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L66-L66)']
```solidity
66:         if (_locked) revert ReentrancyError(); // <= FOUND

```
['[78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L78-L78)']
```solidity
78:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L79-L79)']
```solidity
79:         if (msg.value == 0) revert InputCantBeZero(); // <= FOUND

```
['[104](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L104-L104)']
```solidity
104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[105](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L105-L105)']
```solidity
105:         if (inputTokenAmount == 0) revert InputCantBeZero(); // <= FOUND

```
['[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L130-L130)']
```solidity
130:         if (zetaTokenAmount == 0) revert InputCantBeZero(); // <= FOUND

```
['[153](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L153-L153)']
```solidity
153:         if (!sent) revert ErrorSendingETH(); // <= FOUND

```
['[164](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L164-L164)']
```solidity
164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L46-L51)']
```solidity
46:         if ( // <= FOUND
47:             zetaToken_ == address(0) ||
48:             uniswapV3Router_ == address(0) ||
49:             WETH9Address_ == address(0) ||
50:             poolFactory_ == address(0)
51:         ) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L69-L69)']
```solidity
69:         if (token0 < token1) return (token0, token1); // <= FOUND

```
['[50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L50-L55)']
```solidity
50:         if ( // <= FOUND
51:             zetaToken_ == address(0) ||
52:             uniswapV3Router_ == address(0) ||
53:             uniswapV3Factory_ == address(0) ||
54:             WETH9Address_ == address(0)
55:         ) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L27-L27)']
```solidity
27:         if (zetaToken_ == address(0) || uniswapV2Router_ == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[94](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L94-L94)']
```solidity
94:         if (msg.sender != pauserAddress) revert CallerIsNotPauser(msg.sender); // <= FOUND

```
['[102](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L102-L102)']
```solidity
102:         if (msg.sender != tssAddress) revert CallerIsNotTss(msg.sender); // <= FOUND

```
['[55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L55-L55)']
```solidity
55:         if (msg.sender != tssAddressUpdater) revert CallerIsNotTssUpdater(msg.sender); // <= FOUND

```
['[118](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L118-L118)']
```solidity
118:         if (pauserAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[129](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L129-L129)']
```solidity
129:         if (msg.sender != tssAddress && msg.sender != tssAddressUpdater) revert CallerIsNotTssOrUpdater(msg.sender); // <= FOUND

```
['[130](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L130-L130)']
```solidity
130:         if (tssAddress_ == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[141](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L141-L141)']
```solidity
141:         if (tssAddress == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[75](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L75-L75)']
```solidity
75:         if (target == FUNGIBLE_MODULE_ADDRESS || target == address(this)) revert InvalidTarget(); // <= FOUND

```
['[88](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L88-L88)']
```solidity
88:         if (tokenA == tokenB) revert CantBeIdenticalAddresses(); // <= FOUND

```
['[90](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L90-L90)']
```solidity
90:         if (token0 == address(0)) revert CantBeZeroAddress(); // <= FOUND

```
['[158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L158-L158)']
```solidity
158:         if (addr == address(0)) revert ZeroAddress(); // <= FOUND

```
['[85](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L85-L85)']
```solidity
85:         if (msg.sender != wzeta) revert OnlyWZETA(); // <= FOUND

```
['[94](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L94-L95)']
```solidity
94:         
95:         if (!WZETA(wzeta).transferFrom(msg.sender, address(this), input.zetaValueAndGas)) revert WZETATransferFailed(); // <= FOUND

```
['[97](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L97-L97)']
```solidity
97:         if (!sent) revert FailedZetaSent(); // <= FOUND

```
['[115](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L115-L115)']
```solidity
115:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert OnlyFungibleModule(); // <= FOUND

```
['[69](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L69-L69)']
```solidity
69:         if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply); // <= FOUND

```
['[96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L96-L97)']
```solidity
96:         if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) // <= FOUND
97:             revert ExceedsMaxSupply(maxSupply); // <= FOUND

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L33-L33)']
```solidity
33:         if (!success) revert ZetaTransferError(); // <= FOUND

```
['[34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L34-L34)']
```solidity
34:         if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress(); // <= FOUND

```
['[41](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L41-L41)']
```solidity
41:         if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender); // <= FOUND

```
['[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L42-L42)']
```solidity
42:         if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress(); // <= FOUND

```
['[56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L56-L56)']
```solidity
56:         if (tssAddress == address(0)) revert InvalidAddress(); // <= FOUND

```
['[66](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L66-L69)']
```solidity
66:         
67: 
69:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender); // <= FOUND

```
['[25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L25-L26)']
```solidity
25:         if (keccak256(zetaMessage.zetaTxSenderAddress) != keccak256(interactorsByChainId[zetaMessage.sourceChainId])) // <= FOUND
26:             revert InvalidZetaMessageCall(); // <= FOUND

```
['[32](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L32-L32)']
```solidity
32:         if (zetaRevert.zetaTxSenderAddress != address(this)) revert InvalidZetaRevertCall(); // <= FOUND

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L33-L33)']
```solidity
33:         if (zetaRevert.sourceChainId != currentChainId) revert InvalidZetaRevertCall(); // <= FOUND

```
['[38](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L38-L38)']
```solidity
38:         if (zetaConnectorAddress == address(0)) revert ZetaCommonErrors.InvalidAddress(); // <= FOUND

```
['[44](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L44-L44)']
```solidity
44:         if (msg.sender != address(connector)) revert InvalidCaller(msg.sender); // <= FOUND

```


</details>

## [NonCritical-66] Incorrect withdraw declaration

### Resolution 
In Solidity, it's essential for clarity and interoperability to correctly specify return types in function declarations. If the `withdraw` function is expected to return a `bool` to indicate success or failure, its omission could lead to ambiguity or unexpected behavior when interacting with or calling this function from other contracts or off-chain systems. Missing return values can mislead developers and potentially lead to contract integrations built on incorrect assumptions. To resolve this, the function declaration for `withdraw` should be modified to explicitly include the `bool` return type, ensuring clarity and correctness in contract interactions.

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[193](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L193-L193)']
```solidity
193:     function withdraw(address recipient, IERC20 asset, uint256 amount) external nonReentrant onlyTSS  // <= FOUND

```
['[25](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L25-L25)']
```solidity
25:     function withdraw(uint wad) public  // <= FOUND

```


</details>

## [NonCritical-67] Contract does not follow the Solidity style guide's suggested layout ordering

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L20)']
```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors  // <= FOUND

```
['[22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22-L22)']
```solidity
22: contract ImmutableCreate2Factory  // <= FOUND

```


</details>

## [NonCritical-68] safeApprove()/approve() may revert if the current approval is not zero

### Resolution 
The `approve()` and `safeApprove()` functions in ERC20 token contracts are designed to set an allowance for a spender. However, there's a known issue where calling `approve()` to set a new allowance before the current one is zero can be a potential race condition. Attackers might spend the old allowance and the new one before the owner has a chance to change it. To mitigate this, many token contracts require the current allowance to be zero before setting a new one. As a resolution, always set the allowance to zero with an additional transaction before assigning a new value, or utilize patterns like `increaseAllowance()` and `decreaseAllowance()`.

Num of instances: 12

### Findings 


<details><summary>Click to show findings</summary>

['[126](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L126-L136)']
```solidity
126:     function getZetaFromToken(
127:         address destinationAddress,
128:         uint256 minAmountOut,
129:         address inputToken,
130:         uint256 inputTokenAmount
131:     ) external override returns (uint256) {
132:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
133:         if (inputTokenAmount == 0) revert InputCantBeZero();
134: 
135:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
136:         IERC20(inputToken).safeApprove(address(pancakeV3Router), inputTokenAmount); // <= FOUND
137: 
138:         ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
139:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
140:             recipient: destinationAddress,
141:             amountIn: inputTokenAmount,
142:             amountOutMinimum: minAmountOut
143:         });
144: 
145:         uint256 amountOut = pancakeV3Router.exactInput(params);
146: 
147:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
148:         return amountOut;
149:     }

```
['[99](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L99-L109)']
```solidity
99:     function getZetaFromToken(
100:         address destinationAddress,
101:         uint256 minAmountOut,
102:         address inputToken,
103:         uint256 inputTokenAmount
104:     ) external override returns (uint256) {
105:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
106:         if (inputTokenAmount == 0) revert InputCantBeZero();
107: 
108:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
109:         IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount); // <= FOUND
110: 
111:         (address token0, address token1) = getPair(inputToken, WETH9Address);
112:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
113: 
114:         (token0, token1) = getPair(WETH9Address, zetaToken);
115:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
116: 
117:         address[] memory path = new address[](2);
118:         path[0] = pairPools1[0];
119:         path[1] = pairPools2[0];
120: 
121:         IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
122:             tokenIn: inputToken,
123:             amountIn: inputTokenAmount,
124:             amountOutMinimum: minAmountOut,
125:             path: path,
126:             to: destinationAddress,
127:             unwrap: false
128:         });
129: 
130:         uint256 amountOut = tridentRouter.exactInput(params);
131: 
132:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
133:         return amountOut;
134:     }

```
['[98](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L108)']
```solidity
98:     function getZetaFromToken(
99:         address destinationAddress,
100:         uint256 minAmountOut,
101:         address inputToken,
102:         uint256 inputTokenAmount
103:     ) external override returns (uint256) {
104:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
105:         if (inputTokenAmount == 0) revert InputCantBeZero();
106: 
107:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
108:         IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount); // <= FOUND
109: 
110:         ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
111:             deadline: block.timestamp + MAX_DEADLINE,
112:             path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
113:             recipient: destinationAddress,
114:             amountIn: inputTokenAmount,
115:             amountOutMinimum: minAmountOut
116:         });
117: 
118:         uint256 amountOut = uniswapV3Router.exactInput(params);
119: 
120:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
121:         return amountOut;
122:     }

```
['[58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L68)']
```solidity
58:     function getZetaFromToken(
59:         address destinationAddress,
60:         uint256 minAmountOut,
61:         address inputToken,
62:         uint256 inputTokenAmount
63:     ) external override returns (uint256) {
64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:         if (inputTokenAmount == 0) revert InputCantBeZero();
66: 
67:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
68:         IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount); // <= FOUND
69: 
70:         address[] memory path;
71:         if (inputToken == wETH) {
72:             path = new address[](2);
73:             path[0] = wETH;
74:             path[1] = zetaToken;
75:         } else {
76:             path = new address[](3);
77:             path[0] = inputToken;
78:             path[1] = wETH;
79:             path[2] = zetaToken;
80:         }
81: 
82:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:             inputTokenAmount,
84:             minAmountOut,
85:             path,
86:             destinationAddress,
87:             block.timestamp + MAX_DEADLINE
88:         );
89:         uint256 amountOut = amounts[path.length - 1];
90: 
91:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92:         return amountOut;
93:     }

```
['[151](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L151-L160)']
```solidity
151:     function getEthFromZeta(
152:         address destinationAddress,
153:         uint256 minAmountOut,
154:         uint256 zetaTokenAmount
155:     ) external override returns (uint256) {
156:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
157:         if (zetaTokenAmount == 0) revert InputCantBeZero();
158: 
159:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
160:         IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount); // <= FOUND
161: 
162:         ISwapRouterPancake.ExactInputSingleParams memory params = ISwapRouterPancake.ExactInputSingleParams({
163:             tokenIn: zetaToken,
164:             tokenOut: WETH9Address,
165:             fee: zetaPoolFee,
166:             recipient: address(this),
167:             amountIn: zetaTokenAmount,
168:             amountOutMinimum: minAmountOut,
169:             sqrtPriceLimitX96: 0
170:         });
171: 
172:         uint256 amountOut = pancakeV3Router.exactInputSingle(params);
173: 
174:         WETH9(WETH9Address).withdraw(amountOut);
175: 
176:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
177: 
178:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
179:         if (!sent) revert ErrorSendingETH();
180: 
181:         return amountOut;
182:     }

```
['[136](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L136-L145)']
```solidity
136:     function getEthFromZeta(
137:         address destinationAddress,
138:         uint256 minAmountOut,
139:         uint256 zetaTokenAmount
140:     ) external override returns (uint256) {
141:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
142:         if (zetaTokenAmount == 0) revert InputCantBeZero();
143: 
144:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
145:         IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount); // <= FOUND
146: 
147:         (address token0, address token1) = getPair(zetaToken, WETH9Address);
148:         address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
149: 
150:         IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
151:             tokenIn: zetaToken,
152:             amountIn: zetaTokenAmount,
153:             amountOutMinimum: minAmountOut,
154:             pool: pairPools[0],
155:             to: destinationAddress,
156:             unwrap: true
157:         });
158: 
159:         uint256 amountOut = tridentRouter.exactInputSingle(params);
160: 
161:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
162: 
163:         return amountOut;
164:     }

```
['[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L124-L133)']
```solidity
124:     function getEthFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         uint256 zetaTokenAmount
128:     ) external override returns (uint256) {
129:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
130:         if (zetaTokenAmount == 0) revert InputCantBeZero();
131: 
132:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
133:         IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount); // <= FOUND
134: 
135:         ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
136:             deadline: block.timestamp + MAX_DEADLINE,
137:             tokenIn: zetaToken,
138:             tokenOut: WETH9Address,
139:             fee: zetaPoolFee,
140:             recipient: address(this),
141:             amountIn: zetaTokenAmount,
142:             amountOutMinimum: minAmountOut,
143:             sqrtPriceLimitX96: 0
144:         });
145: 
146:         uint256 amountOut = uniswapV3Router.exactInputSingle(params);
147: 
148:         WETH9(WETH9Address).withdraw(amountOut);
149: 
150:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
151: 
152:         (bool sent, ) = destinationAddress.call{value: amountOut}("");
153:         if (!sent) revert ErrorSendingETH();
154: 
155:         return amountOut;
156:     }

```
['[95](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L104)']
```solidity
95:     function getEthFromZeta(
96:         address destinationAddress,
97:         uint256 minAmountOut,
98:         uint256 zetaTokenAmount
99:     ) external override returns (uint256) {
100:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
101:         if (zetaTokenAmount == 0) revert InputCantBeZero();
102: 
103:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
104:         IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount); // <= FOUND
105: 
106:         address[] memory path = new address[](2);
107:         path[0] = zetaToken;
108:         path[1] = wETH;
109: 
110:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForETH(
111:             zetaTokenAmount,
112:             minAmountOut,
113:             path,
114:             destinationAddress,
115:             block.timestamp + MAX_DEADLINE
116:         );
117: 
118:         uint256 amountOut = amounts[path.length - 1];
119: 
120:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121:         return amountOut;
122:     }

```
['[184](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L184-L194)']
```solidity
184:     function getTokenFromZeta(
185:         address destinationAddress,
186:         uint256 minAmountOut,
187:         address outputToken,
188:         uint256 zetaTokenAmount
189:     ) external override nonReentrant returns (uint256) {
190:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
191:         if (zetaTokenAmount == 0) revert InputCantBeZero();
192: 
193:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
194:         IERC20(zetaToken).safeApprove(address(pancakeV3Router), zetaTokenAmount); // <= FOUND
195: 
196:         ISwapRouterPancake.ExactInputParams memory params = ISwapRouterPancake.ExactInputParams({
197:             path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
198:             recipient: destinationAddress,
199:             amountIn: zetaTokenAmount,
200:             amountOutMinimum: minAmountOut
201:         });
202: 
203:         uint256 amountOut = pancakeV3Router.exactInput(params);
204: 
205:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
206:         return amountOut;
207:     }

```
['[166](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L166-L176)']
```solidity
166:     function getTokenFromZeta(
167:         address destinationAddress,
168:         uint256 minAmountOut,
169:         address outputToken,
170:         uint256 zetaTokenAmount
171:     ) external override nonReentrant returns (uint256) {
172:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
173:         if (zetaTokenAmount == 0) revert InputCantBeZero();
174: 
175:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
176:         IERC20(zetaToken).safeApprove(address(tridentRouter), zetaTokenAmount); // <= FOUND
177: 
178:         (address token0, address token1) = getPair(zetaToken, WETH9Address);
179:         address[] memory pairPools1 = poolFactory.getPools(token0, token1, 0, 1);
180: 
181:         (token0, token1) = getPair(WETH9Address, outputToken);
182:         address[] memory pairPools2 = poolFactory.getPools(token0, token1, 0, 1);
183: 
184:         address[] memory path = new address[](2);
185:         path[0] = pairPools1[0];
186:         path[1] = pairPools2[0];
187: 
188:         IPoolRouter.ExactInputParams memory params = IPoolRouter.ExactInputParams({
189:             tokenIn: zetaToken,
190:             amountIn: zetaTokenAmount,
191:             amountOutMinimum: minAmountOut,
192:             path: path,
193:             to: destinationAddress,
194:             unwrap: false
195:         });
196: 
197:         uint256 amountOut = tridentRouter.exactInput(params);
198: 
199:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
200:         return amountOut;
201:     }

```
['[158](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L168)']
```solidity
158:     function getTokenFromZeta(
159:         address destinationAddress,
160:         uint256 minAmountOut,
161:         address outputToken,
162:         uint256 zetaTokenAmount
163:     ) external override nonReentrant returns (uint256) {
164:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
165:         if (zetaTokenAmount == 0) revert InputCantBeZero();
166: 
167:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
168:         IERC20(zetaToken).safeApprove(address(uniswapV3Router), zetaTokenAmount); // <= FOUND
169: 
170:         ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
171:             deadline: block.timestamp + MAX_DEADLINE,
172:             path: abi.encodePacked(zetaToken, zetaPoolFee, WETH9Address, tokenPoolFee, outputToken),
173:             recipient: destinationAddress,
174:             amountIn: zetaTokenAmount,
175:             amountOutMinimum: minAmountOut
176:         });
177: 
178:         uint256 amountOut = uniswapV3Router.exactInput(params);
179: 
180:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
181:         return amountOut;
182:     }

```
['[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L134)']
```solidity
124:     function getTokenFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         address outputToken,
128:         uint256 zetaTokenAmount
129:     ) external override returns (uint256) {
130:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
131:         if (zetaTokenAmount == 0) revert InputCantBeZero();
132: 
133:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
134:         IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount); // <= FOUND
135: 
136:         address[] memory path;
137:         if (outputToken == wETH) {
138:             path = new address[](2);
139:             path[0] = zetaToken;
140:             path[1] = wETH;
141:         } else {
142:             path = new address[](3);
143:             path[0] = zetaToken;
144:             path[1] = wETH;
145:             path[2] = outputToken;
146:         }
147: 
148:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
149:             zetaTokenAmount,
150:             minAmountOut,
151:             path,
152:             destinationAddress,
153:             block.timestamp + MAX_DEADLINE
154:         );
155: 
156:         uint256 amountOut = amounts[path.length - 1];
157: 
158:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
159:         return amountOut;
160:     }

```


</details>

## [NonCritical-69] Consider disallowing transfers to "address(this)"

### Resolution 
Disallowing transfers to "address(this)" prevents accidental token lockup within the contract. Transferring tokens to the contract's own address might render them irretrievable. Implement a check in the transfer function to reject transactions with the contract's address as the recipient, ensuring tokens aren't unintentionally trapped.

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[125](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L125-L125)']
```solidity
125:     function transfer(address recipient, uint256 amount) public virtual override returns (bool) { // <= FOUND
126:         _transfer(_msgSender(), recipient, amount);
127:         return true;
128:     }

```
['[42](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L42-L42)']
```solidity
42:     function transfer(address dst, uint wad) public returns (bool) { // <= FOUND
43:         return transferFrom(msg.sender, dst, wad);
44:     }

```


</details>

## [NonCritical-70] Don't use assembly for create2

### Resolution 
Using assembly for create2 is error-prone and harder to read than higher-level Solidity. With the evolution of the Solidity language, a more abstracted and clear syntax for salted contract creation, which leverages the create2 opcode, has been introduced. Instead of manually managing assembly code, developers are encouraged to use the modern syntax, ensuring better readability, maintainability, and reduced chances of mistakes. 

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[57](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L57-L57)']
```solidity
53:         assembly {
54:             
55:             let encoded_data := add(0x20, initCode) 
56:             let encoded_size := mload(initCode) 
57:             deploymentAddress := create2( // <= FOUND
58:                 
59:                 callvalue, 
60:                 encoded_data, 
61:                 encoded_size, 
62:                 salt 
63:             )
64:         }

```


</details>

## [NonCritical-71] Don't only depend on Solidity's arithmetic ordering.

### Resolution 
Relying on Solidity's default arithmetic operator precedence can lead to misunderstood or overlooked nuances in code execution. Misinterpretation risks can be significant, especially when different developers or auditors review the code. To ensure clarity and minimize potential errors, it's recommended to use parentheses. These not only override the default precedence when needed but also emphasize the intended order of operations. By deliberately showing the intended calculation sequence using parentheses, developers make the code's logic explicit, reducing the risk of unintended behaviors and making the codebase more maintainable and understandable for all stakeholders.

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[245](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L245-L245)']
```solidity
245:         uint256 gasFee = gasPrice * GAS_LIMIT + PROTOCOL_FLAT_FEE; // <= FOUND

```
['[16](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16-L16)']
```solidity
16:     uint256 public maxSupply = 2 ** 256 - 1; // <= FOUND

```


</details>

## [NonCritical-72] It is best practice to use linear inheritance

### Resolution 
In Solidity, complex inheritance structures can obfuscate code understanding, introducing potential security risks. Multiple inheritance, especially with overlapping function names or state variables, can cause unintentional overrides or ambiguous behavior. Resolution: Strive for linear and simple inheritance chains. Avoid diamond or circular inheritance patterns. Clearly document the purpose and relationships of base contracts, ensuring that overrides are intentional. Tools like Remix or Hardhat can visualize inheritance chains, assisting in verification. Keeping inheritance streamlined aids in better code readability, reduces potential errors, and ensures smoother audits and upgrades.

Num of instances: 7

### Findings 


<details><summary>Click to show findings</summary>

['[20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L20)']
```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors  // <= FOUND

```
['[56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56-L56)']
```solidity
56: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors  // <= FOUND

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33)']
```solidity
33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors  // <= FOUND

```
['[27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27-L27)']
```solidity
27: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors  // <= FOUND

```
['[17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17-L17)']
```solidity
17: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors  // <= FOUND

```
['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15)']
```solidity
15: contract ZetaConnectorBase is ConnectorErrors, Pausable  // <= FOUND

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10)']
```solidity
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors  // <= FOUND

```


</details>

## [NonCritical-73] Contracts with only unimplemented functions can be labeled as abstract

### Resolution 
In Solidity, a contract that's not meant to be deployed on its own but is intended to be inherited by other contracts should be marked `abstract`. This ensures that developers recognize the contract's incomplete or intended-to-be-extended nature. If a contract has unimplemented functions or is designed with the intention that another contract should extend its functionality, it should be explicitly labeled as `abstract`. This helps prevent inadvertent deployments and clearly communicates the contract's purpose to other developers. Resolution: Review the contract, and if it's not supposed to function standalone, mark it as `abstract` to make the intention clear.

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22-L22)']
```solidity
22: contract ImmutableCreate2Factory 

```
['[3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L3-L3)']
```solidity
3: contract WETH9 

```
['[6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6-L6)']
```solidity
6: contract UniswapImports 

```


</details>

## [NonCritical-74] A event should be emitted if a non immutable state variable is set in a constructor

Num of instances: 5

### Findings 


<details><summary>Click to show findings</summary>

['[60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L76)']
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
69:         if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
70:         _name = name_; // <= FOUND
71:         _symbol = symbol_; // <= FOUND
72:         _decimals = decimals_; // <= FOUND
73:         CHAIN_ID = chainid_;
74:         COIN_TYPE = coinType_;
75:         GAS_LIMIT = gasLimit_; // <= FOUND
76:         SYSTEM_CONTRACT_ADDRESS = systemContractAddress_; // <= FOUND
77:     }

```
['[68](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L68-L71)']
```solidity
68:     constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
69:         TSSAddress = TSSAddress_; // <= FOUND
70:         TSSAddressUpdater = TSSAddressUpdater_; // <= FOUND
71:         zetaFee = zetaFee_; // <= FOUND
72:         zeta = zeta_;
73:         zetaMaxFee = zetaMaxFee_;
74:     }

```
['[74](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L74-L87)']
```solidity
74:     constructor(address zetaToken_, address tssAddress_, address tssAddressUpdater_, address pauserAddress_) {
75:         if (
76:             zetaToken_ == address(0) ||
77:             tssAddress_ == address(0) ||
78:             tssAddressUpdater_ == address(0) ||
79:             pauserAddress_ == address(0)
80:         ) {
81:             revert ZetaCommonErrors.InvalidAddress();
82:         }
83: 
84:         zetaToken = zetaToken_;
85:         tssAddress = tssAddress_; // <= FOUND
86:         tssAddressUpdater = tssAddressUpdater_; // <= FOUND
87:         pauserAddress = pauserAddress_; // <= FOUND
88:     }

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L33-L37)']
```solidity
33:     constructor(address tssAddress_, address tssAddressUpdater_) ERC20("Zeta", "ZETA") {
34:         if (tssAddress_ == address(0) || tssAddressUpdater_ == address(0)) revert InvalidAddress();
35: 
36:         tssAddress = tssAddress_; // <= FOUND
37:         tssAddressUpdater = tssAddressUpdater_; // <= FOUND
38:     }

```
['[79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L79-L80)']
```solidity
79:     constructor(address wzeta_) {
80:         wzeta = wzeta_; // <= FOUND
81:     }

```


</details>

## [NonCritical-75] gasLimit should be uint64

### Resolution 
To ensure compatability with the EVM gasLimits should be uint64 to prevent values higher than what is compatible. In instances where L2's are used this is even more paramount as a gasLimit higher than max(uint64) may be allowed within the L2, this may not be the case with hte underlying L1 such as ZKEVM and the EVM

Num of instances: 4

### Findings 


<details><summary>Click to show findings</summary>

['[60](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L60-L70)']
```solidity
60: 
64:     constructor(
65:         string memory name_,
66:         string memory symbol_,
67:         uint8 decimals_,
68:         uint256 chainid_, // <= FOUND
69:         CoinType coinType_,
70:         uint256 gasLimit_, // <= FOUND
71:         address systemContractAddress_
72:     ) {

```
['[279](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L279-L284)']
```solidity
279: 
284:     function updateGasLimit(uint256 gasLimit) external onlyFungible { // <= FOUND

```
['[14](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L14-L15)']
```solidity
14:         
15:         uint256 destinationGasLimit; // <= FOUND

```
['[45](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L45-L45)']
```solidity
45:     event UpdatedGasLimit(uint256 gasLimit); // <= FOUND

```


</details>

## [NonCritical-76] Mint functions should be accompanied by a burn function and vice versa

### Resolution 
When a contract provides a mint function to increase token supply, it's prudent to also include a burn function to decrease supply, and vice versa. This ensures a balanced mechanism to manage token supply. Without a corresponding burn, continuous minting can lead to inflation, devaluing the token. Conversely, without minting, excessive burning can deflate supply excessively. Both scenarios may disrupt the intended economic model. Resolution: Always pair mint and burn functions in token contracts. Implement appropriate access controls to ensure only authorized entities can trigger these functions, preserving the token's integrity and value proposition.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15-L15)']
```solidity
15: contract ZetaConnectorNonEth is ZetaConnectorBase 

```


</details>

## [NonCritical-77] Avoid hard coding gasLimit values

### Resolution 
Hardcoding `gasLimit` values in smart contracts can be problematic. Gas requirements can change due to network conditions or contract updates. If set too low, transactions may fail; if set too high, unnecessary costs might be incurred. Moreover, Ethereum's gas dynamics and costs are subject to change with network upgrades, like the transition to Ethereum 2.0. Instead of hardcoding, dynamically estimate gas or provide mechanisms for administrators to update gas limits. This ensures flexibility and avoids transaction failures or inefficiencies due to outdated gas settings. Always remember to test thoroughly after any changes to gas-related logic.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[75](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L75-L75)']
```solidity
75:         GAS_LIMIT = gasLimit_; // <= FOUND

```


</details>

## [NonCritical-78] Immutable and constant integer state variables should not be casted

### Resolution 
The definition of a constant or immutable variable is that they do not change, casting such variables can potentially push more than one 'value' to a constant, for example a uin128 constant can have its original value and that of when it's casted to uint64 (i.e it has some bytes truncated). This can create confusion and inconsistencies within the code which can inadvertently increase the attack surface of the project. It is thus advise to either change the uint byte size in the constant/immutable definition of the variable or introduce a second state variable to cover the differing casts that are expected such as having a uint128 constant and a separate uint64 constant.

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[58](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L58-L68)']
```solidity
58:     function getZetaFromToken(
59:         address destinationAddress,
60:         uint256 minAmountOut,
61:         address inputToken,
62:         uint256 inputTokenAmount
63:     ) external override returns (uint256) {
64:         if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
65:         if (inputTokenAmount == 0) revert InputCantBeZero();
66: 
67:         IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
68:         IERC20(inputToken).safeApprove(address(uniswapV2Router), inputTokenAmount); // <= FOUND
69: 
70:         address[] memory path;
71:         if (inputToken == wETH) {
72:             path = new address[](2);
73:             path[0] = wETH;
74:             path[1] = zetaToken;
75:         } else {
76:             path = new address[](3);
77:             path[0] = inputToken;
78:             path[1] = wETH;
79:             path[2] = zetaToken;
80:         }
81: 
82:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
83:             inputTokenAmount,
84:             minAmountOut,
85:             path,
86:             destinationAddress,
87:             block.timestamp + MAX_DEADLINE
88:         );
89:         uint256 amountOut = amounts[path.length - 1];
90: 
91:         emit TokenExchangedForZeta(inputToken, inputTokenAmount, amountOut);
92:         return amountOut;
93:     }

```
['[95](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L95-L104)']
```solidity
95:     function getEthFromZeta(
96:         address destinationAddress,
97:         uint256 minAmountOut,
98:         uint256 zetaTokenAmount
99:     ) external override returns (uint256) {
100:         if (destinationAddress == address(0)) revert ZetaCommonErrors.InvalidAddress();
101:         if (zetaTokenAmount == 0) revert InputCantBeZero();
102: 
103:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
104:         IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount); // <= FOUND
105: 
106:         address[] memory path = new address[](2);
107:         path[0] = zetaToken;
108:         path[1] = wETH;
109: 
110:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForETH(
111:             zetaTokenAmount,
112:             minAmountOut,
113:             path,
114:             destinationAddress,
115:             block.timestamp + MAX_DEADLINE
116:         );
117: 
118:         uint256 amountOut = amounts[path.length - 1];
119: 
120:         emit ZetaExchangedForEth(zetaTokenAmount, amountOut);
121:         return amountOut;
122:     }

```
['[124](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L124-L134)']
```solidity
124:     function getTokenFromZeta(
125:         address destinationAddress,
126:         uint256 minAmountOut,
127:         address outputToken,
128:         uint256 zetaTokenAmount
129:     ) external override returns (uint256) {
130:         if (destinationAddress == address(0) || outputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
131:         if (zetaTokenAmount == 0) revert InputCantBeZero();
132: 
133:         IERC20(zetaToken).safeTransferFrom(msg.sender, address(this), zetaTokenAmount);
134:         IERC20(zetaToken).safeApprove(address(uniswapV2Router), zetaTokenAmount); // <= FOUND
135: 
136:         address[] memory path;
137:         if (outputToken == wETH) {
138:             path = new address[](2);
139:             path[0] = zetaToken;
140:             path[1] = wETH;
141:         } else {
142:             path = new address[](3);
143:             path[0] = zetaToken;
144:             path[1] = wETH;
145:             path[2] = outputToken;
146:         }
147: 
148:         uint256[] memory amounts = uniswapV2Router.swapExactTokensForTokens(
149:             zetaTokenAmount,
150:             minAmountOut,
151:             path,
152:             destinationAddress,
153:             block.timestamp + MAX_DEADLINE
154:         );
155: 
156:         uint256 amountOut = amounts[path.length - 1];
157: 
158:         emit ZetaExchangedForToken(outputToken, zetaTokenAmount, amountOut);
159:         return amountOut;
160:     }

```


</details>

## [NonCritical-79] Use the Modern Upgradeable Contract Paradigm

### Resolution 
Modern smart contract development often employs upgradeable contract structures, utilizing proxy patterns like OpenZeppelin’s Upgradeable Contracts. This paradigm separates logic and state, allowing developers to amend and enhance the contract's functionality without altering its state or the deployed contract address. Transitioning to this approach enhances long-term maintainability.

**Resolution**: Adopt a well-established proxy pattern for upgradeability, ensuring proper initialization and employing transparent proxies to mitigate potential risks. Embrace comprehensive testing and audit practices, particularly when updating contract logic, to ensure state consistency and security are preserved across upgrades. This ensures your contract remains robust and adaptable to future requirements.

Num of instances: 16

### Findings 


<details><summary>Click to show findings</summary>

['[20](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L20-L20)']
```solidity
20: contract ZRC20 is IZRC20, IZRC20Metadata, ZRC20Errors 

```
['[56](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L56-L56)']
```solidity
56: contract ZetaTokenConsumerPancakeV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors 

```
['[33](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L33-L33)']
```solidity
33: contract ZetaTokenConsumerTrident is ZetaTokenConsumer, ZetaTokenConsumerTridentErrors 

```
['[27](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L27-L27)']
```solidity
27: contract ZetaTokenConsumerUniV3 is ZetaTokenConsumer, ZetaTokenConsumerUniV3Errors 

```
['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L11-L11)']
```solidity
11: contract ERC20Custody is ReentrancyGuard 

```
['[17](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L17-L17)']
```solidity
17: contract ZetaTokenConsumerUniV2 is ZetaTokenConsumer, ZetaTokenConsumerUniV2Errors 

```
['[22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L22-L22)']
```solidity
22: contract ImmutableCreate2Factory 

```
['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15)']
```solidity
15: contract ZetaConnectorBase is ConnectorErrors, Pausable 

```
['[22](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L22-L22)']
```solidity
22: contract SystemContract is SystemContractErrors 

```
['[55](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L55-L55)']
```solidity
55: contract ZetaConnectorZEVM is ZetaInterfaces 

```
['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15-L15)']
```solidity
15: contract ZetaConnectorNonEth is ZetaConnectorBase 

```
['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15-L15)']
```solidity
15: contract ZetaConnectorEth is ZetaConnectorBase 

```
['[3](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L3-L3)']
```solidity
3: contract WETH9 

```
['[10](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L10-L10)']
```solidity
10: contract ZetaNonEth is ZetaNonEthInterface, ERC20Burnable, ZetaErrors 

```
['[9](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L9-L9)']
```solidity
9: contract ZetaEth is ERC20("Zeta", "ZETA") 

```
['[6](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L6-L6)']
```solidity
6: contract UniswapImports 

```


</details>

## [NonCritical-80] Use transfer libraries instead of low level calls

### Resolution 
Using transfer libraries like OpenZeppelin's Address.sendValue is preferred over low-level calls for transferring Ether in Solidity. These libraries provide clearer, more semantically meaningful methods compared to low-level call() functions. They encapsulate best practices for error handling and gas management, enhancing the security and readability of your code. Low-level calls lack these built-in safety checks and can be more error-prone, especially when dealing with Ether transfers.

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[152](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L152-L153)']
```solidity
152: 
153:         (bool sent, ) = destinationAddress.call{value: amountOut}(""); // <= FOUND

```
['[96](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L96-L96)']
```solidity
96:         (bool sent, ) = FUNGIBLE_MODULE_ADDRESS.call{value: input.zetaValueAndGas}(""); // <= FOUND

```


</details>

## [NonCritical-81] Use a struct to encapsulate multiple function parameters

### Resolution 
Using a struct to encapsulate multiple parameters in Solidity functions can significantly enhance code readability and maintainability. Instead of passing a long list of arguments, which can be error-prone and hard to manage, a struct allows grouping related data into a single, coherent entity. This approach simplifies function signatures and makes the code more organized. It also enhances code clarity, as developers can easily understand the relationship between the parameters. Moreover, it aids in future code modifications and expansions, as adding or modifying a parameter only requires changes in the struct definition, rather than in every function that uses these parameters.

Num of instances: 5

### Findings 


<details><summary>Click to show findings</summary>

['[173](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L173-L177)']
```solidity
172:     function onReceive(
173:         bytes calldata zetaTxSenderAddress, // <= FOUND
174:         uint256 sourceChainId, // <= FOUND
175:         address destinationAddress, // <= FOUND
176:         uint256 zetaValue, // <= FOUND
177:         bytes calldata message, // <= FOUND
178:         bytes32 internalSendHash
179:     ) external virtual 

```
['[53](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L53-L57)']
```solidity
52:     function onReceive(
53:         bytes calldata zetaTxSenderAddress, // <= FOUND
54:         uint256 sourceChainId, // <= FOUND
55:         address destinationAddress, // <= FOUND
56:         uint256 zetaValue, // <= FOUND
57:         bytes calldata message, // <= FOUND
58:         bytes32 internalSendHash
59:     ) external override onlyTssAddress 

```
['[186](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L186-L191)']
```solidity
185:     function onRevert(
186:         address zetaTxSenderAddress, // <= FOUND
187:         uint256 sourceChainId, // <= FOUND
188:         bytes calldata destinationAddress, // <= FOUND
189:         uint256 destinationChainId, // <= FOUND
190:         uint256 remainingZetaValue, // <= FOUND
191:         bytes calldata message, // <= FOUND
192:         bytes32 internalSendHash
193:     ) external virtual 

```
['[78](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L78-L83)']
```solidity
77:     function onRevert(
78:         address zetaTxSenderAddress, // <= FOUND
79:         uint256 sourceChainId, // <= FOUND
80:         bytes calldata destinationAddress, // <= FOUND
81:         uint256 destinationChainId, // <= FOUND
82:         uint256 remainingZetaValue, // <= FOUND
83:         bytes calldata message, // <= FOUND
84:         bytes32 internalSendHash
85:     ) external override whenNotPaused onlyTssAddress 

```
['[68](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L68-L71)']
```solidity
67:     function depositAndCall(
68:         zContext calldata context, // <= FOUND
69:         address zrc20, // <= FOUND
70:         uint256 amount, // <= FOUND
71:         address target, // <= FOUND
72:         bytes calldata message
73:     ) external 

```


</details>

## [Low-15] Contracts inherits pausable without utilising whenNotPaused

### Resolution 
In Solidity, inheriting a Pausable contract without utilizing its whenNotPaused modifier can be an oversight. The Pausable pattern is designed to add an emergency stop mechanism, typically controlled by an admin role. By not using whenNotPaused, the contract fails to leverage this safety feature. To rectify this, functions that should be restricted during the pause state must include the whenNotPaused modifier. This ensures that critical functions are inaccessible when the contract is paused, enhancing security and control. It's important to judiciously apply this modifier to sensitive functions, balancing security with functionality.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[15](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L15-L15)']
```solidity
15: contract ZetaConnectorBase is ConnectorErrors, Pausable 

```


</details>

## [NonCritical-82] Consider using ERC20Capped

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[191](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L191-L191)']
```solidity
191:     function _mint(address account, uint256 amount) internal virtual { // <= FOUND
192:         if (account == address(0)) revert ZeroAddress();
193: 
194:         _totalSupply += amount;
195:         _balances[account] += amount;
196:         emit Transfer(address(0), account, amount);
197:     }

```
['[62](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L68)']
```solidity
62:     function mint(address mintee, uint256 value, bytes32 internalSendHash) external override { // <= FOUND
63:         
64: 
66:         if (msg.sender != connectorAddress) revert CallerIsNotConnector(msg.sender);
67: 
68:         _mint(mintee, value); // <= FOUND
69: 
70:         emit Minted(mintee, value, internalSendHash);
71:     }

```


</details>

## [NonCritical-83] Floating pragma defined inconsistently

### Resolution 
Inconsistent use of floating pragma declarations, like `^` for a specific version or `>=`/`<=` for a range, can lead to version ambiguities and potential compatibility issues. Consistency in specifying compiler versions is crucial for ensuring predictable behavior across different environments. Using one consistent method, either fixed or ranged, throughout the project is recommended for clarity and safety.

Num of instances: 2

### Findings 


<details><summary>Click to show findings</summary>

['[1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1-L1)']
```solidity
1: pragma solidity ^0.4.18; // <= FOUND

```
['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L13-L25)']
```solidity
13: 
25: pragma solidity >=0.8.0; // <= FOUND

```


</details>

## [NonCritical-84] package.json name variable should only consist of lowercase letters and underscores

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[1](https://github.com/code-423n4/2023-11-zetachain/blob/main/package.json#L1-L64)']
```solidity
1: {
2:   "author": "zetachain",
3:   "devDependencies": {
4:     "@changesets/cli": "^2.23.1",
5:     "@ethersproject/abi": "^5.4.7",
6:     "@ethersproject/providers": "^5.4.7",
7:     "@nomicfoundation/hardhat-chai-matchers": "^1.0.6",
8:     "@nomicfoundation/hardhat-network-helpers": "^1.0.0",
9:     "@nomicfoundation/hardhat-toolbox": "^2.0.0",
10:     "@nomiclabs/hardhat-ethers": "^2.0.5",
11:     "@nomiclabs/hardhat-etherscan": "3.0.3",
12:     "@nomiclabs/hardhat-waffle": "^2.0.3",
13:     "@openzeppelin/contracts": "^4.8.3",
14:     "@typechain/ethers-v5": "^10.1.0",
15:     "@typechain/hardhat": "^6.1.2",
16:     "@types/chai": "^4.3.1",
17:     "@types/inquirer": "^8.2.1",
18:     "@types/mocha": "^10.0.1",
19:     "@types/node": "^17.0.25",
20:     "@typescript-eslint/eslint-plugin": "^5.20.0",
21:     "@typescript-eslint/parser": "^5.20.0",
22:     "@uniswap/v2-core": "^1.0.1",
23:     "@uniswap/v2-periphery": "^1.1.0-beta.0",
24:     "@uniswap/v3-periphery": "^1.4.3",
25:     "@zetachain/networks": "^2.4.3",
26:     "chai": "^4.3.6",
27:     "cpx": "^1.5.0",
28:     "del-cli": "^5.0.0",
29:     "dotenv": "^16.0.0",
30:     "eslint": "^8.13.0",
31:     "eslint-config-prettier": "^8.5.0",
32:     "eslint-config-standard": "^17.0.0",
33:     "eslint-import-resolver-typescript": "^2.7.1",
34:     "eslint-plugin-import": "^2.26.0",
35:     "eslint-plugin-node": "^11.1.0",
36:     "eslint-plugin-prettier": "^4.0.0",
37:     "eslint-plugin-promise": "^6.0.0",
38:     "eslint-plugin-simple-import-sort": "7.0.0",
39:     "eslint-plugin-sort-keys-fix": "1.1.2",
40:     "eslint-plugin-typescript-sort-keys": "2.1.0",
41:     "ethereum-waffle": "^4.0.9",
42:     "ethereumjs-utils": "^5.2.5",
43:     "ethers": "5.6.8",
44:     "hardhat": "^2.13.1",
45:     "hardhat-abi-exporter": "^2.10.1",
46:     "hardhat-gas-reporter": "^1.0.9",
47:     "inquirer": "^8.2.4",
48:     "mocha": "^10.2.0",
49:     "solidity-coverage": "^0.8.2",
50:     "ts-mocha": "^10.0.0",
51:     "ts-node": "10.8.1",
52:     "tsconfig-paths": "^3.14.1",
53:     "typechain": "^8.1.0",
54:     "typescript": "^4.6.3"
55:   },
56:   "files": [
57:     "contracts",
58:     "abi",
59:     "dist"
60:   ],
61:   "keywords": [],
62:   "license": "MIT",
63:   "main": "./dist/lib/index.js",
64:   "name": "@zetachain/protocol-contracts", // <= FOUND
65:   "publishConfig": {
66:     "access": "public",
67:     "registry": "https://registry.npmjs.org/"
68:   },
69:   "scripts": {
70:     "build": "yarn clean && yarn compile && npx del-cli dist abi && tsc || exit 0 && npx del-cli './dist/typechain-types/**/*.js' && npx cpx './data/**/*' dist/data && npx cpx './artifacts/contracts/**/*' ./abi && npx del-cli './abi/**/*.dbg.json'",
71:     "clean": "npx hardhat clean",
72:     "compile": "yarn clean && npx hardhat compile",
73:     "generate": "yarn compile && ./scripts/generate_go.sh",
74:     "lint": "npx eslint . --ext .js,.ts",
75:     "lint:fix": "npx eslint . --ext .js,.ts,.json --fix",
76:     "prepublishOnly": "yarn build",
77:     "test": "npx hardhat clean && npx hardhat test",
78:     "tsc:watch": "npx tsc --watch"
79:   },
80:   "types": "./dist/lib/index.d.ts",
81:   "version": "0.0.8"
82: }

```


</details>

## [NonCritical-85] Try catch statement without human readable error

### Resolution 
In Solidity, the `try-catch` statement is used for handling exceptions in external function calls and contract creation. However, when a `try-catch` block doesn't include a catch for specific human-readable errors (using `catch Error(string memory reason)`), it can miss catching exceptions that provide explanatory error messages. This lack of detailed error handling could hinder debugging and obscure the reasons behind transaction failures. To address this, it's recommended to include a catch block specifically for `Error` to capture and handle these descriptive error messages effectively. This practice enhances the contract's robustness by providing clearer insights into why certain operations fail, thereby improving maintainability and troubleshooting.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[169](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV2.strategy.sol#L169-L169)']
```solidity
169:         } catch { // <= FOUND

```


</details>

## [NonCritical-86] Avoid revertible function calls in a constructor

### Resolution 
It is advisable to to perform validation within the constructor itself rather than in function calls it makes. This is because contract deployement may be performed through a frontend or manually so by having all of the validation conditions viewable in a single place allows for greater transparency during deployment for both the team and project users.

Num of instances: 1

### Findings 


<details><summary>Click to show findings</summary>

['[11](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.eth.sol#L11-L11)']
```solidity
10:     constructor(address creator, uint256 initialSupply) {
11:         _mint(creator, initialSupply * (10 ** uint256(decimals()))); // <= FOUND
12:     }

```


</details>

## [NonCritical-87] Use the same Solidity version in non library/interface files throughout the project

### Resolution 
Using the same Solidity version across non-library/interface files in a project is important for consistency and to avoid potential compatibility issues. Solidity follows Semantic Versioning (SemVer), where each version number indicates the type and extent of changes. This system ensures that each version is compatible within its major version. Mismatched versions can lead to errors or warnings when compiling, especially in larger projects. It's crucial to maintain version consistency to avoid these issues and ensure smooth functioning of the smart contracts within the project.

Num of instances: 5

### Findings 


<details><summary>Click to show findings</summary>

['[1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/WZETA.sol#L1-L1)']
```solidity
1: pragma solidity ^0.4.18; // <= FOUND

```
['[1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ImmutableCreate2Factory.sol#L1-L1)']
```solidity
1: pragma solidity 0.5.10;  // <= FOUND

```
['[2](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/UniswapPeriphery.sol#L2-L2)']
```solidity
2: pragma solidity 0.6.6; // <= FOUND

```
['[13](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/interfaces/TridentIPoolRouter.sol#L13-L13)']
```solidity
13: pragma solidity >=0.8.0; // <= FOUND

```
['[2](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/interfaces/ZetaNonEthInterface.sol#L2-L2)']
```solidity
2: pragma solidity 0.8.7; // <= FOUND

```


</details>

## [NonCritical-88] Simplify complex revert statements

### Resolution 
Simplifying complex revert statements with multiple logical OR (||) operators in Solidity can be achieved by using multiple single revert statements. This involves converting the conditional logic of require into separate if statements, each followed by a revert for specific failing conditions. This approach enhances readability and maintains clarity, especially when dealing with multiple conditions. It allows for more descriptive error messages for each specific case, improving the debugging process and making the code more maintainable. 

Num of instances: 3

### Findings 


<details><summary>Click to show findings</summary>

['[79](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L79-L82)']
```solidity
79:         if (
80:             zetaToken_ == address(0) || // <= FOUND
81:             pancakeV3Router_ == address(0) || // <= FOUND
82:             uniswapV3Factory_ == address(0) || // <= FOUND
83:             WETH9Address_ == address(0)
84:         ) revert ZetaCommonErrors.InvalidAddress();

```
['[46](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L46-L49)']
```solidity
46:         if (
47:             zetaToken_ == address(0) || // <= FOUND
48:             uniswapV3Router_ == address(0) || // <= FOUND
49:             WETH9Address_ == address(0) || // <= FOUND
50:             poolFactory_ == address(0)
51:         ) revert ZetaCommonErrors.InvalidAddress();

```
['[50](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L50-L53)']
```solidity
50:         if (
51:             zetaToken_ == address(0) || // <= FOUND
52:             uniswapV3Router_ == address(0) || // <= FOUND
53:             uniswapV3Factory_ == address(0) || // <= FOUND
54:             WETH9Address_ == address(0)
55:         ) revert ZetaCommonErrors.InvalidAddress();

```


</details>